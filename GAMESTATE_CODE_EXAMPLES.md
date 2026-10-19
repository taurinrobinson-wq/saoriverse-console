# GameState System - Code Examples & Reference

## Core GameState API

### NPC Visibility

```csharp
// Hide an NPC (they become inactive)
GameState.Instance.SetNPCVisibility("Ravi", false);

// Show an NPC (they become active)
GameState.Instance.SetNPCVisibility("Ravi", true);

// Check if NPC should be visible
bool isRaviVisible = GameState.Instance.GetNPCVisibility("Ravi");
```

### Dialogue Flags

```csharp
// Mark dialogue as completed
GameState.Instance.SetDialogueFlag("ravi_nima_market_discovery", true);

// Check if dialogue was completed
if (GameState.Instance.GetDialogueFlag("ravi_nima_market_discovery"))
{
    Debug.Log("Player has already done this dialogue");
}

// Mark dialogue as incomplete (rare, but possible)
GameState.Instance.SetDialogueFlag("ravi_nima_market_discovery", false);
```

### Glyph Flags

```csharp
// Mark glyph as collected
GameState.Instance.SetGlyphFlag("glyph_sorrow", true);

// Check if player has glyph
if (GameState.Instance.GetGlyphFlag("glyph_sorrow"))
{
    // Unlock new dialogue or scene
}
```

### Quest States

```csharp
// Set quest to specific state
GameState.Instance.SetQuestState("market_sorrow_quest", "in_progress");
GameState.Instance.SetQuestState("market_sorrow_quest", "completed");

// Check quest state
string questState = GameState.Instance.GetQuestState("market_sorrow_quest");
if (questState == "completed")
{
    // Reward player
}
```

### Debugging

```csharp
// Print ALL state to console
GameState.Instance.DebugPrintState();
// Output:
// === GAME STATE DEBUG ===
// --- NPC Visibility ---
//   Ravi: False
//   Nima: False
//   Kaelen: True
// --- Dialogue Flags ---
//   ravi_nima_market_discovery: True
// --- Glyph Flags ---
//   glyph_sorrow: True
// --- Quest States ---
//   market_sorrow_quest: completed

// Reset all state (useful for testing)
GameState.Instance.ResetAllState();
```

---

## Real-World Examples

### Example 1: Dialogue Completion Hides NPC

**In DialogueManager.cs:**

```csharp
private void ProcessSystemTriggers(string[] triggers, string[] diaryEntries = null)
{
    foreach (var trigger in triggers)
    {
        if (trigger.type == "disable_npc")
        {
            string npcName = trigger.key ?? (trigger.data?[0] ?? null);
            if (!string.IsNullOrEmpty(npcName))
            {
                // CHANGE: Use GameState instead of direct SetActive
                GameState.Instance.SetNPCVisibility(npcName, false);
                
                // Optional: Also disable immediately for visual feedback
                GameObject npcObj = GameObject.Find(npcName);
                if (npcObj != null)
                {
                    npcObj.SetActive(false);
                    Debug.Log($"[DialogueManager] NPC hidden: {npcName}");
                }
            }
        }
        
        if (trigger.type == "set_flag")
        {
            string flagName = trigger.key ?? (trigger.data?[0] ?? null);
            string flagValue = trigger.value ?? (trigger.data?.Length > 1 ? trigger.data[1] : "true");
            
            if (!string.IsNullOrEmpty(flagName))
            {
                bool boolValue = flagValue.ToLower() == "true";
                GameState.Instance.SetDialogueFlag(flagName, boolValue);
                Debug.Log($"[DialogueManager] Dialogue flag: {flagName} = {boolValue}");
            }
        }
    }
}
```

**Result:**
- Player completes Ravi/Nima dialogue
- disable_npc trigger fires
- GameState marks "Ravi" and "Nima" as hidden
- NPCState components on both NPCs see the state changed
- Both NPCs call SetActive(false)
- Player transitions to another scene
- Returns to market
- SceneStateApplier runs, tells NPCState components to sync
- NPCState components check GameState, see they're marked hidden
- NPCs stay hidden ✓

---

### Example 2: Multiple Triggers Affect Same NPC

**Scenario:** Kaelen should appear only after BOTH conditions:
1. Player obtains Sorrow Glyph
2. Player completes Ravi/Nima dialogue

**In GlyphCollector.cs** (when player touches glyph):

