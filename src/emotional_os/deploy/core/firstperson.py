import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
import json

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
        
        # Compute mortality salience (implicit finitude signals)
        mortality = self._compute_mortality_salience(text_lower, {
            "valence": valence,
            "intensity": intensity,
        })

        return {
            "valence": valence,
            "intensity": intensity,
            "tone": tone,
            "arousal": intensity,
            "mortality_salience": mortality,
        }

    def _compute_mortality_salience(self, text_lower: str, affect: Dict[str, Any]) -> float:
        """Lightweight rule-based mortality salience scorer.

        Returns a float in [0.0, 1.0]. This is intentionally simple and
        interpretable; it can be replaced later with an embedding/classifier.
        """
        # Lexicon buckets
        temporal_risk = ["last", "soon", "forever", "end", "final", "won't be here", "one day", "last day"]
        legacy_terms = ["legacy", "what matters", "remember", "remembered", "mean to me", "will matter"]
        conditional_terms = [
            "what if",
            "if i die",
            "if i'm not here",
            "if i'm gone",
            "if i don't",
            "if i won't",
            "i don't want to be here",
            "don't want to be here",
            "want to be gone",
            "not be here",
        ]
        attachment_terms = ["i love", "so much", "wouldn't survive", "can't imagine", "can't live", "can't be without"]

        score = 0.0

        def count_matches(bucket):
            return sum(1 for kw in bucket if kw in text_lower)

        score += 0.22 * count_matches(temporal_risk)
        score += 0.25 * count_matches(legacy_terms)
        score += 0.27 * count_matches(conditional_terms)

        # Attachment intensity should amplify when intensity is high
        intensity = affect.get("intensity", 0.0)
        attach_matches = count_matches(attachment_terms)
        if intensity > 0.6:
            score += 0.3 * attach_matches
        else:
            score += 0.12 * attach_matches

        # Normalize / clamp
        try:
            score = max(0.0, min(1.0, float(score)))
        except Exception:
            score = 0.0

        return score

