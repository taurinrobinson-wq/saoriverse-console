# Implementation Checklist & Next Steps

## ✅ What's Been Completed

### Code Architecture
- [x] Created DialogueMode.cs enum (4 dialogue types)
- [x] Created BeatData.cs with all data structures
- [x] Rewrote DialogueManager.cs (beat-based, 292 lines)
- [x] Updated DialogueUIController.cs with new methods
- [x] Fixed TONE/REMNANTS effect application
- [x] Created backup of old DialogueManager (1389 lines)

### Data Format
- [x] JSON files already in correct beat format
- [x] "passages" array contains beats (no conversion needed)
- [x] All 8 story files are compatible

### Documentation
- [x] Created comprehensive refactoring summary
- [x] Created usage guide with examples
- [x] Documented all 4 dialogue modes
- [x] Documented troubleshooting guide

---

## 🧪 Phase 1: Verification (Do This First)

### 1.1 Verify Compilation
```
Unity → Window → General → Console
```
- [ ] No compilation errors in Console
- [ ] No warnings about missing types (DialogueMode, BeatData)
- [ ] DialogueManager appears in GameObject Inspector → Add Component

### 1.2 Scene Setup
- [ ] Create empty scene or use existing dialogue scene
- [ ] Add empty GameObject "DialogueManager"
  - [ ] Attach DialogueManager.cs component
  - [ ] Attach DialogueUIController.cs component (or find existing)
  - [ ] Assign your JSON file to `dialogueJson` field

### 1.3 JSON Compatibility Test
```csharp
// Temporary test in a MonoBehaviour Start():
var jsonFile = Resources.Load<TextAsset>("velinor/stories/ravi_nima_market_discovery");
var root = JsonUtility.FromJson<DialogueJson>(jsonFile.text);
Debug.Log($"Loaded {root.passages.Length} beats");
```
- [ ] No JSON parse errors
- [ ] Correct number of beats loads
- [ ] Beat IDs are recognized

---

## 🎬 Phase 2: Gameplay Integration (After Verification)

### 2.1 Find NPC Interaction Code
Search for where player talks to NPCs:
```csharp
// Find this pattern:
public void OnInteract() { ... }
// or
public void TalkToNPC(string npcName) { ... }
```
- [ ] Located NPC interaction entry point
- [ ] Understand how NPC is identified (string ID, component, etc.)

### 2.2 Wire Up Dialogue Start
```csharp
// In your NPC interaction code, add:
DialogueManager.Instance.LoadDialogue(npcDialogueJson);
DialogueManager.Instance.StartDialogue(npcId, "beat_1");
```
- [ ] Replace old DialogueManager calls with new ones
- [ ] Test: Player talks to NPC → dialogue starts

### 2.3 Handle Dialogue End
```csharp
// In DialogueManager.EndDialogue(), add a callback:
// Option 1: Add event
public event System.Action OnDialogueEnded;
// Call in EndDialogue(): OnDialogueEnded?.Invoke();

// Option 2: Check IsDialogueActive in your NPC script Update()
if (!DialogueManager.Instance.IsDialogueActive)
{
    // Player regains control
}
```
- [ ] Player regains control when dialogue ends
- [ ] No stuck input state

### 2.4 Test First Dialogue
- [ ] Start game, trigger NPC interaction
- [ ] Check Console for mode inference logs
- [ ] Verify first beat displays
- [ ] Verify choices appear (if expected)
- [ ] Test one choice selection
- [ ] Test dialogue advancement
- [ ] Test dialogue end (UI hides properly)

---

## 🎭 Phase 3: Each Dialogue Mode (Test One at a Time)

### Test NPCToNPC
Find a beat with `beat_type: "npc_shared"`:
- [ ] Speaker name displays (or hides if "Shared")
- [ ] Text shows dialogue between NPCs
- [ ] Auto-advances or [Continue] button appears
- [ ] No choice buttons visible
- [ ] Moves to next beat correctly

### Test NPCToPlayer
Find a beat with `beat_type: "npc_turn"`:
- [ ] NPC name displays
- [ ] NPC's question shows
- [ ] 4 choice buttons appear (T/O/N/E)
- [ ] After choice: result_text disappears, NPC response shows
- [ ] TONE effect applied (check StatManager values)
- [ ] REMNANTS effect applied to correct NPC
- [ ] Advances to target beat

### Test PlayerInnerThought
Find a beat with `beat_type: "player_posture"` (no choices):
- [ ] Speaker name is hidden
- [ ] Player's thought displays (possibly styled differently)
- [ ] No choice buttons appear
- [ ] Auto-advances

### Test PlayerActionChoice
Find a beat with `beat_type: "player_posture"` (has choices):
- [ ] Action prompt displays
- [ ] 4 choice buttons appear
- [ ] After choice: result_text shows
- [ ] Optional NPC response shows (if non-empty)
- [ ] Effects applied
- [ ] Advances correctly

---

## 🔌 Phase 4: System Integration

