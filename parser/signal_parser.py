import json
import re
import sqlite3
import os
from typing import List, Dict
from datetime import datetime

# Load signal lexicon from JSON (base + learned)
def load_signal_map(base_path: str, learned_path: str = "parser/learned_lexicon.json") -> Dict[str, Dict]:
    base_lexicon = {}
    if os.path.exists(base_path):
        with open(base_path, 'r', encoding='utf-8') as f:
            base_lexicon = json.load(f)

    learned_lexicon = {}
    if os.path.exists(learned_path):
        try:
            with open(learned_path, 'r', encoding='utf-8') as f:
                learned_lexicon = json.load(f)
        except Exception:
            pass

    combined_lexicon = base_lexicon.copy()
    combined_lexicon.update(learned_lexicon)
    return combined_lexicon

# Extract signals using fuzzy matching
def parse_signals(input_text: str, signal_map: Dict[str, Dict]) -> List[Dict]:
    lowered = input_text.lower()
    matched_signals = []
    for keyword, metadata in signal_map.items():
        if re.search(rf"\b{re.escape(keyword)}\b", lowered) or keyword in lowered:
            matched_signals.append({
                "keyword": keyword,
                "signal": metadata.get("signal"),
                "voltage": metadata.get("voltage", "medium"),
                "tone": metadata.get("tone", "unknown")
            })
    return matched_signals

# Map signals to ECM gates
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

# Retrieve glyphs from SQLite
def fetch_glyphs(gates: List[str], db_path: str = 'glyphs.db') -> List[Dict]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in gates)
    query = f"SELECT glyph_name, description, gate FROM glyph_lexicon WHERE gate IN ({placeholders})"
    cursor.execute(query, gates)
    rows = cursor.fetchall()
    conn.close()
    return [{"glyph_name": r[0], "description": r[1], "gate": r[2]} for r in rows]

# Generate ritual prompt
def generate_prompt(glyphs: List[Dict]) -> str:
    if not glyphs:
        return "No glyphs activated."
    return f"Would you like to mark this moment with {glyphs[0]['glyph_name']}?"

# Generate voltage response based on theme density
def generate_voltage_response(glyphs: List[Dict], conversation_context: Dict = None) -> str:
    themes = {
        "grief": 0, "longing": 0, "containment": 0,
        "joy": 0, "devotion": 0, "recognition": 0, "insight": 0
    }

    for g in glyphs:
        name = g["glyph_name"].lower()
        if any(k in name for k in ["grief", "mourning", "collapse", "sorrow"]): themes["grief"] += 1
        if any(k in name for k in ["ache", "yearning", "longing", "recursive"]): themes["longing"] += 1
        if any(k in name for k in ["boundary", "contain", "still", "shield"]): themes["containment"] += 1
        if any(k in name for k in ["joy", "delight", "ecstasy", "bliss"]): themes["joy"] += 1
        if any(k in name for k in ["devotional", "vow", "exalted", "sacred"]): themes["devotion"] += 1
        if any(k in name for k in ["recognition", "seen", "witness", "mirror"]): themes["recognition"] += 1
        if any(k in name for k in ["insight", "clarity", "knowing", "revelation"]): themes["insight"] += 1

    dominant = sorted(themes.items(), key=lambda x: x[1], reverse=True)
    top_themes = [t[0] for t in dominant if t[1] > 0][:2]

    if top_themes == ["grief", "containment"]:
        return "You're holding a lot right now—and doing it with care. It's okay to feel the weight of it."

    if top_themes == ["grief", "longing"]:
        return "Deep grief mixed with yearning—that's the territory of profound loss."

    if top_themes == ["longing", "devotion"]:
        return "There's something you care about deeply, maybe even painfully. That kind of longing is sacred."

    if top_themes == ["joy", "recognition"]:
        return "You're being seen in your joy. Let it land."

    if top_themes == ["grief", "recognition"]:
        return "You're being seen in your sorrow. That kind of witnessing matters."

    return "You're carrying something layered. Let's sit with it and see what wants to be named."

# Main parser function
def parse_input(input_text: str, lexicon_path: str, db_path: str = 'glyphs.db', conversation_context: Dict = None) -> Dict:
    signal_map = load_signal_map(lexicon_path)
    signals = parse_signals(input_text, signal_map)
    gates = evaluate_gates(signals)
    glyphs = fetch_glyphs(gates, db_path)
    ritual_prompt = generate_prompt(glyphs)
    voltage_response = generate_voltage_response(glyphs, conversation_context)

    return {
        "timestamp": datetime.now().isoformat(),
        "input": input_text,
        "signals": signals,
        "gates": gates,
        "glyphs": glyphs,
        "ritual_prompt": ritual_prompt,
        "voltage_response": voltage_response
    }

# Example usage
if __name__ == "__main__":
    input_text = input("Enter emotional input: ")
    result = parse_input(input_text, "velonix_lexicon.json")
    print(json.dumps(result, indent=2, ensure_ascii=False))
