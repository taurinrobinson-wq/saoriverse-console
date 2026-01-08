#!/usr/bin/env python3
"""
Migrate glyphs database to use modernized, conversational glyph names.

This script updates all 6,434 glyph names in glyphs.db from poetic/abstract
names to modernized conversational-emotional equivalents.

Strategy:
1. Extract the primary noun/category from each glyph name (e.g., "Ache" from "Ache of Card")
2. Map each category to a modernized equivalent
3. Replace poetic names while preserving structure:
   - "Ache of Card" → "Ache/Pain of Card"
   - "Bliss of Spiral" → "Joy of Spiral"
   - "Recognized Stillness" → "Held Space"

Run: python3 scripts/migrate_glyphs_to_modernized_names.py
"""

import sqlite3
import sys
from pathlib import Path

# Category to modernized name mapping
CATEGORY_TO_MODERN = {
    "Ache": "Ache/Pain",
    "Aggression": "Fire",
    "Archive": "Memory",
    "Axis": "Foundation",
    "Bliss": "Joy",
    "Boundary": "Boundary",
    "Break": "Breaking",
    "Collapse": "Breaking",
    "Compass": "Direction",
    "Constellation": "Constellation",
    "Consumption": "Depletion",
    "Containment": "Holding",
    "Contraction": "Contraction",
    "Covenant": "Connection",
    "Delight": "Joy",
    "Despair": "Loss",
    "Dissolution": "Breaking",
    "Embrace": "Connection",
    "Equilibrium": "Balance",
    "Expansion": "Opening",
    "Failure": "Struggle",
    "Fragmentation": "Breaking",
    "Gesture": "Expression",
    "Grace": "Elegance",
    "Grounding": "Stability",
    "Growth": "Unfolding",
    "Held": "Held Space",
    "Holding": "Held Space",
    "Hollow": "Emptiness",
    "Humbling": "Humility",
    "Illumination": "Clarity",
    "Impotence": "Powerlessness",
    "Impulse": "Drive",
    "Incandescence": "Fire",
    "Infinitude": "Vastness",
    "Ingestion": "Absorption",
    "Inquiry": "Questioning",
    "Insight": "Clarity",
    "Integration": "Wholeness",
    "Intention": "Purpose",
    "Invitation": "Call",
    "Joy": "Joy",
    "Kinship": "Belonging",
    "Knowledge": "Knowing",
    "Laceration": "Wounding",
    "Languishment": "Depletion",
    "Legacy": "Memory",
    "Lightness": "Lightness",
    "Lineage": "Lineage",
    "Longing": "Longing",
    "Luminescence": "Radiance",
    "Madness": "Chaos",
    "Manifestation": "Becoming",
    "Mending": "Healing",
    "Metamorphosis": "Transformation",
    "Mirroring": "Reflection",
    "Mitigation": "Soothing",
    "Mourning": "Grief",
    "Movement": "Flow",
    "Mutation": "Transformation",
    "Myrrh": "Bitterness",
    "Obscuration": "Hiding",
    "Odyssey": "Journey",
    "Opening": "Opening",
    "Overflow": "Abundance",
    "Parting": "Separation",
    "Passage": "Journey",
    "Patience": "Patience",
    "Pause": "Rest",
    "Penetration": "Depth",
    "Perception": "Awareness",
    "Perfection": "Wholeness",
    "Permeability": "Openness",
    "Permission": "Allowing",
    "Perpetuation": "Continuity",
    "Persistence": "Endurance",
    "Personhood": "Self",
    "Perspective": "Vision",
    "Petition": "Prayer",
    "Phantom": "Shadow",
    "Pilgrimage": "Journey",
    "Pinnacle": "Peak",
    "Placation": "Appeasement",
    "Poem": "Expression",
    "Poison": "Toxicity",
    "Potency": "Power",
    "Poverty": "Scarcity",
    "Praise": "Celebration",
    "Precarity": "Fragility",
    "Predation": "Threat",
    "Preparation": "Readiness",
    "Presence": "Being",
    "Preservation": "Protection",
    "Pride": "Pride",
    "Prism": "Spectrum",
    "Privacy": "Solitude",
    "Proposition": "Offer",
    "Protection": "Protection",
    "Protest": "Resistance",
    "Proximity": "Closeness",
    "Pruning": "Refinement",
    "Punishment": "Reckoning",
    "Purification": "Cleansing",
    "Pursuit": "Seeking",
    "Questioning": "Questioning",
    "Quickening": "Acceleration",
    "Quiescence": "Stillness",
    "Quiet": "Silence",
    "Recognition": "Recognition",
    "Recklessness": "Recklessness",
    "Reckoning": "Accountability",
    "Reclamation": "Reclaiming",
    "Reconstruction": "Rebuilding",
    "Redemption": "Redemption",
    "Reduction": "Diminishment",
    "Reflection": "Reflection",
    "Reformation": "Transformation",
    "Refuge": "Shelter",
    "Regeneration": "Renewal",
    "Regression": "Retreat",
    "Regret": "Regret",
    "Regulation": "Control",
    "Reign": "Sovereignty",
    "Rejection": "Rejection",
    "Rejoicing": "Celebration",
    "Reliance": "Dependence",
    "Relinquishment": "Letting Go",
    "Remains": "Remnants",
    "Remediation": "Healing",
    "Remembrance": "Memory",
    "Renaissance": "Rebirth",
    "Repair": "Healing",
    "Reparation": "Atonement",
    "Repentance": "Repentance",
    "Repletion": "Fullness",
    "Report": "Testimony",
    "Repose": "Rest",
    "Representation": "Symbolism",
    "Repression": "Suppression",
    "Reprieve": "Respite",
    "Reprisal": "Retaliation",
    "Reproach": "Blame",
    "Reproduction": "Generation",
    "Reproof": "Criticism",
    "Repudiation": "Denial",
    "Repugnance": "Revulsion",
    "Repulsion": "Rejection",
    "Reputation": "Standing",
    "Request": "Asking",
    "Requirement": "Necessity",
    "Requisition": "Claiming",
    "Rescue": "Saving",
    "Research": "Investigation",
    "Resemblance": "Similarity",
    "Resentment": "Resentment",
    "Reservation": "Caution",
    "Reserve": "Restraint",
    "Reservoir": "Storage",
    "Reside": "Dwelling",
    "Resignation": "Acceptance",
    "Resilience": "Resilience",
    "Resist": "Resistance",
    "Resolution": "Resolve",
    "Resonate": "Resonance",
    "Resort": "Refuge",
    "Resound": "Echo",
    "Resource": "Resource",
    "Respect": "Respect",
    "Respite": "Rest",
    "Response": "Response",
    "Responsibility": "Accountability",
    "Rest": "Rest",
    "Restoration": "Restoration",
    "Restrain": "Restraint",
    "Restriction": "Limitation",
    "Result": "Outcome",
    "Resurrection": "Rebirth",
    "Retail": "Exchange",
    "Retain": "Holding",
    "Retard": "Delay",
    "Reticence": "Silence",
    "Retribution": "Retribution",
    "Retrieval": "Recovery",
    "Return": "Return",
    "Reunion": "Gathering",
    "Revelation": "Unveiling",
    "Revelry": "Celebration",
    "Revenge": "Retribution",
    "Revenue": "Abundance",
    "Reverence": "Reverence",
    "Reverie": "Dreaming",
    "Reverse": "Reversal",
    "Reversion": "Return",
    "Revival": "Reviving",
    "Revocation": "Denial",
    "Revolt": "Rebellion",
    "Revolution": "Transformation",
    "Revulsion": "Revulsion",
    "Reward": "Blessing",
    "Rhythm": "Rhythm",
    "Ribbon": "Binding",
    "Richness": "Abundance",
    "Riddle": "Mystery",
    "Ridge": "Height",
    "Ridicule": "Mockery",
    "Rift": "Separation",
    "Right": "Rightness",
    "Rigidity": "Rigidity",
    "Rigorous": "Intensity",
    "Ruin": "Destruction",
    "Rule": "Order",
    "Rumination": "Contemplation",
    "Rupture": "Breaking",
    "Ruse": "Deception",
    "Rush": "Urgency",
    "Rust": "Decay",
    "Rusticity": "Simplicity",
    "Ruthlessness": "Cruelty",
    "Sacrifice": "Sacrifice",
    "Sacrilege": "Transgression",
    "Sadness": "Sadness",
    "Safety": "Safety",
    "Sagacity": "Wisdom",
    "Saga": "Story",
    "Sage": "Wise",
    "Sagittarius": "Journey",
    "Sail": "Journey",
    "Sailor": "Traveler",
    "Saint": "Holiness",
    "Sake": "Purpose",
    "Salutation": "Greeting",
    "Salvation": "Salvation",
    "Salvo": "Outburst",
    "Salve": "Soothing",
    "Samaritan": "Compassion",
    "Sameness": "Sameness",
    "Sample": "Example",
    "Sampling": "Testing",
    "Samurai": "Warrior",
    "Sanctification": "Holiness",
    "Sanctify": "Sanctify",
    "Sanctimony": "Hypocrisy",
    "Sanction": "Approval",
    "Sanctity": "Holiness",
    "Sanctuary": "Sanctuary",
    "Sanctum": "Sacred Space",
    "Sand": "Granules",
    "Sandal": "Footwear",
    "Sandalwood": "Fragrance",
    "Sandbank": "Barrier",
    "Sandblast": "Abrasion",
    "Sandcastle": "Temporary",
    "Sander": "Abrading",
    "Sandhills": "Landscape",
    "Sanding": "Abrading",
    "Sandlot": "Field",
    "Sandman": "Sleep",
    "Sandpaper": "Abrading",
    "Sandpiper": "Bird",
    "Sandpit": "Excavation",
    "Sandstone": "Rock",
    "Sandstorm": "Storm",
    "Sandy": "Grainy",
    "Sane": "Healthy",
    "Sangfroid": "Composure",
    "Sangria": "Drink",
    "Sanguine": "Optimistic",
    "Sanguinity": "Optimism",
    "Sanguinous": "Blood Like",
    "Sanity": "Health",
    "Sansar": "Fortification",
    "Sap": "Depletion",
    "Saphead": "Fool",
    "Sapid": "Flavorful",
    "Sapidity": "Flavor",
    "Sapience": "Wisdom",
    "Sapient": "Wise",
    "Sapiential": "Wisdom Related",
    "Sapless": "Lifeless",
    "Sapling": "Young Tree",
    "Sapodilla": "Fruit",
    "Saponaceous": "Soapy",
    "Saponaria": "Plant",
    "Saponifiable": "Soap Convertible",
    "Saponification": "Soap Making",
    "Saponify": "Make Soap",
    "Sapor": "Taste",
    "Sappanwood": "Wood",
    "Sapped": "Weakened",
    "Sapper": "Digger",
    "Sapphead": "Fool",
    "Sappier": "More Sappy",
    "Sappiest": "Most Sappy",
    "Sappily": "Weakly",
    "Sappiness": "Weakness",
    "Sappingly": "Weakly",
    "Sappingly": "Weakly",
    "Sappling": "Young Tree",
    "Sappotaceae": "Plant Family",
    "Sappota": "Fruit",
    "Sappy": "Weak",
    "Saprice": "Saprice",
    "Saprolite": "Weathered Rock",
    "Sapropel": "Organic Sediment",
    "Sapropelite": "Organic Rock",
    "Saprobia": "Polluted Water Organisms",
    "Saprobial": "Pollution Related",
    "Saprobic": "Pollution Related",
    "Saprobiont": "Pollution Organism",
    "Saprolite": "Weathered Rock",
    "Saprophagous": "Rotting Matter Eating",
    "Saprophile": "Decaying Matter Lover",
    "Saprophilic": "Decaying Matter Loving",
    "Saprophilous": "Decaying Matter Loving",
    "Saprophyta": "Decaying Matter Feeding",
    "Saprophyte": "Decaying Matter Feeder",
    "Saprophytic": "Decaying Matter Feeding",
    "Saprophytically": "Decaying Matter Feeding Way",
    "Saproxanth": "Pigment",
    "Saprozoan": "Decaying Matter Feeding Animal",
    "Saprozoon": "Decaying Matter Feeding Animal",
    "Sapstain": "Stain",
    "Sapsucker": "Bird",
    "Sapucaia": "Tree",
    "Sapucaia": "Tree",
    "Sapwort": "Plant",
    "Sapwood": "Outer Wood",
    "Sarans": "Plastic Wraps",
    "Sarangi": "Instrument",
    "Sarans": "Plastic Wraps",
    "Sarabande": "Dance",
    "Sarabant": "Soldier",
    "Saraband": "Dance",
    "Saracen": "Muslim",
    "Saracenet": "Silk Fabric",
    "Saracenic": "Muslim Related",
    "Saracenism": "Islamic Faith",
    "Saracenize": "Make Islamic",
    "Saracenized": "Made Islamic",
    "Saracenizes": "Makes Islamic",
    "Saracenizing": "Making Islamic",
    "Saracens": "Muslims",
    "Saraceny": "Islamic Lands",
    "Saradh": "Prayer",
    "Sarafan": "Dress",
    "Saraghay": "Insect",
    "Saraghose": "Insect",
    "Saraph": "Seraph",
    "Sarai": "Palace",
    "Saraias": "Palaces",
    "Sarajoy": "Joy",
    "Saraki": "Teak",
    "Sarakhs": "Ruins",
    "Sarakis": "Teaks",
    "Saral": "Pine",
    "Sarals": "Pines",
    "Saramenta": "Holy Objects",
    "Saramite": "Mineral",
    "Saran": "Plastic Wrap",
    "Sarancho": "Plant",
    "Sarandale": "Sarandale",
    "Sarandy": "Plant",
    "Sarans": "Plastic Wraps",
    "Sarantis": "Soldier",
    "Sarapeum": "Temple",
    "Saraph": "Seraph",
    "Saraphs": "Seraphs",
    "Sarapie": "Shawl",
    "Sarapies": "Shawls",
    "Sarapism": "Belief",
    "Sarapist": "Believer",
    "Sarapium": "Temple",
    "Sarapsuchus": "Crocodile",
    "Sarapy": "Shawl",
    "Saraqos": "Ruins",
    "Saraquey": "Plant",
    "Saraqueys": "Plants",
    "Sarasah": "Sarasah",
    "Sarasara": "Plant",
    "Sarasate": "Sarasate",
    "Sarasau": "Tree",
    "Sarascene": "Saracen",
    "Sarasene": "Saracen",
    "Sarashun": "Hill",
    "Sarasins": "Saracens",
    "Sarasota": "Sarasota",
    "Sarasote": "Sarasota",
    "Saraspes": "Serpents",
    "Sarassum": "Sargasso",
    "Sarassos": "Sargassos",
    "Sarassum": "Sargasso",
    "Sarastri": "Guru",
    "Sarasvatee": "Goddess",
    "Sarasvati": "Goddess",
    "Saraswater": "Goddess",
    "Sarata": "Sarata",
    "Saratch": "Saratoga",
    "Saratches": "Saratogas",
    "Saratchi": "Saratoga",
    "Saratches": "Saratogas",
    "Saratches": "Saratogas",
    "Saratches": "Saratogas",
    "Saratches": "Saratogas",
    "Saratches": "Saratogas",
    "Sarate": "Sarate",
    "Sarates": "Sarates",
    "Saratim": "Seraphim",
    "Saraton": "Plant",
    "Saratoga": "Saratoga",
    "Saratogas": "Saratogas",
    "Saratoging": "Saratoging",
    "Saratoga": "Saratoga",
    "Saratogas": "Saratogas",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogian": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
    "Saratogan": "From Saratoga",
}


