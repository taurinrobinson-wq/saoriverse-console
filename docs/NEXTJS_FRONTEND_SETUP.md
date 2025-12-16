# Velinor Frontend Setup Guide

## Quick Start

### 1. Create Next.js App

```bash

# In the root of your repo or new folder
npx create-next-app@latest velinor-web --typescript --tailwind --eslint
```text
```text
```

### 2. Install Dependencies

```bash

```text
```

- **axios** - HTTP client for API calls
- **zustand** - State management (lightweight alternative to Redux)

### 3. Environment Setup

Create `.env.local`:

```
```text
```text
```

For production (Railway):

```

```text
```

### 4. Project Structure

```
velinor-web/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home/splash screen
│   ├── game/
│   │   └── [sessionId]/
│   │       └── page.tsx        # Game scene
│   └── api/                    # Optional: local API routes
├── components/
│   ├── GameScene.tsx           # Scene renderer with overlays
│   ├── ChoiceButtons.tsx       # Interactive choice buttons
│   ├── Narration.tsx           # Dialogue/text display
│   └── SplashScreen.tsx        # Welcome screen
├── lib/
│   ├── api.ts                  # API client
│   ├── types.ts                # TypeScript interfaces
│   └── store.ts                # Zustand store
├── public/
│   └── assets/
│       ├── backgrounds/        # Scene backgrounds
│       ├── overlays/           # Dust, fog, glyphs
│       └── npcs/               # Character images
└── styles/
```text
```text
```

### 5. Key Files to Create

See the companion files:

- `app.tsx` - Root component
- `GameScene.tsx` - Main game UI with overlays
- `api.ts` - API client hooks
- `store.ts` - Game state management

### 6. Run Locally

```bash


# Terminal 1: Start FastAPI backend
cd /path/to/saoriverse-console
pip install fastapi uvicorn
python velinor_api.py

# Opens on http://localhost:8000

# Terminal 2: Start Next.js frontend
cd velinor-web
npm run dev

```text
```

### 7. Deployment to Railway

See `RAILWAY_DEPLOYMENT.md` for full setup.

TL;DR:

```bash

# Already have Procfile and railway.json
git add .
git commit -m "feat: Add Next.js frontend for Velinor"
git push origin main

```text
```text
```

## API Contract

### Start Game

```

POST /api/game/start
{
  "player_name": "Traveler"
}
→ {
  "session_id": "uuid",
  "state": { ...game state... }

```text
```

### Take Action

```
POST /api/game/{session_id}/action
{
  "choice_index": 0
  // or
  "player_input": "I approach cautiously"
}
```text
```text
```

### Game State Structure

```typescript

{
  passage_id: string           // Current passage ID
  passage_name: string         // Human-readable name
  main_dialogue: string        // Narration text
  npc_name?: string            // NPC speaking
  npc_dialogue?: string        // NPC dialogue
  background_image?: string    // Background image filename
  choices: Array<{
    text: string              // Choice label
    target?: string           // Next passage
  }>
  clarifying_question?: string
  game_state: {
    player_stats: { ... }
  }

```text
```

## Frontend Architecture

### Layers

1. **Background** - Full-width scene image
2. **Overlays** - Dust, fog, glyphs (semi-transparent PNGs)
3. **Narration Box** - Text overlay at top
4. **Choice Buttons** - Interactive buttons (absolute positioned)
5. **UI Controls** - Stats, menu buttons (bottom/sidebar)

### Positioning Example

```jsx
<div style={{ position: 'relative', width: '100%', paddingBottom: '56.25%' }}>
  {/* 16:9 aspect ratio container */}
  <img src="/backgrounds/market.png" style={{
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }} />

  {/* Overlays */}
  <img src="/overlays/dust.png" style={{
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    opacity: 0.3
  }} />

  {/* Text */}
  <div style={{
    position: 'absolute',
    top: '20px',
    left: '20px',
    right: '20px',
    background: 'rgba(0,0,0,0.7)',
    padding: '16px',
    color: '#fff',
    borderRadius: '8px'
  }}>
    {narration}
  </div>

  {/* Buttons */}
  <button style={{
    position: 'absolute',
    bottom: '20px',
    left: '50%',
    transform: 'translateX(-50%)',
    padding: '12px 24px',
    background: '#3a6df0',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer'
  }}>
    Choice
  </button>
</div>
```

## Customization

### Change Colors/Fonts

Edit `styles/globals.css` and component styles.

### Add New Overlays

1. Create PNG with transparency
2. Place in `public/assets/overlays/`
3. Reference in scene JSON: `"overlay": "dust.png"`

### Adjust Button Positions

Modify `ChoiceButtons.tsx` - use `style={{ bottom: '...', left: '...' }}` to position.

### Add Sound/Music

Use HTML5 `<audio>` or `Howler.js` library.

##

**Next Steps:**

1. Run `npm install` and `npm run dev`
2. See `GameScene.tsx` for rendering logic
3. Modify `styles/globals.css` for theme
4. Test API calls via `http://localhost:3000`
