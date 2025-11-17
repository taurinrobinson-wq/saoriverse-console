#!/usr/bin/env python3
"""Detect user clarifications and record them to the clarification memory.

This tool is intended to be invoked with the previous (user, system) turn and the
current user message. If the current user message looks like a clarification, the
tool records the event into `learning/clarification_memory.jsonl`.

Example:
  python3 tools/clarification_detector.py \
    --prev-user "I was wondering do you ever dream?" \
    --prev-system "I'm a companion..." \
    --user "No I'm asking personally, do you dream" \
    --intent personal_question
"""
from pathlib import Path
import argparse
import re
from learning.clarification_memory import record_correction, _normalize_trigger


CLARIFICATION_PATTERNS = [
    r"^no[,\.!\s]",
    r"^actually[,\.!\s]",
    r"^not that",
    r"^i mean",
    r"^i meant",
    r"^sorry",
    r"^what i meant",
    r"^no i'm",
    r"^no i",
]


def looks_like_clarification(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    for p in CLARIFICATION_PATTERNS:
        if re.search(p, t):
            return True
    # also look for phrases starting with 'not', 'rather', 'instead'
    if t.startswith('not ') or t.startswith('rather ') or t.startswith('instead '):
        return True
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prev-user', required=True)
    p.add_argument('--prev-system', required=True)
    p.add_argument('--user', required=True)
    p.add_argument('--intent', default=None,
                   help='Optional corrected intent label')
    p.add_argument('--metadata', default=None, help='Optional JSON metadata')
    args = p.parse_args()

    prev_user = args.prev_user
    prev_system = args.prev_system
    user = args.user

    if looks_like_clarification(user):
        # Use normalized previous user message as trigger
        trigger = _normalize_trigger(prev_user)
        record_correction(trigger=trigger,
                          clarified_as=args.intent,
                          original_input=prev_user,
                          system_response=prev_system,
                          user_clarification=user,
                          metadata={'source': 'clarification_detector'})
        print('Recorded clarification for trigger:', trigger)
    else:
        print('No clarification detected.')


if __name__ == '__main__':
    main()
