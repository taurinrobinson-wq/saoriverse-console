#!/usr/bin/env python3
"""
Glyph Consolidation Script - Remove redundancy and rebalance gates

Refactored into a module with `main()` so root-level compatibility stubs
can import and call the implementation from `tools/`.
"""

import re
import sqlite3
from collections import defaultdict


def consolidate_glyphs():
    conn = sqlite3.connect("emotional_os/glyphs/glyphs.db")
    cursor = conn.cursor()

    print("=== GLYPH CONSOLIDATION PROCESS ===")

    # Get all glyphs
    cursor.execute("SELECT id, glyph_name, description, gate FROM glyph_lexicon")
    all_glyphs = cursor.fetchall()
    print(f"Starting with {len(all_glyphs)} glyphs")

    # Step 1: Remove obvious document artifacts (non-emotional content)
    artifacts_to_remove = []
    valid_glyphs = []

    for glyph in all_glyphs:
        id, name, desc, gate = glyph

        # Identify document artifacts
        is_artifact = any(
            [
                # Chapter/Glyph numbering
                re.match(r"^(Chapter|Glyph) [IVX]+", name),
                re.match(r"^(Chapter|Glyph) \d+", name),
                # Technical terms
                "Protocol" in name and len(name) > 50,
                "Stabilization" in name and "chambers" in desc,
                # Conversation fragments
                "'s " in name or "re " in name or " is " in name,
                # Obviously not emotional states
                "Deployment" in name or "API" in name or "System" in name,
                "Conversation" in name or "Archive" in name or "Module" in name,
                "Pattern Detection" in name or "Integration" in name,
                # Very long technical descriptions
                len(desc) > 200
                and any(
                    word in desc.lower() for word in ["configuration", "implementation", "processing", "algorithm"]
                ),
                # Names that are clearly sentences
                len(name.split()) > 8,
            ]
        )

        if is_artifact:
            artifacts_to_remove.append(id)
        else:
            valid_glyphs.append(glyph)

    print(f"Identified {len(artifacts_to_remove)} artifacts to remove")

    # Step 2: Consolidate similar emotional glyphs
    consolidation_groups = {}

    # Group Recognition glyphs (keep 3 best)
    recognition_glyphs = [g for g in valid_glyphs if "recognition" in g[1].lower()]
    if len(recognition_glyphs) > 3:
        # Keep: basic recognition, grief recognition, joy recognition
        keep_recognition = ["Ache of Recognition", "Grief of Recognition", "Joy of Recognition"]
        for glyph in recognition_glyphs:
            if glyph[1] not in keep_recognition:
                artifacts_to_remove.append(glyph[0])

    # Group Recursive glyphs (keep 2 best per gate)
    recursive_glyphs = [g for g in valid_glyphs if "recursive" in g[1].lower()]
    recursive_by_gate = defaultdict(list)
    for glyph in recursive_glyphs:
        recursive_by_gate[glyph[3]].append(glyph)

    for gate, glyphs in recursive_by_gate.items():
        if len(glyphs) > 2:
            # Keep the first 2, remove others
            for glyph in glyphs[2:]:
                artifacts_to_remove.append(glyph[0])

    # Group Stillness glyphs (keep 3 best)
    stillness_glyphs = [g for g in valid_glyphs if "stillness" in g[1].lower()]
    if len(stillness_glyphs) > 3:
        keep_stillness = ["Grief in Stillness", "Joy in Stillness", "Spiral Stillness"]
        for glyph in stillness_glyphs:
            if glyph[1] not in keep_stillness:
                artifacts_to_remove.append(glyph[0])

    # Step 3: Execute removals
    artifacts_to_remove = list(set(artifacts_to_remove))  # Remove duplicates
    print(f"Total glyphs to remove: {len(artifacts_to_remove)}")

    if artifacts_to_remove:
        placeholders = ",".join(["?" for _ in artifacts_to_remove])
        cursor.execute(f"DELETE FROM glyph_lexicon WHERE id IN ({placeholders})", artifacts_to_remove)
        conn.commit()

    # Step 4: Verify results
    cursor.execute("SELECT COUNT(*) FROM glyph_lexicon")
    final_count = cursor.fetchone()[0]

    cursor.execute("SELECT gate, COUNT(*) FROM glyph_lexicon GROUP BY gate ORDER BY gate")
    gate_distribution = cursor.fetchall()

    print("\n=== CONSOLIDATION RESULTS ===")
    print(f"Glyphs removed: {len(all_glyphs) - final_count}")
    print(f"Final glyph count: {final_count}")
    print("\nNew gate distribution:")
    for gate, count in gate_distribution:
        percentage = (count / final_count) * 100
        print(f"  {gate}: {count} glyphs ({percentage:.1f}%)")

    conn.close()

    # Step 5: Update signal parser and other system files
    print("\n=== UPDATING SYSTEM FILES ===")
    update_system_references(final_count)


def update_system_references(new_count):
    """Update any hardcoded glyph counts in the system"""

    # Update test files
    test_files = ["test_overwhelm_fix.py", "test_enhanced_system.py"]

    for file_path in test_files:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Update any total glyph count references
            content = re.sub(r"Total Available Glyphs: \d+", f"Total Available Glyphs: {new_count}", content)

            with open(file_path, "w") as f:
                f.write(content)

            print(f"Updated {file_path}")
        except FileNotFoundError:
            continue

    print("System files updated successfully")


def main():
    consolidate_glyphs()


if __name__ == "__main__":
    main()
