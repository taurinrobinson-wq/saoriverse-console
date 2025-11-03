"""
Hybrid Learning with User-Specific Overrides

Architecture:
- Shared base lexicon (built over time from quality interactions)
- Per-user overrides (personal learning)
- Quality filtering to prevent toxic content from poisoning shared lexicon
- Trust scoring for contributions
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class HybridLearnerWithUserOverrides:
    """Learn from conversations with per-user personalization and quality filtering."""

    def __init__(
        self,
        shared_lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
        learning_log_path: str = "learning/hybrid_learning_log.jsonl",
        user_overrides_dir: str = "learning/user_overrides",
    ):
        """Initialize the hybrid learner with user overrides.
        
        Args:
            shared_lexicon_path: Shared lexicon all users benefit from
            db_path: Shared glyphs database
            learning_log_path: Append-only learning log
            user_overrides_dir: Directory for per-user learning
        """
        self.shared_lexicon_path = shared_lexicon_path
        self.db_path = db_path
        self.learning_log_path = learning_log_path
        self.user_overrides_dir = user_overrides_dir
        
        # Ensure directories exist
        Path(learning_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(user_overrides_dir).mkdir(parents=True, exist_ok=True)
        
        self.shared_lexicon = self._load_shared_lexicon()
        
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
            user_file = Path(self.user_overrides_dir) / f"{user_id}_lexicon.json"
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
        # Check for minimum quality signals
        if not emotional_signals or len(emotional_signals) == 0:
            return False, "no_emotional_signals"
        
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
        # The "pause for breath" template should NOT appear multiple times
        template_count = ai_response.lower().count("pause for a breath")
        if template_count > 1:
            return False, "repetitive_template"
        
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
            emotional_signals: Detected emotional signals
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
            # 1. Log the exchange
            self._log_exchange(user_id, user_input, ai_response, emotional_signals, glyphs)
            
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
                self._learn_to_shared_lexicon(user_input, ai_response, emotional_signals)
                self._save_shared_lexicon()
                result["learned_to_shared"] = True
                
                # Increase user's trust score significantly for quality contributions
                user_overrides["trust_score"] = min(1.0, user_overrides.get("trust_score", 0.5) + 0.10)
            else:
                # Only slightly decrease trust for low-quality exchanges
                # (don't penalize too hard - learning is messy)
                user_overrides["trust_score"] = max(0.3, user_overrides.get("trust_score", 0.5) - 0.02)
            
            user_overrides["contributions"] = user_overrides.get("contributions", 0) + 1
            self._save_user_overrides(user_id, user_overrides)
            
            result["success"] = True
            result["reason"] = reason
            logger.info(f"Learned from {user_id}: {reason}")
            
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
        """Append exchange to learning log."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "user_input": user_input,
                "ai_response": ai_response,
                "emotional_signals": emotional_signals or [],
                "glyphs": [g.get("glyph_name", "") for g in glyphs] if glyphs else [],
            }
            
            with open(self.learning_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.warning(f"Could not log exchange: {e}")
    
    def _learn_to_user_lexicon(
        self,
        user_overrides: Dict,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
    ):
        """Learn to user's personal lexicon."""
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
                            "examples": [],
                            "frequency": 0
                        }
                    
                    entry = user_overrides["signals"][signal]
                    if keyword not in entry["keywords"]:
                        entry["keywords"].append(keyword)
                    entry["examples"].append(user_input)
                    entry["examples"] = entry["examples"][-10]  # Keep last 10
                    entry["frequency"] = entry.get("frequency", 0) + 1
    
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
                    entry["examples"] = entry["examples"][-5]
                    entry["frequency"] = entry.get("frequency", 0) + 1
    
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
