#!/usr/bin/env python3
"""
Add skill metadata to Glyph_Organizer_Expanded.csv and create Skill_Registry.json
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

# GLYPH TO SKILL MAPPING
# Maps each glyph to the skill it teaches and any prerequisite skills
GLYPH_SKILL_MAP = {
    # Collapse Path - Discernment Skills
    "Glyph of Mirage Echo": {
        "skill_taught": "illusion_discernment",
        "skill_required": "",
        "description": "Seeing through self-deception and false patterns"
    },
    "Glyph of Fractured Memory": {
        "skill_taught": "distortion_recognition",
        "skill_required": "",
        "description": "Understanding how information becomes corrupted"
    },
    "Glyph of Shattered Corridor": {
        "skill_taught": "collapse_navigation",
        "skill_required": "illusion_discernment",
        "description": "Moving through unstable, fracturing systems"
    },
    "Glyph of Fractured Oath": {
        "skill_taught": "trauma_recognition",
        "skill_required": "",
        "description": "Recognizing broken promises and systemic fracture"
    },
    "Glyph of Fractured Rumor": {
        "skill_taught": "truth_discernment",
        "skill_required": "illusion_discernment",
        "description": "Discerning truth from distorted information"
    },
    "Glyph of Hollow Pact": {
        "skill_taught": "false_covenant_recognition",
        "skill_required": "",
        "description": "Identifying covenant without substance"
    },
    "Glyph of Cloaked Fracture": {
        "skill_taught": "deception_detection",
        "skill_required": "illusion_discernment",
        "description": "Recognizing orchestrated collapse and manipulation"
    },
    
    # Legacy Path - Continuity/Memory Skills
    "Glyph of Ancestral Record": {
        "skill_taught": "lineage_interpretation",
        "skill_required": "",
        "description": "Reading and understanding family history and records"
    },
    "Glyph of Sand Memories": {
        "skill_taught": "emotional_data_processing",
        "skill_required": "lineage_interpretation",
        "description": "Understanding that data and memory carry emotional weight"
    },
    "Glyph of Emotional Inheritance": {
        "skill_taught": "ritual_participation",
        "skill_required": "emotional_data_processing",
        "description": "Engaging in rituals that transmit tradition and connection"
    },
    "Glyph of Echoed Breath": {
        "skill_taught": "ancestral_communion",
        "skill_required": "emotional_data_processing",
        "description": "Connecting with ancestors through breath and presence"
    },
    "Glyph of Returning Song": {
        "skill_taught": "generational_voice",
        "skill_required": "ritual_participation",
        "description": "Speaking the voice of multiple generations"
    },
    "Glyph of Hopeful Transmission": {
        "skill_taught": "legacy_persistence",
        "skill_required": "emotional_data_processing",
        "description": "Maintaining hope and transmission despite loss"
    },
    
    # Sovereignty Path - Boundary/Choice Skills
    "Glyph of Measured Step": {
        "skill_taught": "measured_movement",
        "skill_required": "",
        "description": "Moving with intention through consequence"
    },
    "Glyph of Boundary Stone": {
        "skill_taught": "boundary_setting",
        "skill_required": "measured_movement",
        "description": "Defining and holding safe space amid chaos"
    },
    "Glyph of Reckless Trial": {
        "skill_taught": "risk_acceptance",
        "skill_required": "",
        "description": "Accepting calculated risk as a form of sovereignty"
    },
    "Glyph of Iron Boundary": {
        "skill_taught": "enforced_boundaries",
        "skill_required": "boundary_setting",
        "description": "Maintaining limits through weary vigilance"
    },
    "Glyph of Interruptive Restraint": {
        "skill_taught": "impulse_regulation",
        "skill_required": "measured_movement",
        "description": "Pausing destructive impulses and holding rage without releasing it"
    },
    "Glyph of Held Ache": {
        "skill_taught": "co_witnessing",
        "skill_required": "",
        "description": "Holding space for others' pain without fixing it"
    },
    "Glyph of Venomous Choice": {
        "skill_taught": "discernment_in_betrayal",
        "skill_required": "deception_detection",
        "description": "Choosing wisely when all paths carry risk"
    },
    
    # Presence Path - Witnessing Skills
    "Glyph of Tender Witness": {
        "skill_taught": "silent_witnessing",
        "skill_required": "",
        "description": "Being present for others' pain through attention and stillness"
    },
    "Glyph of Echo Communion": {
        "skill_taught": "connection_holding",
        "skill_required": "silent_witnessing",
        "description": "Touching the edge of what's gone and honoring its memory"
    },
    "Glyph of Steadfast Witness": {
        "skill_taught": "emotional_anchoring",
        "skill_required": "silent_witnessing",
        "description": "Anchoring others through presence and sustained attention"
    },
    "Glyph of Listening Silence": {
        "skill_taught": "receptive_presence",
        "skill_required": "silent_witnessing",
        "description": "Silence as observation stronger than speech"
    },
    "Glyph of Quiet Bloom": {
        "skill_taught": "healing_presence",
        "skill_required": "silent_witnessing",
        "description": "Care given and received through quiet presence"
    },
    "Glyph of Fragrant Silence": {
        "skill_taught": "subtle_healing",
        "skill_required": "silent_witnessing",
        "description": "Healing carried in quiet fragrance and presence"
    },
    "Glyph of Sensory Oblivion": {
        "skill_taught": "absence_witnessing",
        "skill_required": "silent_witnessing",
        "description": "Witnessing emptiness without trying to fill it"
    },
    "Glyph of Serpent's Silence": {
        "skill_taught": "discerning_silence",
        "skill_required": "silent_witnessing",
        "description": "Recognizing when silence becomes witness to manipulation"
    },
    "Glyph of Quiet Return": {
        "skill_taught": "presence_as_return",
        "skill_required": "silent_witnessing",
        "description": "Presence that brings people back to themselves"
    },
    
    # Trust Path - Interdependence Skills
    "Glyph of Covenant Flame": {
        "skill_taught": "collective_tending",
        "skill_required": "",
        "description": "Collectively maintaining the bonds that keep community alive"
    },
    "Glyph of Shared Survival": {
        "skill_taught": "interdependence_practice",
        "skill_required": "collective_tending",
        "description": "Relying on others and being relied upon"
    },
    "Glyph of Mutual Passage": {
        "skill_taught": "wordless_coordination",
        "skill_required": "collective_tending",
        "description": "Trust built through reliable, wordless action"
    },
    "Glyph of Shared Burden": {
        "skill_taught": "collaborative_labor",
        "skill_required": "interdependence_practice",
        "description": "Bearing weight together across fractured bridges"
    },
    "Glyph of Binding Cloth": {
        "skill_taught": "thread_binding",
        "skill_required": "collaborative_labor",
        "description": "Weaving threads of lives together through care"
    },
    "Glyph of Weary Justice": {
        "skill_taught": "ethical_boundaries",
        "skill_required": "collective_tending",
        "description": "Maintaining justice through weary, persistent care"
    },
    "Glyph of Whispered Pact": {
        "skill_taught": "sacred_speech",
        "skill_required": "wordless_coordination",
        "description": "Holding secrets and words with ceremonial care"
    },
    "Glyph of Broken Promise": {
        "skill_taught": "trust_repair",
        "skill_required": "sacred_speech",
        "description": "Healing fractured trust through witness and accountability"
    },
    "Glyph of Serpent's Tongue": {
        "skill_taught": "discerning_speech",
        "skill_required": "sacred_speech",
        "description": "Knowing when speech heals and when it poisons"
    },
    "Glyph of Thieves' Honor": {
        "skill_taught": "loyalty_in_shadow",
        "skill_required": "wordless_coordination",
        "description": "Maintaining loyalty that transcends normal bonds"
    },
    
    # Joy Path - Creative/Communal Skills
    "Glyph of Shared Feast": {
        "skill_taught": "communal_celebration",
        "skill_required": "",
        "description": "Gathering others to break bread and create joy"
    },
    "Glyph of Crafted Wonder": {
        "skill_taught": "beauty_creation",
        "skill_required": "communal_celebration",
        "description": "Making something beautiful from broken materials"
    },
    "Glyph of Arrival": {
        "skill_taught": "joy_witnessing",
        "skill_required": "communal_celebration",
        "description": "Honoring safe return and the relief it brings"
    },
    "Glyph of Trade Celebration": {
        "skill_taught": "exchange_appreciation",
        "skill_required": "communal_celebration",
        "description": "Joy in transaction and needs being met"
    },
    "Glyph of Verdant Reunion": {
        "skill_taught": "growth_witnessing",
        "skill_required": "beauty_creation",
        "description": "Reuniting through growth and shared care"
    },
    "Glyph of Dawn Petals": {
        "skill_taught": "ephemeral_appreciation",
        "skill_required": "joy_witnessing",
        "description": "Appreciating what is fleeting and beautiful"
    },
    "Glyph of Laughter's Balm": {
        "skill_taught": "grief_lightening",
        "skill_required": "communal_celebration",
        "description": "Using laughter and memory to lighten sorrow"
    },
    "Glyph of Hidden Warmth": {
        "skill_taught": "connection_breakthrough",
        "skill_required": "joy_witnessing",
        "description": "Finding connection despite walls and defenses"
    },
    "Glyph of Sky Revelry": {
        "skill_taught": "sacred_celebration",
        "skill_required": "communal_celebration",
        "description": "Celebration as sacred act that restores morale"
    },
    "Glyph of Blooming Path": {
        "skill_taught": "renewal_promise",
        "skill_required": "growth_witnessing",
        "description": "Recognizing renewal and the continuation of life"
    },
    
    # Ache Path - Grief Skills
    "Glyph of Sorrow": {
        "skill_taught": "grief_witnessing",
        "skill_required": "",
        "description": "Witnessing sorrow without trying to fix it"
    },
    "Glyph of Remembrance": {
        "skill_taught": "memory_honoring",
        "skill_required": "grief_witnessing",
        "description": "Honoring those who are gone through memory"
    },
    "Glyph of Legacy": {
        "skill_taught": "loss_transmission",
        "skill_required": "memory_honoring",
        "description": "Staying present with loss and choosing to remain"
    },
    "Glyph of Betrayal Scar": {
        "skill_taught": "survival_resilience",
        "skill_required": "grief_witnessing",
        "description": "Carrying scars as evidence of survival"
    },
    "Glyph of Primal Oblivion": {
        "skill_taught": "raw_mourning",
        "skill_required": "grief_witnessing",
        "description": "Keening and expressing grief without language"
    },
    "Glyph of Broken Vessel": {
        "skill_taught": "fragility_understanding",
        "skill_required": "grief_witnessing",
        "description": "Understanding fragility as prerequisite for love"
    },
    "Glyph of Sewn Ache": {
        "skill_taught": "grief_transformation",
        "skill_required": "memory_honoring",
        "description": "Weaving grief into something stronger"
    },
    "Glyph of Widow's Cry": {
        "skill_taught": "shared_lament",
        "skill_required": "raw_mourning",
        "description": "Transmitting grief into the wind where it dissolves"
    },
    "Glyph of Dislocated Attachment": {
        "skill_taught": "relational_rupture_understanding",
        "skill_required": "grief_witnessing",
        "description": "Understanding families fractured by sudden severance"
    },
    "Glyph of Silent Ache": {
        "skill_taught": "quiet_presence_in_ache",
        "skill_required": "silent_witnessing",
        "description": "Sitting with unspoken pain without words"
    },
    "Glyph of Hidden Ache": {
        "skill_taught": "ache_visibility",
        "skill_required": "grief_witnessing",
        "description": "Bringing hidden grief into light and acceptance"
    },
    "Glyph of Infrasensory Oblivion": {
        "skill_taught": "latent_loss_recognition",
        "skill_required": "grief_witnessing",
        "description": "Recognizing loss that arrives after the event"
    },
    "Glyph of Echoed Longing": {
        "skill_taught": "intergenerational_grief",
        "skill_required": "memory_honoring",
        "description": "Feeling grief across generations"
    },
}

def expand_glyph_csv():
    """Add skill columns to Glyph_Organizer_Expanded.csv"""
    
    input_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Organizer_Expanded.csv")
    output_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Glyph_Organizer_Skills.csv")
    
    # Read CSV
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    
    # Add new columns
    new_columns = list(columns) + ["skill_taught", "skill_required"]
    
    # Populate skills
    for row in rows:
        glyph_name = row.get("glyph_name", "")
        skill_info = GLYPH_SKILL_MAP.get(glyph_name, {
            "skill_taught": "",
            "skill_required": ""
        })
        row["skill_taught"] = skill_info.get("skill_taught", "")
        row["skill_required"] = skill_info.get("skill_required", "")
    
    # Write updated CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_columns)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Expanded CSV created: {output_path}")
    print(f"  - Total glyphs: {len(rows)}")
    print(f"  - New columns: skill_taught, skill_required")
    
    return rows

def create_skill_registry(rows):
    """Create Skill_Registry.json from glyph data"""
    
    # Build skill information from glyph mapping
    skills_data = {}
    skill_categories = defaultdict(list)
    
    for glyph_name, skill_info in GLYPH_SKILL_MAP.items():
        skill_id = skill_info["skill_taught"]
        if not skill_id:
            continue
        
        if skill_id not in skills_data:
            # Determine category based on skill
            if skill_id in ["illusion_discernment", "distortion_recognition", "collapse_navigation", "trauma_recognition", "truth_discernment", "false_covenant_recognition", "deception_detection"]:
                category = "collapse_discernment"
            elif skill_id in ["lineage_interpretation", "emotional_data_processing", "ritual_participation", "ancestral_communion", "generational_voice", "legacy_persistence"]:
                category = "legacy_continuity"
            elif skill_id in ["measured_movement", "boundary_setting", "risk_acceptance", "enforced_boundaries", "impulse_regulation", "co_witnessing", "discernment_in_betrayal"]:
                category = "sovereignty_boundaries"
            elif skill_id in ["silent_witnessing", "connection_holding", "emotional_anchoring", "receptive_presence", "healing_presence", "subtle_healing", "absence_witnessing", "discerning_silence", "presence_as_return"]:
                category = "presence_witnessing"
            elif skill_id in ["collective_tending", "interdependence_practice", "wordless_coordination", "collaborative_labor", "thread_binding", "ethical_boundaries", "sacred_speech", "trust_repair", "discerning_speech", "loyalty_in_shadow"]:
                category = "trust_interdependence"
            elif skill_id in ["communal_celebration", "beauty_creation", "joy_witnessing", "exchange_appreciation", "growth_witnessing", "ephemeral_appreciation", "grief_lightening", "connection_breakthrough", "sacred_celebration", "renewal_promise"]:
                category = "joy_creativity"
            elif skill_id in ["grief_witnessing", "memory_honoring", "loss_transmission", "survival_resilience", "raw_mourning", "fragility_understanding", "grief_transformation", "shared_lament", "relational_rupture_understanding", "quiet_presence_in_ache", "ache_visibility", "latent_loss_recognition", "intergenerational_grief"]:
                category = "ache_grief"
            else:
                category = "other"
            
            skills_data[skill_id] = {
                "skill_id": skill_id,
                "skill_name": skill_info["skill_taught"].replace("_", " ").title(),
                "category": category,
                "description": skill_info["description"],
                "taught_by_glyphs": [],
                "prerequisite_skill": skill_info.get("skill_required", ""),
                "emotional_impact": "",  # To be populated based on category
                "remnants_effects": ""
            }
            skill_categories[category].append(skill_id)
        
        # Add glyph to skill's taught_by list
        skills_data[skill_id]["taught_by_glyphs"].append(glyph_name)
    
    # Add emotional impacts based on category
    EMOTIONAL_IMPACTS = {
        "collapse_discernment": "Clarity through understanding collapse",
        "legacy_continuity": "Connection across time and generations",
        "sovereignty_boundaries": "Agency through defined limits",
        "presence_witnessing": "Healing through witnessed presence",
        "trust_interdependence": "Survival through reliable bonds",
        "joy_creativity": "Resilience through beauty and celebration",
        "ache_grief": "Wisdom through witnessed loss"
    }
    
    for skill_id in skills_data:
        category = skills_data[skill_id]["category"]
        skills_data[skill_id]["emotional_impact"] = EMOTIONAL_IMPACTS.get(category, "")
    
    # Add REMNANTS effects based on category
    REMNANTS_EFFECTS = {
        "collapse_discernment": "memory:+0.1,presence:+0.1",
        "legacy_continuity": "memory:+0.2,authority:+0.1",
        "sovereignty_boundaries": "authority:+0.1,presence:+0.1",
        "presence_witnessing": "presence:+0.2,empathy:+0.1",
        "trust_interdependence": "trust:+0.2,empathy:+0.1",
        "joy_creativity": "empathy:+0.1,trust:+0.1",
        "ache_grief": "empathy:+0.2,need:+0.1"
    }
    
    for skill_id in skills_data:
        category = skills_data[skill_id]["category"]
        skills_data[skill_id]["remnants_effects"] = REMNANTS_EFFECTS.get(category, "empathy:+0.1")
    
    # Build final registry
    registry = {
        "metadata": {
            "version": "1.0",
            "description": "Velinor Skill Registry - Vocational apprenticeship system",
            "total_skills": len(skills_data),
            "categories": len(skill_categories),
            "generation_date": "2026-01-06"
        },
        "skill_categories": {
            "collapse_discernment": {
                "name": "Collapse Discernment",
                "description": "Skills for seeing through illusion, recognizing distortion, and navigating fractured systems",
                "core_theme": "Clarity through understanding what breaks"
            },
            "legacy_continuity": {
                "name": "Legacy & Continuity",
                "description": "Skills for holding memory, honoring lineage, and transmitting what survives",
                "core_theme": "Connection across time"
            },
            "sovereignty_boundaries": {
                "name": "Sovereignty & Boundaries",
                "description": "Skills for defined agency, measured movement, and chosen limits",
                "core_theme": "Agency through intention"
            },
            "presence_witnessing": {
                "name": "Presence & Witnessing",
                "description": "Skills for silent companionship, holding space, and healing presence",
                "core_theme": "Healing through witnessed presence"
            },
            "trust_interdependence": {
                "name": "Trust & Interdependence",
                "description": "Skills for reliable bonds, collaborative labor, and shared survival",
                "core_theme": "Survival through reliable bonds"
            },
            "joy_creativity": {
                "name": "Joy & Creativity",
                "description": "Skills for celebration, beauty-making, and communal resilience",
                "core_theme": "Resilience through joy and creation"
            },
            "ache_grief": {
                "name": "Ache & Grief",
                "description": "Skills for witnessing loss, honoring the dead, and transforming sorrow",
                "core_theme": "Wisdom through witnessed loss"
            }
        },
        "skills": skills_data
    }
    
    # Write registry
    output_path = Path("d:/saoriverse-console/velinor/markdowngameinstructions/Skill_Registry.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Skill Registry created: {output_path}")
    print(f"  - Total skills: {len(skills_data)}")
    print(f"  - Categories: {len(skill_categories)}")
    print(f"  - Skills by category:")
    for category in sorted(skill_categories.keys()):
        print(f"    - {category}: {len(skill_categories[category])} skills")
    
    return registry

if __name__ == "__main__":
    print("Expanding Glyph CSV with skill metadata...\n")
    rows = expand_glyph_csv()
    
    print("\nCreating Skill Registry...\n")
    registry = create_skill_registry(rows)
    
    print(f"\n{'='*80}")
    print(f"SKILL SYSTEM GENERATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nFiles created:")
    print(f"1. Glyph_Organizer_Skills.csv - Glyph data with skill metadata")
    print(f"2. Skill_Registry.json - Complete skill system definition")
    print(f"\nNext steps:")
    print(f"- Review skill prerequisites and dependencies")
    print(f"- Create NPC dialogue banks based on skill requirements")
    print(f"- Implement skill_system.py for runtime skill tracking")
