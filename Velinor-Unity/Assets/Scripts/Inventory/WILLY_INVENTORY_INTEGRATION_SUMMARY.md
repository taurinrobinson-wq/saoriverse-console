# ✅ Inventory System + Willy Dialogue Integration – Complete

## 🎭 The Narrative Moment

**Inventory is now unlocked during Willy's payment dialogue at Beat 2**, the moment Lioren and Willy negotiate over whether the metal has value.

This transforms inventory from a "game menu" into a **diegetic learning moment**: Willy teaches Lioren that junk has value.

### Before Willy
```
broken cable = debris (ignore it)
```

### After Willy
```
broken cable = salvage (someone might want this)
```

---

## 📝 What Changed

### Willy Dialogue JSON
**File:** `willy_concourse_ruins_payment.json`

#### Beat 2 Now Includes Three System Triggers:

1. **`unlock_system: inventory`**
   - Marks "inventory" as unlocked in GameFlags
   - InventoryService checks this flag on start
   - If not unlocked, inventory UI is disabled/hidden

2. **`unlock_npc_preference: Willy`**
   - Registers Willy's preferred items: copper_wire, motor_parts, old_circuitry
   - Allows future dialogue to query what Willy wants
   - NPCs know what they value; items don't know who wants them (clean separation)

3. **`system_notification`**
   - Shows non-blocking popup: "Inventory Unlocked"
   - Message: "Useful materials can be collected while exploring."
   - Action hint: "Press I to view your Inventory"
   - Auto-dismisses after 4 seconds

#### Beat 3 Bug Fix
- Changed `prompt_source.beat_id` from `1` to `2`
- Beat 3's prompt now correctly follows Beat 2's npc_response
- Prevents repetition of Beat 1 dialogue

---

## 🔧 How It Works: Three-Stage Gameplay

### Stage 1: Tutorial (Willy Scene – NOW)
```
Beat 2 ends → System triggers fire
  ↓
"Inventory Unlocked" notification appears
  ↓
Player understands: "Things I find have value"
```

### Stage 2: Discovery (First Pickup – Soon)
```
Player explores and finds a WorldItemPickup
  ↓
Interacts to collect (e.g., copper wire)
  ↓
Simple notification: "Copper Wire ×2"
  ↓
Player learns: "I can collect and carry items"
```

### Stage 3: Exchange (Return to Willy – Later)
```
Lioren returns to Willy with collected items
  ↓
Willy notices: "That wire you've got. You using that?"
  ↓
Dialogue queries inventory for matching items
  ↓
Player offers to trade/give
  ↓
Player learns: "People value different materials"
```

---

## 🎯 System Architecture (Event-Driven, No Tight Coupling)

### The Pattern

**Dialogue issues triggers** → **Systems react independently**

```
DialogueSystem.ProcessSystemTrigger("unlock_system", ["inventory"])
  ↓
case "unlock_system":
    GameFlags.Set($"system_unlocked_{system}", true);
    break;
  ↓
InventoryService (independently) checks:
    if (!GameFlags.Get("system_unlocked_inventory"))
        CanvasGroup.alpha = 0f;  // Hide UI
```

### Benefits
- ✅ Dialogue doesn't reference InventoryService directly
- ✅ InventoryService doesn't reference DialogueSystem
- ✅ New systems can hook triggers without changes
- ✅ Each system is independently testable
- ✅ Easy to enable/disable systems via flags

---

## 📋 Implementation Checklist

### DialogueSystem (Your Existing Dialogue Manager)
```csharp
void ProcessSystemTrigger(string triggerType, List<string> data)
{
    case "unlock_system":
        foreach (string system in data)
            GameFlags.Set($"system_unlocked_{system}", true);
        break;
    
    case "unlock_npc_preference":
        string npcName = data[0];
        List<string> items = data.Skip(1).ToList();
        NPCPreferenceManager.Instance.AddPreferences(npcName, items);
        break;
    
    case "system_notification":
        string title = data[0];
        string message = data[1];
        string action = data.Length > 2 ? data[2] : "";
        NotificationManager.Instance.Show(title, message, 4f, action);
        break;
}
```

