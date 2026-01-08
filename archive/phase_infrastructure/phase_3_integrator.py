"""
Phase 3: INTEGRATION
====================

Merge 3,347 Phase 3 glyphs into production system.

Current System State:
  - File: emotional_os/glyphs/glyph_lexicon_rows.json
  - Total glyphs: 3,758
  - ID range: 0-9999 (after Phase 2)

Phase 3 Input:
  - File: phase_3_generated_glyphs.json
  - Total glyphs: 3,347
  - ID range: 10000-13346
  - Gates: 2, 5, 6, 8, 9, 10

Expected Output:
  - Total glyphs: 7,105
  - All 12 gates populated and balanced
  - All 6 ritual sequences intact
  - New system ready for Phase 4
"""

import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


class Phase3Integrator:
    """Integrate Phase 3 glyphs into production system."""

    SYSTEM_JSON = "/workspaces/saoriverse-console/emotional_os/glyphs/glyph_lexicon_rows.json"
    PHASE_3_JSON = "/workspaces/saoriverse-console/phase_3_generated_glyphs.json"
    BACKUP_PATH = "/workspaces/saoriverse-console/glyph_lexicon_rows_before_phase3.json"

    RITUAL_SEQUENCES = {
        "Ascending": list(range(1, 13)),
        "Grounding": list(range(12, 0, -1)),
        "Inner Circle": [4, 5, 6, 7, 8, 9],
        "Outer Cosmic": [1, 2, 3, 10, 11, 12],
        "Shadow Work": [7, 8, 9, 10, 11],
        "Light Work": [1, 2, 3, 4, 5, 6],
    }

    def __init__(self):
        """Initialize integrator."""
        self.current_glyphs = []
        self.phase_3_glyphs = []
        self.integration_results = {
            "backup_created": None,
            "current_count": 0,
            "phase_3_count": 0,
            "final_count": 0,
            "id_conflicts": [],
            "gate_distribution": {},
            "rituals_verified": {},
        }

    def load_current_system(self) -> List[Dict]:
        """Load current production glyphs."""
        print("\n📖 Loading current system...")

        with open(self.SYSTEM_JSON, "r") as f:
            data = json.load(f)

        # Handle both formats: dict with 'glyphs' key or direct list
        if isinstance(data, dict) and "glyphs" in data:
            glyphs = data["glyphs"]
        else:
            glyphs = data if isinstance(data, list) else []

        print(f"   ✅ Loaded {len(glyphs)} current glyphs")
        self.integration_results["current_count"] = len(glyphs)

        return glyphs

    def load_phase_3_glyphs(self) -> List[Dict]:
        """Load Phase 3 generated glyphs."""
        print("\n📖 Loading Phase 3 glyphs...")

        with open(self.PHASE_3_JSON, "r") as f:
            glyphs = json.load(f)

        print(f"   ✅ Loaded {len(glyphs)} Phase 3 glyphs")
        self.integration_results["phase_3_count"] = len(glyphs)

        return glyphs

    def create_backup(self):
        """Create backup before integration."""
        print("\n💾 Creating backup...")
        shutil.copy(self.SYSTEM_JSON, self.BACKUP_PATH)
        print(f"   ✅ Backup created: {self.BACKUP_PATH}")
        self.integration_results["backup_created"] = self.BACKUP_PATH

    def validate_id_ranges(self, current: List[Dict], phase_3: List[Dict]) -> Tuple[set, set]:
        """Validate that ID ranges don't conflict."""
        print("\n🔍 Validating ID ranges...")

        current_ids = set(g.get("id") for g in current if "id" in g)
        phase_3_ids = set(g.get("id") for g in phase_3 if "id" in g)

        conflicts = current_ids & phase_3_ids

        if conflicts:
            print(f"   ⚠️  ID conflicts detected: {len(conflicts)} conflicts")
            self.integration_results["id_conflicts"] = list(conflicts)[:10]
        else:
            print("   ✅ No ID conflicts")
            print(f"      Current ID range: {min(current_ids)}-{max(current_ids)}")
            print(f"      Phase 3 ID range: {min(phase_3_ids)}-{max(phase_3_ids)}")

        return current_ids, phase_3_ids

    def merge_glyphs(self, current: List[Dict], phase_3: List[Dict]) -> List[Dict]:
        """Merge current and Phase 3 glyphs."""
        print("\n🔄 Merging glyphs...")

        merged = current + phase_3

        print(f"   ✅ Merged {len(current)} + {len(phase_3)} = {len(merged)} glyphs")
        self.integration_results["final_count"] = len(merged)

        return merged

    def analyze_gate_distribution(self, glyphs: List[Dict]) -> Dict:
        """Analyze gate distribution."""
        print("\n📊 Analyzing gate distribution...")

        gate_counts = Counter()
        for g in glyphs:
            gate_str = g.get("gate", "").strip()
            if gate_str:
                try:
                    gate_num = int(gate_str.split()[-1])
                    gate_counts[gate_num] += 1
                except (ValueError, IndexError):
                    pass

        distribution = {}
        for gate in range(1, 13):
            count = gate_counts.get(gate, 0)
            distribution[gate] = count
            status = "✅" if count > 0 else "❌"
            print(f"   Gate {gate:2d}: {count:5d} glyphs {status}")

        self.integration_results["gate_distribution"] = distribution

        return distribution

    def verify_ritual_sequences(self, glyphs: List[Dict]) -> Dict[str, bool]:
        """Verify all ritual sequences are intact."""
        print("\n🔄 Verifying ritual sequences...")

        gates_present = set()
        for g in glyphs:
            gate_str = g.get("gate", "").strip()
            if gate_str:
                try:
                    gate_num = int(gate_str.split()[-1])
                    gates_present.add(gate_num)
                except (ValueError, IndexError):
                    pass

        ritual_status = {}
        for ritual_name, gates in self.RITUAL_SEQUENCES.items():
            is_intact = all(gate in gates_present for gate in gates)
            status = "✅" if is_intact else "❌"
            print(f"   {ritual_name:20s}: {status}")
            ritual_status[ritual_name] = is_intact

        self.integration_results["rituals_verified"] = ritual_status

        return ritual_status

    def save_integrated_system(self, glyphs: List[Dict]):
        """Save integrated glyphs to system JSON."""
        print("\n💾 Saving integrated system...")

        # Wrap in dict with 'glyphs' key to match production format
        output = {"glyphs": glyphs}

        with open(self.SYSTEM_JSON, "w") as f:
            json.dump(output, f, indent=2)

        print(f"   ✅ Saved {len(glyphs)} glyphs to {self.SYSTEM_JSON}")

    def execute_phase_3_integration(self):
        """Execute full Phase 3 integration."""
        print("\n" + "=" * 80)
        print("PHASE 3: INTEGRATION")
        print("=" * 80)

        # Load data
        current_glyphs = self.load_current_system()
        phase_3_glyphs = self.load_phase_3_glyphs()

        # Create backup
        self.create_backup()

        # Validate IDs
        self.validate_id_ranges(current_glyphs, phase_3_glyphs)

        # Merge
        merged_glyphs = self.merge_glyphs(current_glyphs, phase_3_glyphs)

        # Analyze distribution
        distribution = self.analyze_gate_distribution(merged_glyphs)

        # Verify rituals
        rituals = self.verify_ritual_sequences(merged_glyphs)

        # Save
        self.save_integrated_system(merged_glyphs)

        # Report
        print("\n" + "=" * 80)
        print("INTEGRATION COMPLETE")
        print("=" * 80)
        print("\n📊 SYSTEM METRICS:")
        print(f"   Previous: {self.integration_results['current_count']} glyphs")
        print(f"   Added: {self.integration_results['phase_3_count']} glyphs")
        print(f"   Total: {self.integration_results['final_count']} glyphs")

        print("\n🔄 RITUAL STATUS:")
        intact_rituals = sum(1 for status in rituals.values() if status)
        print(f"   {intact_rituals}/{len(rituals)} rituals INTACT")

        print("\n✨ NEXT STEPS:")
        print("   1. Run validation suite")
        print("   2. Verify gate balance")
        print("   3. Generate Phase 3 completion report")
        print("   4. Prepare Phase 4 (final deployment)")

        print("\n" + "=" * 80)

        return self.integration_results


def main():
    """Execute Phase 3 integration."""
    print("\n" + "🌟" * 40)
    print("PHASE 3: INTEGRATION")
    print("🌟" * 40)

    integrator = Phase3Integrator()
    results = integrator.execute_phase_3_integration()

    print("\n✨ Integration complete! System ready for validation.")


if __name__ == "__main__":
    main()
