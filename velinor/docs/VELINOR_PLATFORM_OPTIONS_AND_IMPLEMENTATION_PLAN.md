# Velinor Platform Options and Implementation Plan

This document is a deep-dive reference for the two Velinor implementations in this repository and the realistic ways to ship the game across platforms.

## Executive Summary

Velinor currently exists in two materially different forms:

- `velinor/` is the Python-first prototype and engine tree. It contains the core narrative logic, state serialization, and a Streamlit-based UI path for rapid iteration.
- `velinor-web/` is a separate Next.js/React frontend with its own browser UI, local asset bundle, and API client. It is not a Flask app and should not be treated like one.

If the goal is a flagship interactive game that can eventually run as an installable Windows app without internet access, the most practical route is to keep a single headless game engine and ship it through multiple shells:

1. Browser web app for broad reach.
2. Desktop shell around the web app for Windows offline play.
3. Optional pure Python or native client only if you want to replace the web UI later.

Streamlit is best treated as the prototype/iteration path, not the final shipping UI for the flagship game.

## 1. What Exists Today

### 1.1 Python / Streamlit path (`velinor/`)

The Python tree is the most engine-heavy part of the repo. The main control surface is the orchestrator in [velinor/engine/orchestrator.py](../engine/orchestrator.py), which coordinates:

- Game state and sessions from [velinor/engine/core.py](../engine/core.py)
- Trait, coherence, and emotional state systems
- Story/session loading from the Twine-style story pipeline
- NPC response generation and event timeline handling
- Save/load and snapshot serialization via [velinor/engine/game_state.py](../engine/game_state.py)

The Streamlit UI in [velinor/streamlit_ui.py](../streamlit_ui.py) renders the live game loop, sidebar stats, glyphs, NPC perception, and the button-driven interaction model. The implementation summary in [velinor/VELINOR_STREAMLIT_IMPLEMENTATION_SUMMARY.md](../VELINOR_STREAMLIT_IMPLEMENTATION_SUMMARY.md) shows the prototype’s intent clearly: fast iteration, visible emotional systems, and a constrained UI loop.

The FastAPI layer in [velinor/api.py](../api.py) is the more useful long-term seam. It exposes the game as an HTTP service, keeps the engine behind a session store, and is the natural place to decouple the core game logic from any particular UI.

There is also a cipher/decode path in [velinor/velinor_api.py](../velinor_api.py) that connects the emotional signal system to the `emotional_os` package. That is useful for narrative and gatekeeping mechanics, but it is another sign that the Python side is really a game service plus prototype UI stack, not a single monolithic app.

### 1.2 Next.js web path (`velinor-web/`)

The web version is a separate browser app built with Next.js 16 and React 19. The dependencies in [velinor-web/package.json](../../velinor-web/package.json) are standard frontend dependencies: `next`, `react`, `react-dom`, `axios`, and `zustand`.

The main page in [velinor-web/src/app/page.tsx](../../velinor-web/src/app/page.tsx) is a client component that routes into the game flow. The game screen in [velinor-web/src/app/game/[sessionId]/page.tsx](../../velinor-web/src/app/game/%5BsessionId%5D/page.tsx) starts a backend session, stores the returned `session_id`, and renders the active scene.

The UI itself is split across reusable components such as:

- [velinor-web/src/components/TitleScreen.tsx](../../velinor-web/src/components/TitleScreen.tsx)
- [velinor-web/src/components/GameScene.tsx](../../velinor-web/src/components/GameScene.tsx)
- [velinor-web/src/components/KaeleScene.tsx](../../velinor-web/src/components/KaeleScene.tsx)
- [velinor-web/src/components/BossFight.tsx](../../velinor-web/src/components/BossFight.tsx)
- [velinor-web/src/components/ToneStatsDisplay.tsx](../../velinor-web/src/components/ToneStatsDisplay.tsx)

The client API wrapper in [velinor-web/src/lib/api.ts](../../velinor-web/src/lib/api.ts) talks to the backend over REST. The game state store in [velinor-web/src/lib/gameStore.ts](../../velinor-web/src/lib/gameStore.ts) keeps the local UI state for tone values, glyphs, and developer console toggles.

## 2. How the Two Versions Work Internally

### 2.1 Python prototype flow

The Python flow is:

`Streamlit UI` -> `Orchestrator` -> `Core engine / traits / coherence / NPC responses` -> `story session` -> `UI state`

The engine uses normalized emotional stats, story progression, NPC state, and save data. [velinor/engine/game_state.py](../engine/game_state.py) shows that the canonical save format is a full snapshot of all phases, not just a single scene choice.

The Streamlit UI is deliberately constrained:

- It renders a sidebar dashboard for tone, remnants, glyphs, skills, and NPC perception.
- It uses button-driven choices for narrative, glyph selection, and chamber encounters.
- It relies on Streamlit session state and reruns for coherence.

