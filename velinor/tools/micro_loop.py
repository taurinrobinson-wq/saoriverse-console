#!/usr/bin/env python3
"""Velinor Glyph Cipher Interactive Tutorial

This is the first playable experience of Velinor's emotional gating system.

The player speaks to an NPC who holds glyph knowledge. Their emotional state
is parsed in real-time. If aligned with the glyph's emotional requirements,
they unlock the truth. Otherwise, they see only fragments.

This tutorial demonstrates how glyphs are mechanically manifested in the game.

Run: python velinor/micro_loop.py
"""

from velinor.glyph_cipher_engine import get_engine


def pick_npc(engine) -> str:
    """Choose an NPC to learn from."""
    npcs_with_glyphs = {}
    
    print("\n✨ NPCs Who Hold Glyphs:")
    print("─" * 60)
    
    npc_list = [
        ("Malrik", "Archivist — Memory & Institutional Collapse"),
        ("Elenya", "High Seer — Joy, Trust, Sacred Presence"),
        ("Veynar", "Captain — Sovereignty, Fractured Authority"),
        ("Dalen", "Guide — Ache, Reckless Trial"),
        ("Ravi", "Father — Legacy, Loss, Witnessing"),
        ("Nima", "Survivor — Ache, Sorrow"),
        ("Kaelen", "Thief — Trust, Hidden Passage, Apprehension"),
        ("Sera", "Herb Novice — Joy, Presence, Care"),
        ("Mariel", "Weaver — Ache, Legacy, Binding"),
        ("Tala", "Market Cook — Joy, Shared Feast"),
    ]
    
    for i, (name, desc) in enumerate(npc_list, 1):
        print(f"   {i}. {desc}")
        glyphs = engine.get_glyphs_by_npc(name)
        print(f"      └─ {len(glyphs)} glyphs to explore")
        npcs_with_glyphs[str(i)] = name
    
    print()
    while True:
        choice = input("Choose NPC (1-10, or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return None
        if choice in npcs_with_glyphs:
            return npcs_with_glyphs[choice]
        print("   Invalid choice. Try again.")


def pick_glyph(engine, npc_name) -> dict:
    """Choose a glyph from the NPC's collection."""
    glyphs = engine.get_glyphs_by_npc(npc_name)
    
    if not glyphs:
        print(f"\n❌ {npc_name} has no glyphs (this shouldn't happen)")
        return None
    
    print(f"\n📖 {npc_name}'s Glyphs:")
    print("─" * 60)
    
    for i, glyph in enumerate(glyphs, 1):
        print(f"   {i}. [{glyph.category:11}] {glyph.glyph_name}")
        print(f"      └─ {glyph.location}")
    
    print()
    while True:
        choice = input(f"Choose glyph (1-{len(glyphs)}, or 'b' back): ").strip()
        if choice.lower() == 'b':
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(glyphs):
                return glyphs[idx]
        except ValueError:
            pass
        print("   Invalid choice. Try again.")


def format_glyph_response(npc_name, glyph, response) -> str:
    """Format the glyph unlock response for display."""
    access = response.get("access", "locked")
    text = response.get("text", "")
    gates = response.get("required_gates", [])
    
    lines = []
    lines.append(f"\n✨ {npc_name} speaks:")
    lines.append("─" * 60)
    lines.append(f"\n{text}\n")
    
    if access == "locked":
        gates_str = ", ".join(gates) if gates else "unknown emotions"
        lines.append(f"🔒 [Locked] — Requires emotional alignment: {gates_str}")
    elif access == "fragment":
        lines.append(f"🟦 [Fragment] — A glimpse, but not the full truth")
    elif access == "plaintext":
        lines.append(f"🟩 [Plaintext] — The emotional truth revealed")
    
    lines.append("─" * 60)
    
    return "\n".join(lines)


def main():
    """Run the interactive glyph cipher tutorial."""
    engine = get_engine()
    
    print("\n" + "=" * 60)
    print("🌒 Velinor: Glyph Cipher — Interactive Tutorial")
    print("=" * 60)
    print("\nThis is how glyphs manifest in Velinor.")
    print("Speak to an NPC. Show emotional alignment. Unlock their truth.\n")
    
    while True:
        # Pick NPC
        npc_name = pick_npc(engine)
        if not npc_name:
            print("\n👋 Goodbye.\n")
            break
        
        # Conversation loop with this NPC
        while True:
            # Pick glyph
            glyph = pick_glyph(engine, npc_name)
            if not glyph:
                break
            
            print(f"\n{glyph.glyph_name}")
            print(f"Location: {glyph.location}")
            print(f"Emotional Theme: {glyph.category}")
            print("\nSpeak to " + npc_name + " about this. Type messages, or 'back' to choose another glyph.\n")
            
            # Message loop for this glyph
            while True:
                msg = input("You: ").strip()
                
                if msg.lower() in ("back", "b"):
                    break
                
                if msg.lower() in ("exit", "quit", "q"):
                    print("\n👋 Goodbye.\n")
                    return
                
                if not msg:
                    continue
                
                # Unlock the glyph
                response = engine.unlock_glyph(glyph.id, msg)
                print(format_glyph_response(npc_name, glyph, response))
                print("\n(Type another message, 'back' for another glyph, or 'exit' to quit)\n")


if __name__ == "__main__":
    main()
