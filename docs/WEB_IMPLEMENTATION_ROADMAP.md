# Velinor Web - Implementation Roadmap

This document outlines what you need to build to complete the web version.

## 📊 Current Progress

| Component | Status | Priority | Est. Time |
|-----------|--------|----------|-----------|
| Homepage | ✅ Done | - | - |
| Game Scene Layout | ⏳ Partial | 🔴 High | 1-2 hrs |
| Backend Connection | ⏳ Ready | 🔴 High | 1 hr |
| NPC Display | ❌ Not Started | 🟠 Medium | 1-2 hrs |
| Choices/Actions | ❌ Not Started | 🔴 High | 1-2 hrs |
| Stats Display | ❌ Not Started | 🟠 Medium | 30 min |
| Glyph System | ❌ Not Started | 🟡 Low | 2-3 hrs |
| Save/Load | ❌ Not Started | 🟡 Low | 1-2 hrs |
##

## 🎯 Task 1: Implement GameScene Component (HIGH PRIORITY)

**File**: `velinor-web/src/components/GameScene.tsx`
**Status**: Empty file, ready for implementation
**Estimated Time**: 1-2 hours

### What It Should Do
Display the current game state with:
1. **Background Image** - Story location visual
2. **Story Text** - Current passage text from backend
3. **NPC Section** - Portrait + dialogue
4. **Choices** - Interactive buttons
5. **Input Area** - Free text input option
6. **Stats Panel** - Player stats display

### Reference Implementation
See `velinor_app.py` (Streamlit version) for how these are laid out.

### Suggested Structure

```tsx
export function GameScene({
  sessionId: string,
  gameState: GameState // from backend
}) {
  return (
    <div className="w-full h-screen flex flex-col">
      {/* Background with NPC */}
      <div className="relative flex-1">
        <img src={backgroundImage} alt="Location" className="w-full h-full object-cover" />
        <img src={npcImage} alt="NPC" className="absolute right-20 bottom-0" />
      </div>

      {/* Story Text */}
      <div className="bg-white p-8 border-t">
        <p className="text-lg">{gameState.story_text}</p>
      </div>

      {/* Choices */}
      <div className="bg-gray-50 p-8 flex flex-col gap-2">
        {gameState.choices.map(choice => (
          <button onClick={() => handleChoice(choice)}>
            {choice.text}
          </button>
        ))}
      </div>
    </div>
  );
```sql
```sql
```



### Data You'll Receive From Backend

