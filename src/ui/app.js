const COACH_TAXONOMY = [
    {
        id: 'draft',
        title: 'Draft',
        kicker: 'Leitura da tela',
        description: 'Bans, picks e condição de vitória antes da partida começar. Aqui o Minerva decide se a lane existe para ganhar, punir ou sobreviver.',
        signals: ['Bans críticos', 'Matchup', 'Plano de rota'],
        accent: 'var(--primary-light)'
    },
    {
        id: 'lane',
        title: 'Lane',
        kicker: 'Micro e disciplina',
        description: 'Troca, wave state, pressão e janela para punir erro. O foco é não entregar espaço de graça.',
        signals: ['Wave control', 'Trading', 'Punição de erro'],
        accent: 'var(--secondary)'
    },
    {
        id: 'macro',
        title: 'Macro',
        kicker: 'Mapa e tempo',
        description: 'Movimento antes do inimigo, rotação, visão e leitura de espaço. O coach cobra decisão, não passeio.',
        signals: ['Rotação', 'Tempo de mapa', 'Set-up'],
        accent: 'var(--accent)'
    },
    {
        id: 'objective',
        title: 'Objetivo',
        kicker: 'Janelas de objetivo',
        description: 'Dragão, Barão, Arauto, torres e prioridade de luta ou crossmap. Se o objetivo é livre, o Minerva quer resposta na hora.',
        signals: ['Dragão', 'Barão', 'Arauto'],
        accent: 'var(--success)'
    },
    {
        id: 'economy',
        title: 'Economia',
        kicker: 'Recursos e spike',
        description: 'Farm, ouro, itemização e eficiência do jogador na janela atual. Aqui a cobrança é matemática, não narrativa.',
        signals: ['CS por minuto', 'Gold diff', 'Item spike'],
        accent: 'var(--warning)'
    },
    {
        id: 'recovery',
        title: 'Recuperação',
        kicker: 'Consertar sem chorar',
        description: 'Reset após erro, plano de estabilização e rotina para voltar ao jogo sem desandar a partida inteira.',
        signals: ['Reset mental', 'Stop dying', 'Plano de volta'],
        accent: 'var(--danger)'
    }
];

