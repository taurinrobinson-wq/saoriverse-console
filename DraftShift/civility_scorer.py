"""
Civility Scoring Module for DraftShift - Phase 1.2

Implements weighted civility scoring algorithm for legal correspondence.
Combines tone signals, emotion analysis, and language patterns to calculate
civility scores and identify risk indicators.

Scoring Components:
- Tone baseline (formal/neutral/friendly)
- Emotion signals (anger, disgust, contempt indicators)
- Language patterns (profanity, aggression, dismissiveness)
- Sentence structure analysis
- Overall message coherence

Output: Civility score (0-100), risk level, and detailed breakdowns
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import re

logger = logging.getLogger(__name__)


class CivilityLevel(Enum):
    """Civility assessment levels."""
    EXCELLENT = 5       # 85-100: Professional, respectful
    GOOD = 4            # 70-84: Generally professional
    ADEQUATE = 3        # 55-69: Acceptable but could improve
    CONCERNING = 2      # 40-54: Unprofessional patterns detected
    PROBLEMATIC = 1     # 0-39: High risk, significant civility issues


class RiskIndicator(Enum):
    """Risk indicators for civility violations."""
    NONE = 0
    LOW = 1              # Minor issues, easily addressed
    MEDIUM = 2           # Notable concerns
    HIGH = 3             # Serious civility risks
    CRITICAL = 4         # Potential ethical violations


class CivilityScorer:
    """
    Scores legal correspondence for civility compliance.
    
    Attributes:
        tone_weights: How much each tone factor contributes to score
        emotion_weights: How much each emotion factor contributes to score
        pattern_weights: How much each language pattern contributes
    """
    
    def __init__(self):
        """Initialize civility scorer with default weights."""
        
        # Tone scoring weights (how formal/professional the language is)
        self.tone_weights = {
            'very_formal': 1.0,      # Highest civility baseline
            'formal': 0.95,
            'neutral': 0.85,
            'friendly': 0.75,
            'empathetic': 0.90,      # High civility but warmer
        }
        
        # Negative emotion indicators (deduct points)
        self.emotion_penalties = {
            'anger': 15,              # Strong penalty for anger
            'disgust': 12,            # Contempt/disgust
            'contempt': 18,           # Highest penalty for contempt
            'frustration': 8,         # Moderate frustration
            'uncertainty': 3,         # Minor penalty
        }
        
        # Language pattern penalties (deduct points)
        self.pattern_penalties = {
            'all_caps': 10,           # Aggressive emphasis
            'multiple_exclamation': 8,
            'multiple_question': 5,
            'accusatory': 12,         # "You always", "You never"
            'dismissive': 10,         # "Obviously", "clearly", "just"
            'profanity': 20,          # Major violation
            'insult': 18,             # Direct insult
            'sarcasm_heavy': 8,       # Detected sarcasm
        }
        
        # Risk pattern multipliers
        self.risk_patterns = {
            'personal_attack': 3.0,   # Multiplier for personal attacks
            'condescension': 2.5,     # Talking down to recipient
            'threat_language': 3.0,   # Threatening language
        }
    
    def score_sentence(
        self,
        sentence: str,
        detected_tone: str,
        detected_emotions: Optional[Dict[str, float]] = None,
        structure: str = "mixed"
    ) -> Dict[str, Any]:
        """
        Score a single sentence for civility.
        
        Args:
            sentence: The sentence to score
            detected_tone: Detected tone (from detect_tone)
            detected_emotions: Dict of emotion probabilities
            structure: Sentence structure type
        
        Returns:
            Dictionary with:
                - score: Civility score (0-100)
                - level: CivilityLevel enum
                - tone_score: Component scores
                - emotion_penalties: Detected emotion issues
                - pattern_penalties: Detected pattern issues
                - risk_flags: Any risk indicators detected
        """
        
        base_score = 100.0
        tone_score = 0.0
        emotion_deductions = 0.0
        pattern_deductions = 0.0
        risk_flags = []
        
        # 1. Tone baseline (30% of score)
        tone_lower = detected_tone.lower() if detected_tone else "neutral"
        tone_weight = self.tone_weights.get(tone_lower, 0.85)
        tone_score = tone_weight * 30  # 30 points possible from tone
        
        # 2. Emotion analysis (40% of score)
        if detected_emotions:
            for emotion, probability in detected_emotions.items():
                if emotion in self.emotion_penalties:
                    penalty = self.emotion_penalties[emotion] * (probability / 100.0)
                    emotion_deductions += penalty
                    if probability > 60:
                        risk_flags.append(f"High {emotion} (p={probability:.0f}%)")
        
        # Cap emotion deductions at 40 points
        emotion_deductions = min(emotion_deductions, 40.0)
        
        # 3. Language pattern analysis (30% of score)
        pattern_deductions = self._analyze_patterns(sentence, risk_flags)
        pattern_deductions = min(pattern_deductions, 30.0)
        
        # Calculate final score
        final_score = tone_score + (40 - emotion_deductions) + (30 - pattern_deductions)
        final_score = max(0, min(100, final_score))  # Clamp 0-100
        
        # Determine civility level
        civility_level = self._score_to_level(final_score)
        
        return {
            'sentence': sentence,
            'score': round(final_score, 1),
            'level': civility_level,
            'component_scores': {
                'tone': round(tone_score, 1),
                'emotions': round(40 - emotion_deductions, 1),
                'patterns': round(30 - pattern_deductions, 1),
            },
            'deductions': {
                'emotions': round(emotion_deductions, 1),
                'patterns': round(pattern_deductions, 1),
            },
            'risk_flags': risk_flags,
            'tone_detected': detected_tone,
        }
    
    def _analyze_patterns(self, sentence: str, risk_flags: List[str]) -> float:
        """
        Analyze language patterns and return deduction points.
        
        Args:
            sentence: Sentence to analyze
            risk_flags: List to append risk flags to
        
        Returns:
            Deduction points (0-30)
        """
        deductions = 0.0
        sentence_lower = sentence.lower()
        
        # ALL CAPS sections (aggressive emphasis)
        if re.search(r'\b[A-Z]{4,}\b', sentence):
            deductions += self.pattern_penalties['all_caps']
            risk_flags.append("ALL CAPS emphasis detected")
        
        # Multiple exclamation marks (emotional intensity)
        if sentence.count('!') >= 2:
            deductions += self.pattern_penalties['multiple_exclamation']
            risk_flags.append(f"Multiple exclamation marks ({sentence.count('!')})")
        
        # Multiple question marks (rhetorical hostility)
        if sentence.count('?') >= 3:
            deductions += self.pattern_penalties['multiple_question']
            risk_flags.append(f"Multiple question marks ({sentence.count('?')})")
        
        # Accusatory language patterns
        accusatory_patterns = [
            r'\byou always\b',
            r'\byou never\b',
            r'\byou should have\b',
            r'\byou obviously\b',
            r'\byou fail',
        ]
        if any(re.search(pattern, sentence_lower) for pattern in accusatory_patterns):
            deductions += self.pattern_penalties['accusatory']
            risk_flags.append("Accusatory language detected")
        
        # Dismissive language
        dismissive_words = [
            'obviously', 'clearly', 'just', 'simply', 'merely',
            'nonsensical', 'absurd', 'ridiculous', 'pathetic'
        ]
        if any(f' {word} ' in sentence_lower or f' {word},' in sentence_lower 
               for word in dismissive_words):
            deductions += self.pattern_penalties['dismissive']
            risk_flags.append("Dismissive language detected")
        
        # Profanity check (basic)
        profanity_patterns = [
            r'\b(damn|hell|crap)\b',  # Mild
            r'\b(ass|bastard)\b',     # Moderate
        ]
        if any(re.search(pattern, sentence_lower) for pattern in profanity_patterns):
            deductions += self.pattern_penalties['profanity']
            risk_flags.append("Profanity or vulgar language detected")
        
        # Insult detection (basic)
        insult_keywords = [
            'stupid', 'idiotic', 'moronic', 'incompetent', 'incompetence',
            'fraud', 'dishonest', 'liar', 'lying', 'malicious'
        ]
        if any(keyword in sentence_lower for keyword in insult_keywords):
            deductions += self.pattern_penalties['insult']
            risk_flags.append("Insult or derogatory language detected")
        
        # Sarcasm detection (basic - look for common patterns)
        if '"' in sentence or "'" in sentence:
            # Could be sarcasm
            if any(word in sentence_lower for word in ['sure', 'right', 'yeah right', 'of course']):
                deductions += self.pattern_penalties['sarcasm_heavy']
                risk_flags.append("Potential sarcasm detected")
        
        # Threat language patterns
        threat_patterns = [
            r'\bwill have to sue\b',
            r'\bi will report you\b',
            r'\bi will pursue\b',
            r'\byou will regret\b',
            r'\bthreaten',
        ]
        if any(re.search(pattern, sentence_lower) for pattern in threat_patterns):
            deductions += 15  # High deduction for threat language
            risk_flags.append("Potential threat language detected")
        
        # Condescending patterns
        condescending_phrases = [
            r'\blet me explain\b',
            r'\bi understand your concern, but\b',
            r'\bas you probably know\b',
            r'\byou seem to think\b',
            r'\byou apparently\b',
        ]
        if any(re.search(phrase, sentence_lower) for phrase in condescending_phrases):
            deductions += 12
            risk_flags.append("Potentially condescending language detected")
        
        return deductions
    
    def score_document(
        self,
        sentences: List[str],
        tones: List[str],
        emotions_list: Optional[List[Dict[str, float]]] = None,
        structures: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Score an entire document/message.
        
        Args:
            sentences: List of sentences
            tones: List of detected tones
            emotions_list: List of emotion dictionaries
            structures: List of sentence structures
        
        Returns:
            Document-level civility assessment
        """
        
        if not sentences:
            return {
                'score': 100.0,
                'level': CivilityLevel.EXCELLENT,
                'sentence_count': 0,
                'average_score': 100.0,
                'risk_level': RiskIndicator.NONE,
                'all_risk_flags': [],
            }
        
        # Default to empty lists if not provided
        if emotions_list is None:
            emotions_list = [None] * len(sentences)
        if structures is None:
            structures = ['mixed'] * len(sentences)
        
        # Score each sentence
        sentence_scores = []
        all_risk_flags = []
        min_score = 100.0
        max_score = 0.0
        
        for i, sentence in enumerate(sentences):
            score_result = self.score_sentence(
                sentence,
                tones[i] if i < len(tones) else 'neutral',
                emotions_list[i] if i < len(emotions_list) else None,
                structures[i] if i < len(structures) else 'mixed'
            )
            sentence_scores.append(score_result)
            all_risk_flags.extend(score_result['risk_flags'])
            min_score = min(min_score, score_result['score'])
            max_score = max(max_score, score_result['score'])
        
        # Calculate document-level statistics
        average_score = sum(s['score'] for s in sentence_scores) / len(sentence_scores)
        document_level = self._score_to_level(average_score)
        
        # Determine risk level
        risk_level = self._calculate_risk_level(average_score, all_risk_flags)
        
        return {
            'score': round(average_score, 1),
            'level': document_level,
            'sentence_count': len(sentences),
            'sentence_scores': sentence_scores,
            'statistics': {
                'average': round(average_score, 1),
                'minimum': round(min_score, 1),
                'maximum': round(max_score, 1),
                'range': round(max_score - min_score, 1),
            },
            'risk_level': risk_level,
            'all_risk_flags': list(set(all_risk_flags)),  # Deduplicate
            'recommendations': self._generate_recommendations(average_score, all_risk_flags),
        }
    
    def _score_to_level(self, score: float) -> CivilityLevel:
        """Convert numerical score to civility level."""
        if score >= 85:
            return CivilityLevel.EXCELLENT
        elif score >= 70:
            return CivilityLevel.GOOD
        elif score >= 55:
            return CivilityLevel.ADEQUATE
        elif score >= 40:
            return CivilityLevel.CONCERNING
        else:
            return CivilityLevel.PROBLEMATIC
    
    def _calculate_risk_level(
        self,
        score: float,
        risk_flags: List[str]
    ) -> RiskIndicator:
        """
        Calculate overall risk level based on score and flags.
        
        Args:
            score: Average civility score
            risk_flags: List of detected risk indicators
        
        Returns:
            RiskIndicator enum
        """
        
        # Extremely low scores = critical risk
        if score < 30:
            return RiskIndicator.CRITICAL
        
        # Check for critical keywords in flags
        critical_keywords = ['threat', 'profanity', 'insult', 'personal attack']
        if any(keyword in ' '.join(risk_flags).lower() for keyword in critical_keywords):
            return RiskIndicator.HIGH
        
        # Medium risk
        if score < 55:
            return RiskIndicator.HIGH
        if score < 70 and len(risk_flags) >= 2:
            return RiskIndicator.MEDIUM
        if score < 70:
            return RiskIndicator.LOW
        
        # Good score = none or low risk
        if len(risk_flags) >= 2:
            return RiskIndicator.LOW
        
        return RiskIndicator.NONE
    
    def _generate_recommendations(
        self,
        score: float,
        risk_flags: List[str]
    ) -> List[str]:
        """
        Generate recommendations based on score and flags.
        
        Args:
            score: Civility score
            risk_flags: Detected risk indicators
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        if score >= 85:
            recommendations.append("✅ Excellent civility. Message is professional and respectful.")
        
        elif score >= 70:
            recommendations.append("✅ Good civility. Consider minor adjustments if flagged items exist.")
        
        elif score >= 55:
            recommendations.append("⚠️ Adequate civility. Consider toning down emotional language.")
            if 'anger' in ' '.join(risk_flags).lower():
                recommendations.append("   - Reduce anger indicators; use calmer language")
            if 'accusatory' in ' '.join(risk_flags):
                recommendations.append("   - Avoid accusatory 'you always/never' patterns")
        
        elif score >= 40:
            recommendations.append("⚠️ Concerning civility patterns detected. Significant revision recommended.")
            recommendations.append("   - Review all flagged items below")
            recommendations.append("   - Adopt more formal, neutral tone")
        
        else:
            recommendations.append("🚨 CRITICAL: Multiple civility violations detected.")
            recommendations.append("   - Do NOT send without substantial revision")
            recommendations.append("   - Remove offensive/accusatory language")
            recommendations.append("   - Restructure with professional, objective tone")
            recommendations.append("   - Consider consulting with ethics advisor")
        
        return recommendations


# Module-level scoring function
_scorer_instance: Optional[CivilityScorer] = None


def get_scorer() -> CivilityScorer:
    """Get or create civility scorer singleton."""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = CivilityScorer()
    return _scorer_instance


def score_document(
    sentences: List[str],
    tones: List[str],
    emotions_list: Optional[List[Dict[str, float]]] = None,
    structures: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to score document.
    
    Args:
        sentences: List of sentences
        tones: List of detected tones
        emotions_list: List of emotion probabilities
        structures: List of sentence structures
    
    Returns:
        Document civility assessment
    """
    scorer = get_scorer()
    return scorer.score_document(sentences, tones, emotions_list, structures)
