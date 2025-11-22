from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import tempfile
import os

try:
    import numpy as np
except Exception:  # pragma: no cover - tests will install numpy
    np = None


class RewardModel:
    """A tiny perceptron-style reward model.

    It keeps a weight vector and supports scoring and simple online updates.
    We persist weights to a JSON file so learned state survives restarts.
    """

    def __init__(self, dim: int = 128, path: str | Path = "emotional_os/feedback/weights.json", auto_load: bool = False):
        if np is None:
            raise RuntimeError("numpy is required for RewardModel")
        self.dim = int(dim)
        self.path = Path(path)
        self.auto_load = bool(auto_load)
        # initialize weights then attempt to load persisted values
        self.weights = np.zeros(self.dim, dtype=float)
        # Only load persisted weights when explicitly requested to avoid
        # surprising test-time interactions with a repository-level weights
        # file. Callers that want persisted state should pass `auto_load=True`.
        if self.auto_load:
            self.load()

    def score(self, features) -> float:
        arr = self._ensure(features)
        return float(np.dot(self.weights, arr))

    def update(self, features, label: int = 1) -> None:
        """Update weights with label {+1, -1} using a perceptron step."""
        arr = self._ensure(features)
        if label not in (1, -1):
            raise ValueError("label must be +1 or -1")
        self.weights += label * arr
        # persist immediately to keep state durable
        try:
            self.save(self.path)
        except Exception:
            # don't raise on save failure; log could be added
            pass

    def _ensure(self, features):
        a = np.asarray(features, dtype=float)
        if a.shape[0] != self.dim:
            # simple resize/pad/truncate behavior
            b = np.zeros(self.dim, dtype=float)
            b[: min(a.shape[0], self.dim)] = a[: self.dim]
            return b
        return a

    def save(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # save atomically: write to temp file then replace
        data = {"dim": int(self.dim), "weights": self.weights.tolist()}
        fd, tmp = tempfile.mkstemp(
            dir=str(p.parent), prefix="weights_", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f)
            # atomic replace
            os.replace(tmp, str(p))
        except Exception:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass
            raise

    def load(self) -> None:
        p = Path(self.path)
        if not p.exists():
            return
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            w = np.asarray(data.get("weights", []), dtype=float)
            if w.shape[0] == self.dim:
                self.weights = w
            else:
                # if dims differ, pad or truncate
                b = np.zeros(self.dim, dtype=float)
                b[: min(w.shape[0], self.dim)] = w[: self.dim]
                self.weights = b
        except Exception:
            # ignore load errors and keep zero weights
            return

    @classmethod
    def load_from_file(cls, path: Path | str) -> "RewardModel":
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        rm = cls(dim=int(data.get("dim", 128)), path=path)
        rm.weights = np.asarray(data.get("weights", []), dtype=float)
        return rm
