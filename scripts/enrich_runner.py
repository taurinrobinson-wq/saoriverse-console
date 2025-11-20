#!/usr/bin/env python3
import subprocess
import sys
import json
import os
from datetime import datetime

LOG_PATH = "logs/enrich.log"


def run_step(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {cmd[0]}:\n{result.stderr}")
        return False
    else:
        if result.stdout:
            print(result.stdout)
        return True


def summarize_results(scored_path="data/synonyms_scored.json"):
    if not os.path.exists(scored_path):
        return None
    data = json.load(open(scored_path, "r", encoding="utf-8"))
    seeds = len(data)
    total_synonyms = sum(len(entry.get("synonyms_scored", []))
                         for entry in data.values())
    sample = {}
    for seed, entry in list(data.items())[:3]:  # show first 3 seeds
        sample[seed] = [s["word"]
                        for s in entry.get("synonyms_scored", [])[:3]]
    return {
        "seeds": seeds,
        "total_synonyms": total_synonyms,
        "sample": sample
    }


def log_summary(summary):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | Seeds={summary['seeds']} | "
                f"TotalSynonyms={summary['total_synonyms']} | Sample={summary['sample']}\n")


def run_enrichment():
    steps = [
        [sys.executable, 'scripts/local_synonyms.py'],
        [sys.executable, 'scripts/filter_synonyms.py'],
        [sys.executable, 'scripts/score_synonyms.py'],
        [sys.executable, 'scripts/synonym_db.py'],
    ]

    for cmd in steps:
        ok = run_step(cmd)
        if not ok:
            print('Aborting enrichment due to error.')
            return

    summary = summarize_results()
    if summary:
        print("\n=== Run Summary ===")
        print(f"Seeds processed: {summary['seeds']}")
        print(f"Total synonyms scored: {summary['total_synonyms']}")
        print(f"Sample (first 3 seeds): {summary['sample']}")
        log_summary(summary)

    print('\nEnrichment pipeline complete. Synonyms refreshed in data/synonyms.db.')


if __name__ == '__main__':
    run_enrichment()
