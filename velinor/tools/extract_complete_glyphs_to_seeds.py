"""
Build authoritative cipher_seeds.json from complete glyph ecosystem

Integrates:
1. Glyph_Organizer.json - 75 base glyphs (full structure)
2. Glyph_Fragments.csv - 36 intermediate fragments (ability progression)
3. Glyph_Transcendence.csv - 7 fusion glyphs (boss encounters & endgame)

The cipher system becomes the delivery mechanism for ALL three tiers.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class CipherSeed:
    """A cipher seed that unlocks one glyph tier."""
    id: str
    tier: str  # "base", "fragment", "transcendence"
    glyph_id: Optional[int]  # ID from Glyph_Organizer.json
    glyph_name: str
    npc: str
    category: str  # Domain/Category
    location: str
    layer_0: str  # Poetic hint
    layer_1: str  # Fragment/context
    layer_2: str  # Plaintext manifestation
    required_gates: List[str]
    tags: List[str]
    original_storyline: str  # Full story from CSV
    remnants_integration: Optional[List[str]] = None
    ability_gained: Optional[str] = None
    player_choices: Optional[List[str]] = None
    

def load_glyph_organizer_json() -> List[Dict]:
    """Load base glyphs from Glyph_Organizer.json"""
    path = Path("velinor/markdowngameinstructions/glyphs/Glyph_Organizer.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("glyphs", [])


def load_glyph_fragments_csv() -> List[Dict]:
    """Load intermediate fragments from Glyph_Fragments.csv"""
    fragments = []
    path = Path("velinor/markdowngameinstructions/glyphs/Glyph_Fragments.csv")
    
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fragments.append(row)
    
    return fragments


def load_glyph_transcendence_csv() -> List[Dict]:
    """Load fusion glyphs from Glyph_Transcendence.csv"""
    transcendence = []
    path = Path("velinor/markdowngameinstructions/glyphs/Glyph_Transcendence.csv")
    
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transcendence.append(row)
    
    return transcendence


def category_to_gates(category: str) -> List[str]:
    """Map glyph category to emotional gates."""
    mapping = {
        "Collapse": ["fear", "fracture", "dissolution"],
        "Sovereignty": ["clarity", "boundary", "choice"],
        "Ache": ["grief", "loss", "betrayal"],
        "Presence": ["witness", "touch", "silence"],
        "Joy": ["celebration", "reunion", "spark"],
        "Trust": ["communion", "interdependence", "faith"],
        "Legacy": ["memory", "inheritance", "transmission"],
        "Transcendence": ["coherence", "convergence", "synthesis"],
    }
    return mapping.get(category, ["emotion"])


def extract_manifestation(storyline: str) -> str:
    """Extract the key emotional realization from storyline."""
    import re
    
    patterns = [
        r"The (?:glyph )?manifests when (.+?)(?:\.|$)",
        r"The player (?:learns|realizes|recognizes|accepts|understands) (.+?)(?:\.|$)",
        r"is revealed when (.+?)(?:\.|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, storyline, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Fallback: use last sentence
    sentences = [s.strip() for s in storyline.split(".") if s.strip()]
    return sentences[-1] if sentences else storyline[:100]


def build_base_glyph_seeds() -> List[Dict]:
    """Build cipher seeds from 75 base glyphs."""
    seeds = []
    glyphs = load_glyph_organizer_json()
    
    for idx, glyph in enumerate(glyphs, 1):
        glyph_id = glyph.get("id")
        glyph_name = glyph.get("glyph_name", "Unknown")
        domain = glyph.get("domain", "Legacy")
        npc_data = glyph.get("npc", {})
        npc_name = npc_data.get("name", "Unknown").split()[0] if isinstance(npc_data, dict) else str(npc_data)
        location = glyph.get("location", "Unknown")
        storyline = glyph.get("storyline_summary", "")
        
        # Extract plaintext manifestation
        plaintext = extract_manifestation(storyline)
        
        # Create fragments
        words = plaintext.split()[:15]
        fragment_0 = " ".join(words)
        if len(plaintext.split()) > 15:
            fragment_0 += "…"
        
        # Fragment 1: category-based hint
        hints = {
            "Collapse": "What breaks can teach what was fragile.",
            "Sovereignty": "Clarity lives in choosing what you hold and what you release.",
            "Ache": "Grief, when witnessed, becomes wisdom.",
            "Presence": "To witness is to honor without changing.",
            "Joy": "Joy returns when we stop waiting for permission.",
            "Trust": "Bonds forged through reliable action endure.",
            "Legacy": "The living carry forward what breath can hold.",
        }
        fragment_1 = hints.get(domain, "Something stirs at the edge of knowing.")
        
        seed = {
            "id": f"velinor-base-{idx:03d}",
            "tier": "base",
            "glyph_id": glyph_id,
            "glyph_name": glyph_name,
            "npc": npc_name,
            "category": domain,
            "location": location,
            "layer_0": fragment_0,
            "layer_1": fragment_1,
            "layer_2": plaintext,
            "required_gates": category_to_gates(domain),
            "tags": [domain.lower(), npc_name.lower()],
            "original_storyline": storyline,
            "remnants_integration": glyph.get("remnants_integration", []),
            "player_choices": glyph.get("player_choices", []),
        }
        seeds.append(seed)
    
    return seeds


def build_fragment_seeds() -> List[Dict]:
    """Build cipher seeds from 36 intermediate fragments."""
    seeds = []
    fragments = load_glyph_fragments_csv()
    
    for idx, frag in enumerate(fragments, 1):
        frag_id = frag.get("Fragment_ID", f"GF-{idx:03d}")
        npc_name = frag.get("NPC_Name", "Unknown").split()[0]
        title = frag.get("Title", "Unknown Fragment")
        ability = frag.get("Ability_Gained", "")
        storyline = frag.get("Storyline", "")
        emotional_focus = frag.get("Emotional_Focus", "")
        
        # Extract plaintext
        plaintext = extract_manifestation(storyline)
        
        # Create fragments
        words = plaintext.split()[:12]
        fragment_0 = " ".join(words)
        if len(plaintext.split()) > 12:
            fragment_0 += "…"
        
        fragment_1 = f"A step toward {title.lower()}..."
        
        seed = {
            "id": f"velinor-frag-{idx:03d}",
            "tier": "fragment",
            "glyph_id": None,
            "glyph_name": title,
            "npc": npc_name,
            "category": "Fragment",
            "location": frag.get("Biome", "Unknown"),
            "layer_0": fragment_0,
            "layer_1": fragment_1,
            "layer_2": plaintext,
            "required_gates": ["insight", "growth"],  # Fragments are less emotionally gated
            "tags": ["fragment", npc_name.lower(), emotional_focus.lower()],
            "original_storyline": storyline,
            "ability_gained": ability,
        }
        seeds.append(seed)
    
    return seeds


def build_transcendence_seeds() -> List[Dict]:
    """Build cipher seeds from 7 transcendence/fusion glyphs."""
    seeds = []
    transcendence = load_glyph_transcendence_csv()
    
    for idx, trans in enumerate(transcendence, 1):
        glyph_name = trans.get("Glyph", "Unknown")
        npc_name = trans.get("NPC Receiver", "Unknown").split()[0]
        location = trans.get("Location", "Unknown")
        theme = trans.get("Theme", "")
        storyline = trans.get("Storyline", "")
        
        # Extract plaintext
        plaintext = extract_manifestation(storyline)
        
        # Create fragments
        words = plaintext.split()[:12]
        fragment_0 = " ".join(words)
        if len(plaintext.split()) > 12:
            fragment_0 += "…"
        
        fragment_1 = f"The convergence of {theme.lower()}..."
        
        seed = {
            "id": f"velinor-trans-{idx:03d}",
            "tier": "transcendence",
            "glyph_id": None,
            "glyph_name": glyph_name,
            "npc": npc_name,
            "category": "Transcendence",
            "location": location,
            "layer_0": fragment_0,
            "layer_1": fragment_1,
            "layer_2": plaintext,
            "required_gates": ["coherence", "synthesis", "unity"],  # Transcendence requires high alignment
            "tags": ["transcendence", "endgame", theme.lower()],
            "original_storyline": storyline,
        }
        seeds.append(seed)
    
    return seeds


def main():
    """Generate authoritative cipher_seeds.json"""
    print("\n📖 Building Authoritative Cipher Seeds from Complete Glyph Ecosystem\n")
    
    print("🔄 Loading base glyphs...")
    base_seeds = build_base_glyph_seeds()
    print(f"   ✓ {len(base_seeds)} base glyphs loaded")
    
    print("🔄 Loading fragments...")
    fragment_seeds = build_fragment_seeds()
    print(f"   ✓ {len(fragment_seeds)} fragments loaded")
    
    print("🔄 Loading transcendence glyphs...")
    trans_seeds = build_transcendence_seeds()
    print(f"   ✓ {len(trans_seeds)} transcendence glyphs loaded")
    
    # Combine all
    all_seeds = base_seeds + fragment_seeds + trans_seeds
    
    print(f"\n✓ Total seeds: {len(all_seeds)}")
    print(f"  - Base: {len(base_seeds)}")
    print(f"  - Fragments: {len(fragment_seeds)}")
    print(f"  - Transcendence: {len(trans_seeds)}")
    
    # Build output
    output = {
        "metadata": {
            "version": "3.0",
            "description": "Authoritative cipher seeds integrating all glyph tiers",
            "sources": [
                "Glyph_Organizer.json (75 base glyphs)",
                "Glyph_Fragments.csv (36 intermediate fragments)",
                "Glyph_Transcendence.csv (7 fusion/endgame glyphs)",
            ],
            "integration": "Cipher seeds unlock glyphs across all three tiers",
            "total_glyphs": len(all_seeds),
            "tier_breakdown": {
                "base": len(base_seeds),
                "fragment": len(fragment_seeds),
                "transcendence": len(trans_seeds),
            }
        },
        "seeds": all_seeds,
    }
    
    # Write JSON
    output_path = Path("velinor/cipher_seeds_complete.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Wrote {output_path}")
    
    # Summary by tier
    print("\n📊 Seeds by Tier:")
    print(f"  Base:          {len(base_seeds):2d} glyphs")
    print(f"  Fragments:     {len(fragment_seeds):2d} intermediate steps")
    print(f"  Transcendence: {len(trans_seeds):2d} boss encounters/endgame")
    
    print("\n✓ Integration complete: All glyph tiers now available as cipher seeds")


if __name__ == "__main__":
    main()
