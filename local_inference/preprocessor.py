import json
import os
import time
import re
from typing import List, Tuple, Dict, Any


class Preprocessor:
    def __init__(self, test_mode: bool = False, taxonomy_path: str = None):
        self.test_mode = test_mode
        self.taxonomy_path = taxonomy_path
        self.logs_dir = os.path.join(os.getcwd(), "logs") if not test_mode else os.getcwd()
        os.makedirs(self.logs_dir, exist_ok=True)
        # Minimal taxonomy: tier mapping if file not provided
        self.taxonomy = {"tier_1": ["panic"], "tier_2": ["conflict", "longing"], "tier_3": []}
        if taxonomy_path and os.path.exists(taxonomy_path):
            try:
                with open(taxonomy_path, "r", encoding="utf8") as f:
                    data = json.load(f)
                    # Expecting structure with tiers mapping
                    self.taxonomy = data.get("tiers", self.taxonomy) if isinstance(data, dict) else self.taxonomy
            except Exception:
                pass

    def _determine_escalation(self, tags: List[str], confidence: float, context_words: List[str]) -> Tuple[str, str]:
        # Tier 1: immediate escalation on panic with high confidence
        if any(t in tags for t in self.taxonomy.get("tier_1", [])) and confidence >= 0.9:
            return "force_escalation", "tier_1_detected"

        # Tier 2: cluster-based escalation when multiple tier2 tags present
        tier2 = set(self.taxonomy.get("tier_2", []))
        found = [t for t in tags if t in tier2]
        if len(found) >= 2:
            return "conditional_escalation", "cluster_escalation"

        # Single tier2 with low confidence -> conditional escalation by confidence
        if len(found) == 1 and confidence < 0.5:
            return "conditional_escalation", "confidence_escalation"

        return "no_escalation", "none"

    def record_audit(self, payload: Dict[str, Any]) -> None:
        log_path = os.path.join(self.logs_dir, "preprocessor.log")
        entry = {"kind": "preprocessor_audit", "ts": int(time.time() * 1000), "payload": payload}
        with open(log_path, "a", encoding="utf8") as f:
            f.write(json.dumps(entry) + "\n")

    def _pii_redact(self, text: str) -> Tuple[str, List[str]]:
        edits = []
        redacted = text
        # Phone
        phone_re = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
        if phone_re.search(redacted):
            redacted = phone_re.sub("[REDACTED_PHONE]", redacted)
            edits.append("redacted_phone")
        # Email
        email_re = re.compile(r"[\w\.-]+@[\w\.-]+")
        if email_re.search(redacted):
            redacted = email_re.sub("[REDACTED_EMAIL]", redacted)
            edits.append("redacted_email")
        # SSN-like
        ssn_re = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        if ssn_re.search(redacted):
            redacted = ssn_re.sub("[REDACTED_SSN]", redacted)
            edits.append("redacted_ssn")

        return redacted, edits

    def _lexical_emotional_tags(self, text: str) -> List[str]:
        # Very small lexical tagger for tests
        lower = text.lower()
        tags = []
        keywords = {
            "panic": "panic",
            "conflict": "conflict",
            "longing": "longing",
            "joy": "joy",
            "happy": "joy",
            "sad": "sadness",
        }
        for k, v in keywords.items():
            if k in lower:
                tags.append(v)
        return tags

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        # Normalize simple synonyms to canonical forms
        mapping = {"happy": "joy", "sad": "sadness"}
        return [mapping.get(t, t) for t in tags]

    def preprocess(self, text: str) -> Dict[str, Any]:
        sanitized, edits = self._pii_redact(text)
        raw_tags = self._lexical_emotional_tags(sanitized)
        norm = self._normalize_tags(raw_tags)
        # Simple confidence heuristic
        confidence = 0.8 if norm else 0.2
        action, reason = self._determine_escalation(norm, confidence, [])
        result = {
            "sanitized_text": sanitized,
            "edit_log": edits,
            "emotional_tags": norm,
            "escalation_action": action,
            "escalation_reason": reason,
        }
        return result

