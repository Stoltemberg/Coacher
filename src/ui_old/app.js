const COACH_TAXONOMY = [
    {
        id: 'draft',
        title: 'Draft',
        kicker: 'Leitura da tela',
        description: 'Bans, picks e condição de vitória antes da partida começar. Aqui o Minerva define se a lane é para ganhar, punir ou sobreviver.',
        signals: ['Bans críticos', 'Matchup', 'Plano de rota'],
        accent: 'var(--blue)'
    },
    {
        id: 'lane',
        title: 'Lane',
        kicker: 'Micro e disciplina',
        description: 'Troca, estado da wave, pressão e janela para punir erro. O foco é não entregar espaço de graça.',
        signals: ['Wave control', 'Trading', 'Punição de erro'],
        accent: 'var(--teal)'
    },
    {
        id: 'macro',
        title: 'Macro',
        kicker: 'Mapa e tempo',
        description: 'Movimento antes do inimigo, rotação, visão e leitura de espaço. O coach cobra decisão, não passeio.',
        signals: ['Rotação', 'Tempo de mapa', 'Set-up'],
        accent: '#90f3a5'
    },
    {
        id: 'objective',
        title: 'Objetivo',
        kicker: 'Janelas de objetivo',
        description: 'Dragão, Barão, Arauto, torres e prioridade de luta ou crossmap. Se o objetivo está livre, o Minerva quer resposta na hora.',
        signals: ['Dragão', 'Barão', 'Arauto'],
        accent: 'var(--amber)'
    },
    {
        id: 'economy',
        title: 'Economia',
        kicker: 'Recursos e spike',
        description: 'Farm, ouro, itemização e eficiência do jogador na janela atual. Aqui a cobrança é matemática, não narrativa.',
        signals: ['CS por minuto', 'Gold diff', 'Item spike'],
        accent: 'var(--amber)'
    },
    {
        id: 'recovery',
        title: 'Recuperação',
        kicker: 'Consertar sem chorar',
        description: 'Reset após erro, plano de estabilização e rotina para voltar ao jogo sem desandar a partida inteira.',
        signals: ['Reset mental', 'Stop dying', 'Plano de volta'],
        accent: 'var(--rose)'
    }
];

const CATEGORY_PRESETS = {
    balanced: ['draft', 'lane', 'macro', 'objective', 'economy', 'recovery'],
    draft: ['draft', 'lane', 'objective', 'economy'],
    macro: ['lane', 'macro', 'objective', 'economy', 'recovery'],
    recovery: ['macro', 'objective', 'economy', 'recovery']
};

const DEFAULT_CATEGORY_FILTERS = {
    draft: true,
    lane: true,
    macro: true,
    objective: true,
    economy: true,
    recovery: true
};

const POSTGAME_DEFAULT = {
    title: 'Aguardando fim de jogo',
    result: 'Sem dados',
    duration: '--',
    scoreline: '--',
    focus: '--',
    confidence: '--',
    reads: [
        'Quando a partida terminar, o Minerva vai resumir o que decidiu a vitória ou a derrota.',
        'Este espaço mostra padrões como farm baixo, visão fraca, overextend e timings perdidos.',
        'O próximo passo é transformar isso em memória reutilizável entre partidas.'
    ],
    memory: [
        {
            title: 'Sem memória ainda',
            note: 'Nenhum padrão consolidado foi registrado nesta sessão.',
            tone: 'system'
        }
    ],
    timeline: [],
    insights: {
        headline: 'Sem leitura consolidada',
        opening: 'Assim que a partida fechar, o coach organiza os principais sinais do jogo.',
        strengths: [],
        improvements: [],
        key_moments: [],
        next_steps: [],
        adaptive: {
            headline: '',
            repeated_patterns: [],
            recovered_patterns: [],
            phase_pressure: []
        }
    }
};

const JUNGLE_DEFAULT = {
    enemy_jungler_name: null,
    enemy_jungler_champion: null,
    our_jungler_name: null,
    last_seen_clock: '--:--',
    last_seen_source: null,
    probable_side: 'unknown',
    confidence: 0,
    first_gank: null,
    objective_presence: {
        dragon: 0,
        herald: 0,
        baron: 0,
        horde: 0
    },
    notes: [],
    last_impacted_lane: 'unknown'
};

const phaseAliases = new Map([
    ['in game', 'Partida em Andamento'],
    ['ingame', 'Partida em Andamento'],
    ['game in progress', 'Partida em Andamento'],
    ['champ select', 'Seleção de Campeões'],
    ['champselect', 'Seleção de Campeões'],
    ['lobby', 'Lobby'],
    ['post game', 'Pós-jogo'],
    ['postgame', 'Pós-jogo'],
    ['game over', 'Pós-jogo'],
    ['end of game', 'Pós-jogo']
]);

const phaseFocusMap = new Map([
    ['Lobby', 'draft'],
    ['Seleção de Campeões', 'draft'],
    ['Partida em Andamento', 'lane'],
    ['Pós-jogo', 'recovery']
]);

const COACH_MODE_META = {
    draft: {
        label: 'Draft',
        copy: 'O Minerva está lendo draft, matchups e condição de vitória antes da lane existir.',
        taxonomy: 'draft'
    },
    lane: {
        label: 'Lane',
        copy: 'O foco atual é troca, wave e disciplina de rota para não entregar espaço cedo.',
        taxonomy: 'lane'
    },
    economy: {
        label: 'Economia',
        copy: 'O coach está puxando farm, reset e build para recolocar teu ouro no trilho.',
        taxonomy: 'economy'
    },
    recovery: {
        label: 'Recovery',
        copy: 'O Minerva está em modo de contenção: menos ruído e mais correção do que está vazando.',
        taxonomy: 'recovery'
    },
    macro: {
        label: 'Macro',
        copy: 'A prioridade agora é mapa, visão e objetivo. O coach quer decisão e rotação limpa.',
        taxonomy: 'macro'
    }
};

const uiState = {
    activeTaxonomy: 'draft',
    currentPhase: 'Lobby',
    currentSummary: { ...POSTGAME_DEFAULT },
    matchIntel: [],
    postgameMemory: [],
    jungleIntel: { ...JUNGLE_DEFAULT },
    auth: {
        configured: false,
        authenticated: false,
        message: '',
        pending_confirmation: false,
        user: null,
        mode: 'login'
    },
    settings: {
        voice_preset: 'hardcore',
        voice_personality: 'minerva',
        category_filters: { ...DEFAULT_CATEGORY_FILTERS },
        coach_mode: 'draft'
    }
};

