#!/usr/bin/env python3
"""
PHASE 2 QUICK REFERENCE CARD

One-page summary of everything you need to know to integrate and use
the real-time glyph learning system.

Print this out or pin it in your IDE.
"""

# ============================================================================
# THE SYSTEM IN ONE PARAGRAPH
# ============================================================================

"""
When signal_parser finds no matching glyph, instead of returning None or a 
generic message, the learning pipeline:
1. Analyzes the emotional language patterns
2. Generates a new glyph candidate (name, description, gates)
3. Logs it to the database
4. Crafts a response that answers emotionally AND trains the system
5. Returns the response (never None)

Result: Every user interaction teaches the system. Every response is personal.
The database grows from every interaction.
"""

# ============================================================================
# THE THREE MODULES YOU NEED TO KNOW
# ============================================================================

"""
1. GLYPH LEARNER (glyph_learner.py)
   ─────────────────────────────────
   When: No matching glyph found
   What: Generates new glyph candidate
   Entry point: learner.analyze_input_for_glyph_generation(text, signals, user_hash)
   Output: {glyph_name, description, emotional_signal, gates, confidence_score, ...}

2. LEARNING RESPONSE GENERATOR (learning_response_generator.py)
   ────────────────────────────────────────────────────────────
   When: Need to respond to user about new/learning glyph
   What: Crafts response that answers + trains
   Entry point: response_gen.generate_learning_response(candidate, text, tone, ...)
   Output: String response with emotional validation + implicit training signals

3. SHARED GLYPH MANAGER (shared_glyph_manager.py)
   ───────────────────────────────────────────
   When: Need to manage global learning + user segregation
   What: Handles database, adoption tracking, consensus, coverage gaps
   Entry points:
     • get_glyphs_for_user(user_hash, signal, gates)
     • record_glyph_adoption(user_hash, glyph_name, rating)
     • get_system_health_report()
     • recommend_new_glyphs_for_gaps()
"""

# ============================================================================
# HOW TO INTEGRATE (3 STEPS)
# ============================================================================

"""
STEP 1: Add imports to signal_parser.py
─────────────────────────────────────────
from emotional_os.glyphs.glyph_learner import GlyphLearner
from emotional_os.glyphs.learning_response_generator import LearningResponseGenerator
from emotional_os.glyphs.shared_glyph_manager import SharedGlyphManager

_glyph_learner = GlyphLearner()
_learning_response_gen = LearningResponseGenerator()
_shared_glyph_manager = SharedGlyphManager()


STEP 2: Modify parse_input() function
──────────────────────────────────────
def parse_input(text: str, user_hash: Optional[str] = None) -> Dict:
    # ... existing code to detect signals and evaluate gates ...
    
    glyphs = fetch_glyphs(gates)
    
    if glyphs:
        # EXISTING: Use matching glyph
        best_glyph, response = select_best_glyph_and_response(glyphs, signals, text)
        _shared_glyph_manager.record_glyph_adoption(user_hash, best_glyph)
        return {"best_glyph": best_glyph, "voltage_response": response, ...}
    else:
        # NEW: Learning pipeline
        candidate = _glyph_learner.analyze_input_for_glyph_generation(text, signals, user_hash)
        _glyph_learner.log_glyph_candidate(candidate)
        
        glyph_name = candidate.get("glyph_name")
        _shared_glyph_manager.create_glyph_version(
            glyph_name, 
            candidate.get("description"),
            candidate.get("emotional_signal"),
            candidate.get("gates"),
            user_hash
        )
        _shared_glyph_manager.record_glyph_adoption(user_hash, glyph_name, quality_rating=1)
        
        response = _learning_response_gen.generate_learning_response(
            candidate, text, 
            emotional_tone=_determine_emotional_tone(signals),
            emotional_terms=candidate.get("emotional_terms"),
            nrc_analysis=candidate.get("nrc_analysis")
        )
        
        return {"best_glyph": glyph_name, "voltage_response": response, ...}


STEP 3: Add helper function
────────────────────────────
def _determine_emotional_tone(signals):
    if not signals:
        return "unknown"
    tone_map = {
        "grief": "grief",
        "longing": "longing",
        "containment": "containment",
        "insight": "insight",
        "joy": "joy",
        "devotion": "devotion",
        "recognition": "recognition",
        "unknown": "unknown"
    }
    return tone_map.get(signals[0].get("tone", "unknown"), "unknown")
"""

# ============================================================================
# DATABASE SCHEMA (WHAT GETS CREATED)
# ============================================================================

