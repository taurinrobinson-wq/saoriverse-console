# VELINOR_INTEGRATION_CONTRACT.md

**API Contract Between Velinor Backend and Velinor-Web Frontend**

**Status:** Authoritative specification for system communication  
**Version:** 1.0  
**Last Updated:** January 20, 2026  
**Maintained by:** Velinor Development Team

> 📍 **Location:** This document is **mirrored in both repos**:
> - `velinor/VELINOR_INTEGRATION_CONTRACT.md`
> - `velinor-web/VELINOR_INTEGRATION_CONTRACT.md`
>
> ⚠️ **Keep both copies in sync** when making changes to the contract.

---

## Quick Reference

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/api/game/start` | POST | Initialize game session | PlayerStart | GameState |
| `/api/game/action` | POST | Process player choice | PlayerAction | GameState |
| `/api/game/status` | GET | Get current game state | Query: sessionId | GameState |
| `/api/game/save` | POST | Save game to slot | SaveRequest | SaveResponse |
| `/api/game/load` | GET | Load game from slot | Query: sessionId, slot | GameState |
| `/api/debug` | GET | Get debug information | Query: sessionId | DebugInfo |

---

## Authentication & Session

### Session Management

**Session Lifecycle:**
```
1. POST /api/game/start
   → Backend generates sessionId
   → Returns to client
   ↓
2. Client stores sessionId in browser
   ↓
3. All subsequent requests include sessionId
   ↓
4. Backend uses sessionId to locate game state
   ↓
5. POST /api/game/save (optional) or session auto-expires
```

**Session Persistence:**
- Sessions stored in backend memory (default) or database
- Sessions auto-expire after 24 hours of inactivity
- Explicit save via `/api/game/save` persists across sessions
- Load via `/api/game/load` restores from slot

**Client Responsibilities:**
- Store `sessionId` from `/api/game/start` response
- Include `sessionId` in all subsequent requests
- Include `sessionId` in `/api/game/save` and `/api/game/load`

---

## Request/Response Formats

### 1. POST `/api/game/start`

**Purpose:** Initialize a new game session

**Request:**
```json
{
  "player_name": "Alice"
}
```

**Parameters:**
- `player_name` (string, required) — Player's chosen name (1-100 chars)

**Response (200 OK):**
```json
{
  "session_id": "uuid-format-string",
  "player_name": "Alice",
  "current_passage": "passage-001",
  "current_npc": "SaoriName",
  "dialogue_text": "Welcome to Velinor...",
  "choices": [
    {
      "id": "choice-001",
      "text": "Tell me about this place"
    },
    {
      "id": "choice-002",
      "text": "I'm confused"
    }
  ],
  "player_state": {
    "empathy": 50,
    "skepticism": 50,
    "integration": 50,
    "awareness": 50,
    "coherence": 50
  },
  "influence_map": {
    "SaoriName": 0.5,
    "VelinorEntity": 0.5
  },
  "active_glyphs": [],
  "phase": 1
}
```

**Error Responses:**
```json
// 400 Bad Request
{
  "error": "player_name is required",
  "code": "VALIDATION_ERROR"
}