That makes it ideal for quick validation of mechanics, but it is not a good final shape for a polished flagship game.

### 2.2 Web flow

The web flow is:

`Next.js page` -> `title screen` -> `API client` -> `backend session` -> `rendered scene components`

[velinor-web/VELINOR_INTEGRATION_CONTRACT.md](../../velinor-web/VELINOR_INTEGRATION_CONTRACT.md) documents the contract that keeps the frontend and backend in sync:

- `POST /api/game/start`
- `POST /api/game/action`
- `GET /api/game/status`
- `POST /api/game/save`
- `GET /api/game/load`
- `GET /api/debug`

The frontend stores the backend-issued `session_id` and sends it with later calls. That means the web client is already designed as a detached UI, which is the right shape for desktop packaging later.

The current web assets are also intentionally local:

- `velinor-web/public/assets/...` contains the images the UI uses.
- `velinor-web/sync-assets.ps1` and [velinor-web/sync-assets.sh](../../velinor-web/sync-assets.sh) copy selected art from `velinor/assets/` into the web app.
- [velinor-web/src/data/scenes.json](../../velinor-web/src/data/scenes.json) contains scene graph data and background references.

## 3. Dependencies and Runtime Requirements

### 3.1 Python / Streamlit

The Streamlit prototype depends on [velinor/requirements_streamlit.txt](../requirements_streamlit.txt), which currently includes:

- `streamlit`
- `pandas`
- `pillow`
- `python-dotenv`

The Python tree also pulls in FastAPI and related backend packages through the API modules, plus the emotional signal system and any engine-side libraries imported by the orchestrator.

Practical runtime traits:

- Good for local iteration and fast prototype edits.
- Requires Python installation and the correct dependency set.
- Not suitable as the final UI layer if you want richer desktop interactions, animation, or native packaging.

### 3.2 Next.js / React

The web app depends on Node.js 20+ and the Next.js build pipeline. [velinor-web/Dockerfile](../../velinor-web/Dockerfile) shows the current packaging flow:

- Base image: Node 20
- Install dependencies with `npm ci`
- Build the app with `npm run build`
- Start with `npm start`

The `velinor-web` UI uses browser-native rendering and CSS, so it can be packaged in several ways: hosted web, local desktop shell, or eventually a PWA-style installable app.

### 3.3 Asset inventory

The repo already has a substantial art/content pipeline. In `velinor/`, the important surfaces include:

- `assets/` for backgrounds, NPCs, overlays, glyph art, structures, and some 3D/reference assets.
- `stories/` for narrative content and branch definitions.
- `music_prototypes/` and `video/` for future multimedia layers.
- `data/` for runtime data and derived artifacts.

The web version mirrors those assets under `velinor-web/public/assets/`, which is important because it means the browser app can ship the visuals locally without depending on a remote CDN.

## 4. Platform Options

### Option A: Keep Streamlit as the prototype UI

Use this when the goal is fastest mechanical iteration.

Pros:

- Fastest path for editing and testing story logic.
- Minimal UI code.
- Good for debugging the emotional systems, glyph logic, and save/load behavior.

Cons:

- Browser-style rerendering is awkward for game UX.
- Hard to make feel like a polished flagship title.
- Not a great base for a Windows installable app.

Implementation steps:

1. Keep the orchestrator and Streamlit UI aligned only for prototype scenes.
2. Avoid adding new Streamlit-only mechanics that the web app will need to rewrite later.
3. Keep the actual game logic in the engine, not in UI callbacks.

### Option B: Keep the Next.js web app as the main shipping UI

This is the best fit if you want a polished browser game first.

Pros:

- Strong interactive UI potential.
- Clear separation between scene rendering and backend state.
- Easy to host on the web and easy to wrap later in desktop shells.
- Existing code already uses local assets and a session-based API.

Cons:

- Requires Node runtime for builds and hosting.
- Still needs a backend service for stateful game logic.
- Offline play requires either local packaging or a client-side/offline mode plan.

Implementation steps:

1. Make the backend contract canonical and keep it stable.
2. Keep all gameplay rules in the engine/API layer.
3. Keep art and scene data in `public/assets` and JSON data files.
4. Add offline-friendly caching only after the main game loop is stable.

### Option C: Package the web app as a Windows desktop app with a local backend

This is the strongest path for your stated goal: installable Windows app, offline capable, still interactive.

Best implementation pattern:

- Tauri if you want a smaller desktop wrapper.
- Electron if you want the easiest path and do not mind the heavier runtime.
- Bundle or auto-launch the Python backend locally.

Pros:

- Feels like a real app, not just a browser tab.
- Can run fully offline if the backend and assets ship locally.
- Lets you keep the richer Next.js UI you already built.

