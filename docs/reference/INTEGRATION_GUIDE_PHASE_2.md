# !/usr/bin/env python3
""" Integration Guide: Adding Phase 2 Learning to signal_parser.py

This file shows the exact modifications needed to signal_parser.py to activate the real-time glyph
learning system.

BEFORE: signal_parser returns None when no glyph found AFTER: signal_parser generates new glyph +
training response

This is a reference implementation showing exactly where to add the learning pipeline. """

# ============================================================================

# CURRENT signal_parser.py FLOW (Simplified)

# ============================================================================

""" def parse_input(text: str, user_hash: Optional[str] = None) -> Dict:

    # 1. Detect signals (3-phase)
signals = parse_signals(text)

    # 2. Map signals to gates
gates = evaluate_gates(signals)

    # 3. Fetch glyphs matching gates
glyphs = fetch_glyphs(gates)

    # 4. Select best and generate response
if glyphs: best_glyph, response = select_best_glyph_and_response( glyphs, signals, text ) return {
"best_glyph": best_glyph, "voltage_response": response, "signals": signals, "gates": gates } else:
        # PROBLEM: No glyph found → return None
response = generate_contextual_response(signals) return { "best_glyph": None,  # ← THIS IS THE
PROBLEM "voltage_response": response, "signals": signals, "gates": gates } """

# ============================================================================

# PHASE 2 INTEGRATION: The Complete Modification

# ============================================================================

""" MODIFICATION TO signal_parser.py:

At the top, add imports: """

import hashlib

from emotional_os.glyphs.glyph_learner import GlyphLearner from
emotional_os.glyphs.learning_response_generator import LearningResponseGenerator from
emotional_os.glyphs.shared_glyph_manager import SharedGlyphManager

# Initialize managers (once, at module load)

_glyph_learner = GlyphLearner() _learning_response_gen = LearningResponseGenerator()
_shared_glyph_manager = SharedGlyphManager()

def _get_user_hash(user_id: str = None) -> str: """Create anonymous user hash.""" if not user_id:
user_id = "anonymous" return hashlib.sha256(user_id.encode()).hexdigest()[:16]

# ============================================================================

# MODIFIED parse_input() with Learning Pipeline

# ============================================================================

def parse_input(text: str, user_hash: Optional[str] = None) -> Dict: """ Parse emotional input and
return glyph + response.

NOW INCLUDES: Real-time glyph generation when no match found. """

if not user_hash: user_hash = _get_user_hash()

    # STEP 1: Detect signals (existing code)
signals = parse_signals(text)

    # STEP 2: Evaluate gates (existing code)
gates = evaluate_gates(signals)

    # STEP 3: Fetch glyphs matching gates (existing code)
glyphs = fetch_glyphs(gates)

    # STEP 4: SELECT BEST OR GENERATE NEW
if glyphs:
        # ================== PHASE 1: Existing glyph ==================
best_glyph, response = select_best_glyph_and_response( glyphs, signals, text )

        # ADDED: Log adoption (this glyph was used)