// 500 Internal Server Error
{
  "error": "Failed to initialize game",
  "code": "SYSTEM_ERROR"
}
```

---

### 2. POST `/api/game/action`

**Purpose:** Process player choice and advance game

**Request:**
```json
{
  "session_id": "uuid-format-string",
  "action_id": "choice-001"
}
```

**Parameters:**
- `session_id` (string, required) — Session ID from /api/game/start
- `action_id` (string, required) — Choice ID from current choices

**Response (200 OK):**
```json
{
  "session_id": "uuid-format-string",
  "current_passage": "passage-002",
  "current_npc": "SaoriName",
  "dialogue_text": "You asked me about this place...",
  "choices": [
    {
      "id": "choice-003",
      "text": "And then what happened?"
    },
    {
      "id": "choice-004",
      "text": "That doesn't make sense"
    }
  ],
  "player_state": {
    "empathy": 55,
    "skepticism": 48,
    "integration": 52,
    "awareness": 51,
    "coherence": 51
  },
  "influence_map": {
    "SaoriName": 0.55,
    "VelinorEntity": 0.5
  },
  "active_glyphs": [
    {
      "id": "glyph_comfort_001",
      "tier1_hint": "◈",
      "tier2_context": "Presence",
      "tier3_plaintext": null,
      "revealed_tier": 1
    }
  ],
  "collected_glyphs": ["glyph_comfort_001"],
  "phase": 1,
  "message": "Choice processed successfully"
}
```

**Response Fields:**
- `current_passage` — ID of current story passage
- `current_npc` — Name of current NPC (null if narration)
- `dialogue_text` — Full text to display to player
- `choices` — Available player choices (array of {id, text})
- `player_state` — Current TONE stats and coherence
- `influence_map` — Relationship values with each NPC (0-1)
- `active_glyphs` — Currently revealed glyphs
- `collected_glyphs` — All glyphs collected so far
- `phase` — Current game phase (1-5)
- `message` — Status message (optional)

**Error Responses:**
```json
// 400 Bad Request
{
  "error": "action_id not in available choices",
  "code": "INVALID_CHOICE"
}

// 404 Not Found
{
  "error": "session_id not found",
  "code": "SESSION_NOT_FOUND"
}

// 500 Internal Server Error
{
  "error": "Failed to process action",
  "code": "SYSTEM_ERROR"
}
```

---

### 3. GET `/api/game/status`

**Purpose:** Get current game state without advancing

**Request:**
```
GET /api/game/status?session_id=uuid-format-string
```

**Query Parameters:**
- `session_id` (required) — Session ID from /api/game/start

**Response (200 OK):**
```json
{
  "session_id": "uuid-format-string",
  "player_name": "Alice",
  "current_passage": "passage-002",
  "current_npc": "SaoriName",
  "dialogue_text": "...",
  "choices": [...],
  "player_state": {...},
  "influence_map": {...},
  "active_glyphs": [...],
  "collected_glyphs": [...],
  "phase": 1,
  "save_slots": [
    {
      "slot": 0,
      "has_save": true,
      "timestamp": "2025-01-20T15:30:00Z",
      "phase": 1,
      "player_name": "Alice"
    },
    {
      "slot": 1,
      "has_save": false,
      "timestamp": null,
      "phase": null,
      "player_name": null
    }
  ]
}
```

**Error Responses:**
```json
// 404 Not Found
{
  "error": "session_id not found",
  "code": "SESSION_NOT_FOUND"
}
```

---

### 4. POST `/api/game/save`

**Purpose:** Save game state to a save slot

**Request:**
```json
{
  "session_id": "uuid-format-string",
  "slot": 0
}
```

**Parameters:**
- `session_id` (string, required) — Session ID
- `slot` (integer, required) — Save slot 0-9

**Response (200 OK):**
```json
{
  "saved": true,
  "session_id": "uuid-format-string",
  "slot": 0,
  "timestamp": "2025-01-20T15:30:00Z",
  "message": "Game saved to slot 0"
}
```

**Error Responses:**
```json
// 400 Bad Request
{
  "error": "slot must be 0-9",
  "code": "INVALID_SLOT"
}

// 404 Not Found
{
  "error": "session_id not found",
  "code": "SESSION_NOT_FOUND"
}

