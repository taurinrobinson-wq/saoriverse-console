# VELINOR_WEB_MASTER_DOC.md

**Authoritative Source for Web Frontend Architecture, UI/UX, and API Integration**

**Last Updated:** January 20, 2026  
**Status:** Canonical reference for velinor-web frontend  
**Scope:** Next.js application, React components, state management, API integration, deployment

> **Note:** This document defines how the web frontend **renders and interacts with** the Velinor game world.  
> For the **game logic itself**, see `../velinor/VELINOR_MASTER_DOC.md`  
> For the **contract between systems**, see `VELINOR_INTEGRATION_CONTRACT.md` (shared in both repos)

---

## Quick Navigation

- [What is Velinor-Web?](#what-is-velinor-web) — Frontend purpose and architecture
- [How It Connects to Velinor](#how-it-connects-to-velinor) — API integration overview
- [Page & Route Structure](#page--route-structure) — Pages and user flows
- [Component Architecture](#component-architecture) — Component hierarchy and organization
- [State Management](#state-management) — Zustand stores and data flow
- [Rendering Game Systems](#rendering-game-systems) — How UI displays glyphs, NPCs, dialogue
- [Styling & Visual Design](#styling--visual-design) — CSS, theming, layout
- [File Reference](#file-reference) — File organization and purposes
- [Common Frontend Tasks](#common-frontend-tasks) — Quick recipes for modifications
- [Development & Deployment](#development--deployment) — Setup, build, deploy

---

## What is Velinor-Web?

### Purpose

**Velinor-Web** is a Next.js/React frontend that:

1. **Presents** the Velinor game world in an interactive web interface
2. **Communicates** with the Velinor backend API
3. **Manages** UI state and user interactions
4. **Renders** game content: NPCs, dialogue, choices, glyphs, stats
5. **Persists** game sessions via browser state and backend save system

### Architecture

```
User Browser (React Components)
         ↓
  Zustand Store (State)
         ↓
  GameApiClient (TypeScript wrapper)
         ↓
  Velinor Backend API (FastAPI)
         ↓
  Velinor Game Engine (Core logic)
```

**Key Principle:** UI is **view layer** only. Game logic lives in Velinor backend.

---

## How It Connects to Velinor

### API Client Architecture

**File:** `src/lib/api.ts` — TypeScript wrapper around REST API

```typescript
export class GameApiClient {
  constructor(baseUrl: string)
  
  async startGame(playerName: string): Promise<GameResponse>
  async takeAction(sessionId: string, actionId: string): Promise<GameResponse>
  async getGameStatus(sessionId: string): Promise<GameStatus>
  async saveGame(sessionId: string, slot: number): Promise<SaveResponse>
  async loadGame(sessionId: string, slot: number): Promise<GameResponse>
  async debugEndpoint(sessionId: string): Promise<DebugInfo>
}
```

**Configuration:** `src/config/constants.ts`
```typescript
export const VELINOR_API_BASE_URL = process.env.NEXT_PUBLIC_VELINOR_API_BASE_URL 
  || 'http://localhost:8000/api'
```

### Request/Response Flow

**For detailed API contract, see:** `VELINOR_INTEGRATION_CONTRACT.md`

**Quick Overview:**

```
1. User clicks "Play"
   ↓
2. React calls: GameApiClient.startGame(playerName)
   ↓
3. API sends: POST /api/game/start { "player_name": "Alice" }
   ↓
4. Backend responds: { "session_id": "...", "current_passage": "...", ... }
   ↓
5. Store updates: gameStore.setGameState(response)
   ↓
6. Components re-render with new game state
```

### Endpoint Reference

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/api/game/start` | Initialize game | playerName | GameState + sessionId |
| POST | `/api/game/action` | Process choice | sessionId, actionId | Updated GameState |
| GET | `/api/game/status` | Get current state | sessionId | GameState |
| POST | `/api/game/save` | Save to slot | sessionId, slot | SaveConfirm |
| GET | `/api/game/load` | Load from slot | sessionId, slot | GameState |

**Full contract:** See `VELINOR_INTEGRATION_CONTRACT.md`

---

## Page & Route Structure

### Pages (Next.js App Router)

**File Organization:**
```
src/app/
├── page.tsx              ← Title screen (/)
├── game/
│   └── [sessionId]/
│       └── page.tsx      ← Game play (/game/session-123)
├── test/
│   └── page.tsx          ← Dev tools (/test)
├── layout.tsx            ← Root layout wrapper
└── globals.css           ← Global styles
```

### Page 1: Title Screen (`src/app/page.tsx`)

**Purpose:** Game intro and start interface

**User Flow:**
```
1. See Velinor title and intro text
2. Enter player name
3. Click "Play"
4. Navigate to /game/session-id
```

**Components Used:**
- `<TitleScreen>` — Title screen layout
- `<Input>` — Player name field
- `<Button>` — Play button

**State Flow:**
```typescript
const handlePlay = async (playerName: string) => {
  const gameState = await GameApiClient.startGame(playerName)
  gameStore.setGameState(gameState)
  router.push(`/game/${gameState.session_id}`)
}
```

**Files to Modify:**
- `src/app/page.tsx` — Title layout, intro text, styling
- `src/components/TitleScreen.tsx` — Extracted title component (if exists)
- `src/app/globals.css` — Title styling

**Common Changes:**
- Change title text: Edit page.tsx
- Adjust intro message: Edit TitleScreen component
- Styling changes: Edit globals.css or dedicated CSS module

### Page 2: Game Play (`src/app/game/[sessionId]/page.tsx`)

**Purpose:** Main interactive game interface

**Layout:**
```
┌────────────────────────────────┐
│  NPC Portrait  │  Game Status   │
├────────────────────────────────┤
│      Dialogue/Story Text       │
│      (Player reads story)       │
├────────────────────────────────┤
│   [Choice 1] [Choice 2] [...]  │
├────────────────────────────────┤
│  Save  │  Load  │  Status      │
└────────────────────────────────┘
```

**Components Used:**
- `<GameScene>` — Main orchestrator
- `<NpcPortrait>` — NPC image display
- `<DialogueBox>` — Story text
- `<ChoiceButtons>` — Player choices
- `<StatusHud>` — TONE stats, coherence
- `<SaveLoadModal>` — Persistence UI

**State Flow:**
```typescript
// On mount: load game state from sessionId
const gameState = gameStore.getState()

// On choice click: send action to backend
const handleChoice = async (choiceId: string) => {
  const updatedState = await GameApiClient.takeAction(sessionId, choiceId)
  gameStore.setGameState(updatedState)
  // Components auto-re-render with new dialogue, choices, etc.
}
```

**Files to Modify:**
- `src/app/game/[sessionId]/page.tsx` — Main page layout
- `src/components/GameScene.tsx` — Scene orchestration
- `src/components/DialogueBox.tsx` — Dialogue display logic
- `src/components/ChoiceButtons.tsx` — Choice button rendering

**Common Changes:**
- Change layout spacing: Edit CSS in .module.css files
- Add HUD element: Create component, import in GameScene
- Modify dialogue display: Edit DialogueBox component
- Change choice styling: Edit ChoiceButtons component

### Page 3: Dev Tools (`src/app/test/page.tsx`)

**Purpose:** Development and testing

**Features:**
- Quick game start (skip title screen)
- Debug state viewer
- API response inspector
- Test scenario buttons

**Files to Modify:**
- `src/app/test/page.tsx` — Test page layout
- `src/components/DevTools.tsx` — Dev tools component (if extracted)

---

## Component Architecture

### Component Tree

```
<RootLayout>
  ├── <Header />
  ├── <MainContent>
  │   ├── Page 1: <TitleScreen />
  │   │   ├── <Input />
  │   │   └── <Button />
  │   │
  │   └── Page 2: <GameScene />
  │       ├── <NpcPortrait />
  │       ├── <DialogueBox />
  │       ├── <ChoiceButtons />
  │       │   └── <Button /> × N
  │       ├── <StatusHud />
  │       │   ├── <ToneStat />
  │       │   ├── <CoherenceBar />
  │       │   └── <InfluenceGauge />
  │       └── <SaveLoadModal />
  │           ├── <SaveSlot />
  │           └── <LoadSlot />
  └── <Footer />
```

### Core Components

#### `<GameScene>` — Main Game Container
- **File:** `src/components/GameScene.tsx`
- **Purpose:** Orchestrates all game UI and state
- **Props:** `sessionId: string`, `gameState: GameState` (from store)
- **Renders:**
  - NPC portrait
  - Current dialogue/passage
  - Player choices
  - HUD (stats, status)
  - Save/load buttons
- **State:** Connected to gameStore via `useGameStore()`
- **Handles:**
  - Choice selection → `takeAction()`
  - Save/load triggers
  - Modal display

**Modifications:**
- Add UI panel: Add component import and JSX
- Change layout: Modify CSS grid/flex layout
- Add interaction: Add event handler and store action

#### `<DialogueBox>` — Story Text Display
- **File:** `src/components/DialogueBox.tsx`
- **Purpose:** Display current story passage/dialogue
- **Props:** `text: string`, `npcName?: string`, `isDialogue: boolean`
- **Renders:**
  - Story text with formatting
  - Speaker name (if NPC dialogue)
  - Glyph indicators (visual cues)
- **Features:**
  - Text wrapping
  - Emotional tone indicators
  - Glyph highlighting

**Modifications:**
- Change text styling: Edit CSS module
- Add formatting: Add text parsing logic
- Add glyph icons: Import icons, render near glyphs

#### `<ChoiceButtons>` — Player Choices
- **File:** `src/components/ChoiceButtons.tsx`
- **Purpose:** Display and handle player choice selection
- **Props:** `choices: Choice[]`, `onChoose: (choiceId) => void`
- **Renders:** Choice buttons with text
- **Features:**
  - Button states (normal, hover, disabled)
  - Keyboard shortcuts (1-5, arrow keys)
  - Disabled gates (show why choice is locked)

**Modifications:**
- Change button layout: Modify CSS (horizontal vs vertical, grid)
- Add keyboard shortcuts: Add `useEffect` with keydown listener
- Show gate info: Add conditional rendering for locked reasons

#### `<NpcPortrait>` — NPC Image
- **File:** `src/components/NpcPortrait.tsx`
- **Purpose:** Display NPC character image
- **Props:** `npcName: string`, `emotion?: string`
- **Renders:** NPC PNG image with optional effects
- **Source:** `public/assets/npcs/{npcName}.png`
- **Features:**
  - Fade transitions between NPCs
  - Emotional expression variants (optional)
  - Frame/border styling

**Modifications:**
- Change image source: Edit image path construction
- Add effects: Add CSS filters or animations
- Change size: Edit CSS width/height

#### `<StatusHud>` — Player Stats Display
- **File:** `src/components/StatusHud.tsx`
- **Purpose:** Show TONE stats, coherence, influence
- **Props:** `playerState: PlayerState`
- **Renders:**
  - 4 TONE bars (Empathy, Skepticism, Integration, Awareness)
  - Coherence percentage
  - Current NPC influence level

**Modifications:**
- Add stat: Add new bar component and CSS
- Change display: Modify layout (horizontal vs vertical bars)
- Add animation: Add transition effects on stat changes

#### `<SaveLoadModal>` — Persistence UI
- **File:** `src/components/SaveLoadModal.tsx`
- **Purpose:** Save game to slot or load from slot
- **Props:** `sessionId: string`, `onSaved: () => void`
- **Renders:**
  - 10 save slots with previews
  - Timestamp of last save
  - Save/load buttons

**Modifications:**
- Change slot count: Edit constant, adjust grid
- Add more info: Edit slot preview display
- Change styling: Edit modal CSS

### Common Component Tasks

**Add a new UI component:**
1. Create file: `src/components/MyComponent.tsx`
2. Define props interface and return JSX
3. Import in parent (e.g., GameScene.tsx)
4. Add to JSX with props
5. Create CSS module: `src/components/MyComponent.module.css`
6. Style the component

**Connect component to game state:**
```typescript
import { useGameStore } from '@/store/gameStore'

export function MyComponent() {
  const { empathy, coherence, takeAction } = useGameStore()
  
  return (
    <div>
      Empathy: {empathy}
      <button onClick={() => takeAction('choice-id')}>
        Make Choice
      </button>
    </div>
  )
}
```

**Update component on store change:**
- Automatic via React hooks
- Zustand triggers re-render when subscribed state changes
- No manual subscription needed

---

## State Management

### Zustand Store (`src/store/gameStore.ts`)

**Purpose:** Centralized game state management

**Store Interface:**
```typescript
interface GameState {
  // Session
  sessionId: string | null
  playerName: string
  
  // Game Content
  currentPassage: string
  currentNpc: string | null
  dialogueText: string
  choices: Choice[]
  
  // Player Stats (TONE)
  empathy: number
  skepticism: number
  integration: number
  awareness: number
  
  // Game Progress
  coherence: number
  influenceMap: Record<string, number>  // { npcName: 0-1 }
  activeGlyphs: Glyph[]
  collectedGlyphs: string[]
  
  // Persistence
  saveSlots: SaveSlot[]
  loadingState: 'idle' | 'loading' | 'error'
  errorMessage: string | null
  
  // Actions
  startNewGame: (playerName: string) => Promise<void>
  takeAction: (choiceId: string) => Promise<void>
  updateGameState: (state: Partial<GameState>) => void
  saveGame: (slot: number) => Promise<void>
  loadGame: (slot: number) => Promise<void>
}
```

### Using the Store

**In any component:**
```typescript
import { useGameStore } from '@/store/gameStore'

export function MyComponent() {
  // Read state
  const { empathy, coherence, sessionId } = useGameStore()
  
  // Call action
  const { takeAction } = useGameStore()
  
  const handleChoice = async () => {
    await takeAction('choice-123')
    // Store updates automatically
    // Component re-renders
  }
  
  return (
    <div>
      Empathy: {empathy}
      <button onClick={handleChoice}>
        Choose
      </button>
    </div>
  )
}
```

### Data Flow on Player Choice

```
1. Player clicks choice button
   ↓
2. Component calls: takeAction(choiceId)
   ↓
3. Store action:
   a) Set loadingState = 'loading'
   b) Call GameApiClient.takeAction(sessionId, choiceId)
   c) Receive updated GameState from backend
   ↓
4. Store updates:
   updateGameState({
     currentPassage: newPassage,
     choices: newChoices,
     empathy: newEmpathy,
     ...
   })
   ↓
5. Zustand subscribers notified
   ↓
6. Connected components re-render with new state
   ↓
7. UI shows new passage, choices, updated stats
```

### Adding Store State

**To add a new field:**

1. Add to `GameState` interface
2. Add to initial state in store
3. Use in components: `const { myField } = useGameStore()`
4. Update in actions: `updateGameState({ myField: newValue })`

**Example:**
```typescript
// In gameStore.ts
interface GameState {
  // ... existing fields
  currentPhase: number  // NEW
}

const useGameStore = create<GameState>((set) => ({
  // ... existing initial state
  currentPhase: 1,  // NEW
  
  // ... existing actions
  updateGameState: (partial) => set(partial),
}))

// In component
const { currentPhase } = useGameStore()
```

---

## Rendering Game Systems

### How Glyphs Appear in UI

**Source of Truth:** Backend `glyphs_complete.json` defines all glyph data

**Frontend Rendering:**

1. **Tier 1 (Hint)** — Shown in dialogue while playing
   ```
   Text: "I have something I want to tell you... ◈"
   Color: Soft blue (from Tier 1 data)
   Player sees: Visual symbol + emotional tone
   ```

2. **Tier 2 (Context)** — Revealed through interaction
   ```
   Player reads passage: "The glyph stands for... Presence"
   Glyph unlocks in UI
   ```

3. **Tier 3 (Plaintext)** — Revealed in ending
   ```
   In ending passage: Full meaning displayed
   "That symbol meant: 'The promise of companionship held true'"
   ```

**Files:**
- `src/components/GlyphDisplay.tsx` — Render glyph with styling
- `src/components/DialogueBox.tsx` — Integrate glyphs into dialogue text
- `src/data/glyphs.json` — Synced from `velinor/data/glyphs_complete.json`

### How NPCs Are Displayed

**Component:** `<NpcPortrait />`

**Image Source:** `public/assets/npcs/{npcName}.png`
- Synced from `velinor/npcs/` via parallel folder sync
- PNG portraits for each of 21 NPCs

**Display Logic:**
```typescript
<NpcPortrait npcName={currentNpc} emotion="speaking" />
```

**Features:**
- Fade transition when NPC changes
- Emotion variants (if multiple emotions per NPC)
- Frame/border styling
- Responsive sizing

### How Dialogue Displays

**Component:** `<DialogueBox />`

**Content from Backend:**
```json
{
  "currentPassage": "...",
  "currentNpc": "SaoriName",
  "dialogueText": "I have something...",
  "choices": [
    { "id": "choice-1", "text": "Tell me everything" },
    { "id": "choice-2", "text": "I'm not ready" }
  ]
}
```

**Rendering:**
```
If NPC dialogue:
  [NPC Name]
  Dialogue text with glyphs

If narration:
  Story text (no speaker)

Below: Player choices as buttons
```

### How Stats Display

**Component:** `<StatusHud />`

**Data from Store:**
```typescript
const { empathy, skepticism, integration, awareness, coherence } = useGameStore()
```

**Rendering:**
```
TONE Stats:
  Empathy:      ████░░░░ 65/100
  Skepticism:   ██████░░ 75/100
  Integration:  ███░░░░░ 42/100
  Awareness:    █████░░░ 58/100

Coherence: 54%
NPC Trust: Saori 0.72
```

---

## Styling & Visual Design

### Global Styles

**File:** `src/app/globals.css`

**CSS Variables (Theme):**
```css
:root {
  /* Colors */
  --color-primary: #2c3e50;
  --color-secondary: #3498db;
  --color-background: #1a1a1a;
  --color-text: #ecf0f1;
  --color-accent: #e74c3c;
  
  /* Velinor aesthetic */
  --color-glyph-tier1: #9b59b6;
  --color-glyph-tier2: #3498db;
  --color-glyph-tier3: #2ecc71;
  --color-npc-frame: #34495e;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  --spacing-xl: 4rem;
  
  /* Typography */
  --font-family-serif: Georgia, serif;
  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-body: 1rem;
  --font-size-heading: 2rem;
}
```

### Component-Specific Styles

**Pattern:** Create `.module.css` file next to component

**File:** `src/components/DialogueBox.module.css`
```css
.dialogueBox {
  font-family: var(--font-family-serif);
  color: var(--color-text);
  padding: var(--spacing-lg);
  background: rgba(0, 0, 0, 0.3);
  border-left: 3px solid var(--color-accent);
  border-radius: 4px;
  line-height: 1.6;
}

.npcName {
  font-weight: bold;
  color: var(--color-secondary);
  margin-bottom: var(--spacing-sm);
}
```

**Usage in component:**
```typescript
import styles from './DialogueBox.module.css'

export function DialogueBox({ text, npcName }) {
  return (
    <div className={styles.dialogueBox}>
      {npcName && <div className={styles.npcName}>{npcName}</div>}
      <p>{text}</p>
    </div>
  )
}
```

### Tailwind CSS (Alternative)

**Config:** `tailwind.config.ts`

**Usage:**
```tsx
<div className="flex flex-col gap-4 p-6 bg-slate-900 text-white rounded">
  <h1 className="text-2xl font-bold text-purple-400">Title</h1>
  <p>Content</p>
</div>
```

### Common Styling Tasks

**Change color scheme:**
1. Edit CSS variables in `globals.css`
2. All components using vars auto-update

**Adjust layout spacing:**
1. Edit `--spacing-*` variables
2. Or update component padding/margin

**Add animation:**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.element {
  animation: fadeIn 0.5s ease-in;
}
```

---

## File Reference

### Project Structure

```
velinor-web/
├── src/
│   ├── app/                      ← Next.js App Router pages
│   │   ├── page.tsx              ← Title screen
│   │   ├── game/[sessionId]/
│   │   │   └── page.tsx          ← Game play
│   │   ├── test/page.tsx         ← Dev tools
│   │   ├── layout.tsx            ← Root layout
│   │   └── globals.css           ← Global styles + theme
│   ├── components/               ← React components
│   │   ├── GameScene.tsx         ← Main orchestrator
│   │   ├── DialogueBox.tsx       ← Story text
│   │   ├── ChoiceButtons.tsx     ← Choices
│   │   ├── NpcPortrait.tsx       ← NPC image
│   │   ├── StatusHud.tsx         ← Stats display
│   │   ├── SaveLoadModal.tsx     ← Persistence
│   │   ├── TitleScreen.tsx       ← Title screen
│   │   └── common/
│   │       ├── Button.tsx        ← Button component
│   │       ├── Modal.tsx         ← Modal wrapper
│   │       └── ...
│   ├── lib/                      ← Utilities
│   │   └── api.ts               ← GameApiClient
│   ├── store/                    ← Zustand stores
│   │   └── gameStore.ts         ← Game state
│   ├── config/                   ← Configuration
│   │   └── constants.ts         ← API URL, timeouts
│   ├── data/                     ← Synced from Velinor
│   │   ├── npc_profiles.json
│   │   ├── glyphs.json
│   │   └── ...
│   ├── types/                    ← TypeScript types
│   │   ├── game.ts
│   │   └── api.ts
│   └── styles/                   ← Shared styles
│       └── variables.css
├── public/                       ← Static assets (synced)
│   └── assets/
│       ├── npcs/                ← NPC portraits
│       ├── backgrounds/         ← Game scenes
│       ├── overlays/            ← Effects
│       └── ...
├── __tests__/                    ← Unit & integration tests
│   ├── components/
│   ├── lib/
│   └── store/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── ...
```

### Key Files

| File | Purpose | Modify for |
|------|---------|-----------|
| `src/app/page.tsx` | Title screen page | Title text, layout, styling |
| `src/app/game/[sessionId]/page.tsx` | Game play page | Game layout, HUD placement |
| `src/lib/api.ts` | API client wrapper | API endpoint changes |
| `src/config/constants.ts` | Configuration | API URL, timeouts |
| `src/store/gameStore.ts` | Zustand store | State structure, actions |
| `src/components/GameScene.tsx` | Main orchestrator | UI orchestration |
| `src/components/DialogueBox.tsx` | Dialogue display | Dialogue rendering |
| `src/components/ChoiceButtons.tsx` | Choices | Choice rendering, interaction |
| `src/components/NpcPortrait.tsx` | NPC image | Portrait display |
| `src/components/StatusHud.tsx` | Stats | TONE/coherence display |
| `src/app/globals.css` | Global styles | Theme, colors, spacing |

---

## Common Frontend Tasks

### "I want to change the title screen"

1. **Edit** `src/app/page.tsx`
   - Change heading text
   - Modify intro message
   - Adjust layout

2. **Edit styling** `src/app/globals.css` or create `src/app/page.module.css`
   - Change colors
   - Adjust spacing
   - Add effects

### "I want to add a new stat to the HUD"

1. **Update store** `src/store/gameStore.ts`
   - Add field to `GameState` interface
   - Add to initial state

2. **Update component** `src/components/StatusHud.tsx`
   - Add new stat bar rendering
   - Get field from store: `const { newStat } = useGameStore()`
   - Add CSS styling

### "I want to display NPC emotions/expressions"

1. **Add multiple portraits** to `public/assets/npcs/`
   - `saori.png` (neutral)
   - `saori_sad.png` (sad)
   - `saori_hopeful.png` (hopeful)

2. **Modify** `src/components/NpcPortrait.tsx`
   ```typescript
   const emotionFile = `${npcName}${emotion ? `_${emotion}` : ''}.png`
   ```

3. **Pass emotion from store:**
   ```typescript
   <NpcPortrait npcName={currentNpc} emotion={currentEmotion} />
   ```

### "I want to add keyboard shortcuts for choices"

1. **Edit** `src/components/ChoiceButtons.tsx`

```typescript
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    const num = parseInt(e.key)
    if (num >= 1 && num <= choices.length) {
      onChoose(choices[num - 1].id)
    }
  }
  
  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [choices, onChoose])
```

### "I want to sync new data from Velinor"

1. **Run sync command:**
   ```bash
   npm run sync-parallel
   ```

2. **Verifies:**
   - NPCs from `velinor/npcs/` → `public/assets/npcs/`
   - Profiles from `velinor/data/` → `src/data/`
   - Backgrounds synced

### "I want to add a new page/route"

1. **Create** `src/app/my-route/page.tsx`

2. **Access game state** (if needed):
   ```typescript
   import { useGameStore } from '@/store/gameStore'
   
   export default function MyPage() {
     const { sessionId } = useGameStore()
     return <div>Session: {sessionId}</div>
   }
   ```

3. **Navigate to it** from other pages:
   ```typescript
   import { useRouter } from 'next/navigation'
   const router = useRouter()
   router.push('/my-route')
   ```

---

## Development & Deployment

### Local Development

**Setup:**
```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Make changes to .tsx, .css, .ts files
# Hot reload: Changes auto-refresh in browser
```

**Environment Variables:** `.env.local`
```env
NEXT_PUBLIC_VELINOR_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_VELINOR_API_TIMEOUT=30000
```

### Building for Production

```bash
# Build optimized version
npm run build

# Run production build locally
npm start

# Output: .next/ directory (ready to deploy)
```

### Deployment Options

#### Option 1: Vercel (Recommended for Next.js)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# With environment variables
vercel env pull
vercel
```

#### Option 2: Docker
```bash
# Build image
docker build -t velinor-web .

# Run container
docker run -p 3000:3000 velinor-web
```

#### Option 3: Manual Deploy
```bash
npm run build
# Upload .next/ directory to server with Node.js
```

### Type Checking

```bash
# Check for TypeScript errors
npm run type-check

# Watch mode
npm run type-check -- --watch
```

### Linting

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

### Testing

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# With coverage
npm test -- --coverage
```

### Common Development Issues

**API calls failing:**
- Check `NEXT_PUBLIC_VELINOR_API_BASE_URL` in `.env.local`
- Verify Velinor backend is running
- Check browser console for network errors

**NPC portraits not loading:**
- Run `npm run sync-parallel`
- Verify filenames match NPC names
- Check `public/assets/npcs/` exists

**Game state not updating:**
- Check Zustand store in browser DevTools
- Verify API response structure
- Add console.log to debug state changes

**Styling not applying:**
- Clear `.next/` build cache: `rm -rf .next`
- Restart dev server: `npm run dev`
- Verify CSS module imports are correct

---

## Integration with Velinor Backend

### Parallel Folder Sync

**What Gets Synced:**

| Velinor | velinor-web |
|---------|------------|
| `velinor/npcs/` | `public/assets/npcs/` |
| `velinor/backgrounds/` | `public/assets/backgrounds/` |
| `velinor/data/npc_profiles.json` | `src/data/npc_profiles.json` |
| `velinor/data/glyphs_complete.json` | `src/data/glyphs.json` |

**When to Sync:**
- After adding new NPC
- After changing NPC profile
- After updating game data

**Sync Command:**
```bash
npm run sync-parallel
```

### When Backend Changes

**If Velinor adds/changes an endpoint:**
1. Update `src/lib/api.ts` — Add/modify GameApiClient method
2. Update store if needed: `src/store/gameStore.ts`
3. Test: `npm run dev`

**If Velinor changes response format:**
1. Update types: `src/types/api.ts`
2. Update GameApiClient handling
3. Update store if structure changed
4. Test all related components

---

## How to Use This Document

### I want to understand...
- **How the frontend talks to Velinor** → [How It Connects to Velinor](#how-it-connects-to-velinor)
- **How components are organized** → [Component Architecture](#component-architecture)
- **How game state flows** → [State Management](#state-management)
- **How to deploy the app** → [Development & Deployment](#development--deployment)

### I want to modify...
- **The title screen** → [Page 1: Title Screen](#page-1-title-screen-srcapppagetsxhtml)
- **Game play layout** → [Page 2: Game Play](#page-2-game-play-srcappgamesessionidpagetsx)
- **A component's styling** → [Styling & Visual Design](#styling--visual-design)
- **How glyphs display** → [Rendering Game Systems](#rendering-game-systems)

### I want to add...
- **A new UI panel** → [Common Component Tasks](#common-component-tasks)
- **A new page** → [Common Frontend Tasks](#common-frontend-tasks)
- **Keyboard shortcuts** → [Common Frontend Tasks](#common-frontend-tasks)

---

**Last Updated:** January 20, 2026  
**Maintained by:** Velinor-Web Development Team  
**Status:** Production-ready, actively maintained
