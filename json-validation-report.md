# JSON Validation Report & Fixes Needed

## Summary
- ✅ **4 files READY** - Compatible with beats system
- ⚠️  **4 files NEED FIXES** - Missing critical fields

---

## ✅ FILES THAT ARE READY

### 1. willy_concourse_ruins.json
**Status:** ✅ READY  
**Beats:** 8  
**Beat Types:** npc_turn, npc_shared, player_inner  
**Issues:** None

### 2. ravi_nima_market_discovery.json
**Status:** ✅ READY  
**Beats:** 8  
**Beat Types:** player_posture, npc_turn, npc_shared  
**Issues:** None

### 3. nima_encounter_01.json
**Status:** ✅ READY  
**Beats:** 4  
**Beat Types:** player_posture, npc_turn  
**Issues:** None

### 4. kaelen_confession_01.json
**Status:** ✅ READY  
**Beats:** 3  
**Beat Types:** npc_turn  
**Issues:** None

---

## ⚠️  FILES THAT NEED FIXES

### Problem 1: search_remembrance_01.json
**Missing Field:** `beat_type`  
**Current Structure:**
```json
{
  "pid": "search_remembrance_01_passage_1",
  "name": "The Disturbance",
  "conversationId": "search_remembrance_01",
  "active_speaker": "System",
  "text": "...",
  "choices": []
}
```

**Required Field:** `beat_type`  
**Options:** "npc_turn", "npc_shared", "player_posture", "player_inner"

**What to do:** Add `"beat_type": "npc_shared"` to each beat (system messages are like shared dialogue)

---

### Problem 2: saori_desert_encounter_01.json
**Missing Fields:** `beat_type`, `active_speaker`

**Current Structure:**
```json
{
  "pid": "desert_intro",
  "name": "Older Woman in the Desert",
  "conversationId": "saori_encounter_01",
  "text": "You are on your way to the market?",
  "choices": [...]
}
```

**Additional Issue:** Choice structure is OLD format
- Has `"text"` instead of `"label"`
- Has `"shared_beat"` instead of `"npc_response"`
- Has `"tone_effects.entries"` (dict) instead of array format
- Missing `"result_text"`

**What to do:** 
1. Add `"beat_type"` to each beat
2. Add `"active_speaker"` 
3. Update choice structure to new format

---

### Problem 3: ravi_encounter_01.json
**Missing Field:** `beat_type`  
**Also likely has:** Old choice format (needs verification)

---

### Problem 4: nima_encounter_02.json
**Missing Field:** `beat_type`  
**Also likely has:** Old choice format (needs verification)

---

## How the Mode Inference Fails Without beat_type

```csharp
// In DialogueManager.InferModeFromBeat():
if (beat.beat_type == "npc_shared")        // ← FAILS if beat_type is null
    return DialogueMode.NPCToNPC;

if (beat.beat_type == "npc_turn" && ...)   // ← FAILS if beat_type is null
    return DialogueMode.NPCToPlayer;

// Falls back to:
return DialogueMode.NPCToNPC;  // Everything defaults to this!
```

**Result:** Dialogue won't display correctly; mode always defaults to NPCToNPC

---

## Required Fields for Each Beat

```json
{
  "pid": "beat_1",                    // REQUIRED - unique ID
  "beat_type": "npc_turn",            // REQUIRED - determines dialogue mode
  "active_speaker": "Nima",           // REQUIRED - who's speaking
  "text": "What do you want?",         // REQUIRED - dialogue text
  "conversationId": "market_01",      // REQUIRED - groups related beats
  "choices": [],                      // OPTIONAL - player choices
  "required_flags": [],               // OPTIONAL - conditions
  "scene_context": "",                // OPTIONAL - scene description
  "is_shared_beat": false             // OPTIONAL - for shared dialogue
}
```

**MISSING in problem files:**
- `beat_type` ← CRITICAL
- `active_speaker` ← CRITICAL (some files)

---

## Required Fields for Each Choice

```json
{
  "tone": "T",                        // REQUIRED - T/O/N/E
  "label": "Trust",                   // REQUIRED - button label
  "playerLine": "...",                // REQUIRED - player's spoken line
  "npc_response": "...",              // OPTIONAL - NPC's reply
  "result_text": "...",               // OPTIONAL - action feedback
  "target": "beat_2",                 // REQUIRED - next beat
  "tone_effects": [],                 // OPTIONAL - TONE stat changes
  "remnants_effects": []              // OPTIONAL - NPC stat changes
}
```

**OLD format in saori_desert_encounter_01.json:**
- `"text"` ← Should be `"label"`
- `"shared_beat"` ← Should be `"npc_response"`
- `"tone_effects": {"entries": [...]}` ← Should be `"tone_effects": [...]`
- Missing `"result_text"`

---

## Fix Priority

### Priority 1 (BLOCKING - must fix before gameplay)
1. ✅ search_remembrance_01.json - Add `beat_type` to all beats
2. ✅ saori_desert_encounter_01.json - Add `beat_type`, `active_speaker`, update choice format
3. ✅ ravi_encounter_01.json - Add `beat_type`
4. ✅ nima_encounter_02.json - Add `beat_type`

### Priority 2 (After Priority 1)
- Verify all choices have correct structure
- Ensure all `target` IDs point to valid beats
- Test each dialogue in-game

---

## What Will Happen Without These Fixes

| Missing Field | Result |
|---|---|
| `beat_type` | All beats default to NPCToNPC, dialogue won't display correctly |
| `active_speaker` | Possible null reference, speaker name won't show |
| Correct choice structure | JSON parse fails or choices don't work |

---

## Testing After Fixes

```csharp
// Test in Console:
var json = Resources.Load<TextAsset>("velinor/stories/search_remembrance_01");
var root = JsonUtility.FromJson<DialogueJson>(json.text);

// Check each beat
foreach (var beat in root.passages)
{
    Debug.Log($"Beat: {beat.pid}");
    Debug.Log($"  Type: {beat.beat_type}");
    Debug.Log($"  Speaker: {beat.active_speaker}");
    Debug.Log($"  Mode: {DialogueManager.Instance.InferModeFromBeat(beat)}");
}
```

All should show proper modes, not all NPCToNPC.
