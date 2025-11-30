#!/usr/bin/env python3
"""Run a threshold sweep over 0.65-0.85 and summarize tag counts.

Usage: python3 scripts/threshold_sweep.py

Reads `data/tagging_samples.csv` and calls `symbolic_tagger.tag_input_with_diagnostics`
for each threshold. Prints a table of counts per tag per threshold.
"""
import csv
import importlib.util
import json
import os as _os
import sys
from collections import OrderedDict, defaultdict

# Resolve repo root relative to this script file so imports work regardless
# of the current working directory used to invoke the script.
script_dir = _os.path.dirname(_os.path.abspath(__file__))
repo_root = _os.path.abspath(_os.path.join(script_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import the local module by file path to avoid issues with PYTHONPATH
symbolic_path = _os.path.join(repo_root, "symbolic_tagger.py")
spec = importlib.util.spec_from_file_location("symbolic_tagger", symbolic_path)
symbolic_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(symbolic_mod)
tag_input_with_diagnostics = symbolic_mod.tag_input_with_diagnostics

CSV_PATH = _os.path.join(repo_root, "data", "tagging_samples.csv")

# thresholds from 0.65 to 0.85 inclusive step 0.02
thresholds = [round(x, 2) for x in [0.65 + i * 0.02 for i in range(int((0.85 - 0.65) / 0.02) + 1)]]

inputs = []
with open(CSV_PATH, newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        # CSV has header 'input' in first column
        inputs.append(r["input"].strip())

# Collect dynamic set of tags across all thresholds
all_tags = set()
results = OrderedDict()
for t in thresholds:
    counts = defaultdict(int)
    for text in inputs:
        res = tag_input_with_diagnostics(text, fuzzy_thresh=t)
        tags = res.get("tags", [])
        for tag in tags:
            counts[tag] += 1
            all_tags.add(tag)
    results[t] = counts

# Sort tags for consistent columns (prefer canonical ordering)
preferred = ["initiatory_signal", "anchoring_signal", "voltage_surge", "containment_request", "legacy_marker"]
other_tags = sorted(list(all_tags - set(preferred)))
columns = [t for t in preferred if t in all_tags] + other_tags

# Print CSV-like table
print("threshold," + ",".join(columns))
for t, counts in results.items():
    row = [str(t)] + [str(counts.get(c, 0)) for c in columns]
    print(",".join(row))

# Also print a brief human-readable summary
print("\nSummary (threshold -> tag counts):")
for t, counts in results.items():
    print(f"{t}: {dict(counts)}")

# Save results to JSON for inspection
out = {"thresholds": {}, "columns": columns}
for t, counts in results.items():
    out["thresholds"][str(t)] = {c: counts.get(c, 0) for c in columns}
with open("data/threshold_sweep_summary.json", "w", encoding="utf-8") as of:
    json.dump(out, of, indent=2)

print("\nWrote JSON summary to data/threshold_sweep_summary.json")