// 500 Internal Server Error
{
  "error": "Failed to save game",
  "code": "SAVE_ERROR"
}
```

---

### 5. GET `/api/game/load`

**Purpose:** Load game state from a save slot

**Request:**
```
GET /api/game/load?session_id=uuid-format-string&slot=0
```

**Query Parameters:**
- `session_id` (required) — Current session ID (or new session for load)
- `slot` (required) — Save slot 0-9

**Response (200 OK):**
```json
{
  "session_id": "uuid-format-string",
  "current_passage": "passage-015",
  "current_npc": "VelinorEntity",
  "dialogue_text": "...",
  "choices": [...],
  "player_state": {
    "empathy": 62,
    "skepticism": 55,
    "integration": 58,
    "awareness": 60,
    "coherence": 58
  },
  "influence_map": {...},
  "active_glyphs": [...],
  "collected_glyphs": [...],
  "phase": 2,
  "message": "Game loaded from slot 0"
}
```

**Error Responses:**
```json
// 400 Bad Request
{
  "error": "slot must be 0-9",
  "code": "INVALID_SLOT"
}

// 404 Not Found
{
  "error": "no save in slot 0",
  "code": "SAVE_NOT_FOUND"
}

// 500 Internal Server Error
{
  "error": "Failed to load game",
  "code": "LOAD_ERROR"
}
```

---

### 6. GET `/api/debug`

**Purpose:** Get debug information (development only)

**Request:**
```
GET /api/debug?session_id=uuid-format-string
```

**Response (200 OK):**
```json
{
  "session_id": "uuid-format-string",
  "debug_info": {
    "current_state": {...},
    "all_gates": {...},
    "trait_activations": [...],
    "npc_response_pool": {...},
    "phase_state": {...}
  },
  "message": "Debug info for development"
}
```

---

## Glyphs in API

### Glyph Object Format

**In API responses:**
```json
{
  "id": "glyph_comfort_001",
  "name": "Glyph Name",
  "category": "comfort",
  "tier1_hint": "◈",
  "tier1_color": "#9b59b6",
  "tier2_context": "Presence. Someone is here.",
  "tier3_plaintext": "The promise of companionship",
  "revealed_tier": 1,
  "associated_traits": ["Empathy", "Vulnerability"],
  "is_transcendence": false
}
```

**Revealed Tier Logic:**
- `revealed_tier: 0` — Glyph exists but not yet seen
- `revealed_tier: 1` — Tier 1 (Hint) revealed, can see symbol + context
- `revealed_tier: 2` — Tier 2 (Context) revealed, can see meaning
- `revealed_tier: 3` — Tier 3 (Plaintext) revealed, full meaning unlocked

**Frontend Rendering:**
```typescript
// Show only up to revealed tier
switch (glyph.revealed_tier) {
  case 1:
    display(glyph.tier1_hint, glyph.tier2_context)
  case 2:
    display(glyph.tier1_hint, glyph.tier2_context, glyph.tier3_plaintext)
  case 3:
    display(full_glyph_meaning)
}
```

---

## Choice Objects

### Choice Format

**In passages:**
```json
{
  "id": "choice-001",
  "text": "Tell me more",
  "tone_impact": {
    "empathy": 5,
    "skepticism": -3,
    "integration": 2,
    "awareness": 0
  },
  "influence_impact": {
    "SaoriName": 0.1,
    "VelinorEntity": -0.05
  },
  "gates": [
    {
      "type": "empathy",
      "operator": ">=",
      "value": 50
    },
    {
      "type": "influence",
      "npc": "SaoriName",
      "operator": ">=",
      "value": 0.7
    }
  ],
  "is_locked": false,
  "lock_reason": null,
  "next_passage": "passage-002"
}
```

**Fields:**
- `id` — Unique choice identifier
- `text` — Text displayed to player
- `tone_impact` — TONE stat modifications
- `influence_impact` — Relationship changes per NPC
- `gates` — Conditions for choice availability
- `is_locked` — Whether gates prevent this choice
- `lock_reason` — Why choice is locked (if locked)
- `next_passage` — Passage ID if choice selected

**Frontend Logic:**
```typescript
// Check if choice should be selectable
const isAvailable = !choice.is_locked && 
                     evaluateGates(choice.gates, gameState)