class ConversationMemory:
    """Track entities, themes, and emotional patterns across conversation turns."""
    
    def __init__(self):
        """Initialize memory system."""
        self.turns = []  # List of turn records with full context
        self.entities = {}  # name -> {role, valence, recency, frequency}
        self.themes = {}  # theme -> {frequency, last_seen, intensity_history}
        self.emotional_trajectory = []  # Valence over time
        self.repeated_patterns = []  # Themes that recur
        # Mortality/finitude tracking
        self.mortality_running = 0.0
        self.mortality_history = []
        
    def record_turn(self, user_input: str, affect: Dict, theme: str, glyph_name: str = "") -> None:
        """Record a conversation turn with full metadata."""
        self.turns.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "affect": affect,
            "theme": theme,
            "glyph_name": glyph_name,
            "entities_mentioned": self._extract_entities(user_input),
        })
        
        # Track emotional trajectory
        self.emotional_trajectory.append(affect["valence"])
        
        # Update theme frequency and detect patterns
        if theme not in self.themes:
            self.themes[theme] = {"frequency": 0, "last_seen": datetime.now(), "intensity_history": []}
        self.themes[theme]["frequency"] += 1
        self.themes[theme]["last_seen"] = datetime.now()
        self.themes[theme]["intensity_history"].append(affect["intensity"])
        
        # Detect if theme is recurring
        if self.themes[theme]["frequency"] > 1:
            self.repeated_patterns.append(theme)

        # Persist mortality salience for this turn (if present)
        mortality = 0.0
        try:
            mortality = float(affect.get("mortality_salience", 0.0))
        except Exception:
            mortality = 0.0

        self.mortality_history.append(mortality)
        # Exponential smoothing for conversation-level mortality
        alpha = 0.7
        self.mortality_running = (self.mortality_running * alpha) + (mortality * (1 - alpha))
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities and people references."""
        entities = []
        # Simple entity extraction - look for capitalized words and common relationships
        entity_patterns = {
            "partner": ["girlfriend", "boyfriend", "partner", "wife", "husband"],
            "family": ["mom", "dad", "mother", "father", "sister", "brother", "parent"],
            "work": ["boss", "colleague", "coworker", "job", "work"],
            "friend": ["friend", "friendship"],
        }
        
        text_lower = text.lower()
        for entity_type, keywords in entity_patterns.items():
            if any(kw in text_lower for kw in keywords):
                entities.append(entity_type)
        
        return entities
    
    def get_memory_context(self) -> Dict[str, Any]:
        """Get current memory context for use in response generation."""
        if not self.turns:
            return {"has_context": False}
        
        # Get most recent theme
        recent_theme = self.themes[max(self.themes.keys(), key=lambda k: self.themes[k]["last_seen"])] if self.themes else None
        
        # Detect if emotional trajectory is improving or worsening
        emotional_trend = "stable"
        if len(self.emotional_trajectory) > 2:
            recent_avg = sum(self.emotional_trajectory[-3:]) / 3
            early_avg = sum(self.emotional_trajectory[:3]) / 3 if len(self.emotional_trajectory) >= 3 else recent_avg
            if recent_avg > early_avg + 0.2:
                emotional_trend = "improving"
            elif recent_avg < early_avg - 0.2:
                emotional_trend = "worsening"
        
        # Detect recurring themes
        recurring = [t for t, data in self.themes.items() if data["frequency"] > 1]
        
        # Mortality trend detection (compare recent window to early average)
        mortality_trend = "stable"
        try:
            if len(self.mortality_history) >= 6:
                recent_avg = sum(self.mortality_history[-3:]) / 3
                early_avg = sum(self.mortality_history[:3]) / 3
                if recent_avg > early_avg + 0.1:
                    mortality_trend = "rising"
                elif recent_avg < early_avg - 0.1:
                    mortality_trend = "falling"
        except Exception:
            mortality_trend = "stable"

        return {
            "has_context": True,
            "num_turns": len(self.turns),
            "themes": dict(self.themes),
            "recurring_themes": recurring,
            "emotional_trend": emotional_trend,
            "recent_valence": self.emotional_trajectory[-1] if self.emotional_trajectory else 0,
            "repeated_patterns": list(set(self.repeated_patterns)),
            "mortality_salience": self.mortality_running,
            "mortality_trend": mortality_trend,
        }
    
    def get_frequency_reflection(self, theme: str) -> Optional[str]:
        """Generate a companionable reflection on a repeatedly mentioned theme."""
        if theme in self.themes and self.themes[theme]["frequency"] > 1:
            freq = self.themes[theme]["frequency"]
            # Use conversational language that feels like caring attention, not surveillance
            reflections = {
                2: f"I'm hearing {theme} come up again. That's important.",
                3: f"This keeps returning for you—this {theme}. That tells me something.",
                4: f"I keep hearing {theme} from you. It's sitting with you, isn't it?",
            }
            # Default for higher frequencies
            default = f"You keep returning to {theme}. I'm noticing the weight of that."
            return reflections.get(freq, default)
        return None


class FirstPersonOrchestrator:
    def __init__(self, user_id: str = "anon", conversation_id: str = "default"):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.affect_parser = AffectParser()
        self.memory = ConversationMemory()
        self.theme_frequency = {}

    def initialize_session(self):
        logger.debug(f"FirstPerson initialized for {self.user_id}")

    def handle_conversation_turn(self, user_input: str, glyph: Optional[Dict] = None) -> Dict:
        affect = self.affect_parser.analyze_affect(user_input)
        theme = self._extract_theme(user_input)
        
        # Record in memory
        glyph_name = glyph.get("glyph_name", "") if glyph else ""
        self.memory.record_turn(user_input, affect, theme, glyph_name)
        
        # Get memory context
        memory_context = self.memory.get_memory_context()
        
        # Check for frequency reflection
        frequency_reflection = self.memory.get_frequency_reflection(theme)
        
        # Check for safety signals (high mortality + negative valence)
        safety_signal = False
        try:
            mortality = affect.get("mortality_salience", 0.0)
            valence = affect.get("valence", 0.0)
            if mortality > 0.6 and valence < -0.6:
                safety_signal = True
        except Exception:
            pass
        
        return {
            "detected_theme": theme, 
            "theme_frequency": self.theme_frequency, 
            "memory_context_injected": memory_context.get("has_context", False),
            "affect_analysis": affect,
            "memory_context": memory_context,
            "frequency_reflection": frequency_reflection,
            "safety_signal": safety_signal,
        }

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
        
        # Get memory context to inform response
        memory_context = self.memory.get_memory_context()
        frequency_reflection = self.memory.get_frequency_reflection(theme)
        
        # Extract mortality signals
        mortality = affect.get("mortality_salience", 0.0)
        valence = affect.get("valence", 0.0)
        
        # Build response with memory awareness
        if affect["valence"] < -0.5:
            opening = f"I hear the weight of {theme}."
        else:
            opening = "You're naming something real."
        
        # Add memory-informed middle section
        middle = "Tell me more about what that feels like."
        
        # If theme is recurring and we have context, acknowledge it
        if frequency_reflection and len(self.memory.turns) > 1:
            middle = frequency_reflection + " " + middle
        
        # Apply mortality-informed response shaping
        if mortality > 0.6:
            if valence < -0.6:
                # High mortality + high negativity: safety-focused
                middle = (
                    "I'm noticing something in what you're saying — a weight around finitude, around loss. "
                    "That's important to name. Are you safe right now? What would help you feel grounded in this moment?"
                )
                opening = "That matters, and I want to make sure you're okay."
            else:
                # High mortality + neutral/positive: meaning-oriented
                middle = (
                    "I'm hearing something about what matters to you, and what you're afraid of losing. "
                    "That clarity — knowing what's precious — that's a kind of wisdom. What's the most important part of that?"
                )
                opening = "There's meaning in what you're sensing."
        else:
            # Add emotional trajectory awareness (low mortality)
            if memory_context.get("emotional_trend") == "worsening" and len(self.memory.turns) > 2:
                middle += " I'm noticing the weight increasing. What's happening?"
            elif memory_context.get("emotional_trend") == "improving" and len(self.memory.turns) > 2:
                middle += " I'm also noticing a shift. What's helping?"
        
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
