import webview
import threading
import asyncio
import os
import sys
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
from core.app_paths import executable_dir, resource_path, writable_data_path

load_dotenv(resource_path(".env"))
load_dotenv(executable_dir() / ".env", override=False)
load_dotenv(writable_data_path(".env"), override=False)
load_dotenv()

# Core & LCU
from lcu_driver import Connector
from core.auth import SupabaseAuthService
from core.live_data import LiveGameAPI
from core.assistant import VoiceAssistant
from core.coach_brain import CoachBrain
from core.coach_service import CoachService
from core.champ_select import ChampSelectCoach
from core.league_knowledge import LeagueKnowledgeBase
from core.match_analyzer import confidence_label, duration_label
from core.minerva_voice import MinervaVoice
from core.scraper import EnemyScraper
from core.settings_store import SettingsStore
from core.ui_bridge import evaluate_js_call

connector = Connector()
window = None
assistant = VoiceAssistant()
voice = MinervaVoice()
knowledge = LeagueKnowledgeBase(locale="pt_BR")
auth_service = SupabaseAuthService(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY"),
    storage_path=str(writable_data_path("auth_session.json")),
)
settings_store = SettingsStore(writable_data_path("settings.json"))
coach_service = CoachService(knowledge)
coach = CoachBrain(assistant, voice, knowledge=knowledge, coach_service=coach_service)
draft_coach = ChampSelectCoach(
    assistant,
    voice,
    knowledge=knowledge,
    coach_service=coach_service,
    history_provider=lambda: coach.memory.build_history_snapshot(limit_matches=8),
)
scraper = None
live_api = None
lcu_thread = None
lcu_started = False
match_finalize_lock = threading.Lock()
match_finalize_state = {
    "finalizing": False,
    "finalized": False,
    "summary": None,
    "result": None,
}


# UI State Tracking to avoid bridge flooding
LAST_UI_STATE = {"phase": None, "champion": None, "summoner": None}

def sync_ui_game_state(phase=None, champion=None):
    global LAST_UI_STATE
    
    # Defaults to current known state if not provided
    current_phase = phase or LAST_UI_STATE["phase"] or "Lobby"
    current_champion = champion or (coach.current_champion_name if 'coach' in globals() else None)
    current_summoner = (coach.active_player_name if 'coach' in globals() else None)
    
    # Only push if something meaningful changed
    if (current_phase == LAST_UI_STATE["phase"] and 
        current_champion == LAST_UI_STATE["champion"] and 
        current_summoner == LAST_UI_STATE["summoner"]):
        return
        
    LAST_UI_STATE["phase"] = current_phase
    LAST_UI_STATE["champion"] = current_champion
    LAST_UI_STATE["summoner"] = current_summoner
    
    if window:
        evaluate_js_call(window, "updateGameState", current_phase, current_summoner, current_champion)







def push_auth_snapshot(message=None):
    if window:
        evaluate_js_call(window, "hydrateAuthState", auth_service.snapshot(message=message))


def _settings_account_key(snapshot=None):
    auth_snapshot = snapshot or auth_service.snapshot()
    user = auth_snapshot.get("user") if isinstance(auth_snapshot, dict) else None
    if isinstance(user, dict):
        return user.get("id") or user.get("email") or "__default__"
    return "__default__"


def is_app_unlocked():
    return bool(api and getattr(api, "authenticated", False))


def unlock_application():
    global lcu_thread, lcu_started
    if not api.authenticated:
        return

    assistant.set_enabled(api.voice_enabled)
    push_auth_snapshot()
    push_history_overview()
    push_settings_snapshot()
    push_jungle_intel()

    if not lcu_started:
        lcu_thread = threading.Thread(target=start_lcu, daemon=True)
        lcu_thread.start()
        lcu_started = True


def lock_application():
    global live_api
    assistant.set_enabled(False)
    coach.deactivate_match()
    coach.reset()
    draft_coach.reset()
    if live_api:
        live_api.stop()
        live_api = None


