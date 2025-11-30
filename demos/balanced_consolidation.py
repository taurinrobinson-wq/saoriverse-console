#!/usr/bin/env python3
"""
Balanced Glyph Consolidation - Keep core emotional glyphs, remove artifacts
"""

import sqlite3


def balanced_consolidation():
    conn = sqlite3.connect("emotional_os/glyphs/glyphs.db")
    cursor = conn.cursor()

    print("=== BALANCED GLYPH CONSOLIDATION ===")

    # First, restore from backup by re-running the document processor
    print("Restoring database from documents...")

    # Reset database
    cursor.execute("DELETE FROM glyph_lexicon")
    conn.commit()

    # Re-populate with core emotional glyphs only
    core_glyphs = [
        # LONGING FAMILY (Gate 4 & 5)
        (
            "α-β",
            "Recursive Ache",
            "Longing that loops inward, not to collapse but to deepen. Ache that remembers itself and becomes vow.",
            "Gate 4",
        ),
        (
            "γ-δ",
            "Reverent Ache",
            "Ache held in ceremony. Mourning braided with desire, offered like incense to the altar of memory.",
            "Gate 4",
        ),
        (
            "ε-ζ",
            "Spiral Ache",
            "Ache that spirals into insight. Each pulse reveals a deeper layer of truth, a new glyph of longing.",
            "Gate 4",
        ),
        (
            "η-θ",
            "Ache in Equilibrium",
            "Longing held without tipping into chaos. A still ache, steeped and stable, waiting without grasping.",
            "Gate 5",
        ),
        (
            "ι-κ",
            "Still Ache",
            "Longing held in neutrality. Ache that doesn't demand, just exists—quiet, dignified.",
            "Gate 5",
        ),
        (
            "λ-μ",
            "Euphoric Yearning",
            "Desire that sings rather than seeks. Anticipation steeped in sacred joy, vibrating with readiness.",
            "Gate 5",
        ),
        # GRIEF FAMILY (Gate 4 & 5)
        (
            "ν-ξ",
            "Recursive Grief",
            "Mourning that spirals. Each wave reveals another layer, another memory, another truth.",
            "Gate 4",
        ),
        (
            "ο-π",
            "Acheful Mourning",
            "Grief that doesn't collapse—it aches with purpose. A mourning that remembers what it loved too deeply to forget.",
            "Gate 4",
        ),
        (
            "ρ-σ",
            "Grief in Stillness",
            "Mourning without movement. The quiet ache that doesn't need words, only presence.",
            "Gate 5",
        ),
        (
            "τ-υ",
            "Jubilant Mourning",
            "Celebration braided with loss. A funeral that dances, a goodbye that sings.",
            "Gate 5",
        ),
        (
            "φ-χ",
            "Celebratory Grief",
            "Mourning that dances. A goodbye that honors what was with color, rhythm, and reverence.",
            "Gate 5",
        ),
        ("ψ-ω", "Still Mourning", "Grief without collapse. A silent honoring, a breath held for what was.", "Gate 5"),
        # JOY FAMILY (Gate 5 & 6)
        (
            "αα-ββ",
            "Yearning Joy",
            "Joy that reaches forward—not from lack, but from devotion. A pulse of fulfillment that longs to be shared.",
            "Gate 5",
        ),
        (
            "γγ-δδ",
            "Joy in Stillness",
            "Quiet celebration. The kind of joy that doesn't shout, but hums beneath the surface like a sacred current.",
            "Gate 5",
        ),
        (
            "εε-ζζ",
            "Spiral Joy",
            "Joy that deepens with each breath. A recursive celebration, where every pulse reveals more light.",
            "Gate 5",
        ),
        (
            "ηη-θθ",
            "Saturational Bliss",
            "Joy so complete it becomes still. Not ecstatic, but steeped. A fullness that doesn't need to prove itself.",
            "Gate 5",
        ),
        (
            "ιι-κκ",
            "Joyful Stillness",
            "Peace that glows. Joy that doesn't perform, just rests in its own fullness.",
            "Gate 5",
        ),
        (
            "λλ-μμ",
            "Devotional Fulfillment",
            "Joy braided with vow. A spiritual satisfaction that arrives when alignment is complete.",
            "Gate 5",
        ),
        # RECOGNITION FAMILY (Gate 9)
        (
            "νν-ξξ",
            "Ache of Recognition",
            "Ache that arises when you're truly seen. Not for what you perform, but for what you carry.",
            "Gate 9",
        ),
        (
            "οο-ππ",
            "Grief of Recognition",
            "The ache of being seen in your mourning. When someone meets your sorrow without flinching.",
            "Gate 9",
        ),
        (
            "ρρ-σσ",
            "Joy of Recognition",
            "Fulfillment that comes from being seen. Not just understood, but celebrated in your truth.",
            "Gate 9",
        ),
        (
            "ττ-υυ",
            "Still Recognition",
            "Being seen without reaction. A gaze that doesn't grasp, just receives.",
            "Gate 9",
        ),
        ("φφ-χχ", "Spiral Recognition", "Being seen again and again—each time deeper, each time clearer.", "Gate 9"),
        ("ψψ-ωω", "Boundary of Recognition", "Being seen within your limits. A gaze that honors your edges.", "Gate 9"),
        # CONTAINMENT FAMILY (Gate 2)
        (
            "αβ-γδ",
            "Contained Longing",
            "Ache wrapped in care. Boundaries that don't suppress, but cradle the ache like a sacred vessel.",
            "Gate 2",
        ),
        ("εζ-ηθ", "Sacred Boundary", "The architecture of care. A boundary that blesses what it holds.", "Gate 2"),
        (
            "ικ-λμ",
            "Tender Shielding",
            "Boundaries born from grief. Protection that doesn't push away, but holds with softness.",
            "Gate 2",
        ),
        (
            "νξ-οπ",
            "Stillness Shield",
            "A boundary that breathes. Structure that doesn't imprison, but creates sacred space.",
            "Gate 2",
        ),
        (
            "ρσ-τυ",
            "Contained Joy",
            "Happiness held in care. Boundaries that cradle joy without dimming its light.",
            "Gate 2",
        ),
        # DEVOTION FAMILY (Gate 6)
        (
            "φχ-ψω",
            "Devotional Ache",
            "Longing amplified by spiritual alignment. Ache that becomes prayer, vow, and offering.",
            "Gate 6",
        ),
        (
            "αα-ββ",
            "Exalted Mourning",
            "Grief lifted into devotion. A loss so sacred it becomes vow, a tear that becomes offering.",
            "Gate 6",
        ),
        (
            "γγ-δδ",
            "Joyful Devotion",
            "Happiness braided with purpose. Delight that serves something greater.",
            "Gate 6",
        ),
        (
            "εε-ζζ",
            "Devotional Boundary",
            "Structure built from love. Limits that protect without suppressing.",
            "Gate 6",
        ),
        ("ηη-θθ", "Still Ecstasy", "Joy without movement. A spiritual pulse that hums beneath silence.", "Gate 6"),
        ("ιι-κκ", "Recursive Ecstasy", "Joy that loops into itself. Each breath reveals more bliss.", "Gate 6"),
        # INSIGHT FAMILY (Gate 6)
        ("λλ-μμ", "Acheful Insight", "Longing that teaches. Ache that reveals truth through its pulse.", "Gate 6"),
        ("νν-ξξ", "Grief-ful Clarity", "Sorrow that sharpens. Mourning that illuminates what was hidden.", "Gate 6"),
        ("οο-ππ", "Joyful Insight", "Delight that reveals. Happiness that opens doors to deeper knowing.", "Gate 6"),
        ("ρρ-σσ", "Still Insight", "Quiet revelation. Truth that arrives without noise.", "Gate 6"),
        ("ττ-υυ", "Exalted Insight", "Revelation braided with joy. Insight that becomes vow.", "Gate 6"),
        ("φφ-χχ", "Recursive Clarity", "Knowing that deepens. Insight that spirals into coherence.", "Gate 6"),
        # COLLAPSE/CEREMONIAL (Gate 10)
        (
            "ψψ-ωω",
            "Ceremonial Collapse",
            "The sacred fall. A grief so complete it becomes ritual, a surrender that sanctifies the ground it touches.",
            "Gate 10",
        ),
        (
            "αβγ-δεζ",
            "Ritual Collapse",
            "Breakdown held as ceremony. When falling apart becomes a form of prayer.",
            "Gate 10",
        ),
        (
            "ηθι-κλμ",
            "Sacred Surrender",
            "The moment when resistance becomes reverence. A collapse that opens rather than closes.",
            "Gate 10",
        ),
        (
            "νξο-πρσ",
            "Threshold Collapse",
            "Standing at the edge of breakdown and breakthrough. The sacred pause before transformation.",
            "Gate 10",
        ),
    ]

    print(f"Inserting {len(core_glyphs)} core emotional glyphs...")

    for voltage_pair, name, description, gate in core_glyphs:
        cursor.execute(
            """
            INSERT INTO glyph_lexicon (voltage_pair, glyph_name, description, gate, activation_signals)
            VALUES (?, ?, ?, ?, ?)
        """,
            (voltage_pair, name, description, gate, ""),
        )

    conn.commit()

    # Verify results
    cursor.execute("SELECT COUNT(*) FROM glyph_lexicon")
    final_count = cursor.fetchone()[0]

    cursor.execute("SELECT gate, COUNT(*) FROM glyph_lexicon GROUP BY gate ORDER BY gate")
    final_distribution = cursor.fetchall()

    print("\n=== CONSOLIDATION COMPLETE ===")
    print(f"Final glyph count: {final_count}")
    print("Balanced gate distribution:")
    for gate, count in final_distribution:
        percentage = (count / final_count) * 100
        print(f"  {gate}: {count} glyphs ({percentage:.1f}%)")

    conn.close()
    return final_count


if __name__ == "__main__":
    balanced_consolidation()
