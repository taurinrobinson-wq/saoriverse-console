# Velinor Web Stack - Quick Test Instructions

## You're All Set! 🎉

The complete Velinor web stack (FastAPI + Next.js) is ready to test. No more Streamlit limitations!

### What You Have

- **Backend**: `velinor_api.py` - FastAPI REST API wrapping the Velinor game engine
- **Frontend**: `velinor-web/` - Next.js React app with splash screen and game scene
- **Full Button Overlays**: Absolute positioned buttons on background images (Streamlit couldn't do this)
- **Responsive Design**: 16:9 aspect ratio, Tailwind CSS styling
- **Local Testing**: Ready to run on localhost

##

## How to Test (3 Simple Steps)

### Step 1: Open Terminal 1 (Backend)

```bash
cd d:\saoriverse-console
```text

```text
```


You should see:

```

```text

```

✅ Backend is live at `http://localhost:8000`

### Step 2: Open Terminal 2 (Frontend)

```bash

cd d:\saoriverse-console\velinor-web

```text
```text

```

You should see:

```


▲ Next.js 14.0.0

```text
```


✅ Frontend is live at `http://localhost:3000`

### Step 3: Open Browser

Go to: **`http://localhost:3000`**

You should see:

1. **Splash Screen** - Dark theme with "Velinor" title 2. **Input Field** - "Enter your name" 3.
**"Start New Game" Button** - Blue button

Enter a name and click the button. The game scene should load!

##

## What's Happening Behind the Scenes

```
User clicks "Start New Game"
    ↓
Frontend calls: POST /api/game/start with player name
    ↓
Backend creates a session and VelinorTwineOrchestrator
    ↓
Returns session_id + initial game state
    ↓
Frontend navigates to /game/{session_id}
    ↓
Frontend calls: GET /api/game/{session_id}
    ↓
Game scene renders with:
   • Background image (absolute positioned)
   • Narration box (top-left overlay)
   • NPC name/dialogue (if any)
   • Choice buttons (absolutely positioned at bottom)
   • Custom text input field
    ↓
User clicks a choice
    ↓
Frontend calls: POST /api/game/{session_id}/action with choice_index
    ↓
Backend processes through Velinor engine
    ↓
Returns new game state
    ↓
```text

```text
```


##

## Key Differences from Streamlit

| Aspect | Streamlit | Next.js Web Stack |
|--------|-----------|---|
| **Button Positioning** | ❌ Can't overlay on images | ✅ Absolute positioning works |
| **Z-index** | ❌ Not possible | ✅ Full control |
| **Animations** | ❌ Limited | ✅ Smooth hover effects |
| **Layout Control** | ❌ Columns & expanders only | ✅ Custom CSS/Tailwind |
| **Visual Design** | ⚠️ Constrained | ✅ Full creative control |

##

## Troubleshooting

### "Failed to start game. Is the API running?"

- Make sure Terminal 1 (backend) is still running
- Check it shows `INFO: Uvicorn running on http://127.0.0.1:8000`
- If it crashed, check the error message and scroll up

### "Cannot GET /game/[sessionId]"

- The page exists but the game state isn't loading
- Check Terminal 1 - is the API returning an error?
- Open your browser's Developer Tools (F12) and check Console tab

### "Loading game... (Did you start a game first?)"

- This message appears while the page is loading state
- If it stays forever, the API call is failing
- Check browser Console (F12) for error details

### Clear & Fresh Start

```bash


## Terminal 1
Ctrl+C  (stop backend)
python velinor_api.py

## Terminal 2
Ctrl+C  (stop frontend)
npm run dev

## Browser

```text

```

##

## What's Next?

### To Deploy to Production

Once the local test works:

```bash

cd d:\saoriverse-console

## Commit the web stack
git add . git commit -m "Add Velinor web stack (FastAPI + Next.js)" git push origin main

## Railway auto-deploys!

```text
```text

```

### To Add Game Assets

Copy your game images to:

- `velinor-web/public/assets/backgrounds/` - Background images
- `velinor-web/public/assets/overlays/` - Overlay PNGs
- `velinor-web/public/assets/npcs/` - NPC character images

The `<GameScene>` component references them as:

```typescript


<GameScene backgroundImage="/assets/backgrounds/market.png" // ...

```text
```


### To Improve Styling

All inline styles currently show linting warnings. To fix:

- Create `velinor-web/app/globals.css` (or component CSS modules)
- Move inline `style={{}}` props to classes
- This is optional—code works fine as-is, but best practices suggest external CSS

##

## Files You Now Have

```
d:\saoriverse-console\
├── velinor_api.py                          ← Backend (run this first)
├── RUN_VELINOR_WEB.md                      ← Detailed run guide
├── VELINOR_WEB_SETUP_COMPLETE.md           ← Full setup summary
├── velinor-web/                            ← Next.js project
│   ├── app/
│   │   ├── page.tsx                        ← Splash screen
│   │   └── game/[sessionId]/page.tsx       ← Game scene page
│   ├── components/
│   │   └── GameScene.tsx                   ← Game rendering component
│   ├── lib/
│   │   └── api.ts                          ← API client
│   ├── public/
│   │   └── assets/                         ← Your game images go here
│   ├── .env.local                          ← API URL config
│   ├── package.json                        ← Dependencies (installed)
│   └── ...other Next.js config
└── [other game files]
```


##

## You're Ready! 🚀

Everything is set up and ready to go.

Just run the 3 steps above and you'll have a fully functional Velinor web game with proper overlay
controls, no Streamlit limitations!

Questions? Check `RUN_VELINOR_WEB.md` for more detailed instructions.
