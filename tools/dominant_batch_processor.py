"""Dominant batch processor scaffold.

Reads `learning/feedback_log.jsonl` and `learning/conversation_log.jsonl`,
joins entries by `conversation_id` and `turn_index`, and emits simple
training pairs (prompt, target) into `learning/training_pairs.jsonl`.

This is a lightweight, offline processor intended to be run periodically
by the Dominant learner; it does not call remote APIs itself.
"""
from pathlib import Path
import json
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LEARNING_DIR = ROOT / "learning"
FEEDBACK_LOG = LEARNING_DIR / "feedback_log.jsonl"
CONV_LOG = LEARNING_DIR / "conversation_log.jsonl"
PROCESSED = LEARNING_DIR / "processed"
OUT = PROCESSED / "training_data.jsonl"
SUMMARY = PROCESSED / "training_summary.json"


def _read_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
    return out


def _parse_ts(ts: str):
    if not ts:
        return datetime.min
    try:
        # Handle trailing Z
        if ts.endswith("Z"):
            ts = ts[:-1]
        return datetime.fromisoformat(ts)
    except Exception:
        try:
            # Fallback: try common formats
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception:
            return datetime.min


def match_feedback_to_turns(conversations, feedback):
    """For each feedback event, find the most relevant conversation turn.

    Preference order:
    1. Exact match by (conversation_id, turn_index)
    2. Most recent turn with the same conversation_id and timestamp <= feedback
    3. Most recent turn overall with timestamp <= feedback
    """
    # Normalize and sort
    convs = [c for c in conversations]
    convs_sorted = sorted(convs, key=lambda x: _parse_ts(x.get("timestamp") or x.get("ts") or ""))

    fb_sorted = sorted(feedback, key=lambda x: _parse_ts(x.get("timestamp") or x.get("ts") or ""))

    # Index convs by (conversation_id, turn_index)
    conv_index = {}
    for c in convs_sorted:
        cid = c.get("conversation_id")
        ti = c.get("turn_index")
        if cid is not None and ti is not None:
            conv_index[(cid, ti)] = c

    examples = []
    summary_counts = defaultdict(int)

    for fb in fb_sorted:
        fb_time = _parse_ts(fb.get("timestamp") or fb.get("ts") or "")
        cid = fb.get("conversation_id")
        ti = fb.get("turn_index")

        turn = None
        # 1) exact match
        if cid is not None and ti is not None and (cid, ti) in conv_index:
            turn = conv_index[(cid, ti)]

        # 2) most recent in same conversation
        if not turn and cid is not None:
            candidates = [c for c in convs_sorted if c.get("conversation_id") == cid]
            candidates = [c for c in candidates if (_parse_ts(c.get("timestamp") or c.get("ts") or "") or fb_time) <= (fb_time or _parse_ts(c.get("timestamp") or c.get("ts") or ""))]
            if candidates:
                turn = candidates[-1]

        # 3) fallback: most recent overall before feedback
        if not turn:
            candidates = [c for c in convs_sorted if (_parse_ts(c.get("timestamp") or c.get("ts") or "") or fb_time) <= (fb_time or _parse_ts(c.get("timestamp") or c.get("ts") or ""))]
            if candidates:
                turn = candidates[-1]

        if not turn:
            summary_counts["unmatched_feedback"] += 1
            continue

        # Build example
        example = {
            "conversation_id": turn.get("conversation_id"),
            "turn_index": turn.get("turn_index"),
            "user_input": turn.get("user" ) or turn.get("user_input" ) or "",
            "bot_output": turn.get("response") or "",
            "glyph": turn.get("glyph"),
            "emotional_vector": turn.get("emotional_vector"),
            "feedback_type": fb.get("type") or fb.get("feedback_type") or "unknown",
            "notes": fb.get("note") or fb.get("notes") or fb.get("feedback_text"),
            "timestamp": fb.get("timestamp") or fb.get("ts"),
        }

        # If feedback contains an explicit corrected_response or note that looks like a correction, include it
        if fb.get("corrected_response"):
            example["corrected_output"] = fb.get("corrected_response")
        elif fb.get("note") and isinstance(fb.get("note"), str) and len((fb.get("note") or "").split()) > 3:
            # treat longer notes as candidate corrected output (heuristic)
            example["corrected_output"] = fb.get("note")

        examples.append(example)
        summary_counts[example["feedback_type"]] += 1

    return examples, summary_counts


def write_training_data(examples, summary_counts):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # summary
    with SUMMARY.open("w", encoding="utf-8") as sf:
        json.dump({"total": len(examples), "by_feedback_type": dict(summary_counts)}, sf, ensure_ascii=False, indent=2)


def build_pairs():
    feedback = _read_jsonl(FEEDBACK_LOG)
    conv = _read_jsonl(CONV_LOG)

    examples, summary_counts = match_feedback_to_turns(conv, feedback)
    write_training_data(examples, summary_counts)
    return len(examples), summary_counts


if __name__ == "__main__":
    n = build_pairs()
    print(f"Built {n} training pairs from logs.")
