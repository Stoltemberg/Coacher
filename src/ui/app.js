// UI Navigation Logic
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        // Remove active class from all
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        
        // Add active to current
        item.classList.add('active');
        const targetId = `view-${item.dataset.target}`;
        document.getElementById(targetId).classList.add('active');
    });
});

// Logs System
function addAILog(message, type = 'normal') {
    const logsContainer = document.getElementById('ai-logs');
    const logEl = document.createElement('div');
    logEl.className = `log-entry ${type}`;
    logEl.innerText = message;
    logsContainer.appendChild(logEl);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// API for Python to Call
window.updateGameState = function(phase, summonerName = null) {
    document.getElementById('game-phase').innerText = phase;
    if (phase === 'In Game') {
        document.getElementById('league-status').innerText = 'Partida em Andamento';
        document.querySelector('.status-dot').classList.add('active');
    } else {
        document.getElementById('league-status').innerText = phase;
        document.querySelector('.status-dot').classList.remove('active');
    }
    
    if (summonerName) {
        document.getElementById('summoner-name').innerText = summonerName;
    }
};

window.playTTSUpdate = function(message) {
    addAILog(message);
};

window.addPreGameStat = function(name, champion, rank, winrate) {
    const container = document.getElementById('match-intel-content');
    const emptyState = container.querySelector('.empty-state');
    if(emptyState) {
        emptyState.remove();
    }
    
    const card = document.createElement('div');
    card.className = "glass-card";
    card.style.marginBottom = "1rem";
    card.style.borderLeft = "4px solid var(--accent)";
    card.innerHTML = `
        <h4 style="margin-bottom: 5px;">${name} <span style="color:var(--text-muted); font-size:0.8rem">(${champion})</span></h4>
        <p style="font-size: 0.9rem; color: #e2e8f0;"><strong>Elo:</strong> ${rank} | <strong style="color:var(--primary-light)">Winrate:</strong> ${winrate}</p>
    `;
    container.appendChild(card);
};

// Settings bindings to Python
function bindSettings() {
    const volumeSlider = document.getElementById('voice-volume');
    const toggleVoice = document.getElementById('toggle-voice');
    const toggleObjectives = document.getElementById('toggle-objectives');
    const toggleHardcore = document.getElementById('toggle-hardcore');

    volumeSlider.addEventListener('input', (e) => {
        if (window.pywebview) {
            window.pywebview.api.set_volume(e.target.value);
        }
    });

    toggleVoice.addEventListener('change', (e) => {
        if (window.pywebview) {
            window.pywebview.api.toggle_voice(e.target.checked);
        }
    });

    toggleObjectives.addEventListener('change', (e) => {
        if (window.pywebview) {
            window.pywebview.api.toggle_objectives(e.target.checked);
        }
    });

    toggleHardcore.addEventListener('change', (e) => {
        if (window.pywebview) {
            window.pywebview.api.toggle_hardcore(e.target.checked);
        }
    });
}

// Wait for PyWebView to be ready
window.addEventListener('pywebviewready', function() {
    addAILog('Conectado ao núcleo Python.', 'system');
    bindSettings();
});
