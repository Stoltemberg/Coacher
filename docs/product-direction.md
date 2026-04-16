# Product Direction

Atualizado em 15 de abril de 2026.

## Tese do produto

O Coacher nao deve ser "um assistente que fala igual o Minerva".

Ele deve ser "um coach de LoL em tempo real cuja interface e a persona do Minerva".

Isso muda a prioridade do produto:

- primeiro: utilidade competitiva;
- depois: entrega com personalidade;
- nunca: personalidade sem direcao.

## Diagnostico do estado atual

Hoje o produto ja tem tres ativos fortes:

- integra com o cliente do LoL e com dados em tempo real;
- tem uma camada de voz e reacao imediata;
- ja assume uma persona forte e memoravel.

Mas ainda tem tres lacunas centrais:

- a experiencia e mais reativa do que metodica;
- a persona esta espalhada em strings soltas, sem sistema;
- a maior parte das falas ainda privilegia impacto emocional sobre instrucao acionavel.

## Principios para evolucao

### 1. Toda fala precisa ensinar

A call pode xingar, debochar e cobrar, mas precisa deixar uma decisao mais clara para o jogador.

### 2. Minerva nao e decoracao

A voz precisa estar no produto inteiro:
- timing;
- escolha de vocabulario;
- ritmo;
- confianca;
- cobranca.

### 3. O produto precisa ter metodo

O usuario deve sentir que existe uma linha de coaching por tras da zoeira:
- o que priorizar no draft;
- como jogar a lane;
- quando ceder;
- quando punir;
- como resetar depois de erro.

### 4. Menos narracao, mais call

Se o sistema so descreve o evento, ele informa.
Se ele diz o que muda e o que fazer, ele coacha.

## Estrutura recomendada para o motor de fala

Separar a geracao de mensagens em quatro camadas:

1. `evento`
   - kill, death, objective, draft pick, low cs, poor vision
2. `leitura`
   - o que isso significa na partida
3. `acao`
   - o que o jogador precisa fazer agora
4. `persona`
   - como o Minerva entrega essa call

Essa separacao evita que a identidade fique presa em centenas de strings fixas e facilita calibrar intensidade sem perder o personagem.

## Prioridades de produto

### Fase 1 - Consertar a fundacao

- corrigir bugs criticos do `CoachBrain`;
- fazer toggles controlarem o comportamento real;
- alinhar dependencias e configuracao de TTS;
- limpar ponte Python/JS mais fragil.

Sem isso, qualquer melhoria de persona fica instavel.

### Fase 2 - Transformar reacao em coaching

- revisar todas as falas de jogo com a formula:
  - leitura;
  - cobranca;
  - acao;
- reduzir textos que so descrevem evento;
- adicionar plano por fase:
  - draft;
  - lane;
  - mid game;
  - late game;
- diferenciar calls urgentes, importantes e ambiente.

### Fase 3 - Productizar o Minerva

- criar um catalogo central de voz;
- separar modos de intensidade;
- criar regras de timing e cooldown por categoria de fala;
- incluir memoria de erros recorrentes do jogador;
- gerar resumo pos-jogo com linguagem do Minerva.

## Memoria do jogador

A memoria do jogador precisa funcionar como uma camada simples entre o jogo ao vivo e o resumo final.

Fluxo recomendado:

1. `start_match(...)`
   - inicia a memoria da partida;
   - grava contexto inicial como nome do jogador, campeao, rota e identificador da partida.
2. `record_event(...)`
   - registra eventos relevantes do jogo;
   - exemplo: abate, morte, objetivo, alerta de item, call importante.
3. `record_evaluation(...)`
   - registra avaliacoes estruturadas;
   - exemplo: farm abaixo do ideal, visao ruim, posicao arriscada, bom controle de objetivo.
4. `end_match(...)`
   - fecha a partida;
   - gera o resumo final;
   - arquiva o historico da partida.

## Resumo pos-jogo

O resumo pos-jogo deve sair em formato estruturado, para depois poder alimentar:

- a UI;
- a voz do Minerva;
- o historico do jogador;
- futuras metricas de melhoria.

Formato recomendado:

- `headline`
- `opening`
- `strengths`
- `improvements`
- `key_moments`
- `next_steps`
- `coach_note`

Esse resumo nao deve apenas dizer se o jogo foi ganho ou perdido. Ele precisa apontar:

- o que o jogador fez bem;
- o que mais custou a partida;
- qual padrao se repetiu;
- qual e o foco da proxima fila.

## API base prevista

O modulo `src/core/player_memory.py` deve expor uma API simples e clara:

- `PlayerMemory`
- `MemoryEntry`
- `MatchMemory`
- `PostGameSummary`

Essa camada precisa continuar independente do restante do motor, para que `CoachBrain` passe a registrar memoria sem perder estabilidade.

## Primeiros entregaveis recomendados

### 1. Biblioteca de voz

Criar uma camada dedicada a persona com:
- pilares de linguagem;
- frases-modelo;
- templates por situacao;
- variacoes por intensidade.

### 2. Taxonomia de calls

Classificar as falas em:
- `draft`
- `lane`
- `macro`
- `objective`
- `economy`
- `discipline`
- `snowball`
- `recovery`

### 3. Politica de qualidade de call

Uma fala boa do Coacher precisa responder pelo menos duas destas tres perguntas:

- o que aconteceu?
- por que importa?
- o que fazer agora?

Se responder so a primeira, e narracao.

## Exemplo de evolucao

### Antes

"Putz, morreu pro cara de novo."

### Depois

"Tu morreu de novo porque entrou sem visao. Para de peitar essa wave no escuro e guarda teu avancar pro proximo ciclo com ward."

### Antes

"Fizeram dragao."

### Depois

"Cederam o rio cedo e os caras pegaram o dragao de graca. Agora reseta visao e nao entrega a mesma entrada no proximo spawn."

## Resultado desejado

Quando estiver no caminho certo, o Coacher vai parecer:

- um ex-pro lendo tua partida em tempo real;
- um amigo grosseiro, mas util;
- um cobrador que te empurra para a decisao correta;
- uma ferramenta com assinatura propria, nao um overlay generico.

## Relacao com o codigo atual

Arquivos que devem guiar a proxima etapa:

- `src/core/coach_brain.py`
- `src/core/champ_select.py`
- `src/core/assistant.py`
- `src/app.py`

Esses arquivos hoje concentram quase toda a experiencia de coaching e sao o ponto natural para a proxima rodada de refatoracao.
