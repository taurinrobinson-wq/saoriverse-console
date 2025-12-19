"""
Risk Alerts Module for DraftShift - Phase 1.3

Generates real-time alerts for civility compliance risks in legal correspondence.
Patterns detected include:
- Emotional escalation (anger, contempt, frustration)
- Aggressive language patterns (accusations, threats, insults)
- Professional boundary violations
- Rule 9.7 civility mandate violations

Alert System:
- CRITICAL: Immediate action required (ethical violations)
- HIGH: Substantial issues (unprofessional language)
- MEDIUM: Concerns (needs revision)
- LOW: Minor issues (polish only)
"""

import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = 0       # Informational only
    LOW = 1        # Minor issue, polish needed
    MEDIUM = 2     # Moderate concern, revision recommended
    HIGH = 3       # Significant issue, substantial revision needed
    CRITICAL = 4   # Severe violation, do not send


class AlertCategory(Enum):
    """Categories of civility alerts."""
    EMOTION = "emotional_escalation"
    LANGUAGE = "aggressive_language"
    ACCUSATION = "accusatory_pattern"
    THREAT = "threat_language"
    PROFESSIONAL = "professional_boundary"
    ETHICS = "ethics_violation"
    TONE = "tone_mismatch"


@dataclass
class Alert:
    """Represents a single civility alert."""
    
    severity: AlertSeverity
    category: AlertCategory
    message: str
    snippet: Optional[str] = None  # Offending text snippet
    line_number: Optional[int] = None
    suggestion: Optional[str] = None  # Recommended fix
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'severity': self.severity.name,
            'category': self.category.value,
            'message': self.message,
            'snippet': self.snippet,
            'line_number': self.line_number,
            'suggestion': self.suggestion,
        }


