"""Orchestrator wiring the response engine components.

Public:
- process_user_input(user_input: str, context: dict = None) -> str

This file demonstrates the end-to-end flow described in the spec.
"""
from typing import Dict, Optional

from symbolic_tagger import tag_input
from phase_modulator import detect_phase
from tone_adapters import generate_initiatory_response, generate_archetypal_response
from response_adapter import translate_emotional_response
from relational_memory import RelationalMemoryCapsule, store_capsule
from emotional_os.adapter.clarification_trace import ClarificationTrace


# Singleton trace instance for this process
_clarify_trace = ClarificationTrace()


def process_user_input(user_input: str, context: Optional[Dict] = None) -> str:
    """Orchestrate the emotional response pipeline.

    Steps:
    1. Tag input (symbolic tags)
    2. Detect phase
    3. Generate tone-adapted response
    4. Adapt to user-facing language
    5. Store relational memory capsule
    """
    ctx = dict(context or {})
    prefix = ""

    # Check for prior clarifications that could bias interpretation
    try:
        prior = _clarify_trace.lookup(user_input)
        if prior and prior.get("corrected_intent"):
            ctx["inferred_intent"] = prior.get("corrected_intent")
    except Exception:
        prior = None

    # Detect and store an explicit clarification/correction from the user.
    # This expects callers to pass `last_user_input` and `last_system_response`
    # in `context` when available so we can anchor the clarification.
    try:
        stored = _clarify_trace.detect_and_store(user_input, {**ctx})
        if stored:
            prefix = (
                "Thanks for clarifying—I’m still learning, so I really appreciate that.\n"
            )
    except Exception:
        stored = False

    # Accept local_analysis when provided to avoid redundant heavy parsing.
    local_analysis = ctx.get("local_analysis")

    # 1. Tagging (lightweight symbolic tagging)
    tags = tag_input(user_input)

    # 2. Phase detection (give detector access to symbolic tags)
    phase = detect_phase(user_input, {"symbolic_tags": tags})

    # 3. Tone-adapted response
    # Prepare a lightweight context for tone adapters; prefer values
    # surfaced by local_analysis when available.
    tone_ctx = {
        "intensity": ctx.get("intensity", "gentle"),
        "emotion": ctx.get("emotion"),
    }
    # Provide a short preview or anchor hint if available from local analysis
    try:
        if local_analysis:
            tone_ctx["preview"] = local_analysis.get("voltage_response")
            best = local_analysis.get("best_glyph")
            if best:
                tone_ctx["anchor"] = best.get("glyph_name")
    except Exception:
        pass

    if phase == "initiatory":
        raw_response = generate_initiatory_response(tone_ctx)
        voltage = "ΔV↑↑"
        capsule_tags = ["initiatory_signal"]
    else:
        raw_response = generate_archetypal_response(tone_ctx)
        voltage = "ΔV↔"
        capsule_tags = ["anchoring_signal"]

    # 4. Adapt into emotionally fluent language
    system_output = {
        "emotion": ctx.get("emotion", "connection"),
        "intensity": ctx.get("intensity", "gentle"),
        "context": ctx.get("context", "conversation"),
        "resonance": ctx.get("resonance", "presence"),
    }
    adapted_response = translate_emotional_response(system_output)

    # 5. Store relational memory capsule
    # Include glyph names from local analysis in the capsule if present
    glyph_names = []
    try:
        if local_analysis and isinstance(local_analysis.get("glyphs"), list):
            glyph_names = [g.get("glyph_name") for g in local_analysis.get(
                "glyphs", []) if isinstance(g, dict)]
    except Exception:
        glyph_names = []

    capsule = RelationalMemoryCapsule(
        symbolic_tags=capsule_tags + tags + glyph_names,
        relational_phase=phase,
        voltage_marking=voltage,
        user_input=user_input,
        response_summary=raw_response,
    )
    store_capsule(capsule)

    # Return combined response: optional clarification prefix + tone + adapted phrasing
    return f"{prefix}{raw_response}\n\n{adapted_response}"


if __name__ == "__main__":
    # Quick demo when executed as a script
    example = "I just met someone who really sees me."
    resp = process_user_input(
        example, {"emotion": "longing", "intensity": "high"})
    print(resp)
