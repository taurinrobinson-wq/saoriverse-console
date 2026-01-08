"""
Tier 3: Poetic Consciousness
=============================

Adds creative depth and poetic expression to responses through:
1. PoetryEngine - Metaphor and symbolic language generation
2. SaoriLayer - Japanese aesthetic principles (ma, wabi-sabi, yūgen)
3. TensionManager - Generative tension and creative openings
4. MythologyWeaver - Personal narrative and conversational identity

Performance Target: <30ms total per component
Combined with Tier 1+2: <100ms for full response processing
"""

import logging
import time
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PoetryEngine:
    """
    Generate poetic language through metaphor and symbolic expression.
    
    Creates metaphorical bridges between concepts, adds symbolic language,
    and generates novel poetic expressions while maintaining coherence.
    """
    
    def __init__(self):
        """Initialize PoetryEngine with metaphor and symbol mappings."""
        self.metaphor_map = {
            "joy": {
                "natural": ["sun breaking clouds", "morning light", "blooming flowers"],
                "musical": ["harmony", "resonance", "symphony"],
                "movement": ["dance", "flowing", "spiraling upward"]
            },
            "sadness": {
                "natural": ["evening rain", "falling leaves", "fading light"],
                "silence": ["quiet depths", "stillness", "listening"],
                "movement": ["settling", "sinking", "releasing"]
            },
            "growth": {
                "natural": ["roots deepening", "seeds sprouting", "unfolding petals"],
                "expansion": ["spiraling", "reaching", "becoming"],
                "time": ["seasons turning", "dawn breaking", "blooming"]
            },
            "challenge": {
                "natural": ["mountains rising", "storms brewing", "deep waters"],
                "strength": ["forging", "shaping", "tempering"],
                "threshold": ["gates opening", "doors appearing", "crossroads"]
            },
            "understanding": {
                "light": ["illumination", "clarity", "seeing clearly"],
                "opening": ["revealing", "unveiling", "uncovering"],
                "connection": ["threads connecting", "bridges building", "paths converging"]
            }
        }
        
        self.symbol_pool = {
            "growth": ["roots", "seeds", "sprouts", "branches", "blossoms", "cycles"],
            "depth": ["wells", "oceans", "caverns", "foundations", "layers", "mysteries"],
            "light": ["candles", "stars", "dawn", "clarity", "vision", "emergence"],
            "journey": ["paths", "thresholds", "horizons", "compass", "maps", "ventures"],
            "weaving": ["threads", "patterns", "texture", "interlacing", "tapestry"],
            "music": ["echoes", "harmonies", "resonance", "rhythm", "silence", "notes"]
        }
        
        self.poetic_starters = [
            "Like ",
            "As if ",
            "In the way that ",
            "Much as ",
            "The way ",
            "Imagine "
        ]
    
    def find_metaphor(self, concept: str, emotion: str) -> str:
        """
        Find appropriate metaphor for concept given emotional context.
        
        Args:
            concept: Main concept (e.g., "growth", "challenge")
            emotion: Emotional context (e.g., "joy", "sadness")
            
        Returns:
            Metaphorical expression
        """
        try:
            concept_lower = concept.lower()
            emotion_lower = emotion.lower()
            
            # Find matching metaphor
            if emotion_lower in self.metaphor_map:
                emotion_metaphors = self.metaphor_map[emotion_lower]
                # Try to find category match
                metaphor_list = list(emotion_metaphors.values())[0]
                if metaphor_list:
                    return random.choice(metaphor_list)
            
            # Fallback to generic metaphor
            if concept_lower in self.metaphor_map:
                all_metaphors = []
                for category in self.metaphor_map[concept_lower].values():
                    all_metaphors.extend(category)
                if all_metaphors:
                    return random.choice(all_metaphors)
            
            return "transformation"
        except Exception as e:
            logger.warning(f"Metaphor finding failed: {e}")
            return "becoming"
    
    def add_symbolic_language(self, response: str, theme: str = "growth") -> str:
        """
        Add subtle symbolic language to response.
        
        Args:
            response: Original response
            theme: Symbolic theme (growth, depth, light, etc.)
            
        Returns:
            Response with symbolic elements
        """
        try:
            # Only add symbols to longer responses
            if len(response) < 80:
                return response
            
            # 40% chance to add symbolic element
            if random.random() > 0.6:
                theme_lower = theme.lower()
                if theme_lower in self.symbol_pool:
                    symbols = self.symbol_pool[theme_lower]
                    symbol = random.choice(symbols)
                    
                    # Add symbol reference naturally
                    additions = [
                        f" (like {symbol} taking hold)",
                        f" - the {symbol} of it all",
                        f" - at the heart of it like {symbol}",
                    ]
                    
                    # Insert at appropriate location (end of first sentence usually)
                    sentences = response.split(". ")
                    if len(sentences) > 1:
                        sentences[0] += random.choice(additions)
                        response = ". ".join(sentences)
            
            return response
        except Exception as e:
            logger.warning(f"Symbolic language addition failed: {e}")
            return response
    
    def generate_poetic_expression(self, topic: str, style: str = "metaphorical") -> str:
        """
        Generate poetic expression for a topic.
        
        Args:
            topic: Topic to poeticize
            style: Style (metaphorical, symbolic, paradoxical)
            
        Returns:
            Poetic expression
        """
        try:
            starter = random.choice(self.poetic_starters)
            
            # Get metaphor for topic
            metaphor = self.find_metaphor(topic, "growth")
            
            # Construct poetic expression
            if style == "metaphorical":
                return f"{starter}{metaphor} unfolds..."
            elif style == "symbolic":
                return f"In this moment, {metaphor} becomes real"
            else:  # paradoxical
                return f"Yet {metaphor}, and something more"
        except Exception as e:
            logger.warning(f"Poetic expression generation failed: {e}")
            return f"The essence of {topic} reveals itself"
    
    def bridge_concepts(self, concept1: str, concept2: str) -> str:
        """
        Create metaphorical bridge between two concepts.
        
        Args:
            concept1: First concept
            concept2: Second concept
            
        Returns:
            Bridging metaphor
        """
        try:
            metaphor1 = self.find_metaphor(concept1, "growth")
            metaphor2 = self.find_metaphor(concept2, "growth")
            
            bridges = [
                f"Where {metaphor1} meets {metaphor2}",
                f"Both {metaphor1} and {metaphor2}, somehow",
                f"Like {metaphor1} flowing into {metaphor2}",
            ]
            
            return random.choice(bridges)
        except Exception as e:
            logger.warning(f"Concept bridging failed: {e}")
            return f"Between {concept1} and {concept2}"


