#!/usr/bin/env python3
"""
Example: Combining Factorial Expansion with Advanced Pruning

This shows how to:
1. Generate new glyphs through factorial (85k+ combinations)
2. Apply 5-layer advanced pruning
3. Get high-quality final result
"""

import sys

sys.path.insert(0, "/workspaces/saoriverse-console")

import json
from pathlib import Path

from emotional_os.glyphs.advanced_pruning_engine import AdvancedPruningEngine
from emotional_os.glyphs.glyph_factorial_engine import GlyphFactorialEngine


def combined_factorial_and_pruning_pipeline():
    """Complete pipeline: generate + prune new glyphs."""

    print("\n" + "=" * 80)
    print("COMBINED FACTORIAL EXPANSION + ADVANCED PRUNING")
    print("=" * 80)

    # ========== PHASE 1: FACTORIAL EXPANSION ==========
    print("\n[PHASE 1] Generating Factorial Combinations")
    print("-" * 80)

    factorial_engine = GlyphFactorialEngine(
        glyph_csv="emotional_os/glyphs/glyph_lexicon_rows.csv", glyph_json="emotional_os/glyphs/glyph_lexicon_rows.json"
    )

    # Load 292 primary glyphs from CSV
    print("Loading 292 primary glyphs from CSV...")
    factorial_engine.load_primary_glyphs()
    print(f"✓ Loaded {len(factorial_engine.primary_glyphs)} glyphs")

    # Generate combinations (for demo, use sample)
    print("\nGenerating combinations from first 100 glyphs (10,000 combos)...")
    print("(Full: 85,264 combinations - takes longer)")

    sample_size = 100
    combinations = []

    for i in range(sample_size):
        for j in range(sample_size):
            if i <= j:  # Upper triangle only
                glyph1 = factorial_engine.primary_glyphs[i]
                glyph2 = factorial_engine.primary_glyphs[j]

                # Create combination (abbreviated for demo)
                voltage_pair = factorial_engine.combine_voltage_pairs(glyph1["voltage_pair"], glyph2["voltage_pair"])
                name = factorial_engine.generate_combination_name(glyph1["glyph_name"], glyph2["glyph_name"])
                description = factorial_engine.generate_combination_description(
                    glyph1["description"], glyph2["description"], glyph1["glyph_name"], glyph2["glyph_name"]
                )
                signals = factorial_engine.combine_activation_signals(
                    ",".join(glyph1.get("activation_signals", [])), ",".join(glyph2.get("activation_signals", []))
                )
                gate = factorial_engine.estimate_gate(
                    (glyph1.get("gate", "Gate 5"), glyph2.get("gate", "Gate 5")), signals
                )

                from emotional_os.glyphs.glyph_factorial_engine import GlyphCombination

                combo = GlyphCombination(
                    parent_ids=(glyph1["id"], glyph2["id"]),
                    parent_names=(glyph1["glyph_name"], glyph2["glyph_name"]),
                    parent_pairs=(glyph1["voltage_pair"], glyph2["voltage_pair"]),
                    new_voltage_pair=voltage_pair,
                    new_name=name,
                    new_description=description,
                    activation_signals=signals,
                    gate=gate,
                )
                combinations.append(combo)

    factorial_engine.combinations = combinations
    print(f"✓ Generated {len(factorial_engine.combinations):,} combinations")

    # Score combinations
    print("\nScoring combinations...")
    factorial_engine.score_combinations()
    scores = [c.combined_score for c in factorial_engine.combinations]
    print(f"✓ Scored all {len(factorial_engine.combinations):,} combinations")
    print(f"  Average score: {sum(scores)/len(scores):.3f}")
    print(f"  Min: {min(scores):.3f}, Max: {max(scores):.3f}")

    # ========== PHASE 2: BASIC PRUNING (Optional, from factorial engine) ==========
    print("\n[PHASE 2] Initial Basic Pruning (Optional)")
    print("-" * 80)

    print("Pruning low-scoring combinations...")
    original, kept = factorial_engine.prune_combinations(keep_top_percent=0.20)
    print(f"✓ Basic prune: {original:,} → {kept:,} ({kept/original*100:.1f}%)")

    # ========== PHASE 3: ADVANCED PRUNING ==========
    print("\n[PHASE 3] Advanced 5-Layer Pruning")
    print("-" * 80)

    # Convert factorial combinations to glyph-like structure for advanced pruning
    print("Converting combinations to advanced pruning format...")

    # Create temporary glyph structure from factorial results
    factorial_glyphs = []
    for idx, combo in enumerate(factorial_engine.combinations, start=65):  # IDs start after base 64
        glyph = {
            "id": idx,
            "glyph_name": combo.new_name,
            "description": combo.new_description,
            "voltage_pair": combo.new_voltage_pair,
            "gate": combo.gate,
            "activation_signals": combo.activation_signals,
            "valence": "Stable",  # Could be enhanced
            "trace_role": "Combination catalyst",  # Could be derived
            "tone": "Mirror Deep",  # Could be enhanced
            "is_factorial": True,
            "parent_ids": list(combo.parent_ids),
            "parent_names": list(combo.parent_names),
            "combined_score": combo.combined_score,
        }
        factorial_glyphs.append(glyph)

    # Create temporary JSON for advanced pruning
    temp_json_path = "emotional_os/glyphs/factorial_candidates.json"
    with open(temp_json_path, "w") as f:
        json.dump(factorial_glyphs, f)

    # Initialize advanced pruning engine
    pruning_engine = AdvancedPruningEngine(
        glyph_lexicon_path=temp_json_path, archive_dir="emotional_os/glyphs/pruning_archive"
    )

    print(f"✓ Loaded {len(pruning_engine.glyphs)} factorial candidates")

    # Evaluate using 5-layer strategy
    print("\nApplying 5-layer pruning strategy...")
    print("  1. Signal Strength Filtering (25%)")
    print("  2. Trace Role Redundancy (20%)")
    print("  3. Usage Frequency (30%)")
    print("  4. Tone Diversity (15%)")
    print("  5. Reaction Chain Anchoring (10%)")

    candidates = pruning_engine.evaluate_all_glyphs()

    # Get statistics
    stats = pruning_engine.get_pruning_statistics()

    print(f"\n✓ Advanced pruning complete:")
    print(f"  Total evaluated: {stats['total_evaluated']:,}")
    print(f"  Recommended to prune: {stats['total_to_prune']:,} ({stats['prune_percentage']})")
    print(f"  Recommended to keep: {stats['total_to_keep']:,}")
    print(f"  Average confidence: {stats['average_confidence']}")

    # ========== PHASE 4: FINAL RESULTS ==========
    print("\n[PHASE 4] Final Results Summary")
    print("-" * 80)

    kept_candidates = [c for c in candidates if not c.should_prune]

    print(f"\nExpansion Pipeline Results:")
    print(f"  Original base glyphs: 64")
    print(f"  Factorial combinations generated: {len(factorial_engine.combinations):,}")
    print(f"  After basic pruning: {kept:,}")
    print(f"  After advanced 5-layer pruning: {len(kept_candidates):,}")
    print(f"  Final JSON would have: {64 + len(kept_candidates):,} total glyphs")
    print(f"  Expansion ratio: {(64 + len(kept_candidates))/64:.1f}x")

    # Show top new glyphs
    print(f"\nTop 5 New Glyphs (by advanced score):")
    top_candidates = sorted(kept_candidates, key=lambda x: x.combined_prune_score, reverse=True)[:5]
    for i, candidate in enumerate(top_candidates, 1):
        print(f"\n  {i}. {candidate.glyph_name}")
        print(f"     Advanced score: {candidate.combined_prune_score:.3f}")
        print(f"     Confidence: {candidate.prune_confidence:.1%}")
        print(f"     Signal strength: {candidate.signal_strength:.3f}")
        print(f"     Match history: {candidate.match_history}")

    # ========== PHASE 5: ARCHIVAL & REPORTING ==========
    print("\n[PHASE 5] Archival & Reporting")
    print("-" * 80)

    # Archive pruned glyphs
    pruned_candidates = [c for c in candidates if c.should_prune]
    if pruned_candidates:
        archive_path = pruning_engine.archive_pruned_glyphs(pruned_candidates, reason="factorial_expansion_pruning")
        print(f"✓ Archived {len(pruned_candidates):,} pruned glyphs")
        print(f"  Location: {archive_path}")

    # Create comprehensive report
    report_path = "emotional_os/glyphs/FACTORIAL_PRUNING_REPORT.json"
    report = pruning_engine.create_pruning_report(output_path=report_path)
    print(f"✓ Created comprehensive pruning report")
    print(f"  Location: {report_path}")

    # ========== PHASE 6: OPTIONAL - SYNC TO JSON ==========
    print("\n[PHASE 6] Optional: Sync to JSON")
    print("-" * 80)

    print("\nTo sync kept glyphs to JSON:")
    print(
        f"""
  # Create list of approved combos
  approved = [combo for combo in factorial_engine.combinations 
              if combo.glyph_id in [c.glyph_id for c in kept_candidates]]
  
  # Sync to JSON (adds as is_factorial=true)
  factorial_engine.sync_to_json(approved, 
                                output_path="emotional_os/glyphs/glyph_lexicon_rows.json")
  
  # This will expand your JSON from 64 → {64 + len(kept_candidates)} glyphs
    """
    )

    print("\n" + "=" * 80)
    print("✓ COMBINED PIPELINE COMPLETE")
    print("=" * 80)

    return {
        "original_base": 64,
        "factorial_generated": len(factorial_engine.combinations),
        "after_basic_pruning": kept,
        "after_advanced_pruning": len(kept_candidates),
        "final_total": 64 + len(kept_candidates),
        "expansion_ratio": (64 + len(kept_candidates)) / 64,
    }


if __name__ == "__main__":
    print(
        """
╔════════════════════════════════════════════════════════════════════════════╗
║           FACTORIAL EXPANSION + ADVANCED PRUNING EXAMPLE                   ║
║                                                                            ║
║ This demonstrates how to combine:                                         ║
║ 1. Glyph Factorial Engine → Generate 85k+ combinations                    ║
║ 2. Advanced Pruning Engine → 5-layer intelligent filtering                ║
║ 3. Result → High-quality curated expansions                               ║
╚════════════════════════════════════════════════════════════════════════════╝
    """
    )

    try:
        results = combined_factorial_and_pruning_pipeline()

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
