import numpy as np

from emotional_os.feedback.reward_model import RewardModel


def test_update_and_score():
    rm = RewardModel(dim=3)
    f = np.array([1.0, 0.0, 0.0])
    # initial score 0
    assert rm.score(f) == 0.0
    rm.update(f, +1)
    assert rm.score(f) > 0.0
    rm.update(f, -1)
    # after +1 then -1 should return to near zero
    assert abs(rm.score(f)) < 1e-6 or rm.score(f) == 0.0
