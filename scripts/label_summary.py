#!/usr/bin/env python3
"""
Count labels and print percentages and a 10-turn sample from the middle
of learning/imported_conversations/parsed_conversation_reclassified.json
"""
import json
from collections import Counter
from pathlib import Path
import sys

P = Path("learning/imported_conversations/parsed_conversation_reclassified.json")
if not P.exists():
    print("ERROR: reclassified file not found:", P)
    sys.exit(2)

with P.open(encoding="utf-8") as f:
    data = json.load(f)

msgs = data.get("messages", [])
total = len(msgs)
if total == 0:
    print("No messages found in file.")
    sys.exit(0)

counts = Counter((m.get("type") or "") for m in msgs)
print("Total turns:", total)
for label, cnt in counts.items():
    pct = cnt / total * 100
    print(f"{label}: {cnt} ({pct:.1f}%)")

if "ai" not in counts and "system" in counts:
    cnt = counts["system"]
    print(f"system: {cnt} ({cnt/total*100:.1f}%)")

start = max(0, total // 2 - 5)
end = min(total, start + 10)
print(f"\nShowing turns {start+1}..{end} (10-turn sample from middle):\n")
for i, m in enumerate(msgs[start:end], start=start+1):
    t = m.get("type")
    c = (m.get("content") or "").replace("\n", " ")[:400]
    print(f"{i:04d}. {t} — {c}")
