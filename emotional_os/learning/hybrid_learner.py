"""
Hybrid Mode Learning Pipeline

Automatically learns from hybrid mode conversations to improve local mode responses.
Every user-input + AI-response pair is analyzed and used to:
1. Expand the signal lexicon with new emotional patterns
2. Generate new glyphs based on response quality
3. Build a growing knowledge base for local mode

This creates a feedback loop where cloud responses train the local system.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class HybridLearner:
    """Learn from hybrid mode conversations to improve local mode."""

    def __init__(
        self,
        lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
        learning_log_path: str = "learning/hybrid_learning_log.jsonl",
    ):
        """Initialize the hybrid learner.
        
        Args:
            lexicon_path: Path to signal lexicon JSON
            db_path: Path to glyphs database
            learning_log_path: Path to learning log (append-only)
        """
        self.lexicon_path = lexicon_path
        self.db_path = db_path
        self.learning_log_path = learning_log_path
        
        # Ensure learning log directory exists
        Path(learning_log_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.lexicon = self._load_lexicon()
        
    def _load_lexicon(self) -> Dict:
        """Load the signal lexicon."""
        try:
            with open(self.lexicon_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load lexicon: {e}")
            return {"signals": {}}
    
    def _save_lexicon(self):
        """Save lexicon back to disk."""
        try:
            with open(self.lexicon_path, 'w') as f:
                json.dump(self.lexicon, f, indent=2)
            logger.info("Lexicon saved")
        except Exception as e:
            logger.error(f"Failed to save lexicon: {e}")
    
    def learn_from_exchange(
        self,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyphs: Optional[List[Dict]] = None,
    ) -> bool:
        """Learn from a single user-AI exchange.
        
        Args:
            user_input: What the user said
            ai_response: The AI's response
            emotional_signals: Detected emotional signals
            glyphs: Matched glyphs
            
        Returns:
            True if learning succeeded, False otherwise
        """
        try:
            # 1. Log the exchange
            self._log_exchange(user_input, ai_response, emotional_signals, glyphs)
            
            # 2. Extract patterns from user input
            user_patterns = self._extract_patterns(user_input)
            
            # 3. If we have emotional signals from the AI analysis, use them
            if emotional_signals:
                for signal_dict in emotional_signals:
                    signal = signal_dict.get("signal")
                    keyword = signal_dict.get("keyword")
                    if signal and keyword:
                        self._learn_signal_pattern(signal, keyword, user_input)
            
            # 4. Learn from the AI response (what makes good responses)
            self._learn_response_pattern(user_input, ai_response, emotional_signals)
            
            # 5. Save updated lexicon
            self._save_lexicon()
            
            logger.info(f"Learned from exchange: '{user_input[:50]}...'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to learn from exchange: {e}")
            return False
    
    def _log_exchange(
        self,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyphs: Optional[List[Dict]] = None,
    ):
        """Append exchange to learning log."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "ai_response": ai_response,
                "emotional_signals": emotional_signals or [],
                "glyphs": [g.get("glyph_name", "") for g in glyphs] if glyphs else [],
            }
            
            with open(self.learning_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.warning(f"Could not log exchange: {e}")
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract key phrases/words from text."""
        # Simple approach: split on common delimiters, keep multi-word phrases
        words = text.lower().split()
        return words[:10]  # First 10 words as patterns
    
    def _learn_signal_pattern(self, signal: str, keyword: str, user_input: str):
        """Learn that a keyword is associated with a signal.
        
        Updates lexicon to remember this pattern.
        """
        if "signals" not in self.lexicon:
            self.lexicon["signals"] = {}
        
        if signal not in self.lexicon["signals"]:
            self.lexicon["signals"][signal] = {"keywords": [], "examples": []}
        
        signal_entry = self.lexicon["signals"][signal]
        
        # Add keyword if new
        if keyword not in signal_entry["keywords"]:
            signal_entry["keywords"].append(keyword)
        
        # Add example (keep last 5)
        signal_entry["examples"].append(user_input)
        signal_entry["examples"] = signal_entry["examples"][-5:]
        
        # Track frequency
        if "frequency" not in signal_entry:
            signal_entry["frequency"] = 0
        signal_entry["frequency"] += 1
    
    def _learn_response_pattern(
        self,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
    ):
        """Learn what makes good responses for certain inputs.
        
        Store response patterns in the glyph database.
        """
        try:
            if not emotional_signals:
                return
            
            signal = emotional_signals[0].get("signal") if emotional_signals else "neutral"
            
            # Store learned response pattern in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists, if not create it
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_responses (
                    id INTEGER PRIMARY KEY,
                    signal TEXT,
                    user_pattern TEXT,
                    response TEXT,
                    quality INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    learned_from TEXT DEFAULT 'hybrid'
                )
            """)
            
            cursor.execute(
                """
                INSERT INTO learned_responses (signal, user_pattern, response, learned_from)
                VALUES (?, ?, ?, 'hybrid')
                """,
                (signal, user_input[:100], ai_response[:200])
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not store response pattern: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about what the system has learned."""
        stats = {
            "total_signals_known": len(self.lexicon.get("signals", {})),
            "learning_log_entries": 0,
            "signals_by_frequency": {},
        }
        
        # Count log entries
        try:
            with open(self.learning_log_path, 'r') as f:
                stats["learning_log_entries"] = sum(1 for _ in f)
        except:
            pass
        
        # Get signal frequencies
        for signal, data in self.lexicon.get("signals", {}).items():
            freq = data.get("frequency", 0)
            if freq > 0:
                stats["signals_by_frequency"][signal] = freq
        
        return stats


# Singleton instance
_hybrid_learner = None


def get_hybrid_learner() -> HybridLearner:
    """Get or create the hybrid learner singleton."""
    global _hybrid_learner
    if _hybrid_learner is None:
        _hybrid_learner = HybridLearner()
    return _hybrid_learner
