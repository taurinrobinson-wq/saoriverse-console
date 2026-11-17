# Inventory System + Dialogue Integration

## 🎭 Willy's Narrative Introduction to Inventory

The inventory system is **unlocked narratively** during Willy's payment dialogue, not as a separate tutorial. This allows the mechanic to emerge from the story rather than feel tacked on.

### The Design Principle

> **Willy doesn't give Lioren an inventory. Willy teaches Lioren that junk has value.**

Before meeting Willy:
```
broken cable = debris
```

After meeting Willy:
```
broken cable = possibly useful salvage
```

This is an actual change in Lioren's understanding of the world, and it's why the inventory system makes diegetic sense.

---

## 🔧 How It Works: System Triggers

The dialogue system issues **system_triggers** that wake up other systems without creating tight coupling.

### Beat 2: The Negotiation Concludes

When Lioren and Willy finish negotiating over the metal's value (regardless of which dialogue choice), Beat 2's `system_triggers` fire:

```json
"system_triggers": [
  {
    "type": "unlock_system",
    "data": [
      "inventory"
    ]
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
```

#### Trigger 1: `unlock_system`
**What it does:** Marks "inventory" as unlocked in GameFlags

```csharp
// In DialogueSystem.ProcessSystemTrigger():
case "unlock_system":
    foreach (string system in data)
    {
        GameFlags.Set($"system_unlocked_{system}", true);
    }
    break;
```

**What InventoryService checks:**
```csharp
// In InventoryService.OnEnable() or Start():
if (!GameFlags.Get("system_unlocked_inventory"))
{
    // Disable inventory UI or show "Not Yet" message
    canvasGroup.alpha = 0f;
    canvasGroup.blocksRaycasts = false;
}
```

#### Trigger 2: `unlock_npc_preference`
**What it does:** Registers Willy's item preferences in the NPC system

```csharp
// In DialogueSystem.ProcessSystemTrigger():
case "unlock_npc_preference":
    string npcName = data[0];
    List<string> preferences = data.Skip(1).ToList();
    NPCPreferenceManager.Instance.AddPreferencesForNPC(npcName, preferences);
    break;
```

This allows later dialogue (when Lioren returns to Willy with collected items) to query:
```csharp
var willyPreferences = NPCPreferenceManager.Get("Willy");
// Returns: ["copper_wire", "motor_parts", "old_circuitry"]

// Show dialogue options for matching items
var playerItems = InventoryService.Instance.GetAll();
var willyWants = playerItems.Keys.Intersect(willyPreferences);

foreach (var itemId in willyWants)
{
    ItemDefinition item = ItemDatabase.Get(itemId);
    ShowDialogueOption($"Give {item.DisplayName} to Willy?", () =>
    {
        InventoryService.Remove(itemId, 1);
        // Trigger delivery quest, reputation change, etc.
    });
}
```

#### Trigger 3: `system_notification`
**What it does:** Shows a non-blocking notification to the player

```csharp
// In DialogueSystem.ProcessSystemTrigger():
case "system_notification":
    string title = data[0];
    string message = data[1];
    string action = data.Length > 2 ? data[2] : "";
    
    NotificationManager.Instance.ShowNotification(
        title, 
        message, 
        duration: 4f,
        actionText: action
    );
    break;
```

**Display (approximately):**
```
┌─────────────────────────────────┐
│ Inventory Unlocked              │
├─────────────────────────────────┤
│ Useful materials can be         │
│ collected while exploring.      │
│                                 │
│ Press I to view your Inventory  │
└─────────────────────────────────┘
```

---

## 📊 Dialogue Beat Breakdown