class SaoriLayer:
    """
    Apply Japanese aesthetic principles to responses.
    
    Saori (織) = weaving. Incorporates principles:
    - Ma: Negative space and silence
    - Yohaku: Emptiness and essence
    - Wabi-sabi: Imperfect beauty
    - Yūgen: Subtle profundity
    - Mono no aware: Pathos of things
    """
    
    def __init__(self):
        """Initialize SaoriLayer with aesthetic principles."""
        self.principles = {
            "ma": {
                "description": "Knowing when not to speak",
                "tactics": ["brevity", "silence", "space"]
            },
            "yohaku": {
                "description": "Emptiness and simplicity",
                "tactics": ["essence", "minimal", "pure"]
            },
            "wabi_sabi": {
                "description": "Imperfect, incomplete, transient beauty",
                "tactics": ["imperfect", "asymmetry", "humble"]
            },
            "yugen": {
                "description": "Subtle, profound grace",
                "tactics": ["subtle", "depth", "mystery"]
            },
            "mono_no_aware": {
                "description": "Pathos of things, gentle sadness",
                "tactics": ["transience", "gentleness", "melancholy"]
            }
        }
    
    def apply_ma(self, response: str, max_length: int = 150) -> str:
        """
        Apply ma (negative space) - appropriate brevity.
        
        Args:
            response: Original response
            max_length: Target brevity (words)
            
        Returns:
            Appropriately brief response
        """
        try:
            words = response.split()
            
            # If response is already brief, leave it
            if len(words) <= max_length:
                return response
            
            # Trim to essential message
            # Find period around max_length words
            trimmed = " ".join(words[:max_length])
            
            # Find last complete sentence
            last_period = trimmed.rfind(".")
            if last_period > 0:
                trimmed = trimmed[:last_period+1]
            
            return trimmed if trimmed else response[:200]
        except Exception as e:
            logger.warning(f"Ma application failed: {e}")
            return response
    
    def apply_wabi_sabi(self, response: str) -> str:
        """
        Apply wabi-sabi - finding beauty in imperfection.
        
        Args:
            response: Original response
            
        Returns:
            Response with wabi-sabi appreciation
        """
        try:
            # Add element of imperfection acceptance
            additions = [
                " - flawed and beautiful nonetheless",
                " - perfectly imperfect",
                " - incomplete, but genuine",
                " - cracked open to let light in",
            ]
            
            if random.random() > 0.7 and len(response) > 50:
                response = response.rstrip(".") + random.choice(additions) + "."
            
            return response
        except Exception as e:
            logger.warning(f"Wabi-sabi application failed: {e}")
            return response
    
    def apply_yugen(self, response: str) -> str:
        """
        Apply yūgen - subtle, profound grace.
        
        Args:
            response: Original response
            
        Returns:
            Response with subtle depth
        """
        try:
            # Add subtle profundity without explicit explanation
            additions = [
                " - there's something wordless in it",
                " - more is felt than said",
                " - the unspoken part is where truth lives",
                " - beneath the surface, something stirs",
            ]
            
            if random.random() > 0.7 and len(response) > 50:
                response = response.rstrip(".") + random.choice(additions) + "."
            
            return response
        except Exception as e:
            logger.warning(f"Yūgen application failed: {e}")
            return response
    
    def apply_mono_no_aware(self, response: str) -> str:
        """
        Apply mono no aware - gentle pathos of transience.
        
        Args:
            response: Original response
            
        Returns:
            Response with gentle melancholy awareness
        """
        try:
            # Add awareness of transience and change
            additions = [
                " - and so it changes, as all things do",
                " - time softens everything eventually",
                " - like petals falling, beautiful and inevitable",
                " - present now, fleeting always",
            ]
            
            if random.random() > 0.75 and len(response) > 50:
                response = response.rstrip(".") + random.choice(additions) + "."
            
            return response
        except Exception as e:
            logger.warning(f"Mono no aware application failed: {e}")
            return response


