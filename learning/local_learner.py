"""
learning/local_learner.py
Minimal LocalLearner skeleton that records candidate learning events
using `learning/writer.py` and exposes a small API for later evolution
processors to consume.

This is intentionally minimal: it provides methods to collect a candidate,
score it heuristically (placeholder), and persist events to the
configured JSONL file under `learning/local_learning_log.jsonl`.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .writer import append_event, DEFAULT_LEARNING_DIR


DEFAULT_LOGFILE = os.path.join(os.path.dirname(
    __file__), "local_learning_log.jsonl")


class LocalLearner:
    """Minimal local learner.

    Usage pattern:
      learner = LocalLearner(logfile=path)
      learner.collect_candidate(candidate_dict)
      learner.persist()

    This class intentionally avoids in-memory ML state; it is a thin
    adapter to record events and provide a pluggable `score_candidate`
    hook for later enhancement.
    """

    def __init__(self, logfile: Optional[str] = None):
        self.logfile = logfile or DEFAULT_LOGFILE
        self._staging: list[Dict[str, Any]] = []

    def collect_candidate(self, candidate: Dict[str, Any], source: str = "local_system") -> None:
        """Add a candidate to the in-memory staging list.

        `candidate` is expected to be a dict with arbitrary keys describing
        the proposed glyph/lexicon entry.
        """
        evt = {
            "source": source,
            "event_type": "candidate",
            "payload": candidate,
            "confidence": self.score_candidate(candidate),
        }
        self._staging.append(evt)

    def score_candidate(self, candidate: Dict[str, Any]) -> Optional[float]:
        """Heuristic scorer for a candidate.

        Returns a confidence value between 0.0 and 1.0 or None when
        not applicable. This is a placeholder to be replaced with a more
        sophisticated local scoring function in later iterations.
        """
        # Enhanced scoring using symbolic_tagger diagnostics and (optionally)
        # relational_memory for prior occurrence counts.
        text = candidate.get("user_input") or candidate.get("text") or ""
        ai_resp = candidate.get("ai_response") or ""
        combined = " ".join([text, ai_resp]).strip()

        # Defaults
        fuzzy_score = 0.0
        synonym_hits = 0
        tag_count = 0
        prior_occurrence = 0
        voltage_flag = False

        diag = None
        # Try to get diagnostics from symbolic_tagger
        try:
            from symbolic_tagger import tag_input_with_diagnostics

            diag = tag_input_with_diagnostics(combined)
            tags = diag.get("tags", [])
            matches = diag.get("matches", [])
            tag_count = len(set(tags)) if tags else 0

            # Compute fuzzy_match_score as the max fuzzy score among fuzzy matches
            fuzzy_scores = [m.get("score", 0.0)
                            for m in matches if m.get("match_type") == "fuzzy"]
            if fuzzy_scores:
                fuzzy_score = max(fuzzy_scores)

            synonym_hits = sum(1 for m in matches if m.get(
                "category") == "synonym_group")

            # Voltage flag if any tag is voltage_surge
            voltage_flag = "voltage_surge" in tags

        except Exception:
            # symbolic_tagger not available or failed — keep defaults
            pass

        # Prior occurrence count from relational_memory if available
        try:
            import relational_memory

            recent = relational_memory.list_recent(50)
            if recent and diag:
                diag_tags = diag.get("tags", [])
                for cap in recent:
                    if any(t in cap.symbolic_tags for t in diag_tags):
                        prior_occurrence += 1

                    vm = getattr(cap, "voltage_marking", "") or ""
                    if not voltage_flag and isinstance(vm, str) and vm.lower() in ("high", "surge", "1", "true", "yes"):
                        voltage_flag = True
        except Exception:
            # relational_memory not available — ignore
            pass

        # Scoring weights
        weight_fuzzy = 0.60
        weight_syn = 0.30

        # Normalize synonym hits (assume 3 hits -> full score)
        norm_syn = min(1.0, synonym_hits / 3.0)

        base = weight_fuzzy * float(fuzzy_score) + weight_syn * float(norm_syn)

        # Amplifiers
        multiplier = 1.0
        multiplier += 0.05 * float(tag_count)  # small boost per distinct tag
        if voltage_flag:
            multiplier += 0.15
        # prior occurrence provides modest boost, capped
        multiplier += min(0.20, 0.02 * float(prior_occurrence))

        score = base * multiplier

        # Ensure score in [0,1]
        try:
            score = max(0.0, min(1.0, float(score)))
        except Exception:
            score = None

        return score

    def persist(self) -> None:
        """Persist staged events to the logfile using append_event.

        After successful append, clears the staging area.
        """
        for evt in self._staging:
            append_event(self.logfile, evt)
        self._staging.clear()

    def staged_count(self) -> int:
        return len(self._staging)