def _reset_match_finalize_state():
    with match_finalize_lock:
        match_finalize_state.update(
            {
                "finalizing": False,
                "finalized": False,
                "summary": None,
                "result": None,
            }
        )


def _normalize_match_result(value):
    if value is None:
        return None

    token = str(value).strip().lower()
    if not token:
        return None

    aliases = {
        "victory": "win",
        "victorious": "win",
        "won": "win",
        "win": "win",
        "defeat": "loss",
        "defeated": "loss",
        "lost": "loss",
        "loss": "loss",
    }
    return aliases.get(token, token)


def _extract_result_from_payload(payload):
    seen = set()

    def _walk(node, parent_key=""):
        if id(node) in seen:
            return None
        seen.add(id(node))

        if isinstance(node, dict):
            for key, value in node.items():
                normalized_key = str(key).strip().lower().replace(" ", "_")
                normalized_value = _normalize_match_result(value)

                if normalized_key in {"result", "game_result", "match_result", "outcome", "victory", "defeat"}:
                    if normalized_value in {"win", "loss"}:
                        return normalized_value
                    if isinstance(value, bool):
                        return "win" if value else "loss"

                if any(token in normalized_key for token in ("won", "victory", "winner", "is_winner")):
                    if isinstance(value, bool):
                        return "win" if value else "loss"
                    if normalized_value in {"win", "loss"}:
                        return normalized_value

                if any(token in normalized_key for token in ("lost", "loss", "defeat", "defeated", "is_loser")):
                    if isinstance(value, bool):
                        return "loss" if value else "win"
                    if normalized_value in {"win", "loss"}:
                        return normalized_value

                if isinstance(value, (dict, list, tuple)):
                    found = _walk(value, normalized_key)
                    if found:
                        return found
                elif isinstance(value, str):
                    if normalized_value in {"win", "loss"}:
                        return normalized_value
        elif isinstance(node, (list, tuple)):
            for item in node:
                found = _walk(item, parent_key)
                if found:
                    return found
        elif isinstance(node, str):
            normalized_value = _normalize_match_result(node)
            if normalized_value in {"win", "loss"}:
                return normalized_value

        return None

    return _walk(payload)


async def _fetch_endgame_result(connection):
    if connection is None:
        return None

    endpoints = [
        "/lol-end-of-game/v1/eog-stats-block",
        "/lol-end-of-game/v1/gameclient-eog-stats-block",
        "/lol-gameflow/v1/session",
    ]

    for endpoint in endpoints:
        try:
            response = await connection.request("get", endpoint)
        except Exception:
            continue

        if response.status != 200:
            continue

        try:
            payload = await response.json()
        except Exception:
            continue

        result = _extract_result_from_payload(payload)
        if result in {"win", "loss"}:
            return result

    return None


async def finalize_match_flow(connection=None, *, requested_result=None, source="gameflow"):
    global live_api
    if not coach.match_started and not coach.memory.current_match.entries:
        return None

    with match_finalize_lock:
        if match_finalize_state["finalized"]:
            return match_finalize_state["summary"]
        if match_finalize_state["finalizing"]:
            return match_finalize_state["summary"]
        match_finalize_state["finalizing"] = True

    try:
        result = _normalize_match_result(requested_result)
        if result not in {"win", "loss"}:
            result = await _fetch_endgame_result(connection)

        if result not in {"win", "loss"}:
            result = "unknown" if source == "disconnect" else "completed"

        coach.deactivate_match()
        if live_api:
            live_api.stop()

        if window:
            evaluate_js_call(window, "updateGameState", "Partida Finalizada")

        summary = coach.finalize_match(result=result)

        with match_finalize_lock:
            match_finalize_state["summary"] = summary
            match_finalize_state["result"] = result
            match_finalize_state["finalized"] = True
            match_finalize_state["finalizing"] = False

        if summary and api.voice_enabled:
            assistant.say(summary.coach_note, "neutral", category="recovery")

        return summary
    finally:
        with match_finalize_lock:
            match_finalize_state["finalizing"] = False