```csharp
private void OnColliderEnter(Collider other)
{
    if (other.CompareTag("Player"))
    {
        // Mark glyph as collected
        GameState.Instance.SetGlyphFlag("glyph_sorrow", true);
        Debug.Log("[GlyphCollector] Sorrow glyph collected!");
        
        // Check if both conditions met
        if (GameState.Instance.GetDialogueFlag("ravi_nima_market_discovery") &&
            GameState.Instance.GetGlyphFlag("glyph_sorrow"))
        {
            // Make Kaelen appear
            GameState.Instance.SetNPCVisibility("Kaelen", true);
            Debug.Log("[GlyphCollector] Kaelen should now appear in market!");
        }
        
        // Hide this glyph
        gameObject.SetActive(false);
    }
}
```

**In DialogueManager.cs** (when dialogue completes):

```csharp
private void OnDialogueComplete()
{
    // Mark dialogue as complete
    GameState.Instance.SetDialogueFlag("ravi_nima_market_discovery", true);
    
    // Hide Ravi/Nima
    GameState.Instance.SetNPCVisibility("Ravi", false);
    GameState.Instance.SetNPCVisibility("Nima", false);
    
    // Check if both conditions met
    if (GameState.Instance.GetDialogueFlag("ravi_nima_market_discovery") &&
        GameState.Instance.GetGlyphFlag("glyph_sorrow"))
    {
        // Make Kaelen appear
        GameState.Instance.SetNPCVisibility("Kaelen", true);
        Debug.Log("[DialogueManager] Kaelen should now appear in market!");
    }
}
```

**Result:**
- Player gets glyph first: Kaelen not shown yet (dialogue not done)
- Player does dialogue: Kaelen appears (both conditions met)
- **Or** Player does dialogue first: Kaelen not shown yet (glyph not collected)
- Player gets glyph: Kaelen appears (both conditions met)
- Works either way ✓

---

### Example 3: NPC Variants (Nima Alone vs with Ravi)

**Scene Setup:**

```
InsideMarket_00
├─ Ravi (GameObject)
│  ├─ NPCState (npcID: "Ravi")
│  └─ NPCDialogueDriver, etc.
├─ Nima (GameObject)
│  ├─ NPCState (npcID: "Nima")
│  └─ NPCDialogueDriver, etc.
├─ Nima_Solo (GameObject)
│  ├─ NPCState (npcID: "Nima_Solo")
│  └─ NPCDialogueDriver, etc.
```

**In some trigger system:**

```csharp
// Show Nima with Ravi
GameState.Instance.SetNPCVisibility("Ravi", true);
GameState.Instance.SetNPCVisibility("Nima", true);
GameState.Instance.SetNPCVisibility("Nima_Solo", false);

// Or show Nima alone (after Ravi left)
GameState.Instance.SetNPCVisibility("Ravi", false);
GameState.Instance.SetNPCVisibility("Nima", false);
GameState.Instance.SetNPCVisibility("Nima_Solo", true);
```

**Result:**
- Both Nima variants exist in the scene
- GameState controls which one is visible
- Easy to swap between variants
- No scene duplication needed ✓

---

### Example 4: Cross-Scene State (Glyph Trigger in Different Scene)

**In InsideMarket_02** (when player obtains glyph):

```csharp
// SorrowGlyphPickup.cs
private void OnPlayerCollect()
{
    // Mark glyph as collected (GLOBALLY)
    GameState.Instance.SetGlyphFlag("glyph_sorrow", true);
    Debug.Log("[GlyphPickup] Sorrow glyph obtained!");
    
    // Make Kaelen appear IN MARKET (even though this script is in InsideMarket_02)
    GameState.Instance.SetNPCVisibility("Kaelen", true);
    
    // Hide self
    gameObject.SetActive(false);
}
```

**Player then transitions to InsideMarket_00:**

```
Scene loads (InsideMarket_00)
├─ SceneStateApplier.Start() runs
├─ Finds Kaelen (has NPCState)
├─ Calls Kaelen.ApplyState()
├─ Checks GameState.GetNPCVisibility("Kaelen")
├─ Gets: true (was set in InsideMarket_02)
├─ Kaelen calls SetActive(true)
└─ Kaelen is now visible ✓
```

**Result:**
- Glyph collected in one scene
- NPC appears in different scene
- No flag passing, no configuration needed
- Just works ✓

---

### Example 5: Quest-Driven NPC Behavior

**In QuestSystem.cs:**

