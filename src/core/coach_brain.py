import random
import time
import threading

class CoachBrain:
    def __init__(self, assistant):
        self.assistant = assistant
        self.active_player_name = None
        
    def map_pve_name(self, raw_killer):
        lk = raw_killer.lower()
        if "turret" in lk or "torder" in lk: return "uma Torre"
        if "minion" in lk: return "uma Tropa"
        if "sru_" in lk: return "os Monstros da Selva"
        return "o cenário"
        self.player_to_champ = {} 
        self.player_to_team = {}
        self.our_team = "ORDER"
        
        self.game_time = 0.0
        self.current_assists = -1
        self.last_farm_eval = 0
        self.lane_matchup_announced = False
        self.my_position = ""
        self.hardcore_enabled = True
        
        self.ally_drags = 0
        self.enemy_drags = 0
        
        self.armor_ids = [3075, 3143, 3110, 6660, 3068, 6665, 3193, 3026]
        self.mr_ids = [3065, 4401, 3155, 3156, 3001, 3118]
        self.anti_heal_ids = [3123, 3033, 3165, 3916, 6609, 3076, 3075]

        self.last_item_check = 0
        self.advised_items = set()

        self.timer_thread = threading.Thread(target=self._minimap_timer, daemon=True)
        self.timer_thread.start()
        
        self.macro_thread = threading.Thread(target=self._macro_timer, daemon=True)
        self.macro_thread.start()

    def _macro_timer(self):
        while True:
            time.sleep(200)
            self.assistant.say(random.choice([
                "Dica do paizão: Puxa a wave direito antes de ir base. Não deixa teu farm e tua exp morrerem pra torre do nada.",
                "Call de macrogame pra vocês: Priorizem derrubar os bagulhos de graça. Uma torre levada no tempo livre ganha mais mapa que correr atrás de suporte isolado.",
                "Visão ganha jogo moçada. Sobrou 75 de gold na base? Compra e bota uma Ward de controle no rio pra não ficarmos cego.",
                "Tempo é dinheiro. Se abateu o inimigo e não tá perto da torre dele, volta na base, gasta o ouro e volta forte pra cacete.",
                "Sequestro de mente rápido: Sabe onde tá o jungle inimigo agora? Se não fizer a menor ideia, dá uma segurada nos teus avanços aí na rota."
            ]))

    def _minimap_timer(self):
        while True:
            time.sleep(150)
            self.assistant.say(random.choice([
                "Mlk, tem mapa aí na tela sabia? Dá uma pescada na selva deles pra achar o Jungle antes dele te prender na parede.",
                "E as wards animal? Olha o porra desse minimapa pra prever gank. Depois toma ik no susto e põe culpa no time.",
                "Pô paizão, olha as beiradas da tela um segundo caralho! Quer tomar gank do caçador deles atoa sem ver de onde o cara vem?",
                "Na moralzinha, acha o porra do caçador deles no mapa cara. Se tu for gankado de graça agora é de uma asneza inacreditável.",
                "Pinca o mato aí caralho e puxa a rota direito. Se o jungle deles subir, engole ele de porrada ou sai de fininho, recua e cede.",
                "Alô?! Passou a call de gank miado? Fica no radar desse caçadorzinho escroto senao a chinela vai cantar na sua lane papai.",
                "Meu amigo, cadê o caçador inimigo cacete? Foca no minimapa antes que tu vire estatística de abate de graça por burrice.",
                "Previsão do tempo hoje truta: Chuva de gank rolando nas tuas costas se tu continuar cego. Ward nessas moitas do rio caralho!",
                "Visão limpa! Tem cara de gank vindo na tua direção se pá, solta de bater na torre igual doido um segundo e olha o canto do mapa.",
                "Sequestro de atencão! Bota tua ward vermelha antes de estender no mapa debaixo da perna da torre deles pow, caçador ta na bota."
            ]))

    def update_active_player(self, data):
        if "summonerName" in data and not self.active_player_name:
            raw_name = data["summonerName"]
            self.active_player_name = raw_name.split('#')[0].strip()
            self.assistant.say(random.choice([
                "Tudo certo, já identifiquei sua conta. Vamos cair pra dentro dessa partida.",
                "Beleza, carreguei seus dados. Fica tranquilo que eu vou marcando as calls aqui.",
                "Sistema redondo. Pode jogar solto que eu tô acompanhando tudo por trás."
            ]))

    def update_game_stats(self, data):
        self.game_time = data.get("gameTime", 0.0)

    def update_players(self, players_data):
        if not self.active_player_name:
            return

        for p in players_data:
            s_name = p.get("summonerName", "").split('#')[0].strip()
            champ = p.get("championName", "Alguém")
            p_team = p.get("team", "ORDER")
            
            self.player_to_champ[s_name] = champ
            self.player_to_team[s_name] = p_team
            
            if s_name == self.active_player_name:
                self.our_team = p_team
                self.my_position = p.get("position", "")
                
                scores = p.get("scores", {})
                assists = scores.get("assists", 0)
                cs = scores.get("creepScore", 0)
                wards = scores.get("wardScore", 0.0)
                
                if self.current_assists == -1:
                    self.current_assists = assists
                elif assists > self.current_assists:
                    self.current_assists = assists
                    self.assistant.say(random.choice([
                        "Hahaha... Boa assistência paizão. Trabalho em equipe puro, puxaram e tu cravou na ajuda.",
                        "Participação limpa! Abate rendeu pro time e tu pingou a tua faturada ali.",
                        "Hahaha, é o passe do mestre. Deu a assistência perfeita na orelha do inimigo, gg."
                    ]), "positive")

                minutes = self.game_time / 60.0
                
                # Matchup Call no primeiro minuto ou segundo
                if not self.lane_matchup_announced and self.game_time > 80 and self.my_position and self.my_position != "NONE":
                    for e in players_data:
                        if e.get("team") != self.our_team and e.get("position") == self.my_position:
                            enemy_nick = e.get("summonerName", "").split('#')[0].strip()
                            self.assistant.say(random.choice([
                                f"Fase de Rota ativa! Teu confronto direto ali na cara é o {enemy_nick}. Cuidado com a passiva dele e não toma poke atoa.",
                                f"Partida rodando. Tu tá de frente com {enemy_nick}. Puxa a wave pro teu lado se não aguentar a troca franca no lvl 2.",
                                f"Pff... teu espelho lá de posição é o {enemy_nick}. Foca o teu farm, usa o controle de grupo com sabedoria que a gente esmaga ele cedo."
                            ]), "neutral")
                            self.lane_matchup_announced = True

                # Farm / Vision Evaluation a cada 5 Minutos (Apenas no Modo Hardcore)
                if self.hardcore_enabled and self.game_time > 300 and (self.game_time - self.last_farm_eval) > 300:
                    self.last_farm_eval = self.game_time
                    expected_cs = minutes * 6.5
                    
                    if cs < (expected_cs * 0.6):
                        self.assistant.say(random.choice([
                            f"Ai ai... pelo amor de deus mano, tu cravou só {cs} de farm em {int(minutes)} minutos de jogo. Bate em minion cara, tá tiltado?!",
                            f"Pff... Irmão, volta a atenção pra tua tela. Teu CS tá ridículo de baixo, {cs} minions só? Esquece caçar solado de abate e vai bater em fazenda caralho.",
                            f"Se tu não farmar tu não compra os itens de poder. Esse farm de {cs} CS em {int(minutes)} minutos é taxa de bronze frito... Foca nos last hit animal!"
                        ]), "negative")
                    elif cs > expected_cs:
                        self.assistant.say(random.choice([
                            f"Hahaha, farmando liso ein! Teu CS tá lindo, cravou {cs} minions limpos na conta. Mantém isso pra esmagar eles de gold.",
                            f"Papo reto, farm perfeito. {cs} creeps em {int(minutes)} min. Continua controlando a wave igual high elo que o jogo vem na mão.",
                            f"Tá isolado na riqueza, {cs} minions mortos já. Dinheiro na conta paizão, volta base e quebra os itens!"
                        ]), "positive")
                    
                    # Vision Check pros avançados
                    if minutes >= 10 and wards < 5:
                        self.assistant.say(random.choice([
                            f"Pff... E olha esse placar bizarro da tua partida: {wards} Wards no jogo todo?! Literalmente jogando cego. Compra Controle cara!",
                            f"Ai ai, mano do céu, tu quase não plantou ward até agora da base. Usa tuas lentes e vigia gank senao toma surpresa amarga."
                        ]), "negative")
        
        current_time = time.time()
        if current_time - self.last_item_check > 20: 
            self.last_item_check = current_time
            
            for p in players_data:
                s_name = p.get("summonerName", "").split('#')[0].strip()
                if p.get("team") != self.our_team:
                    items = [item.get("itemID", 0) for item in p.get("items", [])]
                    p_nick = p.get("summonerName", "").split('#')[0].strip()
                    
                    has_armor = any(i in self.armor_ids for i in items)
                    has_mr = any(i in self.mr_ids for i in items)
                    has_anti_heal = any(i in self.anti_heal_ids for i in items)
                    
                    if has_armor and "armor_pen" not in self.advised_items:
                        self.assistant.say(random.choice([
                            f"Ó, fica ligado. O {p_nick} já fechou armadura pesada. Começa a pensar em penetração física pro teu próximo item.",
                            f"Aviso de build aqui: o {p_nick} botou tanqueza na frente. Rancor do Serylda ou lembrete mortal vão ser bem úteis daqui pra frente.",
                            f"Pff... Dá um tab aí rapidinho. O {p_nick} tá puro armor. Não mosca com build seca, você vai precisar penetrar essa proteção.",
                            f"Atenção nas lutas: {p_nick} completou item forte de armadura. Ajusta a build assim que voltar pra base.",
                            f"Cara, o {p_nick} bufou na armadura agora. Prioriza uma penetração física logo pra não perder o dano nela."
                        ]), "negative")
                        self.advised_items.add("armor_pen")
                        return
                        
                    if has_mr and "magic_pen" not in self.advised_items:
                        self.assistant.say(random.choice([
                            f"Proteção mágica detectada lá. O {p_nick} fechou resistência. Cajado do Vazio vai ter que entrar na tua lista.",
                            f"Fica esperto: o {p_nick} buildou bastante MR. Você que dá dano mágico vai ter que contornar isso com penetração.",
                            f"Atenção no {p_nick}! Tá segurando muito o dano mágico com item de vida e resistência. Ajusta na loja depois.",
                            f"Ó a bad news: {p_nick} fez escudo anti-magia forte. Uma ampola ou cajado mágico vai curar isso rapidinho.",
                            f"MR pesada rolando do lado deles com o {p_nick}. Esquece lutar se tu não tiver penetração mágica engatilhada."
                        ]), "negative")
                        self.advised_items.add("magic_pen")
                        return

                    if has_anti_heal and "anti_heal" not in self.advised_items:
                        self.assistant.say(random.choice([
                            f"Importante: as curas não vão te salvar mais fácil não, o {p_nick} comprou corta-cura. Joga mais safe nessas lutas.",
                            f"Atenção na build perigosa deles: o {p_nick} fez corta-cura. O teu vampirismo vai cair pela metade nessas trocas longas.",
                            f"Cara do céu, fica ligado. O {p_nick} tá com corta-cura na não. Evita estender luta se tu depende só de life steal.",
                            f"Aviso pra todo mundo: {p_nick} tá aplicando redução de cura. Suporte de heal vai sofrer nas costas dele agora.",
                            f"O bagulho ficou sério. {p_nick} ativou corta-cura nas compras. Presta muita atenção redobrada antes de forçar duelo franco."
                        ]), "negative")
                        self.advised_items.add("anti_heal")
                        return

    def process_event(self, event):
        name = event.get("EventName")
        
        if name == "ChampionKill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            victim = event.get("VictimName", "").split('#')[0].strip()
            
            killer_champ = self.player_to_champ.get(killer, killer)
            victim_champ = self.player_to_champ.get(victim, victim)
            
            if killer == self.active_player_name:
                self.assistant.say(random.choice([
                    f"Aí sim, boa caralho! Excelente jogada em cima do {victim}. Pune o erro desse cara de rato.",
                    f"Hahaha, mentira caralho! Mandou o {victim} pro chuveiro de base mais cedo. Empurra essa porra de wave aí pra punir de vez.",
                    f"Isso aí porra... jogou o fino nessa briga. Abateu o {victim} na malandragem máxima. Mantém esse ritmo absurdo.",
                    f"Nossa senhora, que gap! O {victim} vacilou e pagou o preço salgado. Clica que o bagulho tá doido a nosso favor.",
                    f"Pegou mais um na conta caralho! Abate garantido no {victim}. Limpa a visão e sai fora tranquilão.",
                    f"Mentira! Estilhaçou a cara do {victim} na porrada. Continua o massacre sem dó paizão.",
                    f"Ai cê falou a minha língua! {victim} foi engolido na técnica. Quebra a moral desse bosta agora no all.",
                    f"Lindo de ver mano. Macetou o tal do {victim} lindamente. Manda ele chupar o dedo no chat."
                ]), "positive")
            
            elif victim == self.active_player_name:
                # Checa se morreu por PVE (Torre, Tropas, Selva) quando o killer não for um Invocador Player
                if not killer or killer not in self.player_to_champ:
                    self.assistant.say(random.choice([
                        "Ai ai... morreu pra ambiente? Torre? Toma cuidado com essas derrapadas de graça, pelo amor.",
                        "Putz. Solado pro PvE na tranquilidade... Foca na partida que esse erro aí foi bizarro.",
                        "Pff, foi executado cara? Assim você entrega objetivo de bandeja pros caras. Joga seguro.",
                        "Nossa senhora, falhou rude agora. Morrer pro mapa não dá... presta atenção e limpa a mente.",
                        "Ai deu ruim pesado. Esquece essa morte patética pra torre e vamo voltar pro jogo, foco total."
                    ]), "negative")
                else:
                    self.assistant.say(random.choice([
                        f"Putz... aí cagou no pau. Foi solado pelo {killer}. Cara, recua o cu na torre e foca no farm pra respirar.",
                        f"Mano, que asneza foi essa? Entregou ouro limpo pro {killer} de novo caralho. Fica numa posição segura porra.",
                        f"Nossa senhora, olha o gap imenso aí. O {killer} capitalizou certinho no teu avanço burro. Vai com calma cacete.",
                        f"Deu mole pra caralho. Morrer pro pangaré do {killer} é de foder. Limpa o choro e joga recuado agora.",
                        f"Pff, que decepção nessa luta hein... o {killer} te arregaçou fácil. Tu tá mamando pro inimigo cara, respira antes de brigar.",
                        f"Mentira caralho! Tu apanhou de {killer} mesmo? Esquece tua build de dano e faz alguma defesa que cê tá parecendo um cone.",
                        f"Bagulho ta feio pro teu lado. O {killer} tá esfregando a sua cara no asfalto paizão. Joga no erro dele e para de forçar play."
                    ]), "negative")
            
            else:
                if killer and victim:
                    is_victim_ally = self.player_to_team.get(victim) == self.our_team
                    
                    if not killer or killer not in self.player_to_champ:
                        # Morreu pra PVE
                        pve = self.map_pve_name(killer)
                        if is_victim_ally:
                            self.assistant.say(random.choice([
                                f"Ai ai... o cone do {victim} abriu pra {pve}. Nossa senhora.",
                                f"Pequena bad news ali. Nosso aliado {victim} se matou pra {pve}.",
                                f"O frouxo do {victim} foi solado por {pve}. Meu deus..."
                            ]), "negative")
                        else:
                            self.assistant.say(random.choice([
                                f"Hahaha... O pangaré inimigo lá se matou pra {pve}.",
                                f"Boa! {victim} suicidou no ambiente pra {pve}. Ouro no lixo.",
                                f"Um a menos lá deles. Passou vergonha pro {pve} e foi de base."
                            ]), "positive")
                    else:
                        if is_victim_ally:
                            self.assistant.say(random.choice([
                                f"Fudeu ali, nosso companheiro {victim} morreu pro {killer}.",
                                f"Nossa senhora, o pangaré do {victim} tomou um gap inacreditável e se lascou pesado por {killer}.",
                                f"Pff, foi de base... o frouxo do {victim} apanhou rude do {killer}.",
                                f"E a janta não para! {killer} macetando o fragilzinho de {victim} no meio da cara.",
                                f"Puta sacanagem... o cara de rato do {victim} foi destruído por {killer} numa porrada de cego.",
                                f"Ai ai, Mentira caralho! {victim} já tá mamando na lane phase pro {killer}. Que nojo da play desse aliado.",
                                f"Bagulho tá doido pros lados de lá. O teu aliado {victim} acabou de ser esmagado perante {killer}."
                            ]), "negative")
                        else:
                            self.assistant.say(random.choice([
                                f"Hahaha, Aí sim! O {killer} esbagaçou o {victim} no mapa.",
                                f"Boa caralho! O fragilzinho do {victim} morreu pro nosso time na mão do {killer}.",
                                f"Um a menos pra eles. O {victim} tomou muito gap pro nosso {killer} e rodou.",
                                f"Menos um do lado de lá, o {victim} já tá mamando pra cacete pro {killer}.",
                                f"Lindo abate do {killer} pra cima do doente do {victim}!"
                            ]), "positive")
                        
        elif name == "FirstBlood":
             recipient = event.get("Recipient", "")
             self.assistant.say(random.choice([
                 "Opa, First Blood porra! O sangue rolou cedo pra caralho... Já se preparam aí que a tampa foi aberta e o bagulho tá doido.",
                 "Hahaha, mentira caralho! First Blood cravado já! Bora punir o resto do mapa e engolir eles.",
                 "Primeiro abate pro chão papai. Segura essa emoção fudida e usa a vantagem pra alastrar no mapa.",
                 "Nossa senhora, First blood já derramado no Rift! Presta atencao mano, quem errar agora vai por ralo abaixo na pressao."
             ]), "positive")
                
        elif name == "Multikill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            kill_streak = event.get("KillStreak", 2)
            killer_champ = self.player_to_champ.get(killer, killer)
            
            if killer == self.active_player_name:
                if kill_streak == 2:
                    self.assistant.say(random.choice([
                        "Hahaha, aí sim porra, double kill amassado! Continua acelerando que os cara tão mamando.",
                        "Dobradinha na conta caralho! Pegou dois, foca no resto e dita o ritmo.",
                        "Mentira! Double kill merecido paizão... A malandragem tá em dia, joga muito.",
                        "Lindo double kill! Mandou dois pangarés de ralo. Segue punindo eles.",
                        "Puta merda, limpou dois da play já. Bagulho tá doido pro teu lado!"
                    ]), "positive")
                elif kill_streak == 3:
                    self.assistant.say(random.choice([
                        "Nossa senhora, triple kill já tá no bolso! Tá punindo demais, engole o resto caralho!",
                        "Hahaha! Três mano! Triple kill absurdo! Essa fight já virou bagunça tua.",
                        "Triplo abate cabreiro irmão! Estão pedindo penico, não clica de jeito nenhum.",
                        "Meu Deus amado, sobrou nem farelo! Triple play impecável e macetada nas costas deles.",
                        "Pegou o Terceiro! Mentira caralho... Triple kill fudido pra arrancar o mental deles."
                    ]), "positive")
                elif kill_streak == 4:
                    self.assistant.say(random.choice([
                        "Nossa! Quadra kill, maluco!! Puxa o último capenga se não tú vai tiltar de não pegar o penta!",
                        "Mentira, mentira, mentira... Quadra kill lindo caralho! A luta é nossa, cata o último fujão pelo rabo!",
                        "Quadra kill de livro porra! Ousado e agressivo! Foca toda a tua alma nesse penta agora!",
                        "Quatros limpos de base! Cara do ceu não alivia pro quinto pangaré de jeito nenhum...",
                        "Hahaha, Mano se tu não buscar esse penta tu é maluco! Quadra kill já encaçacado paizão!"
                    ]), "positive")
                elif kill_streak >= 5:
                    self.assistant.say(random.choice([
                        "PUTA QUE PARIU, É PENTA KILL! MEU DEUS DO CÉU, MENTIRA CARALHO! Amassou essa cambada de inútil sozinho!",
                        "PENTA KILL MOLEQUE! Nossa senhora, limpou a rinha inteira de uma vez. Manda os cara dar FF no chat agora!",
                        "Hahaha, maluco... É PENTA! Olha o estrago que tu fez, os cinco mamaram de bico nas tuas skill!",
                        "Eu não acredito, completou o penta kill caralho! Você tá jogando o fino do fino hoje, quebra esses otário!",
                        "ISSO AÍ PORRA! Penta kill consolidado e carimbado na moleira deles. Bagulho tá nivel abissal!"
                    ]), "positive")
            else:
                if kill_streak == 2:
                    self.assistant.say(random.choice([
                        f"Putz, o pangaré do {killer} meteu um double kill ali no canto. Presta atenção pro vagabundo não bufar de ouro.",
                        f"Nossa senhora, double do {killer}. Começa a focar nele senão a bola de neve vai ser nojenta.",
                        f"Pff, leva na maciota e recua a porra da wave que o {killer} faturou duplo agora mesmo. Não dá ousadia atoa."
                    ]), "negative")
                elif kill_streak >= 3:
                    self.assistant.say(random.choice([
                        f"Mano do céu truta. Cuidado. O bagulho escalou pesado, {killer} já tá num multi kill de {kill_streak}! Fudou tudo.",
                        f"Mentira caralho! O {killer} tá estourando nosso time que nem água com {kill_streak} abates seguidos. Agrupa essa bosta.",
                        f"Ai ai, cacete que perigo iminente. O cara de rato do {killer} pegou {kill_streak} kills limpos. Não bate de frente de jeito nenhum isolado."
                    ]), "negative")

        elif name == "DragonKill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            raw_dragon = event.get("DragonType", "Dragão").replace("Dragon", "")
            
            # Mapeamento pra PT-BR com gírias
            dragon_map = {
                "Fire": "Infernal", "Earth": "da Montanha", "Water": "do Oceano", 
                "Air": "das Nuvens", "Hextech": "Hextec", "Chemtech": "Quimtec", "Elder": "Ancião"
            }
            dragon_pt = dragon_map.get(raw_dragon, raw_dragon)
            killer_champ = self.player_to_champ.get(killer, killer)
            
            # Contabilizando pro Ponto de Alma
            team = self.player_to_team.get(killer, "UNKNOWN")
            is_ally = (team == self.our_team)
            
            if is_ally:
                self.ally_drags += 1
                drags = self.ally_drags
            else:
                self.enemy_drags += 1
                drags = self.enemy_drags
                
            alliance_text = "Nós" if is_ally else "O Inimigo"
            
            if dragon_pt == "Ancião":
                if is_ally:
                    self.assistant.say("Meu amigo!!! O Dragão Ancião tá na nossa mão pelo amor de deus! Luta e buffa as execução de HK lá, o jogo acabou!", "positive")
                else:
                    self.assistant.say("Ai ai... CORRE CARALHO. Os caras fizeram o Dragão Ancião e tão com buff de execução de hit kill. Fica debaixo da torre!", "negative")
            else:
                e_type = "positive" if is_ally else "negative"
                if drags == 3:
                    self.assistant.say(random.choice([
                        f"Atenção gigante agora. {alliance_text} fizemos o Dragão {dragon_pt} e tamos no ponto de ALMA! O próximo dragão define a porra do mapa.",
                        f"Ó o Dragão {dragon_pt} na conta do {killer}. Ficamos a 3 de 4 agora papai. Ponto de ALMA ativado... o próximo drag é vida ou morte pra partida."
                    ]), e_type)
                elif drags == 4:
                    self.assistant.say(random.choice([
                        f"ALMA DO DRAGÃO {dragon_pt} DECRETADA! {alliance_text} estraçalharam as runas neutradas de vez. GG absurdo no rio!",
                        f"Deu a Alma do dragão {dragon_pt}. O bônus tá massivo permanentemente. Aproveitar agora que esse game não vira mais de jeito nenhum."
                    ]), e_type)
                else:
                    self.assistant.say(random.choice([
                        f"Fica ligado nas runas neutras. Um Dragão {dragon_pt} escapou pra conta do {killer}. Já são {drags} deles da equipe dele.",
                        f"Mais um do {dragon_pt} garantido lá. O {killer} rasgou o peito da besta e somou pra conta. Prepara pro próximo spawn mais tarde."
                    ]), e_type)
            
        elif name == "BaronKill":
             killer = event.get("KillerName", "").split('#')[0].strip()
             self.assistant.say(random.choice([
                 f"Pff... Deu muito ruim, Barão fechado pro lado deles. O {killer} arrematou, todos pra base cobrir inibidor rápido!",
                 f"Irmão, Barão Nashor caiu pro inimigo sob o smite do {killer}. Defesa recuada, limpem super minions juntos.",
                 f"Ai ai, o jogo apertou! Os cara fizeram Barão lá com o {killer}. Respira, limpa wave nas torre e não caça briga fora de posição."
             ]), "negative")
             
        elif name == "HordeKill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            self.assistant.say(random.choice([
                f"Aí sim, botaram as vastilarvas pro saco pelo que vi. O {killer} puxou elas. Atenção total no dano em torre deles nas rotas agora.",
                f"Vastilarvas dizimadas ali pelo {killer}. Cuidado com o push absoluto deles se tiverem a maioria delas.",
                f"Pff... O grupo das larvinhas do Vazio foi pro telhado na mão do {killer}. Dá uma segurada que essas pestes levam barricada que nem água."
            ]), "negative")
            
        elif name == "HeraldKill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            self.assistant.say(random.choice([
                f"Ai ai, aviso cravado: Arauto capturado. O {killer} enfiou a mão no olho, defende as placas pelo mapa inteiro senão é gg cedo.",
                f"Fizeram o Arauto. O time do {killer} tá com a vantagem de quebrar torre rápida, recua nas lanes se tu não tiver visão.",
                f"Arauto finalizado. Atenção total porque logo o {killer} deve soltar o bicho de cabeçada na tua torre primária."
            ]), "negative")
            
        elif name == "TurretKilled":
            killer = event.get("KillerName", "").split('#')[0].strip()
            
            if killer and "Turret" not in killer and "Minion" not in killer:
                self.assistant.say(random.choice([
                    f"Atenção macro: Torre foi pro espeto. O {killer} abriu uma cratera na rota. Transita e domina aquela visão alí na selva que agora nós tem brecha.",
                    f"O {killer} levou uma torre! O mapa tá mais aberto. Dá call pra arrastar o ouro da barricada, puxa de novo e roda o mapa, porra.",
                    f"Hahaha, estrutura destruída. Menos uma torre dos caras enchendo o saco pelo mapa afora."
                ]), "positive")
            else:
                self.assistant.say(random.choice([
                    "Pff... Torreta de alguém foi engolida por tropas ou bicho. Um obstáculo a menos na vida do League of Legends.",
                    "Torre foi pro buraco ali pelas beiradas. Rota exposta, fica esperto com avanço de super tropa solta.",
                    "Ouviram esse estrondo né paizão. Mais uma estrutura virou pó. Fica rotacionando mapa conforme a demanda de farm lá sobrar."
                ]), "negative")

        elif name == "InhibKilled":
            killer = event.get("KillerName", "").split('#')[0].strip()
            
            self.assistant.say(random.choice([
                f"INIBIDOR FOI PRO SACO RAPAZIADA! Os super minions vão pesar na balança daquela rota agora de forma estupida! Prepara a base lá do lado reverso.",
                f"Pff, inibidor pro chão pelo {killer}! Agora o macrogame mudou absurdo. Esqueça torre da frente e segura o spawn maciço de winion empurrando a base de vocês.",
                f"Ai ai... Inibidor moído. O bicho pegou porque a rota vai pressionar que nem manada. Usa isso pra forçar um Barão de boa enquanto vão segurar base."
            ]), "negative")