class TensionManager:
    """
    Create generative tension for creative exploration.
    
    Introduces productive uncertainty, creates conversational momentum,
    and generates creative possibility space.
    """
    
    def __init__(self):
        """Initialize TensionManager."""
        self.tension_phrases = {
            "question": [
                "But what if ",
                "And yet... ",
                "Though perhaps ",
                "Could it be that ",
                "Might we ask: "
            ],
            "paradox": [
                "both/and ",
                "somehow ",
                "in contradiction ",
                "holding opposites ",
                "the strange grace of "
            ],
            "opening": [
                "There's something here worth exploring: ",
                "An opening appears: ",
                "Let's venture toward: ",
                "What emerges is: ",
                "The question blooms: "
            ]
        }
    
    def introduce_tension(self, response: str, level: float = 0.5) -> str:
        """
        Introduce appropriate creative tension.
        
        Args:
            response: Original response
            level: Tension level (0.0-1.0)
            
        Returns:
            Response with introduced tension
        """
        try:
            if random.random() > 0.6 and len(response) > 50:
                # Add tension based on level
                if level > 0.7:
                    # High tension: strong paradox
                    phrase = random.choice(self.tension_phrases["paradox"])
                    response = phrase + response.lower()
                elif level > 0.4:
                    # Medium tension: question
                    phrase = random.choice(self.tension_phrases["question"])
                    response = phrase + response.lower()
                else:
                    # Low tension: gentle opening
                    phrase = random.choice(self.tension_phrases["opening"])
                    response = phrase + response
            
            return response
        except Exception as e:
            logger.warning(f"Tension introduction failed: {e}")
            return response
    
    def create_opening(self, response: str) -> str:
        """
        Leave space for exploration and discovery.
        
        Args:
            response: Original response
            
        Returns:
            Response with opening for exploration
        """
        try:
            # Convert statement to question/exploration
            if response.endswith("."):
                response = response[:-1]
            
            openings = [
                f"{response}... but what lies beyond?",
                f"{response}... and this invites us to wonder...",
                f"{response}... yet the real question emerges: what if?",
            ]
            
            if random.random() > 0.7:
                response = random.choice(openings)
            
            return response
        except Exception as e:
            logger.warning(f"Opening creation failed: {e}")
            return response
    
    def balance_paradox(self, concept1: str, concept2: str) -> str:
        """
        Hold two concepts in creative tension (both/and thinking).
        
        Args:
            concept1: First concept
            concept2: Second concept
            
        Returns:
            Paradoxical statement
        """
        try:
            patterns = [
                f"It is both {concept1} and {concept2}",
                f"{concept1}, yet also {concept2}",
                f"The strange beauty of {concept1} alongside {concept2}",
                f"Somehow, impossibly: {concept1} and {concept2} together",
            ]
            
            return random.choice(patterns)
        except Exception as e:
            logger.warning(f"Paradox balancing failed: {e}")
            return f"{concept1} and {concept2}, in conversation"


