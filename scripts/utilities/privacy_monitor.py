#!/usr/bin/env python3
"""
Privacy Monitoring Script - Verify no raw user data in learning logs

This script audits the learning log files to ensure:
1. No raw user_input is stored (only signals/gates)
2. No AI response content is stored
3. User IDs are hashed
4. Only derived metadata is present

Implements Gate-Based Data Masking (Option A)
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple


class PrivacyMonitor:
    """Monitor learning logs for privacy compliance."""

    def __init__(self, log_path: str = "learning/hybrid_learning_log.jsonl"):
        self.log_path = Path(log_path)
        self.violations = []
        self.safe_entries = 0
        self.total_entries = 0

        # Common indicators of raw user data
        self.privacy_risk_keywords = {
            "struggling",
            "depression",
            "anxiety",
            "trauma",
            "abuse",
            "pain",
            "grief",
            "loss",
            "shame",
            "fear",
            "suicidal",
            "hurt",
            "broken",
            "relationship",
            "mother",
            "father",
            "friend",
            "boss",
            "divorce",
            "cancer",
            "hospital",
            "medicine",
            "therapy",
            "therapy",
            "session",
            "personal",
            "secret",
            "private",
            "shame",
            "embarrass",
        }

    def audit_log(self) -> Dict:
        """Audit the learning log for privacy issues."""
        if not self.log_path.exists():
            return {"status": "log_not_found", "path": str(self.log_path), "message": "Learning log file not found"}

        print(f"\n📋 PRIVACY AUDIT: {self.log_path}")
        print("=" * 80)

        try:
            with open(self.log_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line)
                        self.total_entries += 1
                        self._check_entry(entry, line_num)
                    except json.JSONDecodeError:
                        self.violations.append({"line": line_num, "issue": "Invalid JSON", "severity": "high"})
        except Exception as e:
            return {"status": "error", "error": str(e)}

        return self._generate_report()

    def _check_entry(self, entry: Dict, line_num: int) -> None:
        """Check a single log entry for privacy violations."""
        violations_in_entry = []

        # Check for raw user_input
        if "user_input" in entry and entry["user_input"]:
            violations_in_entry.append(
                {
                    "line": line_num,
                    "issue": "Raw user_input present (PRIVACY VIOLATION)",
                    "severity": "critical",
                    "field": "user_input",
                }
            )

        # Check for ai_response content
        if "ai_response" in entry and entry["ai_response"]:
            violations_in_entry.append(
                {
                    "line": line_num,
                    "issue": "AI response content present (PRIVACY VIOLATION)",
                    "severity": "critical",
                    "field": "ai_response",
                }
            )

        # Check for unhashed user_id (vs user_id_hash)
        if "user_id" in entry and not entry.get("user_id_hash"):
            # user_id should be user_id_hash (hashed)
            user_id = entry.get("user_id", "")
            if len(user_id) < 30 or not all(c in "0123456789abcdef" for c in user_id.lower()):
                # Looks unhashed (too short or not hex)
                violations_in_entry.append(
                    {"line": line_num, "issue": "User ID may not be hashed", "severity": "high", "field": "user_id"}
                )

        # Check for risk keywords in any string field
        entry_str = json.dumps(entry).lower()
        for keyword in self.privacy_risk_keywords:
            if keyword in entry_str and "signals" not in entry_str:
                violations_in_entry.append(
                    {"line": line_num, "issue": f"Privacy risk keyword '{keyword}' found", "severity": "medium"}
                )
                break  # Only report once per entry

        if violations_in_entry:
            self.violations.extend(violations_in_entry)
        else:
            self.safe_entries += 1

    def _generate_report(self) -> Dict:
        """Generate privacy audit report."""
        report = {
            "total_entries_checked": self.total_entries,
            "safe_entries": self.safe_entries,
            "violations_found": len(self.violations),
            "compliance_percentage": (self.safe_entries / self.total_entries * 100) if self.total_entries > 0 else 0,
            "status": "compliant" if not self.violations else "violations_found",
        }

        print(f"\n✅ Total entries: {self.total_entries}")
        print(f"✅ Safe entries: {self.safe_entries}")
        print(f"❌ Violations: {len(self.violations)}")
        print(f"📊 Compliance: {report['compliance_percentage']:.1f}%")

        if self.violations:
            print("\n⚠️  VIOLATIONS FOUND:")
            print("-" * 80)
            for v in self.violations[:10]:  # Show first 10
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(v.get("severity"), "⚪")
                print(f"{severity_emoji} Line {v['line']}: {v['issue']}")
            if len(self.violations) > 10:
                print(f"\n... and {len(self.violations) - 10} more violations")
        else:
            print("\n✅ NO PRIVACY VIOLATIONS FOUND")
            print("✅ Log is compliant with Option A (Gate-Based Data Masking)")

        return report

    def check_entry_format(self) -> Dict:
        """Show example of compliant entry format."""
        print("\n" + "=" * 80)
        print("📋 COMPLIANT ENTRY FORMAT (Option A - Gate-Based Data Masking):")
        print("=" * 80)

        compliant_entry = {
            "timestamp": "2025-11-03T15:30:45.123456",
            "user_id_hash": "a1b2c3d4e5f6g7h8",  # ✓ Hashed, not raw
            "signals": ["struggle", "depression"],  # ✓ Signals only
            "gates": ["Gate 4", "Gate 6"],  # ✓ Gate indices
            "glyph_names": ["Recursive Grief", "Pattern Recognition"],  # ✓ Metadata
            "ai_response_length": 245,  # ✓ Meta, not content
            "exchange_quality": "logged",  # ✓ Quality indicator
            # ✗ NO "user_input"
            # ✗ NO "ai_response"
        }

        print(json.dumps(compliant_entry, indent=2))

        return compliant_entry


def verify_privacy():
    """Run full privacy verification."""
    monitor = PrivacyMonitor()

    # Run audit
    report = monitor.audit_log()

    # Show compliant format
    monitor.check_entry_format()

    # Summary
    print("\n" + "=" * 80)
    print("📌 SUMMARY")
    print("=" * 80)
    print(f"\nStatus: {report.get('status', 'unknown')}")
    print(f"Compliance: {report.get('compliance_percentage', 0):.1f}%")

    if report.get("status") == "compliant":
        print("\n✅ Your learning logs are PRIVACY-SAFE")
        print("✅ No raw user data is being stored")
        print("✅ Option A (Gate-Based Data Masking) is working correctly")
    else:
        print("\n⚠️  Privacy issues detected - review violations above")

    return report


if __name__ == "__main__":
    verify_privacy()