### 4.1 TONE System Verification
```csharp
// In test code or debug panel:
var trust = StatManager.Instance.GetPlayerTone(ToneType.Trust);
Debug.Log($"Player Trust: {trust}");
```
- [ ] TONE values change after dialogue choices
- [ ] Values persist (don't reset each dialogue)
- [ ] Correct TONE type affected

### 4.2 REMNANTS System Verification
```csharp
// Debug:
var remnants = StatManager.Instance.GetNpcRemnants("Nima");
Debug.Log($"Nima Resolve: {remnants.resolve}");
```
- [ ] NPC stat values change correctly
- [ ] Correct NPC modified (not wrong NPC)
- [ ] Values between 0.1 and 0.9 (clamped properly)
- [ ] Stat names match your RemnantType enum

### 4.3 Codex Integration (if you have it)
- [ ] Dialogue doesn't block codex clicks
- [ ] Glyphs can be clicked during dialogue

### 4.4 Diary Integration (if applicable)
- [ ] Diary entries unlock based on beats
- [ ] No conflicts with dialogue UI

---

## 🐛 Phase 5: Debugging (If Issues Arise)

### Check These First:
1. **Console Logs** - Look for [DialogueManager] messages
2. **Beat Mode** - Verify mode was inferred correctly
3. **JSON Structure** - Run test in Phase 1.3 again
4. **Active NPC ID** - Verify it matches NPC name in StatManager
5. **Effect Names** - Check stat names match ParseTone/ParseRemnantType

### Common Issues & Fixes:

**Issue: "No beat with pid 'beat_X'"**
- Check JSON file path and loading
- Verify target beat ID in choices matches actual beats

**Issue: Choices don't appear**
- Check beat mode inference log
- Verify choices array is non-empty
- Ensure DialogueUIController can find choice buttons

**Issue: Text disappears too fast**
- This is normal (no typewriter animation yet)
- Add animation to ShowText() if you want delay

**Issue: Effects don't apply**
- Check activeNpcId is correct
- Verify stat names in JSON match ParseTone() / ParseRemnantType()
- Look for StatManager warnings in console

**Issue: NPC response not showing**
- Verify npc_response field is non-empty in JSON
- Check dialogue mode is correct (should show responses)

---

## 📋 Optional Enhancements (For Later)

### Add Typewriter Animation
```csharp
// In DialogueUIController.ShowText():
StartCoroutine(TypewriterAnimation(text, onComplete));
```

### Add Audio Support
```csharp
// In BeatData.cs, add:
public string audio_clip;  // Audio for this beat's text

// In DialogueManager.DisplayBeat(), use audio_clip
```

### Add Dialogue Conditions
```csharp
// In BeatData.cs, add:
public string[] required_flags;  // Must be true to see beat

// In DisplayBeat(), check flags before showing
```

### Add UI Polish
- Fade in/out dialogue panel
- Animate choice buttons
- Add speaker portraits
- Add camera pans between speakers

---

## 🎯 Success Criteria

Phase 1 Complete: ✅ Compiles, test beat loads, DialogueManager is accessible  
Phase 2 Complete: ✅ Player can start dialogue, it displays, player can advance  
Phase 3 Complete: ✅ All 4 dialogue modes work correctly  
Phase 4 Complete: ✅ TONE/REMNANTS effects apply correctly  
Phase 5 Complete: ✅ All debug issues resolved  

**Full Success:** Dialogue flows smoothly, effects apply, game feels responsive 🎬

---

## 📞 Quick Reference

### Key Classes/Files
- `DialogueMode.cs` - Enum with 4 modes
- `BeatData.cs` - Data structures (BeatData, BeatChoice, DialogueJson)
- `DialogueManager.cs` - Dialogue runner (292 lines)
- `DialogueUIController.cs` - UI & input (615 lines)

### Key Methods
- `DialogueManager.LoadDialogue(TextAsset)` - Load JSON
- `DialogueManager.StartDialogue(npcId, beatPid)` - Start dialogue
- `DialogueManager.IsDialogueActive` - Check if running
- `DialogueUIController.ShowSpeaker(name)` - Show/hide speaker
- `DialogueUIController.ShowChoices(beat, callback)` - Show choices
- `DialogueUIController.WaitForDisplayComplete()` - Wait for text done

### Important Enums
- `DialogueMode` - NPCToNPC, NPCToPlayer, PlayerInnerThought, PlayerActionChoice
- `ToneType` - Trust, Observation, NarrativePresence, Empathy
- `RemnantType` - Resolve, Empathy, Memory, Nuance, Authority, Need, Trust, Skepticism

---

## 📚 Documentation Files

- `dialogue-system-refactoring-summary.md` - Architecture overview
- `how-to-use-beats-dialogue.md` - Usage guide & examples
- `Implementation Checklist & Next Steps.md` - This file

---

## Ready? 🚀

1. Start with **Phase 1** (Verification)
2. Move to **Phase 2** (Integration)
3. Test each mode in **Phase 3**
4. Verify systems in **Phase 4**
5. Debug if needed in **Phase 5**

Good luck! The new beats system is much cleaner and should resolve all your dialogue timing issues. 🎭
