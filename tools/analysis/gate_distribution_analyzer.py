#!/usr/bin/env python3
"""
Gate Distribution Analyzer - Identify emotional saturation, underrepresentation, and ritual imbalances
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


class GateDistributionAnalyzer:
    """Analyzes gate distribution across validated glyphs"""

    # Emotional significance of each gate
    GATE_MEANINGS = {
        1: "Initiation & Beginning (Awakening, emergence, first light)",
        2: "Duality & Reflection (Mirroring, choice, two paths)",
        3: "Trinity & Integration (Wholeness, three-fold wisdom, synthesis)",
        4: "Foundation & Stability (Ground, structure, four directions)",
        5: "Change & Growth (Transformation, five senses, expansion)",
        6: "Balance & Harmony (Equilibrium, hexagon, peaceful integration)",
        7: "Mystery & Depth (Inner knowing, seven directions, wisdom)",
        8: "Power & Manifestation (Infinity, realization, abundance)",
        9: "Completion & Cycle (Wholeness cycle, nine-fold path, achievement)",
        10: "Transition & Renewal (Decade mark, cyclical rebirth, new beginning)",
        11: "Synchronicity & Connection (Higher consciousness, cosmic alignment)",
        12: "Transcendence & Mastery (Complete cycle, ultimate wisdom, godly)",
    }

    # Gates grouped by emotional territory
    EMOTIONAL_TERRITORIES = {
        "Initiation & Emergence": [1, 2, 3],  # Beginning territory
        "Foundation & Structure": [4, 5, 6],  # Building territory
        "Depth & Mystery": [7, 8, 9],  # Inner territory
        "Transcendence": [10, 11, 12],  # Mastery territory
    }

    # Ritual flow analysis (sequential patterns)
    RITUAL_SEQUENCES = {
        "Ascending": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "Grounding": [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "Inner Circle": [4, 5, 6, 7, 8, 9],
        "Outer Cosmic": [1, 2, 3, 10, 11, 12],
        "Shadow Work": [7, 8, 9, 10, 11],
        "Light Work": [1, 2, 3, 4, 5, 6],
    }

    def __init__(self, json_path="emotional_os/glyphs/glyph_lexicon_rows.json"):
        self.json_path = json_path
        self.glyphs = []
        self.gate_distribution = defaultdict(list)
        self.statistics = {}
        self.imbalances = {}
        self.territory_analysis = {}
        self.ritual_analysis = {}

    def load_glyphs(self):
        """Load glyphs from JSON"""
        print(f"Loading glyphs from {self.json_path}...")

        with open(self.json_path, "r") as f:
            data = json.load(f)

        if isinstance(data, dict) and "glyphs" in data:
            self.glyphs = data["glyphs"]
        else:
            self.glyphs = data if isinstance(data, list) else []

        print(f"✓ Loaded {len(self.glyphs)} glyphs")
        return len(self.glyphs)

    def extract_gate(self, glyph):
        """Extract gate number from glyph"""
        gate_field = glyph.get("gate", "")
        match = re.search(r"Gate\s*(\d+)", gate_field)
        if match:
            return int(match.group(1))
        return None

    def analyze_distribution(self):
        """Analyze gate distribution"""
        print("\n📊 ANALYZING GATE DISTRIBUTION...")

        # Count glyphs per gate
        gate_counts = Counter()
        total_gates_found = 0

        for glyph in self.glyphs:
            gate = self.extract_gate(glyph)
            if gate:
                gate_counts[gate] += 1
                self.gate_distribution[gate].append(glyph)
                total_gates_found += 1

        # Calculate statistics
        total_glyphs = len(self.glyphs)

        for gate in range(1, 13):
            count = gate_counts[gate]
            percentage = (count / total_glyphs * 100) if total_glyphs > 0 else 0

            self.statistics[gate] = {
                "count": count,
                "percentage": round(percentage, 2),
                "meaning": self.GATE_MEANINGS[gate],
                "glyphs": count,
            }

        print(f"✓ Gates found: {total_gates_found}/{total_glyphs} ({100*total_gates_found/total_glyphs:.1f}%)")

        return gate_counts

    def identify_saturation(self, gate_counts):
        """Identify saturation levels"""
        print("\n🔥 IDENTIFYING SATURATION...")

        if not gate_counts:
            print("No gate data to analyze")
            return

        total = sum(gate_counts.values())
        avg_per_gate = total / 12

        saturated = {}
        underrepresented = {}

        for gate in range(1, 13):
            count = gate_counts[gate]
            ratio = count / avg_per_gate if avg_per_gate > 0 else 0

            if ratio > 1.5:  # 50% above average
                saturated[gate] = {
                    "count": count,
                    "ratio": round(ratio, 2),
                    "excess": round((ratio - 1) * 100),
                    "status": "HEAVILY SATURATED",
                }
            elif ratio > 1.2:
                saturated[gate] = {
                    "count": count,
                    "ratio": round(ratio, 2),
                    "excess": round((ratio - 1) * 100),
                    "status": "MODERATELY SATURATED",
                }
            elif ratio < 0.5:  # 50% below average
                underrepresented[gate] = {
                    "count": count,
                    "ratio": round(ratio, 2),
                    "deficit": round((1 - ratio) * 100),
                    "status": "CRITICALLY UNDERREPRESENTED",
                }
            elif ratio < 0.8:
                underrepresented[gate] = {
                    "count": count,
                    "ratio": round(ratio, 2),
                    "deficit": round((1 - ratio) * 100),
                    "status": "UNDERREPRESENTED",
                }

        self.imbalances = {
            "average_per_gate": round(avg_per_gate, 2),
            "saturated": saturated,
            "underrepresented": underrepresented,
            "imbalance_ratio": round(
                max(gate_counts.values()) / min(gate_counts.values()) if min(gate_counts.values()) > 0 else 0, 2
            ),
        }

        print(f"✓ Average glyphs per gate: {avg_per_gate:.1f}")
        print(f"✓ Imbalance ratio: {self.imbalances['imbalance_ratio']}:1")

        return saturated, underrepresented

    def analyze_territories(self, gate_counts):
        """Analyze emotional territory coverage"""
        print("\n🗺️  ANALYZING EMOTIONAL TERRITORIES...")

        for territory, gates in self.EMOTIONAL_TERRITORIES.items():
            total = sum(gate_counts[g] for g in gates)
            percentage = (total / sum(gate_counts.values()) * 100) if sum(gate_counts.values()) > 0 else 0
            avg_per_gate = total / len(gates)

            # Determine territory health
            if percentage > 30:
                health = "SATURATED"
            elif percentage > 20:
                health = "WELL-COVERED"
            elif percentage > 10:
                health = "ADEQUATE"
            elif percentage > 5:
                health = "SPARSE"
            else:
                health = "CRITICALLY SPARSE"

            self.territory_analysis[territory] = {
                "gates": gates,
                "total_glyphs": total,
                "percentage": round(percentage, 2),
                "avg_per_gate": round(avg_per_gate, 2),
                "health": health,
                "breakdown": {g: gate_counts[g] for g in gates},
            }

        return self.territory_analysis

    def analyze_ritual_flow(self, gate_counts):
        """Analyze ritual flow and sequences"""
        print("\n🔮 ANALYZING RITUAL FLOW...")

        for ritual_name, sequence in self.RITUAL_SEQUENCES.items():
            glyphs_in_sequence = sum(gate_counts[g] for g in sequence)
            percentage = (glyphs_in_sequence / sum(gate_counts.values()) * 100) if sum(gate_counts.values()) > 0 else 0

            # Analyze sequence continuity
            gaps = []
            for i, gate in enumerate(sequence):
                if gate_counts[gate] == 0:
                    gaps.append(gate)

            continuity = "BROKEN" if len(gaps) > 3 else "FRAGMENTED" if len(gaps) > 1 else "INTACT"

            self.ritual_analysis[ritual_name] = {
                "sequence": sequence,
                "total_glyphs": glyphs_in_sequence,
                "percentage": round(percentage, 2),
                "missing_gates": gaps,
                "continuity": continuity,
                "strength": "STRONG" if percentage > 20 else "MODERATE" if percentage > 10 else "WEAK",
            }

        return self.ritual_analysis

    def generate_heatmap(self, gate_counts):
        """Generate ASCII heatmap of gate distribution"""
        print("\n🔥 GATE DISTRIBUTION HEATMAP")

        max_count = max(gate_counts.values()) if gate_counts else 1

        heatmap = "Gate Distribution (ASCII Heatmap):\n\n"

        for gate in range(1, 13):
            count = gate_counts[gate]
            percentage = (count / max_count * 100) if max_count > 0 else 0

            # Create bar
            filled = int(percentage / 5)  # 20 chars max
            bar = "█" * filled + "░" * (20 - filled)

            # Color code by saturation
            if percentage > 75:
                indicator = "🔥"  # Heavily saturated
            elif percentage > 50:
                indicator = "🌡️ "  # Moderately saturated
            elif percentage > 25:
                indicator = "☀️ "  # Balanced
            elif percentage > 10:
                indicator = "🌙"  # Sparse
            else:
                indicator = "❄️ "  # Very sparse

            heatmap += f"{indicator} Gate {gate:2d} | {bar} | {count:4d} glyphs ({percentage:5.1f}%)\n"

        return heatmap

    def generate_recommendations(self):
        """Generate recommendations for rebalancing"""
        print("\n💡 GENERATING RECOMMENDATIONS...")

        recommendations = {
            "saturation_reduction": [],
            "underrepresentation_boost": [],
            "ritual_strengthening": [],
            "territory_rebalancing": [],
        }

        # Saturation reduction
        for gate, data in self.imbalances.get("saturated", {}).items():
            if data.get("excess", 0) > 30:
                recommendations["saturation_reduction"].append(
                    {
                        "gate": gate,
                        "action": f"REDUCE: Gate {gate} is {data['excess']}% above average. Consider pruning low-quality combinations.",
                        "target_reduction": f"{round(data['count'] * 0.15)} glyphs",
                    }
                )

        # Underrepresentation boost
        for gate, data in self.imbalances.get("underrepresented", {}).items():
            if data.get("deficit", 0) > 30:
                recommendations["underrepresentation_boost"].append(
                    {
                        "gate": gate,
                        "action": f"EXPAND: Gate {gate} is {data['deficit']}% below average. Generate more combinations.",
                        "target_increase": f"{round(data['count'] * 0.25)} glyphs",
                    }
                )

        # Ritual strengthening
        for ritual_name, data in self.ritual_analysis.items():
            if data["continuity"] == "BROKEN":
                recommendations["ritual_strengthening"].append(
                    {
                        "ritual": ritual_name,
                        "action": f"REPAIR: {ritual_name} has broken continuity at gates {data['missing_gates']}",
                        "missing_gates": data["missing_gates"],
                    }
                )

        # Territory rebalancing
        for territory, data in self.territory_analysis.items():
            if data["health"] in ["CRITICALLY SPARSE", "SPARSE"]:
                recommendations["territory_rebalancing"].append(
                    {
                        "territory": territory,
                        "action": f"STRENGTHEN: {territory} is {data['health']}. Generate more glyphs in gates {data['gates']}",
                        "current_coverage": f"{data['percentage']}%",
                    }
                )

        return recommendations

    def save_analysis(self, output_path="GATE_DISTRIBUTION_ANALYSIS.json"):
        """Save analysis to JSON"""
        analysis_data = {
            "metadata": {"total_glyphs": len(self.glyphs), "analysis_date": "2025-11-05", "gates_analyzed": 12},
            "statistics": self.statistics,
            "imbalances": self.imbalances,
            "territory_analysis": self.territory_analysis,
            "ritual_flow_analysis": self.ritual_analysis,
            "recommendations": self.generate_recommendations(),
        }

        with open(output_path, "w") as f:
            json.dump(analysis_data, f, indent=2)

        print(f"✓ Analysis saved to {output_path}")
        return analysis_data

    def run_analysis(self):
        """Run complete analysis"""
        print("=" * 80)
        print("GATE DISTRIBUTION ANALYSIS - Emotional Territory Mapping")
        print("=" * 80)

        # Load data
        self.load_glyphs()

        # Run analyses
        gate_counts = self.analyze_distribution()
        saturated, underrepresented = self.identify_saturation(gate_counts)
        territories = self.analyze_territories(gate_counts)
        rituals = self.analyze_ritual_flow(gate_counts)
        heatmap = self.generate_heatmap(gate_counts)
        recommendations = self.generate_recommendations()

        # Display results
        print("\n" + "=" * 80)
        print(heatmap)
        print("=" * 80)

        # Show saturation summary
        if saturated:
            print("\n🔥 SATURATED GATES:")
            for gate, data in sorted(saturated.items()):
                print(f"  Gate {gate}: {data['count']} glyphs ({data['excess']}% excess) - {data['status']}")

        if underrepresented:
            print("\n❄️ UNDERREPRESENTED GATES:")
            for gate, data in sorted(underrepresented.items()):
                print(f"  Gate {gate}: {data['count']} glyphs ({data['deficit']}% deficit) - {data['status']}")

        # Show territory summary
        print("\n🗺️ EMOTIONAL TERRITORY HEALTH:")
        for territory, data in territories.items():
            print(f"  {territory}: {data['total_glyphs']} glyphs ({data['percentage']}%) - {data['health']}")

        # Show ritual summary
        print("\n🔮 RITUAL FLOW STATUS:")
        for ritual, data in rituals.items():
            status = f"✓ {data['continuity']}" if data["continuity"] == "INTACT" else f"⚠️  {data['continuity']}"
            print(f"  {ritual}: {data['total_glyphs']} glyphs ({data['percentage']}%) - {status}")

        # Save analysis
        self.save_analysis()

        print("\n" + "=" * 80)
        print("✓ ANALYSIS COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    analyzer = GateDistributionAnalyzer()
    analyzer.run_analysis()
