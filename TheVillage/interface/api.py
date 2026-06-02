"""Flask interface for TheVillage.

Adapted from the session-oriented UI pattern already present in limbic_ai/app.py.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template_string, request

from TheVillage.core.mind import get_or_create_engine, reset_engine
from TheVillage.core.villagers import default_villagers
from TheVillage.interface.dialogue import village_summary_to_dialogue, villager_to_dialogue
from TheVillage.memory.store import save_state


app = Flask(__name__)


def get_color_scheme(hour: int) -> dict:
    normalized_hour = hour % 24
    if 6 <= normalized_hour < 8:
        return {
            "sky_top": "#f4a58f",
            "sky_mid": "#ffc49f",
            "sky_bottom": "#ffe2ba",
            "ground": "#d7ae82",
            "panel": "rgba(255, 246, 236, 0.9)",
            "ink": "#3b2b25",
            "ink_soft": "#6a5449",
            "accent": "#ca6f57",
            "accent_strong": "#9d4d3a",
            "house_start": "rgba(255, 224, 200, 0.96)",
            "house_end": "rgba(236, 186, 154, 0.92)",
            "dream_bg": "rgba(255, 236, 220, 0.75)",
            "dream_border": "rgba(202, 111, 87, 0.45)",
        }
    if 8 <= normalized_hour < 17:
        return {
            "sky_top": "#f8c98d",
            "sky_mid": "#ffdcae",
            "sky_bottom": "#ffeccf",
            "ground": "#d6b07e",
            "panel": "rgba(255, 251, 241, 0.9)",
            "ink": "#3b2d23",
            "ink_soft": "#6a5647",
            "accent": "#bf6f3f",
            "accent_strong": "#8f4a29",
            "house_start": "rgba(250, 236, 207, 0.96)",
            "house_end": "rgba(229, 198, 154, 0.92)",
            "dream_bg": "rgba(255, 239, 216, 0.72)",
            "dream_border": "rgba(191, 111, 63, 0.42)",
        }
    if 17 <= normalized_hour < 20:
        return {
            "sky_top": "#e4875c",
            "sky_mid": "#f0aa66",
            "sky_bottom": "#ffd08f",
            "ground": "#b88c64",
            "panel": "rgba(255, 244, 230, 0.9)",
            "ink": "#3f2a22",
            "ink_soft": "#6d5245",
            "accent": "#c0563b",
            "accent_strong": "#8a3728",
            "house_start": "rgba(247, 208, 167, 0.96)",
            "house_end": "rgba(218, 158, 115, 0.92)",
            "dream_bg": "rgba(255, 226, 188, 0.72)",
            "dream_border": "rgba(192, 86, 59, 0.42)",
        }
    return {
        "sky_top": "#1b2545",
        "sky_mid": "#234066",
        "sky_bottom": "#35526f",
        "ground": "#4f5f69",
        "panel": "rgba(236, 240, 255, 0.9)",
        "ink": "#222238",
        "ink_soft": "#4f4d70",
        "accent": "#4f83a1",
        "accent_strong": "#2f5f7c",
        "house_start": "rgba(211, 226, 241, 0.96)",
        "house_end": "rgba(171, 198, 219, 0.92)",
        "dream_bg": "rgba(208, 225, 246, 0.72)",
        "dream_border": "rgba(79, 131, 161, 0.45)",
    }


MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Village</title>
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
            --house-start: rgba(250, 236, 207, 0.96);
            --house-end: rgba(229, 198, 154, 0.92);
            --dream-bg: rgba(255, 239, 216, 0.72);
            --dream-border: rgba(191, 111, 63, 0.42);
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
            background: linear-gradient(165deg, var(--house-start), var(--house-end));
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

        .footer-note {
            margin-top: 12px;
            color: var(--ink-soft);
            font-size: 0.88rem;
            text-align: right;
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

        .house-brief {
            margin-top: 10px;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid rgba(140, 96, 67, 0.2);
            background: rgba(255, 248, 235, 0.78);
        }

        .dream-box {
            margin: 8px 0;
            padding: 8px 10px;
            border-radius: 10px;
            background: var(--dream-bg);
            border: 1px solid var(--dream-border);
        }

        .choice-grid {
            margin-top: 8px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 6px;
        }

        .choice-btn {
            width: 100%;
            text-align: left;
            border-radius: 10px;
            border: 1px solid rgba(133, 92, 67, 0.35);
            background: rgba(255, 252, 246, 0.95);
            color: #5b3f31;
            padding: 8px 10px;
            cursor: pointer;
            margin: 0;
            transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
        }

        .choice-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 10px rgba(117, 73, 46, 0.15);
            border-color: rgba(143, 74, 41, 0.75);
        }

        .choice-btn.selected {
            border-color: rgba(93, 143, 83, 0.8);
            background: rgba(226, 246, 228, 0.95);
            color: #315436;
            box-shadow: 0 6px 10px rgba(69, 116, 72, 0.18);
        }

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
        <div class="footer-note">The village clock and colors shift by hour.</div>
    </div>
    <script>
        const sessionStorageKey = 'thevillage_session_id';
        let cachedPayload = null;
        let selectedVillager = null;

        const roleIcons = {
            'planner': '🗺️',
            'curiosity keeper': '📚',
            'stability steward': '🛠️',
            'narrator': '🕯️',
            'architect': '🏛️',
            'caretaker': '🌿',
            'oracle': '🔮'
        };

        const fallbackVillagers = [
            { name: 'Tomas', role: 'planner', mood: 'steady' },
            { name: 'Mira', role: 'curiosity keeper', mood: 'steady' },
            { name: 'Edda', role: 'stability steward', mood: 'steady' },
            { name: 'Lio', role: 'narrator', mood: 'steady' },
            { name: 'Sable', role: 'architect', mood: 'steady' },
            { name: 'Jun', role: 'caretaker', mood: 'steady' },
            { name: 'Aura', role: 'oracle', mood: 'watchful' }
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

        function applyColorScheme(scheme) {
            if (!scheme) return;
            const root = document.documentElement;
            const mappings = {
                '--sky-top': 'sky_top',
                '--sky-mid': 'sky_mid',
                '--sky-bottom': 'sky_bottom',
                '--ground': 'ground',
                '--panel': 'panel',
                '--ink': 'ink',
                '--ink-soft': 'ink_soft',
                '--accent': 'accent',
                '--accent-strong': 'accent_strong',
                '--house-start': 'house_start',
                '--house-end': 'house_end',
                '--dream-bg': 'dream_bg',
                '--dream-border': 'dream_border',
            };
            for (const [cssVar, key] of Object.entries(mappings)) {
                if (scheme[key]) root.style.setProperty(cssVar, scheme[key]);
            }
        }

        function renderVillageHouses(villagers, auraData) {
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

            const aura = auraData || { name: 'Aura', role: 'oracle', mood: 'watchful' };
            const shrine = document.createElement('button');
            shrine.className = `house ${selectedVillager === aura.name ? 'active' : ''}`;
            shrine.setAttribute('type', 'button');
            shrine.onclick = () => openVillager(aura.name);
            shrine.innerHTML = `
                <div class="roof"></div>
                <div class="house-name">🔮 ${aura.name}</div>
                <div class="house-role">${aura.role}</div>
                <span class="house-mood steady">${aura.mood || 'watchful'}</span>
            `;
            houseGrid.appendChild(shrine);
        }

        function renderVillagerDetail(villager) {
            const detail = document.getElementById('villagerDetail');
            if (!villager) {
                detail.innerHTML = 'Select a house in the village to talk with a villager.';
                return;
            }
            if ((villager.role || '').toLowerCase() === 'oracle') {
                const recent = Array.isArray(villager.recent_syntheses) ? villager.recent_syntheses : [];
                const synthHtml = recent.length
                    ? `<ul class="task-list">${recent.map(item => `<li>${item}</li>`).join('')}</ul>`
                    : '<p class="muted">No syntheses recorded yet.</p>';
                detail.innerHTML = `
                    <strong>${villager.name}</strong> · ${villager.role}<br>
                    <span class="muted">Read-only locus</span>
                    <div class="house-brief">
                        <strong style="font-size:0.9rem;">Today's Forecast</strong>
                        <p style="margin: 4px 0 8px;">${villager.forecast || 'Aura is listening beneath the village noise.'}</p>
                        <strong style="font-size:0.9rem;">Arc Theme</strong>
                        <p style="margin: 4px 0 8px;">${villager.arc_theme || 'neutral'}</p>
                        <strong style="font-size:0.9rem;">Tension</strong>
                        <p style="margin: 4px 0 8px;">${typeof villager.tension === 'number' ? villager.tension.toFixed(2) : '0.00'}</p>
                        <strong style="font-size:0.9rem;">Recent Syntheses</strong>
                        ${synthHtml}
                    </div>
                `;
                return;
            }
            const tasks = villager.recent_tasks || [];
            const outcomes = villager.recent_outcomes || [];
            const brief = villager.house_brief || {};
            const dreamInsight = brief.dream_insight || null;
            const aspiration = brief.aspiration || null;
            const choices = Array.isArray(brief.choices) ? brief.choices.slice(0, 4) : [];
            const selected = Number.isInteger(brief.selected_choice) ? brief.selected_choice : null;
            const choicesHtml = choices.length
                ? choices.map((choice, index) => `
                    <button type="button" class="choice-btn ${selected === index ? 'selected' : ''}" onclick="chooseHouseOption(${index})">
                        ${index + 1}. ${choice}
                    </button>
                `).join('')
                : '<p class="muted">No guidance choices are available yet.</p>';
            detail.innerHTML = `
                <strong>${villager.name}</strong> · ${villager.role}<br>
                <span class="muted">Mood: ${villager.mood || 'steady'}</span>
                <p style="margin: 8px 0 10px;">${villager.dialogue || 'They are quietly tending their house.'}</p>
                <div class="house-brief">
                    <strong style="font-size:0.9rem;">House Goal</strong>
                    <p style="margin: 4px 0 8px;">${brief.house_goal || 'This house is waiting for a clear goal.'}</p>
                    <strong style="font-size:0.9rem;">Problem</strong>
                    <p style="margin: 4px 0 8px;">${brief.problem_statement || 'No explicit problem has been posted yet.'}</p>
                    <strong style="font-size:0.9rem;">Guidance Request</strong>
                    <p style="margin: 4px 0 8px;">${brief.guidance_request || 'Choose a direction for this house.'}</p>
                    ${dreamInsight ? `<div class="dream-box"><strong style="font-size:0.9rem;">Dream Insight</strong><p style="margin: 4px 0 0;">${dreamInsight}</p></div>` : ''}
                    ${aspiration ? `<div class="dream-box"><strong style="font-size:0.9rem;">Emerging Aspiration</strong><p style="margin: 4px 0 0;">${aspiration}</p></div>` : ''}
                    <div class="choice-grid">${choicesHtml}</div>
                </div>
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
            applyColorScheme(data.color_scheme || null);
            document.getElementById('villageSummary').textContent = data.village_dialogue || 'The village has not reported in yet.';
            document.getElementById('missionText').textContent = `Mission: ${(data.state.main_mission || {}).statement || 'Keep the village coherent and growing.'}`;
            document.getElementById('dayChip').textContent = `Day ${data.state.current_day || 1} • Hour ${String(data.state.current_hour || 0).padStart(2, '0')}`;

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
            renderVillageHouses(villagerItems, data.aura || null);
            renderTownLog(data.state.recent_events || []);

            if (!selectedVillager && villagerItems.length) {
                selectedVillager = villagerItems[0].name;
            }

            const selected = villagerItems.find(v => v.name === selectedVillager);
            if (selectedVillager === 'Aura') {
                renderVillagerDetail(data.aura || { name: 'Aura', role: 'oracle', mood: 'watchful' });
            } else {
                renderVillagerDetail(selected);
            }
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
                if (name === 'Aura') {
                    const auraResp = await fetch(`/aura/${getSessionId()}`);
                    const auraData = await auraResp.json();
                    if (auraResp.ok) {
                        renderVillagerDetail(auraData);
                        renderVillageHouses((cachedPayload && cachedPayload.villagers) ? cachedPayload.villagers : fallbackVillagers, auraData);
                    }
                    return;
                }
                const response = await fetch(`/villager/${getSessionId()}/${encodeURIComponent(name)}`);
                const data = await response.json();
                if (response.ok) {
                    renderVillagerDetail(data);
                    renderVillageHouses((cachedPayload && cachedPayload.villagers) ? cachedPayload.villagers : fallbackVillagers, cachedPayload ? cachedPayload.aura : null);
                }
            } catch (_) {
                // Keep cached details if network request fails.
            }
        }

        async function chooseHouseOption(choiceIndex) {
            if (!selectedVillager) return;
            if (selectedVillager === 'Aura') return;
            const payload = {
                session_id: getSessionId(),
                villager_name: selectedVillager,
                choice_index: choiceIndex,
            };
            try {
                const response = await fetch('/api/villager-choice', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Could not apply house guidance choice.');
                }
                render(data);
            } catch (error) {
                document.getElementById('error').textContent = String(error);
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
            renderVillageHouses(fallbackVillagers, null);
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
                renderVillageHouses(fallbackVillagers, null);
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
            "house_brief": data.get("house_brief", {}),
            "dialogue": villager_to_dialogue(data, engine.state.recent_events),
        })

    aura = {
        "name": "Aura",
        "role": "oracle",
        "mood": "watchful",
        "forecast": engine.state.aura_forecast,
        "arc_theme": engine.state.aura_arc_theme,
        "tension": engine.state.aura_tension,
        "recent_syntheses": (engine.state.aura_dream_history or [])[-3:],
    }
    return {
        "state": engine.state.to_dict(),
        "villagers": villagers,
        "aura": aura,
        "village_dialogue": village_summary_to_dialogue(engine.state.to_dict(), engine.state.narrative),
        "color_scheme": get_color_scheme(engine.state.current_hour),
    }


def _build_villager_detail_payload(engine, data: dict) -> dict:
    return {
        "name": data["name"],
        "role": data["role"],
        "mood": data["mood"],
        "recent_tasks": data["recent_tasks"],
        "recent_outcomes": data["recent_outcomes"],
        "house_brief": data.get("house_brief", {}),
        "dialogue": villager_to_dialogue(data, engine.state.recent_events),
        "day": engine.state.current_day,
        "mission": engine.state.main_mission.statement,
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
    return jsonify(_build_villager_detail_payload(engine, data))


@app.route("/aura/<session_id>", methods=["GET"])
def aura_detail(session_id: str):
    engine = get_or_create_engine(session_id)
    return jsonify({
        "name": "Aura",
        "role": "oracle",
        "forecast": engine.state.aura_forecast,
        "arc_theme": engine.state.aura_arc_theme,
        "tension": engine.state.aura_tension,
        "recent_syntheses": (engine.state.aura_dream_history or [])[-3:],
    })


@app.route("/aura", methods=["GET"])
def aura_default_detail():
    session_id = (request.args.get("session_id") or "default").strip() or "default"
    return aura_detail(session_id)


@app.route("/api/villager-choice", methods=["POST"])
def api_villager_choice():
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip() or "default"
    villager_name = (data.get("villager_name") or "").strip()
    choice_raw = data.get("choice_index")

    if not villager_name:
        return jsonify({"error": "villager_name is required"}), 400
    if choice_raw is None:
        return jsonify({"error": "choice_index is required"}), 400
    try:
        choice_index = int(choice_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "choice_index must be an integer"}), 400

    engine = get_or_create_engine(session_id)
    villager_state = engine.state.villager_states.get(villager_name)
    if villager_state is None:
        for villager in default_villagers():
            if villager.name == villager_name:
                villager_state = villager.ensure_state(engine.state)
                break
    if villager_state is None:
        return jsonify({"error": f"Unknown villager: {villager_name}"}), 404

    choices = villager_state.house_brief.choices or []
    if choice_index < 0 or choice_index >= len(choices):
        return jsonify({"error": f"choice_index must be between 0 and {max(0, len(choices) - 1)}"}), 400

    villager_state.house_brief.selected_choice = choice_index
    villager_state.house_brief.last_updated_turn = engine.state.turn_index
    selected_text = choices[choice_index]
    engine.state.recent_events.append(
        f"{villager_name} accepted guidance option {choice_index + 1}: {selected_text}"
    )
    engine.state.recent_events = engine.state.recent_events[-20:]
    save_state(engine.state)

    return jsonify(_build_village_payload(engine))


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