Object.assign(COACH_MODE_META, {
    draft: {
        label: 'Draft',
        copy: 'O painel est\u00e1 priorizando leitura de draft, matchup e condi\u00e7\u00e3o de vit\u00f3ria da tua pr\u00f3xima fila.',
        taxonomy: 'draft'
    },
    lane: {
        label: 'Lane',
        copy: 'O foco atual est\u00e1 no teu comportamento de lane, disciplina de troca e controle de espa\u00e7o.',
        taxonomy: 'lane'
    },
    economy: {
        label: 'Economia',
        copy: 'O painel est\u00e1 destacando farm, reset e itemiza\u00e7\u00e3o para mostrar como teu jogo escala.',
        taxonomy: 'economy'
    },
    recovery: {
        label: 'Recovery',
        copy: 'A leitura atual est\u00e1 concentrada em corre\u00e7\u00f5es, repeti\u00e7\u00e3o de erro e tua capacidade de recuperar a partida.',
        taxonomy: 'recovery'
    },
    macro: {
        label: 'Macro',
        copy: 'O painel est\u00e1 resumindo tua leitura de mapa, vis\u00e3o e timing de objetivo no momento atual.',
        taxonomy: 'macro'
    }
});

phaseAliases.set('champ select', 'Sele\u00e7\u00e3o de Campe\u00f5es');
phaseAliases.set('champselect', 'Sele\u00e7\u00e3o de Campe\u00f5es');
phaseAliases.set('post game', 'P\u00f3s-jogo');
phaseAliases.set('postgame', 'P\u00f3s-jogo');
phaseAliases.set('game over', 'P\u00f3s-jogo');
phaseAliases.set('end of game', 'P\u00f3s-jogo');
phaseFocusMap.set('Sele\u00e7\u00e3o de Campe\u00f5es', 'draft');
phaseFocusMap.set('P\u00f3s-jogo', 'recovery');

if (COACH_TAXONOMY[0]) {
    COACH_TAXONOMY[0].description = 'Bans, picks e condi\u00e7\u00e3o de vit\u00f3ria antes da partida come\u00e7ar. Aqui o coach define se a lane \u00e9 para ganhar, punir ou sobreviver.';
}
if (COACH_TAXONOMY[3]) {
    COACH_TAXONOMY[3].description = 'Drag\u00e3o, Bar\u00e3o, Arauto, torres e prioridade de luta ou crossmap. Se o objetivo est\u00e1 livre, o coach quer resposta na hora.';
}
POSTGAME_DEFAULT.reads = [
    'Quando a partida terminar, o coach vai resumir o que decidiu a vit\u00f3ria ou a derrota.',
    'Este espa\u00e7o mostra padr\u00f5es como farm baixo, vis\u00e3o fraca, overextend e timings perdidos.',
    'O pr\u00f3ximo passo \u00e9 transformar isso em mem\u00f3ria reutiliz\u00e1vel entre partidas.'
];

function createElement(tag, options = {}) {
    const el = document.createElement(tag);

    if (options.className) {
        el.className = options.className;
    }

    if (options.text !== undefined) {
        el.textContent = options.text;
    }

    if (options.attrs) {
        Object.entries(options.attrs).forEach(([key, value]) => {
            el.setAttribute(key, value);
        });
    }

    if (options.dataset) {
        Object.entries(options.dataset).forEach(([key, value]) => {
            el.dataset[key] = value;
        });
    }

    if (Array.isArray(options.children)) {
        options.children.forEach(child => {
            if (child) {
                el.appendChild(child);
            }
        });
    }

    return el;
}