const POSTGAME_DEFAULT = {
    title: 'Aguardando fim de jogo',
    result: 'Sem dados',
    duration: '--',
    scoreline: '--',
    focus: '--',
    confidence: '--',
    reads: [
        'Quando a partida terminar, o Minerva vai resumir o que decidiu a vitória ou a derrota.',
        'Este espaço pode mostrar padrões como farm baixo, visão fraca, overextend e timings perdidos.',
        'O próximo passo é transformar isso em memória reutilizável entre partidas.'
    ],
    memory: [
        {
            title: 'Sem memória ainda',
            note: 'Nenhum padrão consolidado foi registrado nesta sessão.',
            tone: 'system'
        }
    ]
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

const uiState = {
    activeTaxonomy: 'draft',
    currentPhase: 'Lobby',
    currentSummary: { ...POSTGAME_DEFAULT },
    matchIntel: [],
    postgameMemory: []
};

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

function normalizeText(value, fallback = '') {
    const text = value === undefined || value === null ? '' : String(value).trim();
    return text || fallback;
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
            className: 'taxonomy-card glass-card',
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

    const tone = normalizeTone(entry.tone);

    return {
        title: normalizeText(entry.title, 'Memória'),
        note: normalizeText(entry.note, ''),
        tone,
        meta: normalizeText(entry.meta || entry.category || entry.phase || entry.kind, '')
    };
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

    if (normalizedEntries.length === 0) {
        const empty = createElement('div', {
            className: 'postgame-empty',
            text: 'A memória vai guardar padrões como farm baixo, visão fraca, overextend e timings de objetivo.'
        });
        container.appendChild(empty);
        return;
    }

    const fragment = document.createDocumentFragment();
    normalizedEntries.forEach(entry => {
        const item = createElement('article', {
            className: `memory-item ${entry.tone}`
        });
        const title = createElement('h5', { text: entry.title });
        const note = createElement('p', { text: entry.note });

        item.appendChild(title);

        if (entry.meta) {
            item.appendChild(createElement('span', {
                className: 'memory-meta',
                text: entry.meta
            }));
        }

        item.appendChild(note);
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
    if (normalizedReads.length === 0) {
        const empty = createElement('div', {
            className: 'postgame-empty',
            text: 'Quando a partida terminar, o coach pode detalhar as leituras mais importantes sem virar texto solto.'
        });
        container.appendChild(empty);
        return;
    }

    const fragment = document.createDocumentFragment();
    normalizedReads.forEach((read, index) => {
        const row = createElement('div', { className: 'summary-item' });
        const number = createElement('span', {
            className: 'summary-index',
            text: String(index + 1).padStart(2, '0')
        });
        const text = createElement('p', { text: normalizeText(read) });
        row.appendChild(number);
        row.appendChild(text);
        fragment.appendChild(row);
    });

    container.appendChild(fragment);
}

function setActiveTaxonomy(categoryId) {
    const activeCategory = getTaxonomyId(categoryId);
    uiState.activeTaxonomy = activeCategory || null;

    document.querySelectorAll('.taxonomy-card').forEach(card => {
        const isActive = card.dataset.category === activeCategory;
        card.classList.toggle('active', isActive);
    });
}

function updatePostGameSummary(summary = {}) {
    const merged = {
        ...POSTGAME_DEFAULT,
        ...summary,
        reads: Array.isArray(summary.reads) ? summary.reads : POSTGAME_DEFAULT.reads,
        memory: Array.isArray(summary.memory) ? summary.memory : POSTGAME_DEFAULT.memory
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
    if (focus) focus.textContent = normalizeText(merged.focus, POSTGAME_DEFAULT.focus);
    if (confidence) confidence.textContent = normalizeText(merged.confidence, POSTGAME_DEFAULT.confidence);

    renderPostGameReads(merged.reads);
    renderMemoryFeed(merged.memory);

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
            className: 'glass-card pregame-card'
        });

        const header = createElement('div', { className: 'pregame-card-header' });
        const titleWrap = createElement('div');
        titleWrap.appendChild(createElement('h4', { text: entry.name }));
        titleWrap.appendChild(createElement('p', {
            className: 'pregame-card-subtitle',
            text: entry.champion ? `Campeão: ${entry.champion}` : 'Campeão: desconhecido'
        }));

        const rankBadge = createElement('span', {
            className: 'rank-badge',
            text: entry.rank || '--'
        });

        header.appendChild(titleWrap);
        header.appendChild(rankBadge);

        const stats = createElement('div', { className: 'pregame-stats' });
        stats.appendChild(createElement('div', {
            className: 'pregame-stat',
            children: [
                createElement('span', { className: 'metric-label', text: 'Elo' }),
                createElement('strong', { text: entry.rank || '--' })
            ]
        }));
        stats.appendChild(createElement('div', {
            className: 'pregame-stat',
            children: [
                createElement('span', { className: 'metric-label', text: 'Winrate' }),
                createElement('strong', { text: entry.winrate || '--' })
            ]
        }));

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

    const logEl = createElement('div', {
        className: `log-entry ${type}`,
        text
    });

    logsContainer.appendChild(logEl);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function updateGameState(phase, summonerName = null) {
    const normalizedPhase = normalizePhase(phase);
    const previousPhase = uiState.currentPhase;
    const gamePhase = document.getElementById('game-phase');
    const leagueStatus = document.getElementById('league-status');
    const statusDot = document.querySelector('.status-dot');

    uiState.currentPhase = normalizedPhase;

    if (gamePhase) {
        gamePhase.textContent = normalizedPhase;
    }

    if (leagueStatus) {
        leagueStatus.textContent = isPostGamePhase(phase)
            ? 'Pós-jogo'
            : normalizedPhase;
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

    const phaseFocus = phaseFocusMap.get(normalizedPhase);
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
}

function bindNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));

            item.classList.add('active');
            const targetId = `view-${item.dataset.target}`;
            const target = document.getElementById(targetId);
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
window.playTTSUpdate = function(message, category = null) {
    addAILog(message);

    const activeCategory = getTaxonomyId(category) || inferTaxonomyFromText(category);
    if (activeCategory) {
        setActiveTaxonomy(activeCategory);
    }
};
window.addPreGameStat = addPreGameStat;
window.updatePostGameSummary = updatePostGameSummary;
window.appendPostGameMemory = appendPostGameMemory;
window.setCoachTaxonomyFocus = function(categoryId) {
    const activeCategory = getTaxonomyId(categoryId) || inferTaxonomyFromText(categoryId);
    if (activeCategory) {
        setActiveTaxonomy(activeCategory);
    }
};

bindNavigation();
renderCoachTaxonomy();
renderPostGameBase();
renderMatchIntel();
setActiveTaxonomy('draft');

window.addEventListener('pywebviewready', function() {
    addAILog('Conectado ao núcleo Python.', 'system');
    bindSettings();
});