_shared_glyph_manager.record_glyph_adoption( user_hash=user_hash, glyph_name=best_glyph,
quality_rating=None  # User hasn't rated yet )

return { "best_glyph": best_glyph, "voltage_response": response, "signals": signals, "gates": gates,
"source": "existing_glyph", "learning_status": "production" }

else:
        # ================== PHASE 2: NEW - Learning pipeline ==================

        # STEP 4.1: Analyze input for glyph generation
glyph_candidate = _glyph_learner.analyze_input_for_glyph_generation( input_text=text,
signals=signals, user_hash=user_hash )

        # STEP 4.2: Log candidate to database
_glyph_learner.log_glyph_candidate(glyph_candidate)

        # STEP 4.3: Create version in shared manager
glyph_name = glyph_candidate.get("glyph_name", "Emerging Emotion") version_num =
_shared_glyph_manager.create_glyph_version( glyph_name=glyph_name,
description=glyph_candidate.get("description", ""),
emotional_signal=glyph_candidate.get("emotional_signal", "unknown"),
gates=glyph_candidate.get("gates", ["Gate 5"]), created_by=user_hash )

        # STEP 4.4: Record adoption (user creating = first user adopting)
_shared_glyph_manager.record_glyph_adoption( user_hash=user_hash, glyph_name=glyph_name,
quality_rating=1  # Implicit positive (they're engaging) )

        # STEP 4.5: Generate learning response
emotional_analysis = { "primary_tone": _determine_emotional_tone(signals), "emotional_terms":
glyph_candidate.get("emotional_terms", {}), "nrc_analysis": glyph_candidate.get("nrc_analysis", {})
}

learning_response = _learning_response_gen.generate_learning_response(
glyph_candidate=glyph_candidate, original_input=text,
emotional_tone=emotional_analysis["primary_tone"],
emotional_terms=emotional_analysis["emotional_terms"],
nrc_analysis=emotional_analysis["nrc_analysis"] )

        # STEP 4.6: Return generated glyph + training response
return { "best_glyph": glyph_name,  # ← NO LONGER None! "voltage_response": learning_response,  # ←
Training response "signals": signals, "gates": gates, "source": "glyph_learning_pipeline",
"learning_status": "candidate", "confidence": glyph_candidate.get("confidence_score", 0.5),
"version": version_num, "metadata": glyph_candidate.get("metadata", {}) }

def _determine_emotional_tone(signals: List[Dict]) -> str: """ Determine primary emotional tone from
signals. (Helper for learning response generation) """ if not signals: return "unknown"

    # Look at the primary signal's tone
primary_tone = signals[0].get("tone", "unknown")

    # Map to response tone
tone_map = { "grief": "grief", "longing": "longing", "containment": "containment", "insight":
"insight", "joy": "joy", "devotion": "devotion", "recognition": "recognition", "unknown": "unknown"
}

return tone_map.get(primary_tone, "unknown")

# ============================================================================

# BONUS: Admin Dashboard Helpers

# ============================================================================

def get_system_learning_status() -> Dict: """ Get current system learning status. Useful for admin
dashboard. """ health =_shared_glyph_manager.get_system_health_report()

return { "active_glyphs": health.get("total_active_glyphs", 0), "unique_users":
health.get("unique_users_contributed", 0), "pending_candidates":
health.get("pending_candidate_glyphs", 0), "coverage_gaps": health.get("recommendations", []),
"timestamp": health.get("timestamp", ""), "system_health": "GOOD" if
health.get("total_active_glyphs", 0) > 100 else "DEVELOPING" }

def get_glyph_recommendations() -> List[Dict]: """ Get recommendations for next glyphs to generate.
Based on coverage gaps. """ return _shared_glyph_manager.recommend_new_glyphs_for_gaps()

def promote_candidate_glyph(glyph_name: str) -> bool: """ Move a candidate glyph from candidates →
production. Called after human review/validation. """
return_glyph_learner.promote_candidate_to_production(glyph_name)

# ============================================================================

# INTEGRATION CHECKLIST

# ============================================================================

""" ✓ Step 1: Add imports at top of signal_parser.py ✓ Step 2: Initialize managers (module level) ✓
Step 3: Modify parse_input() to include learning pipeline ✓ Step 4: Add _determine_emotional_tone()
helper ✓ Step 5: Add admin dashboard helpers ✓ Step 6: Test with test_glyph_learning_pipeline.py ✓
Step 7: Verify database schema created (run _ensure_learning_tables) ✓ Step 8: Deploy and monitor

BEFORE AND AFTER:

BEFORE: Input: "I feel caught between who I pretend to be and who I really am" Signals: β, δ Gates:
[4, 5] Glyphs found: 0 Response: Generic contextual message Database: No learning

AFTER: Input: "I feel caught between who I pretend to be and who I really am" Signals: β, δ Gates:
[4, 5] Glyphs found: 0 → GENERATE NEW New Glyph: "Fractured Identity" Response: Learning response
(trains system) Database: Logged, versioned, adoption tracked System: Ready for next user with
similar emotion """

# ============================================================================

# TESTING THE INTEGRATION

# ============================================================================

""" After integration, test with:

python test_glyph_learning_pipeline.py

Expected output: ✓ 3 new glyphs generated ✓ 3 learning responses crafted ✓ 3 adoptions recorded ✓
System health report shows new glyphs ✓ Coverage recommendations generated

Then validate with signal_parser directly:

from emotional_os.parser.signal_parser import parse_input

result = parse_input( "I feel caught between who I pretend to be and who I really am",
user_hash="test_user_001" )

print(result["best_glyph"])  # Should be "Fractured Identity" or similar print(result["source"])
# Should be "glyph_learning_pipeline" print(result["confidence"])  # Should be > 0.5 """
