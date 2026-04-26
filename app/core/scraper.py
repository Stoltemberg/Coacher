import re
import threading
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from core.ui_bridge import evaluate_js_call


def _clean_name(value):
    return str(value or "").split("#")[0].strip()


class EnemyScraper:
    def __init__(self, assistant, window):
        self.assistant = assistant
        self.window = window
        self.scraped_players = set()
        self.cache = {}
        self.region = "br"

    def process_players(self, players_data, active_player_name):
        if not active_player_name or not players_data:
            return

        our_team = "ORDER"
        cleaned_active = _clean_name(active_player_name)
        for player in players_data:
            if _clean_name(player.get("summonerName")) == cleaned_active:
                our_team = player.get("team") or our_team
                break

        for player in players_data:
            team = player.get("team")
            name = str(player.get("summonerName") or "").strip()
            champion = player.get("championName")

            if team != our_team and name and name not in self.scraped_players:
                self.scraped_players.add(name)
                if self.window:
                    evaluate_js_call(
                        self.window,
                        "addPreGameStat",
                        name,
                        champion,
                        "Carregando",
                        "...",
                    )
                threading.Thread(target=self._scrape, args=(name, champion), daemon=True).start()

    def _scrape(self, summoner_name, champion_name):
        try:
            if summoner_name in self.cache:
                rank, winrate = self.cache[summoner_name]
            else:
                url_name = quote(summoner_name.replace("#", "-"), safe="")
                url = f"https://op.gg/lol/summoners/{self.region}/{url_name}"
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    )
                }
                resp = requests.get(url, headers=headers, timeout=8)

                rank = "Indisponivel"
                winrate = "Indisponivel"

                if resp.status_code == 200:
                    rank, winrate = self._parse_opgg_profile(resp.text)

                if rank != "Indisponivel" or winrate != "Indisponivel":
                    self.cache[summoner_name] = (rank, winrate)

            if self.window:
                evaluate_js_call(
                    self.window,
                    "addPreGameStat",
                    summoner_name,
                    champion_name,
                    rank,
                    winrate,
                )

            if any(token in rank.lower() for token in ("diamond", "master", "grandmaster", "challenger")):
                self.assistant.say(
                    f"Atenção. Identifiquei que {champion_name} do time adversário está em {rank}.",
                    "warning",
                    category="draft",
                )

        except Exception as exc:
            print(f"[Scraper] Erro ao buscar {summoner_name}: {exc}")
            if self.window:
                evaluate_js_call(
                    self.window,
                    "addPreGameStat",
                    summoner_name,
                    champion_name,
                    "Indisponivel",
                    "Indisponivel",
                )

    def _parse_opgg_profile(self, html):
        soup = BeautifulSoup(html, "html.parser")
        description = ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag:
            description = str(description_tag.get("content") or "").strip()

        if not description:
            return "Indisponivel", "Indisponivel"

        lowered = description.lower()
        if "unranked" in lowered:
            return "Unranked", "Sem WR"

        rank_match = re.search(
            r"/\s*([A-Za-z]+)\s+(\d)(?:\s+\d+)?\s+\d+\s*LP",
            description,
            flags=re.IGNORECASE,
        )
        wr_match = re.search(
            r"/\s*(\d+)\s*Win\s*(\d+)\s*Lose\s*Win rate\s*(\d+%)",
            description,
            flags=re.IGNORECASE,
        )

        rank = "Indisponivel"
        winrate = "Indisponivel"

        if rank_match:
            tier = rank_match.group(1).capitalize()
            division = rank_match.group(2)
            rank = f"{tier} {division}"

        if wr_match:
            wins = wr_match.group(1)
            losses = wr_match.group(2)
            wr = wr_match.group(3)
            winrate = f"{wr} ({wins}W/{losses}L)"

        return rank, winrate

    def reset(self):
        self.scraped_players.clear()
