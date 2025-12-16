# 🎮 Velinor: Web Stack Migration - Complete

## What Changed

You're ditching **Streamlit** and moving to a proper **web stack** because Streamlit's rendering model can't handle the layered overlays and interactive positioning you want for Velinor.

##

## New Architecture

```text
```

Your Computer (Dev)          Railway Server (Production)
═══════════════════          ════════════════════════════

Backend:                     Backend:
python velinor_api.py        FastAPI (auto-deployed)
<http://localhost:8000>        <https://your-domain.up.railway.app>

Frontend:                    Frontend:
npm run dev                  Next.js (auto-deployed)
<http://localhost:3000>        <https://your-domain.up.railway.app>

Game Engine:                 Game Engine:
Velinor (Python)             Velinor (Python) - embedded in backend

```


##

## What You Have Now

### ✅ Backend
- **File**: `velinor_api.py`
- **What it does**: Wraps your Velinor game engine as REST API
- **Endpoints**:
  - `POST /api/game/start` - Create game session
  - `POST /api/game/{id}/action` - Process player choices
  - `GET/POST/DELETE /api/game/{id}` - Manage sessions

### ✅ Frontend Scaffolding
- **`frontend_lib_api.ts`** - TypeScript API client for axios
- **`frontend_GameScene.tsx`** - React component with:
  - Background image
  - Overlay support (dust, fog, glyphs)
  - Narration box with dark overlay
  - Interactive choice buttons (fully positioned)
  - Custom input field

### ✅ Documentation
- **`VELINOR_WEB_MIGRATION.md`** - Step-by-step setup (6 phases)
- **`NEXTJS_FRONTEND_SETUP.md`** - Detailed Next.js configuration
- **`RAILWAY_DEPLOYMENT.md`** - Production deployment guide
- **`VELINOR_WEB_QUICK_REFERENCE.md`** - Quick command reference
##

## Quick Start (3 Steps)

### Step 1: Create Next.js App

```bash

npx create-next-app@latest velinor-web --typescript --tailwind --eslint --no-git
cd velinor-web

```text
```

### Step 2: Copy Components

```bash

# From repo root
cp frontend_lib_api.ts velinor-web/lib/api.ts
```text
```text
```

### Step 3: Create Pages

- `velinor-web/app/page.tsx` - Splash screen (see `VELINOR_WEB_MIGRATION.md`)
- `velinor-web/app/game/[sessionId]/page.tsx` - Game scene

### Step 4: Test

```bash


# Terminal 1
python velinor_api.py

# Terminal 2
cd velinor-web && npm run dev

```text
```

### Step 5: Deploy

```bash
git add .
git commit -m "feat: Next.js + FastAPI Velinor game"
git push origin main

```text
```text
```

##

## Why This is Better Than Streamlit

| Aspect | Streamlit | Next.js + FastAPI |
|--------|-----------|-------------------|
| **Overlays** | ❌ Doesn't support z-index | ✅ Full control |
| **Button Positioning** | ❌ Linear flow | ✅ Absolute positioning |
| **Styling** | ⚠️ Limited | ✅ Full CSS |
| **Performance** | ⚠️ Slow rerenders | ✅ Fast client-side |
| **Mobile** | ⚠️ Not optimized | ✅ Responsive by default |
| **Animations** | ❌ Not supported | ✅ Framer Motion, CSS |
| **Customization** | ⚠️ Limited | ✅ Unlimited |

##

## File Organization

```

saoriverse-console/
├── velinor/                         ← Game engine (unchanged)
│   ├── engine/
│   ├── stories/
│   └── assets/
│
├── velinor_api.py                   ← NEW: FastAPI backend
├── velinor_app.py                   ← OLD: Streamlit (can delete)
│
├── VELINOR_WEB_MIGRATION.md         ← START HERE
├── NEXTJS_FRONTEND_SETUP.md         ← Setup details
├── RAILWAY_DEPLOYMENT.md             ← Production deploy
├── VELINOR_WEB_QUICK_REFERENCE.md   ← Commands & reference
│
├── frontend_lib_api.ts              ← Copy to velinor-web/lib/
├── frontend_GameScene.tsx           ← Copy to velinor-web/components/
│
└── velinor-web/                     ← NEW: Next.js project (create this)
    ├── app/
    │   ├── page.tsx                 ← Splash screen
    │   └── game/[sessionId]/page.tsx ← Game scene
    ├── components/
    │   └── GameScene.tsx            ← Renderer (copy here)
    ├── lib/
    │   └── api.ts                   ← API client (copy here)
    ├── public/assets/
    │   ├── backgrounds/             ← Copy from velinor/backgrounds/
    │   ├── overlays/                ← NEW: dust, fog, glyphs
    │   └── npcs/                    ← Copy from velinor/npcs/

