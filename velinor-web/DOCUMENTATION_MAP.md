# Velinor-Web Frontend — Documentation Map

**Last Updated:** January 20, 2026  
**Purpose:** Master navigation guide for Next.js/React frontend, component organization, and common updates

---

## Quick Navigation

- [Architecture & Integration](#architecture--integration) — How frontend connects to backend
- [Page Structure](#page-structure) — Pages and routing
- [Components](#components) — UI components and their purposes
- [State Management](#state-management) — Zustand stores and data flow
- [Styling & Theming](#styling--theming) — CSS, theming, visual design
- [Common Updates](#common-updates) — Quick reference for modifications
- [Development](#development) — Running, building, deploying

---

## Architecture & Integration

### Full Stack Overview

**Documentation:**
- `../firstperson/docs/INTEGRATION_SUMMARY.md` — REST API + frontend integration
- `../firstperson/docs/MODULE_INTEGRATION_MAP.md` — Module connection points
- `../firstperson/docs/PARALLEL_FOLDERS_STATUS_REPORT.md` — Data sync strategy

### API Connection

**Files to Modify:**
- `src/lib/api.ts` — GameApiClient with all API calls
- `src/config/constants.ts` — API base URL and configuration

**Key Endpoints Called:**
```typescript
// GameApiClient methods
startGame(playerName: string)          // POST /api/game/start
takeAction(sessionId, actionId)        // POST /api/game/action
saveGame(sessionId, slot)              // POST /api/game/save
loadGame(sessionId, slot)              // GET /api/game/load/{sessionId}
getGameStatus(sessionId)               // GET /api/game/status
```

**Data Flow:**
```
User Input (React)
    ↓
GameApiClient.ts (TypeScript wrapper)
    ↓
Backend API (velinor/velinor_api.py)
    ↓
Velinor Game Engine
    ↓
Response JSON → Zustand Store → React Re-render
```

**Common Updates:**
- Adding API call: Create method in GameApiClient class in api.ts
- Changing API URL: Update VELINOR_API_BASE_URL in constants.ts
- Modifying request format: Edit GameApiClient method signature and body

---

## Page Structure

### Pages & Routing

**Documentation:**
- Design layouts in `src/app/` (Next.js 14 App Router)

**Pages:**

| Page | File | Purpose |
|------|------|---------|
| Title Screen | `src/app/page.tsx` | Game intro, start button |
| Game Play | `src/app/game/[sessionId]/page.tsx` | Main game interface |
| Boss Test | `src/app/test/page.tsx` | Development/testing page |

### Page: Title Screen (`src/app/page.tsx`)

**Purpose:** Game introduction and start button

**Key Elements:**
- Game title and tagline
- Player name input
- "Play" button → calls GameApiClient.startGame()
- Velinor character overlay (4-layer composition)

**Files to Modify:**
- `src/app/page.tsx` — Title screen layout
- `src/components/TitleScreen.tsx` — Title screen component (if extracted)
- `src/app/globals.css` — Title styling

**Common Updates:**
- Changing game title: Edit page.tsx title and heading text
- Updating intro text: Edit page.tsx description/tagline
- Changing start button behavior: Modify startGame() call
- Adjusting character overlay: Edit CSS in globals.css or separate CSS module

### Page: Game Play (`src/app/game/[sessionId]/page.tsx`)

**Purpose:** Main interactive game interface

**Layout:**
```
┌─ Top: NPC Portrait + Name
├─ Middle: Dialogue/Story Text (main content)
├─ Bottom: Choices (player actions)
├─ Sidebar (optional): Character stats, inventory, etc.
└─ HUD: Save/load buttons, settings
```

**Key Elements:**
- NPC portrait (from velinor/npcs/)
- Dialogue/passage text
- Player choice buttons
- Game status (current TONE stats)
- Save/load interface

**Files to Modify:**
- `src/app/game/[sessionId]/page.tsx` — Main game page layout
- `src/components/GameScene.tsx` — Game scene component
- `src/components/DialogueBox.tsx` — Dialogue display
- `src/components/ChoiceButtons.tsx` — Player choice rendering
- `src/styles/game.module.css` — Game styling

**Common Updates:**
- Changing dialogue display: Edit DialogueBox.tsx
- Modifying choice layout: Edit ChoiceButtons.tsx
- Adding HUD element: Add component and integrate in page.tsx
- Adjusting spacing/layout: Edit game.module.css

### Page: Boss Test (`src/app/test/page.tsx`)

**Purpose:** Development and testing interface

**Features:**
- Quick game start without title screen
- Debug information display
- API response viewer
- Test different NPCs/scenarios

**Files to Modify:**
- `src/app/test/page.tsx` — Test page layout
- `src/components/DevTools.tsx` — Dev tools (if extracted)

**Common Updates:**
- Adding test scenario: Add button and handler in page.tsx
- Displaying debug data: Add to response viewer

---

## Components

### Component Tree

```
<RootLayout>
├── <Header>
├── <MainContent>
│   ├── <TitleScreen> (page.tsx)
│   └── <GameScene> (game/[sessionId]/page.tsx)
│       ├── <NpcPortrait>
│       ├── <DialogueBox>
│       ├── <ChoiceButtons>
│       ├── <StatusHud>
│       └── <SaveLoadModal>
└── <Footer>
```

### Core Components

#### `<GameScene>` — Main game interface
- **File:** `src/components/GameScene.tsx`
- **Purpose:** Orchestrates all game UI
- **Props:** `sessionId`, `gameState`, `onAction`
- **Renders:** NPC portrait, dialogue, choices, HUD
- **State:** Integrated with gameStore (Zustand)

#### `<DialogueBox>` — Dialogue/passage display
- **File:** `src/components/DialogueBox.tsx`
- **Purpose:** Shows current story text
- **Props:** `text`, `npcName`, `background`
- **Features:** Text formatting, emotional tone indicators
- **State:** Uses gameStore for dialogue history

#### `<ChoiceButtons>` — Player choices
- **File:** `src/components/ChoiceButtons.tsx`
- **Purpose:** Display and handle player choices
- **Props:** `choices`, `onChoose`
- **Features:** Button styling, disabled states, keyboard shortcuts
- **State:** Tracks selected choice

#### `<NpcPortrait>` — NPC image display
- **File:** `src/components/NpcPortrait.tsx`
- **Purpose:** Show current NPC image
- **Props:** `npcName`, `emotion` (optional)
- **Source:** Images from `/public/assets/npcs/{npcName}.png`
- **Features:** Fade transitions between NPCs

#### `<StatusHud>` — Player stats display
- **File:** `src/components/StatusHud.tsx`
- **Purpose:** Show TONE stats, inventory, progress
- **Props:** `playerState`
- **Displays:** Empathy, Skepticism, Integration, Awareness values
- **State:** Updates from gameStore

#### `<SaveLoadModal>` — Persistence UI
- **File:** `src/components/SaveLoadModal.tsx`
- **Purpose:** Save game to slot, load game from slot
- **Features:** 10 save slots, timestamps, slot preview
- **State:** Calls GameApiClient.saveGame() / loadGame()

### Component Locations
```
src/components/
├── GameScene.tsx
├── DialogueBox.tsx
├── ChoiceButtons.tsx
├── NpcPortrait.tsx
├── StatusHud.tsx
├── SaveLoadModal.tsx
├── TitleScreen.tsx
├── Header.tsx
├── Footer.tsx
└── common/
    ├── Button.tsx
    ├── Modal.tsx
    └── ...
```

**Common Updates:**
- Adding UI element: Create component in src/components/, import in GameScene.tsx
- Changing component behavior: Edit component .tsx file
- Styling component: Add CSS module or edit component's className

---

## State Management

### Zustand Store (`src/store/gameStore.ts`)

**Purpose:** Centralized game state management

**Store Structure:**
```typescript
interface GameState {
  // Session
  sessionId: string | null
  playerName: string

  // Current Game State
  currentPassage: string
  npcName: string
  dialogueText: string
  choices: Choice[]

  // Player Stats (TONE)
  empathy: number
  skepticism: number
  integration: number
  awareness: number

  // Glyphs & Mechanics
  activeGlyphs: Glyph[]
  collectedGlyphs: string[]

  // Game Progress
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

**Files to Modify:**
- `src/store/gameStore.ts` — Store definition and actions

**Common Updates:**
- Adding field: Add to GameState interface, update initialState
- Adding action: Create function in store that calls API or updates state
- Removing field: Delete from interface and initialState

### Using Store in Components

```typescript
// In any component
import { useGameStore } from '@/store/gameStore'

export function MyComponent() {
  const { sessionId, empathy, takeAction } = useGameStore()

  return (
    <button onClick={() => takeAction('choice-123')}>
      Make Choice (Empathy: {empathy})
    </button>
  )
}
```

**Common Pattern:**
1. Component reads state: `const { field } = useGameStore()`
2. User interacts: button click, form submit
3. Component calls action: `takeAction(choiceId)`
4. Action calls API: `GameApiClient.takeAction()`
5. Store updates: `updateGameState()` triggered by response
6. Components re-render: Automatic with Zustand

---

## Styling & Theming

### CSS Organization

**Files:**
- `src/app/globals.css` — Global styles, theme variables, resets
- `src/components/*.module.css` — Component-specific styles
- `tailwind.config.ts` — Tailwind CSS configuration

### Theme Variables

**Global CSS Variables** (in globals.css):
```css
:root {
  /* Colors */
  --color-primary: #2c3e50;      /* Main UI color */
  --color-secondary: #3498db;    /* Accent color */
  --color-background: #1a1a1a;   /* Page background */
  --color-text: #ecf0f1;         /* Main text */

  /* Velinor Aesthetic */
  --color-glyph-active: #9b59b6;   /* Active glyph purple */
  --color-choice-hover: #e74c3c;   /* Choice hover */
  --color-npc-frame: #34495e;      /* NPC frame */

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

**Applying Themes:**
```css
/* Use in component CSS modules */
.dialogueText {
  font-family: var(--font-family-serif);
  color: var(--color-text);
  font-size: var(--font-size-body);
}

.npcFrame {
  border-color: var(--color-npc-frame);
  box-shadow: 0 0 10px rgba(155, 89, 182, 0.5);
}
```

### Tailwind CSS

**Configuration:** `tailwind.config.ts`

**Usage in Components:**
```tsx
<div className="flex flex-col gap-4 p-6 bg-slate-900 text-white rounded-lg">
  <h1 className="text-2xl font-bold text-purple-400">Title</h1>
  <p>Content</p>
</div>
```

**Common Updates:**
- Changing color scheme: Edit CSS variables in globals.css
- Adding component style: Create .module.css file next to component
- Adjusting spacing: Update --spacing-* variables
- Font changes: Edit --font-family-* variables

---

## Common Updates

### "I want to change the title screen"
1. Edit `src/app/page.tsx` — title, tagline, layout
2. Modify `src/components/TitleScreen.tsx` (if extracted)
3. Update CSS in `src/app/globals.css` or TitleScreen.module.css

### "I want to add a new UI panel (stats, inventory, etc.)"
1. Create component: `src/components/MyNewPanel.tsx`
2. Add to GameState in `src/store/gameStore.ts` if needed
3. Import and render in `src/components/GameScene.tsx`
4. Style with component.module.css

### "I want to change how dialogue appears"
1. Edit `src/components/DialogueBox.tsx` — layout, formatting, styling
2. Test in game play: `src/app/game/[sessionId]/page.tsx`
3. Adjust CSS in DialogueBox.module.css

### "I want to add keyboard shortcuts for choices"
1. Edit `src/components/ChoiceButtons.tsx` — add useEffect with keydown listener
2. Map keys (1-5, arrow keys, Enter) to choice IDs
3. Call `takeAction(choiceId)` on key press

### "I want to sync data from backend changes"
1. Velinor updates NPC images in `velinor/npcs/` → syncs to `velinor-web/public/assets/npcs/`
2. Velinor updates `npc_profiles.json` → syncs to `velinor-web/src/data/npc_profiles.json`
3. See `../firstperson/docs/PARALLEL_FOLDERS_STATUS_REPORT.md` for sync process

### "I want to change NPC portrait display"
1. Edit `src/components/NpcPortrait.tsx` — image source, size, transitions
2. Update portrait sources in `public/assets/npcs/`
3. Adjust CSS styling

### "I want to add a new page"
1. Create file in `src/app/my-page/page.tsx` or `src/app/my-page/[id]/page.tsx`
2. Use existing API client: `import { GameApiClient } from '@/lib/api'`
3. Import game store for state: `import { useGameStore } from '@/store/gameStore'`
4. Add navigation link in `src/components/Header.tsx`

---

## Development

### Setup & Installation

```bash
# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Run production build locally
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

### Development Workflow

1. **Start server:** `npm run dev`
2. **Make changes** to `.tsx`, `.css`, `.ts` files
3. **Hot reload:** Changes auto-refresh in browser
4. **Test:** Manually in browser or add tests in `__tests__/` folders
5. **Commit:** `git add .`, `git commit -m "..."`

### Directory Structure

```
velinor-web/
├── src/
│   ├── app/                      ← Pages (Next.js App Router)
│   │   ├── page.tsx              ← Title screen
│   │   ├── game/
│   │   │   └── [sessionId]/
│   │   │       └── page.tsx      ← Game play page
│   │   ├── test/
│   │   │   └── page.tsx          ← Test page
│   │   ├── layout.tsx            ← Root layout
│   │   └── globals.css           ← Global styles
│   ├── components/               ← React components
│   │   ├── GameScene.tsx
│   │   ├── DialogueBox.tsx
│   │   ├── ChoiceButtons.tsx
│   │   ├── NpcPortrait.tsx
│   │   ├── StatusHud.tsx
│   │   ├── SaveLoadModal.tsx
│   │   └── ...
│   ├── lib/                      ← Utilities
│   │   └── api.ts               ← GameApiClient
│   ├── store/                    ← Zustand stores
│   │   └── gameStore.ts
│   ├── config/                   ← Configuration
│   │   └── constants.ts
│   ├── data/                     ← Static data
│   │   ├── npc_profiles.json    ← Synced from Velinor
│   │   └── influence_map.json   ← Synced from Velinor
│   ├── styles/                   ← Shared styles
│   │   └── ...
│   └── types/                    ← TypeScript types
│       └── ...
├── public/
│   └── assets/
│       ├── npcs/                ← NPC portraits (synced)
│       ├── backgrounds/         ← Game backgrounds (synced)
│       ├── overlays/            ← Visual effects (synced)
│       └── ...
├── __tests__/                    ← Tests
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── ...
```

### Environment Variables

**File:** `.env.local`

```env
NEXT_PUBLIC_VELINOR_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_VELINOR_API_TIMEOUT=30000
```

### Type Safety

- All TypeScript files: `*.ts`, `*.tsx`
- Run type check: `npm run type-check`
- Types defined in `src/types/`

### Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# With coverage
npm test -- --coverage
```

**Test Structure:**
```
__tests__/
├── components/
│   ├── GameScene.test.tsx
│   ├── DialogueBox.test.tsx
│   └── ...
├── lib/
│   ├── api.test.ts
│   └── ...
└── store/
    └── gameStore.test.ts
```

### Deployment

**Platform:** Vercel (recommended for Next.js)

```bash
# Deploy to Vercel
vercel deploy

# With environment variables
vercel env pull   # Download from Vercel
vercel deploy     # Deploy with .env.local
```

**Alternative Hosting:** Docker

```bash
# Build Docker image
docker build -t velinor-web .

# Run container
docker run -p 3000:3000 velinor-web
```

---

## Data Sync with Velinor

### Parallel Folder Sync

**Documentation:** `../firstperson/docs/PARALLEL_FOLDERS_STATUS_REPORT.md`

**What Gets Synced:**

| Source (Velinor) | Destination (velinor-web) | Type |
|------------------|---------------------------|------|
| `velinor/data/npc_profiles.json` | `src/data/npc_profiles.json` | NPC metadata |
| `velinor/data/influence_map.json` | `src/data/influence_map.json` | NPC relationships |
| `velinor/npcs/` | `public/assets/npcs/` | NPC portraits (PNG) |
| `velinor/backgrounds/` | `public/assets/backgrounds/` | Game scenes (PNG) |
| `velinor/overlays/` | `public/assets/overlays/` | Visual effects (PNG) |

**Sync Process:**

```bash
# From velinor-web/ directory
npm run sync-parallel

# Or manually (PowerShell - Windows)
.\sync-parallel.ps1

# Or manually (Bash - Linux/Mac)
./sync-parallel.sh
```

**When to Sync:**
- After adding/changing NPC in Velinor
- After updating NPC profiles
- After adding new backgrounds
- After changing NPC relationships

---

## Troubleshooting

### "API calls failing"
1. Check `NEXT_PUBLIC_VELINOR_API_BASE_URL` in `.env.local`
2. Verify Velinor backend is running: `python -m velinor.velinor_api` or `docker-compose up`
3. Check browser console for network errors
4. Verify firewall/CORS settings

### "NPC portraits not loading"
1. Check `public/assets/npcs/` contains PNG files
2. Run sync: `npm run sync-parallel`
3. Verify naming matches `npc_profiles.json`
4. Check browser console for 404 errors

### "Game state not updating"
1. Check Zustand store actions in `src/store/gameStore.ts`
2. Verify API response format matches expected structure
3. Add console.log in components to verify state changes
4. Check browser DevTools → React tab for state

### "Styling not applying"
1. Verify CSS module is imported correctly: `import styles from './component.module.css'`
2. Use className: `className={styles.myClass}` (not className string)
3. Check Tailwind config: `npx tailwind --version`
4. Clear `.next` build cache: `rm -rf .next`, then `npm run dev`

---

## Contact Points with FirstPerson

The Next.js frontend (velinor-web) integrates with:

1. **Velinor Game Engine**
   - Via REST API (`velinor/velinor_api.py`)
   - Using GameApiClient (`src/lib/api.ts`)
   - See `../firstperson/docs/INTEGRATION_SUMMARY.md`

2. **FirstPerson Streamlit App**
   - Separate from this frontend (different tech stack)
   - Both consume same Velinor API
   - See `../firstperson/docs/INTEGRATION_SUMMARY.md` for architecture

3. **Shared Velinor Data**
   - NPC profiles, backgrounds, overlays
   - Synced via parallel folder structure
   - See `../firstperson/docs/PARALLEL_FOLDERS_STATUS_REPORT.md`

---

**Last Update:** January 20, 2026 — Post-reorganization master map
