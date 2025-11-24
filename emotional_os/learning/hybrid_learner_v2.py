"""
Hybrid Learning with User-Specific Overrides

Architecture:
- Shared base lexicon (built over time from quality interactions)
- Per-user overrides (personal learning)
- Quality filtering to prevent toxic content from poisoning shared lexicon
- Trust scoring for contributions
- Poetry signal mapping to expand emotional vocabulary
- Intelligent anonymization for HIPAA/GDPR compliance
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Import anonymization protocol
try:
    from emotional_os.safety.anonymization_protocol import AnonymizationProtocol
    ANONYMIZATION_AVAILABLE = True
except ImportError:
    ANONYMIZATION_AVAILABLE = False
    logger.warning(
        "Anonymization protocol not available - skipping anonymization")

# Map poetry signals to existing Greek letter signals
POETRY_TO_SIGNAL_MAP = {
    "love": "α",           # Devotion / α
    "intimacy": "α",       # Devotion / α
    "vulnerability": "θ",  # Grief / θ
    "transformation": "ε",  # Insight / ε
    "admiration": "Ω",     # Recognition / Ω
    "joy": "λ",           # Joy / λ
    "sensuality": "α",    # Devotion / α (physical/emotional devotion)
    "nature": "γ",        # Longing / γ
}


class HybridLearnerWithUserOverrides:
    """Learn from conversations with per-user personalization and quality filtering."""

    def __init__(
        self,
        shared_lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
        learning_log_path: str = "learning/hybrid_learning_log.jsonl",
        user_overrides_dir: str = "learning/user_overrides",
        enable_anonymization: bool = True,
        allow_medical_details: bool = False,
        allow_names: bool = False,
    ):
        """Initialize the hybrid learner with user overrides and anonymization.

        Args:
            shared_lexicon_path: Shared lexicon all users benefit from
            db_path: Shared glyphs database
            learning_log_path: Append-only learning log
            user_overrides_dir: Directory for per-user learning
            enable_anonymization: Enable HIPAA/GDPR anonymization (default True)
            allow_medical_details: Allow medical terms (requires user consent)
            allow_names: Allow real names (requires user consent)
        """
        self.shared_lexicon_path = shared_lexicon_path
        self.db_path = db_path
        self.learning_log_path = learning_log_path
        self.user_overrides_dir = user_overrides_dir

        # Ensure directories exist
        Path(learning_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(user_overrides_dir).mkdir(parents=True, exist_ok=True)

        self.shared_lexicon = self._load_shared_lexicon()

        # Initialize anonymization if available
        self.anonymization_enabled = enable_anonymization and ANONYMIZATION_AVAILABLE
        if self.anonymization_enabled:
            self.anonymizer = AnonymizationProtocol(
                allow_medical=allow_medical_details,
                allow_names=allow_names
            )
            logger.info("Anonymization protocol enabled")
        else:
            self.anonymizer = None
            logger.warning("Anonymization disabled or unavailable")

    def _load_shared_lexicon(self) -> Dict:
        """Load the shared signal lexicon."""
        try:
            with open(self.shared_lexicon_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load shared lexicon: {e}")
            return {"signals": {}}

    def _load_user_overrides(self, user_id: str) -> Dict:
        """Load user-specific lexicon overrides."""
        user_file = Path(self.user_overrides_dir) / f"{user_id}_lexicon.json"
        try:
            if user_file.exists():
                with open(user_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load user overrides for {user_id}: {e}")
        return {"signals": {}, "trust_score": 0.5, "contributions": 0}

    def _save_user_overrides(self, user_id: str, overrides: Dict):
        """Save user-specific lexicon overrides."""
        try:
            user_file = Path(self.user_overrides_dir) / \
                f"{user_id}_lexicon.json"
            with open(user_file, 'w') as f:
                json.dump(overrides, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user overrides for {user_id}: {e}")

    def _is_quality_exchange(
        self,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
    ) -> Tuple[bool, str]:
        """Determine if an exchange is high quality and safe to contribute to shared lexicon.

        Returns:
            (is_quality: bool, reason: str)
        """
        # Check for excessive length (potential spam/abuse)
        if len(user_input) > 5000:
            return False, "input_too_long"

        if len(ai_response) > 10000:
            return False, "response_too_long"

        # Check for toxic keywords (basic filter)
        toxic_keywords = [
            "hate", "kill", "die", "suicide", "abuse", "assault",
            "rape", "racist", "sexist", "pedophile", "harm", "hurt"
        ]
        combined_text = (user_input + " " + ai_response).lower()
        for keyword in toxic_keywords:
            if keyword in combined_text:
                return False, f"toxic_keyword_{keyword}"

        # Check for meaningful content (at least 3 words)
        if user_input.count(" ") < 2:  # Less than 3 words
            return False, "input_too_short"

        # Check for template repetition (indicator of low quality)
        template_count = ai_response.lower().count("pause for a breath")
        if template_count > 1:
            return False, "repetitive_template"

        # Check if response indicates emotional engagement
        # (even if formal signal detection didn't work)
        engagement_phrases = [
            "feel", "emotion", "beautiful", "powerful", "vulnerable",
            "intimacy", "connection", "love", "poetry", "inspire"
        ]
        response_lower = ai_response.lower()
        has_engagement = any(
            phrase in response_lower for phrase in engagement_phrases)

        if not has_engagement and (not emotional_signals or len(emotional_signals) == 0):
            return False, "no_emotional_engagement"

        # Looks good!
        return True, "quality_exchange"

    def learn_from_exchange(
        self,
        user_id: str,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyphs: Optional[List[Dict]] = None,
    ) -> Dict:
        """Learn from a single user-AI exchange.

        Args:
            user_id: User making the exchange
            user_input: What the user said
            ai_response: The AI's response
            emotional_signals: Detected emotional signals (optional - will be extracted if empty)
            glyphs: Matched glyphs

        Returns:
            Learning result dict with status and details
        """
        result = {
            "success": False,
            "learned_to_shared": False,
            "learned_to_user": False,
            "reason": "",
        }

        try:
            # 0. If no signals detected, try poetry extraction
            if not emotional_signals or len(emotional_signals) == 0:
                try:
                    from emotional_os.learning.poetry_signal_extractor import get_poetry_extractor
                    extractor = get_poetry_extractor()
                    emotional_signals = extractor.extract_signals(user_input)
                except Exception as e:
                    logger.warning(f"Poetry extraction failed: {e}")

            # 1. Log the exchange
            self._log_exchange(user_id, user_input,
                               ai_response, emotional_signals, glyphs)

            # 2. Always learn to user's personal lexicon
            user_overrides = self._load_user_overrides(user_id)
            self._learn_to_user_lexicon(
                user_overrides, user_input, ai_response, emotional_signals
            )
            self._save_user_overrides(user_id, user_overrides)
            result["learned_to_user"] = True

            # 3. Check if quality enough for shared lexicon
            is_quality, reason = self._is_quality_exchange(
                user_input, ai_response, emotional_signals
            )

            if is_quality:
                # Learn to shared lexicon
                self._learn_to_shared_lexicon(
                    user_input, ai_response, emotional_signals)
                self._save_shared_lexicon()
                result["learned_to_shared"] = True

                # Increase user's trust score significantly for quality contributions
                user_overrides["trust_score"] = min(
                    1.0, user_overrides.get("trust_score", 0.5) + 0.10)
            else:
                # Only slightly decrease trust for low-quality exchanges
                # (don't penalize too hard - learning is messy)
                user_overrides["trust_score"] = max(
                    0.3, user_overrides.get("trust_score", 0.5) - 0.02)

            user_overrides["contributions"] = user_overrides.get(
                "contributions", 0) + 1
            self._save_user_overrides(user_id, user_overrides)

            result["success"] = True
            result["reason"] = reason
            logger.info(
                f"Learned from {user_id}: {reason} - Signals: {len(emotional_signals) if emotional_signals else 0}")

        except Exception as e:
            result["reason"] = str(e)
            logger.error(f"Failed to learn from exchange: {e}")

        return result

    def _log_exchange(
        self,
        user_id: str,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyphs: Optional[List[Dict]] = None,
    ):
        """Append exchange to learning log with optional anonymization.

        Implements:
        - Option A (Gate-Based Data Masking): Strips raw user_input/ai_response
        - Plus Optional B (Intelligent Anonymization): Replaces identifiers with glyphs

        Both protect privacy while preserving learning capability.
        """
        try:
            # Extract signal information for logging
            signal_names = []
            signal_gates = []
            if emotional_signals:
                for signal_dict in emotional_signals:
                    if "signal" in signal_dict:
                        signal_names.append(signal_dict.get("signal"))
                    if "gate" in signal_dict:
                        signal_gates.append(signal_dict.get("gate"))

            # Optionally anonymize the text for deeper privacy
            anonymized_text = user_input
            anonymization_map = None
            anonymization_level = "none"

            if self.anonymization_enabled and self.anonymizer:
                try:
                    entry = {
                        "text": user_input,
                        "metadata": {"timestamp": datetime.now().isoformat()}
                    }
                    anonymized_entry, anonymization_map = self.anonymizer.anonymize_entry(
                        entry, user_id
                    )
                    anonymized_text = anonymized_entry.get("text", user_input)
                    anonymization_level = anonymized_entry.get(
                        "_anonymization_consent_level", "full")
                    logger.debug(
                        f"Anonymized exchange for {user_id}: {len(anonymization_map.identifier_glyphs)} identifiers replaced")
                except Exception as e:
                    logger.warning(
                        f"Anonymization failed, logging without anonymization: {e}")
                    anonymized_text = user_input

            # Privacy-safe log entry (NO raw user_input or ai_response)
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id_hash": user_id,  # Already hashed by caller
                "signals": signal_names,  # Signals only, not the raw text
                "gates": list(set(signal_gates)),  # Which gates were activated
                "glyph_names": [g.get("glyph_name", "") for g in glyphs] if glyphs else [],
                "ai_response_length": len(ai_response),  # Meta info only
                "exchange_quality": "logged",
                "anonymization_level": anonymization_level,
                # REMOVED: "user_input" (raw text - PRIVACY)
                # REMOVED: "ai_response" (content - PRIVACY)
                # KEPT: Only derived signals, gates, and metadata
            }

            # Optionally store anonymization map in separate secure location
            if anonymization_map:
                # Link to stored map
                log_entry["anonymization_map_id"] = user_id

            with open(self.learning_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            logger.debug(
                f"Logged privacy-safe exchange for {user_id}: signals={signal_names}, gates={signal_gates}, anonymization={anonymization_level}")
        except Exception as e:
            logger.warning(f"Could not log exchange: {e}")

    def _learn_to_user_lexicon(
        self,
        user_overrides: Dict,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
    ):
        """Learn to user's personal lexicon (PRIVACY-SAFE).

        Stores signal associations and keywords, NOT full user messages.
        This protects user privacy while still learning emotional patterns.
        """
        if "signals" not in user_overrides:
            user_overrides["signals"] = {}

        if emotional_signals:
            for signal_dict in emotional_signals:
                signal = signal_dict.get("signal")
                keyword = signal_dict.get("keyword")
                if signal and keyword:
                    if signal not in user_overrides["signals"]:
                        user_overrides["signals"][signal] = {
                            "keywords": [],
                            "example_contexts": [],  # Stores signal context, not user text
                            "frequency": 0
                        }

                    entry = user_overrides["signals"][signal]
                    if keyword not in entry["keywords"]:
                        entry["keywords"].append(keyword)

                    # Store SIGNAL CONTEXT (what emotions appear together)
                    # NOT the raw user input
                    signal_context = {
                        "keyword": keyword,
                        "associated_signals": [
                            s.get("signal") for s in emotional_signals
                            if s.get("signal") != signal
                        ],
                        "gates": list(set([
                            s.get("gate") for s in emotional_signals
                            if s.get("gate")
                        ])),
                        # NO user_input stored
                    }
                    entry["example_contexts"].append(signal_context)
                    # Keep last 10
                    entry["example_contexts"] = entry["example_contexts"][-10:]
                    entry["frequency"] = entry.get("frequency", 0) + 1

    def _enrich_lexicon_with_signals(
        self,
        user_input: str,
        poetic_signals: Optional[List[Dict]] = None,
    ):
        """Enrich the signal lexicon with keywords and word combinations.

        Maps detected signals to Greek letter signals and:
        - Adds individual keywords to the lexicon
        - Learns word combinations and phrases
        - Tracks contextual relationships between words
        """
        if not poetic_signals:
            return

        try:
            # Extract meaningful phrases from user input (2-5 word combinations)
            words = user_input.lower().split()
            phrases = []

            # Generate 2-gram and 3-gram phrases
            for i in range(len(words) - 1):
                # 2-word phrases
                phrase2 = f"{words[i]} {words[i+1]}".strip()
                if len(phrase2) > 3:  # Meaningful length
                    phrases.append(phrase2)

                # 3-word phrases
                if i < len(words) - 2:
                    phrase3 = f"{words[i]} {words[i+1]} {words[i+2]}".strip()
                    if len(phrase3) > 5:
                        phrases.append(phrase3)

            # Family-word override set prevents family-context phrases from being
            # promoted into signals like 'sensuality'. Update this set to add
            # other tokens as needed.
            FAMILY_WORDS = {"kids", "kid", "mom", "dad", "mother", "father", "daughter",
                            "son", "child", "children", "wife", "husband", "girlfriend", "boyfriend"}

            for signal_dict in poetic_signals:
                signal_name = signal_dict.get("signal")
                confidence = signal_dict.get("confidence", 0.5)
                keywords = signal_dict.get("keywords", [])
                metaphors = signal_dict.get("metaphors", [])

                if not signal_name:
                    continue

                # Map signal to Greek letter signal
                greek_signal = POETRY_TO_SIGNAL_MAP.get(str(signal_name))
                if not greek_signal:
                    continue

                # Add high-confidence keywords to the main lexicon
                # Raise the confidence threshold slightly to avoid noisy additions
                if confidence > 0.5:  # Only add higher-confidence keywords
                    for keyword in keywords:
                        keyword_lower = keyword.lower().strip()

                        # Skip adding raw family words as keywords to avoid
                        # mapping family tokens into signals like 'sensuality'.
                        if keyword_lower in FAMILY_WORDS:
                            logger.debug(
                                f"Skipped adding family keyword to lexicon: {keyword_lower} → {signal_name}")
                            continue

                        # Check if keyword already exists in lexicon
                        if keyword_lower and keyword_lower not in self.shared_lexicon:
                            # Add new keyword mapping with metadata
                            self.shared_lexicon[keyword_lower] = {
                                "signal": greek_signal,
                                "voltage": "high" if confidence > 0.65 else "medium",
                                "tone": str(signal_name),
                                "source": "learned",
                                "confidence": confidence,
                            }
                            logger.info(
                                f"Added keyword to lexicon: {keyword_lower} → {signal_name}")

                    # Also learn phrase combinations (2-3 word expressions)
                    # Only add phrases that explicitly contain a signal keyword or metaphor
                    for phrase in phrases:
                        if len(phrase.split()) <= 3:
                            # Family-word override: if a phrase contains family tokens,
                            # skip promoting it to signals like 'sensuality'. This
                            # prevents phrases such as 'with my kids' or 'my mom'
                            # from being learned as sensuality.
                            phrase_tokens = set(phrase.lower().replace(
                                '.', '').replace(',', '').split())
                            if phrase_tokens & FAMILY_WORDS:
                                logger.debug(
                                    f"Skipped learning family phrase for {signal_name}: '{phrase}' (family token)")
                                continue

                            # require phrase to contain at least one keyword or metaphor
                            contains_signal_token = any(
                                (kw.lower() in phrase.lower()) for kw in (keywords + metaphors)
                            )
                            if not contains_signal_token:
                                # Skip noisy/general phrases that don't reference the signal
                                logger.debug(
                                    f"Skipped learning noisy phrase for {signal_name}: '{phrase}' (no signal token)")
                                continue

                            if phrase not in self.shared_lexicon:
                                self.shared_lexicon[phrase] = {
                                    "signal": greek_signal,
                                    "voltage": "medium" if confidence > 0.6 else "low",
                                    "tone": str(signal_name),
                                    "source": "learned_phrase",
                                    "confidence": confidence * 0.9,  # Slightly lower confidence for phrases
                                    "phrase_length": len(phrase.split())
                                }
                                logger.info(
                                    f"Added phrase to lexicon: '{phrase}' → {signal_name}")
        except Exception as e:
            logger.warning(f"Failed to enrich lexicon with signals: {e}")

    def _learn_to_shared_lexicon(
        self,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
    ):
        """Learn to shared lexicon (only high-quality exchanges)."""
        if "signals" not in self.shared_lexicon:
            self.shared_lexicon["signals"] = {}

        if emotional_signals:
            for signal_dict in emotional_signals:
                signal = signal_dict.get("signal")
                keyword = signal_dict.get("keyword")
                if signal and keyword:
                    if signal not in self.shared_lexicon["signals"]:
                        self.shared_lexicon["signals"][signal] = {
                            "keywords": [],
                            "examples": [],
                            "frequency": 0,
                            "community_contributed": True
                        }

                    entry = self.shared_lexicon["signals"][signal]
                    if keyword not in entry["keywords"]:
                        entry["keywords"].append(keyword)
                    # Only keep 5 community examples per signal (save space)
                    entry["examples"].append(user_input)
                    entry["examples"] = entry["examples"][-5:]
                    entry["frequency"] = entry.get("frequency", 0) + 1

            # Enrich main lexicon with keywords and word combinations
            self._enrich_lexicon_with_signals(user_input, emotional_signals)

    def _save_shared_lexicon(self):
        """Save shared lexicon back to disk."""
        try:
            with open(self.shared_lexicon_path, 'w') as f:
                json.dump(self.shared_lexicon, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save shared lexicon: {e}")

    def get_learning_stats(self, user_id: Optional[str] = None) -> Dict:
        """Get learning statistics.

        Args:
            user_id: If provided, get user-specific stats. Otherwise get shared stats.
        """
        if user_id:
            overrides = self._load_user_overrides(user_id)
            return {
                "signals_learned": len(overrides.get("signals", {})),
                "contributions": overrides.get("contributions", 0),
                "trust_score": overrides.get("trust_score", 0.5),
                "scope": "user"
            }
        else:
            # Shared stats
            return {
                "signals_in_shared_lexicon": len(self.shared_lexicon.get("signals", {})),
                "learning_log_entries": sum(1 for _ in open(self.learning_log_path)) if Path(self.learning_log_path).exists() else 0,
                "scope": "shared"
            }


# Singleton instance
_hybrid_learner = None


def get_hybrid_learner() -> HybridLearnerWithUserOverrides:
    """Get or create the hybrid learner singleton."""
    global _hybrid_learner
    if _hybrid_learner is None:
        _hybrid_learner = HybridLearnerWithUserOverrides()
    return _hybrid_learner
