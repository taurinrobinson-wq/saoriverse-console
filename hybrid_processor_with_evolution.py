#!/usr/bin/env python3
"""
Hybrid Processor with Dynamic Glyph Evolution

Extends the conversation pipeline to automatically:
1. Learn from user-AI exchanges through hybrid processor
2. Expand lexicon with adaptive signal extraction
3. Detect new emotional patterns
4. Generate new glyphs dynamically
5. Make new glyphs available for next dialogue turns

This is the complete integration point for the full system.
"""

import json
import logging
from typing import Dict, List, Optional
from uuid import uuid4

# Import lexicon-aware response generation
try:
    from lexicon_aware_response_generator import LexiconAwareResponseGenerator
    LEXICON_AWARE_AVAILABLE = True
except ImportError:
    LEXICON_AWARE_AVAILABLE = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class HybridProcessorWithEvolution:
    """
    Complete processing pipeline with dynamic glyph evolution.
    
    Integration flow:
    Conversation Input → Signal Extraction (Adaptive) → Lexicon Learning → Pattern Detection → Glyph Generation
    ↑                                                                                               ↓
    └─────────────────── New Glyphs Available for System Use ──────────────────────────────────┘
    """
    
    def __init__(
        self,
        hybrid_learner,
        adaptive_extractor,
        dynamic_glyph_evolution,
        user_id: str = "default",
        auto_track_conversations: bool = True,
    ):
        """Initialize the integrated processor.
        
        Args:
            hybrid_learner: HybridLearnerWithUserOverrides instance
            adaptive_extractor: AdaptiveSignalExtractor for discovering new dimensions
            dynamic_glyph_evolution: DynamicGlyphEvolution instance
            user_id: Default user identifier
            auto_track_conversations: Whether to auto-generate conversation IDs
        """
        self.learner = hybrid_learner
        self.extractor = adaptive_extractor
        self.evolution = dynamic_glyph_evolution
        self.user_id = user_id
        self.auto_track_conversations = auto_track_conversations
        
        # Initialize lexicon-aware response generator
        self.lexicon_aware_generator = None
        if LEXICON_AWARE_AVAILABLE:
            self.lexicon_aware_generator = LexiconAwareResponseGenerator(
                hybrid_learner=hybrid_learner
            )
        
        self.conversation_history = []
        self.generated_glyphs = []
        
        logger.info("[HYBRID PROCESSOR] Initialized with dynamic glyph evolution")
        logger.info(f"  - Hybrid Learner: ready")
        logger.info(f"  - Adaptive Extractor: {adaptive_extractor.__class__.__name__ if adaptive_extractor else 'N/A'}")
        logger.info(f"  - Glyph Evolution: connected")
        if self.lexicon_aware_generator:
            logger.info(f"  - Lexicon-Aware Generator: ready")
            logger.info(f"    → Responses will be personalized based on learned patterns")
    
    def process_user_message(
        self,
        user_message: str,
        ai_response: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        glyphs: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Process a user-AI exchange through the full pipeline.
        
        Args:
            user_message: User's input
            ai_response: AI's response
            user_id: User identifier (uses default if not provided)
            conversation_id: Conversation ID (auto-generates if not provided)
            glyphs: Pre-identified glyphs (optional)
            
        Returns:
            Complete result with learning, lexicon updates, and new glyphs
        """
        if user_id is None:
            user_id = self.user_id
        
        if conversation_id is None:
            if self.auto_track_conversations:
                conversation_id = str(uuid4())[:8]
            else:
                conversation_id = "unknown"
        
        logger.info(f"\n[PROCESSING] User message from {user_id}")
        logger.info(f"  Conversation: {conversation_id}")
        
        result = {
            "status": "processing",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "pipeline_stages": {},
        }
        
        try:
            # STAGE 1: Extract signals (adaptive - may discover new dimensions)
            logger.info("[STAGE 1] Signal Extraction (Adaptive)")
            emotional_signals = self._extract_signals(user_message, ai_response)
            signal_names = [s.get("signal") or s.get("name") for s in emotional_signals]
            result["pipeline_stages"]["signal_extraction"] = {
                "signals_found": len(emotional_signals),
                "signals": signal_names,
            }
            logger.info(f"  ✓ Extracted {len(emotional_signals)} signals")
            if emotional_signals:
                signal_str = ', '.join([str(s) for s in signal_names if s])
                logger.info(f"    Signals: {signal_str}")
            
            # STAGE 2: Hybrid Learning (user overrides + shared lexicon)
            logger.info("[STAGE 2] Hybrid Learning")
            learning_result = self.evolution.process_dialogue_exchange(
                user_id=user_id,
                conversation_id=conversation_id,
                user_input=user_message,
                ai_response=ai_response,
                emotional_signals=emotional_signals,
                glyphs=glyphs,
            )
            result["pipeline_stages"]["hybrid_learning"] = learning_result
            logger.info(f"  ✓ Learning complete: {learning_result.get('learning_result', {}).get('success', False)}")
            
            # STAGE 3: Lexicon Updates
            logger.info("[STAGE 3] Lexicon Analysis")
            lexicon_info = learning_result.get("lexicon_updates", {})
            result["pipeline_stages"]["lexicon"] = lexicon_info
            if lexicon_info:
                logger.info(f"  ✓ Lexicon contains {lexicon_info.get('signal_count', 0)} signals")
            
            # STAGE 4: Pattern Detection & Glyph Generation
            logger.info("[STAGE 4] Pattern Detection & Glyph Generation")
            new_glyphs = learning_result.get("new_glyphs_generated", [])
            patterns = learning_result.get("pattern_analysis", [])
            
            glyph_result = {
                "new_glyphs_count": len(new_glyphs),
                "patterns_detected": len(patterns) if patterns else 0,
                "new_glyphs": [g.to_dict() if hasattr(g, 'to_dict') else g for g in new_glyphs],
            }
            result["pipeline_stages"]["glyph_generation"] = glyph_result
            
            if new_glyphs:
                logger.info(f"  ✓ Generated {len(new_glyphs)} new glyphs:")
                for glyph in new_glyphs:
                    glyph_dict = glyph.to_dict() if hasattr(glyph, 'to_dict') else glyph
                    logger.info(f"    - {glyph_dict.get('symbol', '?')} {glyph_dict.get('name', '?')}")
                    self.generated_glyphs.append(glyph_dict)
            else:
                logger.info(f"  ℹ No new glyphs generated (need more pattern frequency)")
            
            # Add to conversation history
            self.conversation_history.append({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "signals": emotional_signals,
                "new_glyphs": new_glyphs,
                "result": result,
            })
            
            result["status"] = "success"
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}", exc_info=True)
            result["status"] = "error"
            result["error"] = str(e)
        
        logger.info(f"[DONE] Processing complete for {user_id}\n")
        
        return result
    
    def _extract_signals(
        self,
        user_message: str,
        ai_response: str,
    ) -> List[Dict]:
        """Extract emotional signals using adaptive extractor."""
        try:
            combined_text = user_message + " " + ai_response
            
            if self.extractor:
                signals = self.extractor.extract_signals(combined_text)
            else:
                # Fallback to poetry extractor
                from emotional_os.learning.poetry_signal_extractor import get_poetry_extractor
                extractor = get_poetry_extractor()
                signals = extractor.extract_signals(combined_text)
            
            return signals if signals else []
        except Exception as e:
            logger.warning(f"Signal extraction failed: {e}")
            return []
    
    def get_all_generated_glyphs(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all glyphs generated during this session."""
        glyphs = self.generated_glyphs
        if limit:
            glyphs = glyphs[-limit:]
        return glyphs
    
    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get summary of a specific conversation."""
        conv_data = [c for c in self.conversation_history if c["conversation_id"] == conversation_id]
        
        if not conv_data:
            return {"found": False}
        
        summary = {
            "found": True,
            "conversation_id": conversation_id,
            "turns": len(conv_data),
            "all_signals": [],
            "all_glyphs_generated": [],
            "user_id": conv_data[0].get("user_id"),
        }
        
        for turn in conv_data:
            summary["all_signals"].extend(turn.get("signals", []))
            summary["all_glyphs_generated"].extend(turn.get("new_glyphs", []))
        
        return summary
    
    def print_session_summary(self):
        """Print summary of all processing in this session."""
        print("\n" + "=" * 80)
        print("HYBRID PROCESSOR SESSION SUMMARY")
        print("=" * 80)
        
        print(f"\nTotal conversations processed: {len(set(c['conversation_id'] for c in self.conversation_history))}")
        print(f"Total turns processed: {len(self.conversation_history)}")
        print(f"Total new glyphs generated: {len(self.generated_glyphs)}")
        
        if self.generated_glyphs:
            print(f"\nNEW GLYPHS GENERATED:")
            for i, glyph in enumerate(self.generated_glyphs, 1):
                emotions = " + ".join(glyph.get("core_emotions", []))
                print(f"  {i}. {glyph.get('symbol', '?')} {glyph.get('name', '?')} ({emotions})")
        
        print("\n" + "=" * 80 + "\n")
    
    def export_session_glyphs(self, output_file: str) -> Dict:
        """Export all session-generated glyphs to file."""
        try:
            export_data = {
                "source": "hybrid_processor_session",
                "glyphs": self.generated_glyphs,
                "count": len(self.generated_glyphs),
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"✓ Exported {len(self.generated_glyphs)} glyphs to {output_file}")
            return {"success": True, "count": len(self.generated_glyphs), "file": output_file}
        
        except Exception as e:
            logger.error(f"Failed to export glyphs: {e}")
            return {"success": False, "error": str(e)}
    
    def enhance_response_with_learned_context(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_context: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Enhance a response using learned lexicon context.
        
        This is called BEFORE generating an AI response to get personalization
        guidance based on what the system has learned about the user.
        
        Args:
            user_message: User's input
            user_id: User identifier
            conversation_context: Previous messages for context
            
        Returns:
            Dict with personalized response, associations, and confidence
        """
        if user_id is None:
            user_id = self.user_id
        
        if not self.lexicon_aware_generator:
            logger.warning("Lexicon-aware generator not available")
            return {}
        
        result = self.lexicon_aware_generator.generate_response(
            user_message=user_message,
            user_id=user_id,
            conversation_context=conversation_context,
        )
        
        logger.info(f"[LEXICON-AWARE] Personalization level: {result.get('personalization_level')}")
        if result.get('trigger_keywords'):
            logger.info(f"  Learned associations: {result.get('trigger_keywords')}")
        
        return result


# Factory function for easy setup
def create_integrated_processor(
    hybrid_learner,
    adaptive_extractor=None,
    user_id: str = "default",
) -> HybridProcessorWithEvolution:
    """
    Factory to create an integrated processor with all components.
    
    Args:
        hybrid_learner: HybridLearnerWithUserOverrides instance
        adaptive_extractor: AdaptiveSignalExtractor (optional, will use standard if not provided)
        user_id: Default user ID
        
    Returns:
        Fully initialized HybridProcessorWithEvolution instance
    """
    from dynamic_glyph_evolution import integrate_evolution_with_processor
    
    # Create evolution system
    evolution = integrate_evolution_with_processor(
        hybrid_learner=hybrid_learner,
        adaptive_extractor=adaptive_extractor,
    )
    
    # Create integrated processor
    processor = HybridProcessorWithEvolution(
        hybrid_learner=hybrid_learner,
        adaptive_extractor=adaptive_extractor,
        dynamic_glyph_evolution=evolution,
        user_id=user_id,
    )
    
    logger.info("\n✓ FULL INTEGRATION COMPLETE")
    logger.info("  Pipeline: Dialogue → Signals → Learning → Patterns → Glyphs")
    logger.info("  Ready for live conversations\n")
    
    return processor


if __name__ == "__main__":
    print("Hybrid Processor with Dynamic Glyph Evolution")
    print("=" * 80)
    print("\nUsage:")
    print("  from hybrid_processor_with_evolution import create_integrated_processor")
    print("  processor = create_integrated_processor(hybrid_learner, adaptive_extractor)")
    print("  result = processor.process_user_message(user_msg, ai_response)")
    print("\nThe processor automatically:")
    print("  1. Extracts signals (adaptive - discovers new dimensions)")
    print("  2. Learns through hybrid processor (user + shared lexicon)")
    print("  3. Detects patterns in dialogue")
    print("  4. Generates new glyphs from patterns")
    print("  5. Makes glyphs available for system use")
    print("=" * 80)
