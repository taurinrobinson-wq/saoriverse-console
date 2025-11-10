#!/usr/bin/env python3
"""
Safe runner: ensure repo root on PYTHONPATH before importing learner.
"""
from learning.lexicon_learner import learn_from_conversation_data, get_learning_insights
import json
import sys
from pathlib import Path

# Ensure repo root on sys.path so imports resolve when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path.cwd()))


IN = Path("learning/imported_conversations/parsed_conversation_reclassified.json")
OUT = Path("learning/imported_conversations/learning_results.json")

if not IN.exists():
    print("ERROR: reclassified parsed conversation not found:", IN)
    raise SystemExit(2)

with IN.open(encoding="utf-8") as f:
    convo = json.load(f)

print("Running learner on:", IN)
results = learn_from_conversation_data(convo)

OUT.write_text(json.dumps(results, ensure_ascii=False,
               indent=2), encoding="utf-8")
print("WROTE:", OUT)

insights = get_learning_insights()
print("Learning insights:")
print(json.dumps(insights, ensure_ascii=False, indent=2))
