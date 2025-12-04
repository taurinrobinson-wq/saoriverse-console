import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AffectParser:
    def __init__(self):
        pass

    def analyze_affect(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        positive = ["happy", "joy", "wonderful", "amazing"]
        negative = ["sad", "angry", "frustrated", "hurt"]
        intense = ["extremely", "so much", "can't", "never"]
        
        valence = sum(0.3 for w in positive if w in text_lower) - sum(0.3 for w in negative if w in text_lower)
        intensity = 0.5 + sum(0.2 for w in intense if w in text_lower)
        valence = max(-1.0, min(1.0, valence))
        intensity = max(0.0, min(1.0, intensity))
        
        if valence > 0.5:
            tone = "uplifting" if intensity > 0.6 else "gentle"
        elif valence < -0.5:
            tone = "heavy" if intensity > 0.6 else "reflective"
        else:
            tone = "curious"
        
        return {"valence": valence, "intensity": intensity, "tone": tone, "arousal": intensity}

class FirstPersonOrchestrator:
    def __init__(self, user_id: str = "anon", conversation_id: str = "default"):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.affect_parser = AffectParser()
        self.conversation_turns = []
        self.theme_frequency = {}

    def initialize_session(self):
        logger.debug(f"FirstPerson initialized for {self.user_id}")

    def handle_conversation_turn(self, user_input: str, glyph: Optional[Dict] = None) -> Dict:
        affect = self.affect_parser.analyze_affect(user_input)
        theme = self._extract_theme(user_input)
        self.theme_frequency[theme] = self.theme_frequency.get(theme, 0) + 1
        return {"detected_theme": theme, "theme_frequency": self.theme_frequency, "memory_context_injected": len(self.conversation_turns) > 0, "affect_analysis": affect}

    def _extract_theme(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["grief", "loss", "death"]):
            return "grief"
        if any(w in text_lower for w in ["happy", "joy", "celebration"]):
            return "joy"
        return "general"

    def generate_response_with_glyph(self, user_input: str, glyph: Dict) -> str:
        affect = self.affect_parser.analyze_affect(user_input)
        theme = self._extract_theme(user_input)
        glyph_name = glyph.get("glyph_name", "")
        
        if affect["valence"] < -0.5:
            opening = f"I hear the weight of {theme}."
        else:
            opening = "You're naming something real."
        
        middle = "Tell me more about what that feels like."
        closing = "What do you need?"
        
        return f"{opening} {middle} {closing}"

def create_orchestrator(user_id: str = "anon", conversation_id: str = "default"):
    try:
        return FirstPersonOrchestrator(user_id, conversation_id)
    except Exception as e:
        logger.error(f"Failed: {e}")
        return None

def create_affect_parser():
    try:
        return AffectParser()
    except Exception as e:
        logger.error(f"Failed: {e}")
        return None
