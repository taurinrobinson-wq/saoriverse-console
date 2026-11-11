# Scavenging and Skills System

## Purpose

Provide players with a meaningful daily activity loop that reinforces Velinor's core themes: **work gives Lioren a place in the community, trust is built through consistent presence and reliability, and competence grows through practical application.**

The scavenging system transforms exploration into an economic and social activity. Rather than collecting resources abstractly, the player discovers items that specific NPCs need, creating natural opportunities for relationship deepening and backstory revelation.

**Core Design Principle**: Scavenging is not a grinding mechanic—it is a narrative connector that turns Lioren from a stranger into a familiar, dependable presence.

---

## Plan

### Scavenging Loop

```
Explore → Find item → Identify value/preference → Return to marketplace
    ↓
Deliver to NPC → Relationship deepens → Access new dialogue → Unlock skills/tools
    ↓
Use new skill/tool → Access previously blocked areas → Continue exploring
```

### NPC Preferences System

Different NPCs have distinct material preferences tied to their occupations and needs:

- **Tala** (Food preparation, survival): Cookware, containers, heating elements, preserved food, water filtration materials
- **Repair-oriented NPC**: Electrical cable, fasteners, batteries, glass, machine components, metal sheets
- **Craftsperson/Artisan**: Specialized tools, aesthetic objects, rare materials, Old Velharan components
- **Survival-focused NPCs**: Practical containers, preserved goods, medicine components, weatherproofing materials

Each NPC may also value non-practical items with personal or cultural significance—giving the player meaningful choices between utility and emotional connection.

### Relationship Progression (Restrained)

Relationships develop gradually through repeated, meaningful interaction rather than a visible meter:

1. **Recognition**: NPC acknowledges Lioren as a familiar face
2. **Warming Dialogue**: Transactional exchanges become more personal; NPC explains why they need specific items
3. **Small Opportunity**: NPC offers a lesson, minor task, or access privilege (e.g., "Come by before dawn, I'll teach you to prepare this")
4. **Circumstantial Backstory**: Relevant historical or personal details surface naturally through conversation
5. **Trust Marker**: NPC demonstrates trust through a small action (sharing a meal, entrusting Lioren with a task, mentioning family)

**Implementation note**: Progression should remain grounded. After 3-5 successful deliveries, a single dialogue unlock is more appropriate than a major revelation. This preserves narrative subtlety.

### Crafting and Skill System

Crafting remains **narrowly focused on practical competence**, not abstract character progression. Lioren learns occupational skills:

- **Salvage Identification**: Recognize which materials have value and to whom
- **Tool Repair**: Restore damaged or degraded tools to functionality
- **Debris Clearing**: Learn techniques to safely dismantle or bypass obstructions
- **Basic Electrical Work**: Restore simple systems or create makeshift solutions
- **Food Preparation**: Preserve or prepare edible materials (learned from Tala or similar NPC)
- **Medical/Herbal Basics**: Create simple remedies or treatments
- **Material Analysis**: Identify Old Velharan or historically significant components

Each skill is tied to an NPC or occupation and unlocks specific environmental interactions.

### Tool Progression and Environmental Access

Tools enable **Metroidvania-lite progression** without requiring combat:

- **Basic Tools** (Crowbar, Pry Bar): Remove lightweight obstructions, open sealed containers
- **Cutting Tools** (Wire Cutters, Saw): Dismantle cable runs, cut through degraded materials
- **Electrical Tools** (Wire Stripper, Basic Multi-meter): Assess and restore power systems
- **Specialized Tools** (Lockpick, Deactivation Device): Access secured or Old Velhara-sealed areas

Players encounter blocked passages early in the game and naturally remember them later when they acquire the appropriate tool or skill.

---

## Implementation

### Inventory System

**Script**: `InventoryManager.cs`
- Manages item pickup, storage, and removal
- Tracks item quantity and quality
- Exposes simple API: `AddItem()`, `RemoveItem()`, `GetItemCount()`, `GetInventory()`

**UI Component**: `InventoryUI.cs`
- Displays collected items in grid or list format
- Shows item properties (name, category, condition, NPC preferences)
- Allows player to drop, use, or deliver items
- Filters by category (Electrical, Metal, Tools, Food, etc.)