"""
When you initialize, these tables are created in glyphs.db:

NEW TABLES:
──────────
glyph_candidates
  ├─ glyph_name
  ├─ description
  ├─ emotional_signal
  ├─ gates (JSON list)
  ├─ source_input (user's text)
  ├─ created_by (user_hash)
  ├─ confidence_score
  └─ promoted_to_production (0/1)

glyph_versions
  ├─ glyph_name
  ├─ version_num (1, 2, 3...)
  ├─ description
  ├─ emotional_signal
  ├─ gates
  ├─ created_by
  ├─ adoption_count
  ├─ quality_score
  └─ is_active (current version or old?)

user_glyph_preferences
  ├─ user_hash
  ├─ glyph_name
  ├─ usage_count
  ├─ rating (-1/0/+1)
  └─ first_encountered, last_used

glyph_consensus
  ├─ glyph_name
  ├─ total_users_adopted
  ├─ positive_feedback_count
  ├─ negative_feedback_count
  └─ consensus_strength (-1 to +1)

emotional_territory
  ├─ emotional_area (grief, longing, etc)
  ├─ primary_glyphs
  ├─ coverage_quality
  └─ needs_development (0/1)

EXISTING TABLES:
────────────────
glyph_lexicon (unchanged)
glyph_usage_log (retained)
emotional_patterns (retained)
"""

# ============================================================================
# KEY METHODS CHEATSHEET
# ============================================================================

"""
GLYPH LEARNER:
──────────────
learner.analyze_input_for_glyph_generation(text, signals, user_hash)
  → Analyzes input, returns complete glyph candidate

learner.log_glyph_candidate(candidate)
  → Stores to glyph_candidates table

learner.log_glyph_usage(glyph_name, user_hash, input_text, relevance_score)
  → Track which glyphs are used

learner.promote_candidate_to_production(glyph_name)
  → Move candidate to glyph_lexicon after validation


LEARNING RESPONSE GENERATOR:
────────────────────────────
response_gen.generate_learning_response(candidate, text, tone, terms, nrc)
  → Complete response that trains

response_gen.generate_multi_glyph_response(candidates, text, emotions)
  → When multiple glyphs could apply

response_gen.craft_insufficient_glyph_response(partial_glyph, similar, input)
  → When glyph is incomplete, bridge with existing


SHARED GLYPH MANAGER:
─────────────────────
mgr.get_glyphs_for_user(user_hash, signal=None, gates=None, top_k=5)
  → Personalized glyph list for user

mgr.record_glyph_adoption(user_hash, glyph_name, quality_rating)
  → User adopted glyph → update consensus

mgr.create_glyph_version(name, description, signal, gates, created_by)
  → Track new version of glyph

mgr.analyze_coverage_gaps()
  → Which emotional territories need more glyphs

mgr.recommend_new_glyphs_for_gaps()
  → Specific recommendations (emotional areas + priority)

mgr.get_system_health_report()
  → Dashboard: total glyphs, users, adoption rates, etc
"""

# ============================================================================
# RESPONSE TEMPLATES (8 EMOTIONAL TONES)
# ============================================================================

"""
GRIEF:
  "There's a depth to what you're carrying. {term} is one of the truest things..."

LONGING:
  "I hear the {term} in what you're saying. That ache toward something..."

CONTAINMENT:
  "You're doing something quiet but powerful: holding space for {term}."

INSIGHT:
  "You've arrived at something true. That {term}—it's not confusion. It's clarity..."

JOY:
  "The {term} you're feeling—let it exist in its fullness. It doesn't need permission."

DEVOTION:
  "The {{term}} you describe—that's you showing up for something that matters."

RECOGNITION:
  "You're asking to be known. The {{term}} in that question—it matters."

UNKNOWN:
  "You're in territory without a map. The {{term}} is appropriate. Let it teach you."

Key pattern:
  1. Select template for detected tone
  2. Insert key emotional term from user input (reinforcement)
  3. Add validation prompt at end (feedback gathering)
  4. Reference glyph name (training signal)
"""

# ============================================================================
# TESTING
# ============================================================================

"""
QUICK TEST (validate it works):
───────────────────────────────
python test_glyph_learning_pipeline.py
  Expected: 3 new glyphs generated, responses shown, health report printed

UNIT TEST (single function):
────────────────────────────
python -c "
from emotional_os.glyphs.glyph_learner import GlyphLearner
learner = GlyphLearner()
candidate = learner.analyze_input_for_glyph_generation(
    'I feel caught between who I am and who I pretend to be',
    [{'keyword': 'caught', 'signal': 'β', 'voltage': 'medium', 'tone': 'containment'}],
    'test_user'
)
print('Glyph:', candidate['glyph_name'])
print('Confidence:', candidate['confidence_score'])
"

INTEGRATION TEST (with signal_parser):
───────────────────────────────────────
python -c "
from emotional_os.parser.signal_parser import parse_input
result = parse_input('I feel caught between who I pretend to be and who I really am')
print('Glyph:', result['best_glyph'])
print('Source:', result.get('source'))
print('Never None?:', result['best_glyph'] is not None)
"

DATABASE CHECK:
───────────────
sqlite3 emotional_os/glyphs/glyphs.db
  SELECT count(*) FROM glyph_candidates;  # New candidates
  SELECT count(*) FROM glyph_versions;    # Versioned glyphs
  SELECT * FROM glyph_consensus ORDER BY consensus_strength DESC LIMIT 5;
  SELECT * FROM user_glyph_preferences LIMIT 5;
"""

# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

