/**
 * RoboForge Arena — Frontend Application Shell Controller
 * Manages WebSocket state streams, layout mode switching, live stick figure pop cards, and commentary.
 */

document.addEventListener('DOMContentLoaded', () => {
    const renderer = new CanvasRenderer('sim-canvas');

    const statusDot = document.getElementById('connection-dot');
    const statusText = document.getElementById('connection-status');

    const btnPause = document.getElementById('btn-pause');
    const btnReset = document.getElementById('btn-reset');

    const btnSpawnBox = document.getElementById('btn-spawn-box');
    const btnSpawnRobotA = document.getElementById('btn-spawn-robot-a');
    const btnSpawnRobotB = document.getElementById('btn-spawn-robot-b');
    const gravitySlider = document.getElementById('gravity-slider');
    const gravityVal = document.getElementById('gravity-val');

    let socket = null;
    let currentMode = 'playground';
    let isPaused = false;
    let gymFitnessHistory = [];  // populated live from state.gym.history via WebSocket

    // WebSocket Connection
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/state`;

        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            statusDot.className = 'dot connected';
            statusText.textContent = 'Connected (60 Hz)';
        };

        socket.onmessage = (event) => {
            try {
                const state = JSON.parse(event.data);
                renderer.render(state);

                // Update Competitive Match Stats, HP Bars, and Commentary
                if (state.combat) {
                    const hpA = state.combat.robot_a_hp;
                    const hpB = state.combat.robot_b_hp;
                    const maxA = state.combat.max_durability_a || 300.0;
                    const maxB = state.combat.max_durability_b || 300.0;

                    const barA = document.getElementById('hp-bar-a');
                    const barB = document.getElementById('hp-bar-b');

                    if (barA) barA.style.width = `${Math.max(0, (hpA / maxA) * 100)}%`;
                    if (barB) barB.style.width = `${Math.max(0, (hpB / maxB) * 100)}%`;

                    const commText = document.getElementById('commentary-text');
                    if (commText && state.combat.commentary) {
                        commText.textContent = `"${state.combat.commentary}"`;
                    }
                }

                // Update Gym Live Population Grid & Metrics
                if (state.gym) {
                    const genVal = document.getElementById('gym-gen-val');
                    const bestVal = document.getElementById('gym-best-val');
                    const meanVal = document.getElementById('gym-mean-val');

                    if (genVal && state.gym.generation !== undefined) genVal.textContent = state.gym.generation;
                    if (bestVal && state.gym.best_reward !== undefined) bestVal.textContent = state.gym.best_reward.toFixed(1);
                    if (meanVal && state.gym.mean_reward !== undefined) meanVal.textContent = state.gym.mean_reward.toFixed(1);

                    // Update live fitness history from real server data
                    if (state.gym.history && state.gym.history.length > 0) {
                        gymFitnessHistory = state.gym.history;
                        drawGymChart();
                    }

                    if (state.gym.grid) {
                        renderGymPopulationCards(state.gym.grid);
                    }

                    // Show training complete banner
                    if (state.gym.training_complete) {
                        const banner = document.getElementById('gym-complete-banner');
                        if (banner) banner.classList.remove('hidden');
                    }
                }
            } catch (err) {
                console.error('Failed to parse frame:', err);
            }
        };

        socket.onclose = () => {
            statusDot.className = 'dot disconnected';
            statusText.textContent = 'Disconnected (Reconnecting...)';
            setTimeout(connectWebSocket, 2000);
        };

        socket.onerror = () => {
            socket.close();
        };
    }

    // Render Population Stick Figure Cards in Gym Mode
    function renderGymPopulationCards(grid) {
        const container = document.getElementById('gym-grid-cards');
        if (!container) return;
        container.innerHTML = '';

        grid.forEach((item) => {
            const card = document.createElement('div');
            card.className = `pop-card ${item.is_best ? 'best' : ''}`;
            card.innerHTML = `
                ${item.is_best ? '<span class="best-badge">BEST</span>' : ''}
                <svg class="pop-figure-icon" viewBox="0 0 24 36" fill="none" stroke="${item.is_best ? '#22c55e' : '#9ca3af'}" stroke-width="2">
                    <circle cx="12" cy="6" r="4" fill="${item.is_best ? '#22c55e' : '#9ca3af'}" />
                    <line x1="12" y1="10" x2="12" y2="22" />
                    <line x1="12" y1="14" x2="5" y2="19" />
                    <line x1="12" y1="14" x2="19" y2="19" />
                    <line x1="12" y1="22" x2="6" y2="34" />
                    <line x1="12" y1="22" x2="18" y2="34" />
                </svg>
                <span class="pop-score">${item.reward.toFixed(1)}</span>
            `;
            container.appendChild(card);
        });

        drawGymChart();
    }

    // Draw Fitness Curve Sparkline Graph from live server data
    function drawGymChart() {
        const canvas = document.getElementById('gym-chart-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;

        ctx.clearRect(0, 0, w, h);

        const data = gymFitnessHistory;
        if (data.length < 2) {
            // Not enough data yet — show placeholder text
            ctx.fillStyle = '#6b7280';
            ctx.font = '12px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Waiting for training data...', w / 2, h / 2);
            return;
        }

        const maxVal = Math.max(...data, 1);
        const minVal = Math.min(...data, 0);
        const range = maxVal - minVal || 1;

        // Best fitness line (blue)
        ctx.beginPath();
        data.forEach((val, i) => {
            const x = (i / (data.length - 1)) * w;
            const y = h - ((val - minVal) / range) * (h - 20) - 10;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Mark each generation's best with a dot
        data.forEach((val, i) => {
            const x = (i / (data.length - 1)) * w;
            const y = h - ((val - minVal) / range) * (h - 20) - 10;
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#60a5fa';
            ctx.fill();
        });
    }

    // Mode Navigation Switcher
    document.querySelectorAll('.nav-btn').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
            const targetMode = e.currentTarget.getAttribute('data-mode');
            currentMode = targetMode;

            // Update Left Nav Buttons
            document.querySelectorAll('.nav-btn').forEach((b) => b.classList.remove('active'));
            e.currentTarget.classList.add('active');

            // Switch Left Panel Controls
            document.querySelectorAll('.left-panel').forEach((p) => p.classList.remove('active'));
            const leftPanel = document.getElementById(`left-controls-${targetMode}`);
            if (leftPanel) leftPanel.classList.add('active');

            // Switch Headers, Viewports, and Bottom Cards
            const compHeader = document.getElementById('competitive-header');
            const gymHeader = document.getElementById('gym-stats-header');
            const playViewport = document.getElementById('playground-viewport');
            const gymViewport = document.getElementById('gym-viewport');
            const compBottom = document.getElementById('competitive-bottom-row');
            const matchFooter = document.getElementById('match-footer-info');

            if (targetMode === 'playground') {
                if (compHeader) compHeader.classList.add('hidden');
                if (gymHeader) gymHeader.classList.add('hidden');
                if (playViewport) playViewport.classList.remove('hidden');
                if (gymViewport) gymViewport.classList.add('hidden');
                if (compBottom) compBottom.classList.add('hidden');
                if (matchFooter) matchFooter.classList.add('hidden');
            } else if (targetMode === 'gym') {
                if (compHeader) compHeader.classList.add('hidden');
                if (gymHeader) gymHeader.classList.remove('hidden');
                if (playViewport) playViewport.classList.add('hidden');
                if (gymViewport) gymViewport.classList.remove('hidden');
                if (compBottom) compBottom.classList.add('hidden');
                if (matchFooter) matchFooter.classList.add('hidden');
                drawGymChart();
            } else if (targetMode === 'competitive') {
                if (compHeader) compHeader.classList.remove('hidden');
                if (gymHeader) gymHeader.classList.add('hidden');
                if (playViewport) playViewport.classList.remove('hidden');
                if (gymViewport) gymViewport.classList.add('hidden');
                if (compBottom) compBottom.classList.remove('hidden');
                if (matchFooter) matchFooter.classList.remove('hidden');
            }

            // Send Mode Change Request to Backend Server
            await fetch('/api/mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: targetMode }),
            });
        });
    });

    // Pause / Resume Button
    if (btnPause) {
        btnPause.addEventListener('click', async () => {
            isPaused = !isPaused;
            btnPause.textContent = isPaused ? 'Resume' : 'Pause';
            await fetch(`/api/control?action=${isPaused ? 'pause' : 'resume'}`, { method: 'POST' });
        });
    }

    // Reset Button
    if (btnReset) {
        btnReset.addEventListener('click', async () => {
            await fetch('/api/control?action=reset', { method: 'POST' });
        });
    }

    // Playground Control Actions
    if (btnSpawnBox) {
        btnSpawnBox.addEventListener('click', async () => {
            await fetch('/api/spawn_shape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x: (Math.random() - 0.5) * 2, y: 5.0 }),
            });
        });
    }

    if (btnSpawnRobotA) {
        btnSpawnRobotA.addEventListener('click', async () => {
            await fetch('/api/spawn_robot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ preset_path: 'robots/presets/boxer.json', x: -1.5, y: 3.0 }),
            });
        });
    }

    if (btnSpawnRobotB) {
        btnSpawnRobotB.addEventListener('click', async () => {
            await fetch('/api/spawn_robot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ preset_path: 'robots/presets/grappler.json', x: 1.5, y: 3.0 }),
            });
        });
    }

    if (gravitySlider) {
        gravitySlider.addEventListener('input', async (e) => {
            const gy = parseFloat(e.target.value);
            if (gravityVal) gravityVal.textContent = gy.toFixed(1);
            await fetch('/api/gravity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ gx: 0.0, gy: gy }),
            });
        });
    }

    // Natural Language Training Prompt Handler
    const promptInput = document.getElementById('prompt-input');
    const promptInterpreted = document.getElementById('prompt-interpreted');

    if (promptInput) {
        promptInput.addEventListener('input', async (e) => {
            const text = e.target.value;
            if (!text.trim()) {
                if (promptInterpreted) promptInterpreted.textContent = 'Interpreted: aggression 0.5 · mobility 0.5 · caution 0.5';
                return;
            }
            try {
                const res = await fetch('/api/gym/translate_prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: text }),
                });
                const data = await res.json();
                if (data.translation && data.translation.weights && promptInterpreted) {
                    const w = data.translation.weights;
                    promptInterpreted.textContent = `Interpreted: aggression ${w.aggression.toFixed(1)} · mobility ${w.mobility.toFixed(1)} · caution ${w.caution.toFixed(1)}`;
                }
            } catch (err) {
                console.error('Prompt translation failed:', err);
            }
        });
    }

    // Gym Start Training Session Handler
    const btnTrainStart = document.getElementById('btn-train-start');
    if (btnTrainStart) {
        btnTrainStart.addEventListener('click', async () => {
            const algoSelect = document.getElementById('gym-algo-select');
            const algo = algoSelect ? algoSelect.value : 'ga';
            const promptText = promptInput ? promptInput.value : '';

            await fetch('/api/gym/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ algo: algo, timesteps: 10000, generations: 10, prompt: promptText }),
            });
        });
    }

    // Start 1v1 Battle Handler
    const btnStartMatch = document.getElementById('btn-start-match');
    if (btnStartMatch) {
        btnStartMatch.addEventListener('click', async () => {
            await fetch('/api/competitive/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fighter_a_id: 'boxer', fighter_b_id: 'grappler' }),
            });
        });
    }

    // Initialize Connection
    connectWebSocket();
});
