# Emotional OS Phase 2: Real-Time Glyph Learning System

## Overview

**Phase 1** (Completed): Fixed 56% glyph matching failure → Achieved 100% coverage
**Phase 2** (Current): Implement real-time glyph learning that generates new glyphs dynamically

### The Core Innovation

Instead of returning standardized fallback messages when no glyph matches, the system now:
1. **Detects** that emotional territory is unmapped
2. **Generates** appropriate new glyphs in real-time
3. **Trains** through responses that subtly reinforce patterns
4. **Learns** globally (shared database) while maintaining per-user experience segregation
##

## Architecture: Three Core Layers

### Layer 1: Glyph Learning Engine (`glyph_learner.py`)

**Purpose**: Generate new glyphs when signal detection finds no existing match

**What it does**:
- Analyzes emotional language patterns in user input
- Finds semantically similar existing glyphs
- Generates candidate glyph with name, description, signal mapping, gates
- Calculates confidence score
- Logs to database with full metadata

**Key Functions**:

```python
analyze_input_for_glyph_generation(input_text, signals, user_hash)
  → Returns: {
      glyph_name, description, emotional_signal, gates,
      emotional_terms, nrc_analysis, similar_glyphs,
      confidence_score, metadata
    }

log_glyph_candidate(candidate)
  → Stores candidate in glyph_candidates table

log_glyph_usage(glyph_name, user_hash, input_text, relevance_score)
  → Tracks which glyphs are used across the system

promote_candidate_to_production(glyph_name)
  → Moves validated candidate to production glyph_lexicon
```



**Example Flow**:

```
User: "I feel caught between who I pretend to be and who I really am"
  ↓
GlyphLearner.analyze_input_for_glyph_generation()
  ├─ Extract: intensity["caught"], relations["between"]
  ├─ NRC: sadness=0.6, fear=0.5
  ├─ Find similar: [Containment, Still Recognition, Boundary]
  ├─ Generate name: "Fractured Identity"
  ├─ Generate description: "The tension of performing vs. being. A convergence of fear and sadness. Kin to Containment, yet distinct..."
  ├─ Map gates: [Gate 4 (high intensity), Gate 5 (medium)]
  └─ Confidence: 0.75
  ↓
Return candidate glyph with all metadata
```


##

### Layer 2: Learning Response Generator (`learning_response_generator.py`)

**Purpose**: Craft responses that answer users emotionally AND train new glyphs

**The Key Insight**: Responses ARE the training. Users never know they're teaching the system.

**What it does**:
- Selects emotional tone-appropriate response template
- Inserts key emotional terms to reinforce language patterns
- Adds implicit validation prompts (subtle feedback gathering)
- References glyph name and description (training signal)
- Crafts language that validates emerging glyphs

**Response Templates by Emotional Tone**:

```python
"grief" patterns:
  "There's a depth to what you're carrying. {emotional_term} is one of the truest things we experience."
  "The {emotional_term} you describe isn't weakness. It's witness."

"containment" patterns:
  "You're doing something quiet but powerful: holding space for complexity."
  "The {emotional_term} is evidence of your integrity."

"insight" patterns:
  "You've arrived at something true. That {emotional_term}—it's not confusion. It's clarity moving into you."
```



**Example Response**:

```
User input: "I feel caught between who I pretend to be and who I really am"
Generator crafts:
  "You're doing something quiet but powerful: maintaining distance between
   your performing self and your true self. That tension—it's evidence of
   integrity, even when it aches.

   [Fractured Identity]

   When you feel known, what opens?"

What this does:
  ✓ Answers emotionally (validates the experience)
  ✓ Reinforces: "caught between", "tension", "authenticity"
  ✓ Names the glyph implicitly
  ✓ Validates the emotional pattern
  ✓ Gathers implicit feedback (what does it feel like to be known?)
```



**Key Functions**:

