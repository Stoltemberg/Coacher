import requests
import time
import urllib3
import threading

# Disable InsecureRequestWarning because Live Game API uses self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LiveGameAPI:
    def __init__(self, callback):
        self.endpoint = "https://127.0.0.1:2999/liveclientdata"
        self.is_running = False
        self.thread = None
        self.callback = callback
        self.last_events_count = 0
        self.poll_rate = 1.0  # Polling mais rápido para a voz reagir logo

    def _poll_game_data(self):
        while self.is_running:
            try:
                # 1. Eventos (Abates, Dragões)
                resp = requests.get(f"{self.endpoint}/eventdata", verify=False, timeout=1)
                if resp.status_code == 200:
                    data = resp.json()
                    events = data.get("Events", [])
                    if len(events) > self.last_events_count:
                        if getattr(self, '_first_poll', True):
                            self.last_events_count = len(events)
                            self._first_poll = False
                        else:
                            new_events = events[self.last_events_count:]
                            self.last_events_count = len(events)
                            for event in new_events:
                                self.callback("event", event)
                    else:
                        self._first_poll = False
            except Exception:
                pass

            try:
                # 2. Player Info e Inventários Inimigos
                resp = requests.get(f"{self.endpoint}/playerlist", verify=False, timeout=1)
                if resp.status_code == 200:
                    players = resp.json()
                    self.callback("players", players)
            except Exception:
                pass

            try:
                # 3. Descobrir quem é o nosso jogador (para saber quando ELE mata ou morre)
                resp = requests.get(f"{self.endpoint}/activeplayer", verify=False, timeout=1)
                if resp.status_code == 200:
                    active = resp.json()
                    self.callback("active_player", active)
            except Exception:
                pass

            try:
                # 4. Tempo do jogo e stats globais para avaliar farm e fase
                resp = requests.get(f"{self.endpoint}/gamestats", verify=False, timeout=1)
                if resp.status_code == 200:
                    stats = resp.json()
                    self.callback("game_stats", stats)
            except Exception:
                pass

            time.sleep(self.poll_rate)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._poll_game_data, daemon=True)
            self.thread.start()
            print("[LiveAPI] Polling iniciado.")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        print("[LiveAPI] Polling parado.")
