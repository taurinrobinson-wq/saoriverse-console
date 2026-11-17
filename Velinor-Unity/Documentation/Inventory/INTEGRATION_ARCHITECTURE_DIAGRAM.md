# Inventory System – Integration Architecture Diagram

## System Communication Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         WILLY DIALOGUE SCENE                               │
│                                                                            │
│  Beat 1: "I'm a scrapper"                                                 │
│  ↓                                                                         │
│  Beat 2: Negotiate over metal ← SYSTEM TRIGGERS FIRE HERE ⭐             │
│  ├─ unlock_system: "inventory"                                           │
│  ├─ unlock_npc_preference: ["Willy", "copper_wire", ...]                 │
│  └─ system_notification: "Inventory Unlocked..."                         │
│  ↓                                                                         │
│  Beat 3: Continuation                                                     │
│  ↓                                                                         │
│  Beat 4: Lioren's inner thought                                          │
│  └─ Dialogue closes                                                       │
└────────────────────────────────────────────────────────────────────────────┘
                                  ↓
                    (System triggers are broadcast)
                                  ↓
         ┌─────────────────────────┼─────────────────────────┐
         ↓                         ↓                         ↓
    ┌─────────────┐          ┌──────────────┐         ┌──────────────┐
    │ GameFlags   │          │ Inventory    │         │ Notification│
    │             │          │ Service      │         │ Manager      │
    │ Set flag:   │          │              │         │              │
    │ "system_    │          │ Checks flag: │         │ Shows:       │
    │ unlocked_   │          │ "system_     │         │              │
    │ inventory"  │          │ unlocked_    │         │ "Inventory   │
    │  = true     │          │ inventory"   │         │  Unlocked"   │
    │             │          │              │         │              │
    │ (Permanent) │          │ If false:    │         │ (4 sec popup)│
    │             │          │ Hide UI      │         │              │
    │             │          │              │         │              │
    │             │          │ If true:     │         │              │
    │             │          │ Show UI      │         │              │
    └─────────────┘          └──────────────┘         └──────────────┘
                                  ↓
                    (Independent systems react)
                                  ↓
                        ┌──────────────────┐
                        │ InventoryUIPanel │
                        │                  │
                        │ CanvasGroup.alpha│
                        │ transitions 0→1  │
                        │                  │
                        │ Player can now:  │
                        │ • Press I        │
                        │ • Open inventory │
                        │ • See items when │
                        │   collected      │
                        └──────────────────┘
```

---

## Three-Stage Player Journey

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: WILLY TEACHES (Now)                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Willy: "I'm a scrapper..."                                            │
│  Lioren: "What do you want?"                                           │
│  Willy: "I'm a scrapper, and you just showed me some niiice scrap."   │
│                                                                         │
│  ← NEGOTIATION ENDS ← Beat 2 Triggers Fire                            │
│                                                                         │
│  🔔 Notification: "Inventory Unlocked"                                │
│                                                                         │
│  Player Learning:                                                       │
│  ✓ "Things I find have value"                                         │
│  ✓ "Junk is someone's livelihood"                                     │
│  ✓ "I can collect and organize items"                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
                    (Player leaves Willy scene)
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: DISCOVERY (Soon)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Player explores Ruins, Concourse, Market...                          │
│  Finds scattered items:                                                │
│    • Copper Wire (x2)                                                 │
│    • Glass Fragments (x3)                                             │
│    • Old Circuit Board (x1)                                           │
│                                                                         │
│  Each collection:                                                       │
│  🔔 Notification: "Copper Wire ×2"                                    │
│                                                                         │
│  Player Learning:                                                       │
│  ✓ "Inventory works"                                                  │
│  ✓ "I can pick up multiple items"                                    │
│  ✓ "Quantities accumulate"                                            │
│                                                                         │
│  UI Update:                                                             │
│  Open Inventory (Press I):                                            │
│    [ Copper Wire ×2     ]                                             │
│    [ Glass Fragments ×3 ]                                             │
│    [ Old Circuit ×1     ]                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
                    (Player returns to Willy)
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: EXCHANGE (Later)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Willy: "Hold up. That wire you've got. You using that?"              │
│                                                                         │
│  System checks:                                                         │
│  • NPCPreferenceManager.Get("Willy")                                   │
│    → ["copper_wire", "motor_parts", "old_circuitry"]                  │
│  • InventoryService.GetAll()                                          │
│    → ["copper_wire": 2, "glass": 3, "circuit": 1]                    │
│  • Intersect: copper_wire ✓                                           │
│                                                                         │
│  Dialogue Options:                                                      │
│  [T] "You can have it."          → Remove 1 copper_wire, +Willy rep  │
│  [O] "What's it to you?"         → Willy explains why                │
│  [N] "I found two. Want both?"   → Remove 2 copper_wire, ++rep       │
│                                                                         │
│  Player Learning:                                                       │
│  ✓ "Different people want different things"                          │
│  ✓ "My choices affect NPC relationships"                            │
│  ✓ "Inventory is a tool for meaningful interaction"                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
                    (Player meets more NPCs)
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 4+: EXPANSION (Ongoing)                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tala: Prefers Metal, Culinary                                        │
│  Ravi: Prefers Electrical, Mechanical                                 │
│  Nima: Prefers Organic, Medical                                       │
│                                                                         │
│  Each NPC unlocked via same system_trigger pattern                    │
│                                                                         │
│  Player discovers:                                                      │
│  ✓ Collecting items is core to building relationships                │
│  ✓ Listening to NPCs reveals what they value                        │
│  ✓ Inventory is about *people*, not just *stuff*                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## System Trigger Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        DIALOGUE JSON                                     │
│                   (willy_concourse_ruins_payment.json)                  │
│                                                                          │
│  "system_triggers": [                                                   │
│    {                                                                     │
│      "type": "unlock_system",                                          │
│      "data": ["inventory"]                                             │
│    },                                                                    │
│    {                                                                     │
│      "type": "unlock_npc_preference",                                  │
│      "data": ["Willy", "copper_wire", "motor_parts", ...]             │
│    },                                                                    │
│    {                                                                     │
│      "type": "system_notification",                                    │
│      "data": ["Inventory Unlocked", "...", "Press I..."]              │
│    }                                                                     │
│  ]                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                  DialogueSystem.ProcessSystemTriggers()                  │
│                                                                          │
│  for each trigger in beat.system_triggers:                             │
│    case trigger.type:                                                   │
│      "unlock_system":                                                   │
│        → GameFlags.Set("system_unlocked_inventory", true)              │
│                                                                          │
│      "unlock_npc_preference":                                          │
│        → NPCPreferenceManager.AddPreferences("Willy", [items])         │
│                                                                          │
│      "system_notification":                                            │
│        → NotificationManager.Show(title, msg, 4f, action)              │
└──────────────────────────────────────────────────────────────────────────┘
                 ↓              ↓              ↓
     ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
     │  GameFlags    │  │NPCPref       │  │Notification      │
     │               │  │Manager       │  │Manager           │
     │  (Persisted)  │  │              │  │                  │
     │               │  │ Willy:       │  │ Shows popup      │
     │ system_unlocked  │  [copper_wire, │  │                  │
     │ _inventory=true  │   motor_parts]│  │ "Inventory       │
     │               │  │              │  │  Unlocked"       │
     │ (stays set)   │  │  (for later  │  │                  │
     │               │  │   queries)   │  │ (auto-dismiss    │
     │               │  │              │  │  after 4 sec)    │
     └───────────────┘  └──────────────┘  └──────────────────┘
           ↓                                       ↓
     Independent systems check this          UI notifies player
     and enable/disable accordingly
```

