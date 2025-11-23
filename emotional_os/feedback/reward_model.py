import json
import os
from typing import Optional

import numpy as np


class RewardModel:
    """A tiny online reward model (perceptron-like) for demo purposes.

    Stores weights as a simple list in a JSON file. Methods:
    - score(features) -> float
    - update(features, reward) -> None
    - save()/load()
    """

    def __init__(self, dim: int = 128, path: Optional[str] = None, auto_load: bool = True):
        self.dim = int(dim)
        self.path = path or os.path.join(
            os.path.dirname(__file__), "weights.json")
        self.weights = np.zeros(self.dim, dtype=float)
        if auto_load:
            try:
                self.load()
            except Exception:
                # Best-effort: ignore load errors
                pass

    def score(self, features) -> float:
        arr = np.asarray(features, dtype=float)
        if arr.shape[0] != self.weights.shape[0]:
            raise ValueError("Feature length does not match model dimension")
        return float(np.dot(self.weights, arr))

    def update(self, features, reward: float, lr: float = 0.1) -> None:
        """Simple online update: weights += lr * reward * features

        `reward` can be positive/negative or a scalar rating; caller controls scaling.
        Saves weights atomically after update.
        """
        arr = np.asarray(features, dtype=float)
        if arr.shape[0] != self.weights.shape[0]:
            # If shapes differ, resize conservatively (extend or truncate)
            new_dim = max(arr.shape[0], self.weights.shape[0])
            new_w = np.zeros(new_dim, dtype=float)
            new_w[: self.weights.shape[0]] = self.weights
            self.weights = new_w
            if arr.shape[0] > new_dim:
                # shouldn't happen, but guard
                arr = arr[:new_dim]

        self.weights += lr * float(reward) * arr
        try:
            self.save()
        except Exception:
            # non-fatal
            pass

    def save(self) -> None:
        tmp = self.path + ".tmp"
        obj = {"dim": int(self.weights.shape[0]),
               "weights": self.weights.tolist()}
        d = os.path.dirname(self.path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, self.path)

    def load(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        w = obj.get("weights")
        if w is None:
            return
        arr = np.asarray(w, dtype=float)
        if arr.shape[0] != self.weights.shape[0]:
            # resize
            new_dim = max(arr.shape[0], self.weights.shape[0])
            new_w = np.zeros(new_dim, dtype=float)
            new_w[: arr.shape[0]] = arr
            self.weights = new_w
        else:
            self.weights = arr
