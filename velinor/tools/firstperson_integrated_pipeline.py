"""
FirstPerson Integrated Pipeline
================================

Complete response generation pipeline integrating:
- Tier 1: Foundation (safety, learning, signals)
- Tier 2: Aliveness (emotional sync, energy, presence)
- Tier 3: Poetic Consciousness (depth, beauty, tension)
- FirstPerson modules (affect parsing, glyph selection, composition)

Performance target: <100ms per response
Architecture: 7-stage pipeline with graceful degradation
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
    """Track performance of each stage."""
    tier1_time: float = 0.0
    tier2_time: float = 0.0
    tier3_time: float = 0.0
    total_time: float = 0.0
    stages_executed: Optional[List[str]] = None

    def __post_init__(self):
        if self.stages_executed is None:
            self.stages_executed = []


class FirstPersonIntegratedPipeline:
    """
    Orchestrates all response generation through unified pipeline.
    
    Flow:
    1. Tier 1 Foundation: Safety check, signal detection, base response generation
    2. Tier 2 Aliveness: Emotional attunement, energy tracking, presence
    3. Tier 3 Poetic: Poetry, aesthetics, tension, narrative weaving
    4. Composition: Template rotation, prosody finalization
    5. Return enhanced response
    """

    def __init__(self, conversation_memory=None):
        """Initialize integrated pipeline with all tiers."""
        self.memory = conversation_memory
        self.metrics = PipelineMetrics()
        
        # Try to import and initialize Tier 1
        try:
            from src.emotional_os.tier1_foundation import Tier1Foundation
            self.tier1 = Tier1Foundation(conversation_memory=conversation_memory)
            logger.info("✓ Tier 1 Foundation initialized")
        except Exception as e:
            logger.warning(f"Tier 1 Foundation not available: {e}")
            self.tier1 = None
        
        # Try to import and initialize Tier 2
        try:
            from src.emotional_os.tier2_aliveness import Tier2Aliveness
            self.tier2 = Tier2Aliveness()
            logger.info("✓ Tier 2 Aliveness initialized")
        except Exception as e:
            logger.warning(f"Tier 2 Aliveness not available: {e}")
            self.tier2 = None
        
        # Try to import and initialize Tier 3
        try:
            from src.emotional_os.tier3_poetic_consciousness import Tier3PoeticConsciousness
            self.tier3 = Tier3PoeticConsciousness()
            logger.info("✓ Tier 3 Poetic Consciousness initialized")
        except Exception as e:
            logger.warning(f"Tier 3 Poetic Consciousness not available: {e}")
            self.tier3 = None
        
        # Try to import FirstPerson composition modules
        try:
            from src.emotional_os.core.firstperson.response_templates import ResponseTemplates
            self.response_templates = ResponseTemplates()
            logger.info("✓ Response Templates initialized")
        except Exception as e:
            logger.warning(f"Response Templates not available: {e}")
            self.response_templates = None
        
        try:
            from src.emotional_os.core.firstperson.affect_parser import AffectParser
            self.affect_parser = AffectParser()
            logger.info("✓ Affect Parser initialized")
        except Exception as e:
            logger.warning(f"Affect Parser not available: {e}")
            self.affect_parser = None
        
        try:
            from src.emotional_os.core.firstperson.context_selector import ContextAwareSelector
            self.context_selector = ContextAwareSelector()
            logger.info("✓ Context Selector initialized")
        except Exception as e:
            logger.warning(f"Context Selector not available: {e}")
            self.context_selector = None

    def process_response(
        self,
        user_input: str,
        base_response: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process response through complete pipeline.
        
        Args:
            user_input: User's message
            base_response: Initial response (from generate_empathetic_response)
            conversation_history: Prior conversation turns
            context: Additional context (user_id, etc.)
        
        Returns:
            (enhanced_response, metadata)
        """
        pipeline_start = time.perf_counter()
        self.metrics = PipelineMetrics()
        self.metrics.stages_executed = []  # Initialize empty list
        
        try:
            # ===== TIER 1: FOUNDATION =====
            enhanced_response = base_response
            tier1_metadata = {}
            
            if self.tier1:
                try:
                    tier1_start = time.perf_counter()
                    enhanced_response, tier1_perf = self.tier1.process_response(
                        user_input=user_input,
                        base_response=base_response,
                        context=context
                    )
                    self.metrics.tier1_time = time.perf_counter() - tier1_start
                    self.metrics.stages_executed.append("tier1")
                    tier1_metadata = tier1_perf
                    logger.debug(f"Tier 1 processed in {self.metrics.tier1_time*1000:.1f}ms")
                except Exception as e:
                    logger.warning(f"Tier 1 processing failed: {e}, continuing with base response")
                    self.metrics.tier1_time = 0
            
            # ===== TIER 2: ALIVENESS =====
            if self.tier2:
                try:
                    tier2_start = time.perf_counter()
                    enhanced_response, tier2_perf = self.tier2.process_for_aliveness(
                        user_input=user_input,
                        base_response=enhanced_response,
                        history=conversation_history
                    )
                    self.metrics.tier2_time = time.perf_counter() - tier2_start
                    self.metrics.stages_executed.append("tier2")
                    logger.debug(f"Tier 2 processed in {self.metrics.tier2_time*1000:.1f}ms")
                except Exception as e:
                    logger.warning(f"Tier 2 processing failed: {e}, continuing with current response")
                    self.metrics.tier2_time = 0
            
            # ===== TIER 3: POETIC CONSCIOUSNESS =====
            if self.tier3:
                try:
                    tier3_start = time.perf_counter()
                    tier3_context = {
                        "theme": self._detect_theme(user_input),
                        "history": conversation_history or []
                    }
                    enhanced_response, tier3_perf = self.tier3.process_for_poetry(
                        response=enhanced_response,
                        context=tier3_context
                    )
                    self.metrics.tier3_time = time.perf_counter() - tier3_start
                    self.metrics.stages_executed.append("tier3")
                    logger.debug(f"Tier 3 processed in {self.metrics.tier3_time*1000:.1f}ms")
                except Exception as e:
                    logger.warning(f"Tier 3 processing failed: {e}, continuing with current response")
                    self.metrics.tier3_time = 0
            
            # ===== COMPOSITION: Affect analysis for metadata =====
            metadata = {
                "response": enhanced_response,
                "pipeline_metrics": {
                    "tier1_ms": self.metrics.tier1_time * 1000,
                    "tier2_ms": self.metrics.tier2_time * 1000,
                    "tier3_ms": self.metrics.tier3_time * 1000,
                    "stages_executed": self.metrics.stages_executed
                }
            }
            
            # Add affect analysis if available
            if self.affect_parser:
                try:
                    affect = self.affect_parser.analyze_affect(user_input)
                    metadata["affect"] = {
                        "tone": affect.tone,
                        "valence": affect.valence,
                        "arousal": affect.arousal
                    }
                except Exception as e:
                    logger.debug(f"Affect parsing failed: {e}")
            
            # Track total time
            self.metrics.total_time = time.perf_counter() - pipeline_start
            metadata["total_ms"] = self.metrics.total_time * 1000
            
            # Log if over budget
            if self.metrics.total_time > 0.1:
                logger.warning(f"Pipeline exceeded 100ms budget: {self.metrics.total_time*1000:.1f}ms")
            
            return enhanced_response, metadata
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.metrics.total_time = time.perf_counter() - pipeline_start
            return base_response, {
                "error": str(e),
                "total_ms": self.metrics.total_time * 1000
            }

    def _detect_theme(self, user_input: str) -> str:
        """Detect primary emotional theme from input."""
        text_lower = user_input.lower()
        
        if any(word in text_lower for word in ["grief", "loss", "died", "death", "mourning", "lost", "missing"]):
            return "grief"
        elif any(word in text_lower for word in ["joy", "happy", "excited", "wonderful", "amazing", "love"]):
            return "joy"
        elif any(word in text_lower for word in ["anxiety", "worried", "anxious", "nervous", "scared", "afraid"]):
            return "anxiety"
        elif any(word in text_lower for word in ["overwhelmed", "overwhelm", "drowning", "too much", "burden"]):
            return "overwhelm"
        elif any(word in text_lower for word in ["tired", "exhausted", "fatigue", "drained", "weary"]):
            return "fatigue"
        else:
            return "general"

    def get_metrics(self) -> Dict[str, Any]:
        """Return pipeline metrics."""
        return {
            "tier1_ms": self.metrics.tier1_time * 1000,
            "tier2_ms": self.metrics.tier2_time * 1000,
            "tier3_ms": self.metrics.tier3_time * 1000,
            "total_ms": self.metrics.total_time * 1000,
            "stages": self.metrics.stages_executed if self.metrics.stages_executed else []
        }


# Module-level initialization for convenience
_pipeline_instance = None


def get_pipeline(conversation_memory=None) -> FirstPersonIntegratedPipeline:
    """Get or create the global pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = FirstPersonIntegratedPipeline(conversation_memory=conversation_memory)
    return _pipeline_instance


def process_response(
    user_input: str,
    base_response: str,
    conversation_history: Optional[List[Dict]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Process response through integrated pipeline."""
    pipeline = get_pipeline()
    return pipeline.process_response(user_input, base_response, conversation_history, context)
