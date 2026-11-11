# Tala's Living Quarters: Visual Reference & Implementation Guide

## Environmental Progression Summary

### Three Connected Spaces

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│          MARKETPLACE RESIDENTIAL STREET (Public)                │
│                                                                 │
│  ┌─────────────────────┐                                        │
│  │   OTHER STALLS      │    [seating area]                      │
│  └─────────────────────┘         │                              │
│                                  │                              │
│  ┌─────────────────────────────────────────┐                    │
│  │     TALA'S STALL                        │                    │
│  │  (cooking, customers, daytime hub)      │                    │
│  └────┬─────────────────────────────────────┘                    │
│       │                                                          │
│       │  Narrow alley (dim, hanging fabric,                     │
│       │  stacked containers, equipment)                         │
│       │                                                          │
│       └──────────────────────┐                                  │
│                              │                                  │
│                    ┌─────────┴──────────┐                       │
│                    │   SIDE DOOR        │                       │
│                    │ (barred early)     │                       │
│                    │ (keyed later)      │                       │
│                    └────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ TRANSITION
         │
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│          TALA'S STALL AFTER CLOSING (Semi-Private)              │
│                                                                 │
│  Canopy down  │  Fire reduced  │  Lights dim  │  NPCs gone      │
│                                                                 │
│  [Tala cleaning, preparing, or sitting]                         │
│  [Player and Tala have personal conversations here]            │
│                                                                 │
│  Location for:                                                  │
│  - Tala's opening vulnerability (Unbarred Door dialogue)        │
│  - Tala's mother's dinner (Barbed Kinship dialogue)            │
│  - Deep conversations without bedroom intimacy                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ PASSAGE
         │
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    REAR LIVING QUARTERS (Private - Progressively Shared)        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  TALA'S SLEEPING AREA                                   │   │
│  │  (personal, private, clearly defined as hers)           │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  LIOREN'S SLEEPING SPACE                                │   │
│  │  (modest, initially temporary-feeling)                  │   │
│  │  (gradually becomes personalized)                       │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SHARED COOKING/HEATING SURFACE                         │   │
│  │  (connected to stall infrastructure)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SHELVES (Tala's private possessions)                    │   │
│  │  (limited, carefully chosen)                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  STORAGE (food, work implements)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  WASH AREA (small, functional)                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Side door back to alley - locked initially, keyed after]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Door State Progression

### Visual States

```
PHASE 1-2: BARRED + LOCKED
┌──────────────────────────────┐
│ ╔═══════════════════════════╗ │
│ ║ ═══════════════════════════ ║ ← HEAVY BAR IN BRACKETS
│ ╠═══════════════════════════╣ │
│ ║  LOCKED DOOR               ║ │
│ ║  (Mechanical Lock)          ║ │
│ ║  [Cannot Interact]          ║ │
│ ║  "The entrance is          ║ │
│ ║   secured from outside."    ║ │
│ ╚═══════════════════════════╝ │
└──────────────────────────────┘

PHASE 3: UNBARRED + LOCKED
┌──────────────────────────────┐
│                              │
│      [BAR RESTS ON GROUND]    │ ← Conspicuous absence
│                              │
│ ╔═══════════════════════════╗ │
│ ║  LOCKED DOOR               ║ │
│ ║  (Mechanical Lock)          ║ │
│ ║  [Can Interact]             ║ │
│ ║  "Open Living Quarters"     ║ │
│ ║  (Lioren has key)           ║ │
│ ╚═══════════════════════════╝ │
└──────────────────────────────┘

PHASE 4-6: UNBARRED + KEYED (Optional Locked or Open)
┌──────────────────────────────┐
│                              │
│      [BAR RESTS ON GROUND]    │
│                              │
│ ╔═══════════════════════════╗ │
│ ║  KEYED DOOR or OPEN         ║ │
│ ║  (Can Enter Freely)         ║ │
│ ║  [Can Interact]             ║ │
│ ║  "Enter Living Quarters"    ║ │
│ ║  (Home is accessible)       ║ │
│ ╚═══════════════════════════╝ │
└──────────────────────────────┘
```

---

