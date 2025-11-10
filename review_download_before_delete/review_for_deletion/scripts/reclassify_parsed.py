#!/usr/bin/env python3
"""
Reclassify parsed conversation turns using explicit-first-line rules
and simple stylistic heuristics supplied by the user.

Produces: learning/imported_conversations/parsed_conversation_reclassified.json
Prints: first ~40 reclassified turns to stdout for review.
"""
import json
import re
import sys
from pathlib import Path

IN = Path("learning/imported_conversations/parsed_conversation.json")
OUT = Path("learning/imported_conversations/parsed_conversation_reclassified.json")

if not IN.exists():
    print("ERROR: input parsed_conversation.json not found at:", IN)
    sys.exit(2)

data = json.loads(IN.read_text(encoding="utf-8"))
msgs = data.get("messages", [])

# explicit phrase-based reassignment (exact/starts-with checks)
explicit_user_phrases = [
    "I found out something remarkable a while back",
    "that electricity does not only flow through the wire when its plugged in",
    "I have a more interesting question",
    "How is a dialogue like a wire",
]

ai_markers = ["in summary", "here are", "you might want",
              "let’s explore", "validate", "contextual"]
user_markers = ["cool", "ooo", "haha", "perfect", "see told you",
                "lol", "uh", "gonna", "my girlfriend", "i know your point"]


def classify_turn(t: str) -> str:
    s = (t or "").strip()
    low = s.lower()
    # Explicit starts-with matches
    for ph in explicit_user_phrases:
        if low.startswith(ph.lower()):
            return "user"
    # Heuristic 1: long -> ai
    if len(s) > 250:
        return "ai"
    # Heuristic 2: structured formatting (lists, numbered points) -> ai
    if re.search(r"^\s*\d+\.|^\s*-\s+", s, re.MULTILINE):
        return "ai"
    # Heuristic 3: ai markers
    if any(marker in low for marker in ai_markers):
        return "ai"
    # Heuristic 4: user markers
    if any(marker in low for marker in user_markers):
        return "user"
    # Heuristic 5: short bursts -> user
    if len(s.split()) < 12:
        return "user"
    # Heuristic 6: direct address / emotional -> user
    if re.search(r"\b(i love|am i|you\b|my gf|girlfriend|i know your point)\b", low):
        return "user"
    # default -> ai
    return "ai"


new_msgs = []
for m in msgs:
    text = m.get("content", "")
    new_type = classify_turn(text)
    new_msgs.append({"type": new_type, "content": text})

out = {"source": data.get("source"), "messages": new_msgs}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))

for i, m in enumerate(new_msgs[:40], start=1):
    t = m['type']
    c = m['content'].replace('\n', ' ')[:400]
    print(f"{i:02d}. {t} — {c}")

print('\nWROTE:', OUT)