class RiskAlertGenerator:
    """
    Generates alerts for civility risks in legal correspondence.
    
    Attributes:
        pattern_matchers: Compiled regex patterns for various violations
        emotion_triggers: Words/phrases that indicate emotional escalation
        accusation_patterns: Patterns indicating accusations
    """
    
    def __init__(self):
        """Initialize alert generator with patterns and triggers."""
        
        # Emotional escalation indicators
        self.emotion_triggers = {
            'anger': {
                'keywords': ['angry', 'furious', 'enraged', 'outraged', 'furious'],
                'punctuation': ['!!!', '???'],
                'caps_minimum': 4,  # 4+ words in all caps
                'severity': AlertSeverity.HIGH,
                'category': AlertCategory.EMOTION,
            },
            'contempt': {
                'keywords': ['contempt', 'despise', 'loathe', 'abhor', 'pathetic', 'ridiculous'],
                'severity': AlertSeverity.CRITICAL,
                'category': AlertCategory.EMOTION,
            },
            'frustration': {
                'keywords': ['frustrated', 'frustrated', 'exasperated', 'fed up', 'sick of'],
                'severity': AlertSeverity.MEDIUM,
                'category': AlertCategory.EMOTION,
            },
        }
        
        # Accusatory patterns
        self.accusation_patterns = {
            'always_never': r'\b(you always|you never|you constantly)\b',
            'failure': r'\b(you failed|you failed to|you fail to)\b',
            'dishonesty': r'\b(you lied|you\'re lying|you deceived)\b',
            'incompetence': r'\b(you can\'t|you\'re incapable|you don\'t understand)\b',
        }
        
        # Threat language patterns
        self.threat_patterns = {
            'legal_threat': r'\b(will sue|will report|will pursue legal|i\'ll sue|complaint to bar)\b',
            'personal_threat': r'\b(you will regret|i\'ll remember this|don\'t forget)\b',
            'implicit_threat': r'\b(you better|you should be careful|consequences)\b',
        }
        
        # Professional boundary violations
        self.boundary_violations = {
            'personal_attack': r'\b(you\'re|you are)\s+(stupid|idiotic|incompetent|fraud)',
            'character_attack': r'\b(dishonest|untrustworthy|malicious|corrupt)\b',
            'discrimination': r'\b(because|due to)\s+(race|gender|age|religion|ethnicity)\b',
        }
        
        # Rule 9.7 civility mandate violations
        self.civility_violations = {
            'disrespect': r'\b(disrespect|disrespectful|dismiss|dismissive)\b',
            'condescension': r'\b(obviously|clearly|just|simply|merely)\s+(you|the)',
            'sarcasm_hostile': r'[\"\'].*?[\"\'].*?(sure|right|of course)',
        }
    
    def scan_sentence(
        self,
        sentence: str,
        sentence_number: int = 1,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Alert]:
        """
        Scan a single sentence for civility risks.
        
        Args:
            sentence: Sentence to scan
            sentence_number: Line/sentence number for reference
            context: Optional context (detected tone, emotions, etc)
        
        Returns:
            List of Alert objects
        """
        alerts = []
        sentence_lower = sentence.lower()
        
        # 1. Check for emotional escalation
        emotion_alerts = self._check_emotions(sentence, sentence_number)
        alerts.extend(emotion_alerts)
        
        # 2. Check for accusatory patterns
        accusation_alerts = self._check_accusations(sentence, sentence_number)
        alerts.extend(accusation_alerts)
        
        # 3. Check for threat language
        threat_alerts = self._check_threats(sentence, sentence_number)
        alerts.extend(threat_alerts)
        
        # 4. Check for professional boundary violations
        boundary_alerts = self._check_boundary_violations(sentence, sentence_number)
        alerts.extend(boundary_alerts)
        
        # 5. Check for tone/civility violations
        civility_alerts = self._check_civility_violations(sentence, sentence_number)
        alerts.extend(civility_alerts)
        
        return alerts
    
    def _check_emotions(self, sentence: str, line_num: int) -> List[Alert]:
        """Check for emotional escalation indicators."""
        alerts = []
        sentence_lower = sentence.lower()
        
        # Anger indicators
        if any(kw in sentence_lower for kw in self.emotion_triggers['anger']['keywords']):
            alerts.append(Alert(
                severity=AlertSeverity.HIGH,
                category=AlertCategory.EMOTION,
                message="Anger language detected. Professional tone needed.",
                snippet=sentence[:80],
                line_number=line_num,
                suggestion="Replace emotionally charged words with neutral, professional language."
            ))
        
        # Excessive punctuation
        if '!!!' in sentence or '???' in sentence:
            alerts.append(Alert(
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.EMOTION,
                message="Excessive punctuation indicates emotional intensity.",
                snippet=sentence[:80],
                line_number=line_num,
                suggestion="Use single punctuation marks; avoid emphatic repetition."
            ))
        
        # ALL CAPS emphasis
        caps_words = re.findall(r'\b[A-Z]{4,}\b', sentence)
        if len(caps_words) >= 2:
            alerts.append(Alert(
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.EMOTION,
                message=f"Multiple ALL CAPS words ({len(caps_words)}) may appear aggressive.",
                snippet=sentence[:80],
                line_number=line_num,
                suggestion="Use standard capitalization; avoid ALL CAPS for emphasis."
            ))
        
        # Contempt indicators
        if any(kw in sentence_lower for kw in self.emotion_triggers['contempt']['keywords']):
            alerts.append(Alert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.EMOTION,
                message="⚠️ CRITICAL: Contempt language violates civility standards.",
                snippet=sentence[:80],
                line_number=line_num,
                suggestion="Remove contemptuous language entirely. Rewrite with respect."
            ))
        
        return alerts
    
    def _check_accusations(self, sentence: str, line_num: int) -> List[Alert]:
        """Check for accusatory patterns."""
        alerts = []
        sentence_lower = sentence.lower()
        
        for pattern_name, pattern in self.accusation_patterns.items():
            if re.search(pattern, sentence_lower):
                alerts.append(Alert(
                    severity=AlertSeverity.HIGH,
                    category=AlertCategory.ACCUSATION,
                    message=f"Accusatory pattern detected: {pattern_name.replace('_', ' ')}.",
                    snippet=sentence[:80],
                    line_number=line_num,
                    suggestion=f"Reframe without accusation. Use 'In my view...' instead of 'You always...'"
                ))
        
        return alerts
    
    def _check_threats(self, sentence: str, line_num: int) -> List[Alert]:
        """Check for threat language."""
        alerts = []
        sentence_lower = sentence.lower()
        
        for threat_type, pattern in self.threat_patterns.items():
            if re.search(pattern, sentence_lower):
                severity = AlertSeverity.CRITICAL if 'legal' in threat_type or 'personal' in threat_type else AlertSeverity.HIGH
                alerts.append(Alert(
                    severity=severity,
                    category=AlertCategory.THREAT,
                    message=f"⚠️ Potential threat language detected.",
                    snippet=sentence[:80],
                    line_number=line_num,
                    suggestion="Remove threatening language. If action is necessary, phrase factually."
                ))
        
        return alerts
    
    def _check_boundary_violations(self, sentence: str, line_num: int) -> List[Alert]:
        """Check for professional boundary violations."""
        alerts = []
        sentence_lower = sentence.lower()
        
        for violation_type, pattern in self.boundary_violations.items():
            if re.search(pattern, sentence_lower):
                alerts.append(Alert(
                    severity=AlertSeverity.CRITICAL,
                    category=AlertCategory.PROFESSIONAL,
                    message=f"⚠️ CRITICAL: Professional boundary violation ({violation_type}).",
                    snippet=sentence[:80],
                    line_number=line_num,
                    suggestion="Remove personal/discriminatory attacks. Focus on professional issues only."
                ))
        
        return alerts
    
    def _check_civility_violations(self, sentence: str, line_num: int) -> List[Alert]:
        """Check for Rule 9.7 civility mandate violations."""
        alerts = []
        sentence_lower = sentence.lower()
        
        for violation_type, pattern in self.civility_violations.items():
            if re.search(pattern, sentence_lower):
                alerts.append(Alert(
                    severity=AlertSeverity.MEDIUM,
                    category=AlertCategory.ETHICS,
                    message=f"Potential civility concern: {violation_type.replace('_', ' ')}.",
                    snippet=sentence[:80],
                    line_number=line_num,
                    suggestion="Revise for respectful, professional tone."
                ))
        
        return alerts
    
    def scan_document(
        self,
        sentences: List[str],
        tones: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Scan entire document for civility risks.
        
        Args:
            sentences: List of sentences
            tones: Optional list of detected tones
        
        Returns:
            Comprehensive alert report
        """
        
        all_alerts = []
        alerts_by_severity = {
            AlertSeverity.CRITICAL: [],
            AlertSeverity.HIGH: [],
            AlertSeverity.MEDIUM: [],
            AlertSeverity.LOW: [],
            AlertSeverity.INFO: [],
        }
        
        # Scan each sentence
        for i, sentence in enumerate(sentences):
            sentence_alerts = self.scan_sentence(
                sentence,
                sentence_number=i + 1,
                context={'tone': tones[i] if tones and i < len(tones) else None}
            )
            all_alerts.extend(sentence_alerts)
            
            for alert in sentence_alerts:
                alerts_by_severity[alert.severity].append(alert)
        
        # Determine document-level risk assessment
        has_critical = len(alerts_by_severity[AlertSeverity.CRITICAL]) > 0
        has_high = len(alerts_by_severity[AlertSeverity.HIGH]) > 0
        
        if has_critical:
            overall_recommendation = "🚨 DO NOT SEND - Critical civility violations detected. Require substantial revision."
            sendable = False
        elif has_high:
            overall_recommendation = "⚠️ HIGH RISK - Significant civility issues. Recommend substantial revision before sending."
            sendable = False
        elif len(alerts_by_severity[AlertSeverity.MEDIUM]) > 2:
            overall_recommendation = "⚠️ MODERATE CONCERN - Several issues detected. Consider revising before sending."
            sendable = True  # Can send with caution
        elif len(all_alerts) > 0:
            overall_recommendation = "✅ Generally acceptable - Minor issues flagged. Polish recommended."
            sendable = True
        else:
            overall_recommendation = "✅ EXCELLENT - No civility concerns detected."
            sendable = True
        
        return {
            'alerts_total': len(all_alerts),
            'alerts_by_severity': {
                'critical': [a.to_dict() for a in alerts_by_severity[AlertSeverity.CRITICAL]],
                'high': [a.to_dict() for a in alerts_by_severity[AlertSeverity.HIGH]],
                'medium': [a.to_dict() for a in alerts_by_severity[AlertSeverity.MEDIUM]],
                'low': [a.to_dict() for a in alerts_by_severity[AlertSeverity.LOW]],
                'info': [a.to_dict() for a in alerts_by_severity[AlertSeverity.INFO]],
            },
            'all_alerts': [a.to_dict() for a in all_alerts],
            'overall_recommendation': overall_recommendation,
            'sendable': sendable,
            'critical_count': len(alerts_by_severity[AlertSeverity.CRITICAL]),
            'high_count': len(alerts_by_severity[AlertSeverity.HIGH]),
        }


# Module-level alert generator
_alert_generator: Optional[RiskAlertGenerator] = None


def get_alert_generator() -> RiskAlertGenerator:
    """Get or create alert generator singleton."""
    global _alert_generator
    if _alert_generator is None:
        _alert_generator = RiskAlertGenerator()
    return _alert_generator


def scan_document(sentences: List[str], tones: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function to scan document for alerts.
    
    Args:
        sentences: List of sentences
        tones: Optional list of detected tones
    
    Returns:
        Alert report dictionary
    """
    generator = get_alert_generator()
    return generator.scan_document(sentences, tones)