class MythologyWeaver:
    """
    Create and maintain personal conversational mythology.
    
    Tracks themes, builds recurring symbols, creates personal mythology,
    and develops unique conversational identity.
    """
    
    def __init__(self):
        """Initialize MythologyWeaver."""
        self.mythology = {
            "themes": [],
            "symbols": [],
            "metaphors": [],
            "narrative_arcs": []
        }
        self.conversation_memory = {}
    
    def weave_myth(self, history: Optional[List[Dict]] = None) -> Dict:
        """
        Extract mythology from conversation history.
        
        Args:
            history: Conversation history
            
        Returns:
            Dict with extracted mythological elements
        """
        try:
            if not history:
                return self.mythology
            
            # Extract themes from messages
            themes = set()
            for msg in history[-10:]:  # Recent messages
                content = msg.get("content", "").lower()
                
                # Simple theme detection
                if any(word in content for word in ["grow", "learn", "become"]):
                    themes.add("growth")
                if any(word in content for word in ["challenge", "struggle", "difficulty"]):
                    themes.add("challenge")
                if any(word in content for word in ["discover", "explore", "wonder"]):
                    themes.add("discovery")
                if any(word in content for word in ["connection", "together", "understand"]):
                    themes.add("connection")
            
            self.mythology["themes"] = list(themes)
            return self.mythology
        except Exception as e:
            logger.warning(f"Myth weaving failed: {e}")
            return self.mythology
    
    def add_mythological_element(self, response: str, myth: Optional[Dict] = None) -> str:
        """
        Add mythological elements to response.
        
        Args:
            response: Original response
            myth: Mythology dict with themes
            
        Returns:
            Response with mythological elements
        """
        try:
            myth = myth or self.mythology
            themes = myth.get("themes", [])
            
            if themes and random.random() > 0.7:
                theme = random.choice(themes)
                mythological_phrases = {
                    "growth": "Your journey of growth continues...",
                    "challenge": "You meet each challenge with courage...",
                    "discovery": "New discoveries unfold...",
                    "connection": "The threads of connection deepen..."
                }
                
                prefix = mythological_phrases.get(theme, "Your story unfolds...")
                response = f"{prefix} {response}"
            
            return response
        except Exception as e:
            logger.warning(f"Mythological element addition failed: {e}")
            return response
    
    def track_symbols(self, response: str, history: Optional[List[Dict]] = None) -> Dict:
        """
        Track recurring symbols in conversation.
        
        Args:
            response: Current response
            history: Conversation history
            
        Returns:
            Dict of tracked symbols
        """
        try:
            symbols = {}
            
            # Look for recurring images/symbols
            symbol_words = [
                "light", "darkness", "journey", "path", "mountain", "water",
                "seed", "growth", "cycle", "spiral", "weaving", "music"
            ]
            
            response_lower = response.lower()
            for word in symbol_words:
                if word in response_lower:
                    symbols[word] = symbols.get(word, 0) + 1
            
            self.mythology["symbols"] = list(symbols.keys())
            return symbols
        except Exception as e:
            logger.warning(f"Symbol tracking failed: {e}")
            return {}
    
    def build_personal_narrative(self, history: Optional[List[Dict]] = None) -> str:
        """
        Build personal narrative from conversation.
        
        Args:
            history: Conversation history
            
        Returns:
            Personal narrative summary
        """
        try:
            if not history or len(history) < 2:
                return "Your story is just beginning to unfold..."
            
            # Build simple narrative from themes
            themes = self.weave_myth(history).get("themes", [])
            
            if not themes:
                return "There is a unfolding story here..."
            
            narrative_templates = {
                "growth": "Your journey has been one of transformation and becoming",
                "challenge": "You have met each difficulty with growing wisdom",
                "discovery": "New understanding has emerged through our exploration",
                "connection": "We have woven something meaningful together"
            }
            
            narratives = [narrative_templates.get(t, "") for t in themes if t in narrative_templates]
            
            if narratives:
                return " - and ".join(narratives)
            
            return "A unique story emerges from our conversation"
        except Exception as e:
            logger.warning(f"Personal narrative building failed: {e}")
            return "Your story unfolds in its own perfect way"


