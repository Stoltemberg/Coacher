import webview
import threading
import asyncio
import os
import sys
import time
import mimetypes
import http.server
import socketserver
import collections
from pathlib import Path
from dotenv import load_dotenv

# Path logic early to avoid import issues
from core.app_paths import desktop_ui_dir, executable_dir, project_root, writable_data_path

if not getattr(sys, "frozen", False):
    load_dotenv(project_root() / ".env")
load_dotenv(executable_dir() / ".env", override=False)
load_dotenv(writable_data_path(".env"), override=False)
load_dotenv()

# Core & LCU
from lcu_driver import Connector
from core.auth import SupabaseAuthService
from core.live_data import LiveGameAPI
from core.assistant import VoiceAssistant
from core.coach_brain import CoachBrain
from core.coach_state import CoachSettings, MatchState, DEFAULT_CATEGORY_FILTERS
from core.coach_service import CoachService
from core.champ_select import ChampSelectCoach
from core.league_knowledge import LeagueKnowledgeBase
from core.match_analyzer import confidence_label, duration_label
from core.minerva_voice import MinervaVoice
from core.scraper import EnemyScraper
from core.settings_store import SettingsStore
from core.ui_bridge import evaluate_js_call
from core.voice_catalog import normalize_voice_personality, normalize_voice_preset, voice_catalog_snapshot

# --- UI SERVER LOGIC ---

class UIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve UI assets with proper CORS and MIME types."""
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"[UI Server] {format % args}")

def start_ui_server(directory, port):
    """Binds a local server to serve the React/Next build."""
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')
    mimetypes.add_type('image/webp', '.webp')
    mimetypes.add_type('font/woff2', '.woff2')
    mimetypes.add_type('image/svg+xml', '.svg')
    
    class FixedUIHandler(UIHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    try:
        with socketserver.TCPServer(("127.0.0.1", port), FixedUIHandler) as httpd:
            print(f"[Server] UI ativa em http://127.0.0.1:{port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[Server] Erro ao iniciar servidor na porta {port}: {e}")

# --- APPLICATION ORCHESTRATION ---

class CoacherApp:
    def __init__(self):
        self.window = None
        self.port = 5005
        self.connector = Connector()
        self.assistant = VoiceAssistant()
        self.voice = MinervaVoice()
        self.knowledge = LeagueKnowledgeBase(locale="pt_BR")
        self.settings_store = SettingsStore(writable_data_path("settings.json"))
        self.draft_preferences = {
            "preferred_champion_pool": [],
            "prioritize_pool_picks": True,
        }
        
        self.auth_service = SupabaseAuthService(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY"),
            storage_path=str(writable_data_path("auth_session.json")),
        )
        
        self.coach_service = CoachService(self.knowledge)
        self.coach = CoachBrain(self.assistant, self.voice, knowledge=self.knowledge, coach_service=self.coach_service)
        
        self.draft_coach = ChampSelectCoach(
            self.assistant,
            self.voice,
            knowledge=self.knowledge,
            coach_service=self.coach_service,
            history_provider=lambda: self.coach.memory.build_history_snapshot(limit_matches=8),
            counterpick_callback=self.push_draft_recommendations,
            draft_preferences_provider=lambda: self.draft_preferences,
        )
        
        self.live_api = None
        self.scraper = None
        self.lcu_started = False
        self.last_ui_state = {"phase": None, "champion": None, "summoner": None}
        self.match_finalize_lock = threading.Lock()
        self.match_finalize_state = {"finalizing": False, "finalized": False, "summary": None, "result": None}

        # Bind LCU events - register is a decorator that returns a function
        self.connector.ready(self.on_lcu_ready)
        self.connector.ws.register('/lol-gameflow/v1/gameflow-phase')(self.on_gameflow_phase)
        self.connector.ws.register('/lol-champ-select/v1/session')(self.on_champ_select)
        
        self.sync_settings()

    def sync_settings(self):
        s = self.settings_store.get_all()
        # Sync Assistant
        self.assistant.volume = s.get("volume", 80)
        self.assistant.tts_mode = "smart" if not s.get("hardcore_enabled") else "full"
        self.assistant.voice_personality = normalize_voice_personality(
            s.get("voice_personality", "standard")
        )
        
        # Sync CoachBrain
        self.coach.settings.voice_enabled = s.get("voice_enabled", True)
        self.coach.settings.objectives_enabled = s.get("objectives_enabled", True)
        self.coach.settings.macro_interval = s.get("macro_interval", 45)
        self.coach.settings.minimap_interval = s.get("minimap_interval", 15)
        self.coach.settings.economy_interval = s.get("economy_interval", 90)
        self.coach.settings.item_check_interval = s.get("item_check_interval", 120)
        self.coach.settings.category_filters = s.get("category_filters", DEFAULT_CATEGORY_FILTERS)
        self.coach.settings.solo_focus = s.get("solo_focus", True)
        self.coach.settings.set_preset(normalize_voice_preset(s.get("voice_preset", "standard")))
        self.draft_preferences = {
            "preferred_champion_pool": list(s.get("preferred_champion_pool", [])),
            "prioritize_pool_picks": bool(s.get("prioritize_pool_picks", True)),
        }

    def is_authenticated(self):
        return self.auth_service.snapshot().get("authenticated", False)

    def sync_ui_game_state(self, phase=None, champion=None):
        current_phase = phase or self.last_ui_state["phase"] or "Lobby"
        current_champion = champion or self.coach.current_champion_name
        current_summoner = self.coach.active_player_name
        
        if (current_phase == self.last_ui_state["phase"] and 
            current_champion == self.last_ui_state["champion"] and 
            current_summoner == self.last_ui_state["summoner"]):
            return
            
        self.last_ui_state.update({
            "phase": current_phase,
            "champion": current_champion,
            "summoner": current_summoner
        })
        
        if self.window:
            evaluate_js_call(self.window, "updateGameState", current_phase, current_summoner, current_champion)

    def push_auth_snapshot(self, message=None):
        if self.window:
            evaluate_js_call(self.window, "hydrateAuthState", self.auth_service.snapshot(message=message))

    def push_draft_recommendations(self, payload):
        if self.window:
            evaluate_js_call(self.window, "updateDraftRecommendations", payload)

    async def on_lcu_ready(self, connection):
        if not self.is_authenticated(): return
        print('[LCU] Conectado ao League Client')
        
        # Fetch current summoner profile
        try:
            res = await connection.request('get', '/lol-summoner/v1/current-summoner')
            if res.status == 200:
                data = await res.json()
                display_name = data.get('displayName')
                game_name = data.get('gameName')
                tag_line = data.get('tagLine')
                
                if game_name and tag_line:
                    self.coach.active_player_name = f"{game_name}#{tag_line}"
                elif display_name:
                    self.coach.active_player_name = display_name
                else:
                    self.coach.active_player_name = "Invocador"
                    
                print(f'[LCU] Perfil carregado: {self.coach.active_player_name}')
        except Exception as e:
            print(f'[LCU] Erro ao carregar perfil: {e}')

        self.sync_ui_game_state(phase="Lobby")
        evaluate_js_call(self.window, "addAILog", f"Sincronizado com {self.coach.active_player_name}.", "system")
        self.assistant.say(self.voice.lobby_ready(), "positive", category="draft")

    async def on_gameflow_phase(self, connection, event):
        if not self.is_authenticated(): return
        phase = event.data
        print(f'[LCU] Gameflow: {phase}')
        
        if phase == "ChampSelect":
            self.coach.reset()
            self.draft_coach.reset()
            self.sync_ui_game_state(phase="Seleção de Campeões")
            self.assistant.say(self.voice.champ_select_intro(), "neutral", category="draft")
        elif phase == "InProgress":
            self.coach.activate_match()
            self.sync_ui_game_state(phase="Em Partida")
            if self.live_api: self.live_api.stop()
            self.live_api = LiveGameAPI(self.handle_live_event)
            self.live_api.start()
        elif phase in ["EndOfGame", "PreEndOfGame"]:
            await self.finalize_match_flow(connection, source=phase)

    async def on_champ_select(self, connection, event):
        if not self.is_authenticated(): return
        self.draft_coach.process_session(event.data)
        if self.draft_coach.my_champ and self.coach.current_champion_name != self.draft_coach.my_champ:
            self.coach.current_champion_name = self.draft_coach.my_champ
            self.sync_ui_game_state(phase="Seleção de Campeões")

    def handle_live_event(self, event_type, payload):
        if not self.is_authenticated(): return
        if event_type == "active_player":
            self.coach.update_active_player(payload)
        elif event_type == "players":
            self.coach.update_players(payload)
            if self.scraper: self.scraper.process_players(payload, self.coach.active_player_name)
        elif event_type == "event":
            self.coach.process_event(payload)
        elif event_type == "game_stats":
            self.coach.update_game_stats(payload)

    async def finalize_match_flow(self, connection=None, requested_result=None, source="gameflow"):
        if not self.coach.match_started and not self.coach.memory.current_match.entries:
            return None

        with self.match_finalize_lock:
            if self.match_finalize_state["finalized"] or self.match_finalize_state["finalizing"]:
                return self.match_finalize_state["summary"]
            self.match_finalize_state["finalizing"] = True

        try:
            result = self._normalize_match_result(requested_result)
            self.coach.deactivate_match()
            if self.live_api: self.live_api.stop()
            if self.window: evaluate_js_call(self.window, "updateGameState", "Partida Finalizada")

            summary = self.coach.finalize_match(result=result or "completed")
            with self.match_finalize_lock:
                self.match_finalize_state.update({"summary": summary, "result": result, "finalized": True, "finalizing": False})

            self.push_postgame_summary(summary)
            return summary
        finally:
            with self.match_finalize_lock: self.match_finalize_state["finalizing"] = False

    def _normalize_match_result(self, value):
        if not value: return None
        token = str(value).strip().lower()
        aliases = {"victory": "win", "won": "win", "defeat": "loss", "lost": "loss"}
        return aliases.get(token, token)

    def push_postgame_summary(self, summary):
        if not self.window: return
        timeline = self.coach.memory.build_postgame_timeline(limit=12)
        payload = {
            "title": summary.headline,
            "result": "Vitória" if summary.result == "win" else "Derrota",
            "duration": duration_label(summary.stats.get("duration_seconds", 0)),
            "scoreline": f"{summary.stats.get('positive', 0)}+ / {summary.stats.get('negative', 0)}-",
            "focus": "Análise Tática",
            "confidence": confidence_label(summary.stats.get("entries", 0)),
            "reads": [summary.opening, summary.coach_note],
            "memory": [{"title": "Forte", "note": s, "tone": "positive"} for s in summary.strengths[:2]],
            "timeline": timeline
        }
        evaluate_js_call(self.window, "updatePostGameSummary", payload)

    def start_lcu_loop(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        while True:
            try:
                self.connector.start()
                break
            except Exception:
                time.sleep(3)

class Api:
    def __init__(self, app: CoacherApp):
        self._app = app

    def notify_ui_ready(self):
        self._app.push_auth_snapshot()
        self._app.sync_ui_game_state()
        if self._app.is_authenticated() and not self._app.lcu_started:
            threading.Thread(target=self._app.start_lcu_loop, daemon=True).start()
            self._app.lcu_started = True

    def get_auth_snapshot(self):
        return self._app.auth_service.snapshot()

    def get_settings_snapshot(self):
        snap = self._app.settings_store.get_all()
        # Safety check: if filters are somehow empty or missing despite defaults
        if not snap.get("category_filters"):
            from core.settings_store import DEFAULT_SETTINGS
            snap["category_filters"] = DEFAULT_SETTINGS["category_filters"]
        snap["voice_catalog"] = voice_catalog_snapshot()
        return snap

    def login_user(self, email, password):
        res = self._app.auth_service.sign_in(email, password)
        if res.get("authenticated") and not self._app.lcu_started:
            threading.Thread(target=self._app.start_lcu_loop, daemon=True).start()
            self._app.lcu_started = True
        self._app.push_auth_snapshot()
        return res
    
    def register_user(self, email, password, display_name):
        res = self._app.auth_service.sign_up(email, password, display_name)
        self._app.push_auth_snapshot()
        return res

    def logout_user(self):
        res = self._app.auth_service.sign_out()
        self._app.push_auth_snapshot()
        return res

    # --- Settings Bridge ---
    def set_volume(self, value): 
        self._app.settings_store.update("volume", value)
        self._app.sync_settings()
    def toggle_voice(self, state): 
        self._app.settings_store.update("voice_enabled", state)
        self._app.sync_settings()
    def toggle_objectives(self, state): 
        self._app.settings_store.update("objectives_enabled", state)
        self._app.sync_settings()
    def toggle_hardcore(self, state): 
        self._app.settings_store.update("hardcore_enabled", state)
        self._app.sync_settings()
    def set_voice_preset(self, preset): 
        self._app.settings_store.update("voice_preset", normalize_voice_preset(preset))
        self._app.sync_settings()
    def toggle_solo_focus(self, state): 
        self._app.settings_store.update("solo_focus", state)
        self._app.sync_settings()
    def set_macro_interval(self, val): 
        self._app.settings_store.update("macro_interval", val)
        self._app.sync_settings()
    def set_minimap_interval(self, val): 
        self._app.settings_store.update("minimap_interval", val)
        self._app.sync_settings()
    def set_economy_interval(self, val): 
        self._app.settings_store.update("economy_interval", val)
        self._app.sync_settings()
    def set_item_check_interval(self, val): 
        self._app.settings_store.update("item_check_interval", val)
        self._app.sync_settings()
    def set_farm_threshold(self, val): 
        self._app.settings_store.update("farm_threshold", val)
        self._app.sync_settings()
    def set_vision_threshold(self, val): 
        self._app.settings_store.update("vision_threshold", val)
        self._app.sync_settings()
    def set_voice_personality(self, p): 
        self._app.settings_store.update("voice_personality", normalize_voice_personality(p))
        self._app.sync_settings()
    def set_preferred_champion_pool(self, pool):
        self._app.settings_store.update("preferred_champion_pool", pool)
        self._app.sync_settings()
    def toggle_prioritize_pool_picks(self, state):
        self._app.settings_store.update("prioritize_pool_picks", state)
        self._app.sync_settings()
    
    def set_category_enabled(self, category, state):
        filters = self._app.settings_store.get("category_filters", {})
        filters[category] = state
        self._app.settings_store.update("category_filters", filters)
        self._app.sync_settings()
    
    def set_category_preset(self, preset):
        # Could implement presets logic here
        pass

def set_dpi_aware():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except: pass

def main():
    set_dpi_aware()
    app_instance = CoacherApp()
    api = Api(app_instance)
    
    ui_dir = desktop_ui_dir()
    desktop_entry = ui_dir / "desktop" / "index.html"
    if not desktop_entry.exists():
        raise FileNotFoundError(
            f"Desktop UI não encontrada em {desktop_entry}. Gere o frontend antes de iniciar o app."
        )

    threading.Thread(target=start_ui_server, args=(ui_dir, app_instance.port), daemon=True).start()
    
    app_instance.window = webview.create_window(
        'Coacher - Assistente Inteligente',
        f'http://127.0.0.1:{app_instance.port}/desktop/index.html',
        js_api=api,
        width=1100, height=750,
        background_color='#050508'
    )
    
    app_instance.assistant.callback_log = lambda t, ty="normal", c=None: evaluate_js_call(app_instance.window, "playTTSUpdate", t, ty, c)
    app_instance.scraper = EnemyScraper(app_instance.assistant, app_instance.window)
    
    webview.start(debug=False, private_mode=True)

if __name__ == "__main__":
    main()