if (isAvailable) {
  <button onClick={() => takeAction(choice.id)}>
    {choice.text}
  </button>
} else {
  <button disabled title={choice.lock_reason}>
    {choice.text} (locked)
  </button>
}
```

---

## Error Handling

### Error Response Format

**All errors follow this structure:**
```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": {
    "field": "optional additional details"
  }
}
```

### Common Error Codes

| Code | HTTP | Meaning | Recovery |
|------|------|---------|----------|
| `VALIDATION_ERROR` | 400 | Invalid request data | Fix request format |
| `SESSION_NOT_FOUND` | 404 | Session ID not found | Start new game |
| `INVALID_CHOICE` | 400 | Choice ID not available | Show available choices |
| `INVALID_SLOT` | 400 | Save slot out of range | Use 0-9 |
| `SAVE_NOT_FOUND` | 404 | No save in slot | Show save list |
| `SAVE_ERROR` | 500 | Save failed | Retry or contact support |
| `LOAD_ERROR` | 500 | Load failed | Retry or contact support |
| `SYSTEM_ERROR` | 500 | Backend error | Retry, contact if persistent |

### Client Error Handling

**Recommended frontend pattern:**
```typescript
try {
  const response = await GameApiClient.takeAction(sessionId, choiceId)
  gameStore.updateGameState(response)
} catch (error) {
  if (error.code === 'SESSION_NOT_FOUND') {
    // Redirect to title screen
    router.push('/')
  } else if (error.code === 'INVALID_CHOICE') {
    // Show error message, refresh choices
    console.error('Choice no longer available')
    const status = await GameApiClient.getGameStatus(sessionId)
    gameStore.updateGameState(status)
  } else {
    // Generic error handling
    showErrorModal(error.error)
  }
}
```

---

## Data Sync & Coherence

### Coherence Calculation (Backend)

**Formula:**
```
coherence = 100 - average_absolute_deviation(empathy, skepticism, integration, awareness)
```

**Example:**
```
TONE: [60, 55, 62, 58]
Mean: 58.75
Deviations: [1.25, 3.75, 3.25, 0.75]
Avg Deviation: 2.25
Coherence: 100 - 2.25 = 97.75 (round to 98)
```

**Frontend:** Should trust backend calculation, not recalculate

### Influence Updates

**When choice is taken:**
1. Backend evaluates choice's `influence_impact`
2. For each NPC in impact:
   ```
   new_influence[npc] = current_influence[npc] + impact_value
   clamped to [0, 1]
   ```
3. Returns updated `influence_map` in response

**Frontend:** Should display influence as simple 0-1 scale (e.g., 65%)

---

## Emotional Gates

### Gate Types in API

**1. TONE Gates** — Require minimum stat level
```json
{
  "type": "empathy",
  "operator": ">=",
  "value": 60
}
```

**2. Coherence Gates** — Require emotional harmony
```json
{
  "type": "coherence",
  "operator": ">=",
  "value": 75
}
```

**3. Influence Gates** — Require relationship threshold
```json
{
  "type": "influence",
  "npc": "SaoriName",
  "operator": ">=",
  "value": 0.7
}
```

**Operators:** `>=`, `<=`, `>`, `<`, `==`, `!=`

### How Frontend Should Handle Gates

**Option 1: Disable Locked Choices**
- Show disabled button with lock reason
- Allow player to see condition they need

**Option 2: Hide Locked Choices**
- Don't show choices they can't take
- Simpler but less transparent

**Recommended:** Option 1 with explanation

```typescript
function ChoiceButtons({ choices }) {
  return (
    <>
      {choices.map(choice => (
        <button 
          key={choice.id}
          disabled={choice.is_locked}
          title={choice.lock_reason}
          onClick={() => takeAction(choice.id)}
        >
          {choice.text}
          {choice.is_locked && ` (${choice.lock_reason})`}
        </button>
      ))}
    </>
  )
}
```

---

## Session Lifecycle Example

### Full User Session

```
1. User visits website
   ↓

