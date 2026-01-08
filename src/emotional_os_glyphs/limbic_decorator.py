#!/usr/bin/env python3
"""
Limbic reply decorator

Transforms a baseline reply using the limbic system's latent output.
This module runs entirely in the backend and never exposes glyphs or
internal system labels to end users. It produces short, companion-like
augmentations (empathic opener, savoring cue, and a small practical step).
"""
import logging
from typing import Dict

# Module logger — controlled by environment or test harness
logger = logging.getLogger(__name__)


def _safe_short(sentence: str) -> str:
    # Ensure safe length and punctuation
    s = sentence.strip()
    if not s:
        return ""
    if s[-1] not in ".!?":
        s = s + "."
    return s


def decorate_reply(baseline_reply: str, limbic_result: Dict, intensity: float = 1.0) -> str:
    """
    Create a decorated reply from a baseline reply and limbic_result.

    - baseline_reply: original response text
    - limbic_result: output of LimbicAdjacentSystem.create_ritual_chiasmus or process_emotion_with_limbic_mapping
    - intensity: float 0..1 controlling degree of flourish

    Returns a single string (no glyphs, no internal labels).
    """
    try:
        emotion = limbic_result.get("emotion", "") if isinstance(limbic_result, dict) else ""
    except Exception:
        emotion = ""

    # Debug: emit a compact summary of limbic_result when logger is configured
    try:
        if logger.isEnabledFor(logging.DEBUG):
            summary = {
                "emotion": emotion,
                "has_system_signals": (
                    bool(limbic_result.get("system_signals")) if isinstance(limbic_result, dict) else False
                ),
                "ritual_len": len(limbic_result.get("ritual_sequence", [])) if isinstance(limbic_result, dict) else 0,
            }
            logger.debug("decorate_reply() limbic_summary=%s", summary)
    except Exception:
        # Non-fatal logging error
        pass

    opener = ""
    savor = ""
    practical = ""

    # Empathic opener (short)
    if emotion:
        opener = f"I hear {('a sense of ' + emotion) if emotion not in ['joy','sadness','fear','anger','love'] else emotion}."
    else:
        opener = "I hear you."

    opener = _safe_short(opener)

    # Savoring / breath cue — DISABLED (users found it repetitive)
    savor = ""

    # Practical close — DISABLED (users found it repetitive)
    practical = ""

    # Compose: keep baseline as the core, add opener before and a short suggestion after
    baseline = _safe_short(baseline_reply)

    # Merge with light weighting: baseline first, then opener optionally preface if baseline is short
    if len(baseline.split()) < 6:
        decorated = f"{opener} {baseline}".strip()
    else:
        decorated = f"{baseline}".strip()

    # Final cleanup: avoid runaway whitespace
    out = " ".join(decorated.split())
    if logger.isEnabledFor(logging.DEBUG):
        try:
            logger.debug("decorate_reply() out=%s", out)
        except Exception:
            pass
    return out


if __name__ == "__main__":
    # Simple self-check
    b = "That's wonderful — I'm glad to hear that"
    fake = {"emotion": "joy", "system_signals": {}, "ritual_sequence": ["blink", "breath", "brace"]}
    print(decorate_reply(b, fake, intensity=0.8))
