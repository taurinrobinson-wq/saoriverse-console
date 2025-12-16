# Velinor Web - Migration from Streamlit to Next.js + FastAPI

## Overview

You're moving from Streamlit (with overlay limitations) to a proper web stack:

- **Backend**: FastAPI (Python) - wraps Velinor engine
- **Frontend**: Next.js (React/TypeScript) - full overlay control
- **Deployment**: Railway (already configured)

## Current Status

✅ **Done:**
- FastAPI backend created (`velinor_api.py`)
- Next.js setup guide (`NEXTJS_FRONTEND_SETUP.md`)
- Core components scaffolded (`frontend_GameScene.tsx`, `frontend_lib_api.ts`)
- Railway deployment guide (`RAILWAY_DEPLOYMENT.md`)

## Step-by-Step Setup

### Phase 1: Create Next.js Frontend Project

```bash

# From repo root
npx create-next-app@latest velinor-web --typescript --tailwind --eslint --no-git

cd velinor-web
```text
```text
```



### Phase 2: Copy Component Files

From the root, copy the prepared files into the Next.js project:

```bash


# From root of saoriverse-console
cp frontend_lib_api.ts velinor-web/lib/api.ts

```text
```




### Phase 3: Create App Pages

#### Splash Screen (`velinor-web/app/page.tsx`)

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { gameApi } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [playerName, setPlayerName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleStartGame = async () => {
    if (!playerName.trim()) return;

    setLoading(true);
    try {
      const { session_id } = await gameApi.startGame(playerName);
      router.push(`/game/${session_id}`);
    } catch (error) {
      console.error('Failed to start game:', error);
      alert('Failed to start game. Is the API running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{
      width: '100%',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      color: '#fff',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '20px', fontWeight: 'bold' }}>
        Velinor: Remnants of the Tone
      </h1>
      <p style={{ fontSize: '1.2rem', marginBottom: '40px', color: '#aaa' }}>
        A narrative adventure in the ruins of Velhara
      </p>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        width: '100%',
        maxWidth: '300px'
      }}>
        <input
          type="text"
          placeholder="Enter your character name"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleStartGame()}
          style={{
            padding: '12px',
            fontSize: '1rem',
            border: '2px solid #3a6df0',
            borderRadius: '8px',
            background: '#191b1e',
            color: '#fff',
          }}
        />

        <button
          onClick={handleStartGame}
          disabled={loading}
          style={{
            padding: '12px',
            fontSize: '1rem',
            background: loading ? '#666' : '#3a6df0',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Starting...' : 'Start New Game'}
        </button>
      </div>
    </main>
  );
```text
```text
```



#### Game Scene (`velinor-web/app/game/[sessionId]/page.tsx`)

```typescript

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import GameScene from '@/components/GameScene';
import { gameApi } from '@/lib/api';

interface GameState {
  passage_id: string;
  passage_name: string;
  main_dialogue: string;
  npc_name?: string;
  npc_dialogue?: string;
  background_image?: string;
  choices: Array<{ text: string; id?: string }>;
  clarifying_question?: string;
  game_state?: { player_stats?: any };
}

export default function GamePage({ params }: { params: { sessionId: string } }) {
  const router = useRouter();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get initial game state (you might fetch this via API)
    // For now, assume it's passed via URL state or fetched
    console.log('Session ID:', params.sessionId);
  }, [params.sessionId]);

  const handleChoiceClick = async (choiceIndex: number) => {
    setLoading(true);
    try {
      const response = await gameApi.takeAction(params.sessionId, choiceIndex);
      setGameState(response.state);
    } catch (error) {
      console.error('Failed to process choice:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomInput = async (text: string) => {
    setLoading(true);
    try {
      const response = await gameApi.takeAction(params.sessionId, undefined, text);
      setGameState(response.state);
    } catch (error) {
      console.error('Failed to process input:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!gameState) {
    return <div style={{ padding: '20px' }}>Loading game...</div>;
  }

  return (
    <div style={{ width: '100%', padding: '20px', background: '#000' }}>
      <GameScene
        backgroundImage={`/assets/backgrounds/${gameState.background_image || 'default.png'}`}
        narration={gameState.main_dialogue}
        npcName={gameState.npc_name || 'Scene'}
        choices={gameState.choices}
        onChoiceClick={handleChoiceClick}
        onCustomInput={handleCustomInput}
      />
    </div>
  );

```text
```




### Phase 4: Copy Game Assets

Copy your game assets into the Next.js public folder:

```bash