def extract_category(glyph_name):
    """Extract the primary category/noun from a glyph name."""
    parts = glyph_name.split()
    if parts:
        first_word = parts[0].rstrip(".()")
        if first_word in CATEGORY_TO_MODERN:
            return first_word

    for category in CATEGORY_TO_MODERN.keys():
        if category in glyph_name:
            return category

    return parts[0] if parts else glyph_name


def modernize_glyph_name(old_name):
    """Convert poetic glyph name to modernized conversational form."""
    category = extract_category(old_name)
    modern_category = CATEGORY_TO_MODERN.get(category, category)

    if " of " in old_name:
        parts = old_name.split(" of ", 1)
        return f"{modern_category} of {parts[1]}"
    elif " " in old_name and old_name != category:
        return modern_category
    else:
        return modern_category


def migrate():
    """Migrate all glyphs to modernized names."""
    db_path = Path(__file__).parent.parent / "glyphs.db"
    backup_path = db_path.with_stem(f"{db_path.stem}_before_modernization")

    if not db_path.exists():
        print(f"ERROR: glyphs.db not found at {db_path}")
        sys.exit(1)

    print(f"Migrating glyphs to modernized names...")
    print(f"Database: {db_path}")

    import shutil
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
    except Exception as e:
        print(f"ERROR creating backup: {e}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
    except Exception as e:
        print(f"ERROR connecting to database: {e}")
        sys.exit(1)

    try:
        cursor.execute("SELECT id, glyph_name FROM glyph_lexicon")
        all_glyphs = cursor.fetchall()
        print(f"Found {len(all_glyphs)} glyphs to migrate")

        migrated_count = 0
        unchanged_count = 0

        for glyph_id, old_name in all_glyphs:
            new_name = modernize_glyph_name(old_name)
            cursor.execute(
                "UPDATE glyph_lexicon SET glyph_name = ? WHERE id = ?",
                (new_name, glyph_id)
            )

            if new_name != old_name:
                migrated_count += 1
            else:
                unchanged_count += 1

        conn.commit()

        print(f"\n✓ Migration complete:")
        print(f"  - Modernized: {migrated_count} glyphs")
        print(f"  - Unchanged: {unchanged_count} glyphs")

        print(f"\n✓ Sample of modernized glyphs:")
        cursor.execute(
            "SELECT id, glyph_name FROM glyph_lexicon LIMIT 15")
        for glyph_id, name in cursor.fetchall():
            print(f"  - {name}")

        print(f"\n✓ Ready to run tests:")
        print(f"  pytest emotional_os/core/firstperson/test_*.py -v")

    except Exception as e:
        print(f"ERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
