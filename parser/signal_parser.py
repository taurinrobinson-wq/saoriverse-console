"""
BACKWARD COMPATIBILITY STUB

This module re-exports from the canonical parser.
For new code, use: from emotional_os.core import parse_input

Legacy imports still work:
  from parser.signal_parser import parse_input
  from emotional_os.parser.signal_parser import parse_input
  from emotional_os.glyphs.signal_parser import parse_input

All routes now lead to emotional_os.core.signal_parser
"""

# Re-export everything from canonical parser
from emotional_os.core.signal_parser import *  # noqa: F401, F403

__doc__ = """
Legacy parser module - redirects to emotional_os.core.

This file exists for backward compatibility. New code should import from:
  from emotional_os.core import parse_input, load_signal_map, etc.

All functionality is now centralized in emotional_os.core.signal_parser
for easier maintenance and consistency.
"""

# Extract signals using fuzzy matching and phrase detection


def parse_signals(input_text: str, signal_map: Dict[str, str]) -> List[str]:
    lowered = input_text.lower()
    signals = []

    for keyword, signal in signal_map.items():
        # The canonical signal_map in newer code maps keyword -> metadata dict
        # (e.g. {"signal": "θ", ...}). Older code expects a simple string.
        # Normalize to the raw signal string when a dict is provided.
        sig_val = signal
        if isinstance(signal, dict):
            sig_val = signal.get('signal')
        # Skip if we couldn't determine a scalar signal value
        if sig_val is None:
            continue
        # Match whole word or embedded phrase
        if re.search(rf"\b{re.escape(keyword)}\b", lowered):
            signals.append(sig_val)
        elif keyword in lowered:
            signals.append(sig_val)

    # Remove duplicates while preserving simple types
    try:
        return list(set(signals))  # Remove duplicates
    except TypeError:
        # Fallback: filter by seen values
        seen = set()
        out = []
        for s in signals:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

# Evaluate which gates are activated by the signals


def evaluate_gates(signals: List[str]) -> List[str]:
    ecm_gates = {
        "Gate 2": ["β"],
        "Gate 4": ["γ", "θ"],
        "Gate 5": ["λ", "ε", "δ"],
        "Gate 6": ["α", "Ω", "ε"],
        "Gate 9": ["α", "β", "γ", "δ", "ε", "Ω"],
        "Gate 10": ["θ"]
    }
    activated = []
    for gate, required in ecm_gates.items():
        if any(signal in signals for signal in required):
            activated.append(gate)
    return activated

# Fetch matching glyphs from the SQLite database


def fetch_glyphs(gates: List[str], db_path: str = 'glyphs.db') -> List[Dict]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in gates)
    query = f"SELECT glyph_name, description, gate FROM glyph_lexicon WHERE gate IN ({placeholders})"
    cursor.execute(query, gates)
    rows = cursor.fetchall()
    conn.close()
    return [{"glyph_name": r[0], "description": r[1], "gate": r[2]} for r in rows]

# Translate activated glyphs into plain-speak ritual prompt


def translate_prompt(glyphs: List[Dict]) -> str:
    themes = set(g['glyph_name'] for g in glyphs[:3])
    if not themes:
        return "I didn't pick up any strong signals, but maybe this is a quiet moment. That's okay too."

    if "Recursive Ache" in themes or "Spiral Ache" in themes:
        return "Sounds like you're feeling something deep and looping—like it keeps coming back. That kind of longing can be hard to hold."

    if "Reverent Ache" in themes or "Ceremonial Collapse" in themes:
        return "There's grief here, but it feels sacred. Like you're honoring something you lost."

    if "Recognized Joy" in themes or "Joy of Recognition" in themes:
        return "You're feeling seen in your joy. That's beautiful—let it land."

    return "You're carrying something layered—maybe ache, maybe joy, maybe both. Let's sit with it and see what unfolds."