| Beat | Speaker | Purpose | Triggers |
|------|---------|---------|----------|
| 1 | Willy | Intro: "I'm a scrapper" | `update_dialogue_names` |
| 2 | Willy | Negotiation: "So what about that metal?" | **INVENTORY UNLOCK** ⭐ |
| 3 | Willy | Continuation | (prompt from Beat 2's npc_response) |
| 4 | Lioren | Inner thought: "I feel heavy inside" | `glyph_effect`, `diary_append`, `close_dialogue`, `set_flag` |

### Why Beat 2?

**Beat 1** is Willy explaining he's a scrapper. That's information.

**Beat 2** is Lioren and Willy negotiating over whether the metal has value. That's the **moment of realization**: "Oh, things I find *do* matter to people."

All four dialogue choices (Trust, Observation, Narrative, Empathy) lead to the same conclusion: Willy accepts or ignores the metal, but either way, Lioren has learned the principle.

**Beat 3** is a continuation that doesn't strictly matter narratively—it's just acknowledgment.

**Beat 4** is Lioren's internal processing and the scene wrap-up.

---

## 🔄 Multi-Stage Gameplay Integration

### Stage 1: Tutorial (Willy Scene)
- **Unlock:** Inventory system
- **Learn:** Things have value
- **UI:** Shows "Press I to view" notification

### Stage 2: Discovery (First Pickup)
- **Player:** Explores and finds a WorldItemPickup
- **Interaction:** Collects item (copper_wire, glass, etc.)
- **Notification:** Simple notification—"Copper Wire ×2"
- **Learn:** Collecting items works

### Stage 3: Exchange (Returning to Willy)
- **Player:** Has inventory with items Willy wants
- **Dialogue:** Willy notices: "That wire you've got. You using that?"
- **Choice:** Offer to trade/give items
- **Learn:** People want different materials; trading exists

### Stage 4: Expansion (Later NPCs)
- **Player:** Meets Tala, Ravi, others
- **Each NPC:** Has different tag-based preferences
- **System:** Query inventory by tag, offer matching items
- **Learn:** Preferences are universal; any metal item can go to metal-lovers

---

## 🛠️ Implementation Checklist

### DialogueSystem Changes
- [ ] Add `ProcessSystemTrigger()` handler for trigger types
- [ ] Implement `unlock_system` case (GameFlags)
- [ ] Implement `unlock_npc_preference` case (NPCPreferenceManager)
- [ ] Implement `system_notification` case (NotificationManager)

### InventoryService Changes
- [ ] Check GameFlags for "system_unlocked_inventory" on start
- [ ] Disable UI alpha/raycast if not unlocked
- [ ] Show "Inventory not yet available" message if player tries to open

### NPCPreferenceManager (New)
- [ ] Create new ScriptableObject or singleton
- [ ] Store: NPC name → List<itemId> or List<ItemTag>
- [ ] Provide: `Get(npcName)`, `AddPreferences(npcName, items)`

### NotificationManager (New or Existing)
- [ ] Show non-blocking notifications
- [ ] Support title, message, optional action text
- [ ] Auto-dismiss after duration (4 seconds)

---

## 📝 Example: Future Willy Encounter

**Later in the game, Lioren finds copper wire and collects it.**

**Next time she talks to Willy:**

```csharp
// In WillyDialogue.OnStart():
var playerHas = InventoryService.Instance.GetAll();
var willyWants = NPCPreferenceManager.Get("Willy");

if (playerHas.Keys.Intersect(willyWants).Count() > 0)
{
    // Start "trading" branch of dialogue
    dialogue.Play("willy_sees_your_scrap");
}
else
{
    // Start normal greeting branch
    dialogue.Play("willy_hello");
}
```

**Dialogue plays:**
```
Willy: "Hold up. That wire you've got. You using that?"

[Choice 1] "You can have it."
[Choice 2] "What's it to you?"
[Choice 3] "I found two of them. You want both?"
```

**On choice [1]:**
```csharp
InventoryService.Remove("copper_wire", 1);
WillyReputation.Add(0.05);
UnlockDialogue("willy_grateful");
```

---

## 🔌 System Communication (No Tight Coupling)

### Dialogue → Systems
```
Dialogue triggers system_triggers
  ↓
DialogueSystem broadcasts events to all listeners
  ↓
InventoryService, NPCPreferenceManager, NotificationManager each react
```

**No direct call like:**
```csharp
// ❌ AVOID: Tight coupling
InventoryService.Instance.Unlock();
```

**Instead:**
```csharp
// ✅ GOOD: Event-driven
GameFlags.Set("system_unlocked_inventory", true);
// Each system independently checks this flag
```

### Benefits
- Dialogue system doesn't need to know about inventory
- Inventory system doesn't need to know about dialogue
- Each system is independently testable
- New systems can hook into existing triggers without changes
- Easy to add triggers: just add a case in ProcessSystemTrigger()

---

## 📋 JSON Structure Reference

```json
"system_triggers": [
  {
    "type": "unlock_system",
    "data": ["inventory"]
  },
  {
    "type": "unlock_npc_preference",
    "data": ["Willy", "copper_wire", "motor_parts", "old_circuitry"]
  },
  {
    "type": "system_notification",
    "data": [
      "Title Text",
      "Message text with details",
      "Optional action hint like 'Press I'"
    ]
  },
  {
    "type": "set_flag",
    "key": "any_flag_name",
    "value": true
  }
]
```

---

## 🎓 Why This Approach?

### Narrative Benefit
- Inventory isn't a menu item; it's something Lioren *learns* from Willy
- The game doesn't say "Here's an RPG feature"; it says "Willy sees value in scrap"
- By the time inventory UI appears, the player understands *why* it exists

### Technical Benefit
- Dialogue remains a generic trigger system
- New systems can plug in without dialogue code changes
- Inventory can be disabled/hidden without special dialogue logic
- Easy A/B testing: change trigger types, not dialogue code

### Design Benefit
- Tutorial content emerges from story instead of interrupting it
- Player learns through doing (negotiating with Willy, then collecting items)
- Progression feels natural: "Learn → Unlock → Use → Expand"

---

## 🚀 Quick Summary

1. **Beat 2 ends** → Willy accepts/declines the metal
2. **System triggers fire** → Unlock inventory, register preferences, show notification
3. **Inventory system active** → Player can open with I key
4. **First pickup collected** → Simple "Item ×N" notification
5. **Return to Willy later** → He notices what you have; trading dialogue unlocks
6. **Meet new NPCs** → Each has preferences; system scales automatically

**Result:** Inventory feels like part of the world, not a bolted-on menu system.
