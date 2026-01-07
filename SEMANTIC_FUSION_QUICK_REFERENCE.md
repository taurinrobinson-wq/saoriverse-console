"""
🎭 SEMANTIC + REMNANTS FUSION: QUICK REFERENCE
==============================================

This is the cheat sheet. The mapping tables, the equations, the quick lookups.

═══════════════════════════════════════════════════════════════════════════════
STAGE 1: SEMANTIC LAYER EXTRACTION
═══════════════════════════════════════════════════════════════════════════════

SemanticLayer extracted from player message contains:

EMOTIONAL_STANCE options:
  BRACING      → Player pulling back, protecting
  REVEALING    → Player opening up
  AMBIVALENT   → Player holding two things
  COLLAPSING   → Player falling apart
  DEFENSIVE    → Player defending against threat
  SEEKING      → Player looking for connection

DISCLOSURE_PACE options:
  TESTING_SAFETY      → "Is it safe to open up?"
  GRADUAL_REVEAL      → "I'll share slowly"
  CONTEXTUAL_GROUNDING → "Here's background"
  EMOTIONAL_EMERGENCE  → "It's coming to the surface"

POWER_DYNAMICS (can be multiple):
  AGENCY_LOSS     → Player felt powerless
  SELF_PROTECTION → Player defending autonomy
  DOMINANCE       → Player exerting control
  SUBMISSION      → Player yielding

IMPLIED_NEEDS (can be multiple):
  SAFETY         → "I'm not safe"
  AUTONOMY       → "I need control"
  VALIDATION     → "Am I okay?"
  UNDERSTANDING  → "Do you get it?"
  CONNECTION     → "Don't leave me"
  RESPECT        → "Treat me seriously"

EMOTIONAL_WEIGHT: 0.0 to 1.0
  < 0.3  = Calm, measured
  0.3-0.7 = Balanced
  > 0.7  = Intense, activated

IDENTITY_SIGNALS: List of wounds/essences mentioned in speech


═══════════════════════════════════════════════════════════════════════════════
STAGE 2: SEMANTIC → TONE MAPPING
═══════════════════════════════════════════════════════════════════════════════

TONE EFFECTS (standardized output of ToneMapper):
  empathy     → How warmly the NPC responds
  resolve     → How firmly committed to a course
  trust       → How trusting the NPC is being
  need        → How much the NPC emphasizes relational language
  authority   → How directive vs collaborative
  nuance      → How much the NPC acknowledges complexity
  skepticism  → How questioning/challenging
  memory      → How much the NPC references prior states
  courage     → How brave/vulnerable the NPC is willing to be


TONE MAPPING TABLE (STANCE → TONE)
────────────────────────────────────

BRACING:
  courage        → +0.15
  empathy        → -0.10
  skepticism     → +0.10

REVEALING:
  empathy        → +0.20
  trust          → +0.15
  memory         → +0.10

AMBIVALENT:
  nuance         → +0.25
  empathy        → +0.10
  memory         → +0.15

COLLAPSING:
  need           → +0.25
  authority      → -0.15
  empathy        → +0.20

DEFENSIVE:
  skepticism     → +0.20
  trust          → -0.15
  authority      → +0.10

SEEKING:
  empathy        → +0.25
  trust          → +0.20


TONE MAPPING TABLE (PACING → TONE)
───────────────────────────────────

TESTING_SAFETY:
  need           → +0.20
  trust          → +0.05
  skepticism     → +0.10

GRADUAL_REVEAL:
  trust          → +0.15
  empathy        → +0.10

CONTEXTUAL_GROUNDING:
  memory         → +0.20
  nuance         → +0.10

EMOTIONAL_EMERGENCE:
  empathy        → +0.20
  authority      → -0.10
  need           → +0.15


TONE MAPPING TABLE (POWER DYNAMICS → TONE)
──────────────────────────────────────────

AGENCY_LOSS:
  need           → +0.20
  authority      → -0.20
  empathy        → +0.15

SELF_PROTECTION:
  skepticism     → +0.15
  authority      → +0.10
  trust          → -0.10

DOMINANCE:
  authority      → +0.20
  empathy        → -0.10

SUBMISSION:
  need           → +0.15
  authority      → -0.15


TONE MAPPING TABLE (IMPLIED NEEDS → TONE)
─────────────────────────────────────────

SAFETY:
  empathy        → +0.20
  authority      → +0.10

AUTONOMY:
  authority      → +0.15
  need           → -0.10

VALIDATION:
  empathy        → +0.25
  memory         → +0.15

UNDERSTANDING:
  nuance         → +0.20
  memory         → +0.15

CONNECTION:
  empathy        → +0.20
  need           → +0.20

RESPECT:
  authority      → +0.15
  empathy        → +0.10


TONE MAPPING TABLE (EMOTIONAL WEIGHT → TONE)
────────────────────────────────────────────

WEIGHT > 0.7 (High intensity):
  memory         → +0.20
  empathy        → +0.15
  skepticism     → -0.10

WEIGHT < 0.3 (Low intensity):
  skepticism     → +0.15
  need           → -0.10
  authority      → +0.10


TONE NORMALIZATION
──────────────────

All TONE values clamped to [-1.0, 1.0] range:
  tone[key] = max(-1.0, min(1.0, tone[key]))

All canonical TONE keys must exist in output (set to 0.0 if not explicitly set):
  empathy, resolve, trust, need, authority, nuance, skepticism, memory, courage


═══════════════════════════════════════════════════════════════════════════════
STAGE 3: TONE → REMNANTS
═══════════════════════════════════════════════════════════════════════════════

TONE effects flow into NPCManager.apply_tone_effects(npc_id, tone_effects):

  remnants[trait] += tone_effects[mapped_trait]
  remnants[trait] = max(-1.0, min(1.0, remnants[trait]))  # clamp to [-1, 1]

Example:
  TONE: {empathy: 0.2, trust: 0.15}
  Nima's REMNANTS before: {empathy: 0.3, trust: 0.2, ...}
  Nima's REMNANTS after: {empathy: 0.5, trust: 0.35, ...}

REMNANTS TRAITS (8 total):
  empathy     → How warmly responsive
  trust       → How trusting
  need        → How much seeking relational connection
  authority   → How directive
  nuance      → How complex-thinking
  skepticism  → How questioning
  memory      → How referential to prior states
  resolve     → How committed to course


═══════════════════════════════════════════════════════════════════════════════
STAGE 4: REMNANTS → BLOCK PRIORITY ADJUSTMENT
═══════════════════════════════════════════════════════════════════════════════

BLOCK MODIFICATION RULES

────────────────────────────────────────────────────────────────────────────────
EMPATHY-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF empathy > 0.7 (high empathy):
  VALIDATION          → +1.5 boost
  ACKNOWLEDGMENT      → +1.5 boost
  SAFETY              → +1.5 boost
  TOGETHERNESS        → +1.5 boost
  RELATIONAL          → +1.5 boost
  CHALLENGE           → -0.5 reduce
  DISTANCE            → -0.5 reduce
  SKEPTICISM          → -0.5 reduce

IF empathy < 0.3 (low empathy):
  CHALLENGE           → +1.0 boost
  DISTANCE            → +1.0 boost
  INDEPENDENCE        → +1.0 boost
  SKEPTICISM          → +1.0 boost
  DOUBT               → +1.0 boost
  VALIDATION          → -0.5 reduce
  ACKNOWLEDGMENT      → -0.5 reduce
  TOGETHERNESS        → -0.5 reduce

────────────────────────────────────────────────────────────────────────────────
SKEPTICISM-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF skepticism > 0.7 (high skepticism):
  AMBIVALENCE         → +1.5 boost
  DOUBT               → +1.5 boost
  CHALLENGE           → +1.5 boost
  QUESTIONING         → +1.5 boost
  CAUTION             → +1.5 boost
  AGREEMENT           → -1.0 reduce
  OPENNESS            → -1.0 reduce
  TRUST               → -1.0 reduce

IF skepticism < 0.3 (low skepticism):
  AGREEMENT           → +1.0 boost
  OPENNESS            → +1.0 boost
  SAFETY              → +1.0 boost
  TRUST               → +1.0 boost
  VALIDATION          → +1.0 boost
  DOUBT               → -0.5 reduce
  CHALLENGE           → -0.5 reduce
  QUESTIONING         → -0.5 reduce

────────────────────────────────────────────────────────────────────────────────
AUTHORITY-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF authority > 0.7 (high authority):
  GENTLE_DIRECTION    → +1.5 boost
  WISDOM              → +1.5 boost
  COMMITMENT          → +1.5 boost
  CONVICTION          → +1.5 boost
  SUGGESTION          → +1.5 boost
  UNCERTAINTY         → -0.5 reduce
  QUESTIONING         → -0.5 reduce
  EXPLORATION         → -0.5 reduce

IF authority < 0.3 (low authority):
  QUESTIONING         → +1.0 boost
  EXPLORATION         → +1.0 boost
  UNCERTAINTY         → +1.0 boost
  VULNERABILITY       → +1.0 boost
  AMBIVALENCE         → +1.0 boost
  COMMITMENT          → -0.5 reduce
  CONVICTION          → -0.5 reduce
  GENTLE_DIRECTION    → -0.5 reduce

────────────────────────────────────────────────────────────────────────────────
NEED-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF need > 0.7 (high need):
  CONTAINMENT         → +1.5 boost
  TOGETHERNESS        → +1.5 boost
  RELATIONAL          → +1.5 boost
  SAFETY              → +1.5 boost
  ACKNOWLEDGMENT      → +1.5 boost
  INDEPENDENCE        → -0.5 reduce
  DISTANCE            → -0.5 reduce
  SOLITUDE            → -0.5 reduce

IF need < 0.3 (low need):
  INDEPENDENCE        → +1.0 boost
  SOLITUDE            → +1.0 boost
  DISTANCE            → +1.0 boost
  EXPLORATION         → +1.0 boost
  CONTAINMENT         → -0.5 reduce
  TOGETHERNESS        → -0.5 reduce
  RELATIONAL          → -0.5 reduce

────────────────────────────────────────────────────────────────────────────────
TRUST-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF trust > 0.7 (high trust):
  COLLABORATION       → +1.5 boost
  OPENNESS            → +1.5 boost
  AGREEMENT           → +1.5 boost
  VULNERABILITY       → +1.5 boost
  RELATIONAL          → +1.5 boost

IF trust < 0.3 (low trust):
  CAUTION             → +1.5 boost
  PROTECTION          → +1.5 boost
  SKEPTICISM          → +1.5 boost
  DISTANCE            → +1.5 boost
  DOUBT               → +1.5 boost
  COLLABORATION       → -1.0 reduce
  OPENNESS            → -1.0 reduce
  VULNERABILITY       → -1.0 reduce

────────────────────────────────────────────────────────────────────────────────
MEMORY-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF memory > 0.7 (high memory):
  CONTINUITY          → +1.5 boost
  REFERENCE           → +1.5 boost
  HISTORY             → +1.5 boost

IF memory < 0.3 (low memory):
  PRESENT             → +1.0 boost
  NOVELTY             → +1.0 boost
  IMMEDIACY           → +1.0 boost

────────────────────────────────────────────────────────────────────────────────
RESOLVE-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF resolve > 0.7 (high resolve):
  COMMITMENT          → +1.5 boost
  CONVICTION          → +1.5 boost
  BREAKTHROUGH        → +1.5 boost

IF resolve < 0.3 (low resolve):
  AMBIVALENCE         → +1.0 boost
  UNCERTAINTY         → +1.0 boost
  QUESTIONING         → +1.0 boost

────────────────────────────────────────────────────────────────────────────────
COURAGE-BASED MODULATION
────────────────────────────────────────────────────────────────────────────────

IF courage > 0.7 (high courage):
  VULNERABILITY       → +1.5 boost
  BREAKTHROUGH        → +1.5 boost
  COMMITMENT          → +1.5 boost

IF courage < 0.3 (low courage):
  PROTECTION          → +1.0 boost
  RETREAT             → +1.0 boost
  CAUTION             → +1.0 boost
  DISTANCE            → +1.0 boost


═══════════════════════════════════════════════════════════════════════════════
STAGE 5: FACTION PRIORITY OVERRIDES
═══════════════════════════════════════════════════════════════════════════════

FACTION NUDGE TABLE

────────────────────────────────────────────────────────────────────────────────
NIMA FACTION ("We Hold")
────────────────────────────────────────────────────────────────────────────────
Philosophy: Emotional weight can be metabolized and transformed

BOOSTS:
  CONTAINMENT         → +1.5  (specialty: holding weight)
  PACING              → +1.0  (slow, deliberate processing)
  VALIDATION          → +1.0  (confirmation of reality)
  TOGETHERNESS        → +1.5  (shared presence heals)
  ACKNOWLEDGMENT      → +1.0  (naming the loss)
  PROCESSING          → +1.5  (work of transformation)
  RELATIONAL          → +1.0  (bonds deepen in grief)

REDUCTIONS:
  ESCAPE              → -0.5  (griever doesn't flee)
  SUPPRESSION         → -1.0  (face what happened)
  DENIAL              → -1.0  (truth-telling required)

────────────────────────────────────────────────────────────────────────────────
ELENYA FACTION ("We Saw")
────────────────────────────────────────────────────────────────────────────────
Philosophy: Witnessing violence changes the witness

BOOSTS:
  IDENTITY_INJURY     → +1.5  (seeing changes who you are)
  AMBIVALENCE         → +1.5  (hold two truths)
  MEMORY              → +1.5  (cannot forget)
  QUESTIONING         → +1.0  (why? how?)
  VULNERABILITY       → +1.0  (reveal wounds)
  PROCESSING          → +1.0  (making sense)
  NUANCE              → +1.0  (understand complexity)

REDUCTIONS:
  CERTAINTY           → -1.0  (certainty impossible)
  JUDGMENT            → -1.0  (suspend judgment)
  SIMPLIFICATION      → -0.5  (world not simple)
  DENIAL              → -1.0  (cannot unsee)

────────────────────────────────────────────────────────────────────────────────
MALRIK FACTION ("We Show the Way")
────────────────────────────────────────────────────────────────────────────────
Philosophy: Direction comes from wisdom, not force

BOOSTS:
  GENTLE_DIRECTION    → +1.5  (suggesting paths)
  WISDOM              → +1.5  (drawing on experience)
  ACKNOWLEDGMENT      → +1.0  (validate starting point)
  COLLABORATION       → +1.5  (walk alongside)
  QUESTIONING         → +1.0  (open possibilities)
  VALIDATION          → +1.0  (affirm wisdom within)
  RELATIONAL          → +1.0  (relationship transforms)

REDUCTIONS:
  DOMINANCE           → -1.0  (don't impose)
  CONTROL             → -1.0  (respect autonomy)
  JUDGMENT            → -0.5  (suspend judgment)
  DEMAND              → -1.0  (request not demand)

────────────────────────────────────────────────────────────────────────────────
COREN FACTION ("We Remember")
────────────────────────────────────────────────────────────────────────────────
Philosophy: Continuity and memory preserve identity

BOOSTS:
  CONTINUITY          → +1.5  (connect past to present)
  REFERENCE           → +1.5  (call upon shared history)
  HISTORY             → +1.5  (our story matters)
  MEMORY              → +1.0  (remembering preserves)
  COMMITMENT          → +1.5  (vows endure)
  ACKNOWLEDGMENT      → +1.0  (honor what came before)
  RELATIONAL          → +1.0  (bonds of continuity)

REDUCTIONS:
  RUPTURE             → -1.0  (work against rupture)
  FORGETTING          → -1.0  (vow against forgetting)
  NOVELTY             → -0.5  (change within continuity)
  SEVERING            → -1.0  (maintain bonds)


═══════════════════════════════════════════════════════════════════════════════
STAGE 6: PERSONA STYLING
═══════════════════════════════════════════════════════════════════════════════

REMNANTS-BASED TEXT MODULATION

────────────────────────────────────────────────────────────────────────────────
EMPATHY-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF empathy > 0.7 (high empathy):
  Call _soften_edges():
    Replace absolutes with emotional qualifications
    Add internal pauses ("—")
    Use more relational language
    Reduce harsh declarations

IF empathy < 0.3 (low empathy):
  Call _sharpen_edges():
    Remove hedging
    Make more direct
    Use absolutes
    Less relational language

────────────────────────────────────────────────────────────────────────────────
SKEPTICISM-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF skepticism > 0.7 (high skepticism):
  Call _sharpen_edges():
    Cut through sentiment
    Make more challenging
    Express doubt

IF skepticism < 0.3 (low skepticism):
  Call _reduce_skepticism():
    Add trust language
    Remove doubt markers
    Be more believing

────────────────────────────────────────────────────────────────────────────────
AUTHORITY-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF authority > 0.7 (high authority):
  Call _reduce_hedging():
    Remove qualifiers (maybe, perhaps, I think)
    "I think maybe..." → "I..."
    "It seems like" → "It is"
    More directive

IF authority < 0.3 (low authority):
  Call _add_hedging():
    Add qualifiers
    Be more tentative
    "I..." → "I think... I mean, I..."

────────────────────────────────────────────────────────────────────────────────
NEED-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF need > 0.7 (high need):
  Call _add_warmth():
    Use "we" and "us" more
    Add relational pronouns
    Emphasize shared experience
    "I understand" → "I understand, and I'm here with you"

────────────────────────────────────────────────────────────────────────────────
MEMORY-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF memory > 0.7 (high memory):
  Call _add_memory_reference():
    Reference prior conversation
    Call back to mentioned people/events
    "Like when..." language
    "Remember..." references

IF memory < 0.3 (low memory):
  Focus on immediate, present

────────────────────────────────────────────────────────────────────────────────
TRUST-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF trust < 0.3 (low trust):
  Call _express_doubt():
    Add uncertainty markers
    "...or at least, I think so"
    Question own statements

────────────────────────────────────────────────────────────────────────────────
RESOLVE-BASED STYLING
────────────────────────────────────────────────────────────────────────────────

IF resolve < 0.3 (low resolve):
  Call _introduce_uncertainty():
    "will" → "might will"
    "must" → "might must"
    Add wavering to commitment statements


═══════════════════════════════════════════════════════════════════════════════
QUICK LOOKUP: WHAT EACH STAGE DOES
═══════════════════════════════════════════════════════════════════════════════

Stage 1: PARSE SEMANTIC
  INPUT: Player message text
  OUTPUT: SemanticLayer (stance, pacing, needs, weight, identity_signals)
  PURPOSE: Extract emotional meaning

Stage 2: SEMANTIC → TONE
  INPUT: SemanticLayer
  OUTPUT: TONE effects Dict[str, float]
  PURPOSE: Convert semantic findings to standardized emotional signals

Stage 3: APPLY TONE TO REMNANTS
  INPUT: TONE effects, NPC REMNANTS
  OUTPUT: Updated NPC REMNANTS
  PURPOSE: NPC emotional state evolves based on player approach

Stage 4: GET BLOCKS & PRIORITIES
  INPUT: NPC name, context
  OUTPUT: Block list, initial priorities
  PURPOSE: Available dialogue options and their base relevance

Stage 5: ADJUST BY REMNANTS
  INPUT: Block priorities, NPC REMNANTS
  OUTPUT: Adjusted priorities
  PURPOSE: Emotional state shapes what dialogue is emphasized

Stage 6: APPLY FACTION NUDGES
  INPUT: Adjusted priorities, NPC faction
  OUTPUT: Final priorities
  PURPOSE: Faction philosophy shapes emphasis

Stage 7: COMPOSE RESPONSE
  INPUT: Blocks, final priorities
  OUTPUT: Text composed from top blocks
  PURPOSE: Create semantically coherent response

Stage 8: APPLY STYLING
  INPUT: Composed text, NPC persona, REMNANTS
  OUTPUT: Styled response
  PURPOSE: Make response sound like NPC in their emotional state

Stage 9: RECORD QUALITY
  INPUT: All data from stages 1-8
  OUTPUT: DialogueQuality metric
  PURPOSE: Track dialogue quality and emotional arc


═══════════════════════════════════════════════════════════════════════════════
CRITICAL NUMBERS
═══════════════════════════════════════════════════════════════════════════════

THRESHOLDS:

High trait activation:  trait > 0.7
Low trait activation:   trait < 0.3
Saturation:             trait = 1.0 (maximum)
Minimum:                trait = -1.0 or 0.0

BOOST/REDUCE AMOUNTS:

  Strong boost:    +1.5
  Medium boost:    +1.0
  Weak boost:      +0.5
  
  Weak reduce:     -0.5
  Medium reduce:   -1.0
  Strong reduce:   -1.5

TONE DELTA EXAMPLES:

  High empathy approach:
    empathy:   +0.2 to +0.3
    trust:     +0.1 to +0.2
    need:      +0.1 to +0.2
  
  Dismissive approach:
    empathy:   -0.1 to -0.2
    trust:     -0.1 to -0.15
    skepticism: +0.1 to +0.2


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE: QUICK CALCULATION
═══════════════════════════════════════════════════════════════════════════════

PLAYER: "I'll sit with you quietly for a moment."

Stage 1: Parse Semantic
  emotional_stance: SEEKING
  disclosed_pace: TESTING_SAFETY
  implied_needs: [SAFETY, CONNECTION, VALIDATION]
  emotional_weight: 0.7

Stage 2: Semantic → TONE
  From SEEKING:        empathy +0.25, trust +0.20
  From TESTING_SAFETY: need +0.20, trust +0.05
  From SAFETY:         empathy +0.20, authority +0.10
  From CONNECTION:     empathy +0.20, need +0.20
  From VALIDATION:     empathy +0.25, memory +0.15
  From weight 0.7:     memory +0.20, empathy +0.15, skepticism -0.10
  
  Total TONE:
    empathy:   +1.05 → clamp to +1.0
    trust:     +0.25
    need:      +0.40
    authority: +0.10
    memory:    +0.35
    skepticism: -0.10

Stage 3: Apply to NPC REMNANTS
  Nima before: empathy 0.3, trust 0.2
  Nima after:  empathy 1.0, trust 0.45

Stage 4-8: Blocks → Priorities → Styling
  High empathy triggers:
    - VALIDATION/ACKNOWLEDGMENT/TOGETHERNESS blocks boosted
    - Softened word choice in final response
    - Relational language emphasized

RESULT: Nima opens up, shows vulnerability


═══════════════════════════════════════════════════════════════════════════════
"""

print(__doc__)
