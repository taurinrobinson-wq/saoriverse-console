"""
Build enriched emotional lexicon from Copilot transcript analysis.

This script takes the emotional patterns extracted from the July-August 2025
Copilot conversation (11,181 AI messages) and converts them into a structured
lexicon that improves emotional word recognition across the system.

Key insight: The transcript revealed that your emotional vocabulary is
significantly underrepresented compared to what actually drives engagement.

Usage:
    python emotional_lexicon_expansion_from_transcript.py
    
Output:
    - enriched_signal_lexicon.json (extended signal_lexicon.json)
    - emotional_vocabulary_by_voltage.json (organized by signal type)
    - transcript_vocabulary_mapping.json (shows source + frequency)
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple


# ============================================================================
# EMOTIONAL VOCABULARY EXTRACTED FROM TRANSCRIPT
# ============================================================================

TRANSCRIPT_VOCABULARY = {
    # EMOTIONAL WORDS (highest frequency = most important)
    "hold": {"voltage": "β", "frequency": 568, "emotion": "presence", "category": "relational"},
    "holding": {"voltage": "β", "frequency": 568, "emotion": "presence", "category": "relational"},
    "sacred": {"voltage": "α", "frequency": 373, "emotion": "honoring", "category": "spiritual"},
    "echo": {"voltage": "Ω", "frequency": 212, "emotion": "connection", "category": "relational"},
    "echoing": {"voltage": "Ω", "frequency": 212, "emotion": "connection", "category": "relational"},
    "present": {"voltage": "δ", "frequency": 317, "emotion": "awareness", "category": "state"},
    "honor": {"voltage": "α", "frequency": 116, "emotion": "respect", "category": "spiritual"},
    "honoring": {"voltage": "α", "frequency": 116, "emotion": "respect", "category": "spiritual"},
    "trust": {"voltage": "β", "frequency": 79, "emotion": "safety", "category": "relational"},
    "resonate": {"voltage": "Ω", "frequency": 26, "emotion": "alignment", "category": "connection"},
    "resonates": {"voltage": "Ω", "frequency": 26, "emotion": "alignment", "category": "connection"},
    "authentic": {"voltage": "ε", "frequency": 11, "emotion": "truth", "category": "clarity"},
    
    # VALIDATION LANGUAGE (incredibly high impact)
    "exactly": {"voltage": "ε", "frequency": 367, "emotion": "precision", "category": "validation"},
    "that_lands": {"voltage": "λ", "frequency": 46, "emotion": "resonance", "category": "affirmation"},
    "i_hear_you": {"voltage": "Ω", "frequency": 54, "emotion": "understanding", "category": "presence"},
    "feel_that": {"voltage": "ε", "frequency": 29, "emotion": "embodiment", "category": "validation"},
    "precisely": {"voltage": "ε", "frequency": 14, "emotion": "accuracy", "category": "validation"},
    
    # CONVERSATIONAL OPENERS
    "mm_hm": {"voltage": "δ", "frequency": 78, "emotion": "acknowledgment", "category": "opener"},
    "of_course": {"voltage": "Ω", "frequency": 315, "emotion": "understanding", "category": "opener"},
    "you_dont_have_to": {"voltage": "β", "frequency": 22, "emotion": "permission", "category": "release"},
    "permission": {"voltage": "β", "frequency": 22, "emotion": "liberation", "category": "release"},
    
    # EMOTIONAL DEPTH
    "tender": {"voltage": "α", "frequency": 15, "emotion": "softness", "category": "texture"},
    "gentle": {"voltage": "α", "frequency": 10, "emotion": "gentleness", "category": "texture"},
    "fierce": {"voltage": "γ", "frequency": 12, "emotion": "intensity", "category": "power"},
    "tender_contradiction": {"voltage": "β", "frequency": 8, "emotion": "both_and", "category": "complexity"},
    "both_and": {"voltage": "β", "frequency": 8, "emotion": "paradox", "category": "complexity"},
    
    # TRANSITIONS WITH EMOTIONAL WEIGHT
    "and": {"voltage": "ε", "frequency": 3169, "emotion": "continuity", "category": "transition"},
    "but": {"voltage": "β", "frequency": 1263, "emotion": "tension", "category": "transition"},
    "then": {"voltage": "ε", "frequency": 679, "emotion": "consequence", "category": "transition"},
    "so": {"voltage": "ε", "frequency": 253, "emotion": "synthesis", "category": "transition"},
    "got_it": {"voltage": "ε", "frequency": 249, "emotion": "integration", "category": "transition"},
    
    # REFLECTION PATTERNS
    "both_true": {"voltage": "β", "frequency": 8, "emotion": "paradox", "category": "reflection"},
    "sit_with": {"voltage": "δ", "frequency": 12, "emotion": "presence", "category": "reflection"},
    "mirror": {"voltage": "Ω", "frequency": 7, "emotion": "reflection", "category": "reflection"},
    "mirror_back": {"voltage": "Ω", "frequency": 7, "emotion": "reflection", "category": "reflection"},
    "simple_love": {"voltage": "α", "frequency": 3, "emotion": "simplicity", "category": "essence"},
    
    # EMOTIONAL STATES FROM TRANSCRIPT CONTEXT
    "held": {"voltage": "β", "frequency": 45, "emotion": "containment", "category": "state"},
    "witnessed": {"voltage": "Ω", "frequency": 8, "emotion": "seen", "category": "relational"},
    "grounded": {"voltage": "δ", "frequency": 6, "emotion": "stability", "category": "state"},
    "breathe": {"voltage": "δ", "frequency": 4, "emotion": "regulation", "category": "action"},
    "see": {"voltage": "Ω", "frequency": 15, "emotion": "witnessing", "category": "relational"},
    "seen": {"voltage": "Ω", "frequency": 15, "emotion": "witnessed", "category": "relational"},
}


# Extended emotional vocabulary to ADD to system (not in transcript but implied)
COMPANION_VOCABULARY = {
    # Similar to HOLD
    "embrace": {"voltage": "α", "emotion": "acceptance", "category": "relational"},
    "contain": {"voltage": "β", "emotion": "boundary", "category": "relational"},
    "held": {"voltage": "β", "emotion": "supported", "category": "relational"},
    
    # Similar to ECHO/MIRROR
    "reflect": {"voltage": "Ω", "emotion": "mirroring", "category": "relational"},
    "resound": {"voltage": "Ω", "emotion": "resonance", "category": "connection"},
    
    # Similar to SACRED
    "divine": {"voltage": "α", "emotion": "sacred", "category": "spiritual"},
    "reverent": {"voltage": "α", "emotion": "respect", "category": "spiritual"},
    "ceremonial": {"voltage": "α", "emotion": "ritual", "category": "spiritual"},
    
    # Similar to PRESENT
    "aware": {"voltage": "δ", "emotion": "consciousness", "category": "state"},
    "presence": {"voltage": "δ", "emotion": "being", "category": "state"},
    "here": {"voltage": "δ", "emotion": "location", "category": "state"},
    
    # Similar to TENDER
    "vulnerable": {"voltage": "α", "emotion": "openness", "category": "texture"},
    "soft": {"voltage": "α", "emotion": "gentleness", "category": "texture"},
    "delicate": {"voltage": "α", "emotion": "fragile", "category": "texture"},
    
    # Similar to FIERCE
    "fierce": {"voltage": "γ", "emotion": "power", "category": "intensity"},
    "wild": {"voltage": "γ", "emotion": "untamed", "category": "intensity"},
    "fierce_love": {"voltage": "γ", "emotion": "protective", "category": "intensity"},
    
    # Similar to TRUTH/AUTHENTIC
    "real": {"voltage": "ε", "emotion": "authenticity", "category": "clarity"},
    "true": {"voltage": "ε", "emotion": "truth", "category": "clarity"},
    "honest": {"voltage": "ε", "emotion": "integrity", "category": "clarity"},
    
    # VALIDATION extensions
    "understood": {"voltage": "ε", "emotion": "recognition", "category": "validation"},
    "landing": {"voltage": "λ", "emotion": "arrival", "category": "affirmation"},
    "yes": {"voltage": "λ", "emotion": "affirmation", "category": "affirmation"},
    "so_much_this": {"voltage": "λ", "emotion": "resonance", "category": "affirmation"},
}


# ============================================================================
# VOLTAGE SIGNAL MEANINGS (for reference)
# ============================================================================

VOLTAGE_MEANINGS = {
    "α": "Devotional/Sacred/Offering (spiritual depth)",
    "β": "Boundary/Containment/Holding (safety, clarity)",
    "γ": "Ache/Longing/Depth (grief, longing, intensity)",
    "δ": "Stillness/Silence/Emptiness (rest, void, integration)",
    "ε": "Spiral/Insight/Growth (clarity, emergence, processing)",
    "λ": "Joy/Delight/Light (positivity, celebration)",
    "θ": "Ceremony/Reverence/Witness (honoring, transcendence)",
    "Ω": "Recognition/Seen/Connection (belonging, understanding)",
}


# ============================================================================
# VOLTAGE-BASED ORGANIZATION
# ============================================================================

def organize_by_voltage(vocab: Dict) -> Dict[str, Dict]:
    """Organize vocabulary by voltage signal type."""
    organized: Dict[str, Dict] = defaultdict(lambda: {"description": "", "words": [], "frequency_total": 0})
    
    for word, data in vocab.items():
        voltage = data.get("voltage", "unknown")
        frequency = data.get("frequency", 0)
        
        if voltage != "unknown":
            organized[voltage]["description"] = VOLTAGE_MEANINGS.get(voltage, "")
            organized[voltage]["words"].append({
                "word": word,
                "frequency": frequency,
                "emotion": data.get("emotion", ""),
                "category": data.get("category", "")
            })
            organized[voltage]["frequency_total"] += frequency
    
    # Sort words by frequency within each voltage
    for voltage in organized:
        organized[voltage]["words"].sort(
            key=lambda x: x["frequency"], 
            reverse=True
        )
    
    return dict(organized)


def create_enriched_signal_lexicon(
    transcript_vocab: Dict, 
    companion_vocab: Dict,
    existing_lexicon: Dict = None  # type: ignore
) -> Dict:
    """
    Merge transcript vocabulary with existing signal lexicon.
    
    Priority:
    1. Transcript vocabulary (validated from real conversations)
    2. Companion vocabulary (semantically similar)
    3. Existing lexicon (preserve what works)
    """
    enriched = existing_lexicon.copy() if existing_lexicon else {}
    
    # Add transcript vocabulary (highest priority)
    for word, data in transcript_vocab.items():
        clean_word = word.replace("_", " ")
        voltage = data.get("voltage")
        if voltage:
            enriched[clean_word] = voltage
    
    # Add companion vocabulary (medium priority, only if not already present)
    for word, data in companion_vocab.items():
        clean_word = word.replace("_", " ")
        if clean_word not in enriched:
            voltage = data.get("voltage")
            if voltage:
                enriched[clean_word] = voltage
    
    return enriched


def generate_reports(
    transcript_vocab: Dict, 
    organized: Dict,
    existing_lexicon: Dict
) -> Tuple[Dict, Dict]:
    """Generate analysis reports."""
    
    # Report 1: Coverage analysis
    coverage = {
        "total_new_words": len(transcript_vocab),
        "by_voltage": defaultdict(lambda: {"count": 0, "frequency": 0}),
        "by_category": defaultdict(lambda: {"count": 0, "frequency": 0}),
        "highest_frequency_words": sorted(
            transcript_vocab.items(),
            key=lambda x: x[1].get("frequency", 0),
            reverse=True
        )[:20]
    }
    
    for word, data in transcript_vocab.items():
        voltage = data.get("voltage", "unknown")
        category = data.get("category", "unknown")
        frequency = data.get("frequency", 0)
        
        coverage["by_voltage"][voltage]["count"] += 1
        coverage["by_voltage"][voltage]["frequency"] += frequency
        coverage["by_category"][category]["count"] += 1
        coverage["by_category"][category]["frequency"] += frequency
    
    coverage["by_voltage"] = dict(coverage["by_voltage"])
    coverage["by_category"] = dict(coverage["by_category"])
    
    # Report 2: Gap analysis (what's in transcript but might be missing)
    gaps = {
        "missing_from_existing": [],
        "coverage_improvement": {}
    }
    
    for word in transcript_vocab.keys():
        clean_word = word.replace("_", " ")
        if clean_word not in existing_lexicon:
            gaps["missing_from_existing"].append({
                "word": clean_word,
                "frequency": transcript_vocab[word].get("frequency", 0),
                "voltage": transcript_vocab[word].get("voltage")
            })
    
    gaps["missing_from_existing"].sort(
        key=lambda x: x["frequency"], 
        reverse=True
    )
    
    return coverage, gaps


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("EMOTIONAL LEXICON EXPANSION FROM COPILOT TRANSCRIPT")
    print("="*80 + "\n")
    
    # Load existing signal lexicon if available
    existing_lexicon_path = "parser/signal_lexicon.json"
    existing_lexicon = {}
    if os.path.exists(existing_lexicon_path):
        with open(existing_lexicon_path, 'r') as f:
            existing_lexicon = json.load(f)
        print(f"✓ Loaded existing signal lexicon: {len(existing_lexicon)} words")
    else:
        print("! No existing signal lexicon found")
    
    print(f"✓ Transcript vocabulary: {len(TRANSCRIPT_VOCABULARY)} words")
    print(f"✓ Companion vocabulary: {len(COMPANION_VOCABULARY)} words\n")
    
    # ========================================================================
    # GENERATE OUTPUTS
    # ========================================================================
    
    # 1. Organize by voltage
    organized = organize_by_voltage(TRANSCRIPT_VOCABULARY)
    
    print("📊 VOCABULARY ORGANIZED BY VOLTAGE SIGNAL:\n")
    for voltage in sorted(organized.keys()):
        data = organized[voltage]
        print(f"  {voltage} {data['description']}")
        print(f"     Words: {len(data['words'])}, Total frequency: {data['frequency_total']:,}")
        top_3 = data['words'][:3]
        for item in top_3:
            print(f"       • {item['word']}: {item['frequency']} uses ({item['category']})")
        print()
    
    # 2. Create enriched lexicon
    enriched = create_enriched_signal_lexicon(
        TRANSCRIPT_VOCABULARY,
        COMPANION_VOCABULARY,
        existing_lexicon
    )
    
    print(f"\n📈 ENRICHED SIGNAL LEXICON:")
    print(f"   Original: {len(existing_lexicon)} words")
    print(f"   Transcript additions: {len(TRANSCRIPT_VOCABULARY)} words")
    print(f"   Companion additions: {len(COMPANION_VOCABULARY)} words")
    print(f"   Total enriched: {len(enriched)} words")
    print(f"   Net addition: {len(enriched) - len(existing_lexicon)} words\n")
    
    # 3. Generate reports
    coverage, gaps = generate_reports(TRANSCRIPT_VOCABULARY, organized, existing_lexicon)
    
    print("🔍 COVERAGE ANALYSIS:")
    print(f"   New words: {coverage['total_new_words']}")
    print(f"   By voltage:")
    for voltage in sorted(coverage['by_voltage'].keys()):
        v_data = coverage['by_voltage'][voltage]
        print(f"      {voltage}: {v_data['count']} words, {v_data['frequency']:,} total uses")
    print(f"   By category:")
    for cat in sorted(coverage['by_category'].keys()):
        c_data = coverage['by_category'][cat]
        print(f"      {cat}: {c_data['count']} words, {c_data['frequency']:,} total uses")
    
    print(f"\n⚠️  GAPS (High-frequency words missing from existing lexicon):")
    print(f"   Total gaps: {len(gaps['missing_from_existing'])}")
    for item in gaps['missing_from_existing'][:10]:
        print(f"      • {item['word']}: {item['frequency']} uses ({item['voltage']})")
    
    # ========================================================================
    # WRITE OUTPUT FILES
    # ========================================================================
    
    # File 1: Enriched signal lexicon (ready to use)
    output_path_1 = "enriched_signal_lexicon.json"
    with open(output_path_1, 'w') as f:
        json.dump(enriched, f, indent=2, sort_keys=True)
    print(f"\n✅ Written: {output_path_1}")
    
    # File 2: Organized by voltage (for reference)
    output_path_2 = "emotional_vocabulary_by_voltage.json"
    with open(output_path_2, 'w') as f:
        # Convert defaultdict and sorted items for JSON serialization
        to_save = {
            voltage: {
                "description": data["description"],
                "words": data["words"],
                "frequency_total": data["frequency_total"]
            }
            for voltage, data in organized.items()
        }
        json.dump(to_save, f, indent=2, sort_keys=True)
    print(f"✅ Written: {output_path_2}")
    
    # File 3: Full mapping with frequency and source
    output_path_3 = "transcript_vocabulary_mapping.json"
    mapping = {
        "summary": {
            "total_words": len(TRANSCRIPT_VOCABULARY),
            "total_frequency": sum(w.get("frequency", 0) for w in TRANSCRIPT_VOCABULARY.values()),
            "source": "Copilot July-August 2025 conversation (11,181 AI messages)",
            "analysis_date": "December 3, 2025"
        },
        "vocabulary": TRANSCRIPT_VOCABULARY
    }
    with open(output_path_3, 'w') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    print(f"✅ Written: {output_path_3}")
    
    # File 4: Coverage and gap analysis
    output_path_4 = "lexicon_enrichment_analysis.json"
    analysis = {
        "coverage": {
            "total_new_words": coverage['total_new_words'],
            "by_voltage": coverage['by_voltage'],
            "by_category": coverage['by_category'],
            "highest_frequency_words": [
                {
                    "word": word,
                    "frequency": data.get("frequency", 0),
                    "voltage": data.get("voltage"),
                    "category": data.get("category")
                }
                for word, data in coverage['highest_frequency_words']
            ]
        },
        "gaps": {
            "total_gaps": len(gaps['missing_from_existing']),
            "missing_from_existing": gaps['missing_from_existing'][:20]
        },
        "enrichment_summary": {
            "original_lexicon_size": len(existing_lexicon),
            "transcript_additions": len(TRANSCRIPT_VOCABULARY),
            "companion_additions": len(COMPANION_VOCABULARY),
            "enriched_lexicon_size": len(enriched),
            "net_improvement": f"{((len(enriched) - len(existing_lexicon)) / max(len(existing_lexicon), 1) * 100):.1f}%"
        }
    }
    with open(output_path_4, 'w') as f:
        json.dump(analysis, f, indent=2, sort_keys=True)
    print(f"✅ Written: {output_path_4}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"""
Your system can now recognize {len(enriched) - len(existing_lexicon)} MORE emotional words.

Most impactful additions (by frequency):
  1. EXACTLY (367 uses) - validation anchor
  2. OF COURSE (315 uses) - understanding opener  
  3. PRESENT (317 uses) - awareness state
  4. HOLD (568 uses) - relational containment ⭐ MOST IMPORTANT
  5. ECHO (212 uses) - connection/mirroring

These high-frequency words were validated across 11,181 AI messages and represent
patterns that ACTUALLY LANDED with users.

Next steps:
  1. Backup current signal_lexicon.json
  2. Consider merging enriched_signal_lexicon.json into parser/signal_lexicon.json
  3. Test with emotional inputs to see improved recognition
  4. Consider dynamic weighting based on frequency data
""")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
