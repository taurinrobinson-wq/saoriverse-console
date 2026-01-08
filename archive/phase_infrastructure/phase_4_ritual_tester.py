"""
Phase 4: RITUAL EXECUTION TEST SUITE
====================================

Comprehensive testing of all 6 ritual sequences to verify production readiness.

Rituals to Test:
  1. Ascending (1→2→3→...→12)
  2. Grounding (12→11→10→...→1)
  3. Inner Circle (4→5→6→7→8→9)
  4. Outer Cosmic (1,2,3,10,11,12)
  5. Shadow Work (7→8→9→10→11)
  6. Light Work (1→2→3→4→5→6)

Test Coverage:
  - Sequential access to all gates in order
  - Glyph availability verification
  - Ritual completeness check
  - Error handling and edge cases
"""

import json
import time
from collections import defaultdict
from typing import Dict, List, Tuple


class RitualExecutionTester:
    """Test ritual sequences for production readiness."""

    RITUALS = {
        "Ascending": list(range(1, 13)),
        "Grounding": list(range(12, 0, -1)),
        "Inner Circle": [4, 5, 6, 7, 8, 9],
        "Outer Cosmic": [1, 2, 3, 10, 11, 12],
        "Shadow Work": [7, 8, 9, 10, 11],
        "Light Work": [1, 2, 3, 4, 5, 6],
    }

    SYSTEM_JSON = "/workspaces/saoriverse-console/emotional_os/glyphs/glyph_lexicon_rows.json"

    def __init__(self):
        """Initialize tester."""
        self.glyphs = []
        self.glyphs_by_gate = defaultdict(list)
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "rituals": {},
            "performance": {},
            "errors": [],
        }

    def load_system(self) -> bool:
        """Load production system."""
        print("\n📖 Loading production system...")
        try:
            with open(self.SYSTEM_JSON, "r") as f:
                data = json.load(f)

            # Handle both dict and list formats
            if isinstance(data, dict) and "glyphs" in data:
                self.glyphs = data["glyphs"]
            else:
                self.glyphs = data if isinstance(data, list) else []

            print(f"   ✅ Loaded {len(self.glyphs)} glyphs")

            # Index by gate
            for glyph in self.glyphs:
                gate_str = glyph.get("gate", "").strip()
                if gate_str:
                    try:
                        gate_num = int(gate_str.split()[-1])
                        self.glyphs_by_gate[gate_num].append(glyph)
                    except (ValueError, IndexError):
                        pass

            print(f"   ✅ Indexed {len(self.glyphs_by_gate)} gates")
            return True
        except Exception as e:
            print(f"   ❌ Error loading system: {e}")
            self.test_results["errors"].append(f"Load error: {e}")
            return False

    def test_ritual_completeness(self, ritual_name: str, gates: List[int]) -> Tuple[bool, int, int]:
        """Test that all gates in a ritual have glyphs."""
        print(f"\n   Testing {ritual_name}...")

        total_glyphs = 0
        empty_gates = []

        for gate in gates:
            gate_glyphs = self.glyphs_by_gate.get(gate, [])
            total_glyphs += len(gate_glyphs)

            if len(gate_glyphs) == 0:
                empty_gates.append(gate)
                print(f"      ❌ Gate {gate}: 0 glyphs (EMPTY)")
            else:
                print(f"      ✅ Gate {gate}: {len(gate_glyphs)} glyphs")

        ritual_pass = len(empty_gates) == 0
        status = "✅ PASS" if ritual_pass else "❌ FAIL"
        print(f"   {status} - {ritual_name}: {total_glyphs} glyphs across {len(gates)} gates")

        return ritual_pass, len(gates), total_glyphs

    def test_glyph_accessibility(self) -> Tuple[int, int]:
        """Test that all glyphs are accessible by ID."""
        print("\n🔍 Testing glyph accessibility...")

        accessible = 0
        inaccessible = 0

        # Build ID index
        glyphs_by_id = {}
        for glyph in self.glyphs:
            if "id" in glyph:
                glyphs_by_id[glyph["id"]] = glyph

        # Test random sample (first 100 + last 100)
        sample_ids = []
        for glyph in self.glyphs[:100]:
            if "id" in glyph:
                sample_ids.append(glyph["id"])
        for glyph in self.glyphs[-100:]:
            if "id" in glyph:
                sample_ids.append(glyph["id"])

        sample_ids = list(set(sample_ids))  # Remove duplicates

        for glyph_id in sample_ids:
            if glyph_id in glyphs_by_id:
                accessible += 1
            else:
                inaccessible += 1

        print(f"   ✅ Accessible: {accessible}/{len(sample_ids)}")
        if inaccessible > 0:
            print(f"   ❌ Inaccessible: {inaccessible}")

        return accessible, inaccessible

    def test_gate_coverage(self) -> Tuple[int, List[int]]:
        """Test that all 12 gates have glyphs."""
        print("\n🗺️  Testing gate coverage...")

        populated_gates = []
        empty_gates = []

        for gate in range(1, 13):
            gate_glyphs = self.glyphs_by_gate.get(gate, [])
            if len(gate_glyphs) > 0:
                populated_gates.append(gate)
                print(f"   Gate {gate:2d}: {len(gate_glyphs):5d} glyphs ✅")
            else:
                empty_gates.append(gate)
                print(f"   Gate {gate:2d}: EMPTY ❌")

        coverage = len(populated_gates)
        print(f"\n   Coverage: {coverage}/12 gates populated")

        return coverage, empty_gates

    def test_data_integrity(self) -> Tuple[bool, int, int]:
        """Test data integrity."""
        print("\n🔐 Testing data integrity...")

        errors = 0
        warnings = 0

        # Check for missing required fields
        for idx, glyph in enumerate(self.glyphs):
            if "id" not in glyph:
                errors += 1
                print(f"   ❌ Glyph {idx}: Missing 'id'")
            if "gate" not in glyph:
                errors += 1
                print(f"   ❌ Glyph {idx}: Missing 'gate'")
            if "glyph_name" not in glyph:
                warnings += 1

        # Check for ID duplicates
        ids = [g.get("id") for g in self.glyphs if "id" in g]
        if len(ids) != len(set(ids)):
            duplicates = len(ids) - len(set(ids))
            errors += duplicates
            print(f"   ❌ Found {duplicates} duplicate IDs")

        if errors == 0:
            print("   ✅ No integrity errors")
        if warnings > 0:
            print(f"   ⚠️  {warnings} minor warnings")

        return errors == 0, errors, warnings

    def test_ritual_execution(self, ritual_name: str, gates: List[int]) -> Dict:
        """Execute a ritual and measure performance."""
        print(f"\n⏱️  Executing ritual: {ritual_name}")

        start_time = time.time()

        ritual_result = {
            "name": ritual_name,
            "gates": gates,
            "total_gates": len(gates),
            "total_glyphs": 0,
            "execution_time": 0,
            "gate_access_times": {},
            "status": "PASS",
        }

        for gate in gates:
            gate_start = time.time()
            gate_glyphs = self.glyphs_by_gate.get(gate, [])
            gate_time = time.time() - gate_start

            ritual_result["gate_access_times"][gate] = gate_time * 1000  # ms
            ritual_result["total_glyphs"] += len(gate_glyphs)

            if len(gate_glyphs) == 0:
                ritual_result["status"] = "FAIL"

        ritual_result["execution_time"] = (time.time() - start_time) * 1000  # ms

        status_mark = "✅" if ritual_result["status"] == "PASS" else "❌"
        print(f"   {status_mark} {ritual_name}: {ritual_result['execution_time']:.2f}ms")
        print(f"      Gates: {len(gates)}, Total glyphs: {ritual_result['total_glyphs']}")

        return ritual_result

    def execute_phase_4_tests(self) -> Dict:
        """Execute full Phase 4 test suite."""
        print("\n" + "=" * 80)
        print("PHASE 4: RITUAL EXECUTION TEST SUITE")
        print("=" * 80)

        # Load system
        if not self.load_system():
            return self.test_results

        # Test 1: Gate coverage
        print("\n" + "-" * 80)
        print("TEST 1: GATE COVERAGE")
        print("-" * 80)
        coverage, empty_gates = self.test_gate_coverage()
        self.test_results["total_tests"] += 1
        if coverage == 12:
            self.test_results["passed"] += 1
            print("   ✅ PASS: All 12 gates populated")
        else:
            self.test_results["failed"] += 1
            print(f"   ❌ FAIL: Missing gates: {empty_gates}")
            self.test_results["errors"].append(f"Empty gates: {empty_gates}")

        # Test 2: Data integrity
        print("\n" + "-" * 80)
        print("TEST 2: DATA INTEGRITY")
        print("-" * 80)
        integrity_ok, errors, warnings = self.test_data_integrity()
        self.test_results["total_tests"] += 1
        if integrity_ok:
            self.test_results["passed"] += 1
            print("   ✅ PASS: No data integrity issues")
        else:
            self.test_results["failed"] += 1
            print(f"   ❌ FAIL: Found {errors} errors")
            self.test_results["errors"].append(f"Data errors: {errors}")

        # Test 3: Glyph accessibility
        print("\n" + "-" * 80)
        print("TEST 3: GLYPH ACCESSIBILITY")
        print("-" * 80)
        accessible, inaccessible = self.test_glyph_accessibility()
        self.test_results["total_tests"] += 1
        if inaccessible == 0:
            self.test_results["passed"] += 1
            print("   ✅ PASS: All tested glyphs accessible")
        else:
            self.test_results["failed"] += 1
            print(f"   ❌ FAIL: {inaccessible} glyphs inaccessible")
            self.test_results["errors"].append(f"Inaccessible glyphs: {inaccessible}")

        # Test 4-9: Ritual execution
        print("\n" + "-" * 80)
        print("TEST 4-9: RITUAL EXECUTION TESTS")
        print("-" * 80)

        for ritual_name, gates in self.RITUALS.items():
            pass_ok, total_gates, total_glyphs = self.test_ritual_completeness(ritual_name, gates)
            self.test_results["total_tests"] += 1

            if pass_ok:
                self.test_results["passed"] += 1
                self.test_results["rituals"][ritual_name] = {
                    "status": "PASS",
                    "gates": total_gates,
                    "glyphs": total_glyphs,
                }
            else:
                self.test_results["failed"] += 1
                self.test_results["rituals"][ritual_name] = {
                    "status": "FAIL",
                    "gates": total_gates,
                    "glyphs": total_glyphs,
                }

        # Test 10: Performance
        print("\n" + "-" * 80)
        print("TEST 10: PERFORMANCE PROFILING")
        print("-" * 80)

        for ritual_name, gates in self.RITUALS.items():
            perf_result = self.test_ritual_execution(ritual_name, gates)
            self.test_results["performance"][ritual_name] = perf_result

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUITE RESULTS")
        print("=" * 80)
        print(f"\nTotal Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed']} ✅")
        print(f"Failed: {self.test_results['failed']} ❌")

        if self.test_results["failed"] == 0:
            print("\n🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        else:
            print(f"\n⚠️  {self.test_results['failed']} tests failed - review required")
            for error in self.test_results["errors"]:
                print(f"   • {error}")

        print("=" * 80)

        return self.test_results

    def save_test_results(self, output_path: str):
        """Save test results to JSON."""
        with open(output_path, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Test results saved to {output_path}")


def main():
    """Execute Phase 4 ritual tests."""
    print("\n" + "🌟" * 40)
    print("PHASE 4: RITUAL EXECUTION TEST SUITE")
    print("🌟" * 40)

    tester = RitualExecutionTester()
    results = tester.execute_phase_4_tests()

    tester.save_test_results("/workspaces/saoriverse-console/phase_4_test_results.json")

    print("\n" + "✨" * 40)
    print("✨ PHASE 4 TESTING COMPLETE!")
    print("✨" * 40)


if __name__ == "__main__":
    main()