```typescript

{
  story_text: string,
  current_location: string,
  background_image: string,
  npc_info: {
    name: string,
    image: string,
    dialogue: string,
    trust_level: number
  },
  choices: Array<{
    id: string,
    text: string,
    conditional?: boolean
  }>,
  player_stats: {
    courage: number,
    wisdom: number,
    empathy: number,
    resolve: number,
    resonance: number
  },
  discovered_glyphs: string[]

```text
```



##

## 🎯 Task 2: Wire Up Backend Connection (HIGH PRIORITY)

**Files**: `velinor-web/src/hooks/useGame.ts` (NEW)
**Estimated Time**: 1 hour

### What You Need to Build

Create a custom React hook to manage game state and backend calls:

```typescript
// useGame.ts
import { useCallback, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export function useGame() {
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');

  const startGame = useCallback(async (playerName: string) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/sessions`, {
        player_name: playerName,
        player_backstory: 'Default backstory' // or get from user
      });
      setSessionId(response.data.session_id);
      setGameState(response.data.initial_state);
      return response.data;
    } catch (error) {
      console.error('Failed to start game:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const processChoice = useCallback(async (choiceId: string) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE}/sessions/${sessionId}/actions`,
        {
          player_input: choiceId,
          action_type: 'choice'
        }
      );
      setGameState(response.data.new_state);
      return response.data;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const processFreeInput = useCallback(async (input: string) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE}/sessions/${sessionId}/actions`,
        {
          player_input: input,
          action_type: 'free_text'
        }
      );
      setGameState(response.data.new_state);
      return response.data;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return {
    gameState,
    loading,
    sessionId,
    startGame,
    processChoice,
    processFreeInput
  };
```text
```text
```



### Wire It Into GameScene

```tsx

import { useGame } from '@/hooks/useGame';

export function GameScene() {
  const { gameState, processChoice, processFreeInput } = useGame();

  return (
    // Use gameState.story_text, gameState.choices, etc.
  );

```text
```



##

## 🎯 Task 3: Display Choices & Process Input (HIGH PRIORITY)

**File**: `velinor-web/src/components/GameScene.tsx`
**Estimated Time**: 1-2 hours

### Choices UI

```tsx
<div className="space-y-2">
  {gameState.choices.map(choice => (
    <button
      key={choice.id}
      onClick={() => processChoice(choice.id)}
      className="w-full bg-pink-500 hover:bg-pink-600 text-white p-4 rounded"
      disabled={loading}
    >
      {choice.text}
    </button>
  ))}
```text
```text
```



### Free Text Input

```tsx

const [input, setInput] = useState('');

<div className="flex gap-2">
  <input
    type="text"
    value={input}
    onChange={(e) => setInput(e.target.value)}
    onKeyPress={(e) => {
      if (e.key === 'Enter') {
        processFreeInput(input);
        setInput('');
      }
    }}
    placeholder="Or type your own action..."
    className="flex-1 p-4 border rounded"
  />
  <button
    onClick={() => {
      processFreeInput(input);
      setInput('');
    }}
    className="bg-blue-500 text-white px-6 rounded"
  >
    Send
  </button>

```text
```



##

## 🎯 Task 4: NPC Display (MEDIUM PRIORITY)

**File**: `velinor-web/src/components/GameScene.tsx`
**Estimated Time**: 1-2 hours

### Display NPC Info

```tsx
{gameState.npc_info && (
  <div className="flex items-end gap-4">
    {/* NPC Portrait */}
    <img
      src={`/assets/npcs/${gameState.npc_info.image}`}
      alt={gameState.npc_info.name}
      className="h-96 object-contain"
    />

    {/* Dialogue Box */}
    <div className="flex-1 bg-gradient-to-r from-purple-900 to-purple-800 p-6 rounded-lg">
      <h3 className="text-2xl font-bold text-white mb-2">
        {gameState.npc_info.name}
      </h3>
      <p className="text-purple-100">
        {gameState.npc_info.dialogue}
      </p>
      {/* Trust indicator */}
      <div className="mt-4 flex gap-1">
        {Array(5).fill(0).map((_, i) => (
          <div
            key={i}
            className={`h-2 flex-1 rounded ${
              i < gameState.npc_info.trust_level * 5
                ? 'bg-amber-400'
                : 'bg-gray-600'
            }`}
          />
        ))}
      </div>
    </div>
  </div>
```text
```text
```


##

## 🎯 Task 5: Stats Display (MEDIUM PRIORITY)

**File**: `velinor-web/src/components/StatsPanel.tsx` (NEW)
**Estimated Time**: 30 minutes

### Component Structure

```tsx

export function StatsPanel({ stats: PlayerStats }) {
  return (
    <div className="bg-slate-900 p-4 rounded space-y-3">
      <h3 className="text-lg font-bold text-white">Stats</h3>
      {Object.entries(stats).map(([name, value]) => (
        <div key={name}>
          <div className="flex justify-between text-sm text-white mb-1">
            <span className="capitalize">{name}</span>
            <span>{(value * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full"
              style={{ width: `${value * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );

```text
```




### Usage

```tsx
```text
```text
```


##

## 🎯 Task 6: Glyph System (LOW PRIORITY)

**File**: `velinor-web/src/components/GlyphCollection.tsx` (NEW)
**Estimated Time**: 2-3 hours

### What It Shows
- Grid of unlocked glyphs
- Emotional resonance for each
- Interactive glyph details
- "Glyph Journal" view

### Reference
See FirstPerson system output in backend responses - includes glyph data.
##

## 🎯 Task 7: Save/Load System (LOW PRIORITY)

**File**: `velinor-web/src/hooks/useGame.ts` (ADD METHODS)
**Estimated Time**: 1-2 hours

### Add to useGame Hook

```typescript

const saveGame = useCallback(async () => {
  return await axios.post(`${API_BASE}/sessions/${sessionId}/save`, {
    save_name: 'AutoSave'
  });
}, [sessionId]);

const loadGame = useCallback(async (saveId: string) => {
  const response = await axios.get(
    `${API_BASE}/sessions/${sessionId}/load?save_id=${saveId}`
  );
  setGameState(response.data);

```text
```



##

## 📦 Implementation Order

**Start with this order for fastest progress:**

1. **Week 1:**
   - [ ] Task 1: GameScene component layout
   - [ ] Task 2: Backend connection hook
   - [ ] Task 3: Choices & input processing

2. **Week 2:**
   - [ ] Task 4: NPC display
   - [ ] Task 5: Stats display
   - [ ] Polish UI styling

3. **Week 3:**
   - [ ] Task 6: Glyph system (if desired)
   - [ ] Task 7: Save/load (if desired)
   - [ ] Bug fixes & optimization
##

## 🔧 Files to Create/Modify

### New Files Needed

```
velinor-web/
├── src/
│   ├── hooks/
│   │   └── useGame.ts              ← CREATE
│   ├── components/
│   │   ├── GameScene.tsx           ← IMPLEMENT
│   │   ├── StatsPanel.tsx          ← CREATE
│   │   ├── GlyphCollection.tsx     ← CREATE (later)
│   │   └── SaveLoadDialog.tsx      ← CREATE (later)
│   ├── types/
│   │   └── game.ts                 ← CREATE (type definitions)
│   └── lib/
```text
```text
```



### Files to Modify

```

velinor-web/
├── src/
│   ├── app/
│   │   ├── game/
│   │   │   └── [sessionId]/
│   │   │       └── page.tsx        ← WIRE UP COMPONENTS
│   │   └── page.tsx                ← ADD FLOW TO GAME PAGE
│   └── styles/
│       └── globals.css             ← ADD CUSTOM STYLES

```


##

## 💡 Development Tips

1. **Start simple** - Get choices/input working first
2. **Test with curl** - Test backend endpoints with curl before frontend
3. **Use React DevTools** - Debug state and props
4. **Reference Streamlit** - The Streamlit version is your visual guide
5. **Commit often** - Push to git frequently
##

## 🆘 If You Get Stuck

1. **Backend issues**: Check `/velinor_api.py` and FastAPI docs at http://localhost:8000/docs
2. **Component issues**: Reference `/velinor_app.py` for UI logic
3. **Data structure**: Check `/velinor/engine/core.py` for state format
4. **Story data**: See `/velinor/stories/sample_story.json` for structure
##

## ✅ Definition of Done

When all tasks are complete, you should have:
- ✅ A playable Next.js web version
- ✅ Full feature parity with Streamlit version
- ✅ Connected to Python backend
- ✅ FirstPerson emotional analysis integrated
- ✅ All graphics displayed
- ✅ Choices and free-text input working
- ✅ Stats and progress tracking visible
- ✅ Glyph system visible (optional)
- ✅ Save/load functionality (optional)

**Total Estimated Work**: 8-12 hours for core features
**With polish & extras**: 15-20 hours
##

Ready to start? Open `velinor-web/src/components/GameScene.tsx` and begin! 🚀
