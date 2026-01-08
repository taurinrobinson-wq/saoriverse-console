"""Compatibility shim that re-exports the more complete LocalLearner when
available under `local_learner` (preferred) or `src.local_learner`.
"""
try:
    # Preferred implementation (available under src/local_learner.py)
    from local_learner import LocalLearner as _LocalLearner  # type: ignore
except Exception:
    try:
        from src.local_learner import LocalLearner as _LocalLearner  # type: ignore
    except Exception:
        # Minimal fallback implementation
        class _LocalLearner:
            def __init__(self, *args, **kwargs):
                pass

            def score_candidate(self, *args, **kwargs):
                return 0.0


class LocalLearner(_LocalLearner):
    """Expose the concrete LocalLearner class under `learning.local_learner.LocalLearner`.

    If the preferred implementation already defines the class, this simply
    re-exports it; otherwise a minimal fallback provides `score_candidate`.
    """
    pass
