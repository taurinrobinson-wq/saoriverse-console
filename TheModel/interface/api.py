"""Flask interface for TheModel.

Adapted from the session-oriented UI pattern already present in limbic_ai/app.py.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template_string, request

from TheModel.core.mind import get_or_create_engine, reset_engine
from TheModel.core.villagers import default_villagers
from TheModel.interface.dialogue import village_summary_to_dialogue, villager_to_dialogue


app = Flask(__name__)


MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TheModel Village</title>
    <style>
        :root {
            --sky-top: #f8c98d;
            --sky-mid: #ffdcae;
            --sky-bottom: #ffeccf;
            --ground: #d6b07e;
            --panel: rgba(255, 251, 241, 0.9);
            --ink: #3b2d23;
            --ink-soft: #6a5647;
            --accent: #bf6f3f;
            --accent-strong: #8f4a29;
            --good: #609b64;
            --warn: #bc7f34;
            --bad: #ac4e42;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Palatino Linotype", "Book Antiqua", Palatino, serif;
            background: linear-gradient(180deg, var(--sky-top) 0%, var(--sky-mid) 42%, var(--sky-bottom) 68%, var(--ground) 100%);
            color: var(--ink);
            min-height: 100vh;
        }

        .hills {
            position: fixed;
            inset: auto 0 0 0;
            height: 34vh;
            pointer-events: none;
            background:
                radial-gradient(120% 70% at 10% 100%, #cfa678 0%, transparent 56%),
                radial-gradient(120% 70% at 40% 100%, #d6b486 0%, transparent 62%),
                radial-gradient(120% 70% at 70% 100%, #c79d6e 0%, transparent 64%),
                radial-gradient(120% 70% at 95% 100%, #dcb88b 0%, transparent 58%);
            opacity: 0.66;
        }

        .wrap {
            max-width: 1280px;
            margin: 0 auto;
            padding: 26px 18px 34px;
            position: relative;
            z-index: 2;
        }

        .hero {
            background: linear-gradient(140deg, rgba(255, 252, 244, 0.92), rgba(255, 246, 232, 0.88));
            border: 2px solid rgba(148, 96, 62, 0.2);
            border-radius: 22px;
            padding: 20px 24px;
            box-shadow: 0 12px 24px rgba(86, 51, 30, 0.18);
            margin-bottom: 14px;
        }

        .hero-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        h1, h2, h3 {
            margin-top: 0;
        }

        h1 {
            margin: 0;
            font-size: clamp(2rem, 5vw, 3rem);
            letter-spacing: 0.04em;
            color: #6f3f26;
        }

        .subtitle {
            margin: 10px 0 0;
            max-width: 880px;
            color: var(--ink-soft);
            font-size: 1.03rem;
            line-height: 1.6;
        }

        .day-chip {
            border-radius: 999px;
            background: rgba(191, 111, 63, 0.12);
            border: 1px solid rgba(191, 111, 63, 0.32);
            padding: 8px 14px;
            color: #7c4427;
            font-size: 0.95rem;
            font-weight: 700;
        }

        .grid {
            display: grid;
            grid-template-columns: 1.08fr 0.92fr;
            gap: 14px;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(132, 89, 62, 0.2);
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 10px 20px rgba(102, 66, 45, 0.16);
        }

        .village-map {
            position: relative;
            min-height: 420px;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(255, 245, 222, 0.82) 0%, rgba(231, 205, 165, 0.76) 100%),
                repeating-linear-gradient(45deg, rgba(153, 107, 76, 0.08) 0 6px, transparent 6px 12px);
            border-radius: 18px;
            border: 1px solid rgba(157, 108, 75, 0.24);
            padding: 16px;
        }

        .village-path {
            position: absolute;
            left: 8%;
            right: 8%;
            top: 56%;
            height: 28px;
            border-radius: 999px;
            background: linear-gradient(90deg, #d7b587, #c59c6d, #d7b587);
            opacity: 0.56;
            transform: rotate(-2deg);
        }

        .house-grid {
            position: relative;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 14px;
        }

        .house {
            position: relative;
            border-radius: 14px;
            border: 1px solid rgba(134, 88, 58, 0.32);
            background: linear-gradient(165deg, rgba(250, 236, 207, 0.96), rgba(229, 198, 154, 0.92));
            padding: 10px 10px 12px;
            text-align: left;
            cursor: pointer;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            box-shadow: 0 8px 14px rgba(117, 73, 46, 0.2);
        }

        .house:hover {
            transform: translateY(-2px);
            border-color: rgba(143, 74, 41, 0.66);
            box-shadow: 0 12px 20px rgba(117, 73, 46, 0.26);
        }

        .house.active {
            border-color: rgba(143, 74, 41, 0.95);
            box-shadow: 0 14px 24px rgba(117, 73, 46, 0.34);
        }

        .roof {
            width: 0;
            height: 0;
            border-left: 22px solid transparent;
            border-right: 22px solid transparent;
            border-bottom: 18px solid #a65b37;
            margin: 0 auto 6px;
        }

        .house-name {
            font-size: 0.98rem;
            font-weight: 700;
            color: #633726;
        }

        .house-role {
            font-size: 0.82rem;
            color: #7d5a47;
        }

        .house-mood {
            margin-top: 6px;
            display: inline-block;
            border-radius: 999px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            background: rgba(96, 155, 100, 0.14);
            color: #48764b;
        }

        .house-mood.worried {
            background: rgba(172, 78, 66, 0.16);
            color: #8a3a31;
        }

        .house-mood.steady {
            background: rgba(188, 127, 52, 0.14);
            color: #8b5e28;
        }

        .village-summary {
            margin-top: 12px;
            line-height: 1.55;
            color: #5d4436;
            font-size: 0.98rem;
            background: rgba(255, 246, 230, 0.7);
            border-radius: 12px;
            border: 1px solid rgba(162, 109, 77, 0.18);
            padding: 10px;
        }

        .metric-row {
            margin-top: 10px;
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
        }

        .metric {
            background: rgba(255, 250, 241, 0.92);
            border: 1px solid rgba(138, 92, 64, 0.16);
            border-radius: 12px;
            padding: 8px;
            text-align: center;
        }

        .metric-k {
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #8b6d58;
        }

        .metric-v {
            margin-top: 4px;
            font-size: 1.04rem;
            font-weight: 700;
            color: #644130;
        }

        .square-panel h2,
        .control-panel h2,
        .detail-panel h2 {
            color: #6a3e27;
            font-size: 1.28rem;
        }

        textarea, input {
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(173, 127, 93, 0.34);
            background: rgba(255, 252, 246, 0.92);
            color: #4c3528;
            padding: 10px;
            font: inherit;
            box-sizing: border-box;
        }

        textarea {
            min-height: 94px;
            resize: vertical;
        }

        button {
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: #fff8ec;
            border: none;
            border-radius: 999px;
            padding: 9px 14px;
            cursor: pointer;
            font: inherit;
            margin-right: 8px;
            margin-top: 8px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 14px rgba(116, 70, 43, 0.25);
        }

        .ghost-btn {
            background: transparent;
            color: #7b4f36;
            border: 1px solid rgba(135, 88, 61, 0.45);
        }

        .pill {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            background: rgba(210, 155, 91, 0.18);
            border: 1px solid rgba(210, 155, 91, 0.3);
            margin: 4px 6px 0 0;
            font-size: 0.82rem;
            color: #6f4a34;
        }

        .detail-box {
            min-height: 232px;
            background: rgba(255, 248, 235, 0.9);
            border-radius: 14px;
            border: 1px dashed rgba(148, 96, 62, 0.32);
            padding: 12px;
            line-height: 1.55;
            color: #5d4234;
        }

        .town-log {
            margin-top: 10px;
            max-height: 170px;
            overflow: auto;
            padding-right: 6px;
        }

        .town-log p {
            margin: 0 0 8px;
            font-size: 0.92rem;
            color: #684c3d;
        }

        .muted {
            color: #826858;
            font-size: 0.9rem;
        }

        .error {
            color: #8d3026;
            margin-top: 10px;
            min-height: 22px;
        }

        .mission {
            color: #6b4735;
            margin-top: 6px;
            line-height: 1.5;
            font-size: 0.95rem;
        }

        .mini-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .task-list {
            margin-top: 8px;
            padding-left: 16px;
            color: #6d4e3b;
            font-size: 0.9rem;
        }

        .task-list li { margin-bottom: 4px; }

        @media (max-width: 980px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .house-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .metric-row {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 560px) {
            .house-grid {
                grid-template-columns: 1fr;
            }

            .mini-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="hills"></div>
    <div class="wrap">
        <section class="hero">
            <div class="hero-title">
                <h1>Everwarm Village</h1>
                <div id="dayChip" class="day-chip">Day 1</div>
            </div>
            <p class="subtitle">A cozy village where each subsystem has its own house, habits, and concerns. Visit houses, hear villagers speak, and guide the town as it pursues one shared mission.</p>
            <div id="missionText" class="mission"></div>
        </section>

        <div class="grid">
            <div class="card square-panel">
                <h2>Village Square</h2>
                <div class="village-map">
                    <div class="village-path"></div>
                    <div class="house-grid" id="houseGrid"></div>
                    <div class="village-summary" id="villageSummary">The village has not reported in yet.</div>
                    <div class="metric-row" id="metricRow"></div>
                </div>
            </div>

            <div class="card detail-panel">
                <h2>Inside The House</h2>
                <div id="villagerDetail" class="detail-box">
                    Select a house in the village to talk with a villager.
                </div>
                <h3 style="margin: 14px 0 8px;">Town Log</h3>
                <div id="townLog" class="town-log"></div>
            </div>
        </div>

        <div class="grid" style="margin-top: 12px;">
            <div class="card control-panel">
                <h2>Town Actions</h2>
                <div class="row">
                    <label for="inputText">Speak To The Village</label>
                    <textarea id="inputText" placeholder="Describe an event, ask for help, or tell villagers what changed."></textarea>
                </div>
                <div class="row">
                    <label for="actionText">Action</label>
                    <input id="actionText" placeholder="observe, ask, approach, rest, define..." />
                </div>
                <button onclick="interact()">Send To Village</button>
                <button class="ghost-btn" onclick="runDailyCycle()">Run One Day</button>
                <button class="ghost-btn" onclick="resetState()">Reset Village</button>
                <div id="error" class="error"></div>
            </div>

            <div class="card">
                <h2>Goal Board</h2>
                <div id="goals"></div>
                <h3 style="margin-top: 14px;">Village Questions</h3>
                <div id="questions" class="muted"></div>
            </div>

            <div class="card">
                <h2>Teach The Lexicon</h2>
                <div class="mini-grid">
                    <div>
                        <label for="termInput">Term</label>
                        <input id="termInput" placeholder="e.g. limerence" />
                    </div>
                    <div>
                        <label for="definitionInput">Meaning</label>
                        <input id="definitionInput" placeholder="How your village uses it" />
                    </div>
                </div>
                <button onclick="teachTerm()">Teach Term</button>
            </div>
        </div>
    </div>
    <script>
        const sessionStorageKey = 'themodel_session_id';
        let cachedPayload = null;
        let selectedVillager = null;

        const roleIcons = {
            'planner': '🗺️',
            'curiosity keeper': '📚',
            'stability steward': '🛠️',
            'narrator': '🕯️',
            'architect': '🏛️',
            'caretaker': '🌿'
        };

        const fallbackVillagers = [
            { name: 'Tomas', role: 'planner', mood: 'steady' },
            { name: 'Mira', role: 'curiosity keeper', mood: 'steady' },
            { name: 'Edda', role: 'stability steward', mood: 'steady' },
            { name: 'Lio', role: 'narrator', mood: 'steady' },
            { name: 'Sable', role: 'architect', mood: 'steady' },
            { name: 'Jun', role: 'caretaker', mood: 'steady' }
        ];

        function getSessionId() {
            let sessionId = localStorage.getItem(sessionStorageKey);
            if (!sessionId) {
                sessionId = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
                localStorage.setItem(sessionStorageKey, sessionId);
            }
            return sessionId;
        }

        function moodClass(mood) {
            const lowered = (mood || '').toLowerCase();
            if (lowered.includes('worried')) return 'worried';
            if (lowered.includes('steady')) return 'steady';
            return 'hopeful';
        }

        function metricCard(label, value) {
            return `<div class="metric"><div class="metric-k">${label}</div><div class="metric-v">${value}</div></div>`;
        }

        function renderVillageHouses(villagers) {
            const houseGrid = document.getElementById('houseGrid');
            houseGrid.innerHTML = '';
            for (const villager of villagers) {
                const house = document.createElement('button');
                house.className = `house ${selectedVillager === villager.name ? 'active' : ''}`;
                house.setAttribute('type', 'button');
                house.onclick = () => openVillager(villager.name);
                const icon = roleIcons[villager.role] || '🏠';
                house.innerHTML = `
                    <div class="roof"></div>
                    <div class="house-name">${icon} ${villager.name}</div>
                    <div class="house-role">${villager.role}</div>
                    <span class="house-mood ${moodClass(villager.mood)}">${villager.mood || 'steady'}</span>
                `;
                houseGrid.appendChild(house);
            }
        }

        function renderVillagerDetail(villager) {
            const detail = document.getElementById('villagerDetail');
            if (!villager) {
                detail.innerHTML = 'Select a house in the village to talk with a villager.';
                return;
            }
            const tasks = villager.recent_tasks || [];
            const outcomes = villager.recent_outcomes || [];
            detail.innerHTML = `
                <strong>${villager.name}</strong> · ${villager.role}<br>
                <span class="muted">Mood: ${villager.mood || 'steady'}</span>
                <p style="margin: 8px 0 10px;">${villager.dialogue || 'They are quietly tending their house.'}</p>
                <div class="mini-grid">
                    <div>
                        <strong style="font-size:0.9rem;">Recent Tasks</strong>
                        <ul class="task-list">${tasks.length ? tasks.slice(-4).map(t => `<li>${t}</li>`).join('') : '<li>None yet</li>'}</ul>
                    </div>
                    <div>
                        <strong style="font-size:0.9rem;">Outcomes</strong>
                        <ul class="task-list">${outcomes.length ? outcomes.slice(-4).map(t => `<li>${t}</li>`).join('') : '<li>None yet</li>'}</ul>
                    </div>
                </div>
            `;
        }

        function renderTownLog(events) {
            const log = document.getElementById('townLog');
            const list = events && events.length ? events.slice(-8).reverse() : ['The village is waiting for its next day cycle.'];
            log.innerHTML = list.map(item => `<p>• ${item}</p>`).join('');
        }

        function render(data) {
            cachedPayload = data;
            document.getElementById('error').textContent = '';
            document.getElementById('villageSummary').textContent = data.village_dialogue || 'The village has not reported in yet.';
            document.getElementById('missionText').textContent = `Mission: ${(data.state.main_mission || {}).statement || 'Keep the village coherent and growing.'}`;
            document.getElementById('dayChip').textContent = `Day ${data.state.current_day || 1}`;

            const metrics = data.state.health_metrics || {};
            const metricRow = document.getElementById('metricRow');
            metricRow.innerHTML = [
                metricCard('Health', (metrics.global_health || 0).toFixed(2)),
                metricCard('Progress', (metrics.goal_progress_rate || 0).toFixed(2)),
                metricCard('Vocab', (metrics.vocabulary_growth_rate || 0).toFixed(2)),
                metricCard('Contradictions', metrics.contradiction_count || 0),
            ].join('');

            const goals = document.getElementById('goals');
            goals.innerHTML = '';
            for (const goal of data.state.active_goals) {
                const el = document.createElement('span');
                el.className = 'pill';
                el.textContent = `${goal.name} ${(goal.priority * 100).toFixed(0)}%`;
                goals.appendChild(el);
            }
            if (!data.state.active_goals.length) {
                goals.textContent = 'No active goals posted in the square yet.';
            }

            const questions = document.getElementById('questions');
            questions.innerHTML = '';
            for (const question of data.state.vocabulary_questions) {
                const p = document.createElement('p');
                p.textContent = question.question;
                questions.appendChild(p);
            }
            if (!data.state.vocabulary_questions.length) {
                questions.textContent = 'No unresolved vocabulary questions right now.';
            }

            const villagerItems = (data.villagers && data.villagers.length) ? data.villagers : fallbackVillagers;
            renderVillageHouses(villagerItems);
            renderTownLog(data.state.recent_events || []);

            if (!selectedVillager && villagerItems.length) {
                selectedVillager = villagerItems[0].name;
            }

            const selected = villagerItems.find(v => v.name === selectedVillager);
            renderVillagerDetail(selected);
        }

        async function openVillager(name) {
            selectedVillager = name;
            if (cachedPayload) {
                const fromCache = (cachedPayload.villagers || []).find(v => v.name === name);
                if (fromCache) {
                    render(cachedPayload);
                }
            }
            try {
                const response = await fetch(`/villager/${getSessionId()}/${encodeURIComponent(name)}`);
                const data = await response.json();
                if (response.ok) {
                    renderVillagerDetail(data);
                    renderVillageHouses((cachedPayload && cachedPayload.villagers) ? cachedPayload.villagers : fallbackVillagers);
                }
            } catch (_) {
                // Keep cached details if network request fails.
            }
        }

        async function interact() {
            const payload = {
                session_id: getSessionId(),
                text: document.getElementById('inputText').value.trim(),
                action: document.getElementById('actionText').value.trim(),
            };
            try {
                const response = await fetch('/api/interact', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Interaction failed.');
                }
                render(data);
            } catch (error) {
                document.getElementById('error').textContent = String(error);
            }
        }

        async function runDailyCycle() {
            try {
                const response = await fetch('/api/daily-cycle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: getSessionId() }),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Daily cycle failed.');
                }
                render(data);
            } catch (error) {
                document.getElementById('error').textContent = String(error);
            }
        }

        async function teachTerm() {
            const payload = {
                session_id: getSessionId(),
                term: document.getElementById('termInput').value.trim(),
                definition: document.getElementById('definitionInput').value.trim(),
            };
            try {
                const response = await fetch('/api/teach', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Teaching failed.');
                }
                document.getElementById('termInput').value = '';
                document.getElementById('definitionInput').value = '';
                render(data);
            } catch (error) {
                document.getElementById('error').textContent = String(error);
            }
        }

        async function resetState() {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: getSessionId()}),
            });
            const data = await response.json();
            cachedPayload = null;
            selectedVillager = null;
            document.getElementById('goals').textContent = '';
            document.getElementById('questions').textContent = '';
            document.getElementById('villageSummary').textContent = data.message;
            renderVillageHouses(fallbackVillagers);
            renderVillagerDetail(null);
            renderTownLog([]);
            document.getElementById('metricRow').innerHTML = '';
        }

        async function bootVillage() {
            try {
                const response = await fetch(`/api/state/${getSessionId()}`);
                const data = await response.json();
                if (response.ok) {
                    render(data);
                }
            } catch (error) {
                document.getElementById('error').textContent = `Failed to load village: ${String(error)}`;
                renderVillageHouses(fallbackVillagers);
            }
        }

        bootVillage();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(MAIN_TEMPLATE)


def _build_village_payload(engine):
    villagers = []
    if engine.state.villager_states:
        source_items = [state.to_dict() for state in engine.state.villager_states.values()]
    else:
        source_items = []
        for villager in default_villagers():
            state = villager.ensure_state(engine.state)
            source_items.append(state.to_dict())
    for data in source_items:
        villagers.append({
            "name": data["name"],
            "role": data["role"],
            "mood": data["mood"],
            "recent_tasks": data["recent_tasks"],
            "recent_outcomes": data["recent_outcomes"],
            "dialogue": villager_to_dialogue(data, engine.state.recent_events),
        })
    return {
        "state": engine.state.to_dict(),
        "villagers": villagers,
        "village_dialogue": village_summary_to_dialogue(engine.state.to_dict(), engine.state.narrative),
    }


@app.route("/api/interact", methods=["POST"])
def api_interact():
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip() or "default"
    text = (data.get("text") or "").strip()
    action = (data.get("action") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400
    try:
        engine = get_or_create_engine(session_id)
        result = engine.interact(text, action=action)
        payload = result.to_dict()
        payload.update(_build_village_payload(engine))
        return jsonify(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/state/<session_id>", methods=["GET"])
def api_state(session_id: str):
    engine = get_or_create_engine(session_id)
    return jsonify(_build_village_payload(engine))


@app.route("/village/<session_id>", methods=["GET"])
def village_overview(session_id: str):
    engine = get_or_create_engine(session_id)
    payload = _build_village_payload(engine)
    return jsonify(payload)


@app.route("/villager/<session_id>/<name>", methods=["GET"])
def villager_detail(session_id: str, name: str):
    engine = get_or_create_engine(session_id)
    villager_state = engine.state.villager_states.get(name)
    if villager_state is None:
        return jsonify({"error": f"Unknown villager: {name}"}), 404
    data = villager_state.to_dict()
    return jsonify({
        "name": data["name"],
        "role": data["role"],
        "mood": data["mood"],
        "recent_tasks": data["recent_tasks"],
        "recent_outcomes": data["recent_outcomes"],
        "dialogue": villager_to_dialogue(data, engine.state.recent_events),
        "day": engine.state.current_day,
        "mission": engine.state.main_mission.statement,
    })


@app.route("/api/daily-cycle", methods=["POST"])
def api_daily_cycle():
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip() or "default"
    engine = get_or_create_engine(session_id)
    executed = engine.run_daily_cycle()
    payload = _build_village_payload(engine)
    payload["executed_tasks"] = [task.to_dict() for task in executed]
    return jsonify(payload)


@app.route("/api/teach", methods=["POST"])
def api_teach():
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip() or "default"
    term = (data.get("term") or "").strip()
    definition = (data.get("definition") or "").strip()
    if not term or not definition:
        return jsonify({"error": "term and definition are required"}), 400
    engine = get_or_create_engine(session_id)
    engine.vocabulary.learn_definition(term, definition, source="user")
    result = engine.interact(f"I learned the term {term}.", action="define")
    payload = result.to_dict()
    payload.update(_build_village_payload(engine))
    return jsonify(payload)


@app.route("/api/reset", methods=["POST"])
def api_reset():
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip() or "default"
    reset_engine(session_id)
    return jsonify({"message": f"Reset session {session_id}."})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)