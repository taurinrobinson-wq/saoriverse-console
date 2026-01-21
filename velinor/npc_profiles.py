"""NPC profiles for Velinor micro-loop prototype.

Minimal character skins that give narrative context to the decoding mechanic
without committing to full worldbuilding. These are sensory frames that help
players *feel* the emotional gating in action.
"""

NPCS = {
    "tala": {
        "name": "Tala",
        "title": "Market Cook",
        "voice": "warm, practical, grounded",
        "intro": "Tala wipes her hands on her apron and leans in.",
        "locked": "Tala hesitates, as if the words are there but not ready.",
        "fragment": "Tala shares a piece of something she half-remembers.",
        "reveal": "Tala exhales, letting the truth surface.",
    },
    "saori": {
        "name": "Saori",
        "title": "Warden of Quiet Bloom",
        "voice": "soft, precise, emotionally attuned",
        "intro": "Saori studies you with a patient stillness.",
        "locked": "Saori closes her eyes, withholding the deeper meaning.",
        "fragment": "Saori offers a fragment, delicate as breath.",
        "reveal": "Saori opens her guard and lets the truth unfold.",
    },
    "archivist": {
        "name": "The Archivist",
        "title": "Keeper of Fractured Memory",
        "voice": "measured, distant, analytical",
        "intro": "The Archivist adjusts a cracked lens and regards you.",
        "locked": "The Archivist shakes his head — the memory remains sealed.",
        "fragment": "The Archivist retrieves a partial record.",
        "reveal": "The Archivist unlocks the full memory with a quiet click.",
    },
    "echo": {
        "name": "Echo",
        "title": "Mirror of Names",
        "voice": "ethereal, recursive, remembering",
        "intro": "Echo regards you with eyes that seem to know you already.",
        "locked": "Echo falls silent, holding the words just beyond reach.",
        "fragment": "Echo whispers something half-forgotten.",
        "reveal": "Echo speaks the truth as if you'd always known it.",
    },
}


def get_npc(key: str) -> dict:
    """Get NPC profile by key, with fallback to Tala."""
    return NPCS.get(key.lower(), NPCS["tala"])


def list_npcs() -> list:
    """Return list of (key, NPC dict) tuples."""
    return [(k, v) for k, v in NPCS.items()]