**Data Structure**:
```csharp
[System.Serializable]
public class ItemData
{
    public string itemId;           // "copper_wire", "steel_plate"
    public string displayName;      // "Copper Wire"
    public string category;         // "Electrical", "Metal", "Tool", "Food"
    public string description;      // "Useful for electrical repair and small mechanisms"
    public int quantity;            // Stack count
    public List<string> preferredBy;// NPCs who want this (e.g., ["Tala", "Repair_NPC"])
    public List<string> craftingTags;// ["Conductive", "Flexible", "Recyclable"]
}
```

### NPC Preference and Delivery System

**Script**: `NPCPreferenceManager.cs`
- Stores each NPC's material preferences and rarity tiers
- Tracks delivery history per NPC
- Calculates relationship progression

**Script**: `DeliveryInteraction.cs`
- Attached to NPCs; handles item delivery dialogue
- Checks if delivered item matches NPC preferences
- Increments relationship tracker and unlocks dialogue/rewards

**Dialogue Integration**:
- Deliver preferred item → Unlock new dialogue line
- Deliver non-preferred but usable item → Smaller dialogue unlock
- Deliver preferred rare item → Significant relationship jump

### Crafting and Skill System

**Script**: `SkillManager.cs`
- Tracks learned skills and their mastery level
- Exposes methods: `LearnSkill()`, `HasSkill()`, `CanCraft()`

**Script**: `CraftingUI.cs`
- Displays available recipes based on learned skills
- Shows ingredient requirements and output
- Handles crafting animations/progression

**Skill Unlock System**:
- Skills unlocked through dialogue with specific NPCs
- Example: Deliver 3 food items to Tala → Dialogue option: "Will you teach me?" → Learn Food Preparation skill

### Pickup and Placement Strategy

**Asset Placement**:
- Use Unity Asset Store generic industrial props (cable reels, metal scraps, containers, tools, etc.)
- Place selectively in exploration areas—not overwhelming density, making each find feel significant
- Cluster items thematically (electrical area has more wire and components, food storage areas have containers, etc.)

**Script**: `PickupItem.cs`
- Simple trigger on pickup objects
- Adds item to inventory with `InventoryManager.AddItem()`
- Removes GameObject or plays pickup animation
- Optional: Show item name/preview on interaction prompt

**Placement Patterns**:
- **High-visibility scavenging**: Open areas where items are clearly visible
- **Hidden finds**: Tucked in side passages or behind environmental clutter for completionists
- **Progression markers**: Items placed near blocked areas hint at future access (e.g., wire cutter near a sealed cable run)

### Blocked Area and Tool Integration

**Script**: `EnvironmentalObstacle.cs`
- Defines what tools or skills are required to pass/interact
- Example: `requiredTool = "wire_cutter"` or `requiredSkill = "debris_clearing"`
- Shows feedback to player if they lack the requirement

**Example Blocked Passages**:
- Collapsed metal debris → Requires pry bar and strength
- Sealed electrical panel → Requires wire cutter and electrical knowledge
- Old Velhara lock → Requires specialized deactivation tool

### UI Components

**New UI Panels**:
1. **Inventory Panel**: Accessible from main UI, shows collected items and their properties
2. **Delivery Prompt**: Context-sensitive UI when near an NPC, allows selecting item to deliver
3. **Skill Tree/Learned Skills**: Simple list of acquired skills and their descriptions
4. **Crafting Menu**: Shows available crafts based on inventory and learned skills

---

## Minimum Viable Implementation (First Vertical Slice)

To validate this system before full expansion:

1. **Inventory**: Simple pickup system with 3 item categories (Electrical, Metal, Food)
2. **One NPC with Preferences**: Tala has clear preferences (cookware, food items, containers)
3. **3-4 Scattered Pickups**: Small number of deliberate, readable salvage objects in 1-2 areas
4. **One Learnable Skill**: Food Preparation, taught by Tala after 2 deliveries
5. **One Tool**: Wire cutter to access a previously blocked passage
6. **Dialogue Unlock**: 2-3 additional dialogue lines with Tala triggered by successful deliveries

This proves the loop works before building out multiple NPCs, complex crafting chains, and world-wide item placement.

---

## Future Expansion Points

- Additional NPCs with distinct preferences and skill-teaching capabilities
- Expanded crafting recipes tied to multiple skills
- Tool degradation system (tools wear out, need repair)
- Rare item discovery mechanics (hidden Old Velharan components)
- Trading economy between NPCs (delivery chains)
- Reputation system affecting NPC availability and pricing