## Relationship Phase Visual Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1-2: CUSTOMER & WORKER                                   │
│  Duration: First encounters through regular work                 │
│  Location: Marketplace Stall (daytime)                           │
│  Door State: BARRED + LOCKED                                    │
├─────────────────────────────────────────────────────────────────┤
│  Environmental Cues:                                            │
│  • Barred door visible but unapproachable                        │
│  • Alley is dim, concealed, uninviting                          │
│  • Tala meets player at stall (never invites inside)            │
│  • Relationship is transactional                                │
│                                                                 │
│  Key Dialogue:                                                  │
│  • Tala offers work instead of charity                          │
│  • Player learns food preparation techniques                     │
│  • Tala insists small kindnesses are practical                  │
│                                                                 │
│  Trust Stat: 0.0 → 0.15                                         │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: THE UNBARRED DOOR (GLYPH ENCOUNTER 1)                 │
│  Duration: Single pivotal scene                                  │
│  Location: Tala's Stall → Living Quarters                       │
│  Door State: BARRED → UNBARRED (transition)                     │
├─────────────────────────────────────────────────────────────────┤
│  Dialogue Integration:                                          │
│  • tala_unbarred_door_01.json (Beats 3-5)                       │
│  • Tala's observation: "You're here before I open..."          │
│  • Indirect offer: "If you're going to keep helping..."        │
│  • Lioren accepts the offer                                    │
│                                                                 │
│  Environmental Event:                                           │
│  • Tala walks to side door                                      │
│  • Removes bar from brackets                                    │
│  • Bar rests against wall (permanent change)                    │
│  • Gives Lioren key/access item                                │
│  • Unlock notification: "Living quarters unlocked"              │
│                                                                 │
│  Key Moment:                                                    │
│  • Bar removal happens in silence                               │
│  • Player feels the weight of this gesture                      │
│  • Return to marketplace before new access opens               │
│                                                                 │
│  Stat Changes:                                                  │
│  • Trust: 0.40 → 0.65 (significant jump)                        │
│  • Observation: Player sees Tala's space                        │
│  • Empathy: Player understands what this means                  │
│                                                                 │
│  Flag Set: tala_unbarred_door_complete                          │
│  Glyph Available: Glyph of the Unbarred Door                    │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: AWKWARD COHABITATION                                   │
│  Duration: 7-21+ days of gameplay                               │
│  Location: Living Quarters (primary), Stall (secondary)         │
│  Door State: UNBARRED + LOCKED                                 │
├─────────────────────────────────────────────────────────────────┤
│  Environmental Changes (Visible to Player):                     │
│  • Lioren's sleeping space becomes personalized                 │
│  • Small personal items appear (comb, salvaged object)         │
│  • Tala makes room for Lioren's things                          │
│  • Two areas remain distinct but adjacent                       │
│  • Kitchen/heating surface shows usage from both               │
│                                                                 │
│  Relational Milestones (Small Dialogues):                       │
│  • Tala teaches household expectations                          │
│  • Lioren accidentally uses Tala's private possession          │
│  • Tala expresses mild frustration (tests continue)            │
│  • Lioren notices Tala wakes early                              │
│  • Food set aside for Lioren (care without words)              │
│  • Tala complains about material organization                  │
│  • Lioren checks door; realizes Tala's anxiety                │
│  • Tala asks where Lioren's been (deflected care)              │
│  • Lioren offers Bits; Tala responds based on relationship     │
│  • Tala gives extra storage (active support)                   │
│  • Lioren brings first personal object to display              │
│                                                                 │
│  Possible Disappointments:                                      │
│  • Lioren uses materials Tala was saving                        │
│  • Lioren forgets task or commitment                            │
│  • Lioren late returning, Tala notices                          │
│  → Tala reacts but doesn't break trust                          │
│                                                                 │
│  Stat Progression: 0.65 → 0.85 (slow, steady build)            │
│  Tone: Domestic awkwardness becoming comfortable               │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: BARBED KINSHIP (GLYPH ENCOUNTER 2)                    │
│  Duration: Single scene + aftermath                             │
│  Location: Tala's Stall After Closing (mostly)                 │
│  Door State: UNBARRED + LOCKED (unchanged)                     │
├─────────────────────────────────────────────────────────────────┤
│  Dialogue Integration:                                          │
│  • tala_barbed_kinship_01.json (Beats 1-9)                      │
│  • Tala's mother announced                                      │
│  • Tala confesses: "We haven't spoken in a decade"             │
│  • Lioren asks questions, listens                               │
│  • Mother arrives at marketplace                                │
│  • Awkward dinner conversation                                  │
│  • Conflict: Tala brings up old pain                            │
│  • Mother's surprising gesture: "That was impressive"           │
│  • Tala recognizes the ache can exist without resolution       │
│                                                                 │
│  Environmental Consequence (Subtle):                            │
│  • Extra bowl (mother brought/left something)                   │
│  • Repaired utensil (someone fixed something)                   │
│  • Folded cloth (Tala says she'll "probably donate" - doesn't)│
│  • Recipe note (Tala insists she doesn't need - keeps it)     │
│  • Small ingredient jar or similar (gift from mother)           │
│                                                                 │
│  Key Meaning:                                                   │
│  • These objects persist because Tala doesn't throw them away   │
│  • Not displayed proudly, but not hidden                        │
│  • Room now contains evidence of door opening to past          │
│                                                                 │
│  Relational Shift (Player Experience):                          │
│  • Lioren witnesses Tala's deepest wound                       │
│  • Lioren understands Tala's control came from lack of it      │
│  • Lioren becomes confidant, not just roommate                 │
│  • Relationship transforms from practical to intimate           │
│                                                                 │
│  Stat Changes:                                                  │
│  • Trust: 0.85 → 0.95 (near complete)                          │
│  • Empathy: PEAK (Lioren is now keeper of story)               │
│  • Observation: Lioren understands Tala's entire interior      │
│                                                                 │
│  Flag Set: tala_barbed_kinship_complete                         │
│  Glyph Available: Glyph of Barbed Kinship                       │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 6: SALVAGED INHERITANCE (GLYPH ENCOUNTER 3)              │
│  Duration: Multi-beat scene + aftermath integration             │
│  Location: Marketplace → Communal Cooking Fire                  │
│  Door State: UNBARRED (bar gone), UNLOCKED or OPEN             │
├─────────────────────────────────────────────────────────────────┤
│  Dialogue Integration:                                          │
│  • tala_salvaged_inheritance_01.json (Beats 1-10)              │
│  • Community celebration announced                              │
│  • Tala questions whether her skills are "real inheritance"    │
│  • Preparation: salvaging materials together                    │
│  • Storm hits during preparation (crisis)                       │
│  • Tala panics; thinks she's ruined everything                 │
│  • Lioren reminds Tala: this IS what her parents taught       │
│  • Tala recognizes the wisdom in salvage                        │
│  • Together they salvage the meal                               │
│  • Community eats; success feels earned                         │
│  • Tala: "I'm not undoing them by making it better"           │
│                                                                 │
│  Environmental Transformation (Living Quarters):                │
│  BEFORE:                                                        │
│  • Distinct areas (Tala's side / Lioren's side)                │
│  • Tala's possessions remain off-limits                         │
│  • Clear boundary and hierarchy                                 │
│                                                                 │
│  AFTER:                                                         │
│  • Shared sleeping area (or open door between)                  │
│  • Tala's and Lioren's items mixed                              │
│  • Room decoration emerges organically:                         │
│    ├─ Bed built together                                        │
│    ├─ Willy's salvage (other mentor)                           │
│    ├─ Gift from Ravi or Nima (other friendships)               │
│    ├─ Mother's remnant (family healing)                         │
│    ├─ Tool from work (Lioren's agency)                         │
│    ├─ Personal item from Lioren's past (belonging)             │
│    └─ Player-chosen display objects (agency)                    │
│                                                                 │
│  Linguistic Shifts (Tala's Speech):                            │
│  • "We need more grain"  (not "I need")                        │
│  • "We're opening tomorrow" (not "I'm opening")                │
│  • "Our home" (said without correction)                        │
│  • "This is what we created" (joint authorship)               │
│                                                                 │
│  Community Integration:                                        │
│  • Lioren takes turns opening/closing stall                     │
│  • NPCs refer to Lioren as "Tala's" (belonging)                │
│  • Tala introduces Lioren as partner                            │
│  • Community treats them as unit                                │
│  • Tala invites others into living quarters                     │
│                                                                 │
│  Stat Changes:                                                  │
│  • Trust: 0.95 → 1.0 (complete)                                │
│  • Observation: Lioren knows all of Tala                        │
│  • Empathy: TRANSCENDENT (can predict Tala's needs)            │
│  • Narrative: Lioren is now co-author of the story              │
│                                                                 │
│  Relationship Tag: best_friend                                  │
│  Flag Set: tala_salvaged_inheritance_complete                   │
│  Glyph Available: Glyph of Salvaged Inheritance                 │
│  Milestone: "Lioren has a home"                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Object Persistence Guide

### Mother's Remnant Objects

These appear after tala_barbed_kinship_01 completes:

```
Object 1: EXTRA BOWL
├─ What it is: Bowl from mother's visit or new one mother brought
├─ Where stored: Shelf or near cooking area
├─ Lioren can interact with: No (decorative/environmental)
├─ Meaning: Mother participated in this space
└─ Visual cue: Different style (pre-collapse craftsmanship?)

Object 2: REPAIRED UTENSIL
├─ What it is: Something broken, fixed during mother's visit
├─ Where stored: Cooking area, prominently used
├─ Lioren can interact with: Potentially (use while cooking)
├─ Meaning: Someone who cared about the tool repaired it
└─ Visual cue: Repair visible (different materials, neat stitching)

Object 3: FOLDED CLOTH
├─ What it is: Cloth from mother, folded neatly
├─ Where stored: Shelf (not hidden, not displayed)
├─ Lioren can interact with: No
├─ Meaning: Tala keeps it even though she "doesn't need it"
└─ Visual cue: Faded, well-used, clearly old

Object 4: RECIPE NOTE
├─ What it is: Written recipe from mother (maybe requested by mother)
├─ Where stored: Near cooking area, tucked but visible
├─ Lioren can interact with: Can read (dialogue option)
├─ Meaning: Tala insists she doesn't need it, but keeps it
└─ Visual cue: Handwriting, worn paper (real history)

Object 5: INGREDIENT JAR
├─ What it is: Specific ingredient mother brought
├─ Where stored: Storage shelf with other ingredients
├─ Lioren can interact with: Can ask about it
├─ Meaning: Mother gave something practical
└─ Visual cue: Special (not marketplace standard)
```

### Player-Influenced Objects (Phase 4-6)

These appear based on player choices:

```
LIOREN'S FIRST PERSONAL OBJECT
├─ Trigger: Player chooses to display something during Phase 4
├─ Location: Lioren's sleeping area (visible)
├─ Meaning: First permanent mark of Lioren's presence
└─ Example: salvaged mirror, carved object, written journal

BED BUILT WITH TALA
├─ Trigger: Late Phase 4 or early Phase 5
├─ Location: Lioren's sleeping area
├─ Meaning: Practical support, collaborative work
├─ Interaction: Can examine ("Tala helped me build this")

WILLY'S SALVAGE GIFT
├─ Trigger: After Lioren trades with Willy multiple times
├─ Can add to living quarters: Yes (player choice)
├─ Meaning: Other relationships integrated into shared home
├─ Example: Useful tool, decorative salvage, practical item

GIFT FROM RAVI OR NIMA
├─ Trigger: After Lioren befriends other NPCs
├─ Can add to living quarters: Yes (player choice)
├─ Meaning: Tala accepts Lioren's full social world
├─ Example: Food, clothing, craft item, token of friendship

ITEM FROM LIOREN'S PAST
├─ Trigger: Player-carried item from beginning of game
├─ Location: Displayed on shelf or personal space
├─ Meaning: Lioren's past integrated into present life
├─ Example: Family heirloom, journal, personal keepsake

PLAYER-CHOSEN DISPLAY OBJECTS (1-2 maximum)
├─ Trigger: Lioren can choose from collected objects
├─ Limit: Don't overwhelm room with player customization
├─ Meaning: Player agency in home-building
└─ Example: 2-3 objects selected from larger inventory
```

---

## Sound & Atmosphere Guide

### Marketplace Residential Street
- **Morning:** Birds, distant community activity, water sounds, tools being moved
- **Midday:** Cooking sounds, customer voices, Tala's occasional greetings, marketplace bustle
- **Evening:** Reduced activity, wind through alley, Tala cleaning, ambient neighborhood sounds

### Alley
- **Early Game:** Creaking, wind, muffled voices from marketplace, sense of isolation
- **After Unbarring:** Same sounds, but less menacing (familiarity changes perception)
- **Consistent:** Fabric rustling, container shifting, footsteps echoing

### Stall After Closing
- **During Cleanup:** Scraping, water, organized settling, wind in canvas
- **Evening Conversation:** Tala's voice, ambient marketplace fade, intimate scale
- **Mother's Dinner:** Tension, careful movements, meaningful pauses

### Living Quarters
- **Daily:** Cooking, heating sounds from shared surface, water use, footsteps
- **Morning:** Tala awake early (to-do sounds), later Lioren waking
- **Evening:** Quiet, reflective, food preparation, occasional conversation
- **After Barbed Kinship:** Mother's dinner ambience lingers (slightly sadder tone)
- **Phase 6:** Joint routines (synchronized sounds, comfort)

---

## Implementation Checklist

### Environmental Assets Needed

```
MARKETPLACE RESIDENTIAL STREET:
☐ Marketplace street background (day state)
☐ Marketplace street background (evening state)
☐ Tala's stall structure (closed canopy state)
☐ Tala's stall structure (open canopy state)
☐ Alley transition zone
☐ Narrow alley background
☐ Decorative elements (containers, fabric, equipment)

TALA'S STALL AFTER CLOSING:
☐ Stall interior variant (after closing appearance)
☐ Lighting adjustment (evening/night)
☐ Optional: Interior setting for evening conversations

REAR LIVING QUARTERS:
☐ Living quarters background
☐ Sleeping area division visual
☐ Storage shelf structure
☐ Cooking/heating surface
☐ Wash area structure
☐ Door to alley (showing lock mechanism)

DOOR MECHANICS:
☐ Bar asset (removable, can rest on ground)
☐ Bar bracket assets
☐ Locked door appearance
☐ Keyed/open door appearance
☐ Key item sprite
☐ Transition animation (bar removal)
```

### Mother's Visit Assets

```
☐ Tala's Mother character design
☐ Mother's portrait expressions (uncertain, pained, gentle, peaceful)
☐ Bowl/artifact to leave behind
☐ Repaired utensil (damaged vs. repaired states)
☐ Cloth item
☐ Recipe note (readable item)
☐ Ingredient jar
```

### Object Placement System

```
☐ Object persistence script (objects remain after phase transition)
☐ Room state variation system (Phase 4 vs Phase 6 appearance)
☐ Player-choice storage for selected display objects
☐ Interaction system for examining room objects
☐ Dialogue triggers for object-related conversations
```

### Dialogue Triggers

```
☐ Small dialogue system for Phase 4 cohabitation scenes
☐ Living quarters scene variations (morning, evening, after visiting)
☐ Tala speaking about shared possessions ("our home" language)
☐ Optional: Mother reflections (Tala thinking about visit)
└─ These can be ambient/optional, not required for progression
```

---

## Testing Checklist

```
PHASE 1-2 VERIFICATION:
☐ Barred door visible in alley
☐ Door interaction shows "secured from outside" message
☐ Tala meets player only at stall
☐ Regular work conversations available
☐ Relationship trust builds steadily

PHASE 3 TRANSITION:
☐ Unbarred Door dialogue triggers properly
☐ Bar removal animation plays (or player sees static result)
☐ Bar visibly rests on ground (environmental change)
☐ Door now has "Enter Living Quarters" interaction
☐ Key/access item given to player
☐ Living quarters becomes accessible home base

PHASE 4 EXPERIENCE:
☐ Small dialogues available in living quarters
☐ Lioren's objects can be examined
☐ Room changes visually (objects appear)
☐ Disappointment mechanic works (trust can go down slightly)
☐ Recovery from disappointment (trust rebuilds)
☐ Tala's routines observable (early rising, etc.)

PHASE 5 TRANSITION:
☐ Barbed Kinship dialogue triggers after N days
☐ Mother's visit happens at stall or living quarters
☐ Mother's objects appear and persist in room
☐ No cleanup of mother's items (they stay)
☐ Tala's emotional state affected by visit
☐ Lioren can offer comfort or space

PHASE 6 FULL INTEGRATION:
☐ Salvaged Inheritance dialogue triggers
☐ Community celebration event occurs
☐ Storm forces salvage situation
☐ Tala's realization moment lands emotionally
☐ Living quarters feels fully shared
☐ "We" language from Tala appears
☐ Other NPCs can visit (optional scenes)
☐ Relationship tag shows "best_friend"
```

---

## Player Experience Arc

```
START: "That door is barred. I wonder what's behind it."
PHASE 1-2: "I work for Tala. She's practical, kind in her way, but distant."
PHASE 3: *sees bar being removed* "She's letting me in. This matters."
PHASE 4: *living in her space* "I'm learning her routines, her fears, her humor."
PHASE 5: *mother arrives* "I see where Tala's walls come from. She's carrying so much."
PHASE 6: *community celebration* "Tala's not alone anymore. Neither am I."

FINAL STATE: "This is home. This is where I belong. This is where we belong."
```

The door that was barred becomes a threshold.
Not a barrier, but a place where two lives merge.
Where belonging is earned through trust, tested through cohabitation, and cemented through witnessing.

*That's the story the space tells.*
