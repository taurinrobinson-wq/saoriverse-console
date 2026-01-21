import re
from typing import Dict
import logging

logger = logging.getLogger(__name__)


# Attempt to use canonical `emotional_os` signal parser when available.
_USE_EMOTIONAL_OS = False
try:
    # Prefer the packaged core implementation
    from src.emotional_os.core.signal_parser import (
        parse_signals as _eo_parse_signals,
        load_signal_map as _eo_load_signal_map,
    )
    from src.emotional_os.core.paths import signal_lexicon_path as _eo_signal_lexicon_path, learned_lexicon_path as _eo_learned_lexicon_path
    _USE_EMOTIONAL_OS = True
    logger.info("Using emotional_os canonical signal parser")
except Exception:
    try:
        # Try alternate import location
        from emotional_os.core.signal_parser import (
            parse_signals as _eo_parse_signals,
            load_signal_map as _eo_load_signal_map,
        )
        from emotional_os.core.paths import signal_lexicon_path as _eo_signal_lexicon_path, learned_lexicon_path as _eo_learned_lexicon_path
        _USE_EMOTIONAL_OS = True
        logger.info("Using emotional_os canonical signal parser")
    except Exception:
        _USE_EMOTIONAL_OS = False


def _convert_eo_matches_to_compact(matches: list) -> Dict[str, object]:
    """Convert emotional_os parse_signals matches into DraftShift compact signal dict."""
    signals = {
        "frustration": 0.0,
        "resignation": 0.0,
        "boundary": False,
        "escalation": 0.0,
        "softening": 0.0,
        "gratitude": 0.0,
        "empathy": 0.0,
        "urgency": 0.0,
        "avoidance": 0.0,
        "disappointment": 0.0,
        "imperative": False,
    }

    for m in matches:
        try:
            sig = (m.get("signal") or m.get("tone") or m.get("keyword") or "").lower()
            voltage = (m.get("voltage") or "").lower()
        except Exception:
            continue

        # Voltage mapping -> escalation
        if voltage in ("high", "critical"):
            signals["escalation"] = max(signals["escalation"], 0.9)
        elif voltage in ("medium", "moderate"):
            signals["escalation"] = max(signals["escalation"], 0.6)
        elif voltage:
            signals["escalation"] = max(signals["escalation"], 0.4)

        if any(k in sig for k in ("frustration", "anger", "angry", "annoy", "annoyed", "irrit")):
            signals["frustration"] = max(signals["frustration"], 0.9)
        if any(k in sig for k in ("resign", "resignation", "done", "give up", "screw this")):
            signals["resignation"] = max(signals["resignation"], 0.9)
            signals["boundary"] = True
        if any(k in sig for k in ("please", "polite", "soften", "softening", "please note", "could you")):
            signals["softening"] = max(signals["softening"], 0.6)
        if any(k in sig for k in ("gratitude", "thanks", "thank you", "appreciat")):
            signals["gratitude"] = max(signals["gratitude"], 0.9)
        if any(k in sig for k in ("empathy", "sympath", "i understand", "i see")):
            signals["empathy"] = max(signals["empathy"], 0.8)
        if any(k in sig for k in ("urgent", "asap", "immediate", "now", "right away")):
            signals["urgency"] = max(signals["urgency"], 0.9)
            signals["escalation"] = max(signals["escalation"], 0.6)
        if any(k in sig for k in ("avoid", "avoidance", "ignore")):
            signals["avoidance"] = max(signals["avoidance"], 0.6)
        if any(k in sig for k in ("disappoint", "disappointed", "let down")):
            signals["disappointment"] = max(signals["disappointment"], 0.8)
        if any(k in sig for k in ("imperative", "command", "must", "should", "do not", "don't", "stop")):
            signals["imperative"] = True

    # clamp floats
    for k in (
        "frustration",
        "resignation",
        "escalation",
        "softening",
        "gratitude",
        "empathy",
        "urgency",
        "avoidance",
        "disappointment",
    ):
        v = signals.get(k, 0.0)
        try:
            signals[k] = min(max(float(v), 0.0), 1.0)
        except Exception:
            signals[k] = 0.0

    return signals


def parse_signal(text: str) -> Dict[str, object]:
    """Return a compact signal dictionary describing emotional/relational cues.

    When `emotional_os` is available, use its canonical `parse_signals` implementation
    and convert results to the compact DraftShift format. Otherwise fall back to
    the local lightweight parser logic.
    """
    if _USE_EMOTIONAL_OS:
        try:
            # load signal map from emotional_os path manager
            base = str(_eo_signal_lexicon_path())
            learned = str(_eo_learned_lexicon_path())
            signal_map = _eo_load_signal_map(base, learned)
            matches = _eo_parse_signals(text, signal_map)
            compact = _convert_eo_matches_to_compact(matches)
            return compact
        except Exception:
            logger.debug("emotional_os parser failed; falling back to local parser")

    # --- Fallback: local lightweight parser (original implementation) ---
    s = text.strip()
    s_lower = s.lower()

    signals = {
        "frustration": 0.0,
        "resignation": 0.0,
        "boundary": False,
        "escalation": 0.0,
        "softening": 0.0,
        "gratitude": 0.0,
        "empathy": 0.0,
        "urgency": 0.0,
        "avoidance": 0.0,
        "disappointment": 0.0,
        "imperative": False,
    }

    # Simple lexical cues
    if re.search(r"\b(awful|terrible|horrible|hate|idiot|stupid|dumb)\b", s_lower):
        signals["frustration"] = 0.9
        signals["escalation"] = max(signals["escalation"], 0.8)
    if re.search(r"\b(i'?m done|i am done|i'm done talking|screw this)\b", s_lower):
        signals["resignation"] = 0.9
        signals["boundary"] = True
    if re.search(r"\b(please|could you|would you)\b", s_lower):
        signals["softening"] = max(signals["softening"], 0.6)
        signals["imperative"] = False
    if re.search(r"\b(thanks|thank you|appreciate)\b", s_lower):
        signals["gratitude"] = 0.9
    if re.search(r"\b(i understand|i see|i appreciate)\b", s_lower):
        signals["empathy"] = 0.8
    if re.search(r"\b(asap|urgent|immediately|right away|now)\b", s_lower):
        signals["urgency"] = 0.9
        signals["escalation"] = max(signals["escalation"], 0.6)
    if re.search(r"\b(avoid|avoidance|trying not to|I'll ignore)\b", s_lower):
        signals["avoidance"] = 0.6
    if re.search(r"\b(disappoint|disappointed|let down)\b", s_lower):
        signals["disappointment"] = 0.8

    # Detect imperative sentences (commands)
    if s.endswith('!') or re.search(r"^\s*(please\s+)?[A-Z][a-z]+\b.*\b(please)?$", text):
        # crude check for imperative or strong sentence
        if re.search(r"\b(please|do not|don't|stop)\b", s_lower):
            signals["imperative"] = True

    # clamp floats
    for k in ("frustration", "resignation", "escalation", "softening", "gratitude", "empathy", "urgency", "avoidance", "disappointment"):
        v = signals.get(k, 0.0)
        try:
            signals[k] = min(max(float(v), 0.0), 1.0)
        except Exception:
            signals[k] = 0.0

    return signals
