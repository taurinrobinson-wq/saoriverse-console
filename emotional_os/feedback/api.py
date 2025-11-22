from fastapi import APIRouter, Body
from emotional_os.feedback.feedback_store import FeedbackStore
from emotional_os.feedback.reward_model import RewardModel
import numpy as np

router = APIRouter()
store = FeedbackStore()
# reward model persists weights to disk by default; use same path across processes
reward_model = RewardModel(dim=128, path="emotional_os/feedback/weights.json")


@router.post("/ingest_feedback")
def ingest_feedback(
    rating: int = Body(..., embed=True),
    text: str = Body("", embed=True),
    features: list[float] = Body([], embed=True),
):
    """
    Append feedback entry and update reward model online.
    rating: +1 for positive, -1 for negative
    text: optional corrected response
    features: numeric vector representing candidate response
    """
    entry = {"rating": rating, "text": text, "features": features}
    store.append(entry)

    if features:
        arr = np.array(features, dtype=float)
        reward_model.update(arr, rating)

    # return current weights for debugging/interactive use
    return {"status": "ok", "updated_weights": reward_model.weights.tolist()}
