#!/usr/bin/env python3
"""
Dynamic Glyph Evolution System

Connects dialogue-based learning to glyph generation:
- User + AI dialogue → hybrid processor learns new emotional signals
- New signals → lexicon expansion (adaptive dimensions)
- Lexicon patterns → new glyphs generated automatically
- New glyphs → available for next dialogue turns

Architecture:
1. Conversation Input
2. Signal Extraction (adaptive - discovers new dimensions)
3. Lexicon Learning (user overrides + shared lexicon)
4. Pattern Detection (co-occurrence in conversation + learned signals)
5. Glyph Generation (new glyphs from patterns)
6. Integration (new glyphs available for next turn)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@dataclass
class ConversationGlyph:
    """A glyph discovered through live conversation."""
    id: str
    name: str
    symbol: str
    core_emotions: List[str]
    associated_keywords: List[str]
    combined_frequency: int
    response_cue: str
    narrative_hook: str
    created_from_conversation: bool
    user_id: str
    conversation_id: str
    source: str = "dialogue_evolution"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "core_emotions": self.core_emotions,
            "associated_keywords": self.associated_keywords,
            "combined_frequency": self.combined_frequency,
            "response_cue": self.response_cue,
            "narrative_hook": self.narrative_hook,
            "created_from_conversation": self.created_from_conversation,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "source": self.source,
            "created_at": datetime.now().isoformat(),
        }


class DynamicGlyphEvolution:
    """
    Manages dynamic glyph creation during live conversations.
    
    Flow:
    1. Learn from dialogue through hybrid processor
    2. Extract patterns from accumulated signals
    3. Generate new glyphs when patterns reach significance threshold
    4. Make glyphs available for system use
    """
    
    def __init__(
        self,
        hybrid_learner,  # HybridLearnerWithUserOverrides instance
        lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        glyphs_output_dir: str = "learning/generated_glyphs",
        conversation_glyphs_file: str = "learning/conversation_glyphs.json",
        min_frequency_for_glyph: int = 300,
        adaptive_extractor=None,
    ):
        """Initialize dynamic evolution system.
        
        Args:
            hybrid_learner: HybridLearnerWithUserOverrides instance for learning
            lexicon_path: Path to base lexicon
            glyphs_output_dir: Directory to save generated glyphs
            conversation_glyphs_file: File tracking conversation-discovered glyphs
            min_frequency_for_glyph: Minimum co-occurrence frequency to create glyph
            adaptive_extractor: AdaptiveSignalExtractor for discovering new dimensions
        """
        self.learner = hybrid_learner
        self.lexicon_path = lexicon_path
        self.glyphs_output_dir = glyphs_output_dir
        self.conversation_glyphs_file = conversation_glyphs_file
        self.min_frequency_for_glyph = min_frequency_for_glyph
        self.adaptive_extractor = adaptive_extractor
        
        # Ensure directories exist
        Path(glyphs_output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load or initialize conversation glyphs tracking
        self.conversation_glyphs = self._load_conversation_glyphs()
        
        # Emoji mapping for glyph symbols
        self.emotion_symbols = {
            "love": "♥",
            "intimacy": "❤",
            "sensuality": "🌹",
            "transformation": "🦋",
            "admiration": "⭐",
            "joy": "☀",
            "vulnerability": "🌱",
            "nature": "🌿",
            "grief": "🌊",
            "longing": "🎻",
            "wonder": "✨",
            "peace": "🕯",
            "passion": "🔥",
            "connection": "🔗",
        }
    
    def _load_conversation_glyphs(self) -> Dict:
        """Load previously discovered conversation glyphs."""
        try:
            if Path(self.conversation_glyphs_file).exists():
                with open(self.conversation_glyphs_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load conversation glyphs: {e}")
        return {"glyphs": [], "metadata": {"total_discovered": 0, "last_updated": None}}
    
    def _save_conversation_glyphs(self):
        """Save discovered glyphs to file."""
        try:
            with open(self.conversation_glyphs_file, 'w') as f:
                self.conversation_glyphs["metadata"]["last_updated"] = datetime.now().isoformat()
                self.conversation_glyphs["metadata"]["total_discovered"] = len(self.conversation_glyphs["glyphs"])
                json.dump(self.conversation_glyphs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversation glyphs: {e}")
    
    def _load_lexicon(self) -> Dict:
        """Load current lexicon (includes learned signals)."""
        try:
            with open(self.lexicon_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load lexicon: {e}")
            return {"signals": {}}
    
    def process_dialogue_exchange(
        self,
        user_id: str,
        conversation_id: str,
        user_input: str,
        ai_response: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyphs: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Process a user-AI exchange and look for new glyph patterns.
        
        Args:
            user_id: The user identifier
            conversation_id: Unique conversation identifier
            user_input: User's message
            ai_response: AI's response
            emotional_signals: Detected signals (will be extracted if None)
            glyphs: Matched glyphs
            
        Returns:
            Result dict with:
            - learning_result: outcome of learning
            - new_glyphs_generated: list of newly created glyphs
            - lexicon_updates: changes to lexicon
        """
        result = {
            "learning_result": None,
            "new_glyphs_generated": [],
            "lexicon_updates": {},
            "pattern_analysis": None,
        }
        
        try:
            # 1. Learn from exchange through hybrid processor
            learning_result = self.learner.learn_from_exchange(
                user_id=user_id,
                user_input=user_input,
                ai_response=ai_response,
                emotional_signals=emotional_signals,
                glyphs=glyphs,
            )
            result["learning_result"] = learning_result
            
            logger.info(f"[DIALOGUE] User {user_id} in conversation {conversation_id}")
            logger.info(f"  Input: {user_input[:100]}...")
            logger.info(f"  Learning result: {learning_result}")
            
            # 2. Extract signals from this exchange if not provided
            if not emotional_signals or len(emotional_signals) == 0:
                try:
                    if self.adaptive_extractor:
                        emotional_signals = self.adaptive_extractor.extract_signals(
                            user_input + " " + ai_response
                        )
                    else:
                        from emotional_os.learning.poetry_signal_extractor import get_poetry_extractor
                        extractor = get_poetry_extractor()
                        emotional_signals = extractor.extract_signals(
                            user_input + " " + ai_response
                        )
                except Exception as e:
                    logger.warning(f"Signal extraction failed: {e}")
                    emotional_signals = []
            
            # 3. Analyze for new glyph patterns
            patterns = self._detect_patterns_in_exchange(
                user_input, ai_response, emotional_signals
            )
            result["pattern_analysis"] = patterns
            
            # 4. Generate new glyphs if patterns are significant
            if patterns and len(patterns) > 0:
                new_glyphs = self._generate_glyphs_from_patterns(
                    patterns=patterns,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    exchange_text=user_input + " " + ai_response,
                )
                
                if new_glyphs and len(new_glyphs) > 0:
                    result["new_glyphs_generated"] = new_glyphs
                    logger.info(f"[GLYPHS] Generated {len(new_glyphs)} new glyphs from patterns")
                    
                    # Save new glyphs
                    for glyph in new_glyphs:
                        self._add_conversation_glyph(glyph)
            
            # 5. Get lexicon updates
            updated_lexicon = self._load_lexicon()
            if "signals" in updated_lexicon:
                result["lexicon_updates"] = {
                    "signal_count": len(updated_lexicon["signals"]),
                    "signals": list(updated_lexicon["signals"].keys()),
                }
            
        except Exception as e:
            logger.error(f"Error processing dialogue exchange: {e}", exc_info=True)
            result["error"] = str(e)
        
        return result
    
    def _detect_patterns_in_exchange(
        self,
        user_input: str,
        ai_response: str,
        emotional_signals: List[Dict],
    ) -> List[Dict]:
        """
        Detect co-occurrence patterns in a dialogue exchange.
        
        Returns:
            List of pattern dicts with:
            - signal_pair: (signal1, signal2)
            - co_occurrence_count: how many times they appeared together
            - keywords: combined keywords
        """
        patterns = []
        
        if not emotional_signals or len(emotional_signals) < 2:
            return patterns
        
        # Extract unique signals
        signals_found = list(set([s.get("signal") or s.get("name") for s in emotional_signals if s]))
        
        # Find co-occurrence patterns
        if len(signals_found) >= 2:
            for i, signal1 in enumerate(signals_found):
                for signal2 in signals_found[i+1:]:
                    pattern = {
                        "signal_pair": [signal1, signal2],
                        "co_occurrence_count": 1,  # Count in this exchange
                        "keywords": self._extract_pattern_keywords(
                            signal1, signal2, user_input + " " + ai_response
                        ),
                        "context": {
                            "user_input": user_input[:200],
                            "ai_response": ai_response[:200],
                        }
                    }
                    patterns.append(pattern)
            
            logger.info(f"[PATTERNS] Detected {len(patterns)} co-occurrence patterns in exchange")
        
        return patterns
    
    def _extract_pattern_keywords(
        self,
        signal1: str,
        signal2: str,
        text: str,
    ) -> List[str]:
        """Extract keywords related to a signal pair from text."""
        keywords = []
        
        # Simple keyword extraction from context
        words = text.lower().split()
        
        # Common emotional keywords related to signal pairs
        signal_keywords = {
            ("love", "intimacy"): ["love", "intimacy", "close", "near", "tender", "embrace"],
            ("love", "vulnerability"): ["open", "honest", "bare", "exposed", "risk"],
            ("joy", "celebration"): ["happy", "celebrate", "joy", "delight", "wonderful"],
            ("transformation", "growth"): ["change", "grow", "evolve", "transform", "become"],
        }
        
        pair_keywords = signal_keywords.get((signal1, signal2)) or signal_keywords.get((signal2, signal1))
        if pair_keywords:
            keywords = [w for w in words if w in pair_keywords and w in text.lower()]
        
        # Include the signal names as keywords
        keywords.extend([signal1.lower(), signal2.lower()])
        
        return list(set(keywords))[:5]  # Limit to 5 unique keywords
    
    def _generate_glyphs_from_patterns(
        self,
        patterns: List[Dict],
        user_id: str,
        conversation_id: str,
        exchange_text: str,
    ) -> List[ConversationGlyph]:
        """Generate new glyphs from detected patterns."""
        new_glyphs = []
        
        for i, pattern in enumerate(patterns):
            signal_pair = pattern.get("signal_pair", [])
            if len(signal_pair) != 2:
                continue
            
            signal1, signal2 = signal_pair
            
            # Create glyph
            glyph = ConversationGlyph(
                id=f"glyph_dialogue_{user_id}_{conversation_id}_{i+1}",
                name=self._create_pattern_name(signal1, signal2),
                symbol=self._create_pattern_symbol(signal1, signal2),
                core_emotions=[signal1, signal2],
                associated_keywords=pattern.get("keywords", [signal1, signal2]),
                combined_frequency=300,  # Base frequency for conversation-discovered glyphs
                response_cue=self._create_response_cue(signal1, signal2),
                narrative_hook=self._create_narrative_hook(signal1, signal2),
                created_from_conversation=True,
                user_id=user_id,
                conversation_id=conversation_id,
            )
            
            new_glyphs.append(glyph)
            logger.info(f"[NEW GLYPH] {glyph.name} ({glyph.symbol}) from {signal1} + {signal2}")
        
        return new_glyphs
    
    def _create_pattern_name(self, signal1: str, signal2: str) -> str:
        """Generate a meaningful name for a signal pair."""
        # Simple name generation from signal combinations
        name_map = {
            ("love", "intimacy"): "Intimate Connection",
            ("love", "vulnerability"): "Open-Hearted Love",
            ("love", "sensuality"): "Sensual Love",
            ("love", "joy"): "Joyful Love",
            ("intimacy", "vulnerability"): "Vulnerable Closeness",
            ("joy", "celebration"): "Pure Celebration",
            ("transformation", "growth"): "Becoming",
            ("nature", "peace"): "Natural Serenity",
            ("admiration", "wonder"): "Inspired Wonder",
        }
        
        # Check both orderings
        name = name_map.get((signal1, signal2)) or name_map.get((signal2, signal1))
        
        if name:
            return name
        
        # Fallback: combine names
        return f"{signal1.title()} & {signal2.title()}"
    
    def _create_pattern_symbol(self, signal1: str, signal2: str) -> str:
        """Generate emoji symbols for a signal pair."""
        symbol1 = self.emotion_symbols.get(signal1, "💫")
        symbol2 = self.emotion_symbols.get(signal2, "💫")
        return f"{symbol1}{symbol2}"
    
    def _create_response_cue(self, signal1: str, signal2: str) -> str:
        """Generate a response cue for this pattern."""
        cues = {
            ("love", "intimacy"): "Recognize the deep closeness being shared",
            ("love", "vulnerability"): "Honor the courage of opening one's heart",
            ("joy", "celebration"): "Embrace and amplify the joy present",
            ("transformation", "growth"): "Support the journey of becoming",
            ("nature", "peace"): "Connect to the peace of natural cycles",
        }
        
        cue = cues.get((signal1, signal2)) or cues.get((signal2, signal1))
        return cue or f"Acknowledge the {signal1} and {signal2} present here"
    
    def _create_narrative_hook(self, signal1: str, signal2: str) -> str:
        """Generate a narrative hook for this pattern."""
        hooks = {
            ("love", "intimacy"): "A story of two souls finding each other",
            ("love", "vulnerability"): "The courage to love with open wounds",
            ("joy", "celebration"): "A moment of pure, shared delight",
            ("transformation", "growth"): "The metamorphosis within us all",
            ("nature", "peace"): "Finding stillness in the rhythm of the world",
        }
        
        hook = hooks.get((signal1, signal2)) or hooks.get((signal2, signal1))
        return hook or f"A story where {signal1} meets {signal2}"
    
    def _add_conversation_glyph(self, glyph: ConversationGlyph):
        """Add a newly discovered glyph to the tracking system."""
        try:
            self.conversation_glyphs["glyphs"].append(glyph.to_dict())
            self._save_conversation_glyphs()
            logger.info(f"[SAVED] Conversation glyph {glyph.id} for user {glyph.user_id}")
        except Exception as e:
            logger.error(f"Failed to save conversation glyph: {e}")
    
    def get_conversation_glyphs(
        self,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Retrieve conversation-discovered glyphs.
        
        Args:
            user_id: Filter by user (optional)
            conversation_id: Filter by conversation (optional)
            limit: Maximum number to return (optional)
            
        Returns:
            List of glyph dicts
        """
        glyphs = self.conversation_glyphs.get("glyphs", [])
        
        # Apply filters
        if user_id:
            glyphs = [g for g in glyphs if g.get("user_id") == user_id]
        
        if conversation_id:
            glyphs = [g for g in glyphs if g.get("conversation_id") == conversation_id]
        
        # Apply limit
        if limit:
            glyphs = glyphs[-limit:]  # Most recent
        
        return glyphs
    
    def export_glyphs_for_system(self, output_file: str) -> Dict:
        """
        Export all conversation-discovered glyphs for system integration.
        
        Returns:
            Metadata about exported glyphs
        """
        try:
            glyphs = self.conversation_glyphs.get("glyphs", [])
            
            export_data = {
                "source": "dialogue_evolution",
                "count": len(glyphs),
                "glyphs": glyphs,
                "exported_at": datetime.now().isoformat(),
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"[EXPORT] Exported {len(glyphs)} glyphs to {output_file}")
            return {"success": True, "count": len(glyphs), "file": output_file}
            
        except Exception as e:
            logger.error(f"Failed to export glyphs: {e}")
            return {"success": False, "error": str(e)}
    
    def print_discovered_glyphs(self, limit: int = 10):
        """Print recently discovered glyphs."""
        glyphs = self.get_conversation_glyphs(limit=limit)
        
        print("\n" + "=" * 70)
        print("CONVERSATION-DISCOVERED GLYPHS")
        print("=" * 70)
        
        for i, glyph in enumerate(glyphs, 1):
            print(f"\n{i}. {glyph['symbol']} {glyph['name']}")
            print(f"   ID: {glyph['id']}")
            print(f"   Emotions: {' + '.join(glyph['core_emotions'])}")
            print(f"   Keywords: {', '.join(glyph['associated_keywords'])}")
            print(f"   Response: {glyph['response_cue']}")
            print(f"   Created: {glyph.get('created_at', 'unknown')[:10]}")
        
        print("\n" + "=" * 70)
        print(f"Total conversation-discovered glyphs: {len(self.conversation_glyphs['glyphs'])}")
        print("=" * 70 + "\n")


# Integration helper for hybrid processor
def integrate_evolution_with_processor(
    hybrid_learner,
    adaptive_extractor=None,
) -> DynamicGlyphEvolution:
    """Create and initialize the evolution system with a hybrid processor."""
    
    evolution = DynamicGlyphEvolution(
        hybrid_learner=hybrid_learner,
        adaptive_extractor=adaptive_extractor,
    )
    
    logger.info("✓ Dynamic Glyph Evolution system initialized")
    logger.info("  - Hybrid processor: connected")
    logger.info("  - Pattern detection: active")
    logger.info("  - Glyph generation: ready")
    
    return evolution


if __name__ == "__main__":
    # Example usage
    print("Dynamic Glyph Evolution System")
    print("This module integrates with the hybrid processor for live glyph discovery")
    print("\nUsage:")
    print("  from dynamic_glyph_evolution import DynamicGlyphEvolution, integrate_evolution_with_processor")
    print("  evolution = integrate_evolution_with_processor(hybrid_learner, adaptive_extractor)")
    print("  result = evolution.process_dialogue_exchange(...)")