def _postgame_payload(summary, *, timeline=None):
    history_snapshot = _history_snapshot()
    stats = summary.stats or {}
    adaptive = stats.get("adaptive") or {}
    positive = stats.get("positive", 0)
    negative = stats.get("negative", 0)
    neutral = stats.get("neutral", 0)
    duration_seconds = stats.get("duration_seconds", 0)
    duration = duration_label(duration_seconds)

    top_categories = stats.get("top_categories", [])
    top_impacts = stats.get("top_impacts", [])
    focus = top_impacts[0][0].replace("_", " ").title() if top_impacts else top_categories[0][0].replace("_", " ").title() if top_categories else "Leitura geral"
    total_entries = stats.get("entries", 0)
    confidence = confidence_label(total_entries)
    critical_moments = stats.get("critical_moments", 0)

    reads = [summary.opening, *summary.improvements[:2], *summary.strengths[:1], summary.coach_note]
    if critical_moments:
        reads.insert(1, f"Momentos de alto impacto: {critical_moments}. Aqui foi onde a partida realmente virou ou quase virou.")
    if adaptive.get("headline"):
        reads.insert(1 if not critical_moments else 2, adaptive.get("headline"))
    if history_snapshot and history_snapshot.get("matches_played", 0) > 0:
        reads.append(
            f"Histórico recente: {history_snapshot.get('record', '--')}. {history_snapshot.get('headline', '')}".strip()
        )
    memory_items = (
        [{"title": "Pontos fortes", "note": item, "tone": "positive"} for item in summary.strengths[:3]]
        + [{"title": "Ajuste prioritario", "note": item, "tone": "negative"} for item in summary.improvements[:3]]
    )
    memory_items.extend(_history_memory_items(history_snapshot, limit_recent=2))

    result_map = {
        "win": "Vitória",
        "loss": "Derrota",
        "completed": "Concluída",
        "unknown": "Em revisão",
    }

    return {
        "title": summary.headline,
        "result": result_map.get(summary.result, "Em revisão"),
        "duration": duration,
        "scoreline": f"{positive}+ / {negative}- / {neutral}~",
        "focus": focus,
        "confidence": confidence,
        "reads": reads,
        "memory": memory_items,
        "timeline": timeline or [],
        "insights": {
            "headline": summary.headline,
            "opening": summary.opening,
            "strengths": list(summary.strengths),
            "improvements": list(summary.improvements),
            "key_moments": list(summary.key_moments),
            "next_steps": list(summary.next_steps),
            "adaptive": {
                "headline": adaptive.get("headline", ""),
                "repeated_patterns": list(adaptive.get("repeated_patterns", [])),
                "recovered_patterns": list(adaptive.get("recovered_patterns", [])),
                "phase_pressure": list(adaptive.get("phase_pressure", [])),
            },
        },
    }


def push_postgame_summary(summary):
    timeline = coach.memory.build_postgame_timeline(limit=12)
    payload = _postgame_payload(summary, timeline=timeline)
    evaluate_js_call(window, "updatePostGameSummary", payload)
    evaluate_js_call(window, "setCoachTaxonomyFocus", "recovery")


def push_jungle_intel():
    evaluate_js_call(window, "updateJungleIntel", coach.get_jungle_intel_snapshot())


def push_settings_snapshot():
    if window:
        evaluate_js_call(window, "hydrateSettings", api.get_settings_snapshot())
        mode = api.get_settings_snapshot().get("coach_mode")
        if mode:
            evaluate_js_call(window, "setCoachTaxonomyFocus", mode)


def push_memory_entry(entry):
    evaluate_js_call(window, "appendPostGameMemory", entry)


def _history_snapshot():
    try:
        return coach.memory.build_history_snapshot(limit_matches=8)
    except Exception:
        return None