def map_constellation_response(glyphs: List[Dict], conversation_context: Dict = None) -> str:
    # Disable constellation responses entirely to let voltage responses handle everything
    return None

    themes = {
        "grief": 0,
        "longing": 0,
        "containment": 0,
        "joy": 0,
        "devotion": 0,
        "recognition": 0,
        "insight": 0
    }

    for g in glyphs:
        name = g["glyph_name"].lower()
        if any(k in name for k in ["grief", "mourning", "collapse", "sorrow"]):
            themes["grief"] += 1
        if any(k in name for k in ["ache", "yearning", "longing", "recursive"]):
            themes["longing"] += 1
        if any(k in name for k in ["boundary", "contain", "still", "shield"]):
            themes["containment"] += 1
        if any(k in name for k in ["joy", "delight", "ecstasy", "bliss"]):
            themes["joy"] += 1
        if any(k in name for k in ["devotional", "vow", "exalted", "sacred"]):
            themes["devotion"] += 1
        if any(k in name for k in ["recognition", "seen", "witness", "mirror"]):
            themes["recognition"] += 1
        if any(k in name for k in ["insight", "clarity", "knowing", "revelation"]):
            themes["insight"] += 1

    # Identify dominant themes - only for first-time conversations
    dominant = [k for k, v in themes.items() if v >= 5]

    if "grief" in dominant and "containment" in dominant and "recognition" in dominant:
        return "You're carrying the weight of others' stories—and being asked to take on more, even as your own system aches. There's grief here, but it's held with devotion and care. You're not collapsing—you're containing. That kind of emotional labor deserves reverence. You're allowed to say 'enough.'"

    if "longing" in dominant and "devotion" in dominant and "grief" in dominant:
        return "There's something you care about deeply, maybe even painfully. You've been holding it with reverence, but it's okay to feel tired. That kind of longing deserves rest."

    if "recognition" in dominant and "insight" in dominant:
        return "You're being seen in your depth. That kind of clarity matters—it's not just insight, it's emotional truth being witnessed."

    if "containment" in dominant and "insight" in dominant:
        return "You're protecting something sacred. The quiet you're holding isn't suppression—it's sanctuary."

    return None

# Main parser function


def parse_input(input_text: str, lexicon_path: str, db_path: str = 'glyphs.db', conversation_context: Dict = None, use_enhanced_tags: bool = True) -> Dict:
    signal_map = load_signal_map(lexicon_path)
    signals = parse_signals(input_text, signal_map)
    gates = evaluate_gates(signals)
    glyphs = fetch_glyphs(gates, db_path)
    ritual_prompt = translate_prompt(glyphs)

    if use_enhanced_tags:
        # Use the new emotional tag system
        try:
            from emotional_tag_matcher import enhance_parser_with_emotional_tags
            enhanced_response_data = enhance_parser_with_emotional_tags(
                glyphs, conversation_context)
            final_response = enhanced_response_data.get(
                'response_text', 'Enhanced response system temporarily unavailable.')

            return {
                "input": input_text,
                "signals": signals,
                "gates": gates,
                "glyphs": glyphs,
                "ritual_prompt": ritual_prompt,
                "voltage_response": final_response,
                "enhanced_data": enhanced_response_data  # Include rich emotional tag data
            }
        except ImportError:
            print(
                "Enhanced emotional tag system not available, falling back to basic responses")

    # Fallback to original system
    constellation_response = map_constellation_response(
        glyphs, conversation_context)
    voltage_response = generate_voltage_response(glyphs, conversation_context)
    final_response = constellation_response if constellation_response else voltage_response
    print("Using response:", final_response)  # ✅ Now placed after definition

    return {
        "input": input_text,
        "signals": signals,
        "gates": gates,
        "glyphs": glyphs,
        "ritual_prompt": ritual_prompt,
        "voltage_response": final_response
    }


