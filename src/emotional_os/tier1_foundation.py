"""
Tier 1 Foundation - Response handler with LexiconLearner + Safety (Sanctuary).

Architecture: 7-stage pipeline for <100ms response times
1. Memory tracking (context awareness if available)
2. Safety checking (Sanctuary risk classification)
3. Signal detection (emotional signal parsing)
4. Response generation (context-aware composition)
5. Learning update (LexiconLearner from exchange)
6. Compassion wrapping (ensure_sanctuary_response)
7. Final memory update

Performance target: <100ms per response
Local only: NRC, Spacy, TextBlob, regex patterns
"""

import logging
import time
import json
from typing import Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class Tier1Foundation:
    """
    Unified response pipeline with Tier 1 foundation components.
    
    Integrates:
    - LexiconLearner: Learn user's emotional vocabulary
    - Sanctuary: Detect sensitive content and offer compassionate wrapping
    - Optional: ConversationMemory for context tracking
    """
    
    def __init__(self, conversation_memory=None):
        """
        Initialize Tier 1 components.
        
        Args:
            conversation_memory: Optional ConversationMemory instance for context
        """
        self.perf_times = {}
        self.memory = conversation_memory
        
        # Import LexiconLearner from core
        try:
            from emotional_os.core.lexicon_learner import LexiconLearner
            self.lexicon_learner = LexiconLearner()
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"LexiconLearner not available: {e}, using stub")
            self.lexicon_learner = None
        
        # Import signal parser from core
        try:
            from emotional_os.core.signal_parser import parse_signals, load_signal_map
            from emotional_os.core.constants import DEFAULT_GLYPH_DB
            self.parse_signals = parse_signals
            try:
                # Load signal map with required parameters
                self._signal_map = load_signal_map(base_path=DEFAULT_GLYPH_DB)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as file_error:
                logger.warning(f"Could not load signal map file: {file_error}")
                self._signal_map = {}
        except (ImportError, ModuleNotFoundError, TypeError) as e:
            logger.warning(f"Signal parser not available: {e}")
            self.parse_signals = lambda x, signal_map: {}
            self._signal_map = {}
        
        # Import Safety/Sanctuary components from sibling module
        try:
            import emotional_os_safety
            self.is_sensitive_input = emotional_os_safety.is_sensitive_input
            self.ensure_sanctuary_response = emotional_os_safety.ensure_sanctuary_response
            self.classify_risk = getattr(emotional_os_safety, 'classify_risk', lambda x: "none")
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            logger.warning(f"Sanctuary not available: {e}, using stubs")
            self.is_sensitive_input = lambda x: False
            self.ensure_sanctuary_response = lambda input_text, response, **kwargs: response
            self.classify_risk = lambda x: "none"
    
    def process_response(
        self,
        user_input: str,
        base_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, float]]:
        """
        TIER 1: Foundation layer - enhance response with learning and safety.
        
        Flow:
        1. Track in memory (for context)
        2. Check sensitivity (Sanctuary)
        3. Classify risk (low/medium/high/severe)
        4. Learn from input (expand lexicon)
        5. Wrap with compassion (if sensitive)
        6. Update memory (if available)
        
        Args:
            user_input: User's message
            base_response: Initial response to enhance
            context: Optional contextual data
            
        Returns:
            (enhanced_response, perf_metrics)
        """
        total_start = time.perf_counter()
        self.perf_times = {}
        
        try:
            # Initialize all metric keys upfront
            self.perf_times = {
                "memory": 0.0,
                "safety_check": 0.0,
                "signal_detection": 0.0,
                "generation": 0.0,
                "learning": 0.0,
                "wrapping": 0.0,
                "total": 0.0,
            }
            
            # ========== STAGE 1: MEMORY TRACKING ==========
            if self.memory:
                try:
                    stage_start = time.perf_counter()
                    self.memory.add_turn(user_input, base_response)
                    self.perf_times["memory"] = time.perf_counter() - stage_start
                except Exception as e:
                    logger.warning(f"Memory tracking failed: {e}")
                    self.perf_times["memory"] = 0
            
            # ========== STAGE 2: SAFETY CHECKING ==========
            try:
                stage_start = time.perf_counter()
                is_sensitive = self.is_sensitive_input(user_input)
                risk_level = self.classify_risk(user_input)
                self.perf_times["safety_check"] = time.perf_counter() - stage_start
            except Exception as e:
                logger.warning(f"Safety check failed: {e}")
                is_sensitive = False
                risk_level = "none"
                self.perf_times["safety_check"] = 0
            
            # ========== STAGE 3: SIGNAL DETECTION ==========
            try:
                stage_start = time.perf_counter()
                # parse_signals(input_text, signal_map)
                if self._signal_map:
                    signals = self.parse_signals(user_input, self._signal_map)
                else:
                    signals = []
                self.perf_times["signal_detection"] = time.perf_counter() - stage_start
            except Exception as e:
                logger.warning(f"Signal detection failed: {e}")
                signals = []
                self.perf_times["signal_detection"] = 0
            
            # ========== STAGE 4: RESPONSE AVAILABLE ==========
            # (base_response already provided, skip generation)
            current_response = base_response
            self.perf_times["generation"] = 0
            
            # ========== STAGE 5: LEARNING UPDATE ==========
            try:
                stage_start = time.perf_counter()
                if self.lexicon_learner and signals:
                    # Use learn_from_conversation instead of learn_from_exchange
                    conversation_data = {
                        "messages": [
                            {"type": "user", "content": user_input},
                            {"type": "system", "content": current_response},
                        ]
                    }
                    self.lexicon_learner.learn_from_conversation(conversation_data)
                self.perf_times["learning"] = time.perf_counter() - stage_start
            except Exception as e:
                logger.warning(f"Learning update failed: {e}")
                self.perf_times["learning"] = 0
            
            # ========== STAGE 6: COMPASSION WRAPPING ==========
            try:
                stage_start = time.perf_counter()
                if is_sensitive or risk_level in ["high", "severe"]:
                    # ensure_sanctuary_response takes: input_text, base_response, tone, locale
                    current_response = self.ensure_sanctuary_response(
                        user_input,
                        current_response,
                        tone="gentle",
                        locale="US",
                    )
                self.perf_times["wrapping"] = time.perf_counter() - stage_start
            except Exception as e:
                logger.warning(f"Compassion wrapping failed: {e}")
                self.perf_times["wrapping"] = 0
            
            # ========== STAGE 7: FINAL MEMORY UPDATE ==========
            if self.memory and current_response != base_response:
                try:
                    self.memory.add_turn(user_input, current_response, update=True)
                except Exception:
                    pass
            
            # Calculate total time
            total_time = time.perf_counter() - total_start
            self.perf_times["total"] = total_time
            
            # Log if over 100ms
            if total_time > 0.1:
                logger.warning(f"Tier 1 pipeline exceeded 100ms: {total_time:.3f}s")
            
            return current_response, self.perf_times
        
        except Exception as e:
            logger.error(f"Tier 1 pipeline failed: {e}")
            self.perf_times["total"] = time.perf_counter() - total_start
            return base_response, self.perf_times
    
    def get_context_from_memory(self) -> Optional[Dict[str, Any]]:
        """Get context from conversation memory if available."""
        if not self.memory:
            return None
        
        try:
            return self.memory.get_context()
        except Exception as e:
            logger.warning(f"Failed to get memory context: {e}")
            return None
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Return performance metrics from last pipeline execution."""
        return self.perf_times.copy()