def _history_memory_items(snapshot, limit_recent=4):
    if not snapshot or snapshot.get("matches_played", 0) <= 0:
        return []

    items = []

    for note in snapshot.get("recurring_improvements", [])[:2]:
        items.append(
            {
                "title": "Vazamento recorrente",
                "note": note,
                "tone": "negative",
                "meta": "histórico",
            }
        )

    for note in snapshot.get("recurring_strengths", [])[:2]:
        items.append(
            {
                "title": "Padrão forte",
                "note": note,
                "tone": "positive",
                "meta": "histórico",
            }
        )

    for item in snapshot.get("recent_memory", [])[:limit_recent]:
        items.append(
            {
                "title": item.get("title", "Partida recente"),
                "note": item.get("note", ""),
                "tone": item.get("tone", "system"),
                "meta": "últimas partidas",
            }
        )

    return items


def push_history_overview():
    snapshot = _history_snapshot()
    if not snapshot or snapshot.get("matches_played", 0) <= 0:
        return
    adaptive = snapshot.get("adaptive_profile", {})

    matches_played = snapshot.get("matches_played", 0)
    confidence = confidence_label(matches_played)
    reads = [
        snapshot.get("headline", "Memória recente carregada."),
        *snapshot.get("recurring_improvements", [])[:2],
        *snapshot.get("recurring_strengths", [])[:1],
    ]

    evaluate_js_call(
        window,
        "updatePostGameSummary",
        {
            "title": "Memória persistente do jogador",
            "result": snapshot.get("record", "--"),
            "duration": "Histórico",
            "scoreline": f"{matches_played} partidas",
            "focus": "Padrões recorrentes",
            "confidence": confidence,
            "reads": reads,
            "memory": _history_memory_items(snapshot, limit_recent=4),
            "timeline": [],
            "insights": {
                "headline": snapshot.get("headline", "Memória recente carregada."),
                "opening": "Os padrões das últimas filas já estão prontos para orientar a próxima partida.",
                "strengths": snapshot.get("recurring_strengths", [])[:3],
                "improvements": snapshot.get("recurring_improvements", [])[:3],
                "key_moments": [],
                "next_steps": ["Entrar na próxima fila com foco no ajuste prioritário do histórico."],
            },
        },
    )


def reset_postgame_panel():
    snapshot = _history_snapshot()
    reads = [
        "A nova partida já começou. O coach vai guardar os padrões mais importantes durante o jogo.",
        "Farm, visão, itemização e erros repetidos voltam para a memória assim que aparecerem.",
    ]
    if snapshot and snapshot.get("matches_played", 0) > 0:
        reads.append(
            f"Histórico carregado: {snapshot.get('record', '--')}. {snapshot.get('headline', '')}".strip()
        )
    evaluate_js_call(
        window,
        "updatePostGameSummary",
        {
            "title": "Partida em andamento",
            "result": "Em jogo",
            "duration": "--",
            "scoreline": "--",
            "focus": "Lane",
            "confidence": "--",
            "reads": reads,
            "memory": _history_memory_items(snapshot, limit_recent=4),
            "timeline": [],
            "insights": {
                "headline": "Partida em andamento",
                "opening": "O coach vai transformar a partida atual em leitura reaproveitável assim que o jogo andar.",
                "strengths": [],
                "improvements": [],
                "key_moments": [],
                "next_steps": ["Segura disciplina de lane, visão e reset para alimentar um pós-jogo mais forte."],
            },
        },
    )

def handle_live_event(event_type, payload):
    if not is_app_unlocked():
        return
    # Passa o dado para o processador do Coach
    if event_type == "active_player":
        coach.update_active_player(payload)
    elif event_type == "players":
        coach.update_players(payload)
        push_jungle_intel()
        sync_ui_game_state(phase="In Game")
        if scraper:
            scraper.process_players(payload, coach.active_player_name)
    elif event_type == "event":
        coach.process_event(payload)
        push_jungle_intel()
        # Log to UI
        name = payload.get("EventName")
        if name in ["ChampionKill", "DragonKill"]:
            evaluate_js_call(window, "addAILog", f"Detectado evento: {name} no mapa", "normal")
    elif event_type == "game_stats":
        coach.update_game_stats(payload)

