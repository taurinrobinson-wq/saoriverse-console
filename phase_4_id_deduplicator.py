"""
Phase 4: ID DEDUPLICATION FIX
=============================

Remove duplicate IDs from system while preserving all glyph data.
Issue occurred in Phase 1 factorial generation where factorial combinations
were created but may have received non-unique IDs.

Solution: Keep unique glyphs and reassign IDs to ensure 1:1 mapping.
"""

import json
from collections import defaultdict


class IDDeduplicator:
    """Fix duplicate IDs in production system."""

    SYSTEM_JSON = "/workspaces/saoriverse-console/emotional_os/glyphs/glyph_lexicon_rows.json"
    BACKUP_PATH = "/workspaces/saoriverse-console/glyph_lexicon_rows_before_dedup.json"

    def __init__(self):
        """Initialize deduplicator."""
        self.glyphs = []
        self.unique_glyphs = []
        self.fix_results = {
            "original_count": 0,
            "unique_count": 0,
            "duplicates_removed": 0,
            "id_conflicts_resolved": 0,
        }

    def load_system(self) -> bool:
        """Load production system."""
        print("\n📖 Loading system for deduplication...")
        try:
            with open(self.SYSTEM_JSON, "r") as f:
                data = json.load(f)

            if isinstance(data, dict) and "glyphs" in data:
                self.glyphs = data["glyphs"]
            else:
                self.glyphs = data if isinstance(data, list) else []

            self.fix_results["original_count"] = len(self.glyphs)
            print(f"   ✅ Loaded {len(self.glyphs)} glyphs")
            return True
        except Exception as e:
            print(f"   ❌ Error loading: {e}")
            return False

    def create_backup(self):
        """Backup original system before deduplication."""
        print("\n💾 Creating backup...")
        import shutil

        shutil.copy(self.SYSTEM_JSON, self.BACKUP_PATH)
        print(f"   ✅ Backup created: {self.BACKUP_PATH}")

    def deduplicate_by_content(self) -> list:
        """Remove duplicate glyphs by content hash."""
        print("\n🔍 Deduplicating by content...")

        seen_hashes = {}
        unique_glyphs = []
        duplicates_removed = 0

        for glyph in self.glyphs:
            # Create content hash (ignore ID field)
            content = {k: v for k, v in glyph.items() if k != "id"}
            content_hash = json.dumps(content, sort_keys=True)

            if content_hash not in seen_hashes:
                seen_hashes[content_hash] = glyph
                unique_glyphs.append(glyph)
            else:
                duplicates_removed += 1

        self.fix_results["duplicates_removed"] = duplicates_removed
        print(f"   ✅ Removed {duplicates_removed} duplicate glyphs by content")
        print(f"   ✅ Remaining: {len(unique_glyphs)} unique glyphs")

        return unique_glyphs

    def reassign_ids(self, glyphs: list) -> list:
        """Reassign sequential IDs to ensure uniqueness."""
        print("\n🔧 Reassigning IDs...")

        new_start_id = 1  # Start from 1

        for idx, glyph in enumerate(glyphs):
            old_id = glyph.get("id", "unknown")
            new_id = new_start_id + idx
            glyph["id"] = new_id
            glyph["idx"] = idx

            if idx < 5 or idx >= len(glyphs) - 5:
                print(f"   Glyph {idx}: {old_id} → {new_id}")

        self.fix_results["id_conflicts_resolved"] = 1  # Fixed entire system
        print(f"   ✅ Assigned IDs from {new_start_id} to {new_start_id + len(glyphs) - 1}")

        return glyphs

    def verify_deduplication(self, glyphs: list) -> bool:
        """Verify deduplication was successful."""
        print("\n✅ Verifying deduplication...")

        ids = [g.get("id") for g in glyphs]
        gates = [g.get("gate", "") for g in glyphs]

        # Check ID uniqueness
        id_duplicates = len(ids) - len(set(ids))
        if id_duplicates > 0:
            print(f"   ❌ Still have {id_duplicates} duplicate IDs")
            return False
        print(f"   ✅ All {len(ids)} IDs are unique")

        # Check gate coverage
        gates_present = set()
        for gate_str in gates:
            try:
                gate_num = int(gate_str.split()[-1])
                gates_present.add(gate_num)
            except (ValueError, IndexError):
                pass

        if len(gates_present) < 12:
            print(f"   ⚠️  Only {len(gates_present)}/12 gates present")
        else:
            print(f"   ✅ All 12 gates present")

        return True

    def save_deduplicated_system(self, glyphs: list):
        """Save deduplicated system."""
        print("\n💾 Saving deduplicated system...")

        output = {"glyphs": glyphs}

        with open(self.SYSTEM_JSON, "w") as f:
            json.dump(output, f, indent=2)

        self.fix_results["unique_count"] = len(glyphs)
        print(f"   ✅ Saved {len(glyphs)} unique glyphs")

    def execute_deduplication(self) -> dict:
        """Execute full deduplication process."""
        print("\n" + "=" * 80)
        print("PHASE 4: ID DEDUPLICATION FIX")
        print("=" * 80)

        # Load system
        if not self.load_system():
            return self.fix_results

        # Create backup
        self.create_backup()

        # Deduplicate
        unique_glyphs = self.deduplicate_by_content()

        # Reassign IDs
        fixed_glyphs = self.reassign_ids(unique_glyphs)

        # Verify
        if not self.verify_deduplication(fixed_glyphs):
            print("\n⚠️  Verification failed - aborting save")
            return self.fix_results

        # Save
        self.save_deduplicated_system(fixed_glyphs)

        # Report
        print("\n" + "=" * 80)
        print("DEDUPLICATION COMPLETE")
        print("=" * 80)
        print(f"\nResults:")
        print(f"  Original: {self.fix_results['original_count']} glyphs")
        print(f"  Removed: {self.fix_results['duplicates_removed']} duplicates")
        print(f"  Final: {self.fix_results['unique_count']} glyphs")
        print(
            f"  Reduction: {self.fix_results['duplicates_removed']} glyphs (-{100*self.fix_results['duplicates_removed']/self.fix_results['original_count']:.1f}%)"
        )

        print("\n✨ System deduplicated and ready for retesting")
        print("=" * 80)

        return self.fix_results


def main():
    """Execute ID deduplication."""
    print("\n" + "🌟" * 40)
    print("PHASE 4: ID DEDUPLICATION")
    print("🌟" * 40)

    deduplicator = IDDeduplicator()
    deduplicator.execute_deduplication()


if __name__ == "__main__":
    main()
