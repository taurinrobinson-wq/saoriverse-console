#!/usr/bin/env python3
"""
Glyph Factorial Engine

Generates new glyph combinations by multiplying existing glyphs together.
This creates a factorial expansion of emotional vocabulary through
systematic combination and pruning.

Architecture:
1. Load primary glyphs (300+ comprehensive glyphs from CSV)
2. Generate all possible combinations (300² = 90,000+ candidates)
3. Score each combination by quality and novelty
4. Prune redundancy and semantic overlap
5. Curate final set of new glyphs
6. Sync results back to JSON for system use

The "multiplication" is conceptual - combining emotional dimensions
to create new, more nuanced emotional expressions.
"""

import csv
import json
import logging
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


@dataclass
class GlyphCombination:
    """A candidate glyph created from combining two primary glyphs."""

    # Identity
    parent_ids: Tuple[int, int]  # IDs of two parent glyphs
    parent_names: Tuple[str, str]  # Names of parent glyphs
    parent_pairs: Tuple[str, str]  # Voltage pairs of parents

    # New glyph identity
    new_voltage_pair: str  # Combined voltage notation
    new_name: str  # Generated name
    new_description: str  # Generated description

    # Quality metrics
    novelty_score: float = 0.0  # How novel vs. existing
    coherence_score: float = 0.0  # How well combined
    coverage_score: float = 0.0  # Fills emotional gap
    activation_signals: List[str] = field(
        default_factory=list)  # Combined signals
    gate: str = ""  # Estimated gate

    # Status
    is_duplicate: bool = False
    duplicate_of: Optional[int] = None
    pruned: bool = False
    prune_reason: str = ""

    # Metadata
    combined_score: float = 0.0  # Final score
    rank: int = 0  # Ranking among candidates
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class GlyphFactorialEngine:
    """Generates and analyzes glyph combinations."""

    def __init__(
        self,
        glyph_csv: str = "emotional_os/glyphs/glyph_lexicon_rows.csv",
        glyph_json: str = "emotional_os/glyphs/glyph_lexicon_rows.json",
        output_dir: str = "emotional_os/glyphs/factorial",
    ):
        """Initialize the factorial engine.

        Args:
            glyph_csv: Path to comprehensive CSV glyph lexicon (300+ glyphs)
            glyph_json: Path to JSON glyph lexicon for output sync
            output_dir: Directory for output files
        """
        self.glyph_csv_path = Path(glyph_csv)
        self.glyph_json_path = Path(glyph_json)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.primary_glyphs: List[Dict] = []
        self.combinations: List[GlyphCombination] = []
        self.pruned_combinations: List[GlyphCombination] = []

        # Voltage symbols used in system
        self.voltage_symbols = ["γ", "θ", "λ", "δ", "β", "Ω", "α", "ε", "ζ"]

        # Emotional dimensions extracted from gates
        self.emotional_templates = self._build_templates()

    def _build_templates(self) -> Dict[str, List[str]]:
        """Build templates for describing glyph combinations."""
        return {
            "joy_grief": [
                "Celebrating what was lost",
                "Joyful mourning",
                "Grief that honors",
                "Bittersweet remembrance",
            ],
            "stillness_motion": [
                "Movement that grounds",
                "Still energy",
                "Dancing stillness",
                "Quiet momentum",
            ],
            "openness_containment": [
                "Held openness",
                "Bounded freedom",
                "Protected vulnerability",
                "Enclosed spaciousness",
            ],
            "self_other": [
                "Mirrored presence",
                "Witnessed solitude",
                "Connected isolation",
                "Shared singularity",
            ],
            "known_unknown": [
                "Familiar mystery",
                "Recognized unknown",
                "Known darkness",
                "Visible hidden",
            ],
        }

    def load_primary_glyphs(self) -> bool:
        """Load primary glyphs from CSV lexicon (most comprehensive).

        Falls back to JSON if CSV not available.

        Returns:
            bool: True if loaded successfully
        """
        try:
            # Try CSV first (300+ comprehensive glyphs)
            if self.glyph_csv_path.exists():
                logger.info(f"Loading glyphs from CSV: {self.glyph_csv_path}")
                self.primary_glyphs = self._load_glyphs_from_csv()
                logger.info(
                    f"✓ Loaded {len(self.primary_glyphs)} glyphs from CSV")
                return True

            # Fall back to JSON if CSV not available
            elif self.glyph_json_path.exists():
                logger.warning("CSV not found, falling back to JSON")
                with open(self.glyph_json_path, "r", encoding="utf-8") as f:
                    self.primary_glyphs = json.load(f)
                logger.info(
                    f"✓ Loaded {len(self.primary_glyphs)} glyphs from JSON")
                return True

            else:
                logger.error("Neither CSV nor JSON glyph lexicon found")
                return False

        except Exception as e:
            logger.error(f"Error loading primary glyphs: {e}")
            return False

    def _load_glyphs_from_csv(self) -> List[Dict]:
        """Load glyphs from CSV file.

        Returns:
            List of glyph dictionaries
        """
        glyphs: List[Dict[str, Any]] = []
        try:
            with open(self.glyph_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        glyph = {
                            "id": int(row.get("id", 0)) if row.get("id") else len(glyphs) + 1,
                            "voltage_pair": row.get("voltage_pair", ""),
                            "glyph_name": row.get("glyph_name", ""),
                            "description": row.get("description", ""),
                            "gate": row.get("gate", ""),
                            "activation_signals": (
                                row.get("activation_signals", "").split(
                                    ",") if row.get("activation_signals") else []
                            ),
                        }
                        glyphs.append(glyph)

            logger.info(f"✓ Loaded {len(glyphs)} glyphs from CSV")
            return glyphs

        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return []

    def combine_voltage_pairs(self, pair1: str, pair2: str) -> str:
        """Combine two voltage pairs into a new notation.

        Args:
            pair1: First voltage pair (e.g., "α-β")
            pair2: Second voltage pair (e.g., "γ-δ")

        Returns:
            str: Combined voltage notation
        """
        # Handle both simple pairs (α-β) and compound pairs (γ × γ)
        if "×" in pair1:
            symbols1 = [s.strip() for s in pair1.split("×")]
        else:
            symbols1 = [s.strip() for s in pair1.split("-")]

        if "×" in pair2:
            symbols2 = [s.strip() for s in pair2.split("×")]
        else:
            symbols2 = [s.strip() for s in pair2.split("-")]

        # Create new combination by pairing first symbols and second symbols
        # This represents a blending of the emotional voltages
        new_pair = f"{symbols1[0]}-{symbols2[0]} × {symbols1[1] if len(symbols1) > 1 else symbols1[0]}-{symbols2[1] if len(symbols2) > 1 else symbols2[0]}"

        return new_pair

    def combine_activation_signals(self, signals1, signals2) -> List[str]:
        """Combine activation signals from two glyphs.

        Args:
            signals1: Comma-separated string or list of signals from glyph 1
            signals2: Comma-separated string or list of signals from glyph 2

        Returns:
            List of unique combined signals
        """
        # Handle both string and list formats
        if isinstance(signals1, list):
            set1 = set(s.strip() if isinstance(s, str) else str(s)
                       for s in signals1)
        else:
            set1 = set(s.strip() for s in signals1.split(",") if s.strip())

        if isinstance(signals2, list):
            set2 = set(s.strip() if isinstance(s, str) else str(s)
                       for s in signals2)
        else:
            set2 = set(s.strip() for s in signals2.split(",") if s.strip())

        combined = sorted(list(set1 | set2))
        return combined

    def estimate_gate(self, parent_gates: Tuple[str, str], signals: List[str]) -> str:
        """Estimate appropriate gate for combined glyph.

        Args:
            parent_gates: Gates of parent glyphs
            signals: Activation signals of combination

        Returns:
            str: Estimated gate
        """
        # If both parents are same gate, use it
        gate1, gate2 = parent_gates
        if gate1 == gate2:
            return gate1

        # Extract gate numbers
        try:
            num1 = int(gate1.split()[-1])
            num2 = int(gate2.split()[-1])
            avg_gate = int((num1 + num2) / 2)
            # Clamp to valid range (1-10, but primarily 2-10)
            if avg_gate < 2:
                avg_gate = 2
            elif avg_gate > 10:
                avg_gate = 10
            return f"Gate {avg_gate}"
        except:
            # Default to bridging gate
            return "Gate 5"

    def generate_combination_name(self, name1: str, name2: str) -> str:
        """Generate name for combined glyph.

        Strategy: Extract key emotional words and combine poetically

        Args:
            name1: First parent name
            name2: Second parent name

        Returns:
            str: Generated name for combination
        """
        # Extract last meaningful words
        words1 = name1.split()
        words2 = name2.split()

        # Try to create a poetic combination
        if words1 and words2:
            # Use last word from each as base
            word1 = words1[-1]
            word2 = words2[-1]

            # Create various combinations
            combinations = [
                f"{word1} of {word2}",
                f"{word2}-bearing {word1}",
                f"{word1} through {word2}",
            ]

            return combinations[0]  # Default to first pattern

        return f"{name1}-{name2}"

    def generate_combination_description(self, desc1: str, desc2: str, name1: str, name2: str) -> str:
        """Generate description for combined glyph by blending parent descriptions.

        Args:
            desc1: Description of first parent
            desc2: Description of second parent
            name1: Name of first parent
            name2: Name of second parent

        Returns:
            str: Generated description
        """
        # Extract key emotional phrases from descriptions
        # Split by common connectors
        phrases1 = [s.strip() for s in re.split(r"[,;.]", desc1)[:2]]
        phrases2 = [s.strip() for s in re.split(r"[,;.]", desc2)[:2]]

        # Create blended description
        combined = f"{phrases1[0]} interwoven with {phrases2[0]}. "
        combined += f"Where {name1} meets {name2}, a new resonance emerges."

        return combined

    def generate_all_combinations(self) -> List[GlyphCombination]:
        """Generate all possible glyph combinations.

        Returns:
            List of GlyphCombination objects
        """
        if not self.primary_glyphs:
            logger.error("No primary glyphs loaded")
            return []

        logger.info(
            f"Generating combinations from {len(self.primary_glyphs)} glyphs...")

        combinations = []
        total = len(self.primary_glyphs) ** 2
        count = 0

        for i, glyph1 in enumerate(self.primary_glyphs):
            for j, glyph2 in enumerate(self.primary_glyphs):
                count += 1

                # Skip self-combinations (already exist)
                if i == j:
                    continue

                # Create combination
                combination = GlyphCombination(
                    parent_ids=(glyph1["id"], glyph2["id"]),
                    parent_names=(glyph1["glyph_name"], glyph2["glyph_name"]),
                    parent_pairs=(glyph1["voltage_pair"],
                                  glyph2["voltage_pair"]),
                    new_voltage_pair=self.combine_voltage_pairs(
                        glyph1["voltage_pair"], glyph2["voltage_pair"]),
                    new_name=self.generate_combination_name(
                        glyph1["glyph_name"], glyph2["glyph_name"]),
                    new_description=self.generate_combination_description(
                        glyph1["description"], glyph2["description"], glyph1["glyph_name"], glyph2["glyph_name"]
                    ),
                    activation_signals=self.combine_activation_signals(
                        glyph1["activation_signals"], glyph2["activation_signals"]
                    ),
                    gate=self.estimate_gate(
                        (glyph1["gate"], glyph2["gate"]), []),
                )

                combinations.append(combination)

                if count % 500 == 0:
                    logger.info(f"  Generated {count}/{total} combinations...")

        self.combinations = combinations
        logger.info(f"✓ Generated {len(combinations)} total combinations")

        return combinations

    def score_combinations(self) -> None:
        """Score all combinations by novelty, coherence, and coverage."""
        logger.info(f"Scoring {len(self.combinations)} combinations...")

        for combination in self.combinations:
            # Calculate novelty (how different from parents)
            novelty = self._calculate_novelty(combination)

            # Calculate coherence (how well do parents combine?)
            coherence = self._calculate_coherence(combination)

            # Calculate coverage (does this fill an emotional gap?)
            coverage = self._calculate_coverage(combination)

            # Combined score (weighted average)
            combination.novelty_score = novelty
            combination.coherence_score = coherence
            combination.coverage_score = coverage

            # Weight: 40% novelty, 35% coherence, 25% coverage
            combination.combined_score = (
                novelty * 0.40) + (coherence * 0.35) + (coverage * 0.25)

        # Sort by score
        self.combinations.sort(key=lambda c: c.combined_score, reverse=True)

        # Assign ranks
        for rank, combination in enumerate(self.combinations, 1):
            combination.rank = rank

        logger.info("✓ Scored all combinations")

    def _calculate_novelty(self, combination: GlyphCombination) -> float:
        """Calculate how novel this combination is (0-1).

        Higher score = more different from existing glyphs.
        """
        # Check if voltage pair is new
        existing_pairs = set(g["voltage_pair"] for g in self.primary_glyphs)
        if combination.new_voltage_pair not in existing_pairs:
            return 0.8  # New pair = high novelty

        # Check description novelty (length and uniqueness)
        desc_length = len(combination.new_description)
        novelty = min(0.6, desc_length / 200)  # Normalize to 0.6 max

        return novelty

    def _calculate_coherence(self, combination: GlyphCombination) -> float:
        """Calculate how well the combination makes sense (0-1).

        Higher score = parents blend well emotionally.
        """
        # Extract voltage symbols (handle both simple "α-β" and compound "α-β × γ-δ" formats)
        if "×" in combination.parent_pairs[0]:
            parts1 = combination.parent_pairs[0].split("×")
            symbols1 = [s.strip() for pair in parts1 for s in pair.split("-")]
        else:
            symbols1 = [s.strip()
                        for s in combination.parent_pairs[0].split("-")]

        if "×" in combination.parent_pairs[1]:
            parts2 = combination.parent_pairs[1].split("×")
            symbols2 = [s.strip() for pair in parts2 for s in pair.split("-")]
        else:
            symbols2 = [s.strip()
                        for s in combination.parent_pairs[1].split("-")]

        # Symbols that appear together = high coherence
        overlap = len(set(symbols1) & set(symbols2))
        coherence = overlap / max(len(self.voltage_symbols), 1)

        # Diversity bonus - complementary symbols are good
        all_symbols = set(symbols1 + symbols2)
        diversity = len(all_symbols) / max(len(self.voltage_symbols) * 2, 1)

        return min(1.0, (coherence + diversity) / 2)

    def _calculate_coverage(self, combination: GlyphCombination) -> float:
        """Calculate how well this fills an emotional gap (0-1).

        Higher score = addresses under-represented emotional territory.
        """
        # Count how many times each gate appears
        gate_counts = defaultdict(int)
        for glyph in self.primary_glyphs:
            gate_num = int(glyph["gate"].split()[-1]
                           ) if "gate" in glyph and glyph["gate"] else 5
            gate_counts[gate_num] += 1

        # Get combination's gate
        combo_gate = int(combination.gate.split()
                         [-1]) if combination.gate else 5

        # Less common gates get higher coverage score
        gate_frequency = gate_counts[combo_gate] / \
            max(len(self.primary_glyphs), 1)
        coverage = 1.0 - gate_frequency  # Inverse of frequency

        return max(0.0, min(1.0, coverage))

    def prune_combinations(self, keep_top_percent: float = 0.10, min_score_threshold: float = 0.5) -> Tuple[int, int]:
        """Prune low-quality combinations based on scoring and redundancy.

        Removes combinations that:
        - Score below minimum threshold
        - Are semantic duplicates of existing glyphs
        - Are semantic duplicates of higher-scored combinations
        - Combine identical parents (self-multiplication)

        Args:
            keep_top_percent: Keep top X% of combinations (default 10%)
            min_score_threshold: Minimum combined score to keep (0-1)

        Returns:
            Tuple of (total_combinations, kept_combinations)
        """
        if not self.combinations:
            logger.warning("No combinations to prune")
            return (0, 0)

        original_count = len(self.combinations)

        # Step 1: Remove self-combinations (same parent twice)
        before_self_removal = len(self.combinations)
        self.combinations = [
            c for c in self.combinations if c.parent_ids[0] != c.parent_ids[1]]
        logger.info(
            f"Removed {before_self_removal - len(self.combinations)} self-combinations")

        # Step 2: Remove duplicates and semantic near-duplicates
        seen_voltages = set()
        seen_descriptions = {}
        filtered = []
        duplicates = 0

        for combo in self.combinations:
            # Check for exact voltage pair duplicate
            if combo.new_voltage_pair in seen_voltages:
                combo.is_duplicate = True
                combo.pruned = True
                combo.prune_reason = "Duplicate voltage pair"
                duplicates += 1
                self.pruned_combinations.append(combo)
                continue

            # Check for semantic similarity in descriptions (simple substring check)
            is_semantic_dup = False
            for prev_desc, prev_combo in seen_descriptions.items():
                # Calculate simple text similarity
                similarity = self._text_similarity(
                    combo.new_description, prev_desc)
                if similarity > 0.80:  # 80% similar = duplicate
                    combo.is_duplicate = True
                    combo.duplicate_of = prev_combo.rank
                    combo.pruned = True
                    combo.prune_reason = f"Semantic duplicate (similarity: {similarity:.2f})"
                    is_semantic_dup = True
                    duplicates += 1
                    self.pruned_combinations.append(combo)
                    break

            if not is_semantic_dup:
                seen_voltages.add(combo.new_voltage_pair)
                seen_descriptions[combo.new_description] = combo
                filtered.append(combo)

        self.combinations = filtered
        logger.info(f"Removed {duplicates} duplicate/similar combinations")

        # Step 3: Apply score-based filtering
        before_score = len(self.combinations)
        score_removed = 0

        # Calculate threshold based on top percent or minimum score
        if self.combinations:
            scores = [c.combined_score for c in self.combinations]
            max_score = max(scores)
            dynamic_threshold = max_score * (1 - keep_top_percent)
            threshold = max(min_score_threshold, dynamic_threshold)

            filtered_by_score = []
            for combo in self.combinations:
                if combo.combined_score >= threshold:
                    filtered_by_score.append(combo)
                else:
                    combo.pruned = True
                    combo.prune_reason = f"Low score: {combo.combined_score:.3f} (threshold: {threshold:.3f})"
                    score_removed += 1
                    self.pruned_combinations.append(combo)

            self.combinations = filtered_by_score
            logger.info(
                f"Removed {score_removed} low-score combinations (threshold: {threshold:.3f})")

        final_count = len(self.combinations)
        removed_total = original_count - final_count

        logger.info(
            f"✓ Pruning complete: {original_count} → {final_count} combinations kept")
        logger.info(
            f"  Pruning ratio: {(removed_total/original_count*100):.1f}% removed")

        return (original_count, final_count)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (0-1) based on overlapping words.

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def export_combinations(self, filename: str = "factorial_candidates.json") -> Optional[Path]:
        """Export combinations to JSON file.

        Args:
            filename: Output filename

        Returns:
            Path to output file or None if export failed
        """
        output_path = self.output_dir / filename

        try:
            # Convert to serializable format
            export_data = {
                "metadata": {
                    "total_primary_glyphs": len(self.primary_glyphs),
                    "total_combinations": len(self.combinations),
                    "generated_at": datetime.now().isoformat(),
                },
                "combinations": [asdict(c) for c in self.combinations],
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Exported combinations to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting combinations: {e}")
            return None

    def sync_to_json(
        self, approved_combinations: Optional[List[GlyphCombination]] = None, output_path: Optional[str] = None
    ) -> bool:
        """Sync newly approved glyphs back to JSON lexicon file.

        Takes approved combinations and adds them to the JSON glyph lexicon,
        updating the system's working copy with new factorial glyphs.

        Args:
            approved_combinations: List of GlyphCombinations to add. If None, uses all combinations.
            output_path: Path to JSON file to update. If None, uses default glyph_json_path.

        Returns:
            bool: True if sync successful
        """
        try:
            target_path = Path(
                output_path) if output_path else self.glyph_json_path

            # Load existing glyphs from JSON
            existing_glyphs = []
            if target_path.exists():
                with open(target_path, "r", encoding="utf-8") as f:
                    existing_glyphs = json.load(f)

            # Get next ID
            next_id = max([g.get("id", 0)
                          for g in existing_glyphs], default=0) + 1

            # Add approved combinations as new glyphs
            combos_to_add = approved_combinations if approved_combinations else self.combinations

            for combo in combos_to_add:
                if not combo.pruned:  # Only add non-pruned combinations
                    new_glyph = {
                        "id": next_id,
                        "voltage_pair": combo.new_voltage_pair,
                        "glyph_name": combo.new_name,
                        "description": combo.new_description,
                        "gate": combo.gate,
                        "activation_signals": combo.activation_signals,
                        "is_factorial": True,  # Mark as generated from factorial
                        "parent_glyphs": {
                            "id1": combo.parent_ids[0],
                            "id2": combo.parent_ids[1],
                            "name1": combo.parent_names[0],
                            "name2": combo.parent_names[1],
                        },
                        "generated_at": combo.created_at,
                        "combined_score": combo.combined_score,
                    }
                    existing_glyphs.append(new_glyph)
                    next_id += 1

            # Write updated JSON
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(existing_glyphs, f, indent=2, ensure_ascii=False)

            num_added = len([c for c in combos_to_add if not c.pruned])
            logger.info(f"✓ Synced {num_added} new glyphs to {target_path}")
            return True

        except Exception as e:
            logger.error(f"Error syncing glyphs to JSON: {e}")
            return False

    def print_summary(self):
        """Print summary of combinations."""
        print("\n" + "=" * 80)
        print("GLYPH FACTORIAL GENERATION SUMMARY")
        print("=" * 80)

        print(f"\n✓ Primary glyphs: {len(self.primary_glyphs)}")
        print(f"✓ Total combinations: {len(self.combinations)}")

        if self.combinations:
            print("\n✓ Score statistics:")
            scores = [c.combined_score for c in self.combinations]
            print(f"  - Mean score: {sum(scores) / len(scores):.3f}")
            print(f"  - Max score: {max(scores):.3f}")
            print(f"  - Min score: {min(scores):.3f}")

            print("\n✓ Top 10 combinations by score:")
            for combo in self.combinations[:10]:
                print(f"\n  {combo.rank}. {combo.new_name}")
                print(
                    f"     Parents: {combo.parent_names[0]} × {combo.parent_names[1]}")
                print(f"     Score: {combo.combined_score:.3f}")
                print(f"     Novelty: {combo.novelty_score:.2f}")
                print(f"     Coherence: {combo.coherence_score:.2f}")


def main():
    """Test the glyph factorial engine."""
    engine = GlyphFactorialEngine()

    if not engine.load_primary_glyphs():
        logger.error("Failed to load primary glyphs")
        return

    engine.generate_all_combinations()
    engine.score_combinations()
    engine.export_combinations()
    engine.print_summary()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(name)s] - %(message)s")
    main()
