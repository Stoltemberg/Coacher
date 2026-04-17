import random


class MinervaVoice:
    """Centraliza a persona do Minerva em templates orientados a coaching."""

    def __init__(self, intensity="standard"):
        self.intensity = intensity

    def set_intensity(self, intensity):
        self.intensity = intensity

    @staticmethod
    def _pick(*options):
        return random.choice(options)

    def _is_hardcore(self):
        return self.intensity == "hardcore"

    @staticmethod
    def _adaptive_topic_label(topic):
        labels = {
            "farm": "teu farm",
            "vision": "tua leitura de visao",
            "itemization": "tua adaptacao de build",
            "objective_setup": "teu setup de objetivo",
            "fight_discipline": "tuas trocas e entradas",
            "lane_control": "teu controle de lane",
        }
        return labels.get(topic, "essa parte do teu jogo")

    def lobby_ready(self):
        return self._pick(
            "Minerva na area. Abre o cliente e deixa comigo que eu ja vou ler onde esse jogo vai entortar.",
            "Coacher online, meu mano. Quando a partida abrir eu te cobro igual gente grande.",
            "Bora trabalhar. Assim que isso entrar no Rift eu ja comeco a te passar a visao sem enrolacao.",
        )

    def champ_select_intro(self):
        return self._pick(
            "Draft abriu. Para de viajar e ja le a comp comigo, porque essa lane comeca bem antes do loading.",
            "Entramos no draft. Escolhe teu boneco com proposito que eu vou te passar onde essa comp deles quebra.",
            "Fase de picks rolando. Fica esperto nas escolhas ai porque eu ja to montando o plano pra essa partida.",
        )

    def game_start(self):
        return self._pick(
            "Partida comecou. Joga limpo, respeita o tempo de wave e escuta a call que o resto a gente cobra no mapa.",
            "Agora vale. Nada de heroismo torto cedo; faz o basico forte que eu te guio no resto.",
            "Rift aberto. Mantem a cabeca no jogo e executa direito, porque hoje nao tem espaco pra erro preguicoso.",
        )

    def player_identified(self):
        return self._pick(
            "Fechei teus dados. Agora para de se esconder atras da interface e joga o que tu sabe.",
            "Conta identificada. Pode ir pro jogo que eu ja to acompanhando teu passo por tras.",
            "Tudo certo contigo. A partir daqui eu vou te cobrar em tempo real sem passar a mao na cabeca.",
        )

    def macro_reminder(self):
        if self._is_hardcore():
            return self._pick(
                "Abriu tempo e tu vai desperdiçar? Gasta esse ouro, reseta direito e para de passear no mapa igual turista.",
                "Macro ganha jogo, preguica perde. Transformou espaco em nada de novo? Entao acorda e usa esse tempo direito.",
                "Parou pra pensar no mapa ou ta so correndo atras de brilho? Torre, visao e reset valem mais que essa fome de luta torta.",
            )
        return self._pick(
            "Empurrou wave e abriu tempo? Gasta esse ouro e volta pro mapa forte, nao inventa passeio inutil.",
            "Macro nao e enfeite. Se ganhou espaco, transforma isso em visao, reset ou estrutura.",
            "Olha o mapa com malicia: torre, visao e tempo valem mais que correr atras de fight torta.",
        )

    def minimap_reminder(self):
        if self._is_hardcore():
            return self._pick(
                "Olha esse minimapa, porra. Se tu avanca sem saber do jungle, tu ta pedindo pra ser cobrado na marra.",
                "Para de jogar cego. Le rio, rastreia cacador e para de empurrar wave como se o mapa nao existisse.",
                "Tu quer mesmo estender sem visao? Entao depois nao reclama quando o gank vier carimbar tua testa.",
            )
        return self._pick(
            "Olha o minimapa, caralho. Se tu nao sabe onde o jungle ta, entao tu nao tem direito de avancar essa wave.",
            "Para um segundo e le o mapa. Warda, rastreia o cacador e decide a lane com cerebro.",
            "Tem informacao na borda da tela tambem. Ve o rio, sente o gank e para de jogar no escuro.",
        )

    def assist(self):
        return self._pick(
            "Boa. Entrou na jogada, pingou recurso e saiu lucro pro time. Continua somando assim.",
            "Assistencia limpa. Tu leu a fight direito e chegou no tempo certo, e disso que eu to falando.",
            "Participou bem. Nao foi highlight vazio, foi presenca util na luta.",
        )

    def lane_matchup(self, enemy_nick):
        return self._pick(
            f"Teu confronto direto e o {enemy_nick}. Le o padrao dele cedo e puxa a wave pro teu lado se a troca ficar ruim.",
            f"O cara na tua frente e o {enemy_nick}. Descobre logo onde tu ganha a troca e para de bater por bater.",
            f"Lane definida contra {enemy_nick}. Se nao tiver certeza da troca, controla a wave primeiro e luta depois.",
        )

    def lane_matchup_detail(self, my_champion, enemy_champion, enemy_nick=None):
        enemy_label = enemy_nick or enemy_champion
        direct_tips = {
            "Darius": self._pick(
                f"{enemy_label} so parece injusto quando tu troca colado sem criterio. Bate curto, sai da borda e nao deixa stack gratis.",
                f"{enemy_label} quer te puxar pra troca longa. Guarda espaco, congela perto de ti e pune quando ele errar a entrada.",
            ),
            "Yasuo": self._pick(
                f"{enemy_label} cresce quando tu solta wave e luta sem minion contado. Quebra o ritmo da rota e pune o dash previsivel.",
                f"{enemy_label} quer empilhar pressao com tropa. Controla a wave, respeita tornado e faz ele escolher mal o engage.",
            ),
            "Zed": self._pick(
                f"{enemy_label} quer tua vida quando teu recurso cair. Segura poke limpo, respeita nivel seis e prepara defesa cedo.",
                f"{enemy_label} vive de janela curta. Se tu nao der poke gratis e guardar cooldown defensivo, a lane fica bem mais honesta.",
            ),
            "Blitzcrank": self._pick(
                f"{enemy_label} vive de um braco so. Usa a wave como escudo, anda com criterio e pune quando esse cooldown sair errado.",
                f"Contra {enemy_label}, teu trabalho e nao dar cara limpa. Tropa na frente e troca em cima do erro dele.",
            ),
            "Leona": self._pick(
                f"{enemy_label} quer engage reto e bagunca longa. Nao adianta bater na onda errada e ficar sem rota de fuga.",
                f"{enemy_label} entra forte quando tu avanca torto. Mantem a lane fina e guarda resposta pro primeiro all-in.",
            ),
            "Vayne": self._pick(
                f"{enemy_label} escala se tu deixa ela respirar. Aperta wave cedo e nao entrega troca longa perto da parede.",
                f"{enemy_label} quer fight esticada e espaco pra andar. Se tu pressiona cedo e limita a rota dela, o jogo muda.",
            ),
        }
        if enemy_champion in direct_tips:
            return direct_tips[enemy_champion]

        if my_champion in {"Ashe", "Jinx", "Vayne", "Caitlyn", "Kog'Maw"}:
            return self._pick(
                f"Tu ta de {my_champion} contra {enemy_label}. Lane de ADC nao e ego: wave bem posta, poke limpo e respeito total ao engage.",
                f"Com {my_champion} contra {enemy_label}, teu ouro vem de wave e posicionamento. Troca so quando a rota estiver do teu lado.",
            )

        if my_champion in {"Ahri", "Orianna", "Syndra", "Viktor", "Azir"}:
            return self._pick(
                f"Com {my_champion} nessa matchup contra {enemy_label}, controla alcance e empurra quando teu cooldown estiver limpo.",
                f"{my_champion} ganha valor quando tu joga por espaco e tempo. Contra {enemy_label}, usa a wave pra decidir a troca.",
            )

        return self._pick(
            f"Contra {enemy_label}, a lane vai premiar quem controlar melhor a wave e escolher a troca certa. Nada de bater por ansiedade.",
            f"Essa matchup contra {enemy_label} nao se ganha no grito. Espaco, cooldown e wave mandam mais que vontade.",
        )

    def low_farm(self, cs, minutes):
        if self._is_hardcore():
            return self._pick(
                f"{cs} de CS com {int(minutes)} minutos e feio demais. Para de sonhar com fight e vai trabalhar nessa wave.",
                f"Esse farm ta horroroso: {cs} aos {int(minutes)}. Menos ego, mais minion, porque tu ta se afundando sozinho.",
                f"Tu largou dinheiro no mapa ate demais. {cs} CS em {int(minutes)} minutos nao e azar, e execucao ruim.",
            )
        return self._pick(
            f"Teu farm ta uma tristeza: {cs} CS em {int(minutes)} minutos. Para de cacar play aleatoria e recompra teu jogo no minion.",
            f"{cs} de farm com {int(minutes)} minutos e muito pouco, meu mano. Arruma essa wave e para de doar recurso de graca.",
            f"Ta faltando disciplina. Esse {cs} CS aos {int(minutes)} minutos pede menos ego e mais last hit.",
        )

    def high_farm(self, cs, minutes):
        return self._pick(
            f"Ai sim, {cs} de farm em {int(minutes)} minutos. Mantem essa linha que o mapa vai comecar a te respeitar.",
            f"Farm forte: {cs} CS aos {int(minutes)}. Continua jogando em cima da wave que o ouro vem sozinho.",
            f"Ta farmando como gente grande. {cs} creeps na conta e pressao boa pra converter em item.",
        )

    def low_vision(self, wards):
        if self._is_hardcore():
            return self._pick(
                f"{wards} de visao? Ta querendo jogar no escuro e culpar os outros depois. Compra controle e vira gente.",
                f"Esse placar de visao em {wards} e preguica travestida de confianca. Sem ward tu so ta flipando o mapa.",
                f"Visao patetica ate aqui. Para de entrar em mato no sentimento e comeca a preparar o terreno direito.",
            )
        return self._pick(
            f"{wards} de visao ate aqui e muito pouco. Compra controle e para de entrar em zona escura como se fosse milagreiro.",
            f"Ta jogando cego, meu parceiro. Esse placar de visao em {wards} nao sustenta lane nem objetivo.",
            f"Visao fraca. Sem ward tu so ta apostando, e coach nenhum salva aposta burra no escuro.",
        )

    def armor_warning(self, player_name):
        return self._pick(
            f"O {player_name} ja fechou armadura pesada. Ajusta tua build e entra com penetracao, senao teu dano morre ali.",
            f"Olha o tab: {player_name} ja ta blindado. Se tu insistir em build seca, vai bater e nao vai acontecer nada.",
            f"{player_name} bufou na armadura. Prepara penetracao fisica porque agora forca bruta sozinha nao resolve.",
        )

    def magic_resist_warning(self, player_name):
        return self._pick(
            f"{player_name} ja botou resistencia magica. Se teu dano e AP, prepara penetracao e para de fingir que vai atravessar isso no abraco.",
            f"O {player_name} fechou MR. Ajusta a loja depois da base porque teu burst cru vai perder valor.",
            f"Tem resistencia magica do lado deles no {player_name}. Sem item certo, tu so vai cocar essa barra de vida.",
        )

    def anti_heal_warning(self, player_name):
        return self._pick(
            f"{player_name} comprou corta-cura. Se tua luta depende de sustain, respeita e escolhe melhor o momento de entrar.",
            f"O {player_name} ja ta com anti-heal. Nao estica troca achando que vampirismo vai te carregar.",
            f"Tem reducao de cura na mao do {player_name}. Joga a fight com mais criterio porque tua recuperacao caiu bastante.",
        )

    def early_build_plan(self, my_champion, enemy_names, plan_key="standard"):
        enemy_pool = set(enemy_names or [])
        has_healing = bool(enemy_pool & {"Aatrox", "Soraka", "Yuumi", "Vladimir", "Sylas", "Dr. Mundo", "Swain", "Briar"})
        if plan_key == "high_cc":
            return self._pick(
                f"Build de entrada pra {my_champion}: pensa em tenacidade ou bota de MR cedo, porque os caras querem te prender antes da luta existir.",
                f"Pra {my_champion} nessa comp, a loja tem que respeitar controle. Mercurio e luta curta valem mais que ganancia.",
            )
        if plan_key == "assassins":
            return self._pick(
                f"Os caras querem burstar alvo mole. Se tu ta de {my_champion}, ja pensa em defesa cedo e nao monta build de highlight vazio.",
                f"{my_champion} contra assassino precisa de seguro de vida na build. Cronometro, armadura leve ou defesa cedo podem salvar tua partida.",
            )
        if plan_key == "tanks":
            return self._pick(
                f"Tem parede demais do outro lado. Com {my_champion}, tua build precisa mirar dano continuo e penetracao, nao so burst seco.",
                f"Se essa comp deles vier de tanque, tu vai precisar atravessar front line. Pensa cedo em penetracao e em fight mais longa.",
            )
        if has_healing:
            return self._pick(
                f"Tem cura demais do outro lado. Com {my_champion}, deixa o anti-heal no radar e nao espera a luta ficar perdida pra reagir.",
                f"Essa partida pede anti-heal cedo ou no timing certo. Se tu ignorar a cura deles, a build vai nascer torta.",
            )
        return self._pick(
            f"Build base pra {my_champion}: fecha o pico de poder sem inventar moda e adapta a segunda metade da loja ao que aparecer no tab.",
            f"Comeca a build de {my_champion} pelo basico forte. Depois a gente corrige conforme armadura, MR e cura forem aparecendo.",
        )

    def comp_build_adjustment(self, my_champion, enemy_names):
        enemy_pool = set(enemy_names or [])
        if enemy_pool & {"Aatrox", "Soraka", "Yuumi", "Vladimir", "Sylas", "Dr. Mundo", "Swain", "Briar"}:
            return self._pick(
                f"Tem sustain demais do outro lado. Deixa corta-cura no radar da build de {my_champion} antes dessa lane virar novela.",
                f"Se a comp deles sustenta demais, tua build com {my_champion} nao pode fingir que anti-heal e opcional.",
            )
        if len(enemy_pool & {"Rammus", "Malphite", "Ornn", "Sion", "Sejuani", "Leona", "Nautilus"}) >= 2:
            return self._pick(
                f"Essa comp deles vai empilhar front line. Com {my_champion}, pensa em penetracao e luta longa desde cedo.",
                f"Tem muito corpo duro do outro lado. A build de {my_champion} precisa atravessar tanque, nao so explodir suporte.",
            )
        if len(enemy_pool & {"Lissandra", "Ashe", "Morgana", "Leona", "Nautilus", "Amumu", "Sejuani"}) >= 2:
            return self._pick(
                f"Se os controles deles encaixarem, tua partida acaba sem tu jogar. Considera tenacidade ou defesa cedo com {my_champion}.",
                f"Tem CC demais nessa comp. A build de {my_champion} precisa respeitar isso antes de sonhar com dano puro.",
            )
        return None

    def self_kill(self, victim):
        return self._pick(
            f"Boa, matou o {victim}. Agora empurra essa wave ou some do mapa, mas nao entrega o reset de volta.",
            f"Abate limpo no {victim}. Cobra recurso, arruma visao e transforma isso em vantagem de verdade.",
            f"Tu puniu o {victim} bem agora. Nao comemora parado; converte esse espaco em farm, placa ou reset.",
        )

    def self_death_pve(self):
        return self._pick(
            "Tu morreu pro mapa de graca. Limpa a cabeca e volta mais disciplinado porque isso entrega tempo pro inimigo.",
            "Execucao boba pra PvE. Agora para de forcar sem recurso e recompae teu jogo com calma.",
            "Morrer pra torre ou ambiente e presente barato pros caras. Reseta a mente e volta sem tilt.",
        )

    def self_death_enemy(self, killer):
        if self._is_hardcore():
            return self._pick(
                f"O {killer} te cobrou porque tu entrou igual maluco. Agora segura teu ego e para de dar essa janela ridicula.",
                f"Tu morreu pro {killer} porque jogou torto. Respeita a lane, recompra no farm e nao repete a burrada.",
                f"Essa morte pro {killer} foi toda tua. Ajusta posicao, tempo e recurso antes de pensar em peitar de novo.",
            )
        return self._pick(
            f"O {killer} te puniu porque tu entrou torto. Respira, recua a pressao e espera janela boa pra responder.",
            f"Tu morreu pro {killer} e a rota entortou. Joga no seguro agora e recompra a lane no farm.",
            f"Essa morte pro {killer} foi ganancia ou leitura ruim. Ajusta tua posicao e para de dar a mesma janela.",
        )

    def ally_pve_death(self, victim, pve):
        return self._pick(
            f"O {victim} se entregou pra {pve}. Aproveita o tempo no mapa porque os caras tambem ficaram sem recurso ali.",
            f"Nosso lado perdeu o {victim} pra {pve}. Nao entra no desespero; organiza wave e segura o prejuizo.",
            f"{victim} foi de base pra {pve}. Respira e joga a proxima janela direito pra nao virar efeito cascata.",
        )

    def enemy_pve_death(self, victim, pve):
        return self._pick(
            f"O inimigo {victim} passou vergonha pra {pve}. Usa esse tempo e aperta o mapa agora.",
            f"{victim} morreu pra {pve}. Boa, porque isso abriu uma janela limpa pra pressionar.",
            f"Os caras perderam o {victim} pra {pve}. Se mexe no mapa antes que esse presente expire.",
        )

    def ally_death(self, victim, killer):
        return self._pick(
            f"O {victim} caiu pro {killer}. Nao compra a mesma luta torta agora; reorganiza a wave e espera numero.",
            f"Nosso lado perdeu o {victim} pro {killer}. Segura a ansiedade e protege o mapa ate o respawn encaixar.",
            f"{killer} puniu o {victim}. Sem tilt: arruma visao e evita entregar sequencia nessa mesma area.",
        )

    def enemy_death(self, killer, victim):
        return self._pick(
            f"Boa, o {killer} derrubou o {victim}. Usa essa vantagem pra avancar visao ou arrancar recurso.",
            f"O {victim} caiu e o mapa abriu. Se posiciona direito e cobra objetivo ou estrutura.",
            f"Menos um deles, {victim} foi pro chao. Nao dispersa agora; aproveita a janela e acelera o mapa.",
        )

    def first_blood(self):
        return self._pick(
            "First Blood na conta. Agora controla a emocao e usa essa vantagem antes que ela evapore no mapa.",
            "Saiu o primeiro abate. Quem ler melhor o reset e a wave agora toma conta do jogo cedo.",
            "Primeiro sangue rolou. Nao vira bagunca: converte essa vantagem em tempo, recurso e pressao.",
        )

    def self_multikill(self, kill_streak):
        if kill_streak == 2:
            return self._pick(
                "Double kill teu. Mantem a calma e cobra o mapa, porque agora o jogo ta pedindo conversao, nao ego.",
                "Dois abatidos na conta. Boa, mas usa isso pra quebrar estrutura ou objetivo antes de dispersar.",
            )
        if kill_streak == 3:
            return self._pick(
                "Triple kill. Luta tua, entao ja chama mapa e fecha a conta antes que eles respawnem.",
                "Tres no chao por tua causa. Agora empurra com disciplina e transforma isso em algo permanente.",
            )
        if kill_streak == 4:
            return self._pick(
                "Quadra kill. Se der o penta, pega; se nao der, fecha a play com objetivo e nao joga fora a vantagem.",
                "Quatro abatidos. Excelente, mas teu trabalho agora e garantir mapa, nao so cacar highlight.",
            )
        return self._pick(
            "Penta kill, animal. Agora fecha o jogo com cabeca no lugar porque esse tipo de fight decide partida.",
            "Cinco no chao. O highlight veio, entao aproveita e termina o mapa sem inventar moda.",
        )

    def enemy_multikill(self, killer, kill_streak):
        if kill_streak == 2:
            if self._is_hardcore():
                return self._pick(
                    f"O {killer} pegou double kill e voces ainda vao insistir em entrar picado? Junta essa bagunca e mata o tempo dele.",
                    f"Double kill pro {killer}. Para de doar luta isolada pra esse cara e organiza a proxima fight com cerebro.",
                )
            return self._pick(
                f"O {killer} pegou double kill. Segura a onda, nao da mais reset pra esse cara e agrupa melhor a proxima luta.",
                f"Double kill pro {killer}. Respeita o spike dele e para de entrar isolado nessa regiao.",
            )
        if self._is_hardcore():
            return self._pick(
                f"O {killer} ja ta com {kill_streak} kills e voces ainda querem duelo seco. Acorda e joga por visao, numero e disciplina.",
                f"{killer} virou problema real. Para de peitar no braco e quebra o ritmo dele com mapa e setup decente.",
            )
        return self._pick(
            f"O {killer} ja ta com {kill_streak} kills seguidas. Agora e visao, numero e disciplina; duelo seco virou loucura.",
            f"{killer} escalou forte na fight. Nao compra 1v1 torto, organiza recurso e mata esse tempo dele no mapa.",
        )

    def elder_dragon(self, is_ally):
        if is_ally:
            return self._pick(
                "Anciao nosso. Agora e jogar junto e apertar o gatilho na primeira janela boa, porque esse buff fecha partida.",
                "Dragao Anciao na mao. Agrupa, forca visao e usa a execucao pra acabar com essa graca deles.",
            )
        return self._pick(
            "Os caras pegaram o Anciao. Recuo e disciplina agora, porque qualquer erro vira execucao na tua cara.",
            "Anciao deles. Para de sonhar com engage torta e joga debaixo de visao ate esse buff passar ou a janela aparecer.",
        )

    def dragon_control(self, dragon_name, is_ally, drags, killer):
        if drags == 3:
            return self._pick(
                f"{'Nosso' if is_ally else 'Deles'} {dragon_name} e agora tem ponto de alma na mesa. Prepara o mapa desde ja porque o proximo rio vale demais.",
                f"O {killer} garantiu o dragao {dragon_name} e deixou {'a gente' if is_ally else 'eles'} no ponto de alma. A proxima rotacao precisa ser limpa.",
            )
        if drags >= 4:
            return self._pick(
                f"Alma do dragao {dragon_name} {'pra nos' if is_ally else 'pra eles'}. Isso muda a partida inteira, entao ajusta a fight em cima desse bonus.",
                f"Deu alma de {dragon_name} {'do nosso lado' if is_ally else 'pros caras'}. Agora toda decisao tem que respeitar esse spike.",
            )
        return self._pick(
            f"Dragao {dragon_name} {'na nossa conta' if is_ally else 'pra eles'}. Ja pensa no proximo setup de rio porque ninguem ganha objetivo no improviso.",
            f"O {killer} pegou o dragao {dragon_name}. Usa essa informacao pra organizar visao e tempo antes do proximo spawn.",
        )

    def baron_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Barao nosso na mao do {killer}. Agora faz o basico bem feito: reseta, organiza side e pressiona sem jogar buff fora.",
                f"O {killer} garantiu o Barao. Usa essa janela pra sufocar o mapa, nao pra correr atras de kill inutil.",
            )
        return self._pick(
            f"Barao pro lado deles com o {killer}. Respira, limpa wave e para de comprar fight fora de posicao.",
            f"O {killer} fechou o Barao pros caras. Defende com paciencia e nao entrega mais recurso no desespero.",
        )

    def horde_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Vastilarvas nossas com o {killer}. Agora cobra placa e estrutura cedo, porque esse recurso precisa virar ouro.",
                f"O {killer} puxou as larvas. Acelera pressao de torre e joga em cima dessa janela antes que esfrie.",
            )
        return self._pick(
            f"O {killer} levou as vastilarvas pros caras. Respeita o dano em torre e nao larga estrutura de graca.",
            f"Larvas do vazio do lado deles. Fica esperto com push cedo porque isso vai bater forte nas barricadas.",
        )

    def herald_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Arauto nosso com o {killer}. Planeja onde quebrar o mapa e usa isso no timing certo.",
                f"O {killer} garantiu o Arauto. Nao solta de qualquer jeito; escolhe a rota que mais abre visao e espaco.",
            )
        return self._pick(
            f"O {killer} pegou o Arauto. Respeita a proxima pressao de rota e protege placa onde der.",
            f"Arauto deles. Guarda visao e leitura de side porque esse bicho vai tentar abrir teu mapa cedo.",
        )

    def turret_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Torre no chao pelo {killer}. Mapa abriu, entao avanca visao e cobra mais recurso nessa regiao.",
                f"O {killer} quebrou estrutura. Boa, agora ocupa o espaco e nao devolve o controle de graca.",
            )
        return self._pick(
            f"Eles levaram uma torre com o {killer}. Ajusta a visao e respeita o mapa mais aberto daqui pra frente.",
            f"Torre perdida pro lado do {killer}. Agora tu precisa ler melhor as entradas porque a selva ficou mais exposta.",
        )

    def neutral_turret_taken(self):
        return self._pick(
            "Uma torre caiu no caos do mapa. Le a side que abriu e se posiciona antes da proxima onda.",
            "Estrutura destruida. Agora o mapa muda de formato, entao para de andar no automatico.",
        )

    def inhibitor_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Inibidor nosso com o {killer}. Usa a pressao de super minion pra preparar Barao, alma ou fim de jogo.",
                f"O {killer} abriu inibidor. Agora joga em volta da lane pressionada e forca os caras a responderem mal.",
            )
        return self._pick(
            f"Inibidor perdido pro {killer}. Segura a side com calma e nao entrega o resto do mapa no desespero.",
            f"O {killer} quebrou o inibidor. Agora administra os supers direito e espera a proxima janela de resposta.",
        )

    def draft_enemy_locked(self, champion_name):
        return self._pick(
            f"Os caras travaram {champion_name}. Ja le o padrao dessa lane e nao escolhe no piloto automatico.",
            f"{champion_name} apareceu do lado deles. Guarda isso porque muda troca, tempo e janela de erro.",
            f"Confirmaram {champion_name}. Agora monta tua resposta direito e para de pensar so no highlight.",
        )

    def draft_pick_confirmed(self, champion_name):
        return self._pick(
            f"Tu travou {champion_name}. Entao joga como quem escolheu com intencao, nao como quem clicou por costume.",
            f"{champion_name} na tua mao. Agora a gente define runa, feitico e plano pra essa lane nao comecar torta.",
            f"Escolha fechada em {champion_name}. Boa, agora escuta a call e entra no jogo com objetivo claro.",
        )

    def draft_counter_tip(self, champion_name):
        tips = {
            "Zed": f"{champion_name} quer punir erro curto e sumir da tela. Segura a wave perto de ti e ja pensa em defesa cedo pra nao virar alvo livre.",
            "Yasuo": f"{champion_name} so fica confortavel se tu der wave solta. Trava o ritmo, respeita o all-in cedo e cobra ele quando a rota estiver controlada.",
            "Darius": f"{champion_name} ganha quando tu troca colado sem criterio. Kiteia, controla espaco e chama recurso antes de peitar essa lane de frente.",
            "Master Yi": f"{champion_name} quer fight baguncada e alvo sem controle. Guarda CC, organiza entrada e nao entrega reset de graca pra esse maluco.",
            "Blitzcrank": f"{champion_name} quer uma janela so. Nao da cara sem wave, usa a tropa a teu favor e pune o cooldown quando ele errar o braco.",
            "Vayne": f"{champion_name} escala se tu deixa respirar. Marca posicao dela cedo e guarda recurso pra quebrar a fight antes dela andar livre.",
        }
        return tips.get(champion_name)

    def draft_comp_plan(self, plan_key, champion_name):
        plans = {
            "high_cc": self._pick(
                f"Os caras tao lotados de controle. Deixa {champion_name} com tenacidade ou Purificar e joga fight entrando no tempo certo, nao no desespero.",
                f"Comp deles tem cadeia de CC pra te travar inteiro. Ajusta runa defensiva agora e respeita a primeira engage.",
            ),
            "assassins": self._pick(
                f"Tem assassino demais do outro lado. Com {champion_name}, pensa em Exaustao ou ferramenta defensiva porque tua janela de erro ficou curta.",
                f"A comp deles quer explodir alvo mole. Se tu vai de {champion_name}, prepara protecao e joga mais por posicionamento do que por ego.",
            ),
            "tanks": self._pick(
                f"Os caras vieram de front line pesada. Com {champion_name}, tu precisa de dano continuo e paciencia de luta, nao de all-in torto.",
                f"Comp deles e tanquezada pura. Ajusta tua runa pra fight longa e pensa desde cedo em item pra atravessar essa parede.",
            ),
            "standard": self._pick(
                f"A comp deles e mais padrao. Entao usa {champion_name} pra jogar o basico forte: lane limpa, reset bom e entrada no objetivo no tempo.",
                f"Nao tem pegadinha gigante nessa draft. Com {champion_name}, vence quem erra menos execucao, entao organiza teu early direito.",
            ),
        }
        return plans[plan_key]

    def draft_build_tip(self, plan_key, champion_name, enemy_names):
        return self.early_build_plan(champion_name, enemy_names, plan_key=plan_key)

    def draft_comp_snapshot(self, champion_name, comp_style, pressure_points):
        pressure = "; ".join((pressure_points or [])[:2])
        return self._pick(
            f"Leitura da draft: os caras vieram de {comp_style}. De {champion_name}, teu trabalho e {pressure}.",
            f"Essa comp deles ta com cara de {comp_style}. Com {champion_name}, entra no jogo lembrando de {pressure}.",
        )

    def draft_power_spike(self, champion_name, power_spikes):
        spikes = ", depois ".join((power_spikes or [])[:2])
        return self._pick(
            f"Spike de {champion_name}: teu jogo comeca a apertar em {spikes}. Nao inventa luta antes do teu boneco existir.",
            f"Guarda isso de {champion_name}: teus picos mais claros sao {spikes}. Joga em volta disso e para de flipar janela ruim.",
        )

    def draft_build_focus(self, champion_name, build_focus):
        focus = "; ".join((build_focus or [])[:2])
        return self._pick(
            f"Loja pra essa partida com {champion_name}: {focus}. Build boa ganha draft que parecia normal.",
            f"Anota a build de {champion_name} nessa aqui: {focus}. Se tu ignorar isso, a partida ja nasce torta.",
        )

    def draft_role_plan(self, champion_name, lane_plan, first_reset_focus):
        return self._pick(
            f"Plano de rota com {champion_name}: {lane_plan}. No primeiro reset, tua prioridade e {first_reset_focus}.",
            f"De {champion_name}, tua lane quer isto: {lane_plan}. Quando basear, pensa em {first_reset_focus}.",
        )

    def draft_duo_synergy(self, champion_name, synergy):
        label = synergy.get("label", "dupla forte")
        plan = synergy.get("plan", "")
        spike = synergy.get("spike", "")
        return self._pick(
            f"Sinergia de draft com {champion_name}: {label}. Plano da dupla: {plan}.",
            f"Com {champion_name}, tua dupla tem cara de {label}. Joga lembrando disto: {plan}. {spike}",
        )

    def draft_jungle_synergy(self, champion_name, synergy):
        label = synergy.get("label", "setup forte")
        plan = synergy.get("plan", "")
        spike = synergy.get("spike", "")
        return self._pick(
            f"Parceria de mapa pro teu {champion_name}: {label}. O jogo quer isto cedo: {plan}.",
            f"Teu combo de mapa com {champion_name} ta {label}. Guarda o plano: {plan}. {spike}",
        )

    def opening_plan(self, champion_name, opening_plan):
        return self._pick(
            f"Comeco da partida com {champion_name}: {opening_plan}. Nao deixa os primeiros minutos passarem no piloto automatico.",
            f"Opening de {champion_name}: {opening_plan}. O jogo comeca agora, nao so no primeiro objetivo.",
        )

    def jungle_gank_warning(self, jungler_name, lane):
        return self._pick(
            f"O {jungler_name} ja apareceu pro lado do {lane}. Entao para de jogar essa lane como se selva nao existisse.",
            f"Olho no mapa: {jungler_name} bateu no {lane}. Respeita cobertura e nao entrega janela de gank de graca.",
        )

    def jungle_objective_shadow(self, jungler_name, objective_name):
        labels = {
            "dragon": "dragao",
            "herald": "Arauto",
            "baron": "Barao",
            "horde": "larvas",
        }
        label = labels.get(objective_name, "objetivo")
        return self._pick(
            f"O {jungler_name} ja mostrou pressao no {label}. Entao joga esse lado do mapa com cerebro, nao no chute.",
            f"Anota isso: {jungler_name} ja passou pelo {label}. A leitura de selva ficou mais clara, entao reage no tempo certo.",
        )

    def lane_matchup_knowledge(self, my_champion, enemy_champion, insight):
        verdict = insight.get("verdict", "skill")
        plan = insight.get("plan", "")
        danger = insight.get("danger", "")
        spike_race = insight.get("spike_race", "")
        lane_plan = insight.get("lane_plan", "")
        first_reset_focus = insight.get("first_reset_focus", "")
        extra = ""
        if lane_plan:
            extra = f" Tua lane quer {lane_plan}."
        if first_reset_focus:
            extra += f" No primeiro reset, pensa em {first_reset_focus}."
        return self._pick(
            f"Matchup de {my_champion} contra {enemy_champion} ta {verdict}. Plano: {plan}. Perigo real: {danger}. {spike_race}{extra}",
            f"Leitura da lane: {my_champion} contra {enemy_champion} e {verdict}. Joga por {plan} e respeita {danger}. {spike_race}{extra}",
        )

    def early_build_focus(self, champion_name, build_focus):
        focus = "; ".join((build_focus or [])[:2])
        return self._pick(
            f"Plano de loja pra {champion_name}: {focus}. Faz o reset servir pra alguma coisa.",
            f"Abre a loja com cerebro em {champion_name}: {focus}. Item certo compra janela de jogo.",
        )

    def power_spike_call(self, champion_name, power_spikes):
        spikes = ", depois ".join((power_spikes or [])[:2])
        return self._pick(
            f"Teu jogo de {champion_name} vai apertar em {spikes}. Se antecipa a isso e nao luta fora do teu tempo.",
            f"Spike de {champion_name} nessa partida: {spikes}. Luta boa e a que respeita esse relogio.",
        )

    def mid_game_job(self, champion_name, mid_game_job, situational_items):
        items = "; ".join((situational_items or [])[:2])
        return self._pick(
            f"No mid game de {champion_name}, tua funcao e {mid_game_job}. E deixa no radar: {items}.",
            f"Quando o mapa abrir com {champion_name}, teu trabalho vira {mid_game_job}. Loja situacional: {items}.",
        )

    def adaptive_repetition(self, topic, streak):
        label = self._adaptive_topic_label(topic)
        if self._is_hardcore():
            return self._pick(
                f"Mesmo erro de novo em {label}. Ja sao {streak} sinais parecidos e tu ainda nao ajustou essa porra.",
                f"Ta repetindo a mesma falha em {label}. Foram {streak} avisos e tu continua abrindo a janela igual trouxa.",
                f"{label.capitalize()} ta te sabotando de novo. Corrige agora porque esse padrao ja ficou escancarado.",
            )
        return self._pick(
            f"Tem padrao ruim aparecendo em {label}. Ja sao {streak} sinais parecidos, entao ajusta isso agora.",
            f"Mesmo problema repetindo em {label}. Se tu nao corrigir ja, essa partida vai continuar vazando por ai.",
            f"{label.capitalize()} ja apareceu errado mais de uma vez. Para, reorganiza e limpa essa execucao.",
        )

    def adaptive_recovery(self, topic, streak):
        label = self._adaptive_topic_label(topic)
        if self._is_hardcore():
            return self._pick(
                f"Ai sim, tu finalmente arrumou {label}. Mantem isso porque antes ja tinham sido {streak} sinais tortos.",
                f"Boa, agora {label} entrou no eixo. Nao relaxa e nao volta pro mesmo erro idiota de antes.",
                f"Tu corrigiu {label} depois de apanhar nisso. Continua assim e para de devolver a melhoria.",
            )
        return self._pick(
            f"Melhorou {label}. Mantem a mao firme porque antes esse ponto ja tava te cobrando.",
            f"Boa correção em {label}. Agora sustenta isso e nao devolve a consistencia que apareceu.",
            f"{label.capitalize()} entrou no lugar. Continua nessa linha que o jogo responde melhor.",
        )

    def history_draft_focus(self, champion_name, primary_leak, hot_phase=""):
        phase_hint = f" e isso costuma pesar mais no {hot_phase}" if hot_phase else ""
        return self._pick(
            f"Historico na mesa pro teu {champion_name}: teu vazamento mais recorrente tem sido {primary_leak}{phase_hint}. Entra nessa fila ja marcando isso.",
            f"Antes do loading, anota teu padrao ruim recente com {champion_name}: {primary_leak}{phase_hint}. Hoje tu nao vai repetir essa porcaria no automatico.",
        )

    def history_draft_strength(self, champion_name, primary_fix):
        return self._pick(
            f"Tambem tem coisa boa no teu historico com {champion_name}: quando tu acerta {primary_fix}, teu jogo sobe de nivel. Entao puxa isso cedo.",
            f"Tua melhor resposta recente com {champion_name} passa por {primary_fix}. Mantem isso vivo desde o draft ate a lane abrir.",
        )

    def history_early_focus(self, primary_leak, hot_phase=""):
        phase_hint = f" e esse padrao normalmente estoura no {hot_phase}" if hot_phase else ""
        if self._is_hardcore():
            return self._pick(
                f"Jogo abriu e teu historico ja ta te olhando torto: {primary_leak}{phase_hint}. Corrige cedo e para de esperar o erro acontecer pra reagir.",
                f"Nao esquece teu vazamento recente: {primary_leak}{phase_hint}. Se repetir hoje, a cobranca vem na hora.",
            )
        return self._pick(
            f"Teu foco de entrada hoje e {primary_leak}{phase_hint}. Ajusta isso cedo e nao deixa o padrao ruim voltar.",
            f"Historico recente pediu atencao em {primary_leak}{phase_hint}. Usa os primeiros minutos pra estabilizar isso.",
        )
