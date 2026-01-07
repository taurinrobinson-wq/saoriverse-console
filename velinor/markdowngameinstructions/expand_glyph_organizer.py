#!/usr/bin/env python3
"""
Glyph Organizer CSV Expansion Script
Expands Glyph_Organizer.csv with 16 new metadata columns supporting:
- Complete NPC-glyph mappings
- Unlock conditions and stat gates  
- Fusion group relationships (triglyph, octoglyph, pentaglyph, hexaglyph, heptaglyph, tetraglyph)
- Boss gate assignments
- REMNANTS effect mappings
- Semantic/emotional OS integration
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple

# Fusion group mappings from Glyph_Transcendence.csv
FUSION_ARCHETYPES = {
    "triglyph": {
        "glyphs": ["Glyph of Sorrow", "Glyph of Remembrance", "Glyph of Legacy"],
        "boss": "witnessed_crown",
        "chamber": "Triglyph Chamber",
        "receiver": "Ravi & Nima",
        "fusion_glyph": "Glyph of Contained Loss",
        "theme": "coherence of Loss",
        "moral_choice": "take_or_leave_contained_loss",
        "semantic_tags": "grief,memory,legacy,presence",
        "remnants_effects": "empathy:+0.3,need:+0.2,memory:+0.2"
    },
    "octoglyph": {
        "glyphs": [
            "Glyph of Infrasensory Oblivion",
            "Glyph of Sensory Oblivion",
            "Glyph of Primal Oblivion",
            "Glyph of Dislocated Attachment",
            "Glyph of Preemptive Severance",
            "Glyph of Interruptive Restraint",
            "Glyph of Held Ache",
            "Glyph of Hopeful Transmission"
        ],
        "boss": "severed_choir",
        "chamber": "Octoglyph Chamber",
        "receiver": "Coren the Mediator",
        "fusion_glyph": "Glyph of Transmuted Abandonment",
        "theme": "coherence of Abandonment",
        "moral_choice": "take_or_leave_transmuted_abandonment",
        "semantic_tags": "abandonment,severance,harmony,coherence",
        "remnants_effects": "empathy:+0.3,trust:+0.2,presence:+0.2"
    },
    "pentaglyph": {
        "glyphs": [
            "Glyph of Reckless Trial",
            "Glyph of Iron Boundary",
            "Glyph of Measured Step",
            "Glyph of Hidden Passage",
            "Glyph of Covenant Flame"
        ],
        "boss": "lawbound_sentinel",
        "chamber": "Pentaglyph Chamber",
        "receiver": "Captain Veynar",
        "fusion_glyph": "Glyph of Disciplined Boundaries",
        "theme": "coherence of Sovereignty",
        "moral_choice": "take_or_leave_disciplined_boundaries",
        "semantic_tags": "sovereignty,boundaries,discipline,clarity",
        "remnants_effects": "authority:+0.2,empathy:+0.1,presence:+0.1"
    },
    "hexaglyph_silence": {
        "glyphs": [
            "Glyph of Listening Silence",
            "Glyph of Tender Witness",
            "Glyph of Echo Communion",
            "Glyph of Steadfast Witness",
            "Glyph of Emotional Inheritance",
            "Glyph of Widow's Cry"
        ],
        "boss": "silent_choir",
        "chamber": "Hexaglyph Chamber",
        "receiver": "Shrine Healer",
        "fusion_glyph": "Glyph of Witnessed Silence",
        "theme": "coherence of Presence",
        "moral_choice": "take_or_leave_witnessed_silence",
        "semantic_tags": "presence,silence,witness,communion",
        "remnants_effects": "empathy:+0.3,presence:+0.2,need:+0.1"
    },
    "heptaglyph": {
        "glyphs": [
            "Glyph of Laughter's Balm",
            "Glyph of Shared Feast",
            "Glyph of Hidden Warmth",
            "Glyph of Arrival",
            "Glyph of Crafted Wonder",
            "Glyph of Returning Song",
            "Glyph of Whispered Pact"
        ],
        "boss": "reveler_mask",
        "chamber": "Heptaglyph Chamber",
        "receiver": "Sera the Herb Novice",
        "fusion_glyph": "Glyph of Communal Resurrection",
        "theme": "coherence of Joy",
        "moral_choice": "take_or_leave_communal_resurrection",
        "semantic_tags": "joy,reunion,creativity,hope",
        "remnants_effects": "empathy:+0.2,memory:+0.1,trust:+0.2"
    },
    "tetraglyph": {
        "glyphs": [
            "Glyph of Shared Burden",
            "Glyph of Binding Cloth",
            "Glyph of Weary Justice",
            "Glyph of Mutual Passage"
        ],
        "boss": "fractured_bridge",
        "chamber": "Tetraglyph Chamber",
        "receiver": "Mariel the Weaver",
        "fusion_glyph": "Glyph of Interwoven Bonds",
        "theme": "coherence of Trust",
        "moral_choice": "take_or_leave_interwoven_bonds",
        "semantic_tags": "trust,interdependence,bonds,community",
        "remnants_effects": "empathy:+0.2,trust:+0.3,presence:+0.1"
    },
    "hexaglyph_collapse": {
        "glyphs": [
            "Glyph of Fractured Memory",
            "Glyph of Mirage Echo",
            "Glyph of Venomous Choice",
            "Glyph of Masked Boundary",
            "Glyph of Broken Vessel",
            "Glyph of Hidden Ache"
        ],
        "boss": "shattered_archive",
        "chamber": "Hexaglyph Chamber",
        "receiver": "Archivist Malrik",
        "fusion_glyph": "Glyph of Accepted Uncertainty",
        "theme": "coherence of Collapse",
        "moral_choice": "take_or_leave_accepted_uncertainty",
        "semantic_tags": "collapse,acceptance,uncertainty,fracture",
        "remnants_effects": "empathy:+0.2,memory:+0.2,presence:+0.1"
    }
}

# Semantic tag mapping by emotional category
SEMANTIC_TAGS_BY_CATEGORY = {
    "Ache": "grief,memory,ache,loss,betrayal",
    "Collapse": "fracture,collapse,fear,distortion,severance",
    "Presence": "presence,silence,witness,touch,communion",
    "Joy": "joy,reunion,creativity,spark,warmth",
    "Trust": "trust,community,interdependence,covenant,bonds",
    "Legacy": "legacy,inheritance,ancestry,transmission,presence",
    "Sovereignty": "sovereignty,boundaries,choice,clarity,discipline"
}

# REMNANTS effects by glyph category
REMNANTS_BY_CATEGORY = {
    "Ache": "empathy:+0.2,need:+0.1",
    "Collapse": "memory:-0.1,presence:+0.1,empathy:+0.1",
    "Presence": "presence:+0.2,empathy:+0.1",
    "Joy": "empathy:+0.1,trust:+0.2,memory:+0.1",
    "Trust": "trust:+0.2,empathy:+0.1,presence:+0.1",
    "Legacy": "memory:+0.2,empathy:+0.1,authority:+0.1",
    "Sovereignty": "authority:+0.1,empathy:+0.1,presence:+0.1"
}

# NPC-specific unlock conditions
NPC_UNLOCK_CONDITIONS = {
    "Ravi": "after_nima_encounter",
    "Nima": "after_marketplace_exploration",
    "Archivist Malrik": "after_archive_discovery",
    "Captain Veynar": "after_guard_barracks_visit",
    "Coren the Mediator": "after_cult_encampment_encounter",
    "Dakrin - Trial Warden": "after_trial_grounds_intro",
    "Dalen the Rusted Guide": "after_caravan_ruins_discovery",
    "Drossel the Cloaked": "after_market_infiltration",
    "Elka - Glyph Console Worshipper": "after_shrine_visit",
    "Helia - Shrine Healer": "after_shrine_healing_intro",
    "High Seer Elenya": "after_mountain_reach",
    "Inodora - Story Teller": "after_communal_gathering",
    "Juria & Korinth - Sea Merchants": "after_harbor_arrival",
    "Kaelen the Suspected Thief": "after_market_encounter",
    "Kiv - Clay Hermit": "after_forest_clearing_discover",
    "Korrin the Gossip": "after_market_infiltration",
    "Lark - Shrine Mason": "after_river_crossing",
    "Lira - Skilled Boatmaker": "after_harbor_arrival",
    "Mariel the Weaver": "after_shrine_arrival",
    "Nordia the Mourning Singer": "after_civic_center_exploration",
    "Orvak - Ruined Watcher": "after_watchtower_discovery",
    "Rasha - Ferry Operator": "after_harbor_arrival",
    "Sanor - Silent Elder": "after_shrine_visit",
    "Sealina - Street Performer": "after_market_exploration",
    "Sera the Herb Novice": "after_shrine_garden_intro",
    "Seyla - Archivist of Lineage": "after_desert_tomb_reach",
    "Sybil - Forest Loner Camper": "after_forest_deep_discovery",
    "Tala - Market Cook": "after_market_established",
    "Tessa - Desert Widow": "after_desert_shrine_visit",
    "Thalma - The Desert Listener": "after_resonance_chamber_enter",
    "Thoran - Mask-Maker": "after_market_established",
    "Tovren the Cartwright": "after_trade_route_inspection"
}

# Stat reward mapping by theme
STAT_REWARDS_BY_THEME = {
    "Memory distortion": "memory:+0.1,presence:+0.1",
    "Boundaries": "authority:+0.1,clarity:+0.1",
    "Loss, grief, betrayal": "empathy:+0.2,memory:+0.1",
    "Family, ancestry": "memory:+0.2,presence:+0.1",
    "Community, restoration": "trust:+0.2,empathy:+0.1",
    "Touch, silence": "presence:+0.2,empathy:+0.1",
    "Play, reunion": "empathy:+0.1,trust:+0.1,memory:+0.1",
    "Fear, the fracture": "empathy:+0.1,presence:+0.1",
    "Choice, clarity": "authority:+0.1,presence:+0.1"
}

def build_glyph_to_fusion_map() -> Dict[str, Tuple[str, str, str]]:
    """Build a map of all glyphs to their fusion group and relationships."""
    glyph_map = {}
    
    for fusion_id, data in FUSION_ARCHETYPES.items():
        for glyph in data["glyphs"]:
            # Extract fusion type (triglyph, octoglyph, etc.)
            if fusion_id.startswith("hexaglyph"):
                fusion_type = "hexaglyph"
            else:
                fusion_type = fusion_id.replace("_silence", "").replace("_collapse", "")
            
            glyph_map[glyph] = {
                "fusion_group": fusion_type,
                "boss_gate": data["boss"],
                "required_glyphs": ",".join(data["glyphs"]),
                "moral_choice": data["moral_choice"],
                "remnants_effects": data["remnants_effects"],
                "semantic_tags": data["semantic_tags"],
                "fusion_chamber": data["chamber"],
                "fusion_receiver": data["receiver"]
            }
    
    return glyph_map

def determine_stat_rewards(theme: str, category: str) -> str:
    """Determine stat rewards based on theme and category."""
    # Check theme first
    for theme_key, rewards in STAT_REWARDS_BY_THEME.items():
        if theme_key.lower() in theme.lower():
            return rewards
    
    # Fall back to category
    return REMNANTS_BY_CATEGORY.get(category, "empathy:+0.1")

def expand_glyph_organizer():
    """Expand Glyph_Organizer.csv with 16 new metadata columns."""
    
    input_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Organizer.csv")
    output_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Organizer_Expanded.csv")
    
    # Build fusion mapping
    fusion_map = build_glyph_to_fusion_map()
    
    # Read existing CSV
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # New columns to add
    new_columns = [
        "glyph_name",
        "npc_source", 
        "unlock_condition",
        "required_glyphs",
        "required_items",
        "required_stats",
        "stat_rewards",
        "flags_required",
        "flags_set",
        "boss_gate",
        "fusion_group",
        "moral_choice",
        "remnants_effects",
        "semantic_tags"
    ]
    
    # Build header with all columns
    original_columns = list(rows[0].keys()) if rows else []
    all_columns = original_columns + new_columns
    
    # Expand each row
    expanded_rows = []
    for row in rows:
        glyph_name = row.get("Glyph", "")
        category = row.get("Category", "")
        theme = row.get("Theme", "")
        npc_giver = row.get("NPC Giver", "")
        
        # Create expanded row starting with original data
        expanded_row = dict(row)
        
        # Add new columns
        expanded_row["glyph_name"] = glyph_name
        expanded_row["npc_source"] = npc_giver
        expanded_row["unlock_condition"] = NPC_UNLOCK_CONDITIONS.get(npc_giver, "")
        
        # Check if this is a fusion glyph
        fusion_data = fusion_map.get(glyph_name)
        if fusion_data:
            expanded_row["required_glyphs"] = fusion_data["required_glyphs"]
            expanded_row["boss_gate"] = fusion_data["boss_gate"]
            expanded_row["fusion_group"] = fusion_data["fusion_group"]
            expanded_row["moral_choice"] = fusion_data["moral_choice"]
            expanded_row["remnants_effects"] = fusion_data["remnants_effects"]
            expanded_row["semantic_tags"] = fusion_data["semantic_tags"]
        else:
            expanded_row["required_glyphs"] = ""
            expanded_row["boss_gate"] = ""
            expanded_row["fusion_group"] = ""
            expanded_row["moral_choice"] = ""
            expanded_row["remnants_effects"] = REMNANTS_BY_CATEGORY.get(category, "empathy:+0.1")
            expanded_row["semantic_tags"] = SEMANTIC_TAGS_BY_CATEGORY.get(category, "presence")
        
        # Set required_items (common progression gates)
        if "Sorrow" in glyph_name or "Remembrance" in glyph_name:
            expanded_row["required_items"] = "tome_mustard_seed"
        else:
            expanded_row["required_items"] = ""
        
        # Set required_stats
        expanded_row["required_stats"] = ""
        
        # Set stat_rewards
        expanded_row["stat_rewards"] = determine_stat_rewards(theme, category)
        
        # Set flags
        expanded_row["flags_required"] = ""
        expanded_row["flags_set"] = f"acquired_{glyph_name.lower().replace(' ', '_').replace('of_', '')}"
        
        expanded_rows.append(expanded_row)
    
    # Write expanded CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_columns)
        writer.writeheader()
        writer.writerows(expanded_rows)
    
    print(f"✓ Expanded CSV created: {output_path}")
    print(f"  - Original columns: {len(original_columns)}")
    print(f"  - New columns: {len(new_columns)}")
    print(f"  - Total columns: {len(all_columns)}")
    print(f"  - Total rows: {len(expanded_rows)}")
    
    return output_path, expanded_rows, all_columns

def generate_validation_report(rows: List[Dict], columns: List[str]) -> str:
    """Generate a validation report showing gaps in metadata."""
    
    report_lines = [
        "=" * 80,
        "GLYPH ORGANIZER METADATA EXPANSION - VALIDATION REPORT",
        "=" * 80,
        ""
    ]
    
    # Count metadata coverage
    missing_npc_source = [r["Glyph"] for r in rows if not r.get("npc_source")]
    missing_unlock = [r["Glyph"] for r in rows if not r.get("unlock_condition")]
    missing_semantic = [r["Glyph"] for r in rows if not r.get("semantic_tags")]
    fusion_glyphs = [r["Glyph"] for r in rows if r.get("fusion_group")]
    
    report_lines.extend([
        f"METADATA COVERAGE SUMMARY",
        f"-" * 80,
        f"Total glyphs: {len(rows)}",
        f"Glyphs with NPC source: {len(rows) - len(missing_npc_source)} ({100*(len(rows)-len(missing_npc_source))//len(rows)}%)",
        f"Glyphs with unlock condition: {len(rows) - len(missing_unlock)} ({100*(len(rows)-len(missing_unlock))//len(rows)}%)",
        f"Glyphs with semantic tags: {len(rows) - len(missing_semantic)} ({100*(len(rows)-len(missing_semantic))//len(rows)}%)",
        f"Fusion group glyphs: {len(fusion_glyphs)}",
        "",
        f"FUSION GROUP BREAKDOWN",
        f"-" * 80,
    ])
    
    fusion_groups = {}
    for row in rows:
        if row.get("fusion_group"):
            fg = row["fusion_group"]
            if fg not in fusion_groups:
                fusion_groups[fg] = []
            fusion_groups[fg].append(row["Glyph"])
    
    for fg in sorted(fusion_groups.keys()):
        glyphs = fusion_groups[fg]
        report_lines.append(f"{fg.upper()}: {len(glyphs)} glyphs")
        for glyph in sorted(glyphs)[:5]:  # Show first 5
            report_lines.append(f"  - {glyph}")
        if len(glyphs) > 5:
            report_lines.append(f"  ... and {len(glyphs)-5} more")
        report_lines.append("")
    
    report_lines.extend([
        f"MISSING METADATA FLAGS",
        f"-" * 80,
        f"Glyphs missing NPC source ({len(missing_npc_source)}):",
    ])
    
    for glyph in sorted(missing_npc_source)[:10]:
        report_lines.append(f"  - {glyph}")
    if len(missing_npc_source) > 10:
        report_lines.append(f"  ... and {len(missing_npc_source)-10} more")
    
    report_lines.extend([
        "",
        f"Glyphs missing unlock condition ({len(missing_unlock)}):",
    ])
    
    for glyph in sorted(missing_unlock)[:10]:
        report_lines.append(f"  - {glyph}")
    if len(missing_unlock) > 10:
        report_lines.append(f"  ... and {len(missing_unlock)-10} more")
    
    report_lines.extend([
        "",
        "=" * 80,
        "NEXT STEPS:",
        "1. Review fusion_group assignments for accuracy",
        "2. Verify boss_gate mappings match chamber locations",
        "3. Populate required_items and required_stats for progression gates",
        "4. Verify semantic_tags align with emotional OS categories",
        "5. Test stat_rewards balance (current: +0.1 to +0.3 per glyph)",
        "=" * 80,
    ])
    
    return "\n".join(report_lines)

if __name__ == "__main__":
    print("Starting Glyph Organizer expansion...")
    output_path, rows, columns = expand_glyph_organizer()
    
    report = generate_validation_report(rows, columns)
    print("\n" + report)
    
    # Save report
    report_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Expansion_Report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Validation report saved: {report_path}")