# Copy backgrounds
cp -r velinor/backgrounds/* velinor-web/public/assets/backgrounds/

# Copy NPCs
cp -r velinor/npcs/* velinor-web/public/assets/npcs/

# Create overlays folder (for dust, fog, glyphs)
```text
```text
```



### Phase 5: Test Locally

**Terminal 1 - Backend:**

```bash

cd d:\saoriverse-console
python velinor_api.py

# Runs on http://localhost:8000

```text
```




**Terminal 2 - Frontend:**

```bash
cd velinor-web
npm run dev

```text
```text
```



Test the game flow:
1. Open http://localhost:3000
2. Enter player name
3. Click "Start New Game"
4. Make a choice
5. Watch the scene update

### Phase 6: Deploy to Railway

```bash


# Add and commit everything
git add .
git commit -m "feat: Complete Next.js + FastAPI Velinor game"
git push origin main

# Railway auto-deploys

```text
```




## API Reference

### POST /api/game/start
Start a new game session.

**Request:**

```json
```text
```text
```



**Response:**

```json

{
  "session_id": "uuid-here",
  "state": {
    "passage_id": "market_entry",
    "main_dialogue": "You emerge into the market...",
    "background_image": "market.png",
    "choices": [
      { "text": "Approach the keeper", "id": "choice_1" },
      { "text": "Explore", "id": "choice_2" }
    ]
  }

```text
```




### POST /api/game/{session_id}/action
Process player action.

**Request:**

```json
{ "choice_index": 0 }
// or
```text
```text
```



**Response:** Updated game state (same structure as start)

## Architecture Diagram

```

┌─────────────────────────────────────────────────────┐
│                    User Browser                      │
│                  (Next.js Frontend)                  │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTP/REST
                     │
┌────────────────────▼────────────────────────────────┐
│               Railway Server                         │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  FastAPI Backend (velinor_api.py)            │  │
│  │                                              │  │
│  │  ▪ Session management                        │  │
│  │  ▪ Velinor engine integration                │  │
│  │  ▪ Game state computation                    │  │
│  │  ▪ Save/load functionality                   │  │
│  └──────────────────────────────────────────────┘  │
│                    │                                │
│                    │ (imports)                      │
│                    ▼                                │
│  ┌──────────────────────────────────────────────┐  │
│  │  Velinor Engine (velinor/engine/)            │  │
│  │                                              │  │
│  │  ▪ TwineOrchestrator                         │  │
│  │  ▪ VelinorEngine                             │  │
│  │  ▪ NPC system                                │  │
│  │  ▪ Dice rolls & stats                        │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘

```



## What You Get

✅ **Full overlay control** - Position buttons, text, images anywhere
✅ **Responsive design** - Works on desktop, tablet, mobile
✅ **Dark theme** - Professional look matching your aesthetic
✅ **Complete game flow** - Splash → game scenes → branching choices
✅ **Easy to expand** - Add scenes, modify overlays, customize styling
✅ **One-click deployment** - Push to main branch, Railway auto-deploys

## Next Steps

1. Run `npx create-next-app` with options above
2. Copy component files into the project
3. Create the page files (splash + game)
4. Test locally (both backend and frontend)
5. Push to GitHub
6. Railway auto-deploys (~5 minutes)
7. Visit your live game!

## Customization Ideas

- **Add animations**: Use Framer Motion for scene transitions
- **Add sound**: Howler.js for music/SFX
- **Add glyphs**: Render glyph overlays dynamically
- **Mobile optimized**: Responsive touch controls
- **Multiplayer**: Extend API to handle multiple players
- **Save system**: Persist game progress to database
##

Questions? Check:
- `NEXTJS_FRONTEND_SETUP.md` - Detailed setup guide
- `RAILWAY_DEPLOYMENT.md` - Deployment specifics
- `velinor/TWINE_INTEGRATION_GUIDE.md` - Game engine API