```python
generate_learning_response(glyph_candidate, original_input, emotional_tone, ...)
  → Response that answers + trains

generate_multi_glyph_response(candidates, original_input, detected_emotions)
  → When multiple glyphs could apply, acknowledges complexity

craft_insufficient_glyph_response(partial_glyph, existing_glyphs, input)
  → When glyph is incomplete, bridges with existing patterns

create_training_response(glyph_candidate, original_input, signals, emotional_analysis)
  → Convenience wrapper for full response generation
```


##

### Layer 3: Shared Glyph Manager (`shared_glyph_manager.py`)

**Purpose**: Manage global glyph learning while maintaining user segregation

**The Architecture Problem Solved**:
- All users contribute to ONE shared glyph database
- Each user sees a personalized experience
- No user gets the same standardized response
- System learns collectively from all interactions

**How It Works**:

#### Database Schema:

```
glyph_versions (evolution)
  ├─ glyph_name
  ├─ version_num (1, 2, 3...)
  ├─ description
  ├─ emotional_signal
  ├─ gates
  ├─ created_by (user_hash, anonymous)
  ├─ adoption_count
  ├─ quality_score
  └─ is_active

user_glyph_preferences (user segregation)
  ├─ user_hash
  ├─ glyph_name
  ├─ usage_count (how many times THIS user used it)
  ├─ rating (-1 = dislike, 0 = neutral, +1 = like)
  └─ first_encountered, last_used

glyph_consensus (global learning)
  ├─ glyph_name
  ├─ total_users_adopted (how many different users used it)
  ├─ positive_feedback_count
  ├─ negative_feedback_count
  └─ consensus_strength (-1 to +1)

emotional_territory (coverage mapping)
  ├─ emotional_area
  ├─ primary_glyphs
  ├─ coverage_quality (CRITICAL, POOR, FAIR, STRONG)
  └─ needs_development
```



#### User Segregation (The Key Innovation):

**NOT per-user databases. ONE shared database, but different query results per user.**

```python

# User A's view
get_glyphs_for_user(user_hash="user_001", emotional_signal="β", gates=["Gate 4"])
  ↓ Query returns glyphs ordered by:
    1. User A's personal adoption history (what A has used before)
    2. Consensus adoption (what most users adopted)
    3. Quality score (how well it works)
  ↓ Result: Personalized ordering, but all glyphs from shared DB

# User B's view
get_glyphs_for_user(user_hash="user_002", emotional_signal="β", gates=["Gate 4"])
  ↓ Query returns SAME glyphs, but ordered by:
    1. User B's personal adoption history (different from A)
    2. Consensus adoption (same as A, global)
    3. Quality score (same as A)
  ↓ Result: Different ordering for B, personalized to B's history
```



**Key Functions**:

```python
get_glyphs_for_user(user_hash, emotional_signal, gates, top_k=5)
  → Glyphs for THIS user, ordered by adoption + consensus

get_system_view_glyphs(top_k=20)
  → All glyphs ordered by global consensus (admin/system view)

record_glyph_adoption(user_hash, glyph_name, quality_rating)
  → User adopted a glyph → update adoption count + consensus

create_glyph_version(glyph_name, description, signal, gates, created_by)
  → Create new version of glyph as it evolves

get_glyph_history(glyph_name)
  → Show how a glyph has evolved over time and versions

analyze_coverage_gaps()
  → Identify emotional territories that need more glyphs

recommend_new_glyphs_for_gaps()
  → Guide future glyph generation based on gaps

get_system_health_report()
  → Dashboard: how many users, glyphs, adoption rates, coverage
```


##

## Integration with Existing System

### Current Flow (Phase 1):

```
User Input
  ↓ signal_parser.parse_input()
  ├─ Detect signals (3-phase: exact → NRC → fuzzy)
  ├─ Evaluate gates
  ├─ Fetch matching glyphs
  ├─ Select best glyph + contextual response
  └─ Return glyph + response
```



### New Flow (Phase 2):