class Api:
    """ Python API exposed to Javascript UI """

    DEFAULT_CATEGORY_FILTERS = {
        "draft": True,
        "lane": True,
        "macro": True,
        "objective": True,
        "economy": True,
        "recovery": True,
    }

    def __init__(self):
        self.volume = 80
        self.voice_enabled = True
        self.objectives_enabled = True
        self.hardcore_enabled = True
        self.voice_preset = "hardcore"
        self.voice_personality = "minerva"
        self.category_filters = dict(self.DEFAULT_CATEGORY_FILTERS)
        self.solo_focus = True
        
        # New configurable intervals & thresholds
        self.macro_interval = 200
        self.minimap_interval = 150
        self.economy_interval = 300
        self.item_check_interval = 45
        self.farm_threshold = 0.6
        self.vision_threshold = 5.0

        self.authenticated = auth_service.snapshot().get("authenticated", False)
        self._load_settings()

    def _settings_payload(self):
        return {
            "volume": self.volume,
            "voice_enabled": self.voice_enabled,
            "objectives_enabled": self.objectives_enabled,
            "hardcore_enabled": self.hardcore_enabled,
            "voice_preset": self.voice_preset,
            "voice_personality": self.voice_personality,
            "category_filters": dict(self.category_filters),
            "solo_focus": self.solo_focus,
            "macro_interval": self.macro_interval,
            "minimap_interval": self.minimap_interval,
            "economy_interval": self.economy_interval,
            "item_check_interval": self.item_check_interval,
            "farm_threshold": self.farm_threshold,
            "vision_threshold": self.vision_threshold,
        }

    def _persist_settings(self):
        settings_store.save(_settings_account_key(), self._settings_payload())

    def _load_settings(self, snapshot=None):
        payload = settings_store.load(_settings_account_key(snapshot))
        if not payload:
            return

        self.volume = int(payload.get("volume", self.volume))
        self.voice_enabled = bool(payload.get("voice_enabled", self.voice_enabled))
        self.objectives_enabled = bool(payload.get("objectives_enabled", self.objectives_enabled))
        self.voice_preset = str(payload.get("voice_preset", self.voice_preset) or self.voice_preset)
        self.voice_personality = str(payload.get("voice_personality", self.voice_personality) or self.voice_personality)
        self.category_filters = {
            **self.DEFAULT_CATEGORY_FILTERS,
            **(payload.get("category_filters") or {}),
        }
        self.solo_focus = bool(payload.get("solo_focus", True))
        self.hardcore_enabled = bool(payload.get("hardcore_enabled", self.voice_preset == "hardcore"))
        
        # Load new configurable params
        self.macro_interval = int(payload.get("macro_interval", self.macro_interval))
        self.minimap_interval = int(payload.get("minimap_interval", self.minimap_interval))
        self.economy_interval = int(payload.get("economy_interval", self.economy_interval))
        self.item_check_interval = int(payload.get("item_check_interval", self.item_check_interval))
        self.farm_threshold = float(payload.get("farm_threshold", self.farm_threshold))
        self.vision_threshold = float(payload.get("vision_threshold", self.vision_threshold))

    def _apply_settings_runtime(self):
        assistant.set_volume(self.volume)
        assistant.set_enabled(self.voice_enabled if self.authenticated else False)
        assistant.set_voice_personality(self.voice_personality)
        voice.set_intensity("hardcore" if self.hardcore_enabled else "standard")
        coach.objectives_enabled = self.objectives_enabled
        coach.set_voice_preset(self.voice_preset)
        
        # Apply structured settings to CoachBrain
        coach.settings.solo_focus = self.solo_focus
        coach.settings.macro_interval = self.macro_interval
        coach.settings.minimap_interval = self.minimap_interval
        coach.settings.economy_interval = self.economy_interval
        coach.settings.item_check_interval = self.item_check_interval
        coach.settings.farm_threshold = self.farm_threshold
        coach.settings.vision_threshold = self.vision_threshold
        
        assistant.set_tts_mode("minimal" if self.voice_preset == "minimal" else "smart")
        for category, enabled in self.category_filters.items():
            coach.set_category_enabled(category, enabled)

    def reload_settings_for_current_user(self, snapshot=None):
        self._load_settings(snapshot)
        self.authenticated = bool((snapshot or auth_service.snapshot()).get("authenticated", False))
        self._apply_settings_runtime()

    def set_volume(self, value):
        self.volume = int(value)
        assistant.set_volume(self.volume)
        self._persist_settings()
        print(f"[Backend] Volume ajustado para {self.volume}")
        push_settings_snapshot()

    def toggle_voice(self, state):
        self.voice_enabled = state
        assistant.set_enabled(state)
        self._persist_settings()
        print(f"[Backend] Voz: {'Ligada' if state else 'Desligada'}")
        push_settings_snapshot()

    def toggle_objectives(self, state):
        self.objectives_enabled = state
        coach.objectives_enabled = state
        self._persist_settings()
        print(f"[Backend] Alertas de Objetivos: {'Ligado' if state else 'Desligado'}")
        push_settings_snapshot()

    def toggle_hardcore(self, state):
        self.set_voice_preset("hardcore" if state else "standard")
        print(f"[Backend] Hardcore Cobranças: {'Ligado' if state else 'Desligado'}")

    def set_voice_preset(self, preset):
        normalized = str(preset or "standard").strip().lower()
        if normalized not in {"standard", "hardcore", "minimal"}:
            normalized = "standard"

        self.voice_preset = normalized
        self.hardcore_enabled = normalized == "hardcore"
        voice.set_intensity("hardcore" if self.hardcore_enabled else "standard")
        coach.set_voice_preset(normalized)
        assistant.set_tts_mode("minimal" if normalized == "minimal" else "smart")
        self._persist_settings()
        print(f"[Backend] Preset de voz: {normalized}")
        push_settings_snapshot()

    def toggle_solo_focus(self, state):
        self.solo_focus = bool(state)
        if hasattr(coach, 'settings'):
            coach.settings.solo_focus = self.solo_focus
        self._persist_settings()
        print(f"[Backend] Solo Focus: {'Ligado' if self.solo_focus else 'Desligado'}")
        push_settings_snapshot()

    def set_macro_interval(self, value):
        self.macro_interval = int(value)
        coach.settings.macro_interval = self.macro_interval
        self._persist_settings()
        push_settings_snapshot()

    def set_minimap_interval(self, value):
        self.minimap_interval = int(value)
        coach.settings.minimap_interval = self.minimap_interval
        self._persist_settings()
        push_settings_snapshot()

    def set_economy_interval(self, value):
        self.economy_interval = int(value)
        coach.settings.economy_interval = self.economy_interval
        self._persist_settings()
        push_settings_snapshot()

    def set_item_check_interval(self, value):
        self.item_check_interval = int(value)
        coach.settings.item_check_interval = self.item_check_interval
        self._persist_settings()
        push_settings_snapshot()

    def set_farm_threshold(self, value):
        self.farm_threshold = float(value)
        coach.settings.farm_threshold = self.farm_threshold
        self._persist_settings()
        push_settings_snapshot()

    def set_vision_threshold(self, value):
        self.vision_threshold = float(value)
        coach.settings.vision_threshold = self.vision_threshold
        self._persist_settings()
        push_settings_snapshot()

    def set_voice_personality(self, personality):
        normalized = str(personality or "minerva").strip().lower()
        if normalized not in {"minerva", "standard"}:
            normalized = "minerva"
        self.voice_personality = normalized
        assistant.set_voice_personality(normalized)
        self._persist_settings()
        print(f"[Backend] Personalidade de voz: {normalized}")
        push_settings_snapshot()

    def set_category_enabled(self, category, state):
        normalized = str(category or "").strip().lower()
        if normalized not in self.category_filters:
            return
        self.category_filters[normalized] = bool(state)
        coach.set_category_enabled(normalized, state)
        self._persist_settings()
        print(f"[Backend] Categoria {normalized}: {'Ligada' if state else 'Desligada'}")
        push_settings_snapshot()

    def set_category_preset(self, preset):
        presets = {
            "balanced": {"draft": True, "lane": True, "macro": True, "objective": True, "economy": True, "recovery": True},
            "draft": {"draft": True, "lane": True, "macro": False, "objective": True, "economy": True, "recovery": False},
            "macro": {"draft": False, "lane": True, "macro": True, "objective": True, "economy": True, "recovery": True},
            "recovery": {"draft": False, "lane": False, "macro": True, "objective": True, "economy": True, "recovery": True},
        }
        next_filters = presets.get(str(preset or "").strip().lower(), presets["balanced"])
        self.category_filters = dict(next_filters)
        for category, enabled in self.category_filters.items():
            coach.set_category_enabled(category, enabled)
        self._persist_settings()
        print(f"[Backend] Preset de categorias: {preset}")
        push_settings_snapshot()

    def get_settings_snapshot(self):
        return self._settings_payload()

    def get_auth_snapshot(self):
        snapshot = auth_service.snapshot()
        self.authenticated = snapshot.get("authenticated", False)
        return snapshot

    def register_user(self, email, password, display_name=""):
        snapshot = auth_service.sign_up(email, password, display_name)
        self.authenticated = snapshot.get("authenticated", False)
        if self.authenticated:
            self.reload_settings_for_current_user(snapshot)
            evaluate_js_call(window, "addAILog", "Conta criada e sessão iniciada.", "success")
            unlock_application()
        else:
            evaluate_js_call(window, "addAILog", snapshot.get("message", "Cadastro processado."), "system")
        push_auth_snapshot()
        return snapshot

    def login_user(self, email, password):
        snapshot = auth_service.sign_in(email, password)
        self.authenticated = snapshot.get("authenticated", False)
        if self.authenticated:
            self.reload_settings_for_current_user(snapshot)
            evaluate_js_call(window, "addAILog", "Sessão autenticada. Bem-vindo de volta.", "success")
            unlock_application()
        else:
            evaluate_js_call(window, "addAILog", snapshot.get("message", "Não foi possível autenticar."), "warning")
        push_auth_snapshot()
        return snapshot

    def logout_user(self):
        snapshot = auth_service.sign_out()
        self.authenticated = False
        self.reload_settings_for_current_user(snapshot)
        lock_application()
        evaluate_js_call(window, "addAILog", "Sessão encerrada.", "system")
        push_auth_snapshot()
        return snapshot

