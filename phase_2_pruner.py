"""
Phase 2: SATURATION PRUNING
============================

Objective: Reduce Gates 3 & 7 from 95.99% saturation to balanced distribution

Current State:
  - Gate 3: 2,682 glyphs (need → 1,200)
  - Gate 7: 3,494 glyphs (need → 1,200)
  - Removal: 3,776 glyphs total

Strategy: Intelligent diversity-preserving pruning
  - Calculate semantic diversity for each glyph
  - Identify clusters of similar concepts
  - Keep most representative from each cluster
  - Ensure all emotion spectrums preserved
"""

import json
import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple


class Phase2Pruner:
    """Intelligently prune saturated gates while preserving diversity."""

    def __init__(self, lexicon_path):
        """Initialize pruner with glyph lexicon."""
        with open(lexicon_path, "r") as f:
            data = json.load(f)
            # Extract glyphs list from the dict
            if isinstance(data, dict) and "glyphs" in data:
                self.glyphs = data["glyphs"]
            elif isinstance(data, list):
                self.glyphs = data
            else:
                self.glyphs = list(data.values())[0] if data else []

        self.gate_glyphs = defaultdict(list)
        self.glyphs_by_id = {}

        # Index glyphs by gate and ID
        for glyph in self.glyphs:
            gate = glyph.get("gate", None)
            glyph_id = glyph.get("id", None)

            if gate and glyph_id:
                # Extract gate number from "Gate X" format
                if isinstance(gate, str) and "Gate" in gate:
                    gate_num = int(gate.split()[-1])
                else:
                    gate_num = gate

                self.gate_glyphs[gate_num].append(glyph)
                self.glyphs_by_id[glyph_id] = glyph

    def extract_emotion_concepts(self, glyph_name: str) -> Set[str]:
        """Extract core emotion concepts from glyph name."""
        # Remove common words and extract key concepts
        stop_words = {
            "of",
            "in",
            "through",
            "within",
            "with",
            "the",
            "a",
            "an",
            "and",
            "or",
            "to",
            "for",
            "by",
            "is",
            "are",
            "be",
            "sacred",
            "divine",
            "gentle",
            "profound",
            "ultimate",
            "moment",
            "state",
            "journey",
            "flow",
            "essence",
        }

        words = re.findall(r"\b[a-z]+\b", glyph_name.lower())
        concepts = {w for w in words if w not in stop_words and len(w) > 2}
        return concepts

    def calculate_semantic_diversity_score(self, glyph: Dict) -> float:
        """
        Calculate uniqueness score for a glyph.
        Lower score = more common/similar to others
        Higher score = more unique/distinct
        """
        name = glyph.get("name", "")
        gate = glyph.get("gate", None)
        signal = glyph.get("signal", "")

        concepts = self.extract_emotion_concepts(name)

        # Base score from number of unique concepts
        score = len(concepts) * 0.3

        # Bonus for signal complexity (longer = more unique)
        signal_len = len(signal)
        score += min(signal_len / 50, 1.0) * 0.2  # Max 0.2 points

        # Bonus for name length (longer = more specific)
        name_len = len(name)
        score += min(name_len / 100, 1.0) * 0.2  # Max 0.2 points

        # Check how many other glyphs have overlapping concepts
        gate_glyphs = self.gate_glyphs.get(gate, [])
        overlap_count = 0
        for other in gate_glyphs:
            other_concepts = self.extract_emotion_concepts(other.get("name", ""))
            overlap = len(concepts & other_concepts)
            if overlap > 0:
                overlap_count += 1

        # Penalty for high overlap with others
        if gate_glyphs:
            overlap_ratio = overlap_count / len(gate_glyphs)
            score -= overlap_ratio * 0.3  # Penalty: -0.3 max

        return max(score, 0.1)  # Minimum 0.1

    def identify_concept_clusters(self, gate: int, sample_size: int = 100) -> List[Set[str]]:
        """
        Identify clusters of conceptually similar glyphs.
        Returns list of concept sets representing clusters.
        """
        glyphs = self.gate_glyphs.get(gate, [])
        if not glyphs:
            return []

        # Sample if too many glyphs
        import random

        sample = random.sample(glyphs, min(sample_size, len(glyphs)))

        clusters = []
        concept_to_glyphs = defaultdict(list)

        for glyph in sample:
            concepts = self.extract_emotion_concepts(glyph.get("name", ""))
            for concept in concepts:
                concept_to_glyphs[concept].append(glyph)

        # Group similar glyphs
        processed = set()
        for concept, glyph_list in concept_to_glyphs.items():
            if concept in processed:
                continue

            cluster = set()
            for glyph in glyph_list:
                glyph_concepts = self.extract_emotion_concepts(glyph.get("name", ""))
                cluster.update(glyph_concepts)
                processed.update(glyph_concepts)

            if cluster:
                clusters.append(cluster)

        return clusters

    def select_glyphs_to_keep(self, gate: int, target_count: int) -> List[Dict]:
        """
        Intelligently select glyphs to keep from saturated gate.

        Strategy:
          1. Calculate diversity score for each glyph
          2. Identify concept clusters
          3. Keep highest-scoring glyphs overall
          4. Ensure all major clusters represented
          5. Preserve ritual markers
        """
        glyphs = self.gate_glyphs.get(gate, [])
        if len(glyphs) <= target_count:
            return glyphs

        # Calculate diversity scores
        scored_glyphs = []
        for glyph in glyphs:
            score = self.calculate_semantic_diversity_score(glyph)
            glyph_id = glyph.get("glyph_id")

            # Bonus for ritual marker presence
            signal = glyph.get("signal", "")
            ritual_bonus = 0
            if any(marker in signal for marker in ["r:", "ritual"]):
                ritual_bonus = 0.5

            # Bonus for shorter names (more focused)
            name_penalty = -len(glyph.get("name", "")) / 500

            total_score = score + ritual_bonus + name_penalty
            scored_glyphs.append((total_score, glyph_id, glyph))

        # Sort by score descending (highest = keep)
        scored_glyphs.sort(key=lambda x: x[0], reverse=True)

        # Select top N
        kept = scored_glyphs[:target_count]
        kept_glyphs = [g[2] for g in kept]

        return kept_glyphs

    def execute_phase_2_pruning(self) -> Dict:
        """Execute full Phase 2 pruning on Gates 3 & 7."""
        print("\n" + "=" * 80)
        print("PHASE 2: SATURATION PRUNING - EXECUTION")
        print("=" * 80)

        pruning_results = {
            "gates_pruned": [3, 7],
            "removals": {},
            "kept": {},
            "before": {},
            "after": {},
            "total_removed": 0,
        }

        # Gate 3: 2,682 → 1,200 (remove 1,482)
        print("\n🔄 PROCESSING GATE 3")
        print("-" * 80)
        gate_3_glyphs = self.gate_glyphs.get(3, [])
        target_3 = 1200
        removal_count_3 = len(gate_3_glyphs) - target_3

        print(f"   Current: {len(gate_3_glyphs)} glyphs")
        print(f"   Target:  {target_3} glyphs")
        print(f"   Remove:  {removal_count_3} glyphs")

        kept_3 = self.select_glyphs_to_keep(3, target_3)
        kept_3_ids = {g.get("id") for g in kept_3}
        removed_3 = [g for g in gate_3_glyphs if g.get("id") not in kept_3_ids]

        print(f"   ✅ Selected {len(kept_3)} to keep")
        print(f"   ✅ Identified {len(removed_3)} to remove")

        pruning_results["before"][3] = len(gate_3_glyphs)
        pruning_results["after"][3] = len(kept_3)
        pruning_results["kept"][3] = [g.get("id") for g in kept_3]
        pruning_results["removals"][3] = [g.get("id") for g in removed_3]
        pruning_results["total_removed"] += len(removed_3)

        # Gate 7: 3,494 → 1,200 (remove 2,294)
        print("\n🔄 PROCESSING GATE 7")
        print("-" * 80)
        gate_7_glyphs = self.gate_glyphs.get(7, [])
        target_7 = 1200
        removal_count_7 = len(gate_7_glyphs) - target_7

        print(f"   Current: {len(gate_7_glyphs)} glyphs")
        print(f"   Target:  {target_7} glyphs")
        print(f"   Remove:  {removal_count_7} glyphs")

        kept_7 = self.select_glyphs_to_keep(7, target_7)
        kept_7_ids = {g.get("id") for g in kept_7}
        removed_7 = [g for g in gate_7_glyphs if g.get("id") not in kept_7_ids]

        print(f"   ✅ Selected {len(kept_7)} to keep")
        print(f"   ✅ Identified {len(removed_7)} to remove")

        pruning_results["before"][7] = len(gate_7_glyphs)
        pruning_results["after"][7] = len(kept_7)
        pruning_results["kept"][7] = [g.get("id") for g in kept_7]
        pruning_results["removals"][7] = [g.get("id") for g in removed_7]
        pruning_results["total_removed"] += len(removed_7)

        # Summary
        print("\n" + "=" * 80)
        print("PRUNING SUMMARY")
        print("=" * 80)
        print(f"Gate 3: {len(gate_3_glyphs)} → {len(kept_3)} ({removal_count_3} removed)")
        print(f"Gate 7: {len(gate_7_glyphs)} → {len(kept_7)} ({removal_count_7} removed)")
        print(f"Total removed: {pruning_results['total_removed']}")
        print(f"New system total: {len(self.glyphs) - pruning_results['total_removed']} glyphs")
        print("=" * 80)

        return pruning_results

    def apply_pruning(self, pruning_results: Dict) -> List[Dict]:
        """Apply pruning results to create new glyph list."""
        print("\n🔄 Applying pruning...")

        removed_ids = set()
        for gate in [3, 7]:
            removed_ids.update(pruning_results["removals"].get(gate, []))

        # Filter glyphs - keep those whose 'id' is not in removed_ids
        new_glyphs = [g for g in self.glyphs if g.get("id") not in removed_ids]

        print(f"   ✅ Filtered glyphs")
        print(f"   ✅ New total: {len(new_glyphs)} glyphs (removed {len(removed_ids)})")

        return new_glyphs

    def save_pruning_results(self, new_glyphs: List[Dict], pruning_results: Dict, output_path: str, backup_path=None):
        """Save pruned glyphs and backup original."""
        # Backup original if requested
        if backup_path:
            with open(backup_path, "w") as f:
                json.dump(self.glyphs, f, indent=2)
            print(f"\n   ✅ Backup created: {backup_path}")

        # Save pruned glyphs
        with open(output_path, "w") as f:
            json.dump(new_glyphs, f, indent=2)
        print(f"   ✅ Pruned glyphs saved: {output_path}")

        # Save pruning metadata
        metadata_path = output_path.replace(".json", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(pruning_results, f, indent=2)
        print(f"   ✅ Metadata saved: {metadata_path}")

        return new_glyphs


def main():
    """Execute Phase 2 pruning."""
    print("\n" + "🔮" * 40)
    print("PHASE 2: SATURATION PRUNING")
    print("🔮" * 40)

    # Initialize pruner
    pruner = Phase2Pruner("/workspaces/saoriverse-console/emotional_os/glyphs/glyph_lexicon_rows.json")

    print(f"\n📊 System Status:")
    print(f"   Total glyphs loaded: {len(pruner.glyphs)}")
    print(f"   Gate 3 glyphs: {len(pruner.gate_glyphs[3])}")
    print(f"   Gate 7 glyphs: {len(pruner.gate_glyphs[7])}")

    # Execute pruning analysis
    pruning_results = pruner.execute_phase_2_pruning()

    # Apply pruning
    new_glyphs = pruner.apply_pruning(pruning_results)

    # Save results
    pruner.save_pruning_results(
        new_glyphs,
        pruning_results,
        "/workspaces/saoriverse-console/emotional_os/glyphs/glyph_lexicon_rows.json",
        "/workspaces/saoriverse-console/glyph_lexicon_rows_before_phase2.json",
    )

    print("\n" + "✨" * 40)
    print("✨ PHASE 2 PRUNING COMPLETE!")
    print("✨" * 40)
    print(f"\n✅ Results:")
    print(f"   Removed: {pruning_results['total_removed']} glyphs")
    print(f"   New total: {len(new_glyphs)} glyphs")
    print(f"   System status: Ready for Phase 3")


if __name__ == "__main__":
    main()
