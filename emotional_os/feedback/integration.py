from typing import Iterable, Tuple

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


def select_best_response(candidates: Iterable[Tuple[str, object]], reward_model=None):
    """Select the best response from candidates.

    candidates: iterable of (text, features)
    features are numpy arrays (or lists) compatible with RewardModel.
    If no reward_model is provided, returns the first candidate.
    """
    if reward_model is None:
        # fallback: return first candidate text
        for text, _ in candidates:
            return text
        return ""

    best = None
    best_score = float("-inf")
    for text, feats in candidates:
        try:
            score = reward_model.score(feats)
        except Exception:
            score = 0.0
        if score > best_score:
            best_score = score
            best = text

    return best if best is not None else ""
