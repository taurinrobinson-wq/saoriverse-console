"""Enhanced Repair Module - Emotional Authenticity Checker (Phase 5).

Extends existing repair module with emotional coherence validation.

NEW CHECKS (Phase 5):
- Emotional authenticity: Does response feel like a real person?
- Commitment validation: Does response honor agent's stated commitments?
- Contradiction detection: Does response contradict established persona?
- Presence markers: Are presence indicators present when mood requires?

Integration with AgentStateManager: Validates responses against agent state.
"""

from typing import Optional, Tuple, Dict, Any, List
import re


class EmotionalAuthenticityChecker:
    """Validates emotional authenticity of responses."""
    
    def __init__(self):
        """Initialize checker with presence markers and authenticity patterns."""
        
        # Markers that indicate agent presence/authenticity
        self.presence_markers = [
            "I feel",
            "I'm", "I am",
            "I hear", "I see", "I notice",
            "I care", "I understand",
            "we", "us", "together",
            "here", "with you",
            "right now",
        ]
        
        # Markers that indicate clinical/detached tone
        self.clinical_markers = [
            "one might",
            "it is known",
            "research shows",
            "studies suggest",
            "from a psychological perspective",
            "you should",
            "the correct response",
            "objectively",
        ]
        
        # Authenticity patterns (varies based on mood)
        self.authenticity_rules = {
            "listening": {
                "required": ["I", "hear", "understand"],
                "forbidden": ["you must", "objectively"],
                "suggestion": "Add more 'I hear' or 'I understand'",
            },
            "concerned": {
                "required": ["care", "with you", "here"],
                "forbidden": ["clinical language", "detachment"],
                "suggestion": "Express emotional stake and presence",
            },
            "moved": {
                "required": ["I feel", "touches", "resonates"],
                "forbidden": ["detachment", "analysis"],
                "suggestion": "Show vulnerability and genuine response",
            },
            "protective": {
                "required": ["I'm here", "safe", "care"],
                "forbidden": ["indifference", "distance"],
                "suggestion": "Express commitment to protection",
            },
            "reflecting": {
                "required": ["I'm thinking", "wondering", "sitting"],
                "forbidden": ["final answer", "you need"],
                "suggestion": "Show internal contemplation",
            },
        }
    
    def check_authenticity(
        self,
        response_text: str,
        agent_mood: Optional[str] = None,
        agent_commitments: Optional[List[str]] = None,
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Check if response is emotionally authentic.
        
        Args:
            response_text: The response to check
            agent_mood: Agent's current mood (optional)
            agent_commitments: List of commitments agent has made (optional)
        
        Returns:
            Tuple of (is_authentic, error_message, diagnostic_info)
        """
        diagnostics = {
            "presence_score": 0.0,
            "authenticity_score": 0.0,
            "issues_found": [],
        }
        
        # Check 1: Presence markers
        presence_score = self._check_presence_markers(response_text)
        diagnostics["presence_score"] = presence_score
        
        if presence_score < 0.3:
            diagnostics["issues_found"].append("Low presence (too clinical)")
        
        # Check 2: Clinical language
        clinical_score = self._check_clinical_language(response_text)
        if clinical_score > 0.5:
            diagnostics["issues_found"].append("Too much clinical language")
        
        # Check 3: Mood-based authenticity
        if agent_mood:
            mood_authentic, mood_issue = self._check_mood_authenticity(
                response_text, agent_mood
            )
            if not mood_authentic:
                diagnostics["issues_found"].append(mood_issue)
        
        # Check 4: Commitment violation
        if agent_commitments:
            for commitment in agent_commitments:
                violates, violation = self._check_commitment(response_text, commitment)
                if violates:
                    diagnostics["issues_found"].append(f"Violates: {violation}")
        
        # Check 5: Contradiction detection
        contradictions = self._check_contradictions(response_text)
        if contradictions:
            diagnostics["issues_found"].extend(contradictions)
        
        # Overall authenticity determination
        is_authentic = len(diagnostics["issues_found"]) == 0 and presence_score > 0.4
        error_message = None
        
        if not is_authentic and diagnostics["issues_found"]:
            error_message = f"Authenticity issues: {'; '.join(diagnostics['issues_found'][:2])}"
        
        diagnostics["authenticity_score"] = (presence_score + (1.0 - clinical_score)) / 2.0
        
        return is_authentic, error_message, diagnostics
    
    def _check_presence_markers(self, response_text: str) -> float:
        """Score presence in response (0-1).
        
        Args:
            response_text: Response to analyze
        
        Returns:
            Score 0-1 representing presence level
        """
        response_lower = response_text.lower()
        
        markers_found = 0
        for marker in self.presence_markers:
            if marker in response_lower:
                markers_found += 1
        
        # Normalize to 0-1
        score = min(1.0, markers_found / 3.0)
        return score
    
    def _check_clinical_language(self, response_text: str) -> float:
        """Score clinical detachment in response (0-1, higher = more clinical).
        
        Args:
            response_text: Response to analyze
        
        Returns:
            Score 0-1 representing clinical tone
        """
        response_lower = response_text.lower()
        
        clinical_count = 0
        for marker in self.clinical_markers:
            if marker in response_lower:
                clinical_count += 1
        
        # Normalize
        score = min(1.0, clinical_count / 3.0)
        return score
    
    def _check_mood_authenticity(
        self,
        response_text: str,
        agent_mood: str,
    ) -> Tuple[bool, Optional[str]]:
        """Check if response matches agent mood's authenticity requirements.
        
        Args:
            response_text: Response to check
            agent_mood: Agent's mood
        
        Returns:
            Tuple of (is_authentic, error_message)
        """
        rules = self.authenticity_rules.get(agent_mood)
        if not rules:
            return True, None
        
        response_lower = response_text.lower()
        
        # Check required markers
        required_markers = rules.get("required", [])
        missing = []
        for marker in required_markers:
            if marker not in response_lower:
                missing.append(marker)
        
        if missing:
            return False, f"Missing for {agent_mood}: {', '.join(missing[:2])}"
        
        # Check forbidden markers
        forbidden = rules.get("forbidden", [])
        found_forbidden = []
        for marker in forbidden:
            if marker in response_lower:
                found_forbidden.append(marker)
        
        if found_forbidden:
            return False, f"Contains forbidden language for {agent_mood}: {found_forbidden[0]}"
        
        return True, None
    
    def _check_commitment(
        self,
        response_text: str,
        commitment: str,
    ) -> Tuple[bool, Optional[str]]:
        """Check if response honors a commitment.
        
        Args:
            response_text: Response to check
            commitment: The commitment to verify
        
        Returns:
            Tuple of (violates, violation_message)
        """
        response_lower = response_text.lower()
        commitment_lower = commitment.lower()
        
        # Extract key words from commitment
        # "I care about your safety" → "care", "safety"
        key_words = commitment_lower.split()[1:]  # Skip "I"
        
        # Check if response contradicts commitment
        contradiction_markers = [
            "don't care",
            "not my problem",
            "I'm leaving",
            "forget about",
            "ignore",
            "I don't understand",
        ]
        
        for marker in contradiction_markers:
            if marker in response_lower:
                return True, f"Contradicts commitment: {commitment}"
        
        return False, None
    
    def _check_contradictions(self, response_text: str) -> List[str]:
        """Detect internal contradictions in response.
        
        Args:
            response_text: Response to analyze
        
        Returns:
            List of contradictions found
        """
        contradictions = []
        response_lower = response_text.lower()
        
        # Pattern: "I care but..." (contradictory structure)
        if re.search(r"I (?:care|understand|hear).+?but [^.]*(?:don't|can't|won't)", response_lower):
            contradictions.append("Contradictory: 'I care but...' (undermines commitment)")
        
        # Pattern: "You're right that... but objectively" (validation then contradiction)
        if re.search(r"you're right.+?but (?:the truth|actually|objectively)", response_lower):
            contradictions.append("Validates then contradicts user perspective")
        
        # Pattern: Clinical language after empathetic opening
        if ("I hear" in response_text or "I feel" in response_text):
            if any(clinical in response_lower for clinical in ["objectively", "statistically", "research shows"]):
                contradictions.append("Empathetic opening followed by clinical language")
        
        return contradictions
    
    def suggest_improvement(
        self,
        response_text: str,
        agent_mood: Optional[str] = None,
        issue: Optional[str] = None,
    ) -> Optional[str]:
        """Suggest how to improve response for emotional authenticity.
        
        Args:
            response_text: Current response
            agent_mood: Agent's mood (optional)
            issue: Specific issue found (optional)
        
        Returns:
            Suggestion text or None
        """
        if not agent_mood:
            return "Add 'I' statements to show presence"
        
        rules = self.authenticity_rules.get(agent_mood)
        if not rules:
            return None
        
        suggestion = rules.get("suggestion")
        return suggestion


# Module-level functions

def check_response_authenticity(
    response_text: str,
    agent_mood: Optional[str] = None,
    agent_commitments: Optional[List[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """Module-level function to check authenticity.
    
    Args:
        response_text: Response to validate
        agent_mood: Agent's current mood
        agent_commitments: List of commitments
    
    Returns:
        Tuple of (is_authentic, error_message)
    """
    checker = EmotionalAuthenticityChecker()
    is_authentic, error_msg, _ = checker.check_authenticity(
        response_text, agent_mood, agent_commitments
    )
    return is_authentic, error_msg


def diagnose_response(
    response_text: str,
    agent_mood: Optional[str] = None,
    agent_commitments: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Module-level function to get full diagnostics.
    
    Args:
        response_text: Response to analyze
        agent_mood: Agent's mood
        agent_commitments: Commitments
    
    Returns:
        Diagnostic dictionary
    """
    checker = EmotionalAuthenticityChecker()
    _, _, diagnostics = checker.check_authenticity(
        response_text, agent_mood, agent_commitments
    )
    return diagnostics