function clearElement(element) {
    while (element && element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

function normalizeLookup(value) {
    return String(value || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .trim();
}

function repairDisplayText(value) {
    const text = String(value || '');
    if (!text) {
        return '';
    }

    return text
        .replace(/Ã§/g, 'ç')
        .replace(/Ã£/g, 'ã')
        .replace(/Ã¡/g, 'á')
        .replace(/Ã¢/g, 'â')
        .replace(/Ã /g, 'à')
        .replace(/Ã©/g, 'é')
        .replace(/Ãª/g, 'ê')
        .replace(/Ã­/g, 'í')
        .replace(/Ã³/g, 'ó')
        .replace(/Ã´/g, 'ô')
        .replace(/Ãµ/g, 'õ')
        .replace(/Ãº/g, 'ú')
        .replace(/Ã‰/g, 'É')
        .replace(/Ã“/g, 'Ó')
        .replace(/Ãš/g, 'Ú')
        .replace(/Ã/g, 'à')
        .replace(/Sessao/g, 'Sessão')
        .replace(/sessao/g, 'sessão')
        .replace(/autenticacao/g, 'autenticação')
        .replace(/Autenticacao/g, 'Autenticação')
        .replace(/historico/g, 'histórico')
        .replace(/Historico/g, 'Histórico')
        .replace(/evolucao/g, 'evolução')
        .replace(/Evolucao/g, 'Evolução')
        .replace(/configuracoes/g, 'configurações')
        .replace(/Configuracoes/g, 'Configurações')
        .replace(/condicao/g, 'condição')
        .replace(/Condicao/g, 'Condição')
        .replace(/selecao/g, 'seleção')
        .replace(/Selecao/g, 'Seleção')
        .replace(/campeoes/g, 'campeões')
        .replace(/Campeoes/g, 'Campeões')
        .replace(/itemizacao/g, 'itemização')
        .replace(/Itemizacao/g, 'Itemização')
        .replace(/visao/g, 'visão')
        .replace(/Visao/g, 'Visão')
        .replace(/rotacao/g, 'rotação')
        .replace(/Rotacao/g, 'Rotação')
        .replace(/correcoes/g, 'correções')
        .replace(/Correcoes/g, 'Correções')
        .replace(/repeticao/g, 'repetição')
        .replace(/Repeticao/g, 'Repetição')
        .replace(/recuperacao/g, 'recuperação')
        .replace(/Recuperacao/g, 'Recuperação')
        .replace(/pos-jogo/g, 'pós-jogo')
        .replace(/Pos-jogo/g, 'Pós-jogo')
        .replace(/maquina/g, 'máquina')
        .replace(/Memoria/g, 'Memória')
        .replace(/memoria/g, 'memória')
        .replace(/nao/g, 'não')
        .replace(/Nao/g, 'Não')
        .replace(/possivel/g, 'possível');
}

function normalizeText(value, fallback = '') {
    const text = value === undefined || value === null ? '' : String(value).trim();
    return repairDisplayText(text || fallback);
}

function normalizeTone(value) {
    const normalized = normalizeLookup(value);

    if (normalized === 'positive' || normalized === 'success') {
        return 'success';
    }

    if (normalized === 'negative' || normalized === 'urgent' || normalized === 'danger') {
        return 'urgent';
    }

    if (normalized === 'warning') {
        return 'warning';
    }

    if (normalized === 'system') {
        return 'system';
    }

    return 'normal';
}

function normalizePhase(phase) {
    const normalized = normalizeLookup(phase);
    return phaseAliases.get(normalized) || normalizeText(phase, 'Lobby');
}

function slugifyState(value, fallback) {
    const normalized = normalizeLookup(value).replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    return normalized || fallback;
}

function setBodyVisualState() {
    document.body.dataset.phase = slugifyState(uiState.currentPhase, 'lobby');
    document.body.dataset.mode = slugifyState(uiState.settings.coach_mode, 'draft');
    document.body.dataset.auth = uiState.auth.authenticated ? 'member' : 'guest';
    applyAuthShellState();
}

function applyAuthShellState() {
    const authShell = document.getElementById('auth-shell');
    const appShell = document.querySelector('.app-shell');
    const unlocked = Boolean(uiState.auth.authenticated);

    if (authShell) {
        authShell.style.display = unlocked ? 'none' : 'flex';
        authShell.style.pointerEvents = unlocked ? 'none' : 'auto';
        authShell.style.opacity = unlocked ? '0' : '1';
    }

    if (appShell) {
        appShell.style.filter = unlocked ? 'none' : 'blur(8px)';
        appShell.style.opacity = unlocked ? '1' : '0.15';
        appShell.style.pointerEvents = unlocked ? 'auto' : 'none';
        appShell.style.transform = unlocked ? 'none' : 'scale(0.985)';
    }
}

function setAuthMode(mode = 'login') {
    uiState.auth.mode = mode === 'signup' ? 'signup' : 'login';

    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    const submit = document.getElementById('auth-submit');
    const nameGroup = document.getElementById('auth-name-group');
    const password = document.getElementById('auth-password');

    if (title) {
        title.textContent = uiState.auth.mode === 'signup' ? 'Criar conta' : 'Entrar';
    }

    if (subtitle) {
        subtitle.textContent = uiState.auth.mode === 'signup'
            ? 'Crie tua conta para salvar memória e histórico entre partidas.'
            : 'Use tua conta para liberar o Coacher nesta máquina.';
    }

    if (submit) {
        submit.textContent = uiState.auth.mode === 'signup' ? 'Criar conta' : 'Entrar';
    }

    if (nameGroup) {
        const shouldShowName = uiState.auth.mode === 'signup';
        nameGroup.hidden = !shouldShowName;
        nameGroup.toggleAttribute('hidden', !shouldShowName);
        nameGroup.style.display = uiState.auth.mode === 'signup' ? 'flex' : 'none';
    }

    if (password) {
        password.autocomplete = uiState.auth.mode === 'signup' ? 'new-password' : 'current-password';
    }

    document.querySelectorAll('[data-auth-mode]').forEach(button => {
        button.classList.toggle('active', button.dataset.authMode === uiState.auth.mode);
    });

    if (subtitle) {
        subtitle.textContent = uiState.auth.mode === 'signup'
            ? 'Crie tua conta para salvar mem\u00f3ria e hist\u00f3rico entre partidas.'
            : 'Use tua conta para liberar o Coacher nesta m\u00e1quina.';
    }
}

function normalizeAuthSnapshot(snapshot = {}) {
    const user = snapshot.user && typeof snapshot.user === 'object' ? snapshot.user : null;
    return {
        configured: Boolean(snapshot.configured),
        authenticated: Boolean(snapshot.authenticated),
        pending_confirmation: Boolean(snapshot.pending_confirmation),
        message: normalizeText(snapshot.message, ''),
        user: user ? {
            email: normalizeText(user.email, ''),
            display_name: normalizeText(user.display_name, user.email || 'Jogador'),
        } : null
    };
}

function isPostGamePhase(phase) {
    const value = normalizeLookup(phase);
    return value.includes('post') || value.includes('pos') || value.includes('game over') || value.includes('end of game');
}

function getTaxonomyId(categoryId) {
    const normalized = normalizeLookup(categoryId);
    const match = COACH_TAXONOMY.find(category => category.id === normalized);
    return match ? match.id : null;
}

function inferTaxonomyFromText(value) {
    const normalized = normalizeLookup(value);

    if (!normalized) {
        return null;
    }

    if (normalized.includes('draft') || normalized.includes('pick') || normalized.includes('ban')) {
        return 'draft';
    }

    if (normalized.includes('objetivo') || normalized.includes('objective') || normalized.includes('dragao') || normalized.includes('barao') || normalized.includes('herald') || normalized.includes('arauto')) {
        return 'objective';
    }

    if (normalized.includes('econom') || normalized.includes('farm') || normalized.includes('ouro') || normalized.includes('gold') || normalized.includes('item')) {
        return 'economy';
    }

    if (normalized.includes('macro') || normalized.includes('mapa') || normalized.includes('rotacao') || normalized.includes('vision') || normalized.includes('visao')) {
        return 'macro';
    }

    if (normalized.includes('recovery') || normalized.includes('reset') || normalized.includes('recover') || normalized.includes('erro') || normalized.includes('death') || normalized.includes('mort')) {
        return 'recovery';
    }

    if (normalized.includes('lane') || normalized.includes('trade') || normalized.includes('wave') || normalized.includes('micro')) {
        return 'lane';
    }

    return null;
}

function buildChip(text, className = 'signal-chip') {
    return createElement('span', { className, text: normalizeText(text) });
}

function renderCoachTaxonomy() {
    const container = document.getElementById('coach-taxonomy-grid');
    if (!container) {
        return;
    }

    clearElement(container);

    const fragment = document.createDocumentFragment();

    COACH_TAXONOMY.forEach(category => {
        const card = createElement('article', {
            className: 'taxonomy-card',
            dataset: { category: category.id }
        });

        const badge = createElement('span', {
            className: 'taxonomy-badge',
            text: category.title
        });
        badge.style.setProperty('--taxonomy-accent', category.accent);

        const kicker = createElement('p', {
            className: 'taxonomy-kicker',
            text: category.kicker
        });

        const description = createElement('p', {
            className: 'taxonomy-description',
            text: category.description
        });

        const signals = createElement('div', { className: 'taxonomy-signals' });
        category.signals.forEach(signal => signals.appendChild(buildChip(signal)));

        card.appendChild(badge);
        card.appendChild(kicker);
        card.appendChild(description);
        card.appendChild(signals);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);
}

function renderCoachModePanel() {
    const pill = document.getElementById('coach-mode-pill');
    const copy = document.getElementById('coach-mode-copy');
    const modeKey = normalizeLookup(uiState.settings.coach_mode) || 'draft';
    const meta = COACH_MODE_META[modeKey] || COACH_MODE_META.draft;

    if (pill) {
        pill.textContent = meta.label;
        pill.dataset.mode = modeKey;
    }

    if (copy) {
        copy.textContent = meta.copy;
    }

    setBodyVisualState();
}

function normalizeMemoryEntry(entry) {
    if (!entry) {
        return null;
    }

    if (typeof entry === 'string') {
        return {
            title: 'Memória',
            note: entry,
            tone: 'normal'
        };
    }

    return {
        title: normalizeText(entry.title, 'Memória'),
        note: normalizeText(entry.note, ''),
        tone: normalizeTone(entry.tone),
        meta: normalizeText(entry.meta || entry.category || entry.phase || entry.kind, '')
    };
}

function normalizeTimelineEntry(entry) {
    if (!entry || typeof entry !== 'object') {
        return null;
    }

    return {
        clock: normalizeText(entry.clock, '--:--'),
        phase: normalizeText(entry.phase, ''),
        category: normalizeText(entry.category, ''),
        severity: normalizeTone(entry.severity),
        kind: normalizeText(entry.kind, 'event'),
        text: normalizeText(entry.text, ''),
        impact: normalizeText(entry.impact, ''),
        priority: normalizeText(entry.priority, ''),
        metadata: entry.metadata && typeof entry.metadata === 'object' ? entry.metadata : {}
    };
}

function normalizeInsights(insights) {
    const next = insights && typeof insights === 'object' ? insights : {};
    const adaptive = next.adaptive && typeof next.adaptive === 'object' ? next.adaptive : {};
    return {
        headline: normalizeText(next.headline, POSTGAME_DEFAULT.insights.headline),
        opening: normalizeText(next.opening, POSTGAME_DEFAULT.insights.opening),
        strengths: Array.isArray(next.strengths) ? next.strengths.filter(Boolean) : [],
        improvements: Array.isArray(next.improvements) ? next.improvements.filter(Boolean) : [],
        key_moments: Array.isArray(next.key_moments) ? next.key_moments.filter(Boolean) : [],
        next_steps: Array.isArray(next.next_steps) ? next.next_steps.filter(Boolean) : [],
        adaptive: {
            headline: normalizeText(adaptive.headline, ''),
            repeated_patterns: Array.isArray(adaptive.repeated_patterns) ? adaptive.repeated_patterns.filter(Boolean) : [],
            recovered_patterns: Array.isArray(adaptive.recovered_patterns) ? adaptive.recovered_patterns.filter(Boolean) : [],
            phase_pressure: Array.isArray(adaptive.phase_pressure) ? adaptive.phase_pressure.filter(Boolean) : []
        }
    };
}

function normalizeJungleIntel(payload) {
    const next = payload && typeof payload === 'object' ? payload : {};
    return {
        ...JUNGLE_DEFAULT,
        ...next,
        objective_presence: {
            ...JUNGLE_DEFAULT.objective_presence,
            ...(next.objective_presence || {})
        },
        notes: Array.isArray(next.notes) ? next.notes : [],
        first_gank: next.first_gank && typeof next.first_gank === 'object' ? next.first_gank : null
    };
}

function updatePlayerDashboardHighlights() {
    const dominant = document.getElementById('player-signal-dominant');
    const headlineMini = document.getElementById('player-headline-mini');
    const nextFocus = document.getElementById('player-next-focus');
    const leagueStatusMain = document.getElementById('league-status-main');
    const phaseCopy = document.getElementById('player-phase-copy');

    const insights = normalizeInsights(uiState.currentSummary.insights || {});
    const headline = normalizeText(uiState.currentSummary.title, 'Sem leitura ainda');
    const focus = normalizeText(uiState.currentSummary.focus, '--');
    const nextStep = insights.next_steps[0] || insights.improvements[0] || 'Aguardando dados';

    if (dominant) dominant.textContent = focus;
    if (headlineMini) headlineMini.textContent = headline;
    if (nextFocus) nextFocus.textContent = normalizeText(nextStep, 'Aguardando dados');
    if (leagueStatusMain) leagueStatusMain.textContent = normalizeText(document.getElementById('league-status')?.textContent, 'Aguardando League...');
    if (phaseCopy) phaseCopy.textContent = uiState.currentPhase;
}

function renderMemoryFeed(entries) {
    const container = document.getElementById('player-memory-feed');
    if (!container) {
        return;
    }

    clearElement(container);

    const normalizedEntries = Array.isArray(entries)
        ? entries.map(normalizeMemoryEntry).filter(Boolean)
        : [];

    if (!normalizedEntries.length) {
        container.appendChild(createElement('div', {
            className: 'postgame-empty',
            text: 'A memória vai guardar padrões como farm baixo, visão fraca, overextend e timings de objetivo.'
        }));
        return;
    }

    const fragment = document.createDocumentFragment();
    normalizedEntries.forEach(entry => {
        const item = createElement('article', {
            className: `memory-item ${entry.tone}`
        });

        item.appendChild(createElement('h5', { text: entry.title }));

        if (entry.meta) {
            item.appendChild(createElement('span', {
                className: 'memory-meta',
                text: entry.meta
            }));
        }

        item.appendChild(createElement('p', { text: entry.note }));
        fragment.appendChild(item);
    });

    container.appendChild(fragment);
}

function renderPostGameReads(reads) {
    const container = document.getElementById('postgame-reads');
    if (!container) {
        return;
    }

    clearElement(container);

    const normalizedReads = Array.isArray(reads) ? reads.filter(Boolean) : [];

    if (!normalizedReads.length) {
        container.appendChild(createElement('div', {
            className: 'postgame-empty',
            text: 'Quando a partida terminar, o coach detalha aqui as leituras mais importantes sem virar texto solto.'
        }));
        return;
    }

    const fragment = document.createDocumentFragment();
    normalizedReads.forEach((read, index) => {
        const row = createElement('div', { className: 'summary-item' });
        row.appendChild(createElement('span', {
            className: 'summary-index',
            text: String(index + 1).padStart(2, '0')
        }));
        row.appendChild(createElement('p', {
            text: normalizeText(read)
        }));
        fragment.appendChild(row);
    });

    container.appendChild(fragment);
}

function renderPostGameInsights(insights) {
    const container = document.getElementById('postgame-insights');
    if (!container) {
        return;
    }

    clearElement(container);

    const normalized = normalizeInsights(insights);
    const groups = [
        { title: 'Abertura', items: [normalized.opening], tone: 'system' },
        { title: 'Pontos fortes', items: normalized.strengths, tone: 'success' },
        { title: 'Ajustes', items: normalized.improvements, tone: 'urgent' },
        { title: 'Momentos-chave', items: normalized.key_moments, tone: 'warning' },
        { title: 'Próximo treino', items: normalized.next_steps, tone: 'normal' }
    ].filter(group => group.items.length);

    if (!groups.length) {
        container.appendChild(createElement('div', {
            className: 'postgame-empty',
            text: 'Os insights da partida aparecem aqui assim que o resumo final é montado.'
        }));
        return;
    }

    const fragment = document.createDocumentFragment();
    groups.forEach(group => {
        const card = createElement('article', {
            className: `insight-card ${group.tone}`
        });
        card.appendChild(createElement('h5', { text: group.title }));

        const list = createElement('div', { className: 'insight-list' });
        group.items.forEach(item => {
            list.appendChild(createElement('p', {
                className: 'insight-item',
                text: normalizeText(item)
            }));
        });

        card.appendChild(list);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);
}

function renderAdaptiveInsights(insights) {
    const container = document.getElementById('postgame-adaptive');
    if (!container) {
        return;
    }

    clearElement(container);

    const normalized = normalizeInsights(insights);
    const adaptive = normalized.adaptive;
    const groups = [
        { title: 'Headline', items: adaptive.headline ? [adaptive.headline] : [], tone: 'system' },
        { title: 'Padrões repetidos', items: adaptive.repeated_patterns, tone: 'urgent' },
        { title: 'Correções da partida', items: adaptive.recovered_patterns, tone: 'success' },
        { title: 'Fase mais cobrada', items: adaptive.phase_pressure, tone: 'warning' }
    ].filter(group => group.items.length);

    if (!groups.length) {
        container.appendChild(createElement('div', {
            className: 'postgame-empty',
            text: 'Quando o coach detectar repetição de erro e correção real, essa leitura adaptativa aparece aqui.'
        }));
        return;
    }

    const fragment = document.createDocumentFragment();
    groups.forEach(group => {
        const card = createElement('article', {
            className: `adaptive-card ${group.tone}`
        });
        card.appendChild(createElement('h5', { text: group.title }));

        const list = createElement('div', { className: 'adaptive-list' });
        group.items.forEach(item => {
            list.appendChild(createElement('p', {
                className: 'adaptive-item',
                text: normalizeText(item)
            }));
        });

        card.appendChild(list);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);
}

function renderPostGameTimeline(entries) {
    const container = document.getElementById('postgame-timeline');
    if (!container) {
        return;
    }

    clearElement(container);

    const normalizedEntries = Array.isArray(entries)
        ? entries.map(normalizeTimelineEntry).filter(Boolean)
        : [];

    if (!normalizedEntries.length) {
        container.appendChild(createElement('div', {
            className: 'postgame-empty',
            text: 'A timeline aparece com os eventos mais relevantes assim que a partida termina.'
        }));
        return;
    }

    const fragment = document.createDocumentFragment();
    normalizedEntries.forEach(entry => {
        const row = createElement('article', {
            className: `timeline-item ${entry.severity}`
        });
        row.appendChild(createElement('span', {
            className: 'timeline-clock',
            text: entry.clock
        }));

        const body = createElement('div', { className: 'timeline-body' });
        body.appendChild(createElement('strong', {
            className: 'timeline-title',
            text: normalizeText(entry.category || entry.kind, 'timeline')
        }));
        body.appendChild(createElement('p', {
            className: 'timeline-text',
            text: entry.text
        }));

        const metaBits = [entry.phase, entry.kind, entry.impact, entry.priority].filter(Boolean).join(' · ');
        if (metaBits) {
            body.appendChild(createElement('span', {
                className: 'timeline-meta',
                text: metaBits
            }));
        }

        row.appendChild(body);
        fragment.appendChild(row);
    });

    container.appendChild(fragment);
}

function renderJungleIntel() {
    const container = document.getElementById('jungle-intel-content');
    if (!container) {
        return;
    }

    clearElement(container);

    const intel = normalizeJungleIntel(uiState.jungleIntel);
    if (!intel.enemy_jungler_name && !intel.enemy_jungler_champion) {
        container.appendChild(createElement('div', {
            className: 'empty-state',
            text: 'Assim que a partida abrir, o coach começa a montar leitura do jungler inimigo.'
        }));
        return;
    }

    const metrics = createElement('div', { className: 'jungle-metrics' });
    [
        ['JUNGLER', intel.enemy_jungler_name || intel.enemy_jungler_champion || '--'],
        ['IMPACTO', intel.last_seen_clock || '--:--'],
        ['LADO', normalizeText(intel.probable_side, 'UNKNOWN').toUpperCase()],
        ['CONFIANÇA', `${Math.round((intel.confidence || 0) * 100)}%`]
    ].forEach(([label, value]) => {
        metrics.appendChild(createElement('div', {
            className: 'jungle-metric brutalist-card',
            children: [
                createElement('span', { className: 'eyebrow', text: label }),
                createElement('strong', { 
                    text: value,
                    style: 'display: block; font-size: 1.2rem; color: var(--toxic);' 
                })
            ]
        }));
    });

    const objectiveRow = createElement('div', { 
        className: 'jungle-objectives',
        style: 'display: flex; gap: 4px; flex-wrap: wrap; margin-top: 12px;'
    });
    ['dragon', 'herald', 'baron', 'horde'].forEach(objective => {
        objectiveRow.appendChild(buildChip(`${objective.toUpperCase()} ${intel.objective_presence?.[objective] || 0}`, 'jungle-chip'));
    });

    const notesWrap = createElement('div', { className: 'jungle-notes' });
    if (intel.notes.length) {
        intel.notes.forEach(note => {
            const tone = normalizeTone(note.tone);
            notesWrap.appendChild(createElement('article', {
                className: `jungle-note ${tone}`,
                children: [
                    createElement('strong', { text: normalizeText(note.title, 'Leitura de selva') }),
                    createElement('span', { className: 'timeline-meta', text: normalizeText(note.clock, '--:--') }),
                    createElement('p', { text: normalizeText(note.detail, '') })
                ]
            }));
        });
    } else {
        notesWrap.appendChild(createElement('div', {
            className: 'postgame-empty',
            text: 'O jungler inimigo ainda não deixou um rastro forte o suficiente para leitura.'
        }));
    }

    container.appendChild(metrics);
    container.appendChild(objectiveRow);
    container.appendChild(notesWrap);
}

function setActiveTaxonomy(categoryId) {
    const activeCategory = getTaxonomyId(categoryId);
    uiState.activeTaxonomy = activeCategory || null;

    document.querySelectorAll('.taxonomy-card').forEach(card => {
        card.classList.toggle('active', card.dataset.category === activeCategory);
    });
}

function updatePostGameSummary(summary = {}) {
    const merged = {
        ...POSTGAME_DEFAULT,
        ...summary,
        reads: Array.isArray(summary.reads) ? summary.reads : POSTGAME_DEFAULT.reads,
        memory: Array.isArray(summary.memory) ? summary.memory : POSTGAME_DEFAULT.memory,
        timeline: Array.isArray(summary.timeline) ? summary.timeline : POSTGAME_DEFAULT.timeline,
        insights: normalizeInsights(summary.insights || POSTGAME_DEFAULT.insights)
    };

    uiState.currentSummary = merged;
    uiState.postgameMemory = merged.memory.map(normalizeMemoryEntry).filter(Boolean);

    const title = document.getElementById('postgame-title');
    const result = document.getElementById('postgame-result');
    const duration = document.getElementById('postgame-duration');
    const scoreline = document.getElementById('postgame-scoreline');
    const focus = document.getElementById('postgame-focus');
    const confidence = document.getElementById('postgame-confidence');

    if (title) title.textContent = normalizeText(merged.title, POSTGAME_DEFAULT.title);
    if (result) result.textContent = normalizeText(merged.result, POSTGAME_DEFAULT.result);
    if (duration) duration.textContent = normalizeText(merged.duration, POSTGAME_DEFAULT.duration);
    if (scoreline) scoreline.textContent = normalizeText(merged.scoreline, POSTGAME_DEFAULT.scoreline);
    
    const scoreBadge = document.getElementById('postgame-scoreline-badge');
    if (scoreBadge) {
        scoreBadge.textContent = normalizeText(merged.scoreline, '--');
    }
    if (focus) focus.textContent = normalizeText(merged.focus, POSTGAME_DEFAULT.focus);
    if (confidence) confidence.textContent = normalizeText(merged.confidence, POSTGAME_DEFAULT.confidence);

    renderPostGameReads(merged.reads);
    renderMemoryFeed(merged.memory);
    renderPostGameInsights(merged.insights);
    renderAdaptiveInsights(merged.insights);
    renderPostGameTimeline(merged.timeline);
    updatePlayerDashboardHighlights();

    const inferredCategory = inferTaxonomyFromText(merged.focus) || inferTaxonomyFromText(merged.title) || 'recovery';
    setActiveTaxonomy(getTaxonomyId(inferredCategory) || inferredCategory);
}

function renderPostGameBase() {
    updatePostGameSummary(POSTGAME_DEFAULT);
}

function renderMatchIntel() {
    const container = document.getElementById('match-intel-content');
    if (!container) {
        return;
    }

    clearElement(container);

    if (!uiState.matchIntel.length) {
        container.appendChild(createElement('div', {
            className: 'empty-state',
            text: 'Inicie uma partida para visualizar a leitura do time inimigo.'
        }));
        return;
    }

    const fragment = document.createDocumentFragment();

    uiState.matchIntel.forEach(entry => {
        const card = createElement('article', {
            className: 'pregame-card brutalist-card'
        });

        const header = createElement('div', { className: 'pregame-card-header' });
        const titleWrap = createElement('div');
        titleWrap.appendChild(createElement('h4', { 
            text: entry.name,
            style: 'font-size: 0.95rem; margin-bottom: 2px;' 
        }));
        titleWrap.appendChild(createElement('p', {
            className: 'eyebrow',
            text: entry.champion ? entry.champion.toUpperCase() : 'DESCONHECIDO'
        }));

        const rankBadge = createElement('span', {
            className: 'rank-badge',
            text: (entry.rank && entry.rank.length > 10) ? entry.rank.split(' ')[0] : (entry.rank || '--')
        });

        header.appendChild(titleWrap);
        header.appendChild(rankBadge);

        const stats = createElement('div', { 
            className: 'pregame-stats',
            style: 'margin-top: 12px; border-top: 1px solid var(--line); padding-top: 10px;'
        });
        
        // Compact Stat Grid
        const createStat = (label, value) => createElement('div', {
            className: 'pregame-stat',
            children: [
                createElement('span', { className: 'eyebrow', text: label }),
                createElement('strong', { 
                    text: value,
                    style: 'display: block; font-size: 1.1rem; color: var(--text-soft);' 
                })
            ]
        });

        stats.appendChild(createStat('ELO', entry.rank || '--'));
        stats.appendChild(createStat('WINRATE', entry.winrate || '--'));

        card.appendChild(header);
        card.appendChild(stats);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);
}

function addPreGameStat(name, champion, rank, winrate) {
    const normalizedName = normalizeText(name, 'Inimigo');
    const nextEntry = {
        name: normalizedName,
        champion: normalizeText(champion, ''),
        rank: normalizeText(rank, '--'),
        winrate: normalizeText(winrate, '--')
    };

    const existingIndex = uiState.matchIntel.findIndex(entry => entry.name === normalizedName);
    if (existingIndex >= 0) {
        uiState.matchIntel[existingIndex] = nextEntry;
    } else {
        uiState.matchIntel.push(nextEntry);
    }

    renderMatchIntel();
}

function addAILog(message, type = 'normal') {
    const logsContainer = document.getElementById('ai-logs');
    if (!logsContainer) {
        return;
    }

    const text = normalizeText(message, '');
    if (!text) {
        return;
    }

    logsContainer.appendChild(createElement('div', {
        className: `log-entry ${type}`,
        text
    }));
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function updateGameState(phase, summonerName = null) {
    const normalizedPhase = normalizePhase(phase);
    const previousPhase = uiState.currentPhase;
    const gamePhase = document.getElementById('game-phase');
    const leagueStatus = document.getElementById('league-status');
    const statusDot = document.querySelector('.status-dot');

    uiState.currentPhase = normalizedPhase;
    setBodyVisualState();

    if (gamePhase) {
        gamePhase.textContent = normalizedPhase;
    }

    if (leagueStatus) {
        leagueStatus.textContent = isPostGamePhase(phase) ? 'Pós-jogo' : normalizedPhase;
    }

    if (statusDot) {
        statusDot.classList.toggle('active', normalizedPhase === 'Partida em Andamento');
    }

    if (summonerName) {
        const nameEl = document.getElementById('summoner-name');
        if (nameEl) {
            nameEl.textContent = normalizeText(summonerName, 'Desconhecido');
        }
    }

    const modeMeta = COACH_MODE_META[normalizeLookup(uiState.settings.coach_mode)];
    const phaseFocus = modeMeta ? modeMeta.taxonomy : phaseFocusMap.get(normalizedPhase);
    if (phaseFocus) {
        setActiveTaxonomy(phaseFocus);
    }

    if ((normalizedPhase === 'Lobby' || normalizedPhase === 'Seleção de Campeões') && previousPhase !== normalizedPhase) {
        uiState.matchIntel = [];
        renderMatchIntel();
    }

    if (isPostGamePhase(phase)) {
        setActiveTaxonomy('recovery');
    }

    updatePlayerDashboardHighlights();
}

function syncPresetButtons() {
    document.querySelectorAll('[data-voice-preset]').forEach(button => {
        button.classList.toggle('active', button.dataset.voicePreset === uiState.settings.voice_preset);
    });

    document.querySelectorAll('[data-voice-personality]').forEach(button => {
        button.classList.toggle('active', button.dataset.voicePersonality === uiState.settings.voice_personality);
    });

    document.querySelectorAll('[data-category-preset]').forEach(button => {
        const preset = button.dataset.categoryPreset;
        const enabledSet = new Set(
            Object.entries(uiState.settings.category_filters || {})
                .filter(([, enabled]) => enabled)
                .map(([key]) => key)
        );
        const matchesPreset = JSON.stringify([...enabledSet].sort()) === JSON.stringify([...(CATEGORY_PRESETS[preset] || [])].sort());
        button.classList.toggle('active', matchesPreset);
    });

    document.querySelectorAll('[data-category-toggle]').forEach(button => {
        const category = button.dataset.categoryToggle;
        button.classList.toggle('active', Boolean(uiState.settings.category_filters?.[category]));
    });
}

function hydrateSettings(snapshot = {}) {
    uiState.settings = {
        ...uiState.settings,
        ...snapshot,
        category_filters: {
            ...(uiState.settings.category_filters || {}),
            ...((snapshot && snapshot.category_filters) || {})
        }
    };

    const volumeSlider = document.getElementById('voice-volume');
    const toggleVoice = document.getElementById('toggle-voice');
    const toggleObjectives = document.getElementById('toggle-objectives');
    const toggleHardcore = document.getElementById('toggle-hardcore');

    if (volumeSlider && snapshot.volume !== undefined) {
        volumeSlider.value = snapshot.volume;
    }
    if (toggleVoice && snapshot.voice_enabled !== undefined) {
        toggleVoice.checked = Boolean(snapshot.voice_enabled);
    }
    if (toggleObjectives && snapshot.objectives_enabled !== undefined) {
        toggleObjectives.checked = Boolean(snapshot.objectives_enabled);
    }
    if (toggleHardcore && snapshot.hardcore_enabled !== undefined) {
        toggleHardcore.checked = Boolean(snapshot.hardcore_enabled);
    }

    // New Industrial Settings
    const updateSlider = (id, value, suffix = '') => {
        const el = document.getElementById(id);
        const tag = document.getElementById(`${id}-value`);
        if (el && value !== undefined) {
            el.value = value;
            if (tag) tag.textContent = `${value}${suffix}`;
        }
    };

    updateSlider('macro-interval', snapshot.macro_interval, 's');
    updateSlider('minimap-interval', snapshot.minimap_interval, 's');
    updateSlider('economy-interval', snapshot.economy_interval, 's');
    updateSlider('item-check-interval', snapshot.item_check_interval, 's');
    updateSlider('farm-threshold', snapshot.farm_threshold, '%');
    updateSlider('vision-threshold', snapshot.vision_threshold, '%');

    const toggleSoloFocus = document.getElementById('solo-focus');
    if (toggleSoloFocus && snapshot.solo_focus !== undefined) {
        toggleSoloFocus.checked = Boolean(snapshot.solo_focus);
    }

    if (snapshot.voice_personality) {
        uiState.settings.voice_personality = String(snapshot.voice_personality).trim().toLowerCase();
    }

    const activeMode = getTaxonomyId(snapshot.coach_mode) || inferTaxonomyFromText(snapshot.coach_mode);
    if (activeMode) {
        setActiveTaxonomy(activeMode);
    }

    renderCoachModePanel();
    syncPresetButtons();
    setBodyVisualState();
}

function hydrateAuthState(snapshot = {}) {
    uiState.auth = {
        ...uiState.auth,
        ...normalizeAuthSnapshot(snapshot)
    };

    const authMessage = document.getElementById('auth-message');
    const userName = document.getElementById('auth-user-name');
    const logoutButton = document.getElementById('logout-button');

    if (authMessage) {
        if (!uiState.auth.configured) {
            authMessage.textContent = 'Configure SUPABASE_URL e SUPABASE_ANON_KEY para ativar o login.';
        } else if (uiState.auth.message) {
            authMessage.textContent = uiState.auth.message;
        } else {
            authMessage.textContent = uiState.auth.authenticated
                ? 'Sessao ativa nesta maquina.'
                : 'Aguardando autenticacao.';
        }
    }

    if (userName) {
        userName.textContent = uiState.auth.user?.display_name || 'Visitante';
    }

    if (logoutButton) {
        logoutButton.disabled = !uiState.auth.authenticated;
        logoutButton.style.opacity = uiState.auth.authenticated ? '1' : '0.45';
    }

    if (uiState.auth.authenticated) {
        const form = document.getElementById('auth-form');
        if (form) {
            form.reset();
        }
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        const dashboardNav = document.querySelector('.nav-item[data-target="dashboard"]');
        const dashboardView = document.getElementById('view-dashboard');
        if (dashboardNav) {
            dashboardNav.classList.add('active');
        }
        if (dashboardView) {
            dashboardView.classList.add('active');
        }
    }

    setBodyVisualState();
    updatePlayerDashboardHighlights();
}

function bindAuth() {
    document.querySelectorAll('[data-auth-mode]').forEach(button => {
        button.addEventListener('click', () => setAuthMode(button.dataset.authMode));
    });

    const form = document.getElementById('auth-form');
    const logoutButton = document.getElementById('logout-button');
    const submit = document.getElementById('auth-submit');

    async function submitAuthForm() {
        const email = document.getElementById('auth-email')?.value?.trim() || '';
        const password = document.getElementById('auth-password')?.value || '';
        const displayName = document.getElementById('auth-name')?.value?.trim() || '';

        if (!email || !password) {
            hydrateAuthState({ message: 'Preencha e-mail e senha para continuar.' });
            return;
        }

        if (uiState.auth.mode === 'signup' && !displayName) {
            hydrateAuthState({ message: 'Preencha teu nome para criar a conta.' });
            return;
        }

        if (!window.pywebview || !window.pywebview.api) {
            hydrateAuthState({ message: 'PyWebView ainda nao esta pronto.' });
            return;
        }

        hydrateAuthState({
            ...uiState.auth,
            message: uiState.auth.mode === 'signup' ? 'Criando conta...' : 'Tentando entrar...'
        });

        if (submit) {
            submit.disabled = true;
            submit.textContent = uiState.auth.mode === 'signup' ? 'Criando...' : 'Entrando...';
        }

        try {
            const snapshot = uiState.auth.mode === 'signup'
                ? await window.pywebview.api.register_user(email, password, displayName)
                : await window.pywebview.api.login_user(email, password);
            hydrateAuthState(snapshot || {});
        } catch (error) {
            hydrateAuthState({ message: 'Nao foi possivel autenticar agora.' });
        } finally {
            if (submit) {
                submit.disabled = false;
                submit.textContent = uiState.auth.mode === 'signup' ? 'Criar conta' : 'Entrar';
            }
            setAuthMode(uiState.auth.mode);
        }
    }

    if (form) {
        form.addEventListener('submit', async event => {
            event.preventDefault();
            await submitAuthForm();
        });
    }

    if (submit) {
        submit.addEventListener('click', async event => {
            if (form) {
                return;
            }
            event.preventDefault();
            await submitAuthForm();
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            if (!window.pywebview || !window.pywebview.api) {
                return;
            }
            try {
                const snapshot = await window.pywebview.api.logout_user();
                hydrateAuthState(snapshot || {});
            } catch (error) {
                hydrateAuthState({ message: 'Nao foi possivel encerrar a sessao.' });
            }
        });
    }
}

function bindSettings() {
    const volumeSlider = document.getElementById('voice-volume');
    const toggleVoice = document.getElementById('toggle-voice');
    const toggleObjectives = document.getElementById('toggle-objectives');
    const toggleHardcore = document.getElementById('toggle-hardcore');

    if (volumeSlider) {
        volumeSlider.addEventListener('input', event => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_volume(event.target.value);
            }
        });
    }

    if (toggleVoice) {
        toggleVoice.addEventListener('change', event => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggle_voice(event.target.checked);
            }
        });
    }

    if (toggleObjectives) {
        toggleObjectives.addEventListener('change', event => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggle_objectives(event.target.checked);
            }
        });
    }

    if (toggleHardcore) {
        toggleHardcore.addEventListener('change', event => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggle_hardcore(event.target.checked);
            }
        });
    }

    // New Industrial Binds
    const bindSlider = (id, apiFunc, suffix = '') => {
        const el = document.getElementById(id);
        const tag = document.getElementById(`${id}-value`);
        if (el) {
            el.addEventListener('input', (e) => {
                const val = e.target.value;
                if (tag) tag.textContent = `${val}${suffix}`;
            });
            el.addEventListener('change', (e) => {
                if (window.pywebview && window.pywebview.api && window.pywebview.api[apiFunc]) {
                    window.pywebview.api[apiFunc](e.target.value);
                }
            });
        }
    };

    bindSlider('macro-interval', 'set_macro_interval', 's');
    bindSlider('minimap-interval', 'set_minimap_interval', 's');
    bindSlider('economy-interval', 'set_economy_interval', 's');
    bindSlider('item-check-interval', 'set_item_check_interval', 's');
    bindSlider('farm-threshold', 'set_farm_threshold', '%');
    bindSlider('vision-threshold', 'set_vision_threshold', '%');

    const toggleSoloFocus = document.getElementById('solo-focus');
    if (toggleSoloFocus) {
        toggleSoloFocus.addEventListener('change', (e) => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggle_solo_focus(e.target.checked);
            }
        });
    }

    document.querySelectorAll('[data-voice-preset]').forEach(button => {
        button.addEventListener('click', () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_voice_preset(button.dataset.voicePreset);
            }
        });
    });

    document.querySelectorAll('[data-voice-personality]').forEach(button => {
        button.addEventListener('click', () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_voice_personality(button.dataset.voicePersonality);
            }
        });
    });

    document.querySelectorAll('[data-category-preset]').forEach(button => {
        button.addEventListener('click', () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_category_preset(button.dataset.categoryPreset);
            }
        });
    });

    document.querySelectorAll('[data-category-toggle]').forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.categoryToggle;
            const nextState = !Boolean(uiState.settings.category_filters?.[category]);
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_category_enabled(category, nextState);
            }
        });
    });
}

function bindNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));

            item.classList.add('active');
            const target = document.getElementById(`view-${item.dataset.target}`);
            if (target) {
                target.classList.add('active');
            }
        });
    });
}

function appendPostGameMemory(entry) {
    const normalizedEntry = normalizeMemoryEntry(entry);
    if (!normalizedEntry) {
        return;
    }

    const next = [...uiState.postgameMemory, normalizedEntry];
    updatePostGameSummary({
        ...uiState.currentSummary,
        memory: next
    });
}

window.updateGameState = updateGameState;
window.playTTSUpdate = function(message, type = 'normal', category = null) {
    addAILog(message, normalizeTone(type));

    const activeCategory = getTaxonomyId(category) || inferTaxonomyFromText(category);
    if (activeCategory) {
        setActiveTaxonomy(activeCategory);
    }
};
window.addPreGameStat = addPreGameStat;
window.updatePostGameSummary = updatePostGameSummary;
window.appendPostGameMemory = appendPostGameMemory;
window.updateJungleIntel = function(payload = {}) {
    uiState.jungleIntel = normalizeJungleIntel(payload);
    renderJungleIntel();
};
window.hydrateSettings = hydrateSettings;
window.hydrateAuthState = hydrateAuthState;
window.setCoachTaxonomyFocus = function(categoryId) {
    const activeCategory = getTaxonomyId(categoryId) || inferTaxonomyFromText(categoryId);
    if (activeCategory) {
        setActiveTaxonomy(activeCategory);
    }
};

bindNavigation();
bindAuth();
setAuthMode('login');
renderCoachTaxonomy();
renderCoachModePanel();
renderPostGameBase();
renderMatchIntel();
renderJungleIntel();
setActiveTaxonomy('draft');
setBodyVisualState();

window.addEventListener('pywebviewready', function() {
    addAILog('Conectado ao núcleo Python.', 'system');
    bindSettings();
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_auth_snapshot) {
        window.pywebview.api.get_auth_snapshot().then(hydrateAuthState).catch(() => {
            hydrateAuthState({ message: 'Nao foi possivel carregar a sessao.' });
        });
    }
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_settings_snapshot) {
        window.pywebview.api.get_settings_snapshot().then(hydrateSettings).catch(() => {});
    }
});
