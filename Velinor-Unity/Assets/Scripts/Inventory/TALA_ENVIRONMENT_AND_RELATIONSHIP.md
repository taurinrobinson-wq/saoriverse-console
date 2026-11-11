# Tala's Living Quarters: Spatial Narrative & Relational Progression

## Overview: The Door as Storytelling Medium

The entrance to Tala's living quarters tells the story of her relationship with Lioren without a single line of dialogue:

```
Phase 1: BARRED
├─ Message: "This is Tala's. You are not Tala."
├─ Player perception: Private, closed, unapproachable
└─ Interaction: Cannot interact beyond observing

Phase 2: UNBARRED, LOCKED
├─ Message: "I've chosen to trust you with access."
├─ Player perception: Private, but now shared with someone
└─ Interaction: Player receives key/access item

Phase 3: UNLOCKED, POSSESSIONS APPEAR
├─ Message: "You belong here. This is becoming yours too."
├─ Player perception: Shared home emerging
└─ Interaction: Player stores items, decorates within limits

Phase 4: OTHERS INVITED IN
├─ Message: "I'm allowing my life to be witnessed."
├─ Player perception: Tala is integrating Lioren into community
└─ Interaction: Scene variations show visitors

Phase 5: FULLY SHARED
├─ Message: "We are building a home together."
├─ Player perception: This is both women's space
└─ Interaction: "We" language, joint decision-making
```

---

## Three Physical Spaces: Layout & Narrative Function

### Space 1: Marketplace Residential Street (Exterior)

**What the player sees:**
- Tala's stall on the left side of residential market street
- Seating/standing area where people eat during market hours
- Narrow, dim alley immediately beyond stall
- Alley partially concealed by: hanging fabric, stacked containers, stall equipment
- Barred side door visible at back of alley (early game)
- Signs of residential life: laundry, water containers, improvised doors, personal objects

**Narrative Function:**
- Establishes where Lioren first meets Tala
- Shows the barred door as an unresolved spatial mystery
- Creates visual hierarchy: marketplace is public, alley is liminal, door is private
- Player naturally observes the barrier and wonders what's behind it

**Phase Progression:**
```
Phase 1-2: Barred door visible, unapproachable
├─ Alley is atmospheric (mysterious, off-limits)
├─ Player may interact with door prompt: "The entrance is secured from outside."
└─ Tala appears here during market hours for regular interactions

Phase 3+: Bar removed in silent scene
├─ Door remains locked but bar is conspicuously absent
├─ First major visual cue that relationship has shifted
├─ Alley becomes accessible (less threatening, still private)
└─ Side door now has "Enter Living Quarters" prompt
```

**Key Design Principle:**
Don't make the alley completely hidden. Let the player notice it before gaining access. The unresolved possibility becomes earned access.

---

### Space 2: Tala's Stall After Closing (Transitional)

**What the player sees:**
- Same background as marketplace street, but in different state
- Canopy partially closed or adjusted
- Cooking fire reduced to embers
- Fewer NPCs or none
- Cooler ambient lighting (evening/night)
- Tables and implements moved slightly
- Residential lights visible behind stalls
- Tala cleaning, preparing, or simply sitting
- Atmosphere: end of work day, private time beginning

