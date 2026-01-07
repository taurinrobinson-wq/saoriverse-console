#!/usr/bin/env python3
"""
Enhance expanded glyph CSV with missing unlock conditions and special metadata
"""

import csv
from pathlib import Path

def enhance_expanded_glyph_csv():
    """Add missing unlock conditions based on NPC and story context."""
    
    input_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Organizer_Expanded.csv")
    output_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Organizer_Expanded.csv")
    
    # Special unlock conditions for glyphs missing them
    SPECIAL_UNLOCK_CONDITIONS = {
        "Glyph of Apprehension": "after_kaelen_swamp_encounter",
        "Glyph of Covenant Bone": "after_ossuary_ruins_discovery",
        "Glyph of Echoed Breath": "after_tomb_of_echoes_ritual",
        "Glyph of Infrasensory Oblivion": "after_chamber_of_delayed_echoes_discovery",
        "Glyph of Legacy": "after_kaelen_confession",  # Requires Kaelen confession about Ophina
        "Glyph of Mutual Passage": "after_ferry_operator_alignment",
        "Glyph of Returning Song": "after_mourning_singer_reconnection",
        "Glyph of Worn Cloth": "after_mariel_secondary_quest"
    }
    
    # Read expanded CSV
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    
    # Update missing unlock conditions
    updated_count = 0
    for row in rows:
        glyph_name = row.get("glyph_name", "")
        if glyph_name in SPECIAL_UNLOCK_CONDITIONS:
            if not row.get("unlock_condition"):
                row["unlock_condition"] = SPECIAL_UNLOCK_CONDITIONS[glyph_name]
                updated_count += 1
    
    # Write updated CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Enhanced expanded CSV: {output_path}")
    print(f"  - Updated unlock conditions: {updated_count}")
    print(f"  - Total glyphs: {len(rows)}")
    
    return rows

if __name__ == "__main__":
    rows = enhance_expanded_glyph_csv()
