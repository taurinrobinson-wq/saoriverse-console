#!/usr/bin/env python3
"""
Limbic reply decorator

Transforms a baseline reply using the limbic system's latent output.
This module runs entirely in the backend and never exposes glyphs or
internal system labels to end users. It produces short, companion-like
augmentations (empathic opener, savoring cue, and a small practical step).
"""
from typing import Dict


def _safe_short(sentence: str) -> str:
    # Ensure safe length and punctuation
    s = sentence.strip()
    if not s:
        return ""
    if s[-1] not in '.!?':
        s = s + '.'
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
        emotion = limbic_result.get('emotion', '') if isinstance(limbic_result, dict) else ''
    except Exception:
        emotion = ''

    opener = ''
    savor = ''
    practical = ''

    # Empathic opener (short)
    if emotion:
        opener = f"I hear {('a sense of ' + emotion) if emotion not in ['joy','sadness','fear','anger','love'] else emotion}."
    else:
        opener = "I hear you."

    opener = _safe_short(opener)

    # Savoring / breath cue (gentle, optional)
    if intensity > 0.6:
        savor = "You might try pausing for a breath and noticing what stands out in this moment."
    else:
        savor = "Take a steady breath and notice how that feels."

    savor = _safe_short(savor)

    # Practical close — one small, optional suggestion
    practical = "If you want, name one small thing to carry from this feeling into the next hour."
    practical = _safe_short(practical)

    # Compose: keep baseline as the core, add opener before and a short suggestion after
    baseline = _safe_short(baseline_reply)

    # Merge with light weighting: baseline first, then opener optionally preface if baseline is short
    if len(baseline.split()) < 6:
        decorated = f"{opener} {baseline} {savor} {practical}"
    else:
        decorated = f"{baseline} {savor} {practical}"

    # Final cleanup: avoid runaway whitespace
    return ' '.join(decorated.split())


if __name__ == '__main__':
    # Simple self-check
    b = "That's wonderful — I'm glad to hear that"
    fake = {'emotion': 'joy', 'system_signals': {}, 'ritual_sequence': ['blink','breath','brace']}
    print(decorate_reply(b, fake, intensity=0.8))
