import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LEARNING_DIR = ROOT / "learning"
LEARNING_DIR.mkdir(parents=True, exist_ok=True)

FEEDBACK_LOG = LEARNING_DIR / "feedback_log.jsonl"
CONVERSATION_LOG = LEARNING_DIR / "conversation_log.jsonl"


def _append_jsonl(path: Path, obj: dict):
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception:
        # best-effort: don't raise to avoid breaking UI
        pass


def append_feedback(entry: dict):
    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **entry,
    }
    _append_jsonl(FEEDBACK_LOG, payload)


def append_conversation(entry: dict):
    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **entry,
    }
    _append_jsonl(CONVERSATION_LOG, payload)
