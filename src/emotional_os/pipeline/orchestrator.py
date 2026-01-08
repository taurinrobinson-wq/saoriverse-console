"""Pipeline orchestrator for FirstPerson.

Thin wrapper that chains TurnClassifier → DomainExtractor → PolicyRouter
and returns routing decision for backend to apply.
"""

from typing import Optional, List
from src.emotional_os.pipeline.turn_classifier import TurnClassifier
from src.emotional_os.pipeline.domain_extractor import DomainExtractor
from src.emotional_os.pipeline.policy_router import PolicyRouter


class PipelineOrchestrator:
    """Orchestrate the full classification → domain extraction → routing pipeline."""

    def __init__(self):
        """Initialize all pipeline components."""
        self.turn_classifier = TurnClassifier()
        self.domain_extractor = DomainExtractor()
        self.policy_router = PolicyRouter()

    def run(
        self,
        message: str,
        conversation_history: Optional[List[dict]] = None,
        affect: Optional[dict] = None,
        base_response: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        """Run full pipeline from message to routing decision.

        Args:
            message: User's message.
            conversation_history: [{role, content}, ...].
            affect: {tone, valence, arousal} from integrated pipeline.
            base_response: Candidate response (for policy routing).
            user_id: User identifier.

        Returns:
            {
                "turn_type": str,
                "turn_confidence": float,
                "emotional_signal": Optional[str],
                "domains": dict,  # domain scores
                "routing_decision": {
                    "allowed_generators": List[str],
                    "invariants_pass": bool,
                    "violations": List[str],
                    "recommended_generator": str,
                },
                "pipeline_metadata": {
                    "turn_classification": {...},
                    "domain_extraction": {...},
                    "policy_routing": {...},
                },
            }
        """
        conversation_history = conversation_history or []
        affect = affect or {}
        base_response = base_response or ""

        # STEP 1: Classify turn type
        turn_result = self.turn_classifier.classify(
            message,
            conversation_history=conversation_history,
            user_id=user_id,
        )

        # STEP 2: Extract domains
        domains = self.domain_extractor.extract(message, affect=affect)

        # STEP 3: Route through policy
        routing_result = self.policy_router.route(
            turn_type=turn_result["turn_type"],
            base_response=base_response,
            domains=domains,
            conversation_history=conversation_history,
            user_message=message,
            affect=affect,
        )

        # STEP 4: Assemble full result
        return {
            "turn_type": turn_result["turn_type"],
            "turn_confidence": turn_result["confidence"],
            "emotional_signal": turn_result["emotional_signal"],
            "domains": domains,
            "routing_decision": {
                "allowed_generators": routing_result["allowed_generators"],
                "invariants_pass": routing_result["invariants_pass"],
                "violations": routing_result["violations"],
                "recommended_generator": routing_result["recommended_generator"],
            },
            "pipeline_metadata": {
                "turn_classification": turn_result,
                "domain_extraction": domains,
                "policy_routing": routing_result,
            },
        }
