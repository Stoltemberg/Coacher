import threading
import requests
from bs4 import BeautifulSoup

class EnemyScraper:
    def __init__(self, assistant, window):
        self.assistant = assistant
        self.window = window
        self.scraped_players = set()
        self.region = "br"

    def process_players(self, players_data, active_player_name):
        if not active_player_name or not players_data:
            return

        our_team = "ORDER"
        for p in players_data:
            if p.get("summonerName") == active_player_name:
                our_team = p.get("team")
                break

        for p in players_data:
            team = p.get("team")
            name = p.get("summonerName")
            champion = p.get("championName")

            # Apenas busca do time inimigo e que ainda não foi buscado
            if team != our_team and name and name not in self.scraped_players:
                self.scraped_players.add(name)
                # Dispara a busca em thread separada para não travar o loop
                threading.Thread(target=self._scrape, args=(name, champion), daemon=True).start()

    def _scrape(self, summoner_name, champion_name):
        try:
            # Tratamento de Nomes (Name#TAG vira Name-TAG, espaços viram +)
            url_name = summoner_name.replace('#', '-').replace(' ', '+')
            # LeagueOfGraphs é mais amigável a scraping sem JavaScript agressivo/Cloudflare
            url = f"https://www.leagueofgraphs.com/pt/summoner/{self.region}/{url_name}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=6)
            
            rank = "Desconhecido"
            winrate = "N/A"
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Buscar liga/elo
                league_div = soup.find('div', class_='leagueTier')
                if league_div:
                    # Tira quebras de linha e pega o primeiro texto (ex: Ouro II)
                    rank = league_div.get_text(strip=True).replace("\n", " ").split("LP")[0].strip()

                # Buscar Winrate global (Geralmente no primeiro pie-chart lateral)
                pie_chart = soup.find('div', class_='pie-chart')
                if pie_chart:
                    winrate = pie_chart.get_text(strip=True)

            # Envia diretamente ao javascript da interface
            if self.window:
                # Trata aspas e injeta via JS
                safe_name = summoner_name.replace("'", "\\'")
                safe_champ = champion_name.replace("'", "\\'")
                safe_rank = rank.replace("'", "\\'")
                safe_wr = winrate.replace("'", "\\'")
                
                js_code = f"addPreGameStat('{safe_name}', '{safe_champ}', '{safe_rank}', '{safe_wr}')"
                self.window.evaluate_js(js_code)
                
            # Log falado opcional se o winrate for absurdamente alto ou elo perigoso.
            if "Diamante" in rank or "Mestre" in rank:
                self.assistant.say(f"Atenção grave. Identifiquei que jogador {champion_name} do time adversário é Elo {rank}.")

        except Exception as e:
            print(f"[Scraper] Erro ao buscar {summoner_name}: {e}")

    def reset(self):
        self.scraped_players.clear()