# LCU Events Bindings
@connector.ready
async def connect(connection):
    if not is_app_unlocked():
        return
    print('[LCU] Conectado ao League Client')
    
    # Tenta descobrir se o jogo já ta rolando no momento exato em que abriu o app
    res = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
    if res.status == 200:
        phase = await res.json()
        if phase in ["InProgress", "ChampSelect"]:
            import collections
            EventStub = collections.namedtuple('Event', ['data'])
            # Redireciona pro observador logico saltando o lobby
            await gameflow_handler(connection, EventStub(phase))
            return

    if window:
        sync_ui_game_state(phase="Lobby")
        evaluate_js_call(window, "addAILog", "Sincronizado com o Cliente do League.", "system")
        assistant.say(voice.lobby_ready(), "positive", category="draft")

@connector.close
async def disconnect(connection):
    if not is_app_unlocked():
        return
    print('[LCU] Desconectado do League Client')
    if window:
        sync_ui_game_state(phase="Aguardando League...")
        evaluate_js_call(window, "addAILog", "O Cliente do League foi fechado.", "urgent")
    await finalize_match_flow(connection, requested_result="unknown", source="disconnect")

# LCU Champ Select Event (Drafting)
@connector.ws.register('/lol-champ-select/v1/session')
async def champ_select_session_handler(connection, event):
    if is_app_unlocked() and api.voice_enabled:
        draft_coach.process_session(event.data)
        
        # Sync selected champion to main coach and UI background
        if draft_coach.my_champ and coach.current_champion_name != draft_coach.my_champ:
            coach.current_champion_name = draft_coach.my_champ
            sync_ui_game_state(phase="Seleção de Campeões")