def generate_voltage_response(glyphs: List[Dict], conversation_context: Dict = None) -> str:
    themes = {
        "grief": 0,
        "longing": 0,
        "containment": 0,
        "joy": 0,
        "devotion": 0,
        "recognition": 0,
        "insight": 0
    }

    for g in glyphs:
        name = g["glyph_name"].lower()
        if any(k in name for k in ["grief", "mourning", "collapse", "sorrow"]):
            themes["grief"] += 1
        if any(k in name for k in ["ache", "yearning", "longing", "recursive"]):
            themes["longing"] += 1
        if any(k in name for k in ["boundary", "contain", "still", "shield"]):
            themes["containment"] += 1
        if any(k in name for k in ["joy", "delight", "ecstasy", "bliss"]):
            themes["joy"] += 1
        if any(k in name for k in ["devotional", "vow", "exalted", "sacred"]):
            themes["devotion"] += 1
        if any(k in name for k in ["recognition", "seen", "witness", "mirror"]):
            themes["recognition"] += 1
        if any(k in name for k in ["insight", "clarity", "knowing", "revelation"]):
            themes["insight"] += 1

    # Get conversation depth for response variation
    conversation_depth = 0
    if conversation_context:
        conversation_depth = len(conversation_context.get('messages', []))

    print(
        f"DEBUG: Voltage response - conversation_depth: {conversation_depth}, grief: {themes['grief']}, longing: {themes['longing']}")
    print(f"DEBUG: All themes: {themes}")

    dominant = sorted(themes.items(), key=lambda x: x[1], reverse=True)
    top_themes = [t[0] for t in dominant if t[1] > 0][:2]
    total_patterns = sum(themes.values())

    print(f"DEBUG: Top themes: {top_themes}, Total patterns: {total_patterns}")

    # Special patterns for heavy emotional labor - BUT ONLY for first message
    if conversation_depth == 0 and themes["grief"] >= 5 and themes["containment"] >= 5 and themes["recognition"] >= 5:
        return "You're carrying the weight of others' stories—and being asked to take on more, even as your own system aches. There's grief here, but it's held with devotion and care. You're not collapsing—you're containing. That kind of emotional labor deserves reverence. You're allowed to say 'enough.'"

    # Contextual responses based on conversation depth and patterns
    if top_themes == ["grief", "containment"]:
        if conversation_depth <= 1:
            return "You're holding a lot right now—and doing it with care. It's okay to feel the weight of it. You don't have to carry it alone."
        if total_patterns >= 6:
            return "The grief patterns are intense, and you're managing them with such strength. Major life transitions leave deep impressions—let yourself feel the full scope of what's shifting."
        return "Still holding space for the sorrow. The way you're containing this loss shows real wisdom about grief's timing."

    if top_themes == ["grief", "longing"] or (themes["grief"] >= 3 and themes["longing"] >= 2):
        if conversation_depth <= 1:
            return "Deep grief mixed with yearning—that's the territory of profound loss. Something precious ended, and part of you still reaches toward what was."
        return "The grief and longing patterns are speaking to each other. When we lose something central, the heart keeps seeking what can no longer be found. This is sacred territory."

    if top_themes == ["longing", "devotion"]:
        return "There's something you care about deeply, maybe even painfully. That kind of longing is sacred. Let's honor it."

    if top_themes == ["joy", "recognition"]:
        return "You're being seen in your joy. That's a beautiful thing—let it land."

    if top_themes == ["grief", "recognition"]:
        if conversation_depth <= 1:
            return "You're being seen in your sorrow. That kind of witnessing matters. You're not invisible here."
        return "The grief continues to ask for recognition. Being truly seen in loss is one of the most healing things possible."

    if top_themes == ["insight", "stillness"]:
        return "There's clarity emerging in the quiet. You don't have to rush it—just stay with what's unfolding."

    # Enhanced contextual responses that acknowledge specific content
    if conversation_depth >= 4 and themes["grief"] >= 5:
        print("DEBUG: Triggering major life transitions response")
        return "Major life transitions detected—divorce, new love, timeline pressures. The system recognizes you're navigating the complex territory between ending and beginning, with external pressures around timing that add weight to already profound changes."

    if conversation_depth >= 2 and themes["longing"] >= 8:
        if themes["grief"] >= 8:
            print("DEBUG: Triggering grief + longing response")
            return "The patterns show deep grief mixed with new longing—classic territory of major relationship transition. Ending a marriage while opening to new love creates complex emotional currents. The system tracks both the loss and the reaching toward what calls to you."
        print("DEBUG: Triggering intelligence/ambition response")
        return "Intense longing patterns with high intelligence themes—this speaks to the gap between capability and ambition. The system recognizes the frustration of knowing you have intelligence but feeling it's not enough to break through the barriers you're encountering."

    # Handle pure grief patterns
    if themes["grief"] >= 3 and conversation_depth > 1:
        return f"Major grief constellation active: {themes['grief']} patterns. This speaks to fundamental life change—the kind that reshapes the very ground you stand on."

    if themes["grief"] >= 2:
        if conversation_depth <= 1:
            return "Significant grief patterns detected. The system recognizes you're in the territory of real loss."
        return "The grief patterns persist and deepen. Whatever ended was central to your life's architecture."

    # Enhanced default responses
    if conversation_depth >= 4:
        return "Multiple layers emerging—the system tracks frustration with creative barriers, intelligence versus ambition tensions, and relationship transitions. Each thread carries its own emotional signature."

    if total_patterns >= 6:
        return "Rich emotional complexity mapped—you're carrying the full spectrum of human experience through whatever transition you're navigating."

    if conversation_depth > 2:
        return "Your emotional patterns continue to evolve. The system tracks the subtle shifts as you move through this territory."

    return "You're carrying something layered. Let's sit with it and see what wants to be named."


# Example usage
if __name__ == "__main__":
    result = parse_input(
        "I feel reverent and recursive—like something ancient is looping through me, not to collapse but to deepen.",
        "parser/signal_lexicon.json"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
