#!/usr/bin/env python3
"""
Lexicon-Aware Response Generator

Creates nuanced, personalized responses based on learned user vocabulary and patterns.
This bridges the gap between learned lexicon data and response generation.

Key principle: Responses should become MORE appropriate and nuanced as the system
learns about the user's personal associations, not less.

How it works:
1. Load user's personal lexicon (keywords → emotional contexts)
2. Analyze incoming message for learned keywords
3. Build contextual understanding from learned associations
4. Generate response that reflects user's unique patterns
5. Log response quality to improve future matching
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class LexiconAwareResponseGenerator:
    """Generate responses informed by user's learned lexicon."""
    
    def __init__(
        self,
        hybrid_learner=None,
        response_quality_log: str = "learning/response_quality_log.jsonl",
    ):
        """
        Initialize the lexicon-aware generator.
        
        Args:
            hybrid_learner: HybridLearnerWithUserOverrides instance
            response_quality_log: Path to log which personalized responses worked
        """
        self.learner = hybrid_learner
        self.response_quality_log = response_quality_log
        Path(response_quality_log).parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("[LEXICON-AWARE GENERATOR] Initialized")
    
    def generate_response(
        self,
        user_message: str,
        user_id: str,
        signals: Optional[Dict] = None,
        conversation_context: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Generate a response informed by user's learned lexicon.
        
        Args:
            user_message: User's input message
            user_id: User identifier
            signals: Pre-extracted emotional signals (optional)
            conversation_context: Previous messages for context
            
        Returns:
            {
                "response": str,
                "personalization_level": str (none/low/medium/high),
                "learned_associations": List[Dict],
                "trigger_keywords": List[str],
                "confidence": float,
            }
        """
        # Step 1: Load user's learned lexicon
        user_lexicon = self._load_user_lexicon(user_id)
        
        # Step 2: Extract keywords from message
        message_keywords = self._extract_keywords(user_message)
        
        # Step 3: Find learned associations
        learned_contexts = self._find_learned_contexts(
            message_keywords, 
            user_lexicon
        )
        
        # Step 4: Build contextual understanding
        context_understanding = self._build_context_understanding(
            user_message,
            learned_contexts,
            conversation_context,
        )
        
        # Step 5: Generate personalized response
        response = self._generate_personalized_response(
            user_message,
            context_understanding,
            learned_contexts,
        )
        
        # Step 6: Package result with metadata
        result = {
            "response": response,
            "personalization_level": context_understanding.get("personalization_level"),
            "learned_associations": learned_contexts,
            "trigger_keywords": [kw for kw, _ in learned_contexts],
            "confidence": context_understanding.get("confidence", 0.0),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }
        
        return result
    
    def _load_user_lexicon(self, user_id: str) -> Dict:
        """Load user's personal lexicon from learned data."""
        if not self.learner:
            return {}
        
        try:
            return self.learner._load_user_overrides(user_id) or {}
        except Exception as e:
            logger.warning(f"Could not load user lexicon for {user_id}: {e}")
            return {}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'that', 'this', 'these', 'those', 'what',
            'which', 'who', 'when', 'where', 'why', 'how'
        }
        
        words = text.lower().split()
        keywords = [
            word.strip('.,!?;:')
            for word in words
            if word.strip('.,!?;:') not in stop_words and len(word) > 2
        ]
        
        return list(set(keywords))  # Deduplicate
    
    def _find_learned_contexts(
        self,
        keywords: List[str],
        user_lexicon: Dict,
    ) -> List[Tuple[str, Dict]]:
        """
        Find emotional contexts for keywords from user's learned lexicon.
        
        Returns list of (keyword, context) tuples.
        """
        learned_contexts = []
        
        if not user_lexicon or not user_lexicon.get("learned_associations"):
            return learned_contexts
        
        learned_assocs = user_lexicon.get("learned_associations", {})
        
        for keyword in keywords:
            if keyword in learned_assocs:
                context = learned_assocs[keyword]
                learned_contexts.append((keyword, context))
        
        return learned_contexts
    
    def _build_context_understanding(
        self,
        user_message: str,
        learned_contexts: List[Tuple[str, Dict]],
        conversation_context: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Build understanding of emotional context from learned data.
        
        Returns dict with:
        - emotional_core: Main emotions involved
        - personalization_level: How personalized can we be
        - confidence: How confident are we
        - contextual_cues: What patterns emerged
        """
        if not learned_contexts:
            return {
                "personalization_level": "none",
                "confidence": 0.0,
                "contextual_cues": [],
                "emotional_core": [],
            }
        
        # Extract emotional cores from learned contexts
        emotional_cores = []
        for keyword, context in learned_contexts:
            if isinstance(context, dict):
                emotions = context.get("associated_emotions", [])
                emotional_cores.extend(emotions)
        
        # Determine personalization level based on context richness
        personalization_level = "low"
        confidence = 0.3
        
        if len(learned_contexts) >= 2:
            personalization_level = "medium"
            confidence = 0.6
        
        if len(learned_contexts) >= 3 or any(
            len(ctx.get("associated_emotions", [])) > 2 
            for _, ctx in learned_contexts
        ):
            personalization_level = "high"
            confidence = 0.85
        
        return {
            "personalization_level": personalization_level,
            "confidence": confidence,
            "emotional_core": list(set(emotional_cores)),
            "contextual_cues": [kw for kw, _ in learned_contexts],
        }
    
    def _generate_personalized_response(
        self,
        user_message: str,
        context_understanding: Dict,
        learned_contexts: List[Tuple[str, Dict]],
    ) -> str:
        """
        Generate response using personalized context.
        
        This is where learned patterns become VISIBLE in the response.
        """
        personalization_level = context_understanding.get("personalization_level")
        emotional_core = context_understanding.get("emotional_core", [])
        
        # If no personalization available, return generic response
        if personalization_level == "none":
            return self._generic_response(user_message)
        
        # Build response components from learned context
        response_parts = []
        
        # 1. Acknowledgment that shows understanding of their patterns
        ack = self._build_acknowledgment(learned_contexts, emotional_core)
        response_parts.append(ack)
        
        # 2. Deeper exploration using learned vocabulary
        exploration = self._build_exploration(user_message, learned_contexts)
        response_parts.append(exploration)
        
        # 3. Generative question that respects their patterns
        question = self._build_question(learned_contexts, emotional_core)
        response_parts.append(question)
        
        return " ".join(filter(None, response_parts))
    
    def _build_acknowledgment(
        self,
        learned_contexts: List[Tuple[str, Dict]],
        emotional_core: List[str],
    ) -> str:
        """Build acknowledgment that reflects learned patterns."""
        if not learned_contexts:
            return ""
        
        # Show we know what this keyword means to them
        keyword, context = learned_contexts[0]
        
        if isinstance(context, dict):
            emotions = context.get("associated_emotions", [])
            if emotions:
                emotion_str = " and ".join(emotions[:2])
                return f"I recognize that when you mention '{keyword}', it touches {emotion_str}."
        
        return f"I notice '{keyword}' comes up for you—that's important."
    
    def _build_exploration(
        self,
        user_message: str,
        learned_contexts: List[Tuple[str, Dict]],
    ) -> str:
        """Build exploratory statement using learned context."""
        if len(learned_contexts) < 2:
            return ""
        
        # If multiple learned keywords in one message, there's a pattern
        keywords = [kw for kw, _ in learned_contexts[:2]]
        
        if len(keywords) == 2:
            return f"The fact that '{keywords[0]}' and '{keywords[1]}' appear together for you—that's a real pattern. There's something connecting them in your experience."
        
        return ""
    
    def _build_question(
        self,
        learned_contexts: List[Tuple[str, Dict]],
        emotional_core: List[str],
    ) -> str:
        """Build generative question that respects learned patterns."""
        if not learned_contexts or not emotional_core:
            return "What's at the heart of this for you?"
        
        keyword, context = learned_contexts[0]
        primary_emotion = emotional_core[0] if emotional_core else None
        
        if primary_emotion:
            return f"When you feel this {primary_emotion} about '{keyword}'—what part of it asks for something from you?"
        
        return f"What would change if this dynamic around '{keyword}' shifted?"
    
    def _generic_response(self, user_message: str) -> str:
        """Fallback generic response when no personalization available."""
        lower_msg = user_message.lower()
        
        if any(word in lower_msg for word in ["thank", "appreciate"]):
            return "I appreciate you sharing that. That matters. Tell me more—what's underneath this?"
        
        if any(word in lower_msg for word in ["but", "however", "though", "yet"]):
            return "There's a tension there. Can you say more about what's pulling in different directions?"
        
        if any(word in lower_msg for word in ["don't know", "confused", "unclear"]):
            return "That uncertainty—that's actually where the real knowing begins. What would it look like to sit with that for a moment?"
        
        if any(word in lower_msg for word in ["how", "why", "what"]):
            return "That's a good question. Let's explore that together."
        
        return "That lands somewhere real for you. What does it feel like when you say that?"
    
    def log_response_quality(
        self,
        user_id: str,
        user_message: str,
        response: str,
        feedback: Optional[str] = None,
        quality_score: Optional[float] = None,
    ) -> None:
        """
        Log response quality for analysis and improvement.
        
        This tracks which personalized responses work well,
        informing future personalization.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_message": user_message,
            "response": response,
            "feedback": feedback,
            "quality_score": quality_score,
        }
        
        try:
            with open(self.response_quality_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.warning(f"Could not log response quality: {e}")
    
    def get_personalization_stats(self, user_id: str) -> Dict:
        """Get stats on how personalized responses have been for a user."""
        stats = {
            "user_id": user_id,
            "total_responses_logged": 0,
            "personalization_distribution": {
                "none": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
            },
            "average_quality_score": 0.0,
            "trend": "unknown",
        }
        
        responses = []
        try:
            with open(self.response_quality_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("user_id") == user_id:
                            responses.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            return stats
        
        if not responses:
            return stats
        
        stats["total_responses_logged"] = len(responses)
        
        # Calculate quality scores
        scores = [r.get("quality_score", 0) for r in responses if r.get("quality_score")]
        if scores:
            stats["average_quality_score"] = sum(scores) / len(scores)
        
        return stats


def create_lexicon_aware_pipeline(
    hybrid_learner,
    adaptive_extractor,
) -> Tuple[LexiconAwareResponseGenerator, Dict]:
    """
    Factory function to create integrated lexicon-aware pipeline.
    
    Returns:
        (generator, config)
    """
    generator = LexiconAwareResponseGenerator(
        hybrid_learner=hybrid_learner,
    )
    
    config = {
        "learner": hybrid_learner,
        "extractor": adaptive_extractor,
        "generator": generator,
        "mode": "lexicon_aware_local",
    }
    
    logger.info("[LEXICON-AWARE PIPELINE] Ready for local mode")
    logger.info("  - Responses will be personalized based on learned patterns")
    logger.info("  - No API calls required")
    logger.info("  - Increasing nuance as user lexicon grows")
    
    return generator, config


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Mock user lexicon for demonstration
    mock_lexicon = {
        "learned_associations": {
            "michelle": {
                "associated_emotions": ["frustration", "communication_gap"],
                "frequency": 5,
                "context": "mother-in-law relationship"
            },
            "math": {
                "associated_emotions": ["blocked", "inadequacy"],
                "frequency": 3,
                "context": "personal learning block"
            },
            "inherited": {
                "associated_emotions": ["awareness", "pattern_breaking"],
                "frequency": 4,
                "context": "generational patterns"
            }
        }
    }
    
    generator = LexiconAwareResponseGenerator()
    
    # Simulate a message
    result = generator.generate_response(
        user_message="I'm struggling with michelle and feeling like I have this inherited block with math",
        user_id="demo_user",
    )
    
    print("\n=== LEXICON-AWARE RESPONSE ===")
    print(f"Response: {result['response']}")
    print(f"Personalization Level: {result['personalization_level']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Learned Associations: {result['learned_associations']}")