```csharp
public class QuestSystem : MonoBehaviour
{
    public void StartQuest(string questID)
    {
        GameState.Instance.SetQuestState(questID, "in_progress");
        
        // Maybe unlock NPCs for this quest
        if (questID == "market_investigation")
        {
            GameState.Instance.SetNPCVisibility("Kaelen", true);
            GameState.Instance.SetDialogueFlag("can_investigate", true);
        }
    }

    public void CompleteQuest(string questID)
    {
        GameState.Instance.SetQuestState(questID, "completed");
        
        // Hide quest-specific NPCs
        if (questID == "market_investigation")
        {
            GameState.Instance.SetNPCVisibility("Kaelen", false);
        }
    }

    public bool IsQuestActive(string questID)
    {
        return GameState.Instance.GetQuestState(questID) == "in_progress";
    }

    public bool IsQuestCompleted(string questID)
    {
        return GameState.Instance.GetQuestState(questID) == "completed";
    }
}
```

**Usage elsewhere:**

```csharp
// In dialogue system or other game logic
if (QuestSystem.IsQuestCompleted("market_investigation"))
{
    // Show end-quest dialogue
    StartDialogue("kaelen_investigation_complete");
}
```

---

### Example 6: Conditional NPC Appearance

**In CityMarketController.cs** (controls market state):

```csharp
public void UpdateMarketState()
{
    int dayNumber = TimeManager.GetCurrentDay();
    bool hasSorrowGlyph = GameState.Instance.GetGlyphFlag("glyph_sorrow");
    bool metRavi = GameState.Instance.GetDialogueFlag("ravi_nima_market_discovery");

    // Day 1-3: Ravi and Nima in market
    if (dayNumber < 4)
    {
        GameState.Instance.SetNPCVisibility("Ravi", true);
        GameState.Instance.SetNPCVisibility("Nima", true);
        GameState.Instance.SetNPCVisibility("Kaelen", false);
    }
    
    // Day 4-5: Only Nima in market (Ravi gone)
    else if (dayNumber < 6)
    {
        GameState.Instance.SetNPCVisibility("Ravi", false);
        GameState.Instance.SetNPCVisibility("Nima", true);
        GameState.Instance.SetNPCVisibility("Kaelen", hasSorrowGlyph); // Conditional
    }
    
    // Day 6+: All gone except Kaelen
    else
    {
        GameState.Instance.SetNPCVisibility("Ravi", false);
        GameState.Instance.SetNPCVisibility("Nima", false);
        GameState.Instance.SetNPCVisibility("Kaelen", hasSorrowGlyph && metRavi);
    }
}
```

**Call this when:**
- Scene loads
- Day changes
- Quest completes
- Any major game event

**Result:**
- Market state updates based on multiple factors
- NPCs appear/disappear based on logic
- All changes flow through GameState
- Consistent across all scenes ✓

---

## Integration Checklist

When adding GameState to a new system:

```csharp
1. Check GameState.Instance exists
   if (GameState.Instance == null)
   {
       Debug.LogError("GameState not initialized!");
       return;
   }

2. Get current state if needed
   bool isComplete = GameState.Instance.GetDialogueFlag("some_flag");
   bool hasGlyph = GameState.Instance.GetGlyphFlag("glyph_sorrow");

3. Update state when something happens
   GameState.Instance.SetNPCVisibility("Kaelen", true);
   GameState.Instance.SetDialogueFlag("kaelen_met", true);

4. Debug if things don't work
   GameState.Instance.DebugPrintState();
```

---

## Performance Notes

- **Memory:** Each flag is a bool/string in a Dictionary
  - 100 flags = negligible memory
  - 1000 flags = ~50KB

- **Speed:** Dictionary lookups are O(1)
  - SetNPCVisibility() runs instantly
  - No performance penalty

- **Optimization:** GameState never needs to be optimized
  - The expensive part is SetActive() on GameObjects
  - That happens anyway, GameState just controls when

---

## When Things Go Wrong

**Check in this order:**

1. GameState exists?
   ```
   GameState.Instance != null ✓
   ```

2. NPCState components exist?
   ```
   Each NPC has NPCState component ✓
   ```

3. npcIDs match exactly?
   ```
   gameObject.name == NPCState.npcID ✓
   ```

4. State changed correctly?
   ```
   GameState.Instance.DebugPrintState()
   Look for the NPC entry ✓
   ```

5. Scene applier ran?
   ```
   Console shows: [SceneStateApplier] Applied state to X ✓
   ```

6. NPCState sync happened?
   ```
   Console shows: [NPCState] X: Applied state -> VISIBLE/HIDDEN ✓
   ```

If any step fails, that's your issue.

