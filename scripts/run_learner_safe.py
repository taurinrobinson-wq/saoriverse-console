#!/usr/bin/env python3
"""
Run learner with explicit PYTHONPATH setup and debug output.
"""
import json
import sys
from pathlib import Path

# Add repo root and cwd to sys.path before any learning imports
repo_root = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, repo_root)
sys.path.insert(0, str(Path.cwd()))

print("DEBUG: repo_root=", repo_root)
print("DEBUG sys.path[0..4]:")
for p in sys.path[0:5]:
    print("  ", p)

try:
    from learning.lexicon_learner import learn_from_conversation_data, get_learning_insights
except Exception as e:
    print("IMPORT ERROR:", e)
    raise

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