"""
□ Copy 4 files to emotional_os/glyphs/
  ├─ glyph_learner.py
  ├─ learning_response_generator.py
  ├─ shared_glyph_manager.py
  └─ test_glyph_learning_pipeline.py (optional)

□ Modify signal_parser.py
  ├─ Add imports
  ├─ Initialize managers
  ├─ Modify parse_input()
  └─ Add helper functions

□ Test locally
  python test_glyph_learning_pipeline.py

□ Deploy
  git add .
  git commit -m "Phase 2: Real-time glyph learning system"
  git push

□ Monitor
  - Check error logs
  - Verify glyphs generated (not None)
  - Confirm adoptions recorded
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
PROBLEM: "No module named glyph_learner"
SOLUTION: Check files are in emotional_os/glyphs/
          Make sure __init__.py exists in emotional_os/glyphs/

PROBLEM: "Database is locked"
SOLUTION: Only one process can write at a time
          Close other connections/terminals

PROBLEM: "Glyph confidence is too low"
SOLUTION: Check emotional language extraction
          Might need more keywords in signal_lexicon.json

PROBLEM: "Response doesn't reference glyph"
SOLUTION: Check response template is being used
          Verify glyph_name is passed to generator

PROBLEM: "User segregation not working"
SOLUTION: Verify user_hash passed to get_glyphs_for_user()
          Check that adoption is being recorded

PROBLEM: "Coverage gaps not showing"
SOLUTION: Run analyze_coverage_gaps()
          May need 50+ glyphs for pattern to emerge
"""

# ============================================================================
# MONITORING COMMANDS
# ============================================================================

"""
# Check system health
python -c "
from emotional_os.glyphs.shared_glyph_manager import SharedGlyphManager
mgr = SharedGlyphManager()
print(mgr.get_system_health_report())
"

# Get recommendations
python -c "
from emotional_os.glyphs.shared_glyph_manager import SharedGlyphManager
mgr = SharedGlyphManager()
for rec in mgr.recommend_new_glyphs_for_gaps():
    print(rec)
"

# View database size
ls -lh emotional_os/glyphs/glyphs.db

# Count candidates vs production
sqlite3 emotional_os/glyphs/glyphs.db \
  "SELECT 'Candidates', count(*) FROM glyph_candidates 
   UNION ALL 
   SELECT 'Production', count(*) FROM glyph_versions WHERE is_active=1;"

# View top glyphs by adoption
sqlite3 emotional_os/glyphs/glyphs.db \
  "SELECT glyph_name, total_users_adopted, consensus_strength 
   FROM glyph_consensus 
   ORDER BY total_users_adopted DESC LIMIT 10;"
"""

# ============================================================================
# REFERENCE LINKS
# ============================================================================

"""
For more information, see:

COMPLETE ARCHITECTURE:
  → PHASE_2_LEARNING_SYSTEM_ARCHITECTURE.md

INTEGRATION STEPS:
  → INTEGRATION_GUIDE_PHASE_2.md

VISUAL DIAGRAMS:
  → PHASE_2_VISUAL_DIAGRAMS.md (8 ASCII diagrams)

IMPLEMENTATION CHECKLIST:
  → PHASE_2_IMPLEMENTATION_CHECKLIST.md

DELIVERY SUMMARY:
  → PHASE_2_DELIVERY_SUMMARY.md

CODE WITH DOCSTRINGS:
  → glyph_learner.py
  → learning_response_generator.py
  → shared_glyph_manager.py

WORKING EXAMPLE:
  → test_glyph_learning_pipeline.py
"""

# ============================================================================
# PHILOSOPHY
# ============================================================================

"""
Every interaction teaches the system.
No user ever sees a standardized message.
The shared database grows stronger with each user.
The system learns through authentic emotional communication.

Phase 1: Fixed the matching (56% → 100% coverage) ✓
Phase 2: Made it intelligent (learning from every interaction) ✓
Phase 3: Let it evolve (patterns emerging organically)
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              EMOTIONAL OS PHASE 2: QUICK REFERENCE CARD                    ║
║                   Real-Time Glyph Learning System                          ║
╚════════════════════════════════════════════════════════════════════════════╝

THE SYSTEM IN ONE LINE:
  No matching glyph? Generate new one + craft response that trains + log
  adoption → Every interaction teaches system → User never knows

3 MODULES:
  1. GlyphLearner: Generate new glyphs
  2. LearningResponseGenerator: Craft training responses
  3. SharedGlyphManager: Track adoption + user segregation

INTEGRATION: 3 steps (30 minutes)
  1. Add imports to signal_parser.py
  2. Modify parse_input() to use learning pipeline
  3. Add helper functions

DATABASE: 5 new tables (auto-created)
  - glyph_candidates (new ideas)
  - glyph_versions (evolution)
  - user_glyph_preferences (personal history)
  - glyph_consensus (global agreement)
  - emotional_territory (coverage map)

KEY BENEFIT: Every user interaction teaches system
             But every user sees personal response
             Never a standardized message

═══════════════════════════════════════════════════════════════════════════════
For detailed documentation, see documentation files listed above.
""")
