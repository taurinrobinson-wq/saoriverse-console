from typing import Dict

# map signal dict -> glyph representation

def map_signals_to_glyphs(signals: Dict[str, object]) -> Dict[str, object]:
    """Return a compact glyph mapping from parsed signals.

    Glyph fields (example):
      - valence: -1..1
      - intensity: 0..1
      - stance: 'assertive'|'defensive'|'conciliatory'|'neutral'
      - escalation: 0..1
      - intent: 'inform'|'request'|'close'|'warn'|'other'
    """
    valence = 0.0
    intensity = 0.0
    stance = 'neutral'
    escalation = float(signals.get('escalation', 0.0))
    intent = 'other'

    # gratitude and empathy pull valence positive
    valence += 0.8 * float(signals.get('gratitude', 0.0))
    valence += 0.6 * float(signals.get('empathy', 0.0))

    # frustration/disappointment reduce valence and increase intensity
    valence -= 0.9 * float(signals.get('frustration', 0.0))
    valence -= 0.7 * float(signals.get('disappointment', 0.0))

    intensity = max(float(signals.get('frustration', 0.0)), float(signals.get('resignation', 0.0)), float(signals.get('escalation', 0.0)))

    # stance heuristics
    if float(signals.get('softening', 0.0)) > 0.5 or float(signals.get('gratitude', 0.0)) > 0.5:
        stance = 'conciliatory'
    elif float(signals.get('frustration', 0.0)) > 0.6 or float(signals.get('escalation', 0.0)) > 0.6:
        stance = 'assertive'
    elif float(signals.get('resignation', 0.0)) > 0.6:
        stance = 'defensive'

    # intent heuristics (best-effort)
    if float(signals.get('urgency', 0.0)) > 0.6:
        intent = 'warn'
    elif float(signals.get('imperative', 0.0)):
        intent = 'request'
    elif float(signals.get('resignation', 0.0)) > 0.6:
        intent = 'close'
    else:
        intent = 'inform'

    # normalize valence to -1..1
    val = max(min(valence, 1.0), -1.0)

    glyph = {
        'valence': val,
        'intensity': float(intensity),
        'stance': stance,
        'escalation': float(escalation),
        'intent': intent,
    }
    return glyph