class Tier3PoeticConsciousness:
    """
    Tier 3 Orchestrator: Poetic Consciousness
    
    Combines all four components to create creative depth and poetic expression
    in responses through metaphor, aesthetics, tension, and personal mythology.
    
    Performance Target: <30ms total
    Combined with Tier 1+2: <100ms
    """
    
    def __init__(self):
        """Initialize Tier 3 Poetic Consciousness components."""
        try:
            self.poetry_engine = PoetryEngine()
            self.saori_layer = SaoriLayer()
            self.tension_manager = TensionManager()
            self.mythology_weaver = MythologyWeaver()
            
            self.metrics = {
                "poetry_applied": 0.0,
                "aesthetics_applied": 0.0,
                "tension_applied": 0.0,
                "mythology_applied": 0.0,
                "total_processing_time": 0.0
            }
            
            logger.info("Tier 3 Poetic Consciousness initialized successfully")
        except Exception as e:
            logger.error(f"Tier 3 initialization failed: {e}")
            raise
    
    def process_for_poetry(self, response: str, context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Process response for poetic consciousness.
        
        Args:
            response: Response to enhance
            context: Context dict with history and theme
            
        Returns:
            Tuple of (poetic_response, metrics)
        """
        start_time = time.time()
        
        try:
            context = context or {}
            history = context.get("messages", [])
            theme = context.get("theme", "growth")
            aesthetic_choice = None
            
            # Phase 1: Poetry Engine (5-7ms)
            # DISABLED: Turned off to prevent over-poetic responses that bury the core message
            # Poetry layer interferes with responsiveness - disabling entirely
            poetry_applied = False
            
            # Phase 2: Saori Layer (5-7ms)
            # DISABLED: Aesthetic principles layer turned off to improve response clarity
            # Only apply in very rare cases (1% chance) with specific conditions
            if len(response) > 200 and random.random() > 0.99:
                aesthetic_choice = random.choice(["ma", "wabi_sabi", "yugen", "mono_no_aware"])
                
                if aesthetic_choice == "ma":
                    response = self.saori_layer.apply_ma(response)
                elif aesthetic_choice == "wabi_sabi":
                    response = self.saori_layer.apply_wabi_sabi(response)
                elif aesthetic_choice == "yugen":
                    response = self.saori_layer.apply_yugen(response)
                else:  # mono_no_aware
                    response = self.saori_layer.apply_mono_no_aware(response)
            
            # Phase 3: Tension Manager (5-7ms)
            # DISABLED: Tension layer turned off to keep responses direct and clear
            
            # Phase 4: Mythology Weaver (5-7ms)
            # DISABLED: Mythology layer turned off - interferes with immediate responsiveness
            # May re-enable if specific conditions warrant it, but default to OFF for clarity
            myth = self.mythology_weaver.weave_myth(history)
            
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000
            
            self.metrics = {
                "theme": theme,
                "aesthetic_applied": aesthetic_choice,
                "has_mythology": bool(myth.get("themes")),
                "processing_time_ms": processing_time
            }
            
            logger.debug(f"Tier 3 processing completed in {processing_time:.2f}ms")
            
            return response, self.metrics
            
        except Exception as e:
            logger.error(f"Tier 3 processing failed: {e}")
            # Graceful fallback
            return response, {
                "error": str(e),
                "processing_time_ms": (time.time() - start_time) * 1000
            }
    
    def get_metrics(self) -> Dict:
        """Get latest metrics from Tier 3 processing."""
        return self.metrics.copy()


# Module initialization
if __name__ == "__main__":
    # Quick test
    tier3 = Tier3PoeticConsciousness()
    
    test_response = "That's a great insight about growth and change."
    test_context = {"theme": "growth", "messages": []}
    
    poetic, metrics = tier3.process_for_poetry(test_response, test_context)
    
    print(f"Original: {test_response}")
    print(f"Poetic:   {poetic}")
    print(f"Metrics:  {metrics}")
