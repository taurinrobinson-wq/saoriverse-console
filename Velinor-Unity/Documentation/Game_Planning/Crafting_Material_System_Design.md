# Crafting & Material System Design
## Narrative Integration, Exploration Gating, and Community Building

**Document Purpose**: Define how material collection, crafting, and tool/item usage serve story progression, character relationship building, and community contribution—while remaining a *secondary* mechanic that supports narrative, not the primary gameplay.

**Last Updated**: 2026-11-16
**Design Focus**: Text-based inventory, minimal visual assets, variable NPC interactions, narrative-driven mechanics

---

## Part 1: Design Principles

### Core Philosophy
The crafting and material system exists to serve **three narrative purposes**:

1. **Exploration & Progression Gating** - Tools needed to dismantle barriers, creating curiosity and logical reasons to revisit areas
2. **Community Relationship Building** - Repeated NPC visits, variable donation outcomes, and trading encourages organic relationship deepening
3. **Player Agency & Usefulness** - Lioren becomes a contributing member of the community through tools and care items

### Critical Constraints
- **NOT a survival mechanic** - Player never crafts out of necessity for survival
- **NOT central to gameplay** - Inventory/crafting is secondary to narrative and emotional progression
- **Minimal visual overhead** - Text-only descriptions, no unique inventory item graphics
- **Variable outcomes** - Donations and gifts are unpredictable, mirroring real-world charity dynamics
- **One-time use** - Crafted consumables are used in specific narrative moments, then gone

---

## Part 2: Material Discovery & Visibility Gating

### Core Mechanic: Learning to See
Materials are only collectible **after an NPC teaches Lioren where and how to find them**. Before discovery, they are present in the world but not interactive/visible.

**Discovery Process**:
1. NPC mentions or demonstrates finding material in dialogue
2. Player is "taught" (schematic/knowledge unlock)
3. Material becomes visible/interactable in relevant locations
4. Player can now collect indefinitely from those locations

**Implementation Approach**:
- Material state: `discovered = false` by default
- Triggering event: NPC dialogue + scene flag sets `material.discovered = true`
- In scene: Materials only show interaction prompt when `discovered = true`
- Visual handling: Use interaction glow/highlight rather than pre-placed obvious assets
  - Alternative: Keep material asset invisible until `discovered`, then reveal with glow
  - Avoid: Silhouettes, grayed-out versions, or other obvious pre-placed hints

**Examples**:
- **Herbs** - Sera teaches Lioren to look in forest patches → thereafter herbs glow when player approaches
- **Stone/Copper Wire** - Cal or Veynar mentions where to salvage from ruins → become collectible
- **Bone/Leather** - Korrin shows how to source from slaughter/tanning → unlocks collection from specific location

### No Infinite Respawns
- Once materials are discovered, they respawn slowly or based on time progression
- Prevents "farm one location forever"
- Encourages variety and multiple NPC visits

---

## Part 3: Material Categories & Uses

### Materials (Text-Based Inventory Only)
No unique graphics needed—only narrative descriptions in inventory panel.

| Material | Discovery NPC | Primary Use | Secondary Uses |
|----------|---|---|---|
| **Stone** | Cal or Veynar | Building/reinforcement | Trade for Bits |
| **Copper Wire** | Korrin or Lira | Repair/tools | Trade for Bits |
| **Wood Scraps** | Lira | Crafting/tools | Trade for Bits |
| **Cloth/Leather** | Sealina or Korrin | Bindings/repairs | Trade for Bits |
| **Herbs** | Sera | Healing salve/poultice | Trade for Bits |
| **Bone** | Ravi | Tools/implements | Trade for Bits |
| **Parchment** | Elka | Documentation/writing | Trade for Bits |
| **Glass/Mirror** | Kaelen or Elka | Optical tools | Trade for Bits |

