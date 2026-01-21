"""
Extract glyph manifestation moments and build authoritative cipher_seeds.json

This script:
1. Parses Glyph_Organizer.csv
2. Extracts the "manifestation moment" (plaintext truth) from each glyph's storyline
3. Creates 3-layer cipher seeds (hint → fragment → plaintext)
4. Maps emotional gates to glyph categories
5. Generates full cipher_seeds.json integrated with the game
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Glyph category to emotional gates mapping
CATEGORY_TO_GATES = {
    "Collapse": ["fear", "fracture", "dissolution"],
    "Sovereignty": ["clarity", "boundary", "choice"],
    "Ache": ["grief", "loss", "betrayal"],
    "Presence": ["witness", "touch", "silence"],
    "Joy": ["celebration", "reunion", "spark"],
    "Trust": ["communion", "interdependence", "faith"],
    "Legacy": ["memory", "inheritance", "transmission"],
}

# NPC name normalization (handle variations)
NPC_ALIASES = {
    "Archivist Malrik": "Malrik",
    "Captain Veynar": "Veynar",
    "Coren the Mediator": "Coren",
    "Dakrin - Trial Warden": "Dakrin",
    "Dalen the Rusted Guide": "Dalen",
    "Drossel the Cloaked": "Drossel",
    "Elka - Glyph Console Worshipper": "Elka",
    "Helia - Shrine Healer": "Helia",
    "High Seer Elenya": "Elenya",
    "Inodora - Story Teller": "Inodora",
    "Juria & Korinth - Sea Merchants": "Juria",
    "Kaelen the Suspected Thief": "Kaelen",
    "Kiv - Clay Hermit": "Kiv",
    "Korrin the Gossip": "Korrin",
    "Lark - Shrine Mason": "Lark",
    "Lira - Skilled Boatmaker": "Lira",
    "Mariel the Weaver": "Mariel",
    "Nima": "Nima",
    "Nordia the Mourning Singer": "Nordia",
    "Orvak - Ruined Watcher": "Orvak",
    "Rasha - Ferry Operator": "Rasha",
    "Ravi": "Ravi",
    "Sanor - Silent Elder": "Sanor",
    "Sealina - Street Performer": "Sealina",
    "Sera the Herb Novice": "Sera",
    "Seyla - Archivist of Lineage": "Seyla",
    "Sybil - Forest Loner Camper": "Sybil",
    "Tala - Market Cook": "Tala",
    "Tessa - Desert Widow": "Tessa",
    "Thalma - The Desert Listener": "Thalma",
    "Thoran - Mask-Maker": "Thoran",
    "Tovren the Cartwright": "Tovren",
    "Velka - Bone Keeper": "Velka",
    "Saori": "Saori",
    "Mariel the Weaver (secondary quest)": "Mariel",
    "Kaelen the Suspected Thief (as swamp trickster)": "Kaelen",
    "Ravi, Nima": "Ravi",
}


def extract_manifestation(storyline: str) -> Optional[str]:
    """Extract the key emotional realization from the storyline."""
    patterns = [
        r"The glyph manifests when (.+?)(?:\.|$)",
        r"This glyph reveals itself when (.+?)(?:\.|$)",
        r"reveals itself when (.+?)(?:\.|$)",
        r"manifests as (.+?)(?:\.|$)",
        r"The player (?:learns|realizes|recognizes|accepts|understands) (.+?)(?:\.|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, storyline, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Clean up some artifacts
            text = text.replace("???", "'").replace("?", "'")
            return text

    # Fallback: use last sentence
    sentences = [s.strip() for s in storyline.split(".") if s.strip()]
    if sentences:
        return sentences[-1]

    return None


def create_fragments(plaintext: str, npc_name: str, category: str) -> Tuple[str, str]:
    """Create layer 0 and 1 fragments from plaintext."""
    # Layer 0: Poetic fragment (first 15-20 words or key phrase)
    words = plaintext.split()[:15]
    fragment_0 = " ".join(words)
    if len(plaintext.split()) > 15:
        fragment_0 += "…"

    # Layer 1: NPC-perspective fragment (based on category and NPC voice)
    npc_voices = {
        "Malrik": "Archives hold what memory refuses.",
        "Ravi": "Sometimes bearing witness is all we can offer.",
        "Nima": "Loss has a weight that never leaves.",
        "Elenya": "The sacred emerges when we stop forcing it.",
        "Veynar": "Authority without trust is only shadow.",
        "Dalen": "Scars are proof we survived.",
        "Saori": "Presence speaks louder than words.",
    }

    # Build default fragment based on category
    category_hints = {
        "Collapse": "Fracture arrives quietly, unannounced.",
        "Sovereignty": "Clarity is choosing what you will and won't hold.",
        "Ache": "Grief becomes wisdom only when fully felt.",
        "Presence": "To witness is to honor without changing.",
        "Joy": "Liberation lives in small renewals.",
        "Trust": "Bonds are forged through reliable action.",
        "Legacy": "The living carry forward what breath can hold.",
    }

    fragment_1 = npc_voices.get(npc_name, category_hints.get(category, "Something stirs at the edge of knowing."))

    return fragment_0, fragment_1


def build_seed_id(category: str, count: int, index: int) -> str:
    """Generate seed ID like velinor-collapse-001."""
    category_short = category.lower()[:4]
    return f"velinor-{category_short}-{index:03d}"


def parse_glyphs(csv_path: Path) -> List[Dict]:
    """Parse CSV and extract seeds."""
    seeds = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        index_by_category = {}

        for row in reader:
            category = row["Category"].strip()
            npc_full = row["NPC Giver"].strip()
            glyph_name = row["Glyph"].strip()
            storyline = row["Storyline"].strip()

            # Normalize NPC name
            npc = NPC_ALIASES.get(npc_full, npc_full)

            # Extract manifestation moment (plaintext)
            plaintext = extract_manifestation(storyline)
            if not plaintext:
                print(f"⚠ Could not extract manifestation from: {glyph_name}")
                continue

            # Track index per category
            if category not in index_by_category:
                index_by_category[category] = 1

            index = index_by_category[category]
            index_by_category[category] += 1

            # Create fragments
            fragment_0, fragment_1 = create_fragments(plaintext, npc, category)

            # Map gates
            gates = CATEGORY_TO_GATES.get(category, ["emotion"])

            # Build seed
            seed = {
                "id": build_seed_id(category, index, index),
                "glyph_name": glyph_name,
                "npc": npc,
                "category": category,
                "location": row["Location"].strip(),
                "layer": 2,  # Layer 2 = plaintext (emotionally gated)
                "phrase": plaintext,
                "required_gates": gates,
                "tags": [category.lower(), npc.lower()],
                "fragments": {
                    "layer_0": fragment_0,
                    "layer_1": fragment_1,
                    "layer_2": plaintext,
                },
            }

            seeds.append(seed)

    return seeds


def main():
    """Generate cipher_seeds.json from glyph organizer."""
    csv_path = Path("velinor/markdowngameinstructions/glyphs/Glyph_Organizer.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        return

    print("📖 Parsing Glyph_Organizer.csv...")
    seeds = parse_glyphs(csv_path)
    
    print(f"✓ Extracted {len(seeds)} glyphs")

    # Build output structure
    output = {
        "metadata": {
            "version": "2.0",
            "source": "Glyph_Organizer.csv",
            "integration": "Cipher seeds unlock glyphs in-game",
            "total_glyphs": len(seeds),
        },
        "seeds": seeds,
    }

    # Write JSON
    output_path = Path("velinor/cipher_seeds.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Wrote {output_path}")
    
    # Summary by category
    by_category = {}
    for seed in seeds:
        cat = seed["category"]
        by_category[cat] = by_category.get(cat, 0) + 1

    print("\n📊 Seeds by Category:")
    for cat in sorted(by_category.keys()):
        count = by_category[cat]
        gates = CATEGORY_TO_GATES.get(cat, [])
        print(f"  {cat:15} {count:2d} glyphs  →  {', '.join(gates)}")

    print("\n✓ Integration complete: cipher_seeds.json now maps to glyph system")


if __name__ == "__main__":
    main()
