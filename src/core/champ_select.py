import threading
import requests

from core.minerva_voice import MinervaVoice

class ChampSelectCoach:
    def __init__(self, assistant, voice=None):
        self.assistant = assistant
        self.voice = voice or MinervaVoice()
        self.last_enemy_picks = set()
        self.champions_map = {} # ID -> Name
        self.my_champ = None
        self.runes_advised = False
        
        # Categorias para análise tática
        self.high_cc_champs = ["Leona", "Nautilus", "Morgana", "Ashe", "Sejuani", "Lissandra", "Amumu", "Maokai", "Thresh"]
        self.assassins = ["Zed", "Talon", "Akali", "Katarina", "Evelynn", "Rengar", "Kha'Zix", "Leblanc", "Fizz", "Qiyana"]
        self.tanks = ["Malphite", "Ornn", "Sion", "Mundo", "Rammus", "Cho'Gath", "Zac"]

        self._load_champions_async()

    def _schedule_say(self, delay, text, event_type="neutral"):
        threading.Timer(delay, lambda: self.assistant.say(text, event_type, category="draft")).start()

    def _load_champions_async(self):
        def fetch():
            try:
                resp = requests.get("https://ddragon.leagueoflegends.com/cdn/14.6.1/data/pt_BR/champion.json")
                if resp.status_code == 200:
                    data = resp.json()["data"]
                    for name, info in data.items():
                        self.champions_map[int(info["key"])] = name
            except Exception as e:
                print(f"[Draft] Erro ao carregar campeões: {e}")
                
        threading.Thread(target=fetch, daemon=True).start()

    def get_champion_name(self, champ_id):
        return self.champions_map.get(champ_id, f"Campeão {champ_id}")

    def process_session(self, session_data):
        if not session_data:
            return
            
        my_team = session_data.get("myTeam", [])
        enemy_team = session_data.get("theirTeam", [])
        local_cell_id = session_data.get("localPlayerCellId")
        
        # Descobrir qual o nosso campeão atual (Hover ou Lock)
        my_current_champ_id = None
        for player in my_team:
            if player.get("cellId") == local_cell_id:
                my_current_champ_id = player.get("championId")
                break
                
        # Listas ativas
        current_enemy_names = []
        current_enemy_picks = set()

        for player in enemy_team:
            cid = player.get("championId", 0)
            if cid > 0:
                current_enemy_picks.add(cid)
                name = self.get_champion_name(cid)
                current_enemy_names.append(name)
                
        # Verificar se os inimigos travaram algum campeão novo (Apenas Dicas de Counter)
        new_picks = current_enemy_picks - self.last_enemy_picks
        for champ_id in new_picks:
            name = self.get_champion_name(champ_id)
            if name != f"Campeão {champ_id}":
                self.assistant.say(self.voice.draft_enemy_locked(name), category="draft")
                counter_tip = self.voice.draft_counter_tip(name)
                if counter_tip:
                    self._schedule_say(0.8, counter_tip)
                    
        self.last_enemy_picks = current_enemy_picks
        
        # Análise de Runas e Feitiços para NOSSO CAMPEÃO
        if my_current_champ_id and my_current_champ_id > 0 and not self.runes_advised:
            my_champ_name = self.get_champion_name(my_current_champ_id)
            if my_champ_name != self.my_champ:
                self.my_champ = my_champ_name
                self.runes_advised = True # Só falar uma vez por escolha
                
                self.assistant.say(self.voice.draft_pick_confirmed(my_champ_name), category="draft")
                
                # Heurística Tática Inimiga
                cc_count = sum(1 for c in current_enemy_names if c in self.high_cc_champs)
                assassin_count = sum(1 for c in current_enemy_names if c in self.assassins)
                tank_count = sum(1 for c in current_enemy_names if c in self.tanks)
                
                if cc_count >= 2:
                    plan_key = "high_cc"
                
                elif assassin_count >= 2 or (assassin_count == 1 and my_champ_name in ["Ashe", "Jinx", "Vayne", "Caitlyn", "Kog'Maw"]):
                    plan_key = "assassins"
                
                elif tank_count >= 2:
                    plan_key = "tanks"
                
                else:
                    plan_key = "standard"

                self._schedule_say(1.8, self.voice.draft_comp_plan(plan_key, my_champ_name))


    def reset(self):
        self.last_enemy_picks.clear()
        self.my_champ = None
        self.runes_advised = False