### Material Acquisition Sources
Materials are found in:
- **Ruins & Debris** - Stone, wire, glass (discovered through NPC dialogue)
- **Community Spaces** - Cloth, wood, leather (gifted or found near NPCs' work areas)
- **Nature** - Herbs, bone, plants (discovered through NPC teaching)
- **Archive** - Parchment, documents, old metal (Elka-guided discovery)

### Respawn & Scarcity
- Materials respawn after **in-game time passes** (scene transitions or dialogue)
- Prevents "one-time farm" but ensures availability
- Higher-value materials respawn slower
- Some materials only available after specific NPC interactions

---

## Part 4: Tools & Item Crafting

### Tools (Exploration Gating)
Tools are crafted to dismantle barriers, enabling progression and exploration.

| Tool | Required Materials | Barrier It Dismantles | NPC Teacher | Story Context |
|------|---|---|---|---|
| **Pry Bar** | Stone (1), Metal Scraps (2) | Boarded doors, sealed hatches | Korrin | Exploration into collapsed areas |
| **Cutting Tool** | Metal Scraps (2), Stone (1) | Tangled vines/roots blocking paths | Ravi | Access to overgrown zones |
| **Repair Kit** | Cloth (1), Wire (2), Bone (1) | Broken machinery/mechanisms | Lira | Activate functional devices |
| **Lockpick Set** | Metal Scraps (3), Bone (1) | Locked doors/chests | Kaelen | Hidden locations, secrets |
| **Bridge Builder** | Wood (4), Rope (2), Stone (1) | Collapsed/missing bridges | Veynar | Access across gaps |

**Tool Usage**:
- One-time use in specific scene contexts
- Needed to advance to previously blocked areas
- Discovering a barrier creates curiosity to find the tool
- NPC dialogue naturally guides player toward needing/making tool

**Example Flow**:
1. Player encounters boarded-up building
2. Player is curious, asks NPC about it
3. NPC mentions "you'd need a pry bar to open that"
4. Player gathers materials, crafts pry bar
5. Player can now enter building (and find new materials, NPC, story beats)

### Consumable Items (Care & Aid)
Single-use items crafted by Lioren, used in narrative moments of care and community.

| Item | Required Materials | Used When/Why | NPC Teacher | Story Impact |
|------|---|---|---|---|
| **Healing Poultice** | Herbs (2), Cloth (1) | Injured NPC needs aid; Lioren is hurt | Sera | Shows Lioren's care; NPC remembers her aid |
| **Restorative Tea** | Herbs (1), Stone (1) | NPC is emotionally exhausted | Sera/Elenya | Comfort and presence offering |
| **Calming Tincture** | Herbs (2), Parchment (1) | NPC in emotional distress/panic | Sera | De-escalates scene tension |
| **Binding Cloth** | Cloth (2), Stone (1) | Wrapping wounds or securing items | Korrin | Practical aid in crisis moments |
| **Memory Aid** | Parchment (1), Bone (1) | Helping NPC remember something important | Elka | Triggers memory/story revelation |

**Consumable Usage**:
- Used in dialogue/scene interactions, not combat
- One per craft, one per use (doesn't respawn in inventory)
- Lioren offers them to struggling NPCs
- Usage is optional but opens dialogue/story possibilities

**Example Flow**:
1. Lioren encounters injured Ravi after machinery accident
2. Lioren has Healing Poultice (crafted from Sera's teaching)
3. Lioren offers it in dialogue
4. Ravi is surprised, accepts aid, and reveals story about past injury
5. Later: Ravi mentions this moment, affects relationship tone

### No Armor/Combat Items
- Consumable items are for care and narrative, not combat protection
- Lioren is not fighting enemies; she's part of a community
- Avoids "survival game" feeling

---

## Part 5: Material Trading & The Bits Economy

### Trading System
Lioren can trade materials to NPCs for **Bits** (in-game currency). Each NPC offers different rates based on their specialization.

| NPC | Specialty Materials | Base Rate | Premium Rate | Why They Buy |
|-----|---|---|---|---|
| **Korrin** | Metal, Stone, Bone | 1 material = 1 Bit | +50% (specialist) | Equipment & tools |
| **Sera** | Herbs, Cloth | 1 material = 1 Bit | +50% (specialist) | Medicine supplies |
| **Lira** | Wood, Parchment | 1 material = 1 Bit | +50% (specialist) | Craft materials |
| **Elka** | Parchment, Glass, Metal | 1 material = 1 Bit | +50% (specialist) | Archive restoration |
| **Veynar** | Herbs, Stone, Bone | 1 material = 1 Bit | +50% (specialist) | Healing & building |
| **Ravi** | Bone, Leather, Metal | 1 material = 1 Bit | +50% (specialist) | Hunting equipment |
| **Sealina** | Cloth, Parchment | 1 material = 1 Bit | +50% (specialist) | Textile & records |
| **Generic Merchant** | Any | 1 material = 0.75 Bits | — | Reseller (always available) |

**Mechanics**:
- Lioren can trade with any NPC, but specialists pay more for their specialty materials
- Incentivizes return visits to specific NPCs (trading Bone to Ravi vs generic merchant)
- As relationship improves with NPC, they might offer occasional bonus rates
- Trading is optional—Lioren can also keep materials for crafting

### Why Trade Materials?
Players need Bits to:
- Purchase rare items from merchants
- Pay for services (repairs, information)
- Support NPCs in need (variable outcome—see donation mechanics)
- Access certain areas or events (fees, tolls)

**Example**: 
- Lioren has 10 Bone materials
- Can either: Craft 2 Repair Kits OR trade to Ravi for 15 Bits (at specialist rate)
- If she chooses Bits, she can buy information from Kaelen or repair a community well
- This shapes her journey and relationship priorities

### Trading as Relationship Building
- Repeated visits to trade strengthen NPC familiarity
- Familiar NPCs open up additional dialogue/story
- Trading becomes a "natural" reason to visit regularly
- Each visit is an opportunity for new conversation beats

---

## Part 6: Donation & Charity Mechanics

### Variable Outcome System
When Lioren donates materials or crafted items to struggling NPCs, outcomes are **unpredictable and variable**—mirroring real-world charity dynamics.

### Donation Triggers
Lioren encounters NPCs in need:
- NPC mentions financial hardship, lack of resources, or specific need
- Player can choose to donate materials/items or decline
- Donation is **always optional**

### Possible Outcomes (Variable)

| Outcome | Frequency | Later Impact | Narrative Feel |
|---------|-----------|---|---|
| **Appreciated & Remembered** | 40% | Later: NPC offers gift/aid to Lioren; mentions donation in dialogue | Warm reciprocity |
| **Graciously Accepted** | 35% | Later: NPC acknowledges debt; offers small favor or discount | Quiet gratitude |
| **Accepted Ungraciously** | 20% | Later: NPC accepts but seems resentful; might make snide comment | Uncomfortable reality |
| **Refused** | 5% | Later: NPC refuses, says "I don't need charity"; creates tension | Pride/shame |

**Mechanic**: 
- Outcome determined by NPC personality, current relationship tier, and random seed
- Player never knows outcome in advance
- Encourages authentic generosity (without transaction-mindset)

**Examples**:

*Scenario 1: Lioren gives Herbs to Ravi (who's sick)*
- 40% chance: Later, Ravi hunts extra game and gives Lioren meat
- 35% chance: Ravi thanks her quietly, relationship improves slightly
- 20% chance: Ravi accepts but says "I didn't ask for pity"
- 5% chance: Ravi refuses, saying he'll manage

*Scenario 2: Lioren trades her best Bone materials to help Sera rebuild her shop*
- 40% chance: Sera creates something special and gifts it to Lioren months later
- 35% chance: Sera is grateful, offers Lioren a permanent discount
- 20% chance: Sera accepts but seems uncomfortable receiving aid
- 5% chance: Sera refuses, says she'll earn it herself

### Design Intent
This avoids the "transaction" feeling of "give item → get quest reward". Instead:
- Generosity is **genuine**, not strategic
- Outcomes teach players about real relationships
- Some NPCs are grateful, some are stubborn, some are ashamed
- Reinforces that community isn't transactional

---

## Part 7: Technical Implementation

### UI/UX - Text-Based Inventory
Minimal visual overhead:
1. **Materials Tab** - List with counts and text descriptions
   - Example: "Stone (5) — Grey fragments from collapsed structures"
   - Example: "Herbs (2) — Healing plants from the forest"
2. **Crafting Menu** - Shows recipe, required materials, brief craft description
   - No item graphics, just text
3. **Inventory Display** - Crafted tools/items listed with narrative descriptions
   - Example: "Pry Bar — A makeshift tool for opening blocked passages"
   - Example: "Healing Poultice — A salve for wounds, made with care"
4. **Trade Menu** - Material → NPC → Bits conversion
5. **Donation Prompt** - Offer materials to NPC in need

### Data Structure
**Materials**:
- ID, name, description (text only)
- NPC who teaches it
- Locations where found
- Respawn conditions
- Trade value (Bits)

**Tools/Items**:
- ID, name, type (tool vs consumable)
- Description
- Required materials
- NPC who teaches recipe
- Usage trigger (what scene/condition uses it)
- One-time use flag

**Donations**:
- Donor: NPC
- Item donated: material/item ID
- Outcome table (40% grateful, 35% accepted, 20% ungracious, 5% refused)
- Later impact dialogue

### Save System
Track:
- Materials owned (dictionary: material ID → count)
- Items crafted (list of item IDs with timestamps)
- Donations made (NPC → item → outcome)
- NPCs taught (NPC → list of taught materials/recipes)
- Material respawn timers (location → next respawn time)

---

## Part 8: Player Progression & Discovery Flow

### Early Game (Acts 1-2)
**Focus**: Discovery & light material gathering

**Materials Unlocked**:
- 2-3 basic materials (Stone, Wood, Cloth) through NPC teaching
- Player learns "how to see" through dialogue

**Tools Available**:
- None yet; barriers visible but inaccessible

**Gameplay**:
- Lioren meets NPCs and naturally hears about materials
- First material collection is discovery moment
- No pressure to craft; exploration is optional

### Mid Game (Act 3)
**Focus**: Tool creation for exploration, care item crafting

**Materials Unlocked**:
- 5-8 materials discovered through various NPCs
- Trading becomes available (source of Bits)
- Consumables from care NPCs (Sera, Elenya)

**Tools Available**:
- Pry Bar, Repair Kit crafted from gathered materials
- Each tool opens new area or enables new scene

**Gameplay**:
- Barrier discovery → tool need → material gathering → crafting → exploration
- Early donations to NPCs (variable outcomes experienced)
- Trading materials for Bits if needed

### Late Game (Acts 4-5+)
**Focus**: Deeper storytelling through care, complex donations

**Materials Unlocked**:
- All materials now available
- Rare trades with specialist NPCs
- Consumables used in meaningful story moments

**Tools Available**:
- All tools unlocked and usable
- Exploration complete; focus shifts to narrative

**Gameplay**:
- Crafting consumables to aid injured/struggling NPCs
- Donations become more impactful with deeper relationships
- Trading reflects established NPC connections
- Inventory serves story, not gameplay

---

## Part 9: Example Complete Loop

### Scenario: The Injured Ravi Arc

**Act 2: Setup**
- Ravi is injured or falls ill
- Lioren encounters him struggling
- Ravi mentions needing "something to help with the pain"

**Act 2-3: Gathering**
- Sera teaches Lioren to find Herbs
- Lioren collects Herbs from forest
- Sera teaches Lioren to craft Healing Poultice
- Lioren gathers Cloth from marketplace

**Act 3: Crafting & Offering**
- Lioren crafts Healing Poultice (uses: Herbs, Cloth)
- Lioren visits Ravi and offers the poultice
- Ravi's response is **variable**:
  - 40%: Grateful, later offers Lioren special game meat
  - 35%: Accepts quietly, relationship improves
  - 20%: Accepts grudgingly, mentions he "didn't ask for help"
  - 5%: Refuses, says he'll manage on his own

**Act 4: Story Integration**
- If Lioren gave poultice: Ravi references it during later scene ("You helped me once")
- If Lioren refused: Ravi is distant, Lioren misses dialogue opportunity
- Different outcomes based on donation result, not on crafting

### Scenario: The Blocked Path Arc

**Act 1: Discovery**
- Lioren explores and finds a boarded-up building
- She's curious but can't enter
- She asks Korrin about it; Korrin mentions "you'd need a pry bar"

**Act 2: Learning**
- Korrin teaches Lioren how to make a Pry Bar
- Korrin explains which materials she needs
- Player naturally gathers Stone and Metal Scraps from ruins

**Act 3: Crafting**
- Lioren crafts Pry Bar (uses: Stone, Metal Scraps)
- Lioren returns to boarded building

**Act 3: Exploration**
- Lioren uses Pry Bar to open door
- Discovers hidden NPC or area
- Access to new materials, dialogue, story beats
- **Tool is consumed** (one-time use)

**Later: Relationship Building**
- Lioren later encounters similar locked door
- Needs new Pry Bar (encourages repeat material gathering)
- Or visits Korrin to get advice: "You could make another"
- Trading for Bits becomes alternative option
- Either way, reason to interact with Korrin again

---

## Part 10: Open Design Questions

1. **Material respawn timing**: After how many scenes/time units do materials respawn?
2. **Tool durability**: Do tools break after use, or are they one-time consumables?
3. **NPC biographical expansion**: What story does each NPC reveal on repeat visits? How is this tracked?
4. **Donation memory**: Does an NPC remember multiple donations, or just the most recent one?
5. **Bits economy**: How many Bits does Lioren need? For what services/purchases?
6. **Crafting speed**: Is crafting instantaneous, or does it require time/scene transition?

---

**End of Document**
