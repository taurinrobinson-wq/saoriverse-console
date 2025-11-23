#!/usr/bin/env python3
"""Summarize unsafe/internal glyph tags logged to `logs/unsafe_tags.log`.

Log format (tab-separated per-line):
  <iso-timestamp>\t<tag>\t<confidence>\t<overlays_repr>\n
This script prints:
 - Top N tags by frequency
 - Confidence statistics per tag (count, mean, median, stdev)
 - Co-occurrence counts (which overlays tend to appear with the tag)
 - Sample log lines for each top tag

Usage:
  python scripts/unsafe_tags_summary.py [--path logs/unsafe_tags.log] [--top 10] [--samples 3]

"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import os
import random
import statistics
from typing import Dict, List, Tuple


def parse_line(line: str) -> Tuple[str, str, float, List[Dict]]:
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 4:
        # tolerant parsing for older formats
        ts = parts[0] if parts else ""
        tag = parts[1] if len(parts) > 1 else ""
        try:
            conf = float(parts[2]) if len(parts) > 2 else 0.0
        except Exception:
            conf = 0.0
        overlays = []
        return ts, tag, conf, overlays

    ts, tag, conf_s, overlays_repr = parts[0], parts[1], parts[2], parts[3]
    try:
        conf = float(conf_s)
    except Exception:
        conf = 0.0

    try:
        overlays = ast.literal_eval(overlays_repr)
        if not isinstance(overlays, list):
            overlays = []
    except Exception:
        overlays = []

    return ts, tag, conf, overlays


def summarize(path: str, top_n: int = 10, samples: int = 3) -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found: {path}")

    tag_counts: collections.Counter = collections.Counter()
    tag_confidences: Dict[str, List[float]] = collections.defaultdict(list)
    tag_samples: Dict[str, List[str]] = collections.defaultdict(list)
    cooccurrence: Dict[str, collections.Counter] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            ts, tag, conf, overlays = parse_line(line)
            tag_counts[tag] += 1
            tag_confidences[tag].append(conf)
            tag_samples[tag].append(line.strip())

            # extract overlay tags from overlays list (list of dicts expected)
            seen = []
            for o in overlays:
                if isinstance(o, dict):
                    t = o.get("tag") or o.get("glyph_name") or o.get("name")
                    if t and t != tag:
                        seen.append(t)
            if tag not in cooccurrence:
                cooccurrence[tag] = collections.Counter()
            cooccurrence[tag].update(seen)

    # build summary
    top = tag_counts.most_common(top_n)
    summary = {
        "total_lines": sum(tag_counts.values()),
        "unique_tags": len(tag_counts),
        "top_tags": [],
    }

    for tag, cnt in top:
        confs = tag_confidences.get(tag, [])
        try:
            mean = statistics.mean(confs) if confs else 0.0
            med = statistics.median(confs) if confs else 0.0
            stdev = statistics.stdev(confs) if len(confs) > 1 else 0.0
        except Exception:
            mean = med = stdev = 0.0

        co = cooccurrence.get(tag, collections.Counter()).most_common(10)
        sample_lines = random.sample(tag_samples.get(
            tag, []), min(samples, len(tag_samples.get(tag, []))))

        summary["top_tags"].append({
            "tag": tag,
            "count": cnt,
            "mean_confidence": round(mean, 4),
            "median_confidence": round(med, 4),
            "stdev_confidence": round(stdev, 4),
            "top_cooccurring_overlays": co,
            "sample_lines": sample_lines,
        })

    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize logs/unsafe_tags.log")
    p.add_argument("--path", default="logs/unsafe_tags.log",
                   help="Path to unsafe tags log")
    p.add_argument("--top", type=int, default=10, help="Top N tags to show")
    p.add_argument("--samples", type=int, default=3,
                   help="Sample lines per tag")
    p.add_argument("--json", action="store_true",
                   help="Print machine-readable JSON")
    args = p.parse_args()

    try:
        out = summarize(args.path, top_n=args.top, samples=args.samples)
    except FileNotFoundError as e:
        print(str(e))
        return

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    print(f"Total logged lines: {out['total_lines']}")
    print(f"Unique unsafe tags: {out['unique_tags']}")
    print()
    print("Top tags:")
    for item in out["top_tags"]:
        print(f"- {item['tag']}  (count={item['count']}, mean_conf={item['mean_confidence']}, median={item['median_confidence']}, stdev={item['stdev_confidence']})")
        if item['top_cooccurring_overlays']:
            co = ", ".join(
                [f"{t}:{c}" for t, c in item['top_cooccurring_overlays']])
            print(f"    co-occurs with: {co}")
        if item['sample_lines']:
            print("    samples:")
            for s in item['sample_lines']:
                print(f"      {s}")
        print()


if __name__ == "__main__":
    main()
