import json
import os
from typing import Any, Dict, List

MODULE_DIR = os.path.dirname(__file__)
FEEDBACK_PATH = os.path.join(MODULE_DIR, "feedback.jsonl")


def _ensure_dir():
    os.makedirs(MODULE_DIR, exist_ok=True)


def append_feedback(entry: Dict[str, Any]) -> None:
    """Append a JSON-serializable entry as a single JSONL line to the feedback file.

    This uses an append+fsync pattern to make writes durable and avoids partial-line
    corruption on POSIX filesystems.
    """
    _ensure_dir()
    line = json.dumps(entry, ensure_ascii=False)
    # Open in append mode, write line, flush and fsync to ensure durability.
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except AttributeError:
            # Windows or environments without fsync on file objects
            pass


def read_all() -> List[Dict[str, Any]]:
    """Read all JSONL entries from the feedback file.

    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(FEEDBACK_PATH):
        return []
    out: List[Dict[str, Any]] = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # skip malformed lines but continue
                continue
    return out
