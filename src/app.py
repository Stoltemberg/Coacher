import webview
import threading
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Core & LCU
from lcu_driver import Connector
from core.live_data import LiveGameAPI
from core.assistant import VoiceAssistant
from core.coach_brain import CoachBrain
from core.champ_select import ChampSelectCoach
from core.minerva_voice import MinervaVoice
from core.scraper import EnemyScraper
from core.ui_bridge import evaluate_js_call

connector = Connector()
window = None
assistant = VoiceAssistant()
voice = MinervaVoice()
coach = CoachBrain(assistant, voice)
draft_coach = ChampSelectCoach(assistant, voice)
scraper = None
live_api = None
match_finalize_lock = threading.Lock()
match_finalize_state = {
    "finalizing": False,
    "finalized": False,
    "summary": None,
    "result": None,
}


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
        if result not in {"win", "loss"} and source != "disconnect":
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


def _postgame_payload(summary):
    history_snapshot = _history_snapshot()
    stats = summary.stats or {}
    positive = stats.get("positive", 0)
    negative = stats.get("negative", 0)
    neutral = stats.get("neutral", 0)
    duration_seconds = stats.get("duration_seconds", 0)
    duration_minutes = int(duration_seconds // 60) if duration_seconds else 0
    duration = f"{duration_minutes} min" if duration_minutes else "--"

    top_categories = stats.get("top_categories", [])
    focus = top_categories[0][0].replace("_", " ").title() if top_categories else "Leitura geral"
    total_entries = stats.get("entries", 0)
    confidence = "Alta" if total_entries >= 8 else "Media" if total_entries >= 4 else "Baixa"

    reads = [summary.opening, *summary.improvements[:2], *summary.strengths[:1], summary.coach_note]
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
    }


def push_postgame_summary(summary):
    payload = _postgame_payload(summary)
    evaluate_js_call(window, "updatePostGameSummary", payload)
    evaluate_js_call(window, "setCoachTaxonomyFocus", "recovery")


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

    matches_played = snapshot.get("matches_played", 0)
    confidence = "Alta" if matches_played >= 8 else "Media" if matches_played >= 4 else "Baixa"
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
        },
    )


def reset_postgame_panel():
    snapshot = _history_snapshot()
    baseline_reads = [
        "A nova partida jÃ¡ comeÃ§ou. O coach vai guardar os padrÃµes mais importantes durante o jogo.",
        "Farm, visÃ£o, itemizaÃ§Ã£o e erros repetidos voltam para a memÃ³ria assim que aparecerem.",
    ]
    if snapshot and snapshot.get("matches_played", 0) > 0:
        baseline_reads.append(
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
            "reads": [
                "A nova partida já começou. O coach vai guardar os padrões mais importantes durante o jogo.",
                "Farm, visão, itemização e erros repetidos voltam para a memória assim que aparecerem.",
            ],
            "memory": [],
        },
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
            "reads": [
                "A nova partida ja comecou. O coach vai guardar os padroes mais importantes durante o jogo.",
                "Farm, visao, itemizacao e erros repetidos voltam para a memoria assim que aparecerem.",
                *baseline_reads[2:],
            ],
            "memory": _history_memory_items(snapshot, limit_recent=4),
        },
    )

def handle_live_event(event_type, payload):
    # Passa o dado para o processador do Coach
    if event_type == "active_player":
        coach.update_active_player(payload)
    elif event_type == "players":
        coach.update_players(payload)
        if scraper:
            scraper.process_players(payload, coach.active_player_name)
    elif event_type == "event":
        coach.process_event(payload)
        # Log to UI
        name = payload.get("EventName")
        if name in ["ChampionKill", "DragonKill"]:
            evaluate_js_call(window, "addAILog", f"Detectado evento: {name} no mapa", "normal")
    elif event_type == "game_stats":
        coach.update_game_stats(payload)

