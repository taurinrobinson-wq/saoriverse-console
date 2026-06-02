"""Vocabulary learning and unknown-term questioning for TheVillage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from TheVillage.learning.logging import append_vocabulary
from TheVillage.learning.mw_dictionary import lookup_word


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RUNTIME_DIR = BASE_DIR / "runtime"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
VOCABULARY_PATH = RUNTIME_DIR / "vocabulary.json"
SEED_PATH = DATA_DIR / "seed_vocabulary.json"


class VocabularyLearner:
    def __init__(self, vocabulary_path: Path | None = None):
        self.vocabulary_path = vocabulary_path or VOCABULARY_PATH
        self.vocabulary = self._load_vocabulary()

    def _load_vocabulary(self) -> Dict[str, dict]:
        if self.vocabulary_path.exists():
            return json.loads(self.vocabulary_path.read_text(encoding="utf-8"))
        if SEED_PATH.exists():
            payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
            self._save(payload)
            return payload
        payload = {"terms": {}}
        self._save(payload)
        return payload

    def _save(self, payload: Dict[str, dict] | None = None) -> None:
        data = payload if payload is not None else self.vocabulary
        self.vocabulary_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def known_terms(self) -> set[str]:
        return set(self.vocabulary.get("terms", {}).keys())

    def learn_definition(self, term: str, definition: str, *, source: str = "user") -> None:
        normalized = term.strip().lower()
        if not normalized or not definition.strip():
            return
        terms = self.vocabulary.setdefault("terms", {})
        terms[normalized] = {
            "definition": definition.strip(),
            "source": source,
            "confidence": 1.0 if source == "user" else 0.7,
        }
        self._save()
        append_vocabulary({"event": "learn_definition", "term": normalized, "source": source})

    def inspect_unknown_terms(self, session_id: str, terms: List[str]) -> dict:
        questions = []
        auto_definitions = {}
        for term in terms[:3]:
            if term in self.known_terms():
                continue
            lookup = lookup_word(term, session_key=session_id)
            if lookup.get("ok") and lookup.get("definitions"):
                definition = lookup["definitions"][0]
                self.learn_definition(term, definition, source="merriam_webster")
                auto_definitions[term] = definition
                continue
            questions.append({
                "term": term,
                "question": f"What does '{term}' mean in your context?",
                "reason": "unknown_term",
            })
            append_vocabulary({"event": "unknown_term", "session_id": session_id, "term": term})
        return {
            "questions": questions,
            "auto_definitions": auto_definitions,
            "known_terms": sorted(self.known_terms()),
        }