# When gameflow changes
@connector.ws.register('/lol-gameflow/v1/gameflow-phase')
async def gameflow_handler(connection, event):
    global live_api
    if not is_app_unlocked():
        return
    phase = event.data
    print(f'[LCU] Gameflow alterado para: {phase}')
    phase_map = {
        "ChampSelect": "draft",
        "InProgress": "in_game",
        "PreEndOfGame": "postgame",
        "EndOfGame": "postgame",
        "Lobby": "lobby",
    }
    coach.set_phase(phase_map.get(phase, phase.lower()))
    
    if not window:
        return
        
    if phase == "ChampSelect":
        _reset_match_finalize_state()
        draft_coach.reset()
        coach.reset()
        coach.deactivate_match()
        push_jungle_intel()
        sync_ui_game_state(phase="Seleção de Campeões")
        evaluate_js_call(window, "addAILog", "Fase de Draft. Analisando picks inimigos...", "system")
        evaluate_js_call(window, "setCoachTaxonomyFocus", "draft")
        assistant.say(voice.champ_select_intro(), "neutral", category="draft")
    elif phase == "InProgress":
        _reset_match_finalize_state()
        coach.reset()
        coach.activate_match()
        coach.start_match_memory()
        reset_postgame_panel()
        push_jungle_intel()
        if scraper:
            scraper.reset()
        sync_ui_game_state(phase="In Game")
        evaluate_js_call(window, "addAILog", "Partida Iniciada! Assistente ouvindo...", "system")
        evaluate_js_call(window, "setCoachTaxonomyFocus", "lane")
        if api.voice_enabled:
            assistant.say(voice.game_start(), "positive", category="lane")
            
        # Iniciar polling da Live Client Data
        if live_api:
            live_api.stop()
        live_api = LiveGameAPI(handle_live_event)
        live_api.start()
        
    elif phase in ["PreEndOfGame", "EndOfGame"]:
        await finalize_match_flow(connection, source=phase.lower())
    elif phase == "Lobby":
        coach.reset()
        coach.deactivate_match()
        push_jungle_intel()
        evaluate_js_call(window, "updateGameState", "Lobby", coach.active_player_name, coach.current_champion_name)
    else:
        evaluate_js_call(window, "updateGameState", phase, coach.active_player_name, coach.current_champion_name)