```
User Input
  ↓ signal_parser.parse_input()
  ├─ Detect signals (3-phase: exact → NRC → fuzzy)
  ├─ Evaluate gates
  ├─ Fetch matching glyphs
  ├─ Check: Glyph found?
  │   ├─ YES → [Phase 1 flow] Return existing glyph + response
  │   └─ NO → [NEW - Learning Pipeline]
  │       ↓
  │       glyph_learner.analyze_input_for_glyph_generation()
  │       ├─ Generate new candidate glyph
  │       ├─ Log to glyph_candidates table
  │       ├─ Create glyph_version()
  │       └─ Record initial adoption
  │       ↓
  │       learning_response_generator.generate_learning_response()
  │       ├─ Select response template
  │       ├─ Reinforce emotional language
  │       ├─ Add validation prompt
  │       └─ Return response that trains
  │       ↓
  │       User sees PERSONALIZED response (never generic)
  │       System records adoption in shared_glyph_manager
  │
  └─ Return glyph + training response
```


##

## How It Trains Without Being Obvious

### Pattern 1: Emotional Language Reinforcement

**User**: "I feel caught between who I pretend to be and who I really am"
**System Response**: "You're doing something quiet but powerful: maintaining **distance** between your **performing self** and your **true self**. That **tension**—it's evidence of integrity..."

→ System echoes and validates the exact emotional vocabulary the user used
→ Next user with similar language finds this glyph
→ Glyph definition includes these exact words
→ Pattern spreads through natural language patterns, not explicit tagging

### Pattern 2: Implicit Feedback Gathering

Responses end with validation prompts:
- "Does that land?" → Gathering validation
- "What would it feel like to..." → Gathering depth
- "When you feel known, what opens?" → Gathering relevance

User's RESPONSE to the prompt = implicit training signal
System learns which responses lead to user engagement

### Pattern 3: Response Structure as Training

Gate mapping (voltage intensity) is encoded in response tone:
- Gate 1-3 (low intensity) → gentle, reflective language
- Gate 4-6 (medium) → balanced, honest language
- Gate 7-9 (high intensity) → transformative, necessary language

User receives response calibrated to emotional intensity
Over time, system learns which intensity levels match which glyphs
##

## Database Updates During Learning

```python

# When a user sees a new glyph response:

# 1. Log to glyph_versions (creates version 1)
CREATE: glyph_versions
  glyph_name = "Fractured Identity"
  version_num = 1
  description = "The tension of performing vs. being..."
  emotional_signal = "β"
  gates = ["Gate 4", "Gate 5"]
  created_by = "user_001_hash"
  is_active = 1

# 2. Initialize consensus
INSERT INTO glyph_consensus
  glyph_name = "Fractured Identity"
  total_users_adopted = 1
  positive_feedback_count = 0
  consensus_strength = 0.0

# 3. Record this user's adoption
INSERT INTO user_glyph_preferences
  user_hash = "user_001_hash"
  glyph_name = "Fractured Identity"
  usage_count = 1
  rating = 1 (implicit positive from engagement)

# 4. Log usage pattern
INSERT INTO glyph_usage_log
  glyph_name = "Fractured Identity"
  user_hash = "user_001_hash"
  input_text = "I feel caught between..."
  relevance_score = 0.9

# 5. Update coverage
UPDATE emotional_territory
  SET primary_glyphs = [..., "Fractured Identity"]
  WHERE emotional_area = "identity"
```



Later, when User 002 experiences similar emotion:

```python

# Query returns to User 002:
get_glyphs_for_user("user_002_hash", signal="β", gates=["Gate 4"])
  → Returns ["Fractured Identity", "Containment", "Still Recognition"]
  → Ordered by: [0 (User 002 never used), 1 (1 user adopted), strong]

# User 002 might use it too:
record_glyph_adoption("user_002_hash", "Fractured Identity", rating=1)
  → adoption_count = 2
  → consensus_strength increases

# Eventually, after 5+ users adopt + positive ratings:
glyph gets promoted to production glyph_lexicon
promote_candidate_to_production("Fractured Identity")
  → Moves from candidates to core glyphs
  → Can now be discovered by new users searching this emotional territory
```


