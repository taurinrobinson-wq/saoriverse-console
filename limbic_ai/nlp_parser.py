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
        "rejected", "rejection", "abandoned", "left me", "left alone", "alone", "lonely",
        "excluded", "not invited", "dismissed", "ignored", "not heard", "not listened to",
        "pushed away", "avoided", "ghosted", "betrayed", "betrayal", "broke up", "breakup",
        "break up", "fired", "let go", "kicked out", "cast out", "shunned",
        "friend zone", "cheated", "unfaithful", "divorce", "divorced", "separated",
        "thrown away", "discarded", "don't want me", "doesn't want me", "unwanted",
        "not good enough", "not worthy", "unvalued", "disrespected", "disrespect"
    }
    
    # Keywords indicating self-blame
    SELF_BLAME_KEYWORDS = {
        "my fault", "i failed", "i failed", "my mistake", "i should have", "i should",
        "i didn't", "i couldn't", "because of me", "my problem", "i screwed up",
        "i messed up", "i'm the problem", "i'm to blame", "my responsibility",
        "i made", "i could have", "guilty", "ashamed", "embarrassed", "shame",
        "embarrass", "regret", "remorse", "i take responsibility", "a failure",
        "i'm a failure", "not good enough", "incompetent", "inadequate", "i failed them",
        "my fault entirely", "i didn't try hard enough", "i gave up"
    }
    
    # Keywords indicating blaming others
    OTHER_BLAME_KEYWORDS = {
        "their fault", "they failed", "they should", "they didn't", "because of them",
        "they're to blame", "it's their problem", "they screwed up", "they messed up",
        "they're the problem", "unfair", "unjust", "unreasonable", "selfish", "inconsiderate",
        "they're wrong", "they're the problem", "his fault", "her fault", "their fault",
        "they don't care", "they don't try", "they don't listen", "they don't understand",
        "they're being unfair", "they're being selfish", "they're being hurtful"
    }
    
    # Keywords indicating empathy/perspective-taking
    EMPATHY_KEYWORDS = {
        "understand", "understanding", "feel for", "feel their pain", "support",
        "supporting", "help", "helping", "care", "caring", "compassion", "compassionate",
        "empathy", "empathic", "perspective", "their pain", "their suffering",
        "how they feel", "imagine", "put myself", "put myself in their shoes",
        "see their", "see where they're coming from", "i get it", "i can see why",
        "concerned about", "worried for", "worried about", "their distress",
        "their struggle", "their hurt", "their feelings", "their perspective"
    }
    
    # Keywords indicating rationalization/downregulation
    RATIONALIZATION_KEYWORDS = {
        "it's not a big deal", "happens all the time", "no big deal", "over-dramatic",
        "too sensitive", "exaggerate", "not that bad", "it's fine", "whatever",
        "doesn't matter", "people get over it", "common", "normal", "not unusual",
        "i don't see the problem", "i don't get why", "don't understand the big deal",
        "the big deal", "making a big deal", "making a mountain", "overreacting",
        "being dramatic", "too dramatic", "can happen to anyone", "it's just",
        "just happens", "it happens", "move on", "get over it", "not that serious"
    }
    
    # Keywords indicating threat to identity
    IDENTITY_THREAT_KEYWORDS = {
        "scared", "afraid", "anxiety", "anxious", "insecure", "insecurity",
        "threatened", "unsafe", "panicked", "panic", "terrified", "fear",
        "fear of losing", "fear she'll leave", "fear he'll leave", "fear losing",
        "who i am", "my character", "my worth", "my value", "define me",
        "what i am", "my identity", "my legacy", "my reputation", "people think",
        "they'll think", "what people think", "my self worth", "challenge",
        "challenged", "questioned", "doubt myself", "doubting myself", "unsure of myself"
    }
    
    # Keywords indicating loss of reward
    LOSS_KEYWORDS = {
        "lost", "lose", "losing", "no longer", "can't have", "couldn't have",
        "failed to", "lost something", "losing her", "losing him", "losing the",
        "losing them", "losing connection", "disappointed", "let down",
        "gone", "ended", "finished", "over", "ruined", "destroyed",
        "won't have", "won't be able", "can't be", "can't have", "no more",
        "never again", "can't go back", "nothing will be the same", "it's over",
        "lost opportunity", "missed opportunity", "regret", "regretful", "wishful",
        "wish i had", "wish i could", "what could have been", "what if"
    }
    
    # Phrase patterns for emotional expressions
    PHRASE_PATTERNS = {
        "i feel like": "emotional_expression",
        "i got defensive": "defensive_behavior",
        "i shut down": "shutdown_behavior",
        "i panicked": "panic_behavior",
        "i keep thinking": "rumination",
        "keep replaying": "rumination",
        "can't stop thinking": "rumination",
        "i tried to": "effort",
        "i don't understand why": "confusion",
        "why would they": "confusion",
        "i feel so": "emotional_intensity",
        "so overwhelmed": "overwhelm",
        "feel guilty": "guilt",
        "feel ashamed": "shame",
        "feel embarrassed": "embarrassment",
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
        
        # Compile phrase patterns as well
        self.phrase_patterns = {}
        for phrase, category in self.PHRASE_PATTERNS.items():
            self.phrase_patterns[phrase] = re.compile(re.escape(phrase), re.IGNORECASE)
    
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
        
        # Count keyword matches for each feature
        social_rejection_count = len(self.social_rejection_pattern.findall(text_lower))
        self_blame_count = len(self.self_blame_pattern.findall(text_lower))
        other_blame_count = len(self.other_blame_pattern.findall(text_lower))
        empathy_count = len(self.empathy_pattern.findall(text_lower))
        rationalization_count = len(self.rationalization_pattern.findall(text_lower))
        identity_threat_count = len(self.identity_threat_pattern.findall(text_lower))
        loss_count = len(self.loss_pattern.findall(text_lower))
        
        # Also count phrase pattern matches
        phrase_match_counts = {category: 0 for category in set(self.PHRASE_PATTERNS.values())}
        for phrase, pattern in self.phrase_patterns.items():
            phrase_matches = len(pattern.findall(text_lower))
            category = self.PHRASE_PATTERNS[phrase]
            phrase_match_counts[category] += phrase_matches
        
        # Add phrase matches to relevant feature counts
        if phrase_match_counts.get("panic_behavior", 0) > 0 or \
           phrase_match_counts.get("defensive_behavior", 0) > 0 or \
           phrase_match_counts.get("shutdown_behavior", 0) > 0:
            identity_threat_count += phrase_match_counts.get("panic_behavior", 0)
        
        if phrase_match_counts.get("rumination", 0) > 0:
            identity_threat_count += phrase_match_counts.get("rumination", 0) * 0.5
        
        # Enhanced scoring: use log-based scaling to better distribute values
        # This prevents compression to near-zero while staying in [0, 1]
        def scale_feature(count: float, max_threshold: float = 5.0) -> float:
            """Scale count to 0-1 range using logarithmic scaling."""
            if count == 0:
                return 0.0
            # Log scale with max threshold
            scaled = (1.0 + count) / (1.0 + max_threshold)
            return clamp_01(scaled)
        
        # Convert counts to 0-1 scale using better normalization
        social_rejection = scale_feature(social_rejection_count)
        self_blame = scale_feature(self_blame_count)
        other_blame = scale_feature(other_blame_count)
        empathy_for_other = scale_feature(empathy_count)
        rationalization = scale_feature(rationalization_count)
        threat_to_identity = scale_feature(identity_threat_count)
        loss_of_reward = scale_feature(loss_count)
        
        # Ensure at least some features are non-zero if any emotion detected
        total_count = (social_rejection_count + self_blame_count + other_blame_count + 
                      empathy_count + rationalization_count + identity_threat_count + loss_count)
        
        if total_count > 0:
            # Amplify features slightly to escape the "all near zero" problem
            amplify = clamp_01(1.0 + (total_count * 0.05))  # Slightly boost if many features detected
            social_rejection = clamp_01(social_rejection * amplify)
            self_blame = clamp_01(self_blame * amplify)
            other_blame = clamp_01(other_blame * amplify)
            empathy_for_other = clamp_01(empathy_for_other * amplify)
            rationalization = clamp_01(rationalization * amplify)
            threat_to_identity = clamp_01(threat_to_identity * amplify)
            loss_of_reward = clamp_01(loss_of_reward * amplify)
        
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
