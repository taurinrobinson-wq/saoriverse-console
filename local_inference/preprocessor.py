import re
import json
import os
import time
from typing import List, Dict, Any, Optional

try:
    # Heavy model imports deferred; optional GPU usage
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False


DEFAULT_TAXONOMY = {
    "joy": ["joy", "happy", "delight", "pleased", "glad"],
    "sadness": ["sad", "grief", "sorrow", "lonely"],
    "anger": ["angry", "mad", "furious", "irritat"],
    "fear": ["afraid", "scared", "fear", "anxious"],
    "trust": ["trust", "safe", "secure"],
    "surprise": ["surpris", "startl"],
    "neutral": []
}


DEFAULT_ESCALATION_TIERS = {
    "tier_1": {
        "tags": ["panic", "grief", "boundary_violation", "abandonment", "betrayal"],
        "action": "force_escalation"
    },
    "tier_2": {
        "tags": ["conflict", "longing", "confusion", "vulnerability", "rupture"],
        "action": "conditional_escalation"
    },
    "tier_3": {
        "tags": ["curiosity", "joy", "calm", "reunion", "support_seeking"],
        "action": "no_escalation"
    }
}


class Preprocessor:
    """Local preprocessor that can optionally use a HF causal LM (e.g. GPT-J) to classify,
    tag, redact and produce short replies. Designed as a privacy-first steward.

    Behavior:
    - Runs lightweight PII redaction first (regex)
    - If Transformers are available and model_name provided, will attempt to load model
      (model loading is optional and deferred to expensive environments)
    - Returns a dict with intent, confidence, sanitized_text, short_reply, emotional_tags, edit_log
    """

    def __init__(self, model_name: Optional[str] = None, test_mode: bool = False, taxonomy_path: Optional[str] = None, confidence_threshold: float = 0.6, cluster_size: int = 2):
        """If taxonomy_path is provided, load canonical emotional taxonomy from JSON.

        Expected taxonomy JSON format (simple):
        {
            "calm": ["calm", "peaceful", "relieved"],
            "panic": ["panic", "terrified", "hysterical"],
            ...
        }
        """
        self.model_name = model_name
        self.test_mode = test_mode
        # Configurable thresholds for escalation logic
        self.confidence_threshold = float(confidence_threshold)
        self.cluster_size = int(cluster_size)
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.taxonomy = DEFAULT_TAXONOMY
        self.taxonomy_source = "default"

        # If taxonomy_path provided or exists at standard location, try to load it
        if taxonomy_path:
            try:
                if os.path.exists(taxonomy_path):
                    with open(taxonomy_path, "r", encoding="utf-8") as tf:
                        self.taxonomy = json.load(tf)
                        self.taxonomy_source = taxonomy_path
                else:
                    # Attempt to load taxonomy relative to this module to
                    # avoid issues when tests change the current working
                    # directory during a full suite run.
                    alt = os.path.join(os.path.dirname(
                        __file__), 'emotional_taxonomy_sample.json')
                    if os.path.exists(alt):
                        with open(alt, 'r', encoding='utf-8') as tf:
                            self.taxonomy = json.load(tf)
                            self.taxonomy_source = alt
                    else:
                        self.taxonomy = DEFAULT_TAXONOMY
                        self.taxonomy_source = "default"
            except Exception:
                self.taxonomy = DEFAULT_TAXONOMY
                self.taxonomy_source = "default"
        else:
            # also allow a workspace-level default file
            default_path = os.path.join(
                os.getcwd(), "local_inference", "emotional_taxonomy.json")
            if os.path.exists(default_path):
                try:
                    with open(default_path, "r", encoding="utf-8") as tf:
                        self.taxonomy = json.load(tf)
                        self.taxonomy_source = default_path
                except Exception:
                    self.taxonomy = DEFAULT_TAXONOMY
                    self.taxonomy_source = "default"

        # Escalation tiers may be provided inside the taxonomy file under 'escalation_tiers'
        self.escalation_tiers = DEFAULT_ESCALATION_TIERS.copy()
        try:
            # Allow taxonomy-embedded escalation tiers
            if isinstance(self.taxonomy, dict) and 'escalation_tiers' in self.taxonomy:
                self.escalation_tiers = self.taxonomy.get(
                    'escalation_tiers', self.escalation_tiers)
            else:
                # also look for a standalone escalation file
                esc_path = os.path.join(
                    os.getcwd(), 'local_inference', 'escalation_tiers.json')
                if os.path.exists(esc_path):
                    try:
                        with open(esc_path, 'r', encoding='utf-8') as ef:
                            self.escalation_tiers = json.load(ef)
                    except Exception:
                        pass
        except Exception:
            # fallback to defaults on any issue
            self.escalation_tiers = DEFAULT_ESCALATION_TIERS.copy()
        # simple logs directory
        self.logs_dir = os.path.join(os.getcwd(), "local_inference", "logs")
        os.makedirs(self.logs_dir, exist_ok=True)

        if model_name and TRANSFORMERS_AVAILABLE and not test_mode:
            try:
                # prefer fp16 + device_map auto where available
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name, torch_dtype=torch.float16, device_map="auto")
                self.loaded = True
            except Exception:
                # Loading may fail in restricted environments; fall back to test mode.
                self.loaded = False

    # --- utility helpers ---
    def _log(self, entry: Dict[str, Any]):
        path = os.path.join(self.logs_dir, "preprocessor.log")
        entry["ts"] = time.time()
        try:
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def record_audit(self, payload: Dict[str, Any]):
        """Public wrapper for recording audit entries.

        Ensures minimal normalization and avoids recording raw unredacted user text.
        Use this from external callers instead of touching the internal _log.
        """
        try:
            if not isinstance(payload, dict):
                payload = {'payload': str(payload)}

            # Normalize keys for traceability
            audit = {
                'kind': 'preprocessor_audit',
                'payload': payload,
                'taxonomy_source': self.taxonomy_source,
                'test_mode': bool(self.test_mode)
            }
            # Preserve existing minimal timestamping and write via internal logger
            self._log(audit)
        except Exception:
            # Swallow to avoid UI breakage
            pass

    def _pii_redact(self, text: str) -> (str, List[str]):
        edits = []
        redacted = text
        # email
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        if re.search(email_pattern, redacted):
            redacted = re.sub(email_pattern, "[REDACTED_EMAIL]", redacted)
            edits.append("redacted_email")

        # phone (simple)
        phone_pattern = r"\b\+?\d[\d\-() ]{7,}\d\b"
        if re.search(phone_pattern, redacted):
            redacted = re.sub(phone_pattern, "[REDACTED_PHONE]", redacted)
            edits.append("redacted_phone")

        # ssn-like
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        if re.search(ssn_pattern, redacted):
            redacted = re.sub(ssn_pattern, "[REDACTED_SSN]", redacted)
            edits.append("redacted_ssn")

        return redacted, edits

    def _lexical_emotional_tags(self, text: str) -> List[str]:
        tags = set()
        lower = text.lower()
        for tag, keywords in self.taxonomy.items():
            # Keywords may be a list or single string
            if isinstance(keywords, list):
                for kw in keywords:
                    if kw and kw in lower:
                        tags.add(tag)
            elif isinstance(keywords, str) and keywords in lower:
                tags.add(tag)
        if not tags:
            tags.add("neutral")
        return list(tags)

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """Ensure returned tags are canonical keys present in the taxonomy."""
        canonical = set()
        for t in tags:
            if t in self.taxonomy:
                canonical.add(t)
            else:
                # attempt fuzzy match by substring
                lt = t.lower()
                for key, kws in self.taxonomy.items():
                    if lt == key or lt in key:
                        canonical.add(key)
                        break
        if not canonical:
            canonical.add("neutral")
        return list(canonical)

    def _rule_intent(self, text: str) -> (str, float):
        # very small heuristic intent classifier
        t = text.strip()
        if len(t) < 140 and t.endswith("?"):
            return "local_reply", 0.9
        if "help" in t.lower() or "urgent" in t.lower():
            return "escalate", 0.95
        # sensitive markers
        if "password" in t.lower() or "ssn" in t.lower() or "credit card" in t.lower():
            return "sensitive", 0.99
        # fallback
        return "unknown", 0.5

    def _determine_escalation(self, emotional_tags: List[str], confidence: float, editorial_interventions: List[str]) -> (str, Optional[str]):
        """Determine escalation action and reason based on configured escalation tiers and rules.

        Returns tuple (escalation_action, escalation_reason)
        escalation_action in {'force_escalation','conditional_escalation','no_escalation'}
        """
        try:
            tags_set = set([t for t in emotional_tags if isinstance(t, str)])
            # Build tier sets
            tier1 = set(self.escalation_tiers.get(
                'tier_1', {}).get('tags', []))
            tier2 = set(self.escalation_tiers.get(
                'tier_2', {}).get('tags', []))
            tier3 = set(self.escalation_tiers.get(
                'tier_3', {}).get('tags', []))

            # Tier 1 immediate escalation
            if tags_set & tier1:
                return 'force_escalation', 'tier_1_detected'

            # Tier 2 conditional rules
            t2_hits = tags_set & tier2
            if t2_hits:
                # cluster escalation: multiple tier2 tags together (configurable)
                if len(t2_hits) >= self.cluster_size:
                    return 'conditional_escalation', 'cluster_escalation'
                # confidence-based escalation (configurable)
                if confidence < float(self.confidence_threshold):
                    return 'conditional_escalation', 'confidence_escalation'
                # otherwise do not escalate automatically
                return 'no_escalation', None

            # Tier 3 or none -> no escalation
            return 'no_escalation', None
        except Exception:
            return 'no_escalation', None

    def _model_generate_guided(self, prompt: str, max_new_tokens: int = 64) -> str:
        # Use HF model if loaded, otherwise return empty
        if not self.loaded or not self.model or not self.tokenizer:
            return ""
        try:
            inputs = self.tokenizer(
                prompt, return_tensors="pt").to(self.model.device)
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            return self.tokenizer.decode(out[0], skip_special_tokens=True)
        except Exception:
            return ""

    def preprocess(self, user_text: str, conversation_context: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Main preprocessing entry. Returns structured result and logs the intervention."""
        edit_log: List[str] = []
        sanitized, edits = self._pii_redact(user_text)
        edit_log.extend(edits)

        # Lexical emotional tags
        emotional_tags = self._lexical_emotional_tags(sanitized)
        emotional_tags = self._normalize_tags(emotional_tags)

        # Basic rule-based intent and confidence
        intent, confidence = self._rule_intent(sanitized)

        short_reply = None

        # If model available, try to generate a short_reply and refine tags
        if self.loaded:
            prompt = (
                "You are a privacy-preserving assistant that classifies user intent and tags emotional tone.\n"
                f"User: {sanitized}\n\nReturn JSON with fields: intent, confidence (0-1), short_reply (optional), emotional_tags (list)."
            )
            raw = self._model_generate_guided(prompt, max_new_tokens=128)
            if raw:
                # try to extract JSON from model output
                try:
                    jtext = raw[raw.find("{"):]
                    parsed = json.loads(jtext)
                    intent = parsed.get("intent", intent)
                    confidence = float(parsed.get("confidence", confidence))
                    short_reply = parsed.get("short_reply")
                    emotional_tags = parsed.get(
                        "emotional_tags", emotional_tags)
                    edit_log.append("model_refined")
                except Exception:
                    edit_log.append("model_parse_failed")

        # Human-in-the-loop trigger: emotional mismatch heuristic
        # (if lexical tags and model tags strongly disagree — simulate by checking 'neutral' vs others)
        editorial_interventions: List[str] = []
        if "neutral" in emotional_tags and intent == "escalate":
            edit_log.append("emotional_mismatch")
            editorial_interventions.append("emotional_mismatch")

        # Determine escalation action based on emotional tags and confidence
        escalation_action, escalation_reason = self._determine_escalation(
            emotional_tags, float(confidence), editorial_interventions)
        if escalation_action != 'no_escalation':
            # ensure the editorial_interventions list contains the escalation reason
            if escalation_reason:
                editorial_interventions.append(escalation_reason)
            # Enforce editorial logging rule: ensure key fields are present (they are added to log below)

        result = {
            "intent": intent,
            "confidence": float(confidence),
            "sanitized_text": sanitized,
            "short_reply": short_reply,
            "emotional_tags": emotional_tags,
            "edit_log": edit_log,
            "editorial_interventions": editorial_interventions,
            "escalation_action": escalation_action,
            "escalation_reason": escalation_reason,
            "taxonomy_source": self.taxonomy_source,
        }

        # Write a log entry (minimal, no raw unredacted text)
        try:
            log_entry = {
                "intent": intent,
                "confidence": float(confidence),
                "emotional_tags": emotional_tags,
                "edits": edit_log,
                "editorial_interventions": editorial_interventions,
                "escalation_action": escalation_action,
                "escalation_reason": escalation_reason,
                "taxonomy_source": self.taxonomy_source,
                "text_hash": hash(sanitized) if sanitized else None,
            }
            self._log(log_entry)
        except Exception:
            pass

        return result


if __name__ == "__main__":
    # quick interactive test (falls back to rule-based)
    p = Preprocessor(test_mode=True)
    examples = [
        "Hi, can you summarize my notes and redact john@example.com?",
        "I'm feeling really sad and lonely today.",
        "Is this urgent? I lost my job and need help."
    ]
    for e in examples:
        print("INPUT:", e)
        print(json.dumps(p.preprocess(e), indent=2))
        print("---")
