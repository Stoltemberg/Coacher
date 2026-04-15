import webview
import threading
import asyncio
import os
import sys
import random

# Core & LCU
from lcu_driver import Connector
from core.live_data import LiveGameAPI
from core.assistant import VoiceAssistant
from core.coach_brain import CoachBrain
from core.champ_select import ChampSelectCoach
from core.scraper import EnemyScraper

connector = Connector()
window = None
assistant = VoiceAssistant()
coach = CoachBrain(assistant)
draft_coach = ChampSelectCoach(assistant)
scraper = None
live_api = None

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
            if window:
                window.evaluate_js(f'addAILog("Detectado evento: {name} no mapa", "normal")')
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
        print(f"[Backend] Voz: {'Ligada' if state else 'Desligada'}")

    def toggle_objectives(self, state):
        self.objectives_enabled = state
        print(f"[Backend] Alertas de Objetivos: {'Ligado' if state else 'Desligado'}")

    def toggle_hardcore(self, state):
        self.hardcore_enabled = state
        coach.hardcore_enabled = state
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
        window.evaluate_js('updateGameState("Lobby", "Invocador")')
        window.evaluate_js('addAILog("Sincronizado com o Cliente do League.", "system")')
        assistant.say(random.choice([
            "Hahaha... até que enfim. Pensei que não ia arrastar pros cara. Bora meu cuzans!",
            "Coacher online paizão! Bora dar aula pra esses caras.",
            "Minerva na área! Pode dar o play que eu tô só anotando esses erro."
        ]), "positive")

@connector.close
async def disconnect(connection):
    print('[LCU] Desconectado do League Client')
    if window:
        window.evaluate_js('updateGameState("Aguardando League...")')
        window.evaluate_js('addAILog("O Cliente do League foi fechado.", "urgent")')
        if live_api:
            live_api.stop()

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
    
    if not window:
        return
        
    if phase == "ChampSelect":
        draft_coach.reset()
        window.evaluate_js('updateGameState("Seleção de Campeões")')
        window.evaluate_js('addAILog("Fase de Draft. Analisando picks inimigos...", "system")')
        assistant.say(random.choice([
            "Hahaha... Bora pro draft seu porra! O olho do pai tá brilhando aqui nas comp inimiga. Loca logo esse boneco direito.",
            "Vamo de seleção! Vamos caçar esses mortos de fome pelos picks... escuta as call que o gap tá garantido.",
            "Seleção rolando papai! Qualquer resto de aborto que os cara locar lá, eu já vou te cantar a fraqueza mental deles.",
            "Caiu no draft! Puxa o teu boneco aí que eu vou arregaçar o cu deles e garantir seu ponto na moralzinha.",
            "Fase de escolhas! Picka o cãncer de sempre e dexa o jogo vir paizão. Tô na escuta e nós vamos meter bala neles.",
            "Pff... E lá vamos nós pro draft. Pega a porra do boneco que você sabe jogar e vamo moer a esperança desses pangaré no mid game.",
            "Bagulhos taticos rolando na tela de draft. Faz teu esquema aí, muta geral da tua comp que eu cuido das cãncer do lado oposto.",
            "Ai ai... Já arrumou a cadeira? Seleção abriu, não mosca na runa caralho, foca na tela pra não tiltar o time inteiro aos três minutos."
        ]), "neutral")
    elif phase == "InProgress":
        if scraper:
            scraper.reset()
        window.evaluate_js('updateGameState("In Game")')
        window.evaluate_js('addAILog("Partida Iniciada! Assistente ouvindo...", "system")')
        if api.voice_enabled:
            assistant.say(random.choice([
                "Hahaha... Partida começou... agora não tem como chorar no chat. Boa sorte mano, e não inta pelo amor de deus caralho!",
                "Carregou a partida. Bora esmagar as cara deles no gap e dar GG aos quinze minutos. Confia e bate papai!",
                "Hahaha... Mentira caralho! O jogo começou! Deixa os inimigo implorando arrego no All e vamo!",
                "Escuta minhas call. Farma seu imundo de merda, não me dá brecha em erro atoa e bota os maluco pra dormir de cabeça curvada.",
                "E lá vamos nós paizão. Faz teu joguinho limpo, puxa tua wave perfeitinha e arrasta os pontos na brutalidade pura!",
                "Bora pro Rift. Respira fundo, desmutar esses merdas não é opção, segue a risca do Macrogame que a gente fecha isso com as duas mão nas costas.",
                "Entrou no jogo de vez né. Já sabe o papo: gankou você cobra de volta, morreu você amassa no minion pra recuperar. Bora porra!",
                "Pff... Libera o monstro. Os cara lá do outro lado já tão tiltado antes da rota bater na outra, só faz tua parte com força."
            ]), "positive")
            
        # Iniciar polling da Live Client Data
        live_api = LiveGameAPI(handle_live_event)
        live_api.start()
        
    elif phase in ["PreEndOfGame", "EndOfGame"]:
        if live_api:
            live_api.stop()
        window.evaluate_js('updateGameState("Partida Finalizada")')
    elif phase == "Lobby":
        window.evaluate_js('updateGameState("Lobby")')
    else:
        window.evaluate_js(f'updateGameState("{phase}")')

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
    def log_handler(text, type_="normal"):
        if window:
            # Escape strings para JS
            t = text.replace('"', '\\"')
            window.evaluate_js(f'addAILog("{t}", "{type_}")')
            
    assistant.callback_log = log_handler
    scraper = EnemyScraper(assistant, window)

    def on_loaded():
        lcu_thread = threading.Thread(target=start_lcu, daemon=True)
        lcu_thread.start()

    window.events.loaded += on_loaded
    webview.start(debug=False)

if __name__ == '__main__':
    main()