---

## Future NPC Integration (Same Pattern)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      TALA DIALOGUE JSON                                  │
│              (Some future scene: tala_introduction.json)                 │
│                                                                          │
│  "system_triggers": [                                                   │
│    {                                                                     │
│      "type": "unlock_npc_preference",                                  │
│      "data": [                                                          │
│        "Tala",                                                          │
│        "copper_wire",      ← Prefers electrical                         │
│        "circuit_board",                                                 │
│        "glass",            ← Prefers glass/optical                      │
│        "scrap_metal"       ← Prefers metal                             │
│      ]                                                                   │
│    }                                                                     │
│  ]                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                   ↓
           NPCPreferenceManager stores Tala's preferences
                                   ↓
           Later, when Lioren has copper_wire + circuit:
           
           Dialogue shows: "Give copper wire? Give circuit board?"
           
           No dialogue code changed—same system_trigger pattern
```

---

## Data Flow: Player Returns to Willy with Items

```
Player has:
  • Copper Wire ×2
  • Glass ×3
  • Old Circuit ×1

↓

Dialogue checks:
  playerItems = InventoryService.GetAll()
  willyPrefs = NPCPreferenceManager.Get("Willy")
  
  playerItems: {copper_wire: 2, glass: 3, circuit: 1}
  willyPrefs: [copper_wire, motor_parts, old_circuitry]
  
  match = copper_wire ✓

↓

Dialogue renders option:
  "Give Copper Wire to Willy?"
  
  On accept:
    InventoryService.Remove("copper_wire", 1)
    WillyReputation.Change(+0.05)

↓

Inventory updates:
  OnInventoryChanged("copper_wire", 1)
  ↓
  InventoryUIPanel.HandleInventoryChanged()
  ↓
  UI updates: "Copper Wire ×1"
```

---

## Summary: Three Levels of Integration

### Level 1: System Unlock (Already Done)
```json
{
  "type": "unlock_system",
  "data": ["inventory"]
}
```
Flips a GameFlags switch; InventoryService checks it and enables UI.

### Level 2: NPC Preferences (Already Set for Willy)
```json
{
  "type": "unlock_npc_preference",
  "data": ["Willy", "copper_wire", "motor_parts", "old_circuitry"]
}
```
Registers what an NPC wants; dialogue can query this later.

### Level 3: Player Interaction (Custom per dialogue)
```csharp
// In dialogue response handler:
if (InventoryService.Contains("copper_wire"))
{
    ShowDialogueOption("Give wire?", () => 
    {
        InventoryService.Remove("copper_wire", 1);
        // Trigger quest, reputation, etc.
    });
}
```
Dialogue queries inventory and offers choices.

---

## No Tight Coupling = Clean Expansion

**Adding a new NPC takes:**
1. Create dialogue JSON
2. Add `unlock_npc_preference` trigger with their items
3. Optional: Add custom dialogue response logic

**No changes needed to:**
- InventoryService code
- Dialogue system code
- UI system code
- Any other system

Each system remains independently maintainable.

---

**Architecture: ✅ Complete and ready to implement**