2. Click "Play" → enters name "Alice"
   POST /api/game/start
   Request: { "player_name": "Alice" }
   Response: { 
     "session_id": "abc-123",
     "current_passage": "passage-001",
     "choices": [...],
     "player_state": { "empathy": 50, ... }
   }
   ↓

3. Browser stores sessionId in store
   ↓

4. See first passage and choices
   Click choice "Tell me about this place"
   POST /api/game/action
   Request: { "session_id": "abc-123", "action_id": "choice-001" }
   Response: { 
     "current_passage": "passage-002",
     "choices": [...],
     "player_state": { "empathy": 55, ... }
   }
   ↓

5. Stats updated, new passage shown
   Continue playing...
   ↓

6. Click "Save Game" to slot 0
   POST /api/game/save
   Request: { "session_id": "abc-123", "slot": 0 }
   Response: { "saved": true, "timestamp": "..." }
   ↓

7. Continue or close browser
   ↓

8. Next day, user returns
   Click "Load Game"
   GET /api/game/load?session_id=abc-123&slot=0
   Response: { 
     "current_passage": "passage-045",
     "player_state": { "empathy": 68, ... }
   }
   ↓

9. Game restored to previous state
   Player continues where they left off
```

---

## Versioning & Changes

### How to Update This Contract

1. **Backward Compatibility** — Prefer adding fields, not removing
   - New optional fields: OK
   - Removing fields: Must version
   - Changing field types: Must version

2. **Version Increments:**
   - `1.x` — New optional fields, non-breaking additions
   - `2.0` — Breaking changes (removals, type changes)

3. **Publishing Changes:**
   - Update `VELINOR_INTEGRATION_CONTRACT.md` in **both** repos
   - Update version number
   - Notify frontend team of changes
   - Give clients 2 weeks notice before breaking changes

### Current Version

- **Version:** 1.0
- **Released:** January 20, 2026
- **Status:** Stable, production-ready

---

## Testing the API

### Using cURL

```bash
# Start game
curl -X POST http://localhost:8000/api/game/start \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Alice"}'

# Take action
curl -X POST http://localhost:8000/api/game/action \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "action_id": "choice-001"}'

# Get status
curl http://localhost:8000/api/game/status?session_id=abc-123

# Save game
curl -X POST http://localhost:8000/api/game/save \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "slot": 0}'

# Load game
curl http://localhost:8000/api/game/load?session_id=abc-123&slot=0
```

### Using Postman

1. Create new collection "Velinor API"
2. Add requests for each endpoint
3. Set base URL: `{{BASE_URL}}/api`
4. Set variable: `BASE_URL = http://localhost:8000`
5. Set variable: `SESSION_ID` (from /start response)
6. Test each endpoint

---

## Implementation Checklist

### For Backend (Velinor)

- ✅ Implement all 6 endpoints
- ✅ Validate all request parameters
- ✅ Return specified response format
- ✅ Implement error handling with specified codes
- ✅ Calculate coherence per formula
- ✅ Update influence on choices
- ✅ Evaluate gates correctly
- ✅ Return glyphs with `revealed_tier`
- ✅ Generate unique sessionIds
- ✅ Persist save slots

### For Frontend (velinor-web)

- ✅ Implement GameApiClient with all methods
- ✅ Store sessionId from /start response
- ✅ Send sessionId in all requests
- ✅ Update game state from responses
- ✅ Display glyphs respecting `revealed_tier`
- ✅ Show gate lock reasons for locked choices
- ✅ Handle error responses with retry logic
- ✅ Implement save/load UI
- ✅ Sync assets (NPCs, backgrounds)

---

**Last Updated:** January 20, 2026  
**Maintained by:** Velinor Integration Team  
**Status:** Authoritative specification — keep both copies in sync
