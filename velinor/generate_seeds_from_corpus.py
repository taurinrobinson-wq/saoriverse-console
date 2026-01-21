#!/usr/bin/env python3
"""Generate seeds from phrase corpus using real Emotional OS gates.

Reads a phrase corpus, derives emotional gates from each phrase using
the Emotional OS parser, and writes cipher_seeds.json with full layers.
"""
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

# Import Emotional OS components
try:
    from emotional_os.core.signal_parser import (
        load_signal_map,
        parse_signals,
        convert_signal_names_to_codes,
        evaluate_gates,
    )
    from emotional_os.core import constants as e_constants
    HAS_EMOTIONAL_OS = True
except ImportError:
    HAS_EMOTIONAL_OS = False
    print("Warning: Emotional OS not available; gates will be empty")


# 12 Velinorian phrases (user-provided)
PHRASE_CORPUS = [
    # Layer 0 — surface fragments (poetic, incomplete, safe)
    {
        "layer": 0,
        "text": "Wind carries the names we no longer speak.",
        "npc": "Echo",
        "tags": ["memory", "loss"],
    },
    {
        "layer": 0,
        "text": "A boundary is a story told in stone.",
        "npc": "Tala",
        "tags": ["protection", "boundary"],
    },
    {
        "layer": 0,
        "text": "Shadows gather where memory thins.",
        "npc": "Archivist",
        "tags": ["forgetting", "darkness"],
    },
    # Layer 1 — deeper fragments (hint at emotional truth)
    {
        "layer": 1,
        "text": "You stood at the threshold long before you knew it existed.",
        "npc": "Velinor",
        "tags": ["destiny", "threshold"],
    },
    {
        "layer": 1,
        "text": "The heart keeps its own archive, even when the mind refuses.",
        "npc": "Saori",
        "tags": ["hidden", "truth"],
    },
    {
        "layer": 1,
        "text": "Some promises echo louder when broken.",
        "npc": "Oath-keeper",
        "tags": ["pact", "betrayal"],
    },
    # Layer 2 — plaintext (emotionally gated revelations)
    {
        "layer": 2,
        "text": "I could not name the fear, so I carried it in silence.",
        "npc": "Whisper",
        "tags": ["fear", "silence"],
    },
    {
        "layer": 2,
        "text": "Your presence softened the places I had armored for years.",
        "npc": "Saori",
        "tags": ["tenderness", "vulnerability"],
    },
    {
        "layer": 2,
        "text": "I hid the truth because I feared you would see the whole of me.",
        "npc": "Velinor",
        "tags": ["shame", "exposure"],
    },
    {
        "layer": 2,
        "text": "The pact failed because neither of us could bear the weight of honesty.",
        "npc": "Oath-keeper",
        "tags": ["broken", "honesty"],
    },
    {
        "layer": 2,
        "text": "I remember you even in the fractures — especially there.",
        "npc": "Echo",
        "tags": ["memory", "brokenness"],
    },
    {
        "layer": 2,
        "text": "Quiet Bloom is not affection; it is surrender without collapse.",
        "npc": "Archivist",
        "tags": ["surrender", "bloom"],
    },
]


def derive_gates_from_text(text: str) -> List[str]:
    """Use Emotional OS to derive required gates from phrase text."""
    if not HAS_EMOTIONAL_OS:
        return []

    try:
        # Load signal map
        base = e_constants.DEFAULT_LEXICON_BASE
        signal_map = load_signal_map(base)

        # Parse signals from text
        signals = parse_signals(text, signal_map)
        signals = convert_signal_names_to_codes(signals)

        # Evaluate gates
        gates = evaluate_gates(signals)

        return gates if gates else []
    except Exception as e:
        print(f"  Warning: Could not derive gates for '{text[:50]}...': {e}")
        return []


def generate_seeds() -> List[Dict[str, Any]]:
    """Generate seed entries from the phrase corpus."""
    seeds = []

    for idx, phrase_entry in enumerate(PHRASE_CORPUS, start=1):
        text = phrase_entry.get("text", "")
        layer = phrase_entry.get("layer", 2)
        npc = phrase_entry.get("npc", "unknown")
        tags = phrase_entry.get("tags", [])

        # Generate a deterministic but unique ID
        seed_id = f"velinor-{layer:d}-{idx:03d}"

        # Derive required gates from the text
        required_gates = derive_gates_from_text(text)

        # For layer 2 (plaintext), also add manual gate hints based on tags
        if layer == 2 and tags:
            gate_hints = {
                "silence": "Infrasensory Oblivion",
                "fear": "Primal Oblivion",
                "tenderness": "Quiet Bloom",
                "vulnerability": "Echoed Breath",
                "shame": "Fractured Memory",
                "broken": "Hollow Pact",
                "surrender": "Quiet Bloom",
                "bloom": "Quiet Bloom",
                "boundary": "Iron Boundary",
            }
            for tag in tags:
                if tag in gate_hints:
                    hint_gate = gate_hints[tag]
                    if hint_gate not in required_gates:
                        required_gates.append(hint_gate)

        seed = {
            "id": seed_id,
            "phrase": text,
            "layer": layer,
            "npc": npc,
            "tags": tags,
            "required_gates": required_gates,
        }
        seeds.append(seed)
        print(f"  [{idx}] Layer {layer}: {text[:40]}... → gates: {required_gates}")

    return seeds


def main():
    """Generate seeds and write to cipher_seeds.json."""
    print("Generating cipher seeds from Velinorian phrase corpus...")
    print()

    seeds = generate_seeds()

    # Write to cipher_seeds.json
    out_path = Path(__file__).parent / "cipher_seeds.json"
    output = {"seeds": seeds}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"✓ Wrote {len(seeds)} seeds to {out_path}")
    print()


if __name__ == "__main__":
    main()
