"""
Generate a CSV of top-selected glyphs across a conversation corpus.

Usage: python3 scripts/generate_top_glyphs_csv.py

Outputs: scripts/output/top_glyphs.csv

This script searches for conversation files in these locations (if present):
 - learning/imported_conversations/*.json
 - learning/processed_conversations/*.txt, *.json
 - conversations/*.json

It parses each file to extract user message texts, runs `parse_input()` on each message,
collects `glyphs_selected` occurrences, and writes a CSV with columns:
 glyph_name, display_name, count, avg_score, sample_inputs

Notes:
 - Processing is capped per file to avoid extremely long runs (default 200 messages/file).
 - If `glyphs_selected` is empty for a message, the script skips it.
"""

import csv
import glob
import json
import os
from collections import defaultdict

from emotional_os.core.signal_parser import parse_input

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, "emotional_os", "glyphs", "glyphs.db")
LEXICON_PATH = os.path.join(ROOT, "parser", "signal_lexicon.json")

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "top_glyphs.csv")

# File patterns to search for corpus
PATTERNS = [
    os.path.join(ROOT, "learning", "imported_conversations", "*.json"),
    os.path.join(ROOT, "learning", "processed_conversations", "*.*"),
    os.path.join(ROOT, "conversations", "*.json"),
    os.path.join(ROOT, "learning", "processed_conversations", "*.txt"),
]

# Limits
MAX_MESSAGES_PER_FILE = 200
TOTAL_MESSAGE_CAP = 2000

# Helper: extract texts from a file path (robust to formats)


def extract_texts_from_file(path):
    lower = path.lower()
    texts = []
    try:
        if lower.endswith(".txt"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Split by blank lines into message-like chunks
            parts = [p.strip() for p in content.split("\n\n") if p.strip()]
            texts.extend(parts[:MAX_MESSAGES_PER_FILE])
        elif lower.endswith(".json"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            # If it's a dict with conversation content
            if isinstance(data, dict):
                # Try known keys
                if "messages" in data and isinstance(data["messages"], list):
                    for m in data["messages"][:MAX_MESSAGES_PER_FILE]:
                        if isinstance(m, dict):
                            # common fields
                            for k in ("text", "content", "message", "input"):
                                if k in m and isinstance(m[k], str):
                                    texts.append(m[k])
                                    break
                        elif isinstance(m, str):
                            texts.append(m)
                else:
                    # Flatten dict values that are strings
                    for v in data.values():
                        if isinstance(v, str) and len(v) > 20:
                            texts.append(v)
                        elif isinstance(v, list):
                            for it in v:
                                if isinstance(it, str) and len(it) > 20:
                                    texts.append(it)
                        if len(texts) >= MAX_MESSAGES_PER_FILE:
                            break
            elif isinstance(data, list):
                # Expect list of messages or conversation turns
                for item in data[:MAX_MESSAGES_PER_FILE]:
                    if isinstance(item, str):
                        texts.append(item)
                    elif isinstance(item, dict):
                        # find a text-like field
                        for k in ("input", "text", "message", "utterance", "user"):
                            if k in item and isinstance(item[k], str):
                                texts.append(item[k])
                                break
            else:
                # fallback: string representation
                s = str(data)
                if len(s) > 20:
                    texts.append(s[:1000])
        else:
            # unknown extension: try to read as text
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            parts = [p.strip() for p in content.split("\n\n") if p.strip()]
            texts.extend(parts[:MAX_MESSAGES_PER_FILE])
    except Exception:
        pass
    return texts


def main():
    # Gather files
    files = []
    for pat in PATTERNS:
        files.extend(glob.glob(pat))

    # Deduplicate
    files = sorted(list(set(files)))
    if not files:
        print("No corpus files found using patterns:", PATTERNS)
        return

    print(
        f"Found {len(files)} files; sampling up to {TOTAL_MESSAGE_CAP} messages total (max {MAX_MESSAGES_PER_FILE}/file)"
    )

    glyph_counts = defaultdict(int)
    glyph_score_sums = defaultdict(float)
    glyph_samples = defaultdict(list)
    glyph_gates = defaultdict(lambda: defaultdict(int))

    total_processed = 0

    for fp in files:
        if total_processed >= TOTAL_MESSAGE_CAP:
            break
        texts = extract_texts_from_file(fp)
        if not texts:
            continue
        print(f"Processing {len(texts)} messages from {os.path.relpath(fp)}")
        for t in texts:
            if total_processed >= TOTAL_MESSAGE_CAP:
                break
            total_processed += 1
            try:
                out = parse_input(t, LEXICON_PATH, db_path=DB_PATH)
            except Exception:
                continue
            glyphs = out.get("glyphs_selected") or []
            # glyphs_selected is list of dicts with glyph_name, display_name, score, gate
            for g in glyphs:
                name = g.get("glyph_name") or ""
                display = g.get("display_name") or name
                key = display.strip()
                score = g.get("score") or 0
                glyph_counts[key] += 1
                glyph_score_sums[key] += float(score)
                if len(glyph_samples[key]) < 3:
                    glyph_samples[key].append(t.replace("\n", " ")[:200])
                gate = g.get("gate")
                if gate:
                    glyph_gates[key][gate] += 1

    # Prepare CSV rows
    rows = []
    for disp, cnt in glyph_counts.items():
        avg = glyph_score_sums[disp] / cnt if cnt else 0
        samples = " | ".join(glyph_samples[disp])
        # determine top gate
        gates = glyph_gates[disp]
        top_gate = max(gates.items(), key=lambda x: x[1])[0] if gates else ""
        rows.append((disp, cnt, round(avg, 2), top_gate, samples))

    # Sort by count desc
    rows_sorted = sorted(rows, key=lambda x: x[1], reverse=True)

    # Write CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["display_name", "count", "avg_score", "top_gate", "sample_inputs"])
        for r in rows_sorted:
            writer.writerow(r)

    print(f"Wrote {len(rows_sorted)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
