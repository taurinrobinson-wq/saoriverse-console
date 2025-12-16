# Velinor Web Stack Documentation Index

## Quick Reference

Start here based on what you need:

### 🚀 I Just Want to Run It
→ **`VELINOR_WEB_QUICK_START.md`** - 3 steps, 5 minutes

### 📋 I Want Detailed Setup Instructions
→ **`RUN_VELINOR_WEB.md`** - Full guide with troubleshooting

### ✅ I Want to Know What Was Built
→ **`VELINOR_WEB_SETUP_COMPLETE.md`** - Architecture, checklist, status

### 🏗️ I Want Architecture Details
→ **`VELINOR_WEB_MIGRATION.md`** - Why we switched, how it works
##

## What's in This Stack?

### Backend: FastAPI (`velinor_api.py`)
- REST API for game management
- Session handling
- Wraps VelinorTwineOrchestrator
- Runs on `http://localhost:8000`

### Frontend: Next.js (`velinor-web/`)
- React 18 + TypeScript
- Splash screen with player name input
- Game scene with overlays on background images
- API client for backend communication
- Runs on `http://localhost:3000`

### How They Talk

```
Frontend (http://localhost:3000)
    ↓ (HTTP)
FastAPI Backend (http://localhost:8000)
    ↓ (Python)
Velinor Game Engine
```


##

## The 3-Step Start

**Terminal 1:**

```bash
cd d:\saoriverse-console
python velinor_api.py
```



**Terminal 2:**

```bash
cd d:\saoriverse-console\velinor-web
npm run dev
```



**Browser:** Open `http://localhost:3000`

That's it! You should see the splash screen.
##

## Why This Works Better Than Streamlit

✅ **Button Overlays** - Can now position buttons on top of background images
✅ **Z-index Control** - Full layering support
✅ **Animations** - Smooth hover effects, transitions
✅ **Custom Layout** - Not constrained to columns/expanders
✅ **Performance** - Lightweight React vs heavy Streamlit
##

## File Structure

```
d:\saoriverse-console\
├── Backend
│   └── velinor_api.py                     ← Start this first
│
├── Frontend (velinor-web/)
│   ├── Screens
│   │   ├── app/page.tsx                   ← Splash screen
│   │   └── app/game/[sessionId]/page.tsx  ← Game scene
│   │
│   ├── Components
│   │   └── components/GameScene.tsx       ← Game renderer
│   │
│   ├── API Client
│   │   └── lib/api.ts                     ← Calls backend
│   │
│   ├── Config
│   │   ├── .env.local                     ← API URL
│   │   ├── package.json                   ← Dependencies
│   │   └── tsconfig.json                  ← TypeScript config
│   │
│   └── Assets
│       └── public/assets/
│           ├── backgrounds/               ← Your background images
│           ├── overlays/                  ← Overlay PNGs
│           └── npcs/                      ← Character images
│
└── Documentation
    ├── VELINOR_WEB_QUICK_START.md         ← Start here
    ├── RUN_VELINOR_WEB.md                 ← Detailed guide
    ├── VELINOR_WEB_SETUP_COMPLETE.md      ← Full status
    └── VELINOR_WEB_MIGRATION.md           ← Architecture
```


##

## Next Actions

1. **Test Locally** - Follow `VELINOR_WEB_QUICK_START.md`
2. **Add Your Game Assets** - Copy images to `velinor-web/public/assets/`
3. **Deploy to Production** - Push to git, Railway auto-deploys
4. **Optional: Fix Linting Warnings** - Move inline styles to CSS files
##

## Key Endpoints

### Backend API (localhost:8000)

- `GET /` - Health check
- `POST /api/game/start` - Create new game
- `POST /api/game/{session_id}/action` - Player choice
- `GET /api/game/{session_id}` - Get current state
- `POST /api/game/{session_id}/save` - Save game
- `POST /api/game/{session_id}/load` - Load game
- `DELETE /api/game/{session_id}` - End session
- `GET /api/sessions` - List active sessions

### Frontend Pages (localhost:3000)

- `/` - Splash screen (enter player name)
- `/game/[sessionId]` - Game scene (play the game)
##

## Troubleshooting Quick Links

**Backend won't start?**
→ `RUN_VELINOR_WEB.md` → Troubleshooting section

**Frontend shows errors?**
→ `RUN_VELINOR_WEB.md` → Troubleshooting section

**API returns 404?**
→ Make sure backend is running on terminal 1

**Button overlays not working?**
→ Check browser console (F12) for JavaScript errors
##

## Environment Configuration

`.env.local` (in `velinor-web/`)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```



Change this to your Railway backend domain for production.
##

## You're All Set! 🎉

The entire web stack is ready to run.

**Start with:** `VELINOR_WEB_QUICK_START.md` (3 steps, 5 minutes)

Happy gaming! 🎮
