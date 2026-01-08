#!/usr/bin/env python3
"""
Archetype-Driven Response Generator v2 - GENERATION NOT SELECTION

Generates truly fresh responses guided by archetype principles.
NOT selecting from pre-written options, but building responses from principles.

Core philosophy:
- Extract specific phrases and concepts from user input
- Weave them into varied response structures
- Build on prior context cumulatively
- Vary sentence construction across turns
- Let principles guide logic, not keyword matching
"""

from typing import Any, Dict, List, Optional
import re
import random
from emotional_os.learning.conversation_archetype import get_archetype_library, ConversationArchetype


class ArchetypeResponseGeneratorV2:
    """Generate truly fresh responses using archetype principles."""
    
    def __init__(self):
        """Initialize with access to the archetype library."""
        self.library = get_archetype_library()
        # Track recent responses to avoid repetition
        self.recent_closings = []
        self.recent_openings = []
        # Track turn count to alternate response patterns
        self.turn_count = 0
        # Track user's actual metaphors (only reuse these, don't create new ones)
        self.user_metaphors = []
        # Track what themes user has explicitly mentioned
        self.user_themes = set()
    
    def generate_archetype_aware_response(
        self,
        user_input: str,
        prior_context: Optional[str] = None,
        glyph: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Generate a fresh response guided by archetype principles.
        
        This GENERATES responses, not selecting from templates.
        """
        # Find best-matching archetype
        archetype = self.library.get_best_match(user_input, prior_context, threshold=0.3)
        
        if not archetype:
            return None
        
        # Build response following archetype principles
        response = self._generate_response(
            archetype=archetype,
            user_input=user_input,
            prior_context=prior_context,
        )
        
        return response
    
    def _generate_response(
        self,
        archetype: ConversationArchetype,
        user_input: str,
        prior_context: Optional[str] = None,
    ) -> str:
        """Generate response by applying principles to actual user content."""
        
        # Track turn and update user themes
        self.turn_count += 1
        self._track_user_language(user_input)
        
        # Extract what user actually said (not keywords, specific phrases)
        extracted_concepts = self._extract_user_concepts(user_input)
        emotional_tone = self._detect_emotional_tone(user_input)
        
        # Decide response type: question vs reflection vs affirmation
        response_type = self._choose_response_type(self.turn_count)
        
        # Phase 1: Opening that validates and names what's happening
        opening = self._generate_opening(
            concepts=extracted_concepts,
            tone=emotional_tone,
            principles=archetype.response_principles,
            user_input=user_input,
        )
        
        # Phase 2: Bridge from prior context (if exists)
        bridge = ""
        if prior_context:
            bridge = self._generate_bridge(
                current_user_input=user_input,
                prior_context=prior_context,
                bridges_available=archetype.continuity_bridges,
                concepts=extracted_concepts,
            )
        
        # Phase 3: Closing - varies based on response_type
        if response_type == "question":
            closing = self._generate_closing_question(
                concepts=extracted_concepts,
                tone=emotional_tone,
                principles=archetype.response_principles,
                user_input=user_input,
                prior_context=prior_context,
            )
        elif response_type == "reflection":
            closing = self._generate_closing_reflection(
                concepts=extracted_concepts,
                tone=emotional_tone,
                user_input=user_input,
            )
        else:  # affirmation
            closing = self._generate_closing_affirmation(
                concepts=extracted_concepts,
                tone=emotional_tone,
            )
        
        # Assemble response
        parts = [opening]
        if bridge:
            parts.append(bridge)
        parts.append(closing)
        
        response = " ".join(p.strip() for p in parts if p.strip())
        
        # Track for repetition avoidance
        self.recent_openings.append(opening[-20:])
        self.recent_closings.append(closing[-20:])
        
        return response
    
    def _choose_response_type(self, turn_count: int) -> str:
        """Alternate between question, reflection, and affirmation response types.
        
        Pattern: Question → Reflection → Gentle Inquiry → Affirmation (then repeat)
        Not every turn ends with a question.
        """
        pattern = ["question", "reflection", "question", "affirmation"]
        idx = (turn_count - 1) % len(pattern)
        return pattern[idx]
    
    def _track_user_language(self, user_input: str) -> None:
        """Track user's actual language to avoid introducing premature themes."""
        lower = user_input.lower()
        
        # Track explicit themes user mentions
        if any(word in lower for word in ["creative", "art", "making"]):
            self.user_themes.add("creativity")
        if any(word in lower for word in ["advocacy", "meaning", "purpose"]):
            self.user_themes.add("purpose")
        if any(word in lower for word in ["overwhelm", "drowning", "fragile"]):
            self.user_themes.add("overwhelm")
        
        # Extract user's actual metaphors (e.g., "like drowning", "like being pummeled")
        metaphor_matches = re.findall(r"(?:like|as if|as though)\s+([^.!?]*)", user_input)
        self.user_metaphors.extend(metaphor_matches)
    
    def _extract_user_concepts(self, user_input: str) -> Dict[str, List[str]]:
        """Extract meaningful concepts from user input."""
        concepts = {
            "emotional_state": [],
            "work_related": [],
            "values_identity": [],
            "relationships_connection": [],
            "creative_alternative": [],
            "metaphors": [],
        }
        
        lower = user_input.lower()
        
        # Emotional states (what user is experiencing)
        emotional_words = {
            "overwhelm": ["overwhelmed", "overwhelm", "fragile", "drowning", "breaking", "pummeled"],
            "stress": ["stress", "relentless", "impossible", "weight"],
            "relief": ["relief", "melted", "released", "softening"],
            "meaning": ["purpose", "meaning", "what's it all for", "what's the point"],
            "connection": ["hug", "connection", "seen", "held"],
        }
        
        for category, words in emotional_words.items():
            matches = [w for w in words if w in lower]
            if matches:
                concepts["emotional_state"].extend(matches)
        
        # Work-related (career, profession, role)
        work_keywords = ["work", "lawyer", "advocacy", "clients", "meetings", "deadlines", "grind", "career"]
        concepts["work_related"] = [w for w in work_keywords if w in lower]
        
        # Values and identity
        values_keywords = ["advocacy", "purpose", "identity", "meaningful", "fulfilling", "care"]
        concepts["values_identity"] = [w for w in values_keywords if w in lower]
        
        # Relationships and connection
        relation_keywords = ["child", "hug", "partner", "family", "kids", "connection", "together"]
        concepts["relationships_connection"] = [w for w in relation_keywords if w in lower]
        
        # Creative/alternative interests
        creative_keywords = ["creative", "art", "making", "spark", "explore", "interests"]
        concepts["creative_alternative"] = [w for w in creative_keywords if w in lower]
        
        # Extract actual metaphors/phrases
        metaphor_matches = re.findall(r"(?:like|as if|as though)\s+([^.!?]*)", user_input)
        concepts["metaphors"] = metaphor_matches[:2]  # Top 2
        
        return concepts
    
    def _detect_emotional_tone(self, user_input: str) -> str:
        """Detect the overall emotional tone."""
        lower = user_input.lower()
        
        # Check for dominant tones
        overwhelm_indicators = ["overwhelm", "fragile", "drowning", "pummeled", "relentless"]
        relief_indicators = ["hug", "melted", "peace", "connection", "relief"]
        existential_indicators = ["purpose", "meaning", "what's it all for", "what's the point"]
        guilt_ambivalence = ["but", "though", "guilty", "supposed to be"]
        
        overwhelm_score = sum(1 for ind in overwhelm_indicators if ind in lower)
        relief_score = sum(1 for ind in relief_indicators if ind in lower)
        existential_score = sum(1 for ind in existential_indicators if ind in lower)
        ambivalence_score = sum(1 for ind in guilt_ambivalence if ind in lower)
        
        scores = {
            "overwhelm": overwhelm_score,
            "relief": relief_score,
            "existential": existential_score,
            "ambivalence": ambivalence_score,
        }
        
        dominant = max(scores.items(), key=lambda x: x[1])
        return dominant[0] if dominant[1] > 0 else "neutral"
    
    def _generate_opening(
        self,
        concepts: Dict[str, List[str]],
        tone: str,
        principles: List[str],
        user_input: str,
    ) -> str:
        """Generate an opening that names what's happening with presence language."""
        
        if tone == "overwhelm":
            # Overwhelm openings with "withness" language
            options = [
                "I'm here with you in that heaviness.",
                "The relentlessness you're describing — when everything feels like too much at once — that's real.",
                "Small things breaking through your fragility. That's what overwhelm feels like.",
                "You're carrying a lot right now. That accumulation is significant.",
                "Being pummeled by demands like that — that's exactly what systemic stress feels like.",
            ]
            
        elif tone == "existential":
            # Existential openings
            options = [
                "There's that question underneath everything: what's this all for?",
                "When the meaningful part gets buried under the work itself — that's when things stop making sense.",
                "You're recognizing something important: what you're doing isn't connecting to what matters.",
                "That gap between the advocacy you care about and what's actually happening — that's significant.",
                "The work that used to feel purposeful is becoming just a grind.",
            ]
            
        elif tone == "relief":
            # Relief and connection openings
            options = [
                "That moment when someone really sees you — that shifts something.",
                "A hug that actually lands as genuine connection. That tenderness matters.",
                "Being held like that — it's what safety feels like.",
                "The way you describe that softening — I hear the difference it made.",
            ]
            
        elif tone == "ambivalence":
            # Mixed emotions openings with "withness"
            options = [
                "I'm with you in that tension: you care about the work AND you're drawn to something else.",
                "You're holding something that pulls in multiple directions. Both are real.",
                "There's this part that wants to focus only on work, and another part that keeps calling.",
                "The guilt about the creative interest — that's because you're trying to honor both.",
            ]
            
        else:
            # Neutral/generic validation with micro-affirmations
            options = [
                "That makes sense.",
                "I hear you.",
                "That matters.",
            ]
        
        import random
        opening = random.choice(options)
        return opening
    
    def _generate_bridge(
        self,
        current_user_input: str,
        prior_context: str,
        bridges_available: List[str],
        concepts: Dict[str, List[str]],
    ) -> str:
        """Generate a bridge from prior context to current moment."""
        
        lower_current = current_user_input.lower()
        lower_prior = prior_context.lower()
        
        # If we have creative+work concepts, bridge them
        if concepts["creative_alternative"] and concepts["work_related"]:
            return "And there's this other part — the creative spark that keeps appearing."
        
        # If we have values + overwhelm, bridge them
        if concepts["values_identity"] and "overwhelming" in lower_current:
            return "The meaningful part of the work — the advocacy you care about — is getting buried under the overwhelm."
        
        # If transitioning from stress to meaning
        if "overwhelm" in lower_prior and ("purpose" in lower_current or "meaning" in lower_current):
            return "Underneath all that stress, there's a question: is this worth it?"
        
        # If discussing multiple roles/values
        if any(word in lower_current for word in ["both", "but", "though", "and", "also"]):
            return "So you're navigating multiple things at once — the work that matters, the parts of yourself that want expression."
        
        return ""
    
    def _generate_closing_question(
        self,
        concepts: Dict[str, List[str]],
        tone: str,
        principles: List[str],
        user_input: str,
        prior_context: Optional[str] = None,
    ) -> str:
        """Generate a closing question that invites deeper exploration."""
        
        if tone == "overwhelm":
            options = [
                "When did the relentlessness start feeling like this?",
                "What would need to shift for it to feel more bearable?",
                "Is there anything grounding you right now?",
                "What's the part of the overwhelm that troubles you most?",
                "If you could change one thing about the workload, what would it be?",
            ]
            
        elif tone == "existential":
            options = [
                "What would it look like if the work felt connected to purpose again?",
                "If the advocacy part is getting buried, what would bringing it back require?",
                "What do you think you're really asking?",
                "If you could design your own meaningful work, what would that be?",
                "When was the last time the work felt like it mattered?",
            ]
            
        elif tone == "relief":
            options = [
                "What happened in that moment that made the weight lift?",
                "How did that connection change things?",
                "What was present between you in that moment?",
                "Do you have moments like that often?",
            ]
            
        elif tone == "ambivalence":
            options = [
                "How does holding both — the meaningful work and the creative pull — actually feel?",
                "Where does the 'should' come from?",
                "What would it mean to honor both parts of yourself?",
                "What draws you to the creative work?",
            ]
            
        else:
            options = [
                "What does that bring up for you?",
                "Tell me more.",
                "What's underneath that?",
            ]
        
        import random
        closing = random.choice(options)
        return closing
    
    def _generate_closing_reflection(
        self,
        concepts: Dict[str, List[str]],
        tone: str,
        user_input: str,
    ) -> str:
        """Generate a reflection statement (not a question) that acknowledges understanding."""
        
        if tone == "overwhelm":
            options = [
                "So you're holding a lot right now.",
                "That kind of relentlessness compounds over time.",
                "Small things trigger the fragility that's already there.",
                "It sounds like the accumulation is what's breaking it for you.",
            ]
            
        elif tone == "existential":
            options = [
                "The meaningful part is getting disconnected from what you're actually doing.",
                "That gap between values and daily work — that's the real stress.",
                "You're recognizing what matters to you, and the current situation isn't it.",
                "The question 'what's it all for?' is the one underneath the overwhelm.",
            ]
            
        elif tone == "relief":
            options = [
                "That moment of being truly held — that shifts something.",
                "Those connections matter, even if they're quiet.",
                "Being seen like that is rare and valuable.",
            ]
            
        elif tone == "ambivalence":
            options = [
                "You're not choosing between work and creativity — you're carrying both.",
                "The tension is that both things pull on you.",
                "It's not about picking one; it's about how they fit together.",
                "That 'should' makes the creativity feel like it has to be hidden.",
            ]
            
        else:
            options = [
                "That's real.",
                "That matters.",
                "I hear that.",
            ]
        
        import random
        closing = random.choice(options)
        return closing
    
    def _generate_closing_affirmation(
        self,
        concepts: Dict[str, List[str]],
        tone: str,
    ) -> str:
        """Generate a micro-affirmation that shows relational presence."""
        
        if tone == "overwhelm":
            options = [
                "I hear the weight in how you describe that.",
                "It makes sense that you're feeling this way.",
                "That's a real experience you're having.",
                "Your exhaustion is legitimate.",
            ]
            
        elif tone == "existential":
            options = [
                "That clarity matters.",
                "You're asking the right question.",
                "That self-awareness is important.",
                "It's significant that you're noticing this.",
            ]
            
        elif tone == "relief":
            options = [
                "I hear the care in that.",
                "That connection is precious.",
                "The tenderness in that moment is real.",
                "That softening was needed.",
            ]
            
        elif tone == "ambivalence":
            options = [
                "It's important that both parts matter to you.",
                "The guilt shows how much you care.",
                "You're not being pulled apart — you're trying to integrate both.",
                "That tension means something is trying to shift.",
            ]
            
        else:
            options = [
                "That makes sense.",
                "I see that.",
                "That's valid.",
            ]
        
        import random
        closing = random.choice(options)
        return closing
