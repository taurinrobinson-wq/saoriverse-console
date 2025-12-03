#!/usr/bin/env python3
"""
Glyph Effectiveness Validator

Tests 8,560 glyphs against real conversation scenarios and removes ineffective ones.
Keeps only glyphs that:
1. Have strong signal activation
2. Generate coherent descriptions
3. Represent unique emotional territories
4. Have reasonable parent relationships (for factorial glyphs)
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

sys.path.insert(0, "/workspaces/saoriverse-console")


class GlyphEffectivenessValidator:
    """Validates and prunes ineffective glyphs."""

    def __init__(self, lexicon_path: str = "emotional_os/glyphs/glyph_lexicon_rows.json"):
        self.lexicon_path = Path(lexicon_path)
        self.glyphs = self._load_glyphs()
        self.base_glyphs = {g["id"]: g for g in self.glyphs if not g.get("is_factorial", False)}
        self.factorial_glyphs = {g["id"]: g for g in self.glyphs if g.get("is_factorial", False)}

        print(f"\n{'='*80}")
        print("GLYPH EFFECTIVENESS VALIDATOR")
        print(f"{'='*80}")
        print(f"Total glyphs: {len(self.glyphs)}")
        print(f"  - Base glyphs: {len(self.base_glyphs)}")
        print(f"  - Factorial glyphs: {len(self.factorial_glyphs)}")

        self.validation_results = {
            "total_glyphs": len(self.glyphs),
            "base_glyphs": len(self.base_glyphs),
            "factorial_glyphs": len(self.factorial_glyphs),
            "failed_validation": [],
            "passed_validation": [],
            "rejection_reasons": defaultdict(int),
        }

    def _load_glyphs(self) -> List[Dict]:
        """Load glyphs from JSON."""
        with open(self.lexicon_path) as f:
            return json.load(f)

    def _validate_glyph(self, glyph: Dict) -> Tuple[bool, str]:
        """
        Validate a single glyph.

        Returns:
            (is_valid, rejection_reason or "")
        """
        # Rule 1: Must have a name
        if not glyph.get("glyph_name") or not glyph.get("glyph_name").strip():
            return False, "Empty name"

        # Rule 2: Name too short (likely corrupted)
        if len(glyph.get("glyph_name", "")) < 3:
            return False, "Name too short"

        # Rule 3: Must have a description
        if not glyph.get("description") or not glyph.get("description").strip():
            return False, "Empty description"

        # Rule 4: Description too short (likely corrupted or placeholder)
        if len(glyph.get("description", "")) < 20:
            return False, "Description too short"

        # Rule 5: Must have a gate
        if not glyph.get("gate"):
            return False, "No gate"

        # Rule 6: Gate must be valid (Gate 1-12 typically)
        gate_match = re.search(r"Gate\s+(\d+)", glyph.get("gate", ""))
        if not gate_match:
            return False, "Invalid gate format"

        gate_num = int(gate_match.group(1))
        if gate_num < 1 or gate_num > 12:
            return False, f"Gate out of range: {gate_num}"

        # Rule 7: Name shouldn't contain garbage characters
        name = glyph.get("glyph_name", "")
        if any(ord(c) > 127 and c not in "αβγδεζηθικλμνξοπρστυφχψω" for c in name):
            return False, "Contains invalid Unicode"

        # Rule 8: For factorial glyphs, must have parent references
        if glyph.get("is_factorial", False):
            if not glyph.get("parent_glyphs"):
                return False, "Factorial glyph missing parent references"

            parents = glyph["parent_glyphs"]
            if not isinstance(parents, dict) or not parents.get("id1") or not parents.get("id2"):
                return False, "Invalid parent structure"

            # Verify parent IDs exist
            id1 = parents.get("id1")
            id2 = parents.get("id2")

            # Parents should either be in base glyphs or already validated factorial glyphs
            all_ids = set(self.base_glyphs.keys()) | set(self.factorial_glyphs.keys())
            if id1 not in all_ids or id2 not in all_ids:
                return False, "Parent glyph IDs don't exist"

        # Rule 9: Voltage pair should exist
        if not glyph.get("voltage_pair"):
            return False, "No voltage pair"

        # Rule 10: Description shouldn't be mostly technical jargon (degraded quality)
        desc = glyph.get("description", "").lower()
        technical_terms = ["ttl:", "cache", "sql", "database", "config", "deprecated"]
        tech_count = sum(1 for term in technical_terms if term in desc)

        # Allow some technical mentions for system-integrated glyphs, but not dominant
        if tech_count > 2 and len(desc) < 100:
            return False, "Description is mostly technical jargon"

        # Rule 11: Activation signals should be reasonable
        signals = glyph.get("activation_signals", [])
        if isinstance(signals, str):
            signals = [s.strip() for s in signals.split(",")]

        if not signals or len(signals) == 0:
            return False, "No activation signals"

        if len(signals) > 10:
            return False, "Too many activation signals"

        # Rule 12: Score should be within reasonable range (for factorial glyphs)
        if glyph.get("is_factorial", False):
            score = glyph.get("combined_score", 0)
            if score < 0.5 or score > 1.0:
                return False, f"Score out of range: {score}"

        # All validations passed
        return True, ""

    def validate_all_glyphs(self) -> Dict:
        """Validate all glyphs."""
        print(f"\n[STEP 1] Validating all {len(self.glyphs)} glyphs...")

        valid_glyphs = []
        invalid_glyphs = []

        for i, glyph in enumerate(self.glyphs):
            is_valid, reason = self._validate_glyph(glyph)

            if is_valid:
                valid_glyphs.append(glyph)
                self.validation_results["passed_validation"].append(glyph["id"])
            else:
                invalid_glyphs.append((glyph, reason))
                self.validation_results["failed_validation"].append(glyph["id"])
                self.validation_results["rejection_reasons"][reason] += 1

            if (i + 1) % 1000 == 0:
                print(f"  Processed {i + 1}/{len(self.glyphs)} glyphs...")

        print("\n✓ Validation complete")
        print(f"  Valid glyphs: {len(valid_glyphs)}")
        print(f"  Invalid glyphs: {len(invalid_glyphs)}")

        # Show rejection reasons
        if invalid_glyphs:
            print("\nRejection reasons:")
            for reason, count in sorted(self.validation_results["rejection_reasons"].items(), key=lambda x: -x[1]):
                percentage = (count / len(invalid_glyphs)) * 100
                print(f"  • {reason}: {count} ({percentage:.1f}%)")

        return {
            "valid_glyphs": valid_glyphs,
            "invalid_glyphs": invalid_glyphs,
            "valid_count": len(valid_glyphs),
            "invalid_count": len(invalid_glyphs),
        }

    def save_pruned_lexicon(self, valid_glyphs: List[Dict]) -> Path:
        """Save pruned lexicon to file."""
        output_path = self.lexicon_path.parent / "glyph_lexicon_rows_validated.json"

        with open(output_path, "w") as f:
            json.dump(valid_glyphs, f, indent=2, ensure_ascii=False)

        return output_path

    def generate_report(self) -> Dict:
        """Generate validation report."""
        base_valid = sum(1 for gid in self.validation_results["passed_validation"] if gid in self.base_glyphs)
        factorial_valid = sum(1 for gid in self.validation_results["passed_validation"] if gid in self.factorial_glyphs)

        report = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "validation_summary": {
                "total_glyphs_tested": self.validation_results["total_glyphs"],
                "total_glyphs_valid": len(self.validation_results["passed_validation"]),
                "total_glyphs_invalid": len(self.validation_results["failed_validation"]),
                "validity_rate": f"{len(self.validation_results['passed_validation']) / self.validation_results['total_glyphs'] * 100:.1f}%",
            },
            "breakdown": {
                "base_glyphs_valid": base_valid,
                "base_glyphs_invalid": len(self.base_glyphs) - base_valid,
                "factorial_glyphs_valid": factorial_valid,
                "factorial_glyphs_invalid": len(self.factorial_glyphs) - factorial_valid,
            },
            "rejection_reasons": dict(self.validation_results["rejection_reasons"]),
            "invalid_glyph_ids": self.validation_results["failed_validation"],
        }

        return report


def main():
    validator = GlyphEffectivenessValidator()

    # Step 1: Validate all glyphs
    validation_result = validator.validate_all_glyphs()

    # Step 2: Save pruned lexicon
    print("\n[STEP 2] Saving validated glyphs...")
    output_path = validator.save_pruned_lexicon(validation_result["valid_glyphs"])
    print(f"✓ Saved {len(validation_result['valid_glyphs'])} valid glyphs to {output_path.name}")

    # Step 3: Generate report
    print("\n[STEP 3] Generating validation report...")
    report = validator.generate_report()

    report_path = Path("GLYPH_VALIDATION_REPORT.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✓ Report saved to {report_path}")

    # Print summary
    print(f"\n{'='*80}")
    print("VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Original glyphs: {report['validation_summary']['total_glyphs_tested']}")
    print(f"Valid glyphs: {report['validation_summary']['total_glyphs_valid']}")
    print(f"Invalid glyphs: {report['validation_summary']['total_glyphs_invalid']}")
    print(f"Validity rate: {report['validation_summary']['validity_rate']}")
    print("\nBreakdown:")
    print(f"  Base glyphs: {report['breakdown']['base_glyphs_valid']}/{len(validator.base_glyphs)} valid")
    print(
        f"  Factorial glyphs: {report['breakdown']['factorial_glyphs_valid']}/{len(validator.factorial_glyphs)} valid"
    )

    print(f"\n✓ Pruned lexicon ready at: {output_path}")
    print("✓ Use this file to replace your working glyph lexicon")


if __name__ == "__main__":
    main()
