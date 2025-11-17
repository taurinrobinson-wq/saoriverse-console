#!/usr/bin/env python3
"""Query the clarification memory to suggest corrected intents for an input.

Usage:
  python3 tools/apply_clarification_bias.py --input "how are you" --min-count 1

This prints a JSON suggestion if any and returns exit code 0.
"""
import argparse
import json
from pathlib import Path
from learning.clarification_memory import suggest_for_input


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--min-count', type=int, default=1)
    args = p.parse_args()

    suggestion = suggest_for_input(args.input, min_count=args.min_count)
    print(json.dumps({'input': args.input,
          'suggestion': suggestion}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