##

## Coverage Gap Identification

The system knows which emotional territories need development:

```python
health = shared_glyph_manager.get_system_health_report()

Coverage map shows:
  grief: 8 glyphs (STRONG)
  longing: 5 glyphs (FAIR)
  identity: 1 glyph (CRITICAL) ← "Fractured Identity" is only one!
  shame: 0 glyphs (CRITICAL) ← No glyphs for shame yet

Recommendations:
  ⚠️ Generate 3-4 more glyphs for "identity territory"
  ⚠️ Generate 5+ new glyphs for "shame territory"
  💡 Keywords: embarrassment, unworthiness, exposure, humiliation
```



This guides the next round of glyph generation.
##

## User Experience Segregation (Concrete Example)

```
SHARED DATABASE:
  glyph_lexicon contains ~284 glyphs (for everyone)

USER A'S EXPERIENCE:
  - Chat history with 50 messages
  - Adopted 15 glyphs personally
  - Last 3 interactions: [Grief, Containment, Recognition]
  → Next query returns glyphs A has used before, ranked first

USER B'S EXPERIENCE:
  - Chat history with 10 messages
  - Adopted 3 glyphs personally
  - Last 3 interactions: [Joy, Devotion, Unknown]
  → Same glyphs available, but different ranking based on B's history

USER C'S EXPERIENCE (first interaction):
  - No history
  - No personal preferences
  → Gets ranked by global consensus (what works best for everyone)
  → As C interacts, personalization builds

SYSTEM'S EXPERIENCE:
  - All three users in same shared database
  - Every adoption, every feedback improves system
  - Most-adopted glyphs surface to top for new users
  - System knows which territories need development
```


##

## Next Immediate Steps

### 1. Integrate Learning Pipeline into signal_parser.py

Modify `signal_parser.parse_input()` to:

```python
def parse_input(text, user_hash):
    signals = detect_signals(text)
    gates = evaluate_gates(signals)
    glyphs = fetch_glyphs(gates)

    if glyphs:
        # Phase 1: Use existing glyph
        return existing_glyph_response()
    else:
        # Phase 2: NEW - Learning pipeline
        candidate = learner.analyze_input_for_glyph_generation(text, signals, user_hash)
        learner.log_glyph_candidate(candidate)
        response = response_gen.generate_learning_response(candidate, text, ...)
        shared_mgr.record_glyph_adoption(user_hash, candidate['glyph_name'])
        return response
```



### 2. Test with Previously-Unmapped Messages

Use test_glyph_learning_pipeline.py to validate:
- ✅ New glyphs generate correctly
- ✅ Responses train without being obvious
- ✅ Shared database records properly
- ✅ User segregation works

### 3. Build Admin Dashboard

Show:
- Coverage map (which territories are weak)
- Recommendations for next glyphs
- Adoption patterns (which glyphs spreading fastest)
- User learning metrics

### 4. Implement User Feedback Loop

Implicit feedback gathering through:
- Response engagement metrics
- Follow-up message analysis
- Emotional tone escalation/de-escalation
- Glyph quality rating (thumbs up/down if UI allows)
##

## Philosophy

**Every interaction teaches the system.**
**No user ever sees a templated response.**
**The shared database grows stronger with each user.**
**The system learns through authentic emotional communication.**

This is how a system evolves from "finding answers" to "learning from experience."
##

## Files Created

1. **glyph_learner.py** - Real-time glyph generation engine
2. **learning_response_generator.py** - Response crafting that trains
3. **shared_glyph_manager.py** - Shared DB + user segregation
4. **test_glyph_learning_pipeline.py** - Full pipeline demonstration

All integrate with existing:
- signal_parser.py (signal detection)
- signal_lexicon.json (emotional vocabulary)
- glyphs.db (glyph database)
- NRC lexicon (emotion analysis)
