#!/usr/bin/env python3
"""Force a range of turns to a given label in the reclassified JSON.

Usage: python3 scripts/force_labels.py <start> <end> [label]
Example: python3 scripts/force_labels.py 4 11 user
"""
import json
import sys
from pathlib import Path

P = Path("learning/imported_conversations/parsed_conversation_reclassified.json")
if not P.exists():
    print("ERROR: reclassified file not found:", P)
    sys.exit(2)

if len(sys.argv) < 3:
    print("Usage: force_labels.py <start> <end> [label]")
    sys.exit(2)

start = int(sys.argv[1])
end = int(sys.argv[2])
label = sys.argv[3] if len(sys.argv) > 3 else "user"

with P.open(encoding="utf-8") as f:
    data = json.load(f)

msgs = data.get("messages", [])
total = len(msgs)
if start < 1 or end < start or end > total:
    print(f"Index range out of bounds: 1..{total} (you passed {start}..{end})")
    sys.exit(2)

for i in range(start - 1, end):
    msgs[i]["type"] = label

data["messages"] = msgs
with P.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Forced turns {start}..{end} to label '{label}' in {P}")
