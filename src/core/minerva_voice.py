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

    def lobby_ready(self):
        return self._pick(
            "Minerva na área. Abre o cliente e deixa comigo que eu já vou ler onde esse jogo vai entortar.",
            "Coacher online, meu mano. Quando a partida abrir eu te cobro igual gente grande.",
            "Bora trabalhar. Assim que isso entrar no Rift eu já começo a te passar a visão sem enrolação.",
        )

    def champ_select_intro(self):
        return self._pick(
            "Draft abriu. Para de viajar e já lê a comp comigo, porque essa lane começa bem antes do loading.",
            "Entramos no draft. Escolhe teu boneco com propósito que eu vou te passar onde essa comp deles quebra.",
            "Fase de picks rolando. Fica esperto nas escolhas aí porque eu já tô montando o plano pra essa partida.",
        )

    def game_start(self):
        return self._pick(
            "Partida começou. Joga limpo, respeita o tempo de wave e escuta a call que o resto a gente cobra no mapa.",
            "Agora vale. Nada de heroísmo torto cedo; faz o básico forte que eu te guio no resto.",
            "Rift aberto. Mantém a cabeça no jogo e executa direito, porque hoje não tem espaço pra erro preguiçoso.",
        )

    def player_identified(self):
        return self._pick(
            "Fechei teus dados. Agora para de se esconder atrás da interface e joga o que tu sabe.",
            "Conta identificada. Pode ir pro jogo que eu já tô acompanhando teu passo por trás.",
            "Tudo certo contigo. A partir daqui eu vou te cobrar em tempo real sem passar a mão na cabeça.",
        )

    def macro_reminder(self):
        if self._is_hardcore():
            return self._pick(
                "Abriu tempo e tu vai desperdiçar? Gasta esse ouro, reseta direito e para de passear no mapa igual turista.",
                "Macro ganha jogo, preguiça perde. Transformou espaço em nada de novo? Então acorda e usa esse tempo direito.",
                "Parou pra pensar no mapa ou tá só correndo atrás de brilho? Torre, visão e reset valem mais que essa fome de luta torta.",
            )
        return self._pick(
            "Empurrou wave e abriu tempo? Gasta esse ouro e volta pro mapa forte, não inventa passeio inútil.",
            "Macro não é enfeite. Se ganhou espaço, transforma isso em visão, reset ou estrutura.",
            "Olha o mapa com malícia: torre, visão e tempo valem mais que correr atrás de fight torta.",
        )

    def minimap_reminder(self):
        if self._is_hardcore():
            return self._pick(
                "Olha esse minimapa, porra. Se tu avança sem saber do jungle, tu tá pedindo pra ser cobrado na marra.",
                "Para de jogar cego. Lê rio, rastreia caçador e para de empurrar wave como se o mapa não existisse.",
                "Tu quer mesmo estender sem visão? Então depois não reclama quando o gank vier carimbar tua testa.",
            )
        return self._pick(
            "Olha o minimapa, caralho. Se tu não sabe onde o jungle tá, então tu não tem direito de avançar essa wave.",
            "Para um segundo e lê o mapa. Ward, rastreia o caçador e decide a lane com cérebro.",
            "Tem informação na borda da tela também. Vê o rio, sente o gank e para de jogar no escuro.",
        )

    def assist(self):
        return self._pick(
            "Boa. Entrou na jogada, pingou recurso e saiu lucro pro time. Continua somando assim.",
            "Assistência limpa. Tu leu a fight direito e chegou no tempo certo, é disso que eu tô falando.",
            "Participou bem. Não foi highlight vazio, foi presença útil na luta.",
        )

    def lane_matchup(self, enemy_nick):
        return self._pick(
            f"Teu confronto direto é o {enemy_nick}. Lê o padrão dele cedo e puxa a wave pro teu lado se a troca ficar ruim.",
            f"O cara na tua frente é o {enemy_nick}. Descobre logo onde tu ganha a troca e para de bater por bater.",
            f"Lane definida contra {enemy_nick}. Se não tiver certeza da troca, controla a wave primeiro e luta depois.",
        )

    def low_farm(self, cs, minutes):
        if self._is_hardcore():
            return self._pick(
                f"{cs} de CS com {int(minutes)} minutos é feio demais. Para de sonhar com fight e vai trabalhar nessa wave.",
                f"Esse farm tá horroroso: {cs} aos {int(minutes)}. Menos ego, mais minion, porque tu tá se afundando sozinho.",
                f"Tu largou dinheiro no mapa até demais. {cs} CS em {int(minutes)} minutos não é azar, é execução ruim.",
            )
        return self._pick(
            f"Teu farm tá uma tristeza: {cs} CS em {int(minutes)} minutos. Para de caçar play aleatória e recompra teu jogo no minion.",
            f"{cs} de farm com {int(minutes)} minutos é muito pouco, meu mano. Arruma essa wave e para de doar recurso de graça.",
            f"Tá faltando disciplina. Esse {cs} CS aos {int(minutes)} minutos pede menos ego e mais last hit.",
        )

    def high_farm(self, cs, minutes):
        return self._pick(
            f"Aí sim, {cs} de farm em {int(minutes)} minutos. Mantém essa linha que o mapa vai começar a te respeitar.",
            f"Farm forte: {cs} CS aos {int(minutes)}. Continua jogando em cima da wave que o ouro vem sozinho.",
            f"Tá farmando como gente grande. {cs} creeps na conta e pressão boa pra converter em item.",
        )

    def low_vision(self, wards):
        if self._is_hardcore():
            return self._pick(
                f"{wards} de visão? Tá querendo jogar no escuro e culpar os outros depois. Compra controle e vira gente.",
                f"Esse placar de visão em {wards} é preguiça travestida de confiança. Sem ward tu só tá flipando o mapa.",
                f"Visão patética até aqui. Para de entrar em mato no sentimento e começa a preparar o terreno direito.",
            )
        return self._pick(
            f"{wards} de visão até aqui é muito pouco. Compra controle e para de entrar em zona escura como se fosse milagreiro.",
            f"Tá jogando cego, meu parceiro. Esse placar de visão em {wards} não sustenta lane nem objetivo.",
            f"Visão fraca. Sem ward tu só tá apostando, e coach nenhum salva aposta burra no escuro.",
        )

    def armor_warning(self, player_name):
        return self._pick(
            f"O {player_name} já fechou armadura pesada. Ajusta tua build e entra com penetração, senão teu dano morre ali.",
            f"Olha o tab: {player_name} já tá blindado. Se tu insistir em build seca, vai bater e não vai acontecer nada.",
            f"{player_name} bufou na armadura. Prepara penetração física porque agora força bruta sozinha não resolve.",
        )

    def magic_resist_warning(self, player_name):
        return self._pick(
            f"{player_name} já botou resistência mágica. Se teu dano é AP, prepara penetração e para de fingir que vai atravessar isso no abraço.",
            f"O {player_name} fechou MR. Ajusta a loja depois da base porque teu burst cru vai perder valor.",
            f"Tem resistência mágica do lado deles no {player_name}. Sem item certo, tu só vai coçar essa barra de vida.",
        )

    def anti_heal_warning(self, player_name):
        return self._pick(
            f"{player_name} comprou corta-cura. Se tua luta depende de sustain, respeita e escolhe melhor o momento de entrar.",
            f"O {player_name} já tá com anti-heal. Não estica troca achando que vampirismo vai te carregar.",
            f"Tem redução de cura na mão do {player_name}. Joga a fight com mais critério porque tua recuperação caiu bastante.",
        )

    def self_kill(self, victim):
        return self._pick(
            f"Boa, matou o {victim}. Agora empurra essa wave ou some do mapa, mas não entrega o reset de volta.",
            f"Abate limpo no {victim}. Cobra recurso, arruma visão e transforma isso em vantagem de verdade.",
            f"Tu puniu o {victim} bem agora. Não comemora parado; converte esse espaço em farm, placa ou reset.",
        )

    def self_death_pve(self):
        return self._pick(
            "Tu morreu pro mapa de graça. Limpa a cabeça e volta mais disciplinado porque isso entrega tempo pro inimigo.",
            "Execução boba pra PvE. Agora para de forçar sem recurso e recompõe teu jogo com calma.",
            "Morrer pra torre ou ambiente é presente barato pros caras. Reseta a mente e volta sem tilt.",
        )

    def self_death_enemy(self, killer):
        if self._is_hardcore():
            return self._pick(
                f"O {killer} te cobrou porque tu entrou igual maluco. Agora segura teu ego e para de dar essa janela ridícula.",
                f"Tu morreu pro {killer} porque jogou torto. Respeita a lane, recompra no farm e não repete a burrada.",
                f"Essa morte pro {killer} foi toda tua. Ajusta posição, tempo e recurso antes de pensar em peitar de novo.",
            )
        return self._pick(
            f"O {killer} te puniu porque tu entrou torto. Respira, recua a pressão e espera janela boa pra responder.",
            f"Tu morreu pro {killer} e a rota entortou. Joga no seguro agora e recompra a lane no farm.",
            f"Essa morte pro {killer} foi ganância ou leitura ruim. Ajusta tua posição e para de dar a mesma janela.",
        )

    def ally_pve_death(self, victim, pve):
        return self._pick(
            f"O {victim} se entregou pra {pve}. Aproveita o tempo no mapa porque os caras também ficaram sem recurso ali.",
            f"Nosso lado perdeu o {victim} pra {pve}. Não entra no desespero; organiza wave e segura o prejuízo.",
            f"{victim} foi de base pra {pve}. Respira e joga a próxima janela direito pra não virar efeito cascata.",
        )

    def enemy_pve_death(self, victim, pve):
        return self._pick(
            f"O inimigo {victim} passou vergonha pra {pve}. Usa esse tempo e aperta o mapa agora.",
            f"{victim} morreu pra {pve}. Boa, porque isso abriu uma janela limpa pra pressionar.",
            f"Os caras perderam o {victim} pra {pve}. Se mexe no mapa antes que esse presente expire.",
        )

    def ally_death(self, victim, killer):
        return self._pick(
            f"O {victim} caiu pro {killer}. Não compra a mesma luta torta agora; reorganiza a wave e espera número.",
            f"Nosso lado perdeu o {victim} pro {killer}. Segura a ansiedade e protege o mapa até o respawn encaixar.",
            f"{killer} puniu o {victim}. Sem tilt: arruma visão e evita entregar sequência nessa mesma área.",
        )

    def enemy_death(self, killer, victim):
        return self._pick(
            f"Boa, o {killer} derrubou o {victim}. Usa essa vantagem pra avançar visão ou arrancar recurso.",
            f"O {victim} caiu e o mapa abriu. Se posiciona direito e cobra objetivo ou estrutura.",
            f"Menos um deles, {victim} foi pro chão. Não dispersa agora; aproveita a janela e acelera o mapa.",
        )

    def first_blood(self):
        return self._pick(
            "First Blood na conta. Agora controla a emoção e usa essa vantagem antes que ela evapore no mapa.",
            "Saiu o primeiro abate. Quem ler melhor o reset e a wave agora toma conta do jogo cedo.",
            "Primeiro sangue rolou. Não vira bagunça: converte essa vantagem em tempo, recurso e pressão.",
        )

    def self_multikill(self, kill_streak):
        if kill_streak == 2:
            return self._pick(
                "Double kill teu. Mantém a calma e cobra o mapa, porque agora o jogo tá pedindo conversão, não ego.",
                "Dois abatidos na conta. Boa, mas usa isso pra quebrar estrutura ou objetivo antes de dispersar.",
            )
        if kill_streak == 3:
            return self._pick(
                "Triple kill. Luta tua, então já chama mapa e fecha a conta antes que eles respawnem.",
                "Três no chão por tua causa. Agora empurra com disciplina e transforma isso em algo permanente.",
            )
        if kill_streak == 4:
            return self._pick(
                "Quadra kill. Se der o penta, pega; se não der, fecha a play com objetivo e não joga fora a vantagem.",
                "Quatro abatidos. Excelente, mas teu trabalho agora é garantir mapa, não só caçar highlight.",
            )
        return self._pick(
            "Penta kill, animal. Agora fecha o jogo com cabeça no lugar porque esse tipo de fight decide partida.",
            "Cinco no chão. O highlight veio, então aproveita e termina o mapa sem inventar moda.",
        )

    def enemy_multikill(self, killer, kill_streak):
        if kill_streak == 2:
            if self._is_hardcore():
                return self._pick(
                    f"O {killer} pegou double kill e vocês ainda vão insistir em entrar picado? Junta essa bagunça e mata o tempo dele.",
                    f"Double kill pro {killer}. Para de doar luta isolada pra esse cara e organiza a próxima fight com cérebro.",
                )
            return self._pick(
                f"O {killer} pegou double kill. Segura a onda, não dá mais reset pra esse cara e agrupa melhor a próxima luta.",
                f"Double kill pro {killer}. Respeita o spike dele e para de entrar isolado nessa região.",
            )
        if self._is_hardcore():
            return self._pick(
                f"O {killer} já tá com {kill_streak} kills e vocês ainda querem duelo seco. Acorda e joga por visão, número e disciplina.",
                f"{killer} virou problema real. Para de peitar no braço e quebra o ritmo dele com mapa e setup decente.",
            )
        return self._pick(
            f"O {killer} já tá com {kill_streak} kills seguidas. Agora é visão, número e disciplina; duelo seco virou loucura.",
            f"{killer} escalou forte na fight. Não compra 1v1 torto, organiza recurso e mata esse tempo dele no mapa.",
        )

    def elder_dragon(self, is_ally):
        if is_ally:
            return self._pick(
                "Ancião nosso. Agora é jogar junto e apertar o gatilho na primeira janela boa, porque esse buff fecha partida.",
                "Dragão Ancião na mão. Agrupa, força visão e usa a execução pra acabar com essa graça deles.",
            )
        return self._pick(
            "Os caras pegaram o Ancião. Recuo e disciplina agora, porque qualquer erro vira execução na tua cara.",
            "Ancião deles. Para de sonhar com engage torta e joga debaixo de visão até esse buff passar ou a janela aparecer.",
        )

    def dragon_control(self, dragon_name, is_ally, drags, killer):
        if drags == 3:
            return self._pick(
                f"{'Nosso' if is_ally else 'Deles'} {dragon_name} e agora tem ponto de alma na mesa. Prepara o mapa desde já porque o próximo rio vale demais.",
                f"O {killer} garantiu o dragão {dragon_name} e deixou {'a gente' if is_ally else 'eles'} no ponto de alma. A próxima rotação precisa ser limpa.",
            )
        if drags >= 4:
            return self._pick(
                f"Alma do dragão {dragon_name} {'pra nós' if is_ally else 'pra eles'}. Isso muda a partida inteira, então ajusta a fight em cima desse bônus.",
                f"Deu alma de {dragon_name} {'do nosso lado' if is_ally else 'pros caras'}. Agora toda decisão tem que respeitar esse spike.",
            )
        return self._pick(
            f"Dragão {dragon_name} {'na nossa conta' if is_ally else 'pra eles'}. Já pensa no próximo setup de rio porque ninguém ganha objetivo no improviso.",
            f"O {killer} pegou o dragão {dragon_name}. Usa essa informação pra organizar visão e tempo antes do próximo spawn.",
        )

    def baron_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Barão nosso na mão do {killer}. Agora faz o básico bem feito: reseta, organiza side e pressiona sem jogar buff fora.",
                f"O {killer} garantiu o Barão. Usa essa janela pra sufocar o mapa, não pra correr atrás de kill inútil.",
            )
        return self._pick(
            f"Barão pro lado deles com o {killer}. Respira, limpa wave e para de comprar fight fora de posição.",
            f"O {killer} fechou o Barão pros caras. Defende com paciência e não entrega mais recurso no desespero.",
        )

    def horde_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Vastilarvas nossas com o {killer}. Agora cobra placa e estrutura cedo, porque esse recurso precisa virar ouro.",
                f"O {killer} puxou as larvas. Acelera pressão de torre e joga em cima dessa janela antes que esfrie.",
            )
        return self._pick(
            f"O {killer} levou as vastilarvas pros caras. Respeita o dano em torre e não larga estrutura de graça.",
            f"Larvas do vazio do lado deles. Fica esperto com push cedo porque isso vai bater forte nas barricadas.",
        )

    def herald_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Arauto nosso com o {killer}. Planeja onde quebrar o mapa e usa isso no timing certo.",
                f"O {killer} garantiu o Arauto. Não solta de qualquer jeito; escolhe a rota que mais abre visão e espaço.",
            )
        return self._pick(
            f"O {killer} pegou o Arauto. Respeita a próxima pressão de rota e protege placa onde der.",
            f"Arauto deles. Guarda visão e leitura de side porque esse bicho vai tentar abrir teu mapa cedo.",
        )

    def turret_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Torre no chão pelo {killer}. Mapa abriu, então avança visão e cobra mais recurso nessa região.",
                f"O {killer} quebrou estrutura. Boa, agora ocupa o espaço e não devolve o controle de graça.",
            )
        return self._pick(
            f"Eles levaram uma torre com o {killer}. Ajusta a visão e respeita o mapa mais aberto daqui pra frente.",
            f"Torre perdida pro lado do {killer}. Agora tu precisa ler melhor as entradas porque a selva ficou mais exposta.",
        )

    def neutral_turret_taken(self):
        return self._pick(
            "Uma torre caiu no caos do mapa. Lê a side que abriu e se posiciona antes da próxima onda.",
            "Estrutura destruída. Agora o mapa muda de formato, então para de andar no automático.",
        )

    def inhibitor_taken(self, killer, is_ally):
        if is_ally:
            return self._pick(
                f"Inibidor nosso com o {killer}. Usa a pressão de super minion pra preparar Barão, alma ou fim de jogo.",
                f"O {killer} abriu inibidor. Agora joga em volta da lane pressionada e força os caras a responderem mal.",
            )
        return self._pick(
            f"Inibidor perdido pro {killer}. Segura a side com calma e não entrega o resto do mapa no desespero.",
            f"O {killer} quebrou o inibidor. Agora administra os supers direito e espera a próxima janela de resposta.",
        )

    def draft_enemy_locked(self, champion_name):
        return self._pick(
            f"Os caras travaram {champion_name}. Já lê o padrão dessa lane e não escolhe no piloto automático.",
            f"{champion_name} apareceu do lado deles. Guarda isso porque muda troca, tempo e janela de erro.",
            f"Confirmaram {champion_name}. Agora monta tua resposta direito e para de pensar só no highlight.",
        )

    def draft_pick_confirmed(self, champion_name):
        return self._pick(
            f"Tu travou {champion_name}. Então joga como quem escolheu com intenção, não como quem clicou por costume.",
            f"{champion_name} na tua mão. Agora a gente define runa, feitiço e plano pra essa lane não começar torta.",
            f"Escolha fechada em {champion_name}. Boa, agora escuta a call e entra no jogo com objetivo claro.",
        )

    def draft_counter_tip(self, champion_name):
        tips = {
            "Zed": f"{champion_name} quer punir erro curto e sumir da tela. Segura a wave perto de ti e já pensa em defesa cedo pra não virar alvo livre.",
            "Yasuo": f"{champion_name} só fica confortável se tu der wave solta. Trava o ritmo, respeita o all-in cedo e cobra ele quando a rota estiver controlada.",
            "Darius": f"{champion_name} ganha quando tu troca colado sem critério. Kiteia, controla espaço e chama recurso antes de peitar essa lane de frente.",
            "Master Yi": f"{champion_name} quer fight bagunçada e alvo sem controle. Guarda CC, organiza entrada e não entrega reset de graça pra esse maluco.",
            "Blitzcrank": f"{champion_name} quer uma janela só. Não dá cara sem wave, usa a tropa a teu favor e pune o cooldown quando ele errar o braço.",
            "Vayne": f"{champion_name} escala se tu deixa respirar. Marca posição dela cedo e guarda recurso pra quebrar a fight antes dela andar livre.",
        }
        return tips.get(champion_name)

    def draft_comp_plan(self, plan_key, champion_name):
        plans = {
            "high_cc": self._pick(
                f"Os caras tão lotados de controle. Deixa {champion_name} com tenacidade ou Purificar e joga fight entrando no tempo certo, não no desespero.",
                f"Comp deles tem cadeia de CC pra te travar inteiro. Ajusta runa defensiva agora e respeita a primeira engage.",
            ),
            "assassins": self._pick(
                f"Tem assassino demais do outro lado. Com {champion_name}, pensa em Exaustão ou ferramenta defensiva porque tua janela de erro ficou curta.",
                f"A comp deles quer explodir alvo mole. Se tu vai de {champion_name}, prepara proteção e joga mais por posicionamento do que por ego.",
            ),
            "tanks": self._pick(
                f"Os caras vieram de front line pesada. Com {champion_name}, tu precisa de dano contínuo e paciência de luta, não de all-in torto.",
                f"Comp deles é tanquezada pura. Ajusta tua runa pra fight longa e pensa desde cedo em item pra atravessar essa parede.",
            ),
            "standard": self._pick(
                f"A comp deles é mais padrão. Então usa {champion_name} pra jogar o básico forte: lane limpa, reset bom e entrada no objetivo no tempo.",
                f"Não tem pegadinha gigante nessa draft. Com {champion_name}, vence quem erra menos execução, então organiza teu early direito.",
            ),
        }
        return plans[plan_key]
