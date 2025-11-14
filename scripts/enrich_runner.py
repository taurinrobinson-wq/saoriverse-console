#!/usr/bin/env python3
import subprocess
import sys


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

    print('Enrichment pipeline complete. Synonyms refreshed in data/synonyms.db.')


if __name__ == '__main__':
    run_enrichment()
