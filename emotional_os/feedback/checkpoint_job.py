import json
import numpy as np
from datetime import datetime
from pathlib import Path
from emotional_os.feedback.reward_model import RewardModel


class CheckpointJob:
    def __init__(self, model: RewardModel, dir: str = "emotional_os/feedback/checkpoints"):
        self.model = model
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def snapshot(self) -> Path:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        path = self.dir / f"weights_{ts}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.model.weights.tolist(), f)
        return path


if __name__ == "__main__":
    # simple CLI: create a model from default path and snapshot
    try:
        rm = RewardModel()
    except Exception as e:
        print("Failed to load RewardModel:", e)
        raise
    job = CheckpointJob(rm)
    p = job.snapshot()
    print("Snapshot written:", p)