def start_lcu():
    """ Run LCU Driver in the asyncio loop for this thread """
    asyncio.set_event_loop(asyncio.new_event_loop())
    import time
    while True:
        try:
            connector.start()
            break
        except Exception as e:
            print(f"[LCU] Crash do LCU Driver interceptado (psutil ProcessLookupError). Retentando em 2s: {e}")
            time.sleep(2)


def set_dpi_aware():
    """Ensure the application handles high DPI scaling correctly on Windows."""
    try:
        import ctypes
        # Windows 8.1+
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            # Windows Vista+
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def main():
    set_dpi_aware()
    global window, api, scraper
    api = Api()
    api.reload_settings_for_current_user(auth_service.snapshot())
    
    # Resolve UI Path
    ui_path = str(resource_path('ui', 'index.html'))
    
    if not os.path.exists(ui_path):
        print("Erro: Arquivo de UI não encontrado em", ui_path)
        sys.exit(1)

    icon_path = resource_path('assets', 'icon.ico')
    icon_path_str = str(icon_path) if os.path.exists(icon_path) else None

    # Initialize PyWebView
    window = webview.create_window(
        'Coacher - Assistente Inteligente', 
        ui_path, 
        js_api=api, 
        width=1100, 
        height=750, 
        background_color='#050508'
    )

    # Make VoiceAssistant log to the webview
    def log_handler(text, type_="normal", category=None):
        evaluate_js_call(window, "playTTSUpdate", text, type_, category)
            
    assistant.callback_log = log_handler
    coach.set_summary_callback(push_postgame_summary)
    coach.set_memory_callback(push_memory_entry)
    coach.set_mode_callback(lambda _snapshot: push_settings_snapshot())
    scraper = EnemyScraper(assistant, window)

    def on_loaded():
        push_auth_snapshot()
        if api.authenticated:
            unlock_application()
        else:
            lock_application()

    window.events.loaded += on_loaded
    webview.start(debug=False, icon=icon_path_str, private_mode=False)

if __name__ == '__main__':
    main()
