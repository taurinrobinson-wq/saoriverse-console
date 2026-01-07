# COMPREHENSIVE STORY ANALYSIS: more_story_stuff.md + more_story_stuff_2.md

**Purpose**: Reference guide for wiring story elements into game systems  
**Status**: Ready for dialogue banking + mechanical integration  
**Date Created**: January 6, 2026  

---

## TABLE OF CONTENTS

1. [File-by-File Breakdown](#file-by-file-breakdown)
2. [Character Architecture Index](#character-architecture-index)
3. [Narrative Mechanics](#narrative-mechanics)
4. [NPC Relationship Map](#npc-relationship-map)
5. [Scene & Location Index](#scene--location-index)
6. [Skill & Glyph Progression](#skill--glyph-progression)
7. [REMNANTS Integration Points](#remnants-integration-points)
8. [Dialogue Hooks & Choice Points](#dialogue-hooks--choice-points)
9. [Implementation Checkpoints](#implementation-checkpoints)

---

## FILE-BY-FILE BREAKDOWN

### more_story_stuff.md (2,150 lines)

**Core Content**:
- Corelink system architecture (emotional lattice, memory backup, collective decision-making)
- Velinor collapse mechanics (3-phase cascade: Overload → Fragmentation → Severance)
- Velinor worldbuilding (Qatar location, manufactured water, melting pot culture)
- 20-year post-collapse timeline (Year 0-20 with character age progression)
- Player origin story (age 2-3 at collapse, parents died from knowledge loss)
- Three philosophical endings (Restore/Destroy/Do Nothing with Archaeologist path)
- Moral paradox (system died but healed planet accidentally)

**Key Passages for Wiring**:
- **Corelink emotional lattice**: Foundation for understanding why NPCs have fractured identities
- **Collapse mechanics**: Explains REMNANTS stat profiles (memory loss, emotional injury, identity fractures)
- **Player orphaning**: Justifies why player seeks mentorship (emotional anchor lost, needs purpose)
- **20-year timeline**: Establishes NPC ages and how they survived collapse
- **Three endings**: Set up as late-game branching points based on player's accumulated wisdom

**Reference Points**:
- Saori: Age 23 at collapse → 43-45 by game present
- Player: Age 2-3 at collapse → 22-23 by game present
- Tessa: Lost husband Ammar, became Desert Widow
- Velinor: True world capital accidentally healed by collapse

### more_story_stuff_2.md (10,578 lines)

**Lines 1-400: Tessa (Desert Widow) Foundation**
- Ache glyph: Widow's Cry (ritual lament teaching)
- Pre-collapse role: OS calibrator for Corelink
- Husband Ammar: Ceremonial scribe, "Still Flame" glyph (deceased)
- Current role: Market kitchen keeper, shrine maintainer
- Glyph mechanics: Teaches through ritual presence, not instruction
- Dialogue pattern: Warm, ceremonial, honor-focused

**Lines 400-1000: Swamp Trickster Introduction**
- Name changes every encounter (denies previous ones)
- TONE system integration (dialogue gates conversations)
- Conditional information gating (trickster as test NPC)
- Four-phase encounter structure
- Influence metrics on other NPCs

**Lines 1000-1500: Swamp Trickster REMNANTS Profile**
- Complete stat breakdown: R2/E4/M1/N7/A0/N6/T1/S9
- Four-phase encounter dialogue structure
- Influence metrics (Kaelen +3, Drossel +1, Veynar -4)
- Gaslighting dialogue pattern (never lies directly, always answers around)

**Lines 1500-2000: Kaelen × Trickster Fusion Theory**
- Trickster is Kaelen's dissociated self (identity fragmentation)
- Swamp maze = externalized fragmented mind
- Three passages: False Path / Fog Stones / Hidden Threshold
- Glyph of Stolen Memory restores fractured identity
- Codex device specifications (7.5" × 5.5", 45-degree corners, wood-tone)
- Bodhisattva mechanic justification (player endures so NPCs heal)

**Lines 2000-3500: Kaelen Fracture Mechanics + Visual Specs**
- Height/posture/age matching Kaelen (plausibly same person)
- Artifacts: Rusted bells, leaked tokens, warped lantern
- Emotional OS cues mirroring REMNANTS profile
- Dialogue mirrors Kaelen phrasing (high memory fragments, high skepticism)
- Visual design: No adornments, mask over nose-chin, hood forward, lantern

**Lines 3500-5500: Sealina + Elenya Glyphs + Malrik Glyphs**
- Sealina: Ache (Echoed Longing) + Legacy (Hopeful Transmission)
- Elenya glyphs: Sky Revelry, Blooming Path, Veiled Silence, Covenant Flame
- Malrik glyphs: Mirage Echo, Ancestral Record, Sand Memories, Measured Step, Boundary Stone
- Glyph interplay mechanics (two sides of emotional coin)
- Malrik's fracture vs. Elenya's wholeness (opposite approaches to impermanence)

**Lines 5500-7500: JSON Schema + Enrichment Discussion**
- Rationale for JSON as narrative database
- Schema design with extended fields
- Codespace handling technical conversion
- Integration patterns for semantic + REMNANTS

**Lines 7500-10578: Malrik Deep-Dive + Elenya + Coren + Observational Mechanics**
- Malrik: Overclocked mind, under-expressive voice, secret Buddhist spirituality, secretly loves Elenya
- Elenya: Luminous presence, intuitive clarity, rejects Malrik for philosophical incompatibility
- Sand-drawing scene: Malrik creating, Elenya watching unseen
- Observational mini-game: Four shared observations, four orientation-based interpretations
- Coren: Dual-glyph (Preemptive Severance / Held Ache)
- Extended biome descriptions with emotional logic

---

## CHARACTER ARCHITECTURE INDEX

### Tier 1: Main Characters (Deep Profile Required)

#### Archivist Malrik
**Location**: Desert archives  
**Role**: Knowledge keeper, mentor, glyph teacher  
**Glyphs Teaches**: Mirage Echo, Ancestral Record, Sand Memories, Measured Step, Boundary Stone

**Emotional Architecture**:
- **Heart Secret**: In love with Elenya
- **Speech Pattern**: Overclocked mind, under-expressive voice, stammers around Elenya
- **Philosophy**: Systems safer than people (unintentional Buddhist)
- **Wound**: Punishes self through precision for emotional vulnerability
- **Teaching Method**: Glyph trials as confessions about hidden love

**REMNANTS Profile** (To Define):
- Resolve: Moderate-high (disciplined, committed)
- Empathy: Moderate (cares deeply but compartmentalized)
- Memory: High (archivist, preserves everything)
- Narrative Presence: Low (avoids being seen)
- Authority: High (respected, commands attention through knowledge)
- Neediness: Low (self-sufficient, doesn't ask for help)
- Trust: Moderate-high (reliable, consistent)
- Skepticism: Moderate (questions but accepts evidence)

**Glyph Arc** (Reframed in skills_jobs_mentorship.md):
1. **Mirage Echo**: Self-deception (he lives in mirage of unrequited love)
2. **Ancestral Record**: Erasure (he believes his story isn't worth recording)
3. **Sand Memories**: Ache (memories of Elenya are treated as contraband)
4. **Measured Step**: Pacing (years spent holding precise distance from her)
5. **Boundary Stone**: Breaking point (realizes boundary around heart held too long)

**Player Return Loop**:
- Early: "I need your help retrieving the next fragment" (technical)
- Mid: "The archives have destabilized" (still technical, becoming personal)
- Late: "I don't want to do this alone" (fully emotional)

**Dialogue Banking Strategy**:
- **Untrained**: Turns player away gently, explains archives are dangerous
- **Adjacent Skills** (trained with Tala): "Your instincts are sharp but archives require patience"
- **Ready**: Full glyph trial, reveals his emotional vulnerability gradually
- **Overqualified** (trained with Elenya): Notices player's perception, offers deeper insights

#### High Seer Elenya
**Location**: Mountain shrine or marketplace  
**Role**: Spiritual guide, co-witness, glyph teacher  
**Glyphs Teaches**: Sky Revelry, Blooming Path, Veiled Silence, Covenant Flame

**Emotional Architecture**:
- **Heart**: Loves Malrik but fears relational imbalance
- **Philosophy**: Intuition as clarity, compassion as highest order, uncertainty as doorway
- **Presence**: Luminous, magnetic, listening inward constantly
- **Perception Power**: She sees Malrik's tenderness in his precision
- **Rejection**: Softly rejects him because their worldviews are incompatible despite shared heart

**REMNANTS Profile** (To Define):
- Resolve: High (spiritual commitment, unwavering)
- Empathy: Very high (feels everything deeply)
- Memory: Moderate (focuses on present, not past)
- Narrative Presence: High (charismatic, draws attention naturally)
- Authority: Very high (people listen, follow her wisdom)
- Neediness: Low (complete within herself)
- Trust: High (trusts intuition implicitly)
- Skepticism: Low (open to paradox and mystery)

**Glyph Arc** (Inverted to Malrik):
1. **Sky Revelry**: Freedom (she trusts the sky, not systems)
2. **Blooming Path**: Growth (she sees potential in all things, including Malrik)
3. **Veiled Silence**: Mystery (she honors what cannot be spoken)
4. **Covenant Flame**: Sacred bonds (she understands love's parameters)

**Rejection Scene Architecture**:
- Acknowledges his love (she sees it)
- Acknowledges her love (she feels it)
- Names the incompatibility (she can't live in his precision)
- Leaves him whole (not cruel, not unclear)

**Dialogue Banking Strategy**:
- **Untrained**: Tests player's openness before teaching
- **Adjacent Skills** (trained with Malrik): "You understand systems. Now understand yourself"
- **Ready**: Full spiritual teaching, begins revealing her own struggles
- **Overqualified** (trained with Coren): "You hold ache well. Come deeper"

#### Coren the Mediator
**Location**: Market square (neutral ground) or mountain cult hideaway  
**Role**: Dual-aspect character (fear vs. wisdom)  
**Glyphs Teaches**: Preemptive Severance (collapse), Held Ache (sovereignty)

**Emotional Architecture**:
- **Core**: Same person, two fractures depending on pressure + approach
- **Aspect 1 - Severance** (collapse/fear): Mountain cult, teaches cutting bonds before betrayal
- **Aspect 2 - Held Ache** (sovereignty/wisdom): Market mediator, teaches co-witnessing pain
- **Correlation Shift**: NPC relationships change based on which aspect player aligns with

**REMNANTS Profile** (To Define - Changes by Aspect):
- **Severance Aspect**: High skepticism, low empathy (protects through distance)
- **Held Ache Aspect**: Moderate skepticism, very high empathy (present through pain)

**Dual-Glyph Mechanic**:
- Same NPC embodies both glyphs depending on emotional context
- Player's approach determines which aspect emerges
- Surrounding NPCs' correlations shift based on which aspect dominates
- Creates dynamic character who feels alive through philosophical stakes

**Dialogue Banking Strategy**:
- **Mountain Encounter**: Severe, protective, teaching severance
- **Market Encounter**: Grounded, compassionate, teaching ache-holding
- **Aspect Shift**: Dialogue can transition between aspects based on player choices

---

### Tier 2: Secondary Characters (Moderate Profile)

#### Swamp Trickster (Kaelen's Dissociated Echo)
**Location**: Swamp maze  
**Role**: Test NPC, glyph gate-keeper, memory distortion mechanic

**REMNANTS Profile** (Exact):
- **R2**: Almost no resolve (cannot commit to anything)
- **E4**: Some empathy but detached (cares but can't stay)
- **M1**: No memory (stolen, fragmented)
- **N7**: High narrative presence (needs attention, tells stories)
- **A0**: No authority (never believed in command)
- **N6**: Craves attention (high neediness, wants reaction)
- **T1**: No trust (extreme skepticism, questions everything)
- **S9**: Extreme skepticism (doubts reality itself)

**Mechanics**:
- Name changes every encounter (Murk → Maurr → Charl → Rilk → Fenrick)
- Gives Glyph of Apprehension (Trust domain) to aligned players
- Gives Glyph of Stolen Memory (Collapse domain) if player opposes
- Four-phase encounter structure
- Gaslighting dialogue (never lies directly, always answers around)

**Identity Fusion Theory**:
- Trickster is Kaelen's dissociated self through memory theft
- Swamp maze = externalized fragmented mind
- Fog loops = memory distortion (paths repeat with slight differences)
- If Kaelen's fracture severe enough, he loses continuity and becomes trickster without knowing

**Maze Architecture**:
- False Path: Leads nowhere, teaches caution
- Fog Stones: Requires stillness to navigate (emotional mastery)
- Hidden Threshold: True exit, found through presence not panic
- Glyph of Stolen Memory: Restores Kaelen's fractured identity

**Dialogue Banking Strategy**:
- **Phase 1**: Greeting (name-denial, testing player)
- **Phase 2**: Information exchange (gaslighting, half-truths)
- **Phase 3**: Maze entry (conditional based on alignment)
- **Phase 4**: Glyph offering (depends on player's path through maze)

#### Sealina (Street Performer)
**Location**: Marketplace  
**Role**: Dual-domain character, emotional witness

**Glyph Architecture**:
- **Ache Domain**: Echoed Longing (body remembers mother/grandmother, confusion mid-dance)
- **Legacy Domain**: Hopeful Transmission (player collects photos, glyph emerges, family appears)
- **Same Character, Different Domains**: Not personality change, emotional threshold change

**Mechanic**:
- No player participation required (purely observational)
- Player witnesses her mid-performance confusion (ache triggers)
- Player collects scattered family photographs across game
- Corelink resonance with photo collection produces glyph
- She completes inherited dance, sees ghostly family presence
- Moment of recognition: "I remember their names"

**Dialogue Banking Strategy**:
- **First Encounter**: Joyful performance, no sign of confusion
- **Ache Moment**: Mid-dance fracture, player witnesses her disorientation
- **Legacy Building**: Each photograph encountered, subtle callback dialogues
- **Glyph Moment**: Recognition dialogue, gratitude to player for witnessing

#### Tessa (Desert Widow)
**Location**: Market kitchen / Shrine  
**Role**: Ritual keeper, ache teacher

**Background**:
- Lost husband Ammar (ceremonial scribe, "Still Flame" glyph)
- Pre-collapse role: OS calibrator for Corelink
- Current role: Maintains kitchen, keeps shrine, teaches ritual

**Glyphs**:
- **Widow's Cry**: Lament ritual, teaches through presence and silence
- Teaches: Grief as sacred, honor through ritual, continuity through ceremony

**Dialogue Banking Strategy**:
- **Untrained**: Shares kitchen duties, explains ritual significance
- **Adjacent**: "You're learning to honor what's lost"
- **Ready**: Full ritual teaching, opens about Ammar
- **Overqualified**: "You understand the sacredness now"

### Tier 3: Tertiary Characters (Light Profile)

**Characters Mentioned, Profiles to Develop**:
- Ravi & Nima: Married couple, market weavers, +50% correlation model
- Kaelen: Archivist fractured by memory theft (before trickster dissociation)
- Veynar: Antagonist, resistance to player's path
- Drossel: Ally, supporter of player growth
- Ophina: Deceased figure, mourned by multiple NPCs
- Helia: Witness/caretaker character
- Mariel: Trust domain character
- Dakrin: Legacy domain character
- Lira: Craftsmanship teacher

---

## NARRATIVE MECHANICS

### Collapse Physics (3-Phase System)

**Phase 1: Overload**
- Corelink emotional lattice becomes oversaturated
- Collective emotional processing breaks down
- Individual identity anchors begin fracturing
- System tries to adapt but causes feedback loops

**Phase 2: Fragmentation**
- Individual identities splinter into trauma responses
- Memory becomes unreliable (some retain, some lose everything)
- Emotional connections fragment (some NPCs remember relationships, some don't)
- REMNANTS profiles emerge from these fragmentations

**Phase 3: Severance**
- Final separation from Corelink system
- Some NPCs choose isolation (Coren's severance teaching)
- Some NPCs choose community (Nima's weaving teaching)
- Emotional OS evolves as new operating system

**Game Implementation**:
- Player's backstory: Age 2-3 at collapse, emotionally intact (lucky accident)
- NPC backstories: Vary wildly (total amnesia to perfect recall to selective trauma)
- REMNANTS system: Reflects each NPC's collapse response
- Three endings: Restore (reconnect Corelink), Destroy (keep it dead), Do Nothing (accept emergence)

### Memory Distortion Mechanics (Swamp Maze)

**Fog Loop System**:
- Paths repeat with slight differences (testing if player remembers)
- Moments loop but alter (memory distortion in real-time)
- Players may question reality (intentional disorientation)
- Stillness breaks the loop (emotional mastery overcomes fracture)

**Implementation**:
- Swamp maze as dungeon encounter
- Fog effects obscure true path
- Player must choose: panic (fast movement fails) or stillness (presence finds truth)
- Optional: Glyph of Stolen Memory reveals maze as Kaelen's mind externalized

### Observational Mini-Game (Perception Mechanic)

**Core Concept**: Player's TONE orientation determines what they see and what choices appear

**Scene: Elenya Watching Malrik Draw in Sand**

**Shared Observations** (all players see these):
1. Elenya's silence (why does she stay?)
2. Malrik's hand on his gut (what's he holding back?)
3. Malrik's obliviousness (does he know she's there?)
4. Irony of his aloofness (the only time he's accessible is when unseen)

**Choice Menu** (varies by player TONE profile):

**If High Trust**:
- "Distance is normal between them" (+0.02 Trust)
- "He's probably sensing her presence" (+0.01 Trust, +0.01 Observation)
- "She respects his boundary" (+0.03 Trust)

**If High Observation**:
- "Something in his posture shifts" (+0.02 Observation, +0.01 Empathy)
- "Her breathing matches the wind" (+0.01 Observation)
- "They move in different tempos" (+0.02 Observation)

**If High Narrative Presence**:
- "This is a turning point" (+0.02 Narrative, +0.02 Empathy)
- "One of them should step forward" (+0.02 Narrative)
- "The moment feels charged" (+0.01 Narrative, +0.02 Empathy)

**If High Empathy**:
- "She loves him, he doesn't know" (+0.04 Empathy, +0.02 Narrative)
- "His hand on his gut = he feels her presence" (+0.03 Empathy, +0.01 Observation)
- "Her silence is devotion" (+0.03 Empathy)

**Mechanic**: Invisible attunement score for Malrik/Elenya pair tracks which choices player makes
- 0-0.10 attunement: Their correlation is -50% (opposition)
- 0.11-0.25: Their correlation is 0% (neutral coexistence)
- 0.26+: Their correlation is +50% (synergistic)

---

## NPC RELATIONSHIP MAP

### Correlation Pairs

**Standard Correlations** (Fixed):
- **Ravi & Nima**: +50% (married, mutual support, stat bleed)
- **Tessa & Ammar (deceased)**: One-way (her ache references his memory)

**Dynamic Correlations** (Variable):

| Pair | Correlation Type | Baseline | Trigger | Max |
|---|---|---|---|---|
| Malrik ↔ Elenya | Love/Incompatibility | -50% | Attunement score | +50% |
| Malrik ↔ Kaelen | Mentor/Fracture | 0% | Player resolves identity | +30% |
| Elenya ↔ Coren | Wisdom/Fear | 0% | Player's alignment | ±50% |
| Coren ↔ Kaelen | Protector/Victim | Varies | Which Coren aspect | ±40% |
| Kaelen ↔ Trickster | Same/Fragmented | -100% | Memory restoration | 0% |

**NPC Influence on Others**:
- **Trickster on Kaelen**: -4 (destabilizing)
- **Trickster on Drossel**: +1 (minor charm)
- **Malrik on Kaelen**: +3 (stabilizing)
- **Elenya on community**: +2 general (calming presence)

### Faction-Style Groupings

**Elenya's Guardians** (Intuitive, Spiritual):
- Elenya (leader)
- Coren (when in Held Ache aspect)
- Helia (witness)
- Sealina (through art)

**Malrik's Architects** (Knowledge, Systems):
- Malrik (leader)
- Kaelen (before fracture)
- Tessa (pre-collapse role)
- Archive keepers

**Nima's Weavers** (Community, Connection):
- Nima & Ravi (leaders)
- Marketplace vendors
- Craft workers
- Lira (craftsmanship)

**Coren's Keepers** (Containment, Presence):
- Coren (when in both aspects)
- Mediation circle members
- Those who choose ache-holding

---

## SCENE & LOCATION INDEX

### Desert-Mountain Biome

**Elenya/Malrik Sand-Drawing Scene**
- **Description**: Malrik kneeling in foreground creating sand diagram, Elenya standing mid-distance on ridge watching unseen
- **Emotional Tone**: Unspoken love, two philosophical domains coexisting
- **Player Mechanic**: Observational mini-game, choice-based attunement tracking
- **Visual Metaphor**: Distance between them = philosophical incompatibility + physical space
- **Implementation**: Scene composition triggers observational mechanic at specific location

**Desert Archives**
- **Location**: Deep desert, buried structures
- **Function**: Malrik's glyph trial location
- **Mechanics**: Progressive deeper archives unlock as player completes glyphs
- **Atmosphere**: Knowledge preserved against impermanence

**Mountain Shrine**
- **Location**: High altitude, wind-swept
- **Function**: Elenya's teaching space, ritual location
- **Mechanics**: Seasonal changes affect glyph availability
- **Atmosphere**: Spiritual clarity, isolation with vast perspective

### Swamp-Maze Biome

**Swamp Entrance**
- **Description**: Murky water, fog rolling, lantern-marked paths
- **Guardian**: Trickster (name-shifting, always present)
- **Mechanic**: Enter only after meeting Trickster in marketplace
- **Glyph Offered**: Glyph of Apprehension (Trust domain, optional)

**Interior Maze**
- **Three Passages**:
  1. **False Path**: Leads to dead-end, teaches caution
  2. **Fog Stones**: Requires stillness to navigate (emotional mastery)
  3. **Hidden Threshold**: True exit, found through presence not panic

**Maze Center** (Optional):
- **Kaelen's Inner Chamber**: If player pursues identity restoration
- **Glyph of Stolen Memory**: Restores fractured identity
- **Visual**: Externalized fragmented mind, impossible architecture

### Urban Ruins Biome

**Marketplace**
- **Central Hub**: Vendors, performers, traders
- **Key NPCs Located Here**:
  - Tessa (kitchen)
  - Sealina (performance area)
  - Coren (mediation circle)
  - Nima & Ravi (weaving stall)

**Collapsed City Structures**
- **Exploration Location**: Architectural fragments, collapsed Corelink nodes
- **Mechanic**: Optional exploration, finds skill books and memory fragments
- **Atmosphere**: Grief at systems' end, opportunity in ruins

**Archive Ruins** (Alternative Malrik Location):
- **Description**: Partially collapsed archive building
- **Function**: Secondary glyph trial location
- **Mechanic**: Structural instability adds time pressure to trials

### Forest Biome

**Intuitive Paths**
- **Description**: Misty, layered, nonlinear
- **Mechanic**: Emotional state affects pathfinding
- **Glyph Function**: Intuition-based glyphs activate here
- **Atmosphere**: Feeling shapes reality

**Elenya's Sanctuary** (Optional):
- **Hidden Location**: Found through intuition, not directions
- **Function**: Deepest dialogue with Elenya
- **Mechanic**: Player must reach through emotional alignment, not mechanical skill

---

## SKILL & GLYPH PROGRESSION

### Skill Dependency Map

**Collapse Domain** (System Understanding):
- Discernment (taught by Malrik: Mirage Echo trial)
  - Prerequisite: None
  - Unlocks: Elenya's Veiled Silence
  - Effect: See through illusions, understand distortion

- Resilience (taught by Tessa: Widow's Cry trial)
  - Prerequisite: Discernment
  - Unlocks: Coren's Held Ache
  - Effect: Withstand emotional pressure, hold ache

- System Navigation (taught by Kaelen/Archives)
  - Prerequisite: Discernment, Resilience
  - Unlocks: Trickster's maze passages
  - Effect: Navigate fractured systems, find hidden paths

**Legacy Domain** (Memory & Continuity):
- Ritual Presence (taught by Tessa: Widow's Cry trial)
  - Prerequisite: None
  - Unlocks: Covenant Flame
  - Effect: Honor lineage, perform ceremony

- Interpretation (taught by Malrik: Ancestral Record trial)
  - Prerequisite: Ritual Presence
  - Unlocks: Kaelen dialogue deepening
  - Effect: Read records, understand inheritance

- Lineage Navigation (taught by Sealina: photograph collection)
  - Prerequisite: Ritual Presence, Interpretation
  - Unlocks: Legacy Transmission glyph
  - Effect: Recover family connections, heal through memory

**Sovereignty Domain** (Boundary & Choice):
- Boundary Setting (taught by Malrik: Boundary Stone trial)
  - Prerequisite: None
  - Unlocks: Measured Step
  - Effect: Define safe space, say no clearly

- Measured Pace (taught by Malrik: Measured Step trial)
  - Prerequisite: Boundary Setting
  - Unlocks: Mariel dialogue
  - Effect: Move through consequence intentionally

- Presence Sovereignty (taught by Coren: Held Ache trial)
  - Prerequisite: Boundary Setting, Measured Pace
  - Unlocks: Final dialogue options
  - Effect: Choose presence without fixing outcomes

**Presence Domain** (Witnessing & Co-presence):
- Silent Witnessing (taught by Elenya: Veiled Silence trial)
  - Prerequisite: None
  - Unlocks: Coren's Severance (inverse)
  - Effect: Hold emotional space without words

- Co-Witnessing (taught by Coren: Held Ache trial)
  - Prerequisite: Silent Witnessing
  - Unlocks: Helia dialogue
  - Effect: Share pain without fixing it

- Sacred Presence (taught by Elenya: Covenant Flame trial)
  - Prerequisite: Silent Witnessing, Co-Witnessing
  - Unlocks: Spiritual domain glyphs
  - Effect: Hold emotional space as sacred act

**Trust Domain** (Interdependence):
- Cooperative Labor (taught by Nima/Ravi: marketplace tasks)
  - Prerequisite: None
  - Unlocks: Ravi dialogue deepening
  - Effect: Build community bonds

- Covenant Building (taught by Elenya: Covenant Flame trial)
  - Prerequisite: Cooperative Labor
  - Unlocks: Deep NPC relationships
  - Effect: Form meaningful bonds, not shallow ones

- Shared Vulnerability (taught by Malrik: late-game trials)
  - Prerequisite: Covenant Building
  - Unlocks: Final dialogue arcs
  - Effect: True emotional intimacy with NPCs

**Joy Domain** (Creative Celebration):
- Celebration (taught by Sealina: watching performances)
  - Prerequisite: None
  - Unlocks: Sky Revelry
  - Effect: Find joy in trauma's aftermath

- Communal Crafting (taught by Lira: craft alongside her)
  - Prerequisite: Celebration
  - Unlocks: Blooming Path
  - Effect: Create beauty collaboratively

- Shared Reverence (taught by Elenya: Sky Revelry trial)
  - Prerequisite: Celebration, Communal Crafting
  - Unlocks: Transcendent dialogue
  - Effect: Share profound joy with community

### Glyph-to-Skill Cross-Reference

| Glyph | Domain | Teaches Skill | Location | NPC |
|---|---|---|---|---|
| Mirage Echo | Collapse | Discernment | Desert illusion field | Malrik |
| Ancestral Record | Legacy | Interpretation | Archive chamber | Malrik |
| Sand Memories | Legacy | Ritual Presence (alt) | Sand dunes | Malrik |
| Measured Step | Sovereignty | Measured Pace | Desert ruins | Malrik |
| Boundary Stone | Sovereignty | Boundary Setting | Shifting sands | Malrik |
| Widow's Cry | Legacy/Collapse | Ritual Presence, Resilience | Market shrine | Tessa |
| Sky Revelry | Joy | Celebration, Shared Reverence | Mountain peak | Elenya |
| Blooming Path | Joy | Communal Crafting | Forest renewal | Elenya |
| Veiled Silence | Presence | Silent Witnessing | Mountain shrine | Elenya |
| Covenant Flame | Trust | Covenant Building | Sacred space | Elenya |
| Preemptive Severance | Collapse | System Navigation | Mountain cult (fear path) | Coren |
| Held Ache | Presence | Co-Witnessing, Presence Sovereignty | Market mediation | Coren |
| Echoed Longing | Legacy/Collapse | Lineage Navigation (alt) | Marketplace | Sealina |
| Hopeful Transmission | Legacy | Lineage Navigation | Marketplace | Sealina |
| Glyph of Apprehension | Trust | Trust building | Swamp entrance | Trickster |
| Glyph of Stolen Memory | Collapse | System Navigation, Memory recovery | Maze center | Trickster |

---

## REMNANTS INTEGRATION POINTS

### NPC REMNANTS Profiles (By Character)

#### Malrik (Template)
- **Resolve**: 6/10 (disciplined but emotionally fragile)
- **Empathy**: 4/10 (feels deeply but compartmentalized)
- **Memory**: 9/10 (perfect recall, preserves everything)
- **Narrative Presence**: 2/10 (avoids being seen)
- **Authority**: 7/10 (command through knowledge)
- **Neediness**: 2/10 (self-sufficient)
- **Trust**: 6/10 (reliable, consistent)
- **Skepticism**: 5/10 (questions but accepts evidence)

**What Changes These Stats During Game**:
- High player empathy → Malrik Resolve increases (feels seen, gains strength)
- High player observation → Malrik Narrative Presence increases (learns to show himself)
- High player trust → Malrik Empathy increases (allows vulnerability)
- High player narrative presence → Malrik Authority decreases (shares power)

#### Elenya (Template)
- **Resolve**: 8/10 (spiritual commitment unwavering)
- **Empathy**: 9/10 (feels everything deeply)
- **Memory**: 5/10 (focuses on present)
- **Narrative Presence**: 8/10 (charismatic naturally)
- **Authority**: 9/10 (people listen naturally)
- **Neediness**: 1/10 (complete within herself)
- **Trust**: 8/10 (trusts intuition)
- **Skepticism**: 2/10 (open to paradox)

**What Changes These Stats During Game**:
- High player empathy → Elenya Resolve increases (feels supported)
- High player observation → Elenya Skepticism increases (questioned, has to defend)
- High player trust → Elenya Empathy remains stable (she's already there)
- Player romance choices → Elenya Narrative Presence decreases (feels exposed)

#### Coren (Template - Changes by Aspect)

**Severance Aspect**:
- Resolve: 5/10, Empathy: 2/10, Memory: 7/10, Narrative: 6/10, Authority: 4/10, Neediness: 3/10, Trust: 1/10, Skepticism: 9/10

**Held Ache Aspect**:
- Resolve: 7/10, Empathy: 9/10, Memory: 6/10, Narrative: 5/10, Authority: 6/10, Neediness: 2/10, Trust: 7/10, Skepticism: 4/10

**What Changes These Stats During Game**:
- Player wisdom + presence → Coren aspect shifts (fear transforms to wisdom)
- Community building → Coren correlations shift (severance aspect erodes)
- Shared vulnerability → Coren Held Ache aspect strengthens

#### Swamp Trickster (Fixed Profile)
- **Resolve**: 2/10 (can't commit to anything)
- **Empathy**: 4/10 (cares but detached)
- **Memory**: 1/10 (stolen, fragmented)
- **Narrative Presence**: 7/10 (needs attention, tells stories)
- **Authority**: 0/10 (never believed in command)
- **Neediness**: 6/10 (craves attention)
- **Trust**: 1/10 (extreme skepticism)
- **Skepticism**: 9/10 (doubts reality itself)

**What Changes These Stats During Game**:
- Nothing (trickster is external manifestation, not NPC proper)
- BUT: If player restores Kaelen's identity, trickster stats reverse/merge

### TONE-to-REMNANTS Mapping

**When Player Uses High Trust Choices**:
- NPC Resolve increases (+0.02)
- NPC Empathy increases (+0.01)
- NPC Skepticism decreases (-0.01)

**When Player Uses High Observation Choices**:
- NPC Narrative Presence increases (+0.02)
- NPC Skepticism increases (+0.01)
- NPC Empathy may decrease (-0.01, feeling analyzed)

**When Player Uses High Narrative Presence Choices**:
- NPC Authority decreases (-0.01, authority shared)
- NPC Narrative Presence increases (+0.01, story reciprocated)
- NPC Resolve increases (+0.01, feels supported)

**When Player Uses High Empathy Choices**:
- NPC Empathy increases (+0.02)
- NPC Resolve increases (+0.02)
- NPC Skepticism decreases (-0.01)
- NPC Neediness increases (+0.01, feels seen)

### REMNANTS Triggers for Dialogue Changes

**If NPC Resolve > 7**:
- Dialogue becomes more open
- NPC shares vulnerabilities
- Glyph trials become collaborations, not tests

**If NPC Empathy > 7**:
- NPC initiates deeper conversations
- Offers wisdom about player's growth
- Recognizes player's emotional state

**If NPC Memory < 3**:
- Dialogue becomes fragmented
- NPC forgets prior conversations
- Requires re-introduction each encounter

**If NPC Narrative Presence < 3**:
- NPC barely speaks
- Dialogue becomes sparse, sparse
- Acts through presence not words

**If NPC Authority > 8**:
- NPC gives directives, not suggestions
- Dialogue becomes command-like
- Expects obedience

**If NPC Neediness > 6**:
- NPC asks player for help frequently
- Dialogue becomes emotionally demanding
- Creates player-as-caregiver dynamic

---

## DIALOGUE HOOKS & CHOICE POINTS

### Malrik Dialogue Progression

**First Meeting**:
- "The archives are fractured. I don't typically take apprentices."
- **Player Response Options**:
  - Trust: "I'm reliable. I can help restore them" → Malrik gains +0.02 Resolve
  - Observation: "What fractured them?" → Malrik gains +0.02 Narrative
  - Narrative: "I've survived the collapse. I'm here to learn" → Malrik gains +0.01 Authority
  - Empathy: "You look exhausted from carrying this alone" → Malrik gains +0.02 Empathy

**Mirage Echo Trial**:
- Malrik: "The mirages are fed by Corelink remnants broadcasting phantom signals. Tell me what you see."
- Scene: Desert mirages (false water, false paths, false homes)
- **Player Interpretation** (observational mechanic):
  - Trust: "We should mark safe ground and move systematically"
  - Observation: "The mirages change when I look away from them"
  - Narrative: "This is a test of my faith, not my sight"
  - Empathy: "Something is grieving here. The signals are mourning"

**Sand Memories Trial**:
- Malrik hesitates before speaking: "There are memories in the sand here I carved years ago. Some are... personal."
- **Dialogue Hook**: Player can ask about Elenya or respect his boundary
  - High Empathy: Player notices pain and changes subject
  - High Observation: Player notices Elenya reference and investigates
  - High Narrative: Player insists on full story
  - High Trust: Player waits for him to volunteer information

**Boundary Stone Trial**:
- Malrik voice breaks: "I've held a boundary around my heart for so long. I'm not sure how to let it down."
- **Dialogue Hook**: This is peak vulnerability moment
  - High Empathy: "You don't have to know how. You just have to try"
  - High Observation: "You've been doing this since Elenya came to the shrine"
  - High Narrative: "This is the real trial. Everything else was training for this"
  - High Trust: "I'll hold the space while you figure it out"

### Elenya Dialogue Progression

**First Meeting**:
- "The High Seer's role is to see, not to be seen. But perhaps you need seeing right now."
- **Player Response Options**:
  - Trust: "I'm looking for something solid in a broken world" → Elenya Empathy +0.01
  - Observation: "You're different from other NPCs I've met" → Elenya Narrative +0.01
  - Narrative: "I feel like I've been lost and you're the light" → Elenya Authority +0.01
  - Empathy: "You're carrying something heavy. Can I help?" → Elenya Resolve +0.01

**Veiled Silence Trial**:
- Elenya: "Silence has many languages. Speak with me without words."
- Scene: Sitting in stillness, wind carries moments
- **Player Options**:
  - Trust: Remain silent, trust her guidance
  - Observation: Notice small movements, gestures, breaths
  - Narrative: Imagine the story the wind is telling
  - Empathy: Feel what her presence is communicating

**Sky Revelry Trial**:
- Elenya invites player to mountain peak at dawn
- "The sky shows us that breaking apart can be beautiful."
- **Dialogue Hook**: Malrik reference (if player has trained with him)
  - Player trained with Malrik: "He shows you the same truth in sand. Different medium"
  - Player hasn't trained with Malrik: "There's someone else learning this. An archivist"

**Covenant Flame Trial** (Late Game):
- Elenya: "Love that demands resolution is not true love. Can you hold what is beautiful but unfinished?"
- **Dialogue Hook**: Direct Malrik/Elenya relationship reveal
  - High Empathy: "I understand. Two beautiful things moving in different directions"
  - High Observation: "You're talking about Malrik"
  - High Narrative: "This is the real trial. Not the glyphs. This"
  - High Trust: "I'll protect what you can't complete. That's how I love"

### Observational Mini-Game Dialogue

**Scene Setup**:
- Player discovers Elenya on ridge, Malrik in foreground drawing
- Shared observations with interpretation questions

**Four Observation Prompts**:

1. "Elenya's silence is striking. In a moment of revelation, what does it mean?"
   - Trust: "Respect. She honors his space"
   - Observation: "Waiting. She's watching to see something"
   - Narrative: "Longing. This is a turning point"
   - Empathy: "Love. She has given him his aloneness back"

2. "Malrik has one hand on his stomach. What does it indicate?"
   - Trust: "Standard archivist posture for concentration"
   - Observation: "Self-containment. He's holding something in"
   - Narrative: "Vulnerability. He's more exposed than he realizes"
   - Empathy: "He feels her. His body knows"

3. "Malrik has not looked up. Does he know she's there?"
   - Trust: "No. His focus is absolute"
   - Observation: "Uncertain. His breathing suggests awareness"
   - Narrative: "Yes, but he's chosen not to acknowledge it"
   - Empathy: "Yes. The fact that he won't look is his answer"

4. "What is the irony in this moment?"
   - Trust: "Distance is sometimes how we show respect"
   - Observation: "When he's most unavailable, he's most visible"
   - Narrative: "Their love is profound because it can't be completed"
   - Empathy: "She sees him most clearly when he doesn't see her"

**Attunement Tracking**:
- Empathy/Narrative choices increase attunement score
- Over game, scores accumulate toward correlation thresholds
- Player doesn't see this happening (emergent mechanic)

---

## IMPLEMENTATION CHECKPOINTS

### Phase 4.1: Dialogue Banking
**Checkpoint**: Write 4 dialogue banks for Malrik (untrained/partial/ready/overqualified)
- [ ] Untrained dialogue: Malrik rejects player, explains why
- [ ] Adjacent skills dialogue: Tala→Malrik path (intuition person meets precision teacher)
- [ ] Ready dialogue: Full glyph trial, reveals emotional vulnerability
- [ ] Overqualified dialogue: Elenya→Malrik path (player has spiritual clarity already)

**Checkpoint**: Write 4 dialogue banks for Elenya
- [ ] Untrained: Tests player's openness before teaching
- [ ] Adjacent (Malrik→Elenya): "You understand systems. Now understand yourself"
- [ ] Ready: Full spiritual teaching, reveals her own struggles
- [ ] Overqualified (Coren→Elenya): "You hold ache well. Come deeper"

**Checkpoint**: Write 4 dialogue banks for Coren (2 aspects)
- [ ] Severance aspect, untrained: Fear-based teaching
- [ ] Severance aspect, ready: Full severance trial
- [ ] Held Ache aspect, untrained: Gentle mediation
- [ ] Held Ache aspect, ready: Deep co-witnessing teaching

### Phase 4.2: Choice System Implementation
**Checkpoint**: Build observational mini-game scene
- [ ] Load Elenya/Malrik scene composition
- [ ] Generate 4 observation prompts
- [ ] Create 4 choice menus (Trust/Observation/Narrative/Empathy)
- [ ] Implement micro-stat shifts (±0.01 to ±0.04)
- [ ] Track attunement score (invisible to player)

**Checkpoint**: Implement correlation threshold detection
- [ ] Check if attunement_score crosses 0.10 threshold → correlate -50%
- [ ] Check if attunement_score crosses 0.25 threshold → correlate 0%
- [ ] Check if attunement_score crosses 0.26 threshold → correlate +50%
- [ ] Log threshold crossing events for testing

### Phase 4.3: Dialogue Variant Population
**Checkpoint**: Create first TONE variant set (Malrik, Ready bank)
- [ ] Trust variant: Focus on reliability, system coherence
- [ ] Observation variant: Focus on noticing, hidden truths
- [ ] Narrative variant: Focus on story arc, turning points
- [ ] Empathy variant: Focus on emotional truth, vulnerability

**Checkpoint**: Test voice consistency
- [ ] All variants maintain Malrik's speech patterns
- [ ] REMNANTS state affects tone (if Resolve high, more open)
- [ ] Counterweights prevent stat runaway
- [ ] Dialogue quality scores record consistency

### Phase 4.4: REMNANTS Dynamic Integration
**Checkpoint**: Implement TONE→REMNANTS mapping
- [ ] High empathy choice → target NPC Empathy +0.02
- [ ] High observation choice → target NPC Narrative +0.02
- [ ] High trust choice → target NPC Resolve +0.02
- [ ] High narrative choice → target NPC Authority change

**Checkpoint**: Test REMNANTS-driven dialogue changes
- [ ] If Malrik Resolve > 7 → unlock vulnerability dialogue
- [ ] If Elenya Empathy > 8 → unlock initiation dialogue
- [ ] If Coren Empathy swings → aspect transitions
- [ ] Log NPC stat evolution across conversation

### Phase 4.5: Scene Mechanics Testing
**Checkpoint**: Swamp Maze implementation
- [ ] Trickster name-shifting at each encounter
- [ ] Four-phase encounter structure
- [ ] Three passage types (false/fog/hidden)
- [ ] Glyph offering based on player path
- [ ] Kaelen identity recovery mechanics (optional)

**Checkpoint**: Dual-Glyph character testing (Sealina)
- [ ] Ache glyph triggers on observer witness
- [ ] Legacy glyph triggers on photograph collection
- [ ] No player participation required
- [ ] Emotional threshold transitions feel natural

**Checkpoint**: Coren aspect mechanics
- [ ] Severance aspect emerges in mountain cult context
- [ ] Held Ache aspect emerges in market mediation context
- [ ] NPC correlations shift based on aspect
- [ ] Player choices influence which aspect dominates

### Phase 4.6: Integration Testing
**Checkpoint**: Full scene flow test
- [ ] Player enters Elenya/Malrik scene
- [ ] Attunement score correctly invisible to player
- [ ] Choice menu generates based on current TONE stats
- [ ] Micro-stats shift correctly on choice selection
- [ ] Correlation updates check thresholds
- [ ] NPC dialogue reflects correlation level

**Checkpoint**: Cross-NPC relationship testing
- [ ] Malrik/Elenya correlation affects their dialogue toward each other
- [ ] Ravi/Nima stat bleed works correctly
- [ ] Coren aspect changes affect surrounding NPCs
- [ ] Player can perceive relationship evolution over game

---

## ADDITIONAL REFERENCE MATERIALS

### Character Voice Reference

**Malrik's Speech Patterns**:
- Authoritative proclamations ("The archives are fractured")
- Abrupt pivots (shifts from technical to emotional without warning)
- Half-explanations (assumes player knows context)
- Impatient clarity mixed with stammering (only with Elenya)
- Thoughts outrun words (speaks in fragments, has to backtrack)
- Internal vs. external contrast (overclocked mind, under-expressive voice)

**Elenya's Speech Patterns**:
- Poetic but grounded (metaphor rooted in sensory experience)
- Questions instead of statements (invites player into discovery)
- Long pauses (listening inward between thoughts)
- Paradox-holding (comfort with contradiction)
- Gentle power (command through presence, not assertion)
- Resting-open quality (always available, never demanding)

**Coren's Dual Speech**:
- **Severance aspect**: Clipped, protective, boundary-emphasizing
- **Held Ache aspect**: Warm, spacious, witnessing-focused

---

### Dialogue Banking Template

For each NPC, create this structure:

```
NPC: [Name]
Glyph: [Name of glyph they teach]
Location: [Where they teach]

BANK A: UNTRAINED
- Greeting: [How they greet untrained player]
- Test: [How they evaluate readiness]
- Rejection: [How they turn player away]
- Follow-up: [What unlocks return]

BANK B: ADJACENT SKILLS
- Recognition: [How they recognize player's unusual path]
- Modified trial: [Adjusted version of glyph trial]
- Bridge dialogue: [How they connect adjacent skills to their teaching]
- Progression: [What unlocks Bank C]

BANK C: READY
- Full trial dialogue
  - Setup: [Scene composition]
  - Observational: [What player witnesses]
  - Choice moments: [TONE-gated choice points]
  - Resolution: [How glyph is earned]
- Post-glyph dialogue: [Reflection on learning]
- Skill gained: [What player learns mechanically]
- Correlation shift: [How this affects other NPCs]

BANK D: OVERQUALIFIED
- Surprise recognition: [How NPC notices unusual preparation]
- Deeper trial: [Advanced version of glyph trial]
- Advanced dialogue: [Deeper insights NPC offers]
- Reciprocal teaching: [Player teaches NPC something]
```

---

**This document is your reference for continuing work. All character architectures, mechanical implementations, dialogue strategies, and integration points are specified here. Use this to guide dialogue banking, choice system implementation, and REMNANTS integration testing.**

---

*Analysis Document Complete - Ready for Implementation Phase*