```text
```

##

## Key Differences from Streamlit

### Before (Streamlit - Broken)

```python

# Streamlit can't layer properly
st.image(splash_img)  # Shows image
st.button("Start")    # Shows below, not on top

```text
```text
```

### After (Next.js - Works)

```jsx

<div style={{ position: 'relative' }}>
  <img src="background" style={{ position: 'absolute' }} />
  <button style={{ position: 'absolute', bottom: '20px' }}>
    Start  {/* Button is truly on top */}
  </button>

```text
```

##

## What Happens When You Push

1. You `git push origin main`
2. GitHub notifies Railway of changes
3. Railway reads `Procfile` and deploys:
   - `velinor_api.py` (FastAPI backend)
   - `velinor-web/` (Next.js frontend)
4. Your game is live in ~3-5 minutes
5. Users visit `https://your-railway-domain.up.railway.app`

##

## Next Phase

Once you have it running locally:

### Phase A: Add Scene Styling

- Add background images to `velinor-web/public/assets/backgrounds/`
- Create overlay PNGs for dust/fog/glyphs
- Update `GameScene.tsx` to load them dynamically

### Phase B: Enhance UI

- Add animations with Framer Motion
- Add sound with Howler.js
- Add glyph rendering
- Add stats panel

### Phase C: Mobile Optimization

- Test on phone (might need `--host 0.0.0.0` locally)
- Adjust button sizes for touch
- Responsive image sizing

### Phase D: Advanced Features

- Save/load system with database
- Multiplayer sessions
- Settings panel
- Achievements/progress tracking

##

## Documentation Map

```
START → VELINOR_WEB_MIGRATION.md (complete guide, 6 phases)
  ├─→ NEXTJS_FRONTEND_SETUP.md (detailed setup)
  ├─→ RAILWAY_DEPLOYMENT.md (production deploy)
  ├─→ VELINOR_WEB_QUICK_REFERENCE.md (commands)
```text
```text
```

##

## Commands You'll Need

```bash


# Create Next.js project (one time)
npx create-next-app@latest velinor-web --typescript --tailwind --eslint --no-git

# Install dependencies (one time)
cd velinor-web && npm install axios zustand

# Development (every session)

# Terminal 1:
python velinor_api.py

# Terminal 2:
cd velinor-web && npm run dev

# Deployment (when ready)
git add .
git commit -m "your message"
git push origin main

```

##

## Success Criteria

You'll know it's working when:

- ✅ You can start a game and see the splash screen
- ✅ You can enter a player name
- ✅ You can click "Start New Game"
- ✅ A game scene loads with background image
- ✅ You can click a choice and the scene updates
- ✅ Custom text input works
- ✅ It's responsive on mobile

##

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `CORS error` | Already handled in `velinor_api.py` |
| `API returns 404` | Check `NEXT_PUBLIC_API_URL` in `.env.local` |
| `Images not loading` | Ensure files are in `velinor-web/public/assets/` |
| `Slow to start` | Backend initializes - takes 1-2 seconds |
| `Button doesn't work` | Check browser console for errors |

##

## What's Next for You

1. **Now**: Read `VELINOR_WEB_MIGRATION.md` (your roadmap)
2. **Step 1**: Run the `npx create-next-app` command
3. **Step 2**: Copy the component files
4. **Step 3**: Create the page files
5. **Step 4**: Test locally (backend + frontend)
6. **Step 5**: Deploy to Railway
7. **Done**: Your Velinor game is live!

##

**Total time to first deployment:** ~30-45 minutes

**Estimated effort:** Low (most work is already scaffolded)

**Complexity**: Medium (setting up two services, but well-documented)

##

## Questions?

Check the documentation files or the Velinor game engine guide:

- `VELINOR_WEB_MIGRATION.md` - Complete step-by-step
- `velinor/TWINE_INTEGRATION_GUIDE.md` - Game engine API
- `RAILWAY_DEPLOYMENT.md` - Production specifics

##

**Ready to build the web version of Velinor?**

Start with: `VELINOR_WEB_MIGRATION.md` → Phase 1