class Api:
    """ Python API exposed to Javascript UI """
    def __init__(self):
        self.volume = 80
        self.voice_enabled = True
        self.objectives_enabled = True
        self.hardcore_enabled = True

    def set_volume(self, value):
        self.volume = int(value)
        assistant.set_volume(self.volume)
        print(f"[Backend] Volume ajustado para {self.volume}")

    def toggle_voice(self, state):
        self.voice_enabled = state
        assistant.set_enabled(state)
        print(f"[Backend] Voz: {'Ligada' if state else 'Desligada'}")

    def toggle_objectives(self, state):
        self.objectives_enabled = state
        coach.objectives_enabled = state
        print(f"[Backend] Alertas de Objetivos: {'Ligado' if state else 'Desligado'}")

    def toggle_hardcore(self, state):
        self.hardcore_enabled = state
        coach.hardcore_enabled = state
        voice.set_intensity("hardcore" if state else "standard")
        coach.set_intensity("hardcore" if state else "standard")
        print(f"[Backend] Hardcore Cobranças: {'Ligado' if state else 'Desligado'}")

# LCU Events Bindings
@connector.ready
async def connect(connection):
    print('[LCU] Conectado ao League Client')
    
    # Tenta descobrir de o jogo já ta rolando no momento exato em que abriu o app
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
        evaluate_js_call(window, "updateGameState", "Lobby", "Invocador")
        evaluate_js_call(window, "addAILog", "Sincronizado com o Cliente do League.", "system")
        assistant.say(voice.lobby_ready(), "positive", category="draft")

@connector.close
async def disconnect(connection):
    print('[LCU] Desconectado do League Client')
    if window:
        evaluate_js_call(window, "updateGameState", "Aguardando League...")
        evaluate_js_call(window, "addAILog", "O Cliente do League foi fechado.", "urgent")
    await finalize_match_flow(connection, requested_result="unknown", source="disconnect")

# LCU Champ Select Event (Drafting)
@connector.ws.register('/lol-champ-select/v1/session')
async def champ_select_session_handler(connection, event):
    if api.voice_enabled:
        draft_coach.process_session(event.data)

# When gameflow changes
@connector.ws.register('/lol-gameflow/v1/gameflow-phase')
async def gameflow_handler(connection, event):
    global live_api
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
        coach.deactivate_match()
        evaluate_js_call(window, "updateGameState", "Seleção de Campeões")
        evaluate_js_call(window, "addAILog", "Fase de Draft. Analisando picks inimigos...", "system")
        evaluate_js_call(window, "setCoachTaxonomyFocus", "draft")
        assistant.say(voice.champ_select_intro(), "neutral", category="draft")
    elif phase == "InProgress":
        _reset_match_finalize_state()
        coach.reset()
        coach.activate_match()
        coach.start_match_memory()
        reset_postgame_panel()
        if scraper:
            scraper.reset()
        evaluate_js_call(window, "updateGameState", "In Game")
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
        coach.deactivate_match()
        evaluate_js_call(window, "updateGameState", "Lobby")
    else:
        evaluate_js_call(window, "updateGameState", phase)

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

def main():
    global window, api, scraper
    api = Api()
    voice.set_intensity("hardcore" if api.hardcore_enabled else "standard")
    coach.set_intensity("hardcore" if api.hardcore_enabled else "standard")
    
    # Resolve UI Path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(current_dir, 'ui', 'index.html')
    
    if not os.path.exists(ui_path):
        print("Erro: Arquivo de UI não encontrado em", ui_path)
        sys.exit(1)

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
        evaluate_js_call(window, "playTTSUpdate", text, category)
            
    assistant.callback_log = log_handler
    coach.set_summary_callback(push_postgame_summary)
    coach.set_memory_callback(push_memory_entry)
    scraper = EnemyScraper(assistant, window)

    def on_loaded():
        push_history_overview()
        lcu_thread = threading.Thread(target=start_lcu, daemon=True)
        lcu_thread.start()

    window.events.loaded += on_loaded
    webview.start(debug=False)

if __name__ == '__main__':
    main()
