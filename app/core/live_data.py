import threading
import time
from urllib.parse import urlencode

import requests
import urllib3

# Live Client uses a local self-signed certificate.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LiveGameAPI:
    def __init__(self, callback):
        self.endpoint = "https://127.0.0.1:2999/liveclientdata"
        self.is_running = False
        self.thread = None
        self.callback = callback
        self.last_events_count = 0
        self.poll_rate = 1.0
        self._cycle = 0
        self._first_poll = True

    def _emit_json(self, route, event_name, timeout=1):
        try:
            resp = requests.get(f"{self.endpoint}/{route}", verify=False, timeout=timeout)
            if resp.status_code == 200:
                self.callback(event_name, resp.json())
        except Exception:
            pass

    def _fetch_json(self, route, *, params=None, timeout=1):
        try:
            query = f"?{urlencode(params)}" if params else ""
            resp = requests.get(f"{self.endpoint}/{route}{query}", verify=False, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            return None
        return None

    def _poll_game_data(self):
        while self.is_running:
            self._cycle += 1

            try:
                resp = requests.get(f"{self.endpoint}/eventdata", verify=False, timeout=1)
                if resp.status_code == 200:
                    data = resp.json()
                    events = data.get("Events", [])
                    if len(events) > self.last_events_count:
                        if self._first_poll:
                            self.last_events_count = len(events)
                            self._first_poll = False
                        else:
                            new_events = events[self.last_events_count :]
                            self.last_events_count = len(events)
                            for event in new_events:
                                self.callback("event", event)
                    else:
                        self._first_poll = False
            except Exception:
                pass

            players = self._fetch_json("playerlist")
            if players is not None:
                self.callback("players", players)
                if self._cycle % 2 == 0:
                    summoner_spells = {}
                    for player in players:
                        summoner_name = player.get("summonerName")
                        if not summoner_name:
                            continue
                        payload = self._fetch_json(
                            "playersummonerspells",
                            params={"summonerName": summoner_name},
                            timeout=1,
                        )
                        if payload is not None:
                            summoner_spells[summoner_name] = payload
                    if summoner_spells:
                        self.callback("player_summoner_spells", summoner_spells)
            self._emit_json("activeplayer", "active_player")
            self._emit_json("activeplayerabilities", "active_player_abilities")
            self._emit_json("activeplayerrunes", "active_player_runes")
            self._emit_json("gamestats", "game_stats")

            # Poll the heavier aggregate snapshot less frequently.
            if self._cycle % 3 == 0:
                self._emit_json("allgamedata", "all_game_data", timeout=2)

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
