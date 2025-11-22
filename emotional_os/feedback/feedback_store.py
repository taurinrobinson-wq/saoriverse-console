import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class FeedbackStore:
    def __init__(self, path: str | Path = "emotional_os/feedback/feedback.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: Dict[str, Any]) -> None:
        entry = dict(entry)
        entry.setdefault("timestamp", datetime.utcnow().isoformat())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def load_all(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