Cons:

- More moving parts: desktop shell, backend process, local assets, update mechanism.
- Packaging and antivirus false positives can be annoying, especially on Windows.
- You need to decide whether the Python engine runs as a local service or is translated into another runtime.

Implementation steps:

1. Freeze the engine into a headless API that can run from localhost.
2. Put the Next.js app behind the desktop shell.
3. Ship the art bundle and story JSON locally.
4. On app startup, launch or connect to the local backend.
5. Persist saves to a local user data directory.
6. Add an offline check so the app never depends on remote services to start.

### Option D: Build a pure Python desktop app

This means replacing the browser UI with a Python desktop toolkit such as PySide6 or PyQt.

Pros:

- Single-language stack if you keep the engine in Python.
- Good control over local file access and offline saves.
- Easier to ship as a traditional Windows executable than a web stack.

Cons:

- You would be rebuilding the entire UI layer from scratch.
- Rich scene transitions and polished visuals take more time in desktop widgets than in a web UI.
- You lose the Next.js asset pipeline and React component reuse.

Implementation steps:

1. Keep the engine and save/load logic in Python.
2. Rebuild the title screen, scene renderer, HUD, and encounter screens in Qt or a similar toolkit.
3. Convert the asset paths to a desktop-safe resource system.
4. Package with PyInstaller or a similar bundler.

### Option E: Build a native game using Unity or Godot

This is the long-term “ship it like a game” option.

Pros:

- Best fit for rich animation, effects, sound, and controller-style interaction.
- Strong offline desktop story.
- Easier to grow into a truly flagship interactive title.

Cons:

- Highest rewrite cost.
- Existing React and Python UI work would mostly become reference material, not reusable code.
- Requires a new content and runtime architecture.

Implementation steps:

1. Preserve the engine rules, story JSON, and asset definitions.
2. Rebuild scenes, HUD, and encounter logic inside the game engine.
3. Recreate the save format and session model.
4. Add import tools for art, stories, and dialogue banks.

### Option F: Ship as a PWA or browser-installable offline experience

This is attractive if you want “installable” without a full desktop shell.

Pros:

- Very low friction for users.
- Installable on many systems through the browser.
- Can cache assets and some content locally.

Cons:

- True offline gameplay is harder if the backend is server-dependent.
- Complex game state and save logic are easier with a local backend or desktop shell.
- Windows app feel is weaker than a dedicated desktop package.

Implementation steps:

1. Convert as much runtime state as possible to client-local storage.
2. Cache art and story data aggressively.
3. Decide whether gameplay is fully client-side or backed by a local service.
4. Add install prompts and offline fallbacks.

## 5. Recommended Path for Velinor

If the flagship goal is interactive and eventually installable on Windows without internet, the best path is:

1. Keep the game engine headless and API-driven.
2. Use the Next.js UI as the main presentation layer.
3. Package that UI in a desktop shell for Windows.
4. Run the Python engine locally as a bundled backend.

That path preserves the work already done in `velinor-web`, avoids a full UI rewrite, and still gives you an offline desktop experience.

Streamlit should stay the prototype path only. It is excellent for iterating on narrative mechanics, but it should not be the shipping architecture for the flagship game.

## 6. Practical Migration Plan

### Phase 1: Stabilize the engine

1. Make [velinor/api.py](../api.py) the canonical game-service entrypoint.
2. Remove any UI-specific logic from the core engine.
3. Make save/load, story loading, and session state deterministic.
4. Keep assets referenced by stable IDs instead of ad hoc UI paths.

### Phase 2: Keep one canonical frontend contract

1. Keep [velinor-web/VELINOR_INTEGRATION_CONTRACT.md](../VELINOR_INTEGRATION_CONTRACT.md) synchronized with the backend.
2. Make scene responses uniform across title, narrative, encounter, and ending states.
3. Keep local asset copies under `velinor-web/public/assets`.

### Phase 3: Choose the shipping shell

- Browser-only web release if you want fastest public distribution.
- Tauri/Electron if you want installable Windows desktop.
- Native desktop engine only if you are ready to rewrite the UI for a game runtime.

### Phase 4: Packaging and offline support

1. Store saves under the user profile, not inside the app directory.
2. Bundle story JSON and art locally.
3. Add an app-startup check that can launch the backend automatically.
4. Test fresh installs on Windows with no network access.

## 7. Bottom Line

Velinor already has the raw ingredients for a real flagship game:

- A meaningful Python engine.
- A browser-first React/Next.js UI.
- A session-based API contract.
- A local asset pipeline.

The best next move is not to force Flask into the web client. It is to pick one UI direction and standardize the engine behind it. For your offline Windows dream, the web UI plus a local desktop shell is the shortest path that preserves the most work.