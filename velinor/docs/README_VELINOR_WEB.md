# 🎮 Velinor: Web Stack Implementation - Index

## 📚 Documentation Overview

This is your complete guide to migrating Velinor from Streamlit to a proper web stack.

### **START HERE** ⭐

- **[VELINOR_WEB_COMPLETE.md](VELINOR_WEB_COMPLETE.md)** - Complete overview & migration summary

### **Then Read** (In Order)

1. **[VELINOR_WEB_MIGRATION.md](VELINOR_WEB_MIGRATION.md)** - 6-phase step-by-step setup guide 2.
**[NEXTJS_FRONTEND_SETUP.md](NEXTJS_FRONTEND_SETUP.md)** - Detailed Next.js configuration 3.
**[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - Production deployment to Railway 4.
**[VELINOR_WEB_QUICK_REFERENCE.md](VELINOR_WEB_QUICK_REFERENCE.md)** - Command reference &
troubleshooting

### **Reference** (As Needed)

- **[velinor/TWINE_INTEGRATION_GUIDE.md](velinor/TWINE_INTEGRATION_GUIDE.md)** - Velinor game engine API
- **[velinor/README.md](velinor/README.md)** - Game engine overview
- **[velinor/QUICKSTART.md](velinor/QUICKSTART.md)** - Scene examples

##

## 🛠️ Files Created for You

### Backend

```text
```


velinor_api.py          FastAPI server that wraps Velinor engine
                        - Session management
                        - Game state handling
                        - API endpoints

```



### Frontend Components
```text

```text
```


frontend_lib_api.ts     TypeScript API client for axios
                        - Game start
                        - Action processing
                        - Session management

frontend_GameScene.tsx  React component for game scenes
                        - Background image rendering
                        - Overlay support
                        - Narration box
                        - Choice buttons (absolutely positioned)
                        - Custom input

```




### Documentation

```text

```

VELINOR_WEB_COMPLETE.md         Complete overview (read first!)
VELINOR_WEB_MIGRATION.md        Step-by-step setup (6 phases)
NEXTJS_FRONTEND_SETUP.md        Detailed Next.js guide
RAILWAY_DEPLOYMENT.md            Production deployment
VELINOR_WEB_QUICK_REFERENCE.md  Commands & troubleshooting

```



##

## 🚀 Quick Start (The Absolute Minimum)

```bash


## Phase 1: Create Next.js project
npx create-next-app@latest velinor-web --typescript --tailwind --eslint --no-git
cd velinor-web
npm install axios zustand

## Phase 2: Copy components
cp ../frontend_lib_api.ts lib/api.ts
cp ../frontend_GameScene.tsx components/GameScene.tsx

## Phase 3: Create pages

## → app/page.tsx (splash screen)

## → app/game/[sessionId]/page.tsx (game scene)

## See VELINOR_WEB_MIGRATION.md for code

## Phase 4: Test locally

## Terminal 1:
python velinor_api.py

## Terminal 2:
npm run dev

## Phase 5: Deploy
git add .
git commit -m "Velinor web game"

```text

```

##

## 📊 Architecture

```

Next.js Frontend (http://localhost:3000)
                             │
Game Scene Component
                    ├─ Background Image
                    ├─ Overlay (Dust/Fog/Glyphs)
                    ├─ Narration Box
                    ├─ Choice Buttons (absolute positioned!)
                    └─ Custom Input
                             │
                             │ HTTP/REST
▼ FastAPI Backend (http://localhost:8000)
                             │
Game Logic & State
                    ├─ Session Management
                    ├─ Velinor Engine
                    ├─ Dice Rolls
                    ├─ NPC Dialogue

```text
```text

```

##

## 🎯 What You Get

✅ **Full Overlay Control** - Position buttons & text anywhere
✅ **Responsive Design** - Works on desktop, tablet, mobile
✅ **Professional Look** - Dark theme, smooth interactions
✅ **Complete Game Flow** - Splash screen → scenes → branching
✅ **Easy to Expand** - Add scenes, change overlays, customize styling
✅ **One-Click Deploy** - Push to GitHub, Railway auto-deploys
✅ **No More Streamlit Limitations** - Full CSS, animations, z-index control

##

## 📖 Reading Map

```


Are you...              Then read... ───────────────────────────────────────────────────────────
Starting fresh?         VELINOR_WEB_COMPLETE.md Ready to set up?        VELINOR_WEB_MIGRATION.md
(Phase 1) Stuck on Next.js?       NEXTJS_FRONTEND_SETUP.md Ready to deploy? RAILWAY_DEPLOYMENT.md
Forgot a command?       VELINOR_WEB_QUICK_REFERENCE.md

```text
```


##

## ⚡ Key Commands

```bash

## Create project
npx create-next-app@latest velinor-web --typescript --tailwind --eslint --no-git

## Install deps
cd velinor-web && npm install axios zustand

## Run backend
python velinor_api.py

## Run frontend
cd velinor-web && npm run dev

## Deploy
```text

```text
```


##

## 📋 Checklist

- [ ] Read `VELINOR_WEB_COMPLETE.md`
- [ ] Run `npx create-next-app` command
- [ ] Copy `frontend_*` files to `velinor-web/`
- [ ] Create splash screen page (`app/page.tsx`)
- [ ] Create game scene page (`app/game/[sessionId]/page.tsx`)
- [ ] Copy game assets to `velinor-web/public/assets/`
- [ ] Test locally (backend + frontend)
- [ ] Deploy to Railway
- [ ] Verify at your Railway domain

##

## 🆘 Troubleshooting

| Issue | Solution | More Info |
|-------|----------|-----------|
| API returns 404 | Check `NEXT_PUBLIC_API_URL` in `.env.local` | RAILWAY_DEPLOYMENT.md |
| Images not loading | Ensure assets in `velinor-web/public/assets/` | NEXTJS_FRONTEND_SETUP.md |
| Backend slow to start | It initializes on first request | Normal! |
| Button doesn't respond | Check browser console for errors | Dev tools F12 |
| CORS errors | Already handled in code | velinor_api.py |

##

## 🎓 Learning Resources

- **Next.js**: <https://nextjs.org/docs>
- **FastAPI**: <https://fastapi.tiangolo.com/>
- **Railway**: <https://docs.railway.app/>
- **React**: <https://react.dev/>

##

## 💡 Tips

1. **Start with local development** - Get it working on your machine first 2. **Use Swagger UI** -
Visit `http://localhost:8000/docs` to test API 3. **Browser DevTools** - F12 to check network
requests & errors 4. **Test on mobile** - The game should work on phones too 5. **Version control**

- Commit frequently so you can revert if needed

##

## 🎮 What's Next

After you get the basic setup working:

### Immediate

- Add more backgrounds to `public/assets/backgrounds/`
- Create overlay PNGs (dust, fog, glyphs)
- Flesh out game scenes

### Soon

- Add animations (Framer Motion)
- Add sound (Howler.js)
- Add glyph rendering
- Add stats panel

### Later

- Multiplayer support
- Save/load with database
- Settings menu
- Achievements system

##

## 📞 Documentation Map

```

VELINOR_WEB_COMPLETE.md  ← You are here (overview)
    ↓
VELINOR_WEB_MIGRATION.md  ← Follow this (6 phases)
    ↓
NEXTJS_FRONTEND_SETUP.md  ← Details here
RAILWAY_DEPLOYMENT.md     ← Deploy here
    ↓
Test locally → Deploy → Live!

```


##

## ✨ You're All Set

You have:

- ✅ FastAPI backend (`velinor_api.py`)
- ✅ React components (`frontend_*.tsx`)
- ✅ Complete documentation
- ✅ Deployment configured (Railway)

**Next step:** Open `VELINOR_WEB_COMPLETE.md` and start Phase 1!

##

**Questions?** Check the relevant documentation file or the game engine guide.

**Ready?** Let's build Velinor! 🎮