### InventoryService (Already Created)
```csharp
void Start()
{
    // ... existing setup ...
    
    // Check if inventory is unlocked
    if (!GameFlags.Get("system_unlocked_inventory"))
    {
        canvasGroup.alpha = 0f;
        canvasGroup.blocksRaycasts = false;
        Debug.Log("[InventoryService] Inventory not yet unlocked");
    }
}

void Update()
{
    // Check if newly unlocked
    if (GameFlags.Get("system_unlocked_inventory") && canvasGroup.alpha == 0f)
    {
        canvasGroup.alpha = 1f;
        canvasGroup.blocksRaycasts = true;
        Debug.Log("[InventoryService] Inventory unlocked by system trigger");
    }
}
```

### NPCPreferenceManager (New – Minimal)
```csharp
public class NPCPreferenceManager : MonoBehaviour
{
    private Dictionary<string, List<string>> preferences;
    
    public void AddPreferences(string npcName, List<string> itemIds)
    {
        preferences[npcName] = itemIds;
        Debug.Log($"[NPCPreference] {npcName} now wants: {string.Join(", ", itemIds)}");
    }
    
    public List<string> GetPreferences(string npcName)
    {
        return preferences.ContainsKey(npcName) ? preferences[npcName] : new List<string>();
    }
}
```

### NotificationManager (New – Minimal)
```csharp
public class NotificationManager : MonoBehaviour
{
    public void Show(string title, string message, float duration = 4f, string actionText = "")
    {
        // Show UI notification with title/message/action
        // Auto-hide after duration seconds
        StartCoroutine(ShowNotificationRoutine(title, message, duration, actionText));
    }
    
    IEnumerator ShowNotificationRoutine(string title, string message, float duration, string action)
    {
        // Create temporary notification UI
        // Wait duration seconds
        // Fade out and destroy
        yield return new WaitForSeconds(duration);
    }
}
```

---

## 🔗 Future Integration Points

### When Player Returns to Willy Later:

```csharp
// In WillyDialogue.OnStart():
var playerInventory = InventoryService.Instance.GetAll();
var willyWants = NPCPreferenceManager.Instance.GetPreferences("Willy");

var matchingItems = playerInventory.Keys.Where(itemId => 
    willyWants.Contains(itemId)
).ToList();

if (matchingItems.Count > 0)
{
    // Play "trading" dialogue branch
    dialogueSystem.Play("willy_sees_your_scrap");
    
    // Later, in dialogue response handling:
    foreach (var itemId in matchingItems)
    {
        ItemDefinition item = ItemDatabase.Instance.Get(itemId);
        DialogueOption($"Give {item.DisplayName}?", () =>
        {
            InventoryService.Instance.Remove(itemId, 1);
            WillyReputation.Increase(0.05);
        });
    }
}
```

### When Player Meets New NPCs (Tala, Ravi, etc.):

```json
// In dialogue JSON for meeting Tala:
"system_triggers": [
  {
    "type": "unlock_npc_preference",
    "data": [
      "Tala",
      "metal_sheet",
      "insulation",
      "copper_wire"
    ]
  }
]
```

Now Tala automatically queries for those items without dialogue code changes.

---

## 📊 JSON Structure in Beat 2

```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "Willy",
  "prompt_source": {
    "type": "previous_choice_response",
    "beat_id": 1,
    "choice_field": "npc_response"
  },
  "tone_choices": [
    // Four dialogue choices (Trust, Observation, Narrative, Empathy)
    // All converge on same system_triggers
  ],
  "next_beat_id": 3,
  "system_triggers": [
    {
      "type": "unlock_system",
      "data": ["inventory"]
    },
    {
      "type": "unlock_npc_preference",
      "data": [
        "Willy",
        "copper_wire",
        "motor_parts",
        "old_circuitry"
      ]
    },
    {
      "type": "system_notification",
      "data": [
        "Inventory Unlocked",
        "Useful materials can be collected while exploring.",
        "Press I to view your Inventory"
      ]
    }
  ]
}
```