**Narrative Function:**
- Space where serious conversations can happen without bedroom intimacy
- Represents transition between public (marketplace) and private (quarters)
- Allows for tonal shifts (tired, vulnerable, thoughtful)
- Perfect venue for Barbed Kinship dialogue (mother's dinner)

**Phase Progression:**
```
Phase 1-2: Player joins Tala for work conversations
├─ Still feels like workplace, just quieter
├─ Tala is accessible but professional
└─ Topics: ingredients, techniques, expectations

Phase 3-4: Personal conversations begin
├─ Player sits with Tala after customers leave
├─ Tala discusses her mother, her past, her fears
├─ Still technically workplace, but emotionally intimate
└─ Bridge between "we work together" and "we live together"

Phase 5: Extended cooking time together
├─ Collaborative preparation for community events
├─ Joint decision-making about the stall's future
├─ Reminiscing about earlier phases
└─ "Remember when you didn't know which grain was safe?"
```

**Dialogue Integration:**
- **Tala_Unbarred_Door Beat 1-2:** Daytime stall work (Phase 1-2)
- **Tala_Barbed_Kinship Beat 1:** Evening stall conversation (Phase 3-4)
- **Tala_Barbed_Kinship Beats 3-7:** Mother's dinner (Phase 4)
- **Tala_Salvaged_Inheritance Beat 1:** Discussion about community celebration (Phase 4-5)

---

### Space 3: Rear Living Quarters (Interior)

**What the player sees:**

Initial state (Phase 1-2):
- Unmistakably Tala's space into which Lioren has been accommodated
- Functional, not decorative
- Small cooking/heating surface (shared with stall infrastructure)
- Tala's sleeping area (clearly defined as hers)
- A modest second sleeping space prepared for Lioren
- Shelves with Tala's private possessions (limited, carefully chosen)
- Storage for food and work implements
- Small wash area
- Side door back to alley (locked initially, then keyed)
- Secured storage if needed

Later state (Phase 4-5):
- Subtle signs that Lioren inhabits the space
- Her storage area established
- One or two personal objects visible
- Evidence of shared routines (both women's tools)
- Gradually becomes "our space" rather than "Tala's space"

**Narrative Function:**
- Visual record of relationship progression
- Player sees, not tells, how intimacy develops
- Anchors abstract dialogue moments in physical reality
- Becomes safe space where Lioren processes other relationships

**Design Principle:**
Let the room subtly change rather than the player actively "decorating." Changes are driven by relational progress, not by free-form player design.

---

## Six Phases of Relationship Development

### Phase 1: Customer and Unfamiliar Newcomer

**Context:** Before housing is offered

**Dialogue Integration:**
- **tala_unbarred_door_01.json, Beat 1-2** occurs here
- Tala offers work instead of charity
- Player learns food preparation

**Environmental Details:**
- Player encounters Tala only at her stall
- Cannot access alley or rear quarters
- Barred door is visible but unreachable
- Interaction: "The entrance is secured from outside."

**Relational Milestones:**
```
- Lioren asks what food costs
- Tala notices Lioren has little money
- Tala offers minor stall work instead of charity
- Lioren learns which scavenged ingredients are safe
- Tala corrects her food preparation technique
- Lioren observes Tala saving portions for people who cannot pay
- Tala insists this is inventory management, not generosity
```

**NPC Stat Progression:**
- Trust: builds slowly (0.0 → 0.15)
- Observation: Lioren notices Tala's patterns
- Empathy: Lioren begins understanding Tala's reality
- Narrative: Lioren hears Tala's history in fragments

**Scene Variations:**
- Morning: Tala setting up (task-focused)
- Midday: Tala rushing between customers (efficient)
- Evening: Tala cleaning up (tired but satisfied)

---

### Phase 2: Worker and Reliable Familiar Face

**Context:** Lioren begins helping regularly; relationship becomes real

**Dialogue Integration:**
- Willy dialogue completes (Lioren has inventory, can trade)
- Lioren spends more time at stall
- Small conversations embedded in work

**Environmental Details:**
- Alley is now part of regular path (to/from stall)
- Barred door becomes familiar landmark (raises questions)
- Player may interact multiple times: "Still secured."
- Tala's space (behind stall) remains inaccessible but less mysterious

**Relational Milestones:**
```
- delivering ingredients from marketplace
- cleaning the stall (trusted with Tala's tools)
- sorting salvage (learning her standards)
- preparing simple food (gaining competency)
- carrying water (basic partnership)
- covering the stall briefly (high trust moment)
- remembering a regular customer's preference (integration)
- noticing when Tala is exhausted (empathy deepens)
```

**Relational Reality - Disappointment:**
```
Player can now disappoint Tala in small ways:
- Using materials Tala expected delivery for
- Arriving without something promised
- Prioritizing another NPC's need over stall work
- Forgetting a customer's preference
- Being late or careless

Tala doesn't treat this as betrayal, but she notices.
She might respond with mild disappointment or redoubled testing.
Their relationship becomes real because it's not built entirely from success.
```

**NPC Stat Progression:**
- Trust: builds steadily (0.15 → 0.40)
- Observation: Lioren knows Tala's rhythms
- Empathy: Lioren understands Tala's need to control space
- Narrative: Lioren hears deeper history (parents, caves, survival)

**Scene Variations:**
- Tala teaching (patient, focused on Lioren's learning)
- Tala testing (watching to see if Lioren remembers)
- Tala tired (rare vulnerability)
- Tala satisfied with Lioren's work (subtle approval)

---

### Phase 3: The Unbarred Door

**Context:** Tala discovers Lioren lacks shelter; dialogue trigger

**Dialogue Integration:**
- **tala_unbarred_door_01.json, Beats 3-5** occurs here
- Tala observes: "You're here before I open and still hanging around when I close."
- Offer is indirect: "If you're going to keep helping, you may as well stop wasting time."
- Lioren recognizes the offer without forcing Tala to name it

**Environmental Events:**
```
Dialogue ends → Screen fades slightly
Tala walks to side door
Player sees her reach into brackets
She removes the heavy bar
Sets it against the wall (visible but no longer blocking)
She turns and hands something to Lioren
(key, salvaged keycard, or simple latch device)
Screen fades back

System prompt appears:
"Living quarters unlocked"
"Tala has given Lioren access to the room behind the cookstall."
```

**Critical Design Note:**
- Don't show "Press E to enter your new home!" immediately
- Let the removal of the bar breathe for a few seconds
- The interaction prompt should feel earned, not rushed
- Return to marketplace street so player must choose to approach the now-accessible door

**Environmental Consequence:**
```
BEFORE (Phase 1-2):
- Alley: dim, concealed, unapproachable
- Door: barred, locked, hostile

AFTER (Phase 3):
- Alley: still private, but no longer forbidden
- Door: unbarred, locked (keys matter now)
- Bar: resting against wall (permanent reminder of barrier removed)
- New interaction: "Enter Living Quarters" appears when player approaches
```

**NPC Stat Progression:**
- Trust: significant jump (0.40 → 0.65)
- Observation: Lioren sees Tala's private space
- Empathy: Lioren understands what this means
- Narrative: Lioren becomes part of Tala's story

**Glyph Mechanics:**
- Glyph of the Unbarred Door becomes available for unlock
- Unlocks when: player accepts the offer (any tone choice)
- Narrative consequence: "Lioren has accepted Tala's trust"
- Flag set: "tala_unbarred_door_complete"

---

### Phase 4: Awkward Cohabitation

**Context:** After Lioren moves in; relationship becomes domestic and complex

**Dialogue Integration:**
- Small, frequent dialogues in living quarters
- Topics: expectations, privacy, habits, care
- Tala complains about small things (shows comfort, not hostility)
- Lioren navigates shared space boundaries

**Environmental Details:**
- Living quarters now accessible after each stall close
- Visual changes emerge: Lioren's sleeping space becomes personalized
- Two separate areas (Tala's private section, Lioren's accommodation)
- Evidence of cohabitation: water used, food prepared, tools moved

**Relational Milestones:**
```
- Tala communicates household expectations (quiet after certain hour, etc.)
- Lioren accidentally uses something Tala considers private (reaction: mild frustration)
- Tala gets up much earlier than Lioren (discovered through ambient events)
- Lioren returns late and finds food set aside without comment (care expressed indirectly)
- Tala complains about Lioren leaving salvaged materials in wrong place (still teaching)
- Lioren notices Tala checks the door more than once before sleeping (reveals anxiety)
- Tala asks where Lioren has been, then insists she was only asking about work (deflected care)
- Lioren offers Bits for lodging; Tala reacts based on relationship development (acceptance/refusal)
- Tala gives Lioren additional storage after pretending she merely needs space (active support)
- Lioren brings home an object for the room, creating first visible mark of her presence
```

**Spatial Progression:**
```
Day 1-7 (Arrival):
├─ Lioren's sleeping space is bare, temporary
├─ Tala shows where to store things
├─ Clear demarcation: "This is yours" / "This is mine"
└─ Tala maintains control of most shared surfaces

Day 8-21 (Settlement):
├─ Lioren leaves personal items (comb, salvaged item, clothing)
├─ Tala neither removes nor comments on them
├─ Subtle: things move to make room
├─ Tala begins asking Lioren opinion ("Should we...?")
└─ First time Tala says "we"

Day 22+ (Integration):
├─ Lioren's space shows personality
├─ Objects from other relationships appear (Willy's salvage, Nima's gift)
├─ Shared spaces reflect both women's presence
├─ Tala treats Lioren's space as off-limits to her (parallel respect)
└─ Morning routines become synchronized
```

**NPC Stat Progression:**
- Trust: deepens (0.65 → 0.85)
- Observation: Lioren understands Tala's need for control, privacy, ritual
- Empathy: Lioren recognizes Tala's trauma around shared space
- Narrative: Lioren becomes keeper of Tala's secrets

**Scene Variations:**
- Morning (Tala already up, coffee/meal preparing)
- Evening (Tala processing the day's work, reflective)
- Weekend (Tala resting, slightly less guarded)
- After community event (Tala discussing people, more open)

---

### Phase 5: Barbed Kinship

**Context:** Tala's mother arrives; relationship becomes tested and deepened

**Dialogue Integration:**
- **tala_barbed_kinship_01.json, Beats 1-9** occurs here
- Tala's mother visits marketplace
- Dinner happens (location: Tala's Stall After Closing, or perhaps in living quarters)
- Conversation about past, survival, inherited pain
- No resolution, but acknowledgment

**Environmental Consequence:**
```
After mother's visit, living quarters shows physical evidence:
- An extra bowl (mother brought something)
- A repaired utensil (someone fixed Tala's thing)
- A folded cloth Tala claims she'll "probably donate" (but doesn't)
- A recipe note "just in case" (Tala insists she doesn't need it)
- A small ingredient jar (gift from mother)

These objects persist because Tala doesn't throw them away.
They're not displayed proudly, but they're not hidden.
The room now contains physical evidence that the door opened briefly to someone from Tala's past.
```

**Relational Shifts:**
```
Before mother's visit:
- Lioren has witnessed Tala's competence and care
- Lioren trusts that Tala can handle anything
- Relationship feels stable and reliable

After mother's visit:
- Lioren has seen Tala's wounds
- Lioren understands Tala was once a child who needed things
- Lioren recognizes that Tala's control is born from lack of it
- Relationship is no longer just partnership; it's witnessing

Consequence:
- Lioren's empathy deepens (Observation stat increases)
- Lioren may offer comfort without words (small gestures matter)
- Tala allows Lioren to see her exhausted, sad, conflicted
```

**NPC Stat Progression:**
- Trust: exceptional (0.85 → 0.95)
- Observation: Lioren understands Tala's entire interior landscape
- Empathy: Peak (Lioren becomes confidant, not just roommate)
- Narrative: Lioren is now keeper of Tala's family story

**Scene Variations:**
- During mother's visit (tension, awkwardness, careful civility)
- After mother leaves (quiet processing, vulnerability)
- Next morning (Tala acting normal, but Lioren knows better)

---

### Phase 6: Shared Home and Community

**Context:** After Salvaged Inheritance dialogue; Tala fully integrates Lioren

**Dialogue Integration:**
- **tala_salvaged_inheritance_01.json, Beats 3-10** occurs here
- Community celebration, storm, salvage
- Tala recognizes her inheritance as gift, not burden
- Lioren becomes visible partner in Tala's work

**Environmental Details:**

Living Quarters Transformation:
```
BEFORE (Phase 4-5):
- Tala's side: personal, controlled, private
- Lioren's side: guest space with personality
- Tala's things: off-limits to Lioren
- Distinction: clear boundary

AFTER (Phase 6):
- Shared sleeping area (or adjacent, door between can be left open)
- Joint storage (Tala's things and Lioren's things mixed)
- Tala invites other NPCs inside (Willy, Nima, Ravi)
- Visible representations of both women's relationships
- Decoration emerges organically:
  ├─ A bed Tala helped Lioren build
  ├─ An object Willy made from salvage
  ├─ Something Ravi or Nima gave Lioren
  ├─ An item connected to Tala's mother (kept now, not hidden)
  ├─ A tool representing Lioren's first stable work
  ├─ Something personally connected to Lioren's parents
  └─ 1-2 objects the player consciously chose to display
```

Marketplace Changes:
```
- Lioren takes turns opening/closing the stall
- Marketplace NPCs refer to Lioren as "Tala's" (belonging, not possession)
- Tala introduces Lioren to people: "This is Lioren, she works with me"
- Community treats them as unit
```

**Linguistic Shifts (Subtle but Powerful):**
```
BEFORE:
Tala: "I need more grain."
Tala: "I'm opening the stall tomorrow."
Tala: "I'll prepare the food."

AFTER:
Tala: "We need more grain."
Tala: "We're opening the stall tomorrow."
Tala: "We'll prepare the food."
Tala: "Our home" (without correcting herself)
```

**NPC Stat Progression:**
- Trust: complete (0.95 → 1.0)
- Observation: Lioren knows Tala's rhythms, history, unspoken needs
- Empathy: Transcendent (Lioren can predict Tala's responses)
- Narrative: Lioren is now author of her own story alongside Tala's

**Relational Milestones:**
```
- Tala asks Lioren's opinion about stall decisions
- Tala entrusts her with valuable ingredients
- Tala allows Lioren to share private possessions
- Tala allows others inside their home
- Tala makes room for objects meaningful to Lioren
- Tala gives Lioren responsibility for opening/closing stall
- Tala refers to living quarters as "home" without correction
- Tala introduces Lioren to new people as someone she trusts
- Tala admits when she's wrong or needs help
- Tala plans future with Lioren ("When we expand the stall...")
```

**Scene Variations:**
- Morning: Coordinated routines, shared coffee
- Evening: Joint reflection on the day's work
- Community events: Tala and Lioren as visible partners
- Quiet moments: Tala reading or working, Lioren nearby (comfortable silence)

---

## The Room as Relationship Record

### What Objects Mean

Each object in the living quarters represents a choice and a relationship:

```
Bed Tala helped build
├─ Built together after Lioren moved in
├─ Represents: practical trust, shared work, care expressed through making
└─ Meaning: Tala invested physical effort in Lioren's comfort

Object from Willy
├─ Salvaged item Willy made or repaired
├─ Represents: connection to marketplace work, respect from other mentor
└─ Meaning: Tala permits display of other relationships in their shared home

Gift from Ravi or Nima
├─ Something from Lioren's other friendships
├─ Represents: Tala accepts Lioren's full social world
└─ Meaning: Home isn't Tala's private fortress anymore; it's Lioren's intersection point

Item from mother's visit
├─ Bowl, cloth, recipe, ingredient jar
├─ Represents: Tala's willingness to keep piece of painful relationship
└─ Meaning: Tala's past is no longer sealed off; Lioren witnesses it

Tool from first stable work
├─ Something Lioren used during Phase 2-3 work
├─ Represents: Lioren's agency, skill, independence
└─ Meaning: Room contains evidence of Lioren's becoming, not just belonging

Personal connection to Lioren's parents
├─ Chosen by player (what Lioren brought to Velinor)
├─ Represents: Lioren's past integrated into present
└─ Meaning: Tala holds space for Lioren's grief without judgment

Player-chosen display
├─ 1-2 items player specifically decides to display
├─ Represents: Player agency in building the home
└─ Meaning: This is collaborative curation, not imposed aesthetics
```

### The Room Tells Different Stories

Different players' rooms will look different because players made different choices:

**Player A's room** (focused on work):
- Bed, various tools, salvage items, community gifts
- Story: "This is where I sleep between work shifts. My life is built on creating and solving."

**Player B's room** (focused on relationships):
- Bed, gifts from many people, family heirlooms, community celebration photos
- Story: "This is where I gather evidence of people who matter. Connection is my work."

**Player C's room** (focused on discovery):
- Bed, exploration equipment, found objects, nature items, maps
- Story: "This is my base camp. Everything I learn about Velinor finds its way here."

No room is "wrong." The living quarters become a visual autobiography of what Lioren valued during her time with Tala.

---

## The Door as Final Metaphor

### Visual Language

```
LOCKED BAR (Phase 1-2):
This is where Tala keeps the world out.
Includes Lioren until Lioren is trusted.

REMOVED BAR (Phase 3):
Tala has chosen vulnerability.
This moment matters forever.

OPEN DOOR (Phase 4+):
Community enters Tala's private space.
She has remade her boundaries.

LIVED-IN ROOM (Phase 5-6):
The barrier is no longer about keeping people out.
It's about defining who belongs inside.
```

### The Glyph as Threshold

The Glyph of the Unbarred Door doesn't just mark a single moment. It marks the beginning of something larger:

```
What the glyph captures:
"Lioren has been given access to Tala's inner life."

What the glyph enables:
- Deeper conversations
- Physical shelter
- Community integration
- Access to living quarters as home base

What the glyph symbolizes:
- Trust as choice, not assumption
- Belonging as earned, not given
- Vulnerability as strength
- Doors that open change everything
```

---

## Implementation Timeline

### During Phase 1-2
- Barred door visible but unapproachable
- Regular stall interactions at marketplace
- Build trust through work
- Willy dialogue completes during this period

### Trigger for Phase 3
- Lioren doesn't have designated sleeping location
- Lioren appears at stall morning and evening repeatedly
- Tala makes observation comment
- tala_unbarred_door_01.json triggers
- Bar is removed, key is given
- Living quarters becomes accessible

### During Phase 4
- Multiple small dialogues in living quarters
- Relational development through cohabitation
- Objects appear gradually in room
- Small disappointments and recoveries

### Trigger for Phase 5
- Time-gated (N days after Phase 3)
- OR triggered by player returning to stall after N interactions
- Tala mentions her mother is coming
- tala_barbed_kinship_01.json triggers
- Mother's visit happens in stall or living quarters
- Physical remnants remain in room

### During Phase 5-6
- Tala's relationship tag changes to "best_friend"
- Linguistic shifts ("we" instead of "I")
- Tala invites others into living quarters
- Shared decision-making increases

### Trigger for Phase 6
- Community celebration event
- Storm sequence during preparation
- tala_salvaged_inheritance_01.json triggers
- Tala's realization about inheritance
- Full integration into shared home
- Glyph of Salvaged Inheritance becomes available

---

## Dialogue Files in Environmental Context

### tala_unbarred_door_01.json
```
Location: Tala's Stall (primarily) → Living Quarters (Beat 3)
Phase: End of Phase 2 / Beginning of Phase 3
Environmental trigger: Barred door, Lioren without shelter
Outcome: Bar removed, key given, access granted
Consequence: Living quarters becomes accessible home base
```

### tala_barbed_kinship_01.json
```
Location: Tala's Stall After Closing (Beats 1-2, 3-8)
Phase: Phase 4 culminating in Phase 5
Environmental trigger: Mother's arrival at marketplace
Outcome: Mother's visit, difficult conversation, remnants remain
Consequence: Room contains physical evidence of Tala's past
```

### tala_salvaged_inheritance_01.json
```
Location: Marketplace Residential Street → Communal Cooking Fire
Phase: Phase 5 culminating in Phase 6
Environmental trigger: Community celebration, storm
Outcome: Tala recognizes her inheritance, salvages the meal
Consequence: Full integration, shared home, "we" language, best friend status
```

---

## Supporting Small Dialogues (Phase 4)

Between major glyph encounters, small dialogues should occur in living quarters:

**Tala teaching household expectations:**
```
Tala: "I wake before dawn. The noise wakes me if you move around too much."
Lioren: (options to apologize, ask about timing, offer solution)
```

**Lioren using something private:**
```
Tala: "That's my repair kit. I had it set aside for a specific purpose."
Lioren: (options: apologize, explain, replace it)
Tala: "Never mind. Just... ask next time."
```

**Tala shows she cares indirectly:**
```
Lioren returns late to find dinner waiting.
Tala: "I had extra. Would've gone bad otherwise."
Lioren: (can thank her or play along with the practicality)
```

**Tala tests Lioren's trustworthiness:**
```
Tala: "I need to run to the market supplier. Can you watch the stall?"
Lioren: (accepts or declines; affects trust stat)
```

**Tala admits vulnerability:**
```
Tala: "I didn't sleep well. Just... thinking about things."
Lioren: (listen, offer support, or respect silence)
```

These small moments make the glyph encounters feel earned rather than sudden.

---

## The Strongest Narrative Arc

### Act 1: Separation
The barred door. Tala's life is closed.
Lioren notices it, questions it, but cannot access it.

### Act 2: Permission
Tala removes the bar.
This single action says: "I choose to let you see me."

### Act 3: Inhabitation
Lioren moves in.
Awkward cohabitation teaches both women how to share space.

### Act 4: Rupture
Tala's mother arrives.
The boundaries Tala built are tested.
Lioren witnesses Tala's deepest wounds.

### Act 5: Integration
Community celebration.
Tala recognizes her inheritance.
The room becomes not Tala's fortress with a guest, but a home built by two.

### Resolution: Belonging
The door that was barred is now a threshold.
Not a barrier, but a place where public and private merge.
Where Lioren belongs, and Tala permits that belonging.

---

## Final Principle

The space tells the story that dialogue articulates.

**Dialogue says:**
"We're developing a relationship."

**Space shows:**
Bar → Key → Objects → Mother's remnant → Shared life

**Together:**
Story becomes unforgettable because it lives in the player's memory as *place* and *experience*, not just words.
