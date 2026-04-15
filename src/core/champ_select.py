import threading
import time
import requests
import random

class ChampSelectCoach:
    def __init__(self, assistant):
        self.assistant = assistant
        self.last_enemy_picks = set()
        self.champions_map = {} # ID -> Name
        self.my_champ = None
        self.runes_advised = False
        
        # Heurísticas de Draft Estáticas Iniciais (serão integradas ao scraper na Fase 3 depois)
        self.matchup_tips = {
            "Zed": "Ó, o cara locou Zed lá. Pega um mago que tenha clear wave bom ou mete um Zhonyas logo de cara, senão ele vai te deletar debaixo da torre.",
            "Yasuo": "Yasuo inimigo. Esse maluco vai ficar dashando igual um macaco na wave. Pega algo tipo Pantheon ou Renekton e amassa a cabeça dele na rota.",
            "Darius": "O cara pegou Darius. Esquece lutar colado com ele, tu vai ser jantado. Joga de Teemo ou Vayne e faz ele chorar pro gank.",
            "Master Yi": "Master Yi na jungle dos caras. Avisa o teu time pra não esquecer de guardar stun pra ele. Se ele entrar solto na backline é open mid na hora.",
            "Blitzcrank": "Fica ligado que tem Blitzcrank. Não bota a cara se não tiver wave, ele vai pescar teu suporte inteiro. Pega um Ezreal pra fugir do puxão fácil.",
            "Vayne": "Apareceu uma Vayne lá. Boneco nojento, foca ela de primeira antes de qualquer tanque senão ela derrete a comp toda de vocês."
        }
        
        # Categorias para análise tática
        self.high_cc_champs = ["Leona", "Nautilus", "Morgana", "Ashe", "Sejuani", "Lissandra", "Amumu", "Maokai", "Thresh"]
        self.assassins = ["Zed", "Talon", "Akali", "Katarina", "Evelynn", "Rengar", "Kha'Zix", "Leblanc", "Fizz", "Qiyana"]
        self.tanks = ["Malphite", "Ornn", "Sion", "Mundo", "Rammus", "Cho'Gath", "Zac"]

        self._load_champions_async()

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
                self.assistant.say(random.choice([
                    f"Eles locaram {name}.",
                    f"Putz, enfiaram um {name} daquele lado.",
                    f"Confirmação lá pros inimigo: é {name} na tela."
                ]))
                if name in self.matchup_tips:
                    time.sleep(1)
                    self.assistant.say(self.matchup_tips[name])
                    
        self.last_enemy_picks = current_enemy_picks
        
        # Análise de Runas e Feitiços para NOSSO CAMPEÃO
        if my_current_champ_id and my_current_champ_id > 0 and not self.runes_advised:
            my_champ_name = self.get_champion_name(my_current_champ_id)
            if my_champ_name != self.my_champ:
                self.my_champ = my_champ_name
                self.runes_advised = True # Só falar uma vez por escolha
                
                self.assistant.say(random.choice([
                    f"Aí sim, botou {my_champ_name} na tela... Dá um tempo que eu vou dar o papo dos melhores mato pra fugir deles.",
                    f"Maneiro, você cravou {my_champ_name}. Vou passar a visão do que tu precisa fazer com as tuas runas pra deitar esses cara.",
                    f"Boa escolha. Já que meteu {my_champ_name}, escuta a dica quente sobre a comp que tá do outro lado."
                ]))
                time.sleep(3.5)
                
                # Heurística Tática Inimiga
                cc_count = sum(1 for c in current_enemy_names if c in self.high_cc_champs)
                assassin_count = sum(1 for c in current_enemy_names if c in self.assassins)
                tank_count = sum(1 for c in current_enemy_names if c in self.tanks)
                
                if cc_count >= 2:
                    self.assistant.say(random.choice([
                        "Maluco, a comp deles tá entupida de controle de grupo. Bota Purificar e pega runa de tenacidade senão você vai jogar o jogo congelado.",
                        "Cara, tem stun do outro lado que não acaba mais. Vai ser uma tristeza se você não usar a runa de tenacidade. Equipa ela logo."
                    ]))
                
                elif assassin_count >= 2 or (assassin_count == 1 and my_champ_name in ["Ashe", "Jinx", "Vayne", "Caitlyn", "Kog'Maw"]):
                    self.assistant.say(random.choice([
                        "Presta bem atenção... tem assassinos demais no time deles e tua batata tá assando. Põe um exaustão e Osso Revestido agora pra você não tomar hit kill.",
                        "Eles pegaram uns boneco assassino chato lá. Se tu não colocar Exaustão como feitiço e pegar umas runinha defensiva, tá na loss, confia."
                    ]))
                
                elif tank_count >= 2:
                    self.assistant.say(random.choice([
                        "Nossa senhora, a comp dos malucos é puro tanque da pesada. Arranca o conquistador do baú e já prepara que tu vai ter que bater neles por meia hora seguida.",
                        "Tem dois boneco insuportável de tanque neles. Foca em runa que dá dano estendido e derrete armor que senão eles te amassam no final de tudo."
                    ]))
                
                else:
                    self.assistant.say(random.choice([
                        "A composição ali tá bem feijão com arroz, honestamente... Fica no feitiço padrão e mete a runa que achar melhor, joga na maciota que tá fácil.",
                        "Timezinho inimigo padrão sem nada muito fora da curva. Segue o teu jogo com Flash que não tem muito segredo hoje não."
                    ]))


    def reset(self):
        self.last_enemy_picks.clear()
        self.my_champ = None
        self.runes_advised = False