---

## 🎓 Design Philosophy

### Why Beat 2?

| Beat | What Happens | Learning |
|------|--------------|----------|
| 1 | Willy explains he's a scrapper | "This person salvages things" |
| **2** | **Negotiate over metal's value** | **"Things I find have VALUE"** ⭐ |
| 3 | Willy accepts/ignores the metal | Consequence acceptance |
| 4 | Lioren's inner thought | Emotional impact |

Beat 2 is the **moment of realization**. Regardless of which dialogue choice, Lioren has learned: *Things lying around might be useful to someone.*

### Why These Three Triggers?

1. **`unlock_system`** → Makes feature available (technical)
2. **`unlock_npc_preference`** → Teaches the principle (contextual)
3. **`system_notification`** → Explains the UI (UX)

Together: "You learned junk has value. Here's a tool to manage it. Here's how to use it."

---

## ✨ What Makes This Special

### It's Not a Tutorial Dump
❌ **Avoid:** "Welcome to the Inventory System! Here are 10 UI elements..."  
✅ **Instead:** Willy teaches one concept (junk has value); inventory emerges naturally

### It's Diegetic (Part of the Story)
❌ **Avoid:** Menu appears out of nowhere  
✅ **Instead:** Willy's scrapping business makes you rethink the environment

### It Scales Automatically
- Add 50 new metal items → Willy wants them (via tag system)
- Add new NPCs → Each specifies preferences via system triggers
- Add new dialogue → Reuse same trigger types

### It Avoids Tight Coupling
- Dialogue doesn't hard-code inventory behavior
- Inventory doesn't hard-code dialogue behavior
- New systems hook via existing trigger infrastructure

---

## 🚀 Next Steps

1. **Implement ProcessSystemTrigger() in DialogueSystem**
   - Handle `unlock_system`, `unlock_npc_preference`, `system_notification` cases

2. **Create NPCPreferenceManager**
   - Store NPC → List<itemId> mappings
   - Provide Get/Add methods

3. **Create NotificationManager** (or use existing)
   - Show temporary non-blocking notifications
   - Auto-dismiss after duration

4. **Update InventoryService.Start()**
   - Check `system_unlocked_inventory` flag
   - Hide/disable UI if not unlocked

5. **Test in Willy Scene**
   - Play dialogue to Beat 2
   - Verify notification appears
   - Verify inventory UI becomes active
   - Press I → Inventory panel shows (empty, for now)

6. **Place WorldItemPickup in Scene**
   - Collect item → Verify UI updates
   - Verify "Item ×N" notification shows

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [INVENTORY_DIALOGUE_INTEGRATION.md](INVENTORY_DIALOGUE_INTEGRATION.md) | Full technical details |
| [INVENTORY_QUICK_START.md](INVENTORY_QUICK_START.md) | 5-minute setup |
| [INVENTORY_ARCHITECTURE.md](INVENTORY_ARCHITECTURE.md) | Design principles |
| [willy_concourse_ruins_payment.json](C:/saoriverse-console/Velinor-Unity/Assets/Resources/Dialogue/willy_concourse_ruins_payment.json) | Updated dialogue |

---

## 💾 Files Updated

1. ✅ **willy_concourse_ruins_payment.json**
   - Beat 2 now includes three system_triggers
   - Beat 3 prompt_source fixed (references Beat 2, not Beat 1)

2. ✅ **INVENTORY_DIALOGUE_INTEGRATION.md** (New)
   - Complete integration guide
   - Code examples for DialogueSystem, InventoryService, managers
   - Future integration patterns for other NPCs

---

## 🎯 Outcome

Willy is no longer just "NPC that gives you Glyph of Sorrow."

He's **the person who changes how Lioren sees the world**.

Before: *Broken cable = trash*  
After: *Broken cable = someone's livelihood*

And that's not just flavor—it's the entire reason inventory exists in Velinor.

---

**Status: ✅ Ready to implement dialogue triggers in your DialogueSystem**
