"""Policy router for FirstPerson pipeline.

Enforces invariants:
- Turn-type routing (which generator is allowed)
- Response length constraints
- Verbatim echo prevention
- Domain reference requirements
- Affect consistency
"""

from typing import List, Optional


class PolicyRouter:
    """Route responses and enforce pipeline invariants."""

    # Map turn types to allowed generators
    TURN_TYPE_ROUTING = {
        "closure": ["template_composer"],
        "gratitude": ["template_composer"],
        "disclosure": ["compressor", "orchestrator"],
        "meta": ["orchestrator"],
        "correction": ["compressor"],
    }

    # Sentence limits per turn type
    SENTENCE_LIMITS = {
        "closure": 2,
        "gratitude": 2,
        "disclosure": 4,
        "meta": 3,
        "correction": 3,
    }

    def route(
        self,
        turn_type: str,
        base_response: str,
        domains: Optional[dict] = None,
        conversation_history: Optional[List[dict]] = None,
        user_message: Optional[str] = None,
        affect: Optional[dict] = None,
    ) -> dict:
        """Route and validate response against policy invariants.

        Args:
            turn_type: From TurnClassifier ("disclosure", "gratitude", etc.).
            base_response: Candidate response text.
            domains: From DomainExtractor {exhaustion, stress, blocked_joy, ...}.
            conversation_history: Prior [{role, content}, ...].
            user_message: Original user message.
            affect: {tone, valence, arousal} from pipeline.

        Returns:
            {
                "allowed_generators": List[str],
                "invariants_pass": bool,
                "violations": List[str],
                "recommended_generator": str,
                "advice": str,  # optional suggestion
            }
        """
        violations = []
        domains = domains or {}
        conversation_history = conversation_history or []
        user_message = user_message or ""
        affect = affect or {}

        # 1. Check turn-type routing
        allowed_generators = self.TURN_TYPE_ROUTING.get(turn_type, ["compressor"])

        # 2. Check response length
        sentence_limit = self.SENTENCE_LIMITS.get(turn_type, 3)
        sentence_count = self._count_sentences(base_response)
        if sentence_count > sentence_limit:
            violations.append(
                f"response has {sentence_count} sentences, limit is {sentence_limit}"
            )

        # 3. Check verbatim echo
        if self._has_verbatim_echo(base_response, user_message):
            violations.append("response contains >3 consecutive words from user message")

        # 4. Check domain reference (if any domain > 0.6)
        high_domains = [k for k, v in domains.items() if v > 0.6]
        if high_domains:
            referenced = self._count_referenced_domains(base_response, high_domains)
            if referenced == 0:
                violations.append(
                    f"high-scoring domains {high_domains} not referenced in response"
                )

        # 5. Check affect consistency
        valence = affect.get("valence", 0.0)
        tone = affect.get("tone", "neutral").lower()

        # If user is negative, response shouldn't be celebratory
        if valence < 0.4 and tone not in ["neutral", "sad", "tired"]:
            if any(
                word in base_response.lower()
                for word in ["amazing", "wonderful", "fantastic", "incredible"]
            ):
                violations.append(
                    "response is celebratory for negative-valence turn (tone mismatch)"
                )

        # Determine pass/fail
        invariants_pass = len(violations) == 0

        # Recommend generator
        recommended_generator = allowed_generators[0] if allowed_generators else "compressor"

        # Build advice
        advice = ""
        if not invariants_pass:
            advice = f"Fix violations: {'; '.join(violations)}"
        else:
            advice = f"Response passes all invariants. Use {recommended_generator}."

        return {
            "allowed_generators": allowed_generators,
            "invariants_pass": invariants_pass,
            "violations": violations,
            "recommended_generator": recommended_generator,
            "advice": advice,
        }

    def _count_sentences(self, text: str) -> int:
        """Count sentences (approximate)."""
        import re

        # Split on . ! ? followed by space or end
        sentences = re.split(r'[.!?]+\s+|\n+', text.strip())
        return len([s for s in sentences if s.strip()])

    def _has_verbatim_echo(self, response: str, user_message: str) -> bool:
        """Check if response contains >3 consecutive words from user message."""
        if not user_message:
            return False

        user_words = user_message.lower().split()
        response_words = response.lower().split()

        # Look for >3 consecutive words
        for i in range(len(response_words) - 3):
            window = " ".join(response_words[i : i + 4])
            user_text = " ".join(user_words)
            if window in user_text:
                return True

        return False

    def _count_referenced_domains(self, response: str, domains: List[str]) -> int:
        """Count how many domains are referenced in response."""
        response_lower = response.lower()
        count = 0

        # Map domains to reference keywords
        domain_keywords = {
            "exhaustion": ["exhausted", "tired", "weary", "drained", "weight"],
            "stress": ["stress", "pressure", "overwhelmed"],
            "blocked_joy": ["blocked", "can't feel", "joy", "happiness"],
            "contrast": ["contrast", "different", "out of sync"],
            "temporal_pressure": ["time", "rushing", "deadline", "soon"],
            "disappointment": ["disappointed", "let down", "expected"],
            "isolation": ["alone", "lonely", "isolated"],
        }

        for domain in domains:
            keywords = domain_keywords.get(domain, [domain])
            if any(kw in response_lower for kw in keywords):
                count += 1

        return count
