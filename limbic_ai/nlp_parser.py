"""
NLP-based parser to extract emotional features from text scenarios.

This module analyzes user input text to identify emotional features
that will be mapped to limbic activations.
"""

import re
from typing import Dict, List, Tuple
from limbic_ai.models import EmotionalFeatures, clamp_01


class EmotionalFeatureExtractor:
    """Extract emotional features from scenario text using pattern matching and keywords."""
    
    # Keywords indicating social rejection/exclusion
    SOCIAL_REJECTION_KEYWORDS = {
        "break", "broke up", "breakup", "rejected", "rejection", "alone", "lonely", 
        "excluded", "left", "abandoned", "kicked out", "fired", "dismissed", 
        "not invited", "friend zone", "betrayed", "cheated", "divorce", "separated"
    }
    
    # Keywords indicating self-blame
    SELF_BLAME_KEYWORDS = {
        "my fault", "i failed", "my mistake", "i should", "i didn't", "i couldn't",
        "because of me", "my problem", "i screwed up", "i messed up", "i'm the problem",
        "i'm to blame", "my responsibility", "i made", "i could have"
    }
    
    # Keywords indicating blaming others
    OTHER_BLAME_KEYWORDS = {
        "their fault", "they failed", "they should", "they didn't", "because of them",
        "they're to blame", "it's their problem", "they screwed up", "they messed up",
        "they're the problem", "unfair", "unjust", "unreasonable", "selfish", "inconsiderate"
    }
    
    # Keywords indicating empathy/perspective-taking
    EMPATHY_KEYWORDS = {
        "understand", "feel for", "support", "help", "care", "compassionate", "empathy",
        "perspective", "their pain", "how they feel", "imagine", "put myself", "see their"
    }
    
    # Keywords indicating rationalization/downregulation
    RATIONALIZATION_KEYWORDS = {
        "it's not a big deal", "happens all the time", "no big deal", "over-dramatic", 
        "too sensitive", "exaggerate", "not that bad", "it's fine", "whatever",
        "doesn't matter", "people get over it", "common", "normal", "not unusual"
    }
    
    # Keywords indicating threat to identity
    IDENTITY_THREAT_KEYWORDS = {
        "who i am", "my character", "my worth", "my value", "define me", "what i am",
        "my identity", "my legacy", "i'm", "i am", "my reputation", "people think"
    }
    
    # Keywords indicating loss of reward
    LOSS_KEYWORDS = {
        "lost", "lose", "no longer", "can't", "couldn't", "failed", "won't", "won't have",
        "disappointed", "gone", "ended", "finished", "over", "ruined", "destroyed"
    }
    
    def __init__(self):
        """Initialize the extractor with compiled regex patterns."""
        self.social_rejection_pattern = self._compile_pattern(self.SOCIAL_REJECTION_KEYWORDS)
        self.self_blame_pattern = self._compile_pattern(self.SELF_BLAME_KEYWORDS)
        self.other_blame_pattern = self._compile_pattern(self.OTHER_BLAME_KEYWORDS)
        self.empathy_pattern = self._compile_pattern(self.EMPATHY_KEYWORDS)
        self.rationalization_pattern = self._compile_pattern(self.RATIONALIZATION_KEYWORDS)
        self.identity_threat_pattern = self._compile_pattern(self.IDENTITY_THREAT_KEYWORDS)
        self.loss_pattern = self._compile_pattern(self.LOSS_KEYWORDS)
    
    @staticmethod
    def _compile_pattern(keywords: set) -> re.Pattern:
        """Compile keyword list into regex pattern."""
        escaped_keywords = [re.escape(kw) for kw in keywords]
        pattern = r'\b(' + '|'.join(escaped_keywords) + r')\b'
        return re.compile(pattern, re.IGNORECASE)
    
    def extract_features(self, text: str) -> EmotionalFeatures:
        """Extract emotional features from scenario text.
        
        Args:
            text: User-provided scenario description
            
        Returns:
            EmotionalFeatures with extracted values (0-1)
        """
        # Normalize text
        text_lower = text.lower()
        text_length = len(text.split())
        
        # Count keyword matches for each feature
        social_rejection_count = len(self.social_rejection_pattern.findall(text_lower))
        self_blame_count = len(self.self_blame_pattern.findall(text_lower))
        other_blame_count = len(self.other_blame_pattern.findall(text_lower))
        empathy_count = len(self.empathy_pattern.findall(text_lower))
        rationalization_count = len(self.rationalization_pattern.findall(text_lower))
        identity_threat_count = len(self.identity_threat_pattern.findall(text_lower))
        loss_count = len(self.loss_pattern.findall(text_lower))
        
        # Normalize by text length to account for scenario length
        normalization_factor = max(1, text_length / 100)  # Normalize to ~100 word baseline
        
        # Convert counts to 0-1 scale (density-based)
        social_rejection = clamp_01(social_rejection_count / (3 * normalization_factor))
        self_blame = clamp_01(self_blame_count / (3 * normalization_factor))
        other_blame = clamp_01(other_blame_count / (3 * normalization_factor))
        empathy_for_other = clamp_01(empathy_count / (2 * normalization_factor))
        rationalization = clamp_01(rationalization_count / (2 * normalization_factor))
        threat_to_identity = clamp_01(identity_threat_count / (2 * normalization_factor))
        loss_of_reward = clamp_01(loss_count / (3 * normalization_factor))
        
        return EmotionalFeatures(
            social_rejection=social_rejection,
            self_blame=self_blame,
            other_blame=other_blame,
            empathy_for_other=empathy_for_other,
            rationalization=rationalization,
            threat_to_identity=threat_to_identity,
            loss_of_reward=loss_of_reward,
        )
    
    def get_detected_themes(self, text: str) -> Dict[str, List[str]]:
        """Return themes detected in the text.
        
        Args:
            text: User scenario
            
        Returns:
            Dictionary mapping theme names to detected keywords
        """
        text_lower = text.lower()
        
        return {
            "social_rejection": self.social_rejection_pattern.findall(text_lower),
            "self_blame": self.self_blame_pattern.findall(text_lower),
            "other_blame": self.other_blame_pattern.findall(text_lower),
            "empathy": self.empathy_pattern.findall(text_lower),
            "rationalization": self.rationalization_pattern.findall(text_lower),
            "identity_threat": self.identity_threat_pattern.findall(text_lower),
            "loss": self.loss_pattern.findall(text_lower),
        }
