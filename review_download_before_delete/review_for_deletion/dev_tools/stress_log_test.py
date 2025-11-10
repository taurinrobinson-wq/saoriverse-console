"""
Multi-threaded stress test for glyph candidate logging and parse_input concurrency.
Usage: python3 dev_tools/stress_log_test.py
"""
import os
import sys
import threading
import time
import random
from collections import Counter

# ensure repo root on path
sys.path.insert(0, os.path.abspath('.'))

from emotional_os.glyphs import signal_parser as sp

SCENARIOS = [
    "I'm feeling very sad and alone today",
    "I feel anxious and overwhelmed right now",
    "I can't sleep and it makes me anxious",
    "I lost my job and I'm scared",
    "My partner ignored me and I'm angry",
    "This morning I woke up and everything felt heavy",
    "I had a weird dream last night",
    "I just want someone to listen without advice",
    "Tell me about yourself",
    "how are you doing",
    "I feel fine",
    "I can't stop thinking about them",
]

LEXICON_PATH = 'velonix_lexicon.json' if os.path.exists('velonix_lexicon.json') else 'emotional_os/glyphs/learned_lexicon.json'
DB_PATH = 'emotional_os/glyphs/glyphs.db' if os.path.exists('emotional_os/glyphs/glyphs.db') else 'glyphs.db'

THREADS = 20
ITERATIONS_PER_THREAD = 25

errors = []
responses = []
lock = threading.Lock()


def worker(thread_id: int):
    local_errors = 0
    for i in range(ITERATIONS_PER_THREAD):
        text = random.choice(SCENARIOS)
        try:
            rdict = sp.parse_input(text, LEXICON_PATH, db_path=DB_PATH, conversation_context=None)
            with lock:
                responses.append((thread_id, text, rdict.get('response_source'), bool(rdict.get('best_glyph'))))
        except Exception as e:
            local_errors += 1
            with lock:
                errors.append((thread_id, text, str(e)))
        # small jitter to increase interleaving
        time.sleep(random.random() * 0.02)
    if local_errors:
        with lock:
            errors.append((thread_id, 'thread_errors', local_errors))


def main():
    start = time.time()
    threads = []

    for t in range(THREADS):
        th = threading.Thread(target=worker, args=(t,))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    duration = time.time() - start

    print(f"Ran {THREADS} threads x {ITERATIONS_PER_THREAD} iterations = {THREADS*ITERATIONS_PER_THREAD} calls in {duration:.2f}s")

    if errors:
        print("Errors:")
        for e in errors[:20]:
            print(e)
    else:
        print("No exceptions captured in Python-level worker.")

    # Aggregate response_source counts
    src_counts = Counter()
    glyph_counts = 0
    for _, _, src, has_glyph in responses:
        src_counts[src] += 1
        if has_glyph:
            glyph_counts += 1

    print("response_source counts:")
    for k, v in src_counts.most_common():
        print(f"  {k}: {v}")
    print(f"Responses that matched a glyph (best_glyph present): {glyph_counts} / {len(responses)}")

    # Print a few sample responses
    print("Sample responses (first 10):")
    for r in responses[:10]:
        print(r)

    # Exit code
    if errors:
        sys.exit(2)
    print('Stress test completed successfully.')


if __name__ == '__main__':
    main()
