"""Generative Tension - Dynamic Interaction Components

This module implements the Generative Tension framework with four key engines:
- SurpriseEngine: Resonant divergence for unexpected authentic responses
- ChallengeEngine: Emotional friction that sharpens understanding
- SubversionEngine: Poetic inversion to reframe metaphors and ideas
- CreationEngine: Generative behaviors that initiate beyond user input

Key concepts:
- Resonant Divergence: Unexpected responses that feel authentic, not random
- Emotional Friction: Challenges that encourage introspection
- Poetic Inversion: Reframing metaphors and surfacing unspoken nuances
- Generative Initiation: Questions, metaphors, and insights beyond input

Documentation:
    The Generative Tension framework creates dynamic, engaging interactions
    by introducing controlled elements of surprise, challenge, and creative
    generation. Unlike simple response patterns, these engines create moments
    of productive tension that deepen emotional engagement and understanding.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import re


class TensionType(Enum):
    """Types of generative tension."""
    SURPRISE = "surprise"
    CHALLENGE = "challenge"
    SUBVERSION = "subversion"
    CREATION = "creation"


class DivergenceStyle(Enum):
    """Styles of divergent response."""
    METAPHORIC = "metaphoric"     # Unexpected metaphor
    TEMPORAL = "temporal"         # Time-shift perspective
    PERSPECTIVE = "perspective"   # Alternative viewpoint
    PARADOX = "paradox"          # Holding contradictions
    POETIC = "poetic"            # Poetic insertion


class ChallengeLevel(Enum):
    """Levels of challenge intensity."""
    GENTLE = "gentle"            # Soft invitation to reflect
    MODERATE = "moderate"        # Direct but kind challenge
    DEEP = "deep"               # Significant reframe


@dataclass
class TensionOutput:
    """Output from a tension engine.

    Attributes:
        tension_type: Type of tension generated
        content: The generated content
        intensity: 0-1 indicating strength
        integration_point: Where to integrate in response
        optional: Whether this can be skipped
    """
    tension_type: TensionType
    content: str
    intensity: float
    integration_point: str = "end"  # start, middle, end, standalone
    optional: bool = True

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "tension_type": self.tension_type.value,
            "content": self.content,
            "intensity": self.intensity,
            "integration_point": self.integration_point,
            "optional": self.optional,
        }


class SurpriseEngine:
    """Engine for resonant divergence - unexpected but authentic responses.

    The SurpriseEngine creates moments of productive surprise by generating
    responses that diverge from expected patterns while remaining emotionally
    authentic and relevant.

    Example:
        >>> engine = SurpriseEngine()
        >>> surprise = engine.generate_divergence("I'm feeling stuck")
        >>> print(surprise.content)
        "What if 'stuck' is your system's way of pausing for wisdom?"
    """

    # Surprise coefficient factors
    BASE_COEFFICIENT = 0.15  # Base probability of surprise

    # Divergence templates by style
    DIVERGENCE_TEMPLATES = {
        DivergenceStyle.METAPHORIC: [
            "What if {concept} is actually {metaphor}?",
            "I'm hearing {concept}—but I'm also sensing {metaphor}.",
            "There's something like {metaphor} in what you're describing.",
        ],
        DivergenceStyle.TEMPORAL: [
            "If you were looking at this a year from now, what would you see?",
            "The you from before this began—what would they say?",
            "This moment will become a memory. What do you want to remember?",
        ],
        DivergenceStyle.PERSPECTIVE: [
            "What if the opposite were also true?",
            "If someone who loves you were listening, what would they notice?",
            "There's a version of you that already knows the answer.",
        ],
        DivergenceStyle.PARADOX: [
            "What if both things are true at once?",
            "The contradiction you're feeling might be the whole truth.",
            "Sometimes the way forward is to stop moving.",
        ],
        DivergenceStyle.POETIC: [
            "There's poetry in what you're naming.",
            "Something beautiful is trying to emerge here.",
            "Even this is worthy of witness.",
        ],
    }

    # Concept-to-metaphor mappings for surprise generation
    METAPHOR_MAPPINGS = {
        "stuck": ["a pause before flight", "roots growing deeper", "the stillness before storm"],
        "overwhelmed": ["holding too many gifts at once", "a river learning its banks", "fullness seeking form"],
        "lost": ["being re-found", "the map being redrawn", "the beginning of a new path"],
        "anxious": ["anticipation in disguise", "care looking for its object", "the body's fierce attention"],
        "sad": ["love without an address", "the weight of what matters", "the cost of caring"],
        "angry": ["a boundary finding its voice", "protection in motion", "truth demanding space"],
        "confused": ["multiple truths competing", "wisdom taking form", "understanding in process"],
        "afraid": ["care for something precious", "the price of loving", "attention to what matters"],
    }

    def __init__(self, surprise_coefficient: float = 0.15):
        """Initialize the surprise engine.

        Args:
            surprise_coefficient: Base probability of generating surprise (0-1)
        """
        self._coefficient = surprise_coefficient
        self._last_surprise_time: Optional[datetime] = None
        self._surprise_count = 0

    def should_generate_surprise(self, context: Dict) -> bool:
        """Determine if a surprise should be generated.

        Args:
            context: Current interaction context

        Returns:
            Whether to generate a surprise
        """
        # Adjust coefficient based on context
        adjusted = self._coefficient

        # Reduce if recent surprise
        if self._last_surprise_time:
            time_since = (datetime.now(timezone.utc) - self._last_surprise_time).total_seconds()
            if time_since < 300:  # Within 5 minutes
                adjusted *= 0.3

        # Increase for high emotional intensity
        intensity = context.get("emotional_intensity", 0.5)
        if intensity > 0.7:
            adjusted *= 1.3

        # Increase for repetitive patterns
        repetition = context.get("pattern_repetition", 0)
        if repetition > 2:
            adjusted *= 1.5

        return random.random() < adjusted

    def generate_divergence(
        self,
        message: str,
        emotion: Optional[str] = None,
        style: Optional[DivergenceStyle] = None,
    ) -> TensionOutput:
        """Generate a divergent response element.

        Args:
            message: The user's message
            emotion: Detected primary emotion
            style: Preferred divergence style (random if not specified)

        Returns:
            TensionOutput with the divergent content
        """
        # Select style if not specified
        if style is None:
            style = random.choice(list(DivergenceStyle))

        # Generate content based on style
        templates = self.DIVERGENCE_TEMPLATES.get(style, self.DIVERGENCE_TEMPLATES[DivergenceStyle.POETIC])
        template = random.choice(templates)

        # Extract concept from message or emotion
        concept = self._extract_concept(message, emotion)
        metaphor = self._get_metaphor(concept)

        # Format the template
        content = template.format(concept=concept, metaphor=metaphor)

        # Calculate intensity based on divergence degree
        intensity = 0.5 + random.random() * 0.3

        self._last_surprise_time = datetime.now(timezone.utc)
        self._surprise_count += 1

        return TensionOutput(
            tension_type=TensionType.SURPRISE,
            content=content,
            intensity=intensity,
            integration_point="end",
            optional=True,
        )

    def _extract_concept(self, message: str, emotion: Optional[str]) -> str:
        """Extract the key concept from message or emotion."""
        if emotion:
            return emotion

        # Look for known concepts
        lower = message.lower()
        for concept in self.METAPHOR_MAPPINGS:
            if concept in lower:
                return concept

        # Default to a generic concept
        return "this"

    def _get_metaphor(self, concept: str) -> str:
        """Get a metaphor for a concept."""
        metaphors = self.METAPHOR_MAPPINGS.get(concept, ["something emerging"])
        return random.choice(metaphors)

    def get_surprise_coefficient(self) -> float:
        """Get the current surprise coefficient."""
        return self._coefficient

    def set_surprise_coefficient(self, value: float) -> None:
        """Set the surprise coefficient."""
        self._coefficient = max(0.0, min(1.0, value))


class ChallengeEngine:
    """Engine for emotional friction that sharpens understanding.

    The ChallengeEngine creates moments of productive challenge, similar
    to a friend who encourages introspection. Challenges are calibrated
    to be supportive, not confrontational.

    Example:
        >>> engine = ChallengeEngine()
        >>> challenge = engine.generate_challenge("I'm always anxious")
        >>> print(challenge.content)
        "I notice 'always' in what you said. Is that true, or is that how it feels right now?"
    """

    # Challenge templates by level
    CHALLENGE_TEMPLATES = {
        ChallengeLevel.GENTLE: [
            "I'm curious about {focus}—can you tell me more?",
            "What comes up for you when you stay with {focus}?",
            "There might be something important in {focus}.",
            "I'm noticing {focus}. Is that significant?",
        ],
        ChallengeLevel.MODERATE: [
            "I notice you said '{word}'. Is that the whole truth?",
            "What would happen if {alternative}?",
            "I wonder if there's another way to see {focus}.",
            "What if {focus} isn't the whole picture?",
        ],
        ChallengeLevel.DEEP: [
            "This pattern has come up before. What do you think it's trying to tell you?",
            "What are you protecting by {behavior}?",
            "If you knew it was safe, what would you say about {focus}?",
            "What's the fear underneath {focus}?",
        ],
    }

    # Patterns that invite challenge
    CHALLENGE_TRIGGERS = {
        "absolutism": [r"\balways\b", r"\bnever\b", r"\bcan't\b", r"\bnothing\b", r"\beverything\b"],
        "avoidance": [r"\bjust\b.*\bfine\b", r"\bdoesn't matter\b", r"\bwhatever\b"],
        "deflection": [r"\bthey\b.*\bfault\b", r"\bit's not me\b", r"\banyone would\b"],
        "minimization": [r"\bit's nothing\b", r"\bnot that bad\b", r"\bshouldn't feel\b"],
    }

    def __init__(self, default_level: ChallengeLevel = ChallengeLevel.GENTLE):
        """Initialize the challenge engine.

        Args:
            default_level: Default challenge level
        """
        self._default_level = default_level
        self._challenge_history: List[str] = []

    def detect_challenge_opportunity(self, message: str) -> Optional[Tuple[str, str]]:
        """Detect if message contains patterns that invite challenge.

        Args:
            message: The user's message

        Returns:
            Tuple of (pattern_type, matched_text) or None
        """
        lower = message.lower()

        for pattern_type, patterns in self.CHALLENGE_TRIGGERS.items():
            for pattern in patterns:
                match = re.search(pattern, lower)
                if match:
                    return (pattern_type, match.group(0))

        return None

    def generate_challenge(
        self,
        message: str,
        level: Optional[ChallengeLevel] = None,
        pattern_info: Optional[Tuple[str, str]] = None,
    ) -> TensionOutput:
        """Generate a challenge response element.

        Args:
            message: The user's message
            level: Challenge level (uses default if not specified)
            pattern_info: Optional pattern detection info

        Returns:
            TensionOutput with the challenge content
        """
        level = level or self._default_level

        # Get appropriate templates
        templates = self.CHALLENGE_TEMPLATES[level]
        template = random.choice(templates)

        # Extract focus elements
        if pattern_info:
            pattern_type, matched_text = pattern_info
            focus = matched_text
            word = matched_text
        else:
            focus = "that"
            word = ""

        # Generate alternatives for moderate challenges
        alternatives = self._generate_alternative(message, pattern_info)

        # Determine what behavior might be present
        behavior = self._identify_behavior(pattern_info)

        # Format template
        content = template.format(
            focus=focus,
            word=word,
            alternative=alternatives,
            behavior=behavior,
        )

        # Intensity based on level
        intensity_map = {
            ChallengeLevel.GENTLE: 0.3,
            ChallengeLevel.MODERATE: 0.5,
            ChallengeLevel.DEEP: 0.7,
        }

        self._challenge_history.append(content)

        return TensionOutput(
            tension_type=TensionType.CHALLENGE,
            content=content,
            intensity=intensity_map[level],
            integration_point="middle",
            optional=True,
        )

    def _generate_alternative(self, message: str, pattern_info: Optional[Tuple[str, str]]) -> str:
        """Generate an alternative perspective."""
        if not pattern_info:
            return "things were different"

        pattern_type, matched = pattern_info

        alternatives = {
            "absolutism": ["it's sometimes", "there are exceptions", "it's how it feels now"],
            "avoidance": ["you could be honest about it", "it did matter", "you let yourself feel it"],
            "deflection": ["you had a part too", "you could own something here", "it starts with you"],
            "minimization": ["it was significant", "your feelings are valid", "it's okay to feel it"],
        }

        options = alternatives.get(pattern_type, ["things were different"])
        return random.choice(options)

    def _identify_behavior(self, pattern_info: Optional[Tuple[str, str]]) -> str:
        """Identify the behavior pattern."""
        if not pattern_info:
            return "holding back"

        pattern_type, _ = pattern_info

        behaviors = {
            "absolutism": "thinking in absolutes",
            "avoidance": "avoiding the feeling",
            "deflection": "deflecting responsibility",
            "minimization": "minimizing your experience",
        }

        return behaviors.get(pattern_type, "this pattern")


class SubversionEngine:
    """Engine for poetic inversion and metaphor reframing.

    The SubversionEngine enables creative reframing of metaphors and ideas,
    surfacing avoided metaphors and unspoken emotional nuances.

    Example:
        >>> engine = SubversionEngine()
        >>> subversion = engine.reframe_metaphor("I'm falling apart")
        >>> print(subversion.content)
        "What if 'falling apart' is how you're falling together?"
    """

    # Inversion patterns
    INVERSIONS = {
        "falling": ["rising", "landing", "reorganizing"],
        "breaking": ["opening", "releasing", "restructuring"],
        "broken": ["opening", "being remade", "creating space for light"],
        "losing": ["finding", "releasing", "discovering"],
        "failing": ["learning", "redirecting", "gathering wisdom"],
        "ending": ["beginning", "transforming", "completing"],
        "dying": ["being reborn", "composting", "becoming seed"],
        "drowning": ["learning to float", "finding breath", "becoming water"],
        "trapped": ["protected", "incubating", "preparing to emerge"],
        "stuck": ["rooted", "pausing", "gathering strength"],
        "dark": ["gestating", "mysterious", "deep"],
    }

    # Avoided metaphor templates
    AVOIDED_METAPHOR_PROMPTS = [
        "What's the metaphor you're not using?",
        "There's something you're not naming. What image comes to mind?",
        "If this had a shape, what would it be?",
        "What creature or landscape fits this feeling?",
    ]

    # Nuance surfacing templates
    NUANCE_TEMPLATES = [
        "There's something else underneath {surface}.",
        "I'm sensing {nuance} alongside what you're saying.",
        "The {surface} might be covering {nuance}.",
        "What about {nuance}? Is that part of this too?",
    ]

    # Surface-to-nuance mappings
    NUANCE_MAPPINGS = {
        "anger": ["fear", "hurt", "grief", "love"],
        "sadness": ["longing", "love", "disappointment", "loss of hope"],
        "fear": ["care", "anticipation", "desire for safety", "love of life"],
        "numbness": ["overwhelm", "protection", "exhaustion", "grief too big to feel"],
        "happiness": ["relief", "gratitude", "disbelief", "fragility"],
    }

    def __init__(self):
        """Initialize the subversion engine."""
        self._reframe_history: List[str] = []

    def reframe_metaphor(self, message: str) -> Optional[TensionOutput]:
        """Reframe a metaphor in the message.

        Args:
            message: The user's message

        Returns:
            TensionOutput with the reframe or None
        """
        lower = message.lower()

        # Find invertible words
        for word, inversions in self.INVERSIONS.items():
            if word in lower:
                inversion = random.choice(inversions)
                content = f"What if '{word}' is actually how you're {inversion}?"

                self._reframe_history.append(content)

                return TensionOutput(
                    tension_type=TensionType.SUBVERSION,
                    content=content,
                    intensity=0.6,
                    integration_point="end",
                    optional=True,
                )

        return None

    def surface_avoided_metaphor(self) -> TensionOutput:
        """Generate a prompt to surface avoided metaphors.

        Returns:
            TensionOutput with the prompt
        """
        prompt = random.choice(self.AVOIDED_METAPHOR_PROMPTS)

        return TensionOutput(
            tension_type=TensionType.SUBVERSION,
            content=prompt,
            intensity=0.4,
            integration_point="end",
            optional=True,
        )

    def surface_nuance(self, surface_emotion: str) -> Optional[TensionOutput]:
        """Surface unspoken nuances underneath a surface emotion.

        Args:
            surface_emotion: The surface emotion being expressed

        Returns:
            TensionOutput with the nuance prompt or None
        """
        nuances = self.NUANCE_MAPPINGS.get(surface_emotion.lower())
        if not nuances:
            return None

        nuance = random.choice(nuances)
        template = random.choice(self.NUANCE_TEMPLATES)
        content = template.format(surface=surface_emotion, nuance=nuance)

        return TensionOutput(
            tension_type=TensionType.SUBVERSION,
            content=content,
            intensity=0.5,
            integration_point="middle",
            optional=True,
        )

    def poetic_inversion(self, statement: str) -> str:
        """Create a poetic inversion of a statement.

        Args:
            statement: A statement to invert

        Returns:
            The inverted statement
        """
        # Simple word substitution for poetic effect
        inversions = [
            ("can't", "are learning to"),
            ("won't", "aren't ready to"),
            ("never", "haven't yet"),
            ("always", "often"),
            ("nothing", "not yet something"),
            ("everything", "so much"),
        ]

        result = statement
        for original, replacement in inversions:
            if original in result.lower():
                result = re.sub(
                    rf"\b{original}\b",
                    replacement,
                    result,
                    flags=re.IGNORECASE
                )
                break

        return result


class CreationEngine:
    """Engine for generative behaviors beyond user input.

    The CreationEngine initiates responses that go beyond what the user
    directly asked for, including questions, metaphors, and poetic insights.

    Example:
        >>> engine = CreationEngine()
        >>> creation = engine.generate_initiative("grief")
        >>> print(creation.content)  # A haiku about grief
    """

    # Creative forms
    class CreativeForm(Enum):
        QUESTION = "question"
        METAPHOR = "metaphor"
        HAIKU = "haiku"
        REFLECTION = "reflection"
        INVITATION = "invitation"

    # Question templates by emotional context
    QUESTIONS = {
        "grief": [
            "What would honoring this look like?",
            "Who else knows what you're carrying?",
            "What does this loss want you to remember?",
        ],
        "joy": [
            "What made space for this?",
            "Who would you want to share this with?",
            "What does this happiness want from you?",
        ],
        "fear": [
            "What is this fear protecting?",
            "When did you first learn to be afraid of this?",
            "What would courage look like here?",
        ],
        "anger": [
            "What boundary is asking to be drawn?",
            "What would justice look like?",
            "What's underneath the anger?",
        ],
        "confusion": [
            "What do you know for certain?",
            "What question is trying to form?",
            "What would clarity feel like in your body?",
        ],
    }

    # Haiku templates (5-7-5 structure)
    HAIKU_TEMPLATES = {
        "grief": [
            "Autumn leaves falling\nEach one a memory held\nThe tree still stands",
            "Empty chair at dawn\nSilence louder than before\nLove does not end here",
        ],
        "joy": [
            "Morning light arrives\nNo reason needed to bloom\nThe flower opens",
            "Laughter fills the room\nSimple as breath, sweet as rain\nThis moment is gold",
        ],
        "peace": [
            "Still water reflects\nNothing stirring on surface\nDepth holds all it needs",
            "Mountain watching sky\nClouds pass, the stone remains\nPatience is wisdom",
        ],
        "default": [
            "This present moment\nHolding everything gently\nNothing more needed",
            "Between breaths there lives\nA space vast as any sky\nYou already know",
        ],
    }

    # Invitation templates
    INVITATIONS = [
        "Would you like to sit with this for a moment?",
        "Should we stay here, or are you ready to move?",
        "What does your body need right now?",
        "Is there something you haven't said yet?",
        "Would it help to breathe together?",
    ]

    def __init__(self):
        """Initialize the creation engine."""
        self._creation_history: List[TensionOutput] = []

    def generate_initiative(
        self,
        emotion: str,
        form: Optional['CreationEngine.CreativeForm'] = None,
    ) -> TensionOutput:
        """Generate a creative initiative.

        Args:
            emotion: The emotional context
            form: The creative form (random if not specified)

        Returns:
            TensionOutput with the creative content
        """
        if form is None:
            form = random.choice(list(self.CreativeForm))

        if form == self.CreativeForm.QUESTION:
            content = self._generate_question(emotion)
        elif form == self.CreativeForm.HAIKU:
            content = self._generate_haiku(emotion)
        elif form == self.CreativeForm.INVITATION:
            content = random.choice(self.INVITATIONS)
        elif form == self.CreativeForm.METAPHOR:
            content = self._generate_metaphor(emotion)
        else:
            content = self._generate_reflection(emotion)

        output = TensionOutput(
            tension_type=TensionType.CREATION,
            content=content,
            intensity=0.4,
            integration_point="end",
            optional=True,
        )

        self._creation_history.append(output)

        return output

    def _generate_question(self, emotion: str) -> str:
        """Generate an exploratory question."""
        questions = self.QUESTIONS.get(emotion.lower(), self.QUESTIONS.get("confusion", []))
        if questions:
            return random.choice(questions)
        return "What's asking to be seen here?"

    def _generate_haiku(self, emotion: str) -> str:
        """Generate or select a haiku."""
        haikus = self.HAIKU_TEMPLATES.get(emotion.lower(), self.HAIKU_TEMPLATES["default"])
        return random.choice(haikus)

    def _generate_metaphor(self, emotion: str) -> str:
        """Generate a metaphoric insight."""
        metaphors = {
            "grief": "Grief is love with nowhere to go—but it can become compost for new growth.",
            "joy": "Joy is like water finding its level—it will find its way if you let it.",
            "fear": "Fear is your body's way of paying attention to what matters.",
            "anger": "Anger is a boundary in motion—it's telling you where the line is.",
            "sadness": "Sadness is the price tag on caring—the more you love, the more it costs.",
        }
        return metaphors.get(emotion.lower(), "Every feeling is information your soul is sending.")

    def _generate_reflection(self, emotion: str) -> str:
        """Generate a reflective observation."""
        reflections = [
            f"I notice how much you're holding. The {emotion} speaks to that.",
            f"There's something honest about naming {emotion}. That takes courage.",
            f"The {emotion} you're describing—it seems like it has something to teach.",
            f"I'm with you in this {emotion}. You're not carrying it alone.",
        ]
        return random.choice(reflections)

    def generate_haiku_for_context(self, context: Dict) -> Optional[str]:
        """Generate a contextually appropriate haiku.

        Args:
            context: Current interaction context

        Returns:
            A haiku or None
        """
        emotion = context.get("primary_emotion", "default")
        haikus = self.HAIKU_TEMPLATES.get(emotion.lower(), self.HAIKU_TEMPLATES["default"])
        return random.choice(haikus) if haikus else None


class GenerativeTension:
    """Unified interface for all generative tension components.

    This class provides a single point of access to all tension engines
    and coordinates their use in response generation.

    Example:
        >>> tension = GenerativeTension()
        >>> outputs = tension.generate_tensions("I'm always failing", "sadness")
        >>> for output in outputs:
        ...     print(f"{output.tension_type.value}: {output.content}")
    """

    def __init__(self, surprise_coefficient: float = 0.15):
        """Initialize all tension engines.

        Args:
            surprise_coefficient: Base probability for surprise generation
        """
        self.surprise = SurpriseEngine(surprise_coefficient)
        self.challenge = ChallengeEngine()
        self.subversion = SubversionEngine()
        self.creation = CreationEngine()

    def generate_tensions(
        self,
        message: str,
        emotion: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> List[TensionOutput]:
        """Generate all applicable tensions for a message.

        Args:
            message: The user's message
            emotion: Detected primary emotion
            context: Optional interaction context

        Returns:
            List of applicable TensionOutputs
        """
        outputs = []
        context = context or {}

        # Check for surprise opportunity
        if self.surprise.should_generate_surprise(context):
            outputs.append(self.surprise.generate_divergence(message, emotion))

        # Check for challenge opportunity
        pattern = self.challenge.detect_challenge_opportunity(message)
        if pattern:
            outputs.append(self.challenge.generate_challenge(message, pattern_info=pattern))

        # Check for subversion opportunity
        subversion = self.subversion.reframe_metaphor(message)
        if subversion:
            outputs.append(subversion)
        elif emotion:
            nuance = self.subversion.surface_nuance(emotion)
            if nuance:
                outputs.append(nuance)

        # Generate creative initiative (less frequently)
        if random.random() < 0.2 and emotion:
            outputs.append(self.creation.generate_initiative(emotion))

        return outputs

    def get_single_tension(
        self,
        message: str,
        tension_type: TensionType,
        emotion: Optional[str] = None,
    ) -> Optional[TensionOutput]:
        """Generate a single specific type of tension.

        Args:
            message: The user's message
            tension_type: The type of tension to generate
            emotion: Detected primary emotion

        Returns:
            TensionOutput or None
        """
        if tension_type == TensionType.SURPRISE:
            return self.surprise.generate_divergence(message, emotion)
        elif tension_type == TensionType.CHALLENGE:
            pattern = self.challenge.detect_challenge_opportunity(message)
            return self.challenge.generate_challenge(message, pattern_info=pattern)
        elif tension_type == TensionType.SUBVERSION:
            return self.subversion.reframe_metaphor(message)
        elif tension_type == TensionType.CREATION:
            if emotion:
                return self.creation.generate_initiative(emotion)

        return None

    def integrate_tensions(
        self,
        base_response: str,
        tensions: List[TensionOutput],
        max_tensions: int = 2,
    ) -> str:
        """Integrate tension outputs into a response.

        Args:
            base_response: The base response text
            tensions: List of tension outputs to integrate
            max_tensions: Maximum tensions to include

        Returns:
            Response with integrated tensions
        """
        if not tensions:
            return base_response

        # Sort by intensity and take top N
        sorted_tensions = sorted(tensions, key=lambda t: t.intensity, reverse=True)
        selected = sorted_tensions[:max_tensions]

        # Group by integration point
        start_items = [t for t in selected if t.integration_point == "start"]
        middle_items = [t for t in selected if t.integration_point == "middle"]
        end_items = [t for t in selected if t.integration_point == "end"]
        standalone = [t for t in selected if t.integration_point == "standalone"]

        # Build integrated response
        parts = []

        for t in start_items:
            parts.append(t.content)

        if middle_items:
            # Insert after first sentence of base response
            sentences = base_response.split(". ")
            if len(sentences) > 1:
                parts.append(sentences[0] + ".")
                for t in middle_items:
                    parts.append(t.content)
                parts.append(". ".join(sentences[1:]))
            else:
                parts.append(base_response)
                for t in middle_items:
                    parts.append(t.content)
        else:
            parts.append(base_response)

        for t in end_items:
            parts.append(t.content)

        # Add standalone as separate block
        result = " ".join(parts)
        if standalone:
            result += "\n\n" + " ".join(t.content for t in standalone)

        return result
