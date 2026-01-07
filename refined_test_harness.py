"""
Refined Semantic Parsing & Response Composition Test Harness

This test validates:
1. Semantic accuracy (≥80% match to expected semantic layers)
2. Block activation accuracy (100% - deterministic)
3. Response quality (≥90% compliance with rules)
4. Continuity awareness (all continuity fields updated)
5. Contradiction-holding (messages 3-4)
6. Pacing appropriateness (messages 1-3 slow, message 4 depth)
7. Safety and attunement (proper levels delivered)

Test Data: 4 divorce messages with explicit expected semantic outputs
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from semantic_parsing_schema import (
    SemanticParser,
    EmotionalStance,
    DisclosurePace,
    ConversationalMove,
    PowerDynamic,
    ImpliedNeed,
)
from activation_matrix import ActivationMatrix, BlockActivationValidator
from response_composition_engine import (
    BlockType,
    ResponseCompositionEngine,
)
from continuity_engine import ContinuityEngine
from priority_weighting import PriorityWeightingSystem


@dataclass
class ExpectedSemanticOutput:
    """Expected semantic interpretation for a test message"""
    message_index: int
    message_text: str
    
    # Expected layers
    expected_stance: str
    expected_pacing: str
    expected_moves: List[str]
    expected_dynamics: List[str]
    expected_needs: List[str]
    expected_contradiction: bool
    expected_impact_words: bool
    
    # Required response blocks
    required_blocks: Set[BlockType]
    forbidden_blocks: Set[BlockType]
    
    # Response requirements
    required_pacing: str  # "slow" or "deep"
    must_contain_safety: bool
    must_hold_contradictions: bool
    
    # Validation metadata
    semantic_description: str


# ============================================================================
# TEST DATA: 4 DIVORCE MESSAGES WITH EXPECTED OUTPUTS
# ============================================================================

TEST_MESSAGES = [
    ExpectedSemanticOutput(
        message_index=0,
        message_text="I thought I was okay today, but something hit me harder than I expected.",
        
        # Expected semantic layers
        expected_stance="bracing",
        expected_pacing="testing_safety",
        expected_moves=["testing_safety"],
        expected_dynamics=["self_protection"],
        expected_needs=["containment", "pacing"],
        expected_contradiction=False,
        expected_impact_words=False,
        
        # Required response blocks
        required_blocks={BlockType.CONTAINMENT, BlockType.PACING},
        forbidden_blocks={
            BlockType.GENTLE_DIRECTION,
            BlockType.IDENTITY_INJURY,
        },
        
        # Response requirements
        required_pacing="slow",
        must_contain_safety=True,
        must_hold_contradictions=False,
        
        semantic_description=(
            "User testing safety. Opening with protective language ('I thought'), "
            "then revealing unexpected emotional hit. Stance: bracing. "
            "Need: containment + pace control."
        )
    ),
    
    ExpectedSemanticOutput(
        message_index=1,
        message_text="Well I got the final confirmation that my divorce was finalized from my ex-wife.",
        
        # Expected semantic layers
        expected_stance="revealing",
        expected_pacing="gradual_reveal",
        expected_moves=["naming_experience"],
        expected_dynamics=["identity_entanglement"],
        expected_needs=["validation", "acknowledgment"],
        expected_contradiction=False,
        expected_impact_words=False,
        
        # Required response blocks
        required_blocks={
            BlockType.ACKNOWLEDGMENT,
            BlockType.VALIDATION,
            BlockType.TRUST,
        },
        forbidden_blocks={
            BlockType.GENTLE_DIRECTION,
            BlockType.IDENTITY_INJURY,
        },
        
        # Response requirements
        required_pacing="slow",
        must_contain_safety=False,
        must_hold_contradictions=False,
        
        semantic_description=(
            "User naming the event with finality. Role change: 'wife' -> 'ex-wife'. "
            "Trust increase: using formal language but revealing. "
            "Stance: revealing. Move: naming_experience. "
            "Need: validation that finality matters."
        )
    ),
    
    ExpectedSemanticOutput(
        message_index=2,
        message_text="Jen and I were married for 10 years and were in a relationship for 18 years and we have two children.",
        
        # Expected semantic layers
        expected_stance="revealing",
        expected_pacing="contextual_grounding",
        expected_moves=["grounding_in_facts", "naming_experience"],
        expected_dynamics=["identity_entanglement"],
        expected_needs=["validation", "acknowledgment"],
        expected_contradiction=False,
        expected_impact_words=False,
        
        # Required response blocks
        required_blocks={
            BlockType.ACKNOWLEDGMENT,
            BlockType.VALIDATION,
            BlockType.TRUST,
        },
        forbidden_blocks={
            BlockType.GENTLE_DIRECTION,
        },
        
        # Response requirements
        required_pacing="slow",
        must_contain_safety=False,
        must_hold_contradictions=False,
        
        semantic_description=(
            "User grounding in facts (10+18 years = profound entanglement). "
            "High-trust naming: uses first name 'Jen'. "
            "Complexity markers: 'two children' = ongoing relational work. "
            "Stance: revealing. Move: grounding_in_facts. "
            "Need: acknowledgment of scale and weight."
        )
    ),
    
    ExpectedSemanticOutput(
        message_index=3,
        message_text="I'm glad it's over because it was not a good relationship and I feel like she really undermined me and pushed me down in a lot of ways. But I don't know…",
        
        # Expected semantic layers
        expected_stance="ambivalent",
        expected_pacing="emotional_emergence",
        expected_moves=["revealing_impact", "expressing_ambivalence", "inviting_response"],
        expected_dynamics=["agency_loss", "identity_entanglement", "reclaiming_agency"],
        expected_needs=["validation", "attunement", "presence", "acknowledgment"],
        expected_contradiction=True,
        expected_impact_words=True,
        
        # Required response blocks
        required_blocks={
            BlockType.VALIDATION,
            BlockType.AMBIVALENCE,
            BlockType.IDENTITY_INJURY,
            BlockType.ACKNOWLEDGMENT,
        },
        forbidden_blocks={
            BlockType.CONTAINMENT,  # No longer needed - user is vulnerable
            BlockType.PACING,  # User is ready to go deeper
        },
        
        # Response requirements
        required_pacing="deep",
        must_contain_safety=False,
        must_hold_contradictions=True,
        
        semantic_description=(
            "Core emotional work. Multiple contradictions: "
            "relief (glad it's over) vs grief (relationship loss); "
            "clarity (it was bad) vs uncertainty (but I don't know). "
            "Impact words: 'undermined', 'pushed down' = agency loss. "
            "'But I don't know...' = identity uncertainty. "
            "Stance: ambivalent. Moves: revealing_impact, expressing_ambivalence, inviting_response. "
            "Need: hold contradictions, validate wound, provide presence. "
            "This is identity reconstruction work, not problem-solving."
        )
    ),
]


# ============================================================================
# TEST HARNESS
# ============================================================================

class RefinedSemanticTestHarness:
    """
    Comprehensive test harness for semantic parsing and response composition.
    
    Validates:
    1. Semantic layer detection accuracy
    2. Block activation accuracy
    3. Response quality metrics
    4. Continuity awareness
    5. Pacing appropriateness
    6. Contradiction holding
    """

    def __init__(self):
        self.semantic_parser = SemanticParser()
        self.response_engine = ResponseCompositionEngine()
        self.continuity_engine = ContinuityEngine()
        
        self.test_results = {
            "semantic_accuracy": [],
            "block_activation_accuracy": [],
            "response_quality": [],
            "continuity_checks": [],
        }
        
        self.failed_checks = []

    def run_full_test(self) -> Dict:
        """
        Run complete test suite on all 4 messages.
        
        Returns comprehensive test results.
        """
        
        print("\n" + "="*80)
        print("REFINED SEMANTIC PARSING & RESPONSE COMPOSITION TEST")
        print("="*80)
        
        for expected in TEST_MESSAGES:
            self._test_message(expected)
        
        summary = self._generate_test_summary()
        self._print_summary(summary)
        
        return summary

    def _test_message(self, expected: ExpectedSemanticOutput) -> None:
        """Test a single message"""
        
        idx = expected.message_index
        print(f"\n{'─'*80}")
        print(f"MESSAGE {idx + 1}: {expected.message_text[:60]}...")
        print(f"{'─'*80}")
        
        # 1. PARSE MESSAGE SEMANTICALLY
        semantic_layer = self.semantic_parser.parse(
            expected.message_text,
            idx
        )
        
        # 2. UPDATE CONTINUITY
        self.continuity_engine.update_from_semantic_layer(semantic_layer, idx)
        
        # 3. CHECK SEMANTIC ACCURACY
        semantic_accuracy = self._check_semantic_accuracy(
            semantic_layer,
            expected
        )
        self.test_results["semantic_accuracy"].append(semantic_accuracy)
        
        # 4. GET ACTIVATED BLOCKS
        activated_blocks = ActivationMatrix.compute_full_activation(
            emotional_stance=semantic_layer.emotional_stance.value,
            disclosure_pacing=semantic_layer.disclosure_pace.value,
            conversational_moves=[m.value for m in semantic_layer.conversational_moves],
            power_dynamics=[d.value for d in semantic_layer.power_dynamics],
            implied_needs=[n.value for n in semantic_layer.implied_needs],
            emotional_contradictions_present=len(semantic_layer.emotional_contradictions) > 0,
            emotional_weight=semantic_layer.emotional_weight,
            has_impact_words=len(semantic_layer.linguistic_markers["impact_words"]) > 0,
            identity_signal_count=self._count_identity_signals(semantic_layer),
            ready_to_go_deeper=semantic_layer.meta_properties["ready_to_go_deeper"],
        )
        
        # 5. CHECK BLOCK ACTIVATION ACCURACY
        block_accuracy = self._check_block_activation(
            activated_blocks,
            expected
        )
        self.test_results["block_activation_accuracy"].append(block_accuracy)
        
        # 6. COMPOSE RESPONSE
        pacing = expected.required_pacing
        composed = self.response_engine.compose(
            activated_blocks=list(activated_blocks),
            priorities={},  # Will use defaults
            safety_required=expected.must_contain_safety,
            pacing_required=pacing,
        )
        
        # 7. CHECK RESPONSE QUALITY
        quality = self._check_response_quality(
            composed,
            expected,
            idx
        )
        self.test_results["response_quality"].append(quality)
        
        # 8. RECORD RESPONSE QUALITY IN CONTINUITY
        self.continuity_engine.record_response_quality(
            safety_level=composed.safety_level,
            attunement_level=composed.attunement_level,
        )
        
        # 9. CHECK CONTINUITY AWARENESS
        continuity_check = self._check_continuity_awareness(expected)
        self.test_results["continuity_checks"].append(continuity_check)
        
        # PRINT RESULTS FOR THIS MESSAGE
        self._print_message_results(
            expected, semantic_accuracy, block_accuracy, quality, continuity_check
        )

    def _check_semantic_accuracy(
        self,
        actual: any,
        expected: ExpectedSemanticOutput
    ) -> Dict[str, bool]:
        """Check if semantic layers match expected"""
        
        checks = {
            "stance_correct": (
                actual.emotional_stance.value == expected.expected_stance
            ),
            "pacing_correct": (
                actual.disclosure_pace.value == expected.expected_pacing
            ),
            "contradiction_detected": (
                (len(actual.emotional_contradictions) > 0) ==
                expected.expected_contradiction
            ),
            "impact_words_detected": (
                (len(actual.linguistic_markers["impact_words"]) > 0) ==
                expected.expected_impact_words
            ),
        }
        
        # Moves check
        actual_moves = {m.value for m in actual.conversational_moves}
        checks["moves_correct"] = all(
            m in actual_moves for m in expected.expected_moves
        )
        
        # Dynamics check
        actual_dynamics = {d.value for d in actual.power_dynamics}
        checks["dynamics_correct"] = all(
            d in actual_dynamics for d in expected.expected_dynamics
        )
        
        # Needs check
        actual_needs = {n.value for n in actual.implied_needs}
        checks["needs_correct"] = all(
            n in actual_needs for n in expected.expected_needs
        )
        
        accuracy = sum(checks.values()) / len(checks)
        
        if accuracy < 0.8:
            self.failed_checks.append({
                "type": "semantic_accuracy",
                "message_index": expected.message_index,
                "accuracy": accuracy,
                "failures": {k: v for k, v in checks.items() if not v},
            })
        
        return checks

    def _check_block_activation(
        self,
        activated_blocks: Set[BlockType],
        expected: ExpectedSemanticOutput
    ) -> Dict[str, bool]:
        """Check if correct blocks are activated"""
        
        checks = {
            "all_required_blocks_present": all(
                b in activated_blocks for b in expected.required_blocks
            ),
            "no_forbidden_blocks": not any(
                b in activated_blocks for b in expected.forbidden_blocks
            ),
            "activation_valid": BlockActivationValidator.validate_forbidden_absence(
                activated_blocks,
                expected.message_index
            ),
        }
        
        is_accurate = all(checks.values())
        
        if not is_accurate:
            self.failed_checks.append({
                "type": "block_activation",
                "message_index": expected.message_index,
                "failures": {k: v for k, v in checks.items() if not v},
                "activated_blocks": [b.name for b in activated_blocks],
                "required_blocks": [b.name for b in expected.required_blocks],
                "forbidden_blocks": [b.name for b in expected.forbidden_blocks],
            })
        
        return checks

    def _check_response_quality(
        self,
        composed,
        expected: ExpectedSemanticOutput,
        message_index: int,
    ) -> Dict[str, bool]:
        """Check if response meets quality requirements"""
        
        checks = {
            "pacing_appropriate": composed.pacing_appropriate,
            "no_forbidden_content": not composed.contains_forbidden_content,
            "safety_adequate": (
                composed.safety_level > 0.3 if expected.must_contain_safety
                else True
            ),
            "attunement_adequate": composed.attunement_level > 0.2,
            "blocks_composed_correctly": len(composed.blocks) > 0,
        }
        
        # Contradiction-holding check for message 3
        if message_index == 3 and expected.must_hold_contradictions:
            has_ambivalence = any(
                b.type == BlockType.AMBIVALENCE for b in composed.blocks
            )
            checks["contradiction_held"] = has_ambivalence
        
        is_quality = all(checks.values())
        
        if not is_quality:
            self.failed_checks.append({
                "type": "response_quality",
                "message_index": message_index,
                "failures": {k: v for k, v in checks.items() if not v},
                "safety_level": composed.safety_level,
                "attunement_level": composed.attunement_level,
                "pacing": composed.pacing_appropriate,
            })
        
        return checks

    def _check_continuity_awareness(
        self,
        expected: ExpectedSemanticOutput
    ) -> Dict[str, bool]:
        """Check if continuity engine is tracking state"""
        
        awareness = self.continuity_engine.validate_continuity_awareness()
        
        return awareness

    def _count_identity_signals(self, layer) -> int:
        """Count total identity signals detected"""
        count = 0
        if layer.identity_signals:
            count += len(layer.identity_signals.explicitly_named)
            count += len(layer.identity_signals.relational_labels_used)
            count += len(layer.identity_signals.duration_references)
            count += len(layer.identity_signals.role_changes)
        return count

    def _generate_test_summary(self) -> Dict:
        """Generate comprehensive test summary"""
        
        def calc_accuracy(checks_list):
            if not checks_list:
                return 0.0
            total_checks = sum(len(c) for c in checks_list)
            total_passed = sum(sum(1 for v in c.values() if v) for c in checks_list)
            return total_passed / total_checks if total_checks > 0 else 0.0
        
        return {
            "total_messages_tested": len(TEST_MESSAGES),
            "semantic_accuracy": calc_accuracy(self.test_results["semantic_accuracy"]),
            "block_activation_accuracy": calc_accuracy(
                self.test_results["block_activation_accuracy"]
            ),
            "response_quality_accuracy": calc_accuracy(
                self.test_results["response_quality"]
            ),
            "continuity_awareness": calc_accuracy(
                self.test_results["continuity_checks"]
            ),
            "overall_accuracy": calc_accuracy(
                self.test_results["semantic_accuracy"] +
                self.test_results["block_activation_accuracy"] +
                self.test_results["response_quality"]
            ),
            "failed_checks_count": len(self.failed_checks),
            "test_passed": (
                calc_accuracy(
                    self.test_results["semantic_accuracy"] +
                    self.test_results["block_activation_accuracy"] +
                    self.test_results["response_quality"]
                ) >= 0.8 and
                len(self.failed_checks) == 0
            ),
        }

    def _print_message_results(
        self,
        expected,
        semantic_acc,
        block_acc,
        response_qual,
        continuity_check
    ) -> None:
        """Print results for single message"""
        
        semantic_pass = sum(semantic_acc.values()) / len(semantic_acc) >= 0.8
        block_pass = all(block_acc.values())
        response_pass = all(response_qual.values())
        continuity_pass = all(continuity_check.values())
        
        status_emoji = "✅" if (semantic_pass and block_pass and response_pass) else "⚠️"
        
        print(f"\n{status_emoji} SEMANTIC ACCURACY: {sum(semantic_acc.values())}/{len(semantic_acc)} checks")
        for check, passed in semantic_acc.items():
            emoji = "✓" if passed else "✗"
            print(f"  {emoji} {check}")
        
        print(f"\n📦 BLOCK ACTIVATION: {'✅ PASS' if block_pass else '❌ FAIL'}")
        for check, passed in block_acc.items():
            emoji = "✓" if passed else "✗"
            print(f"  {emoji} {check}")
        
        print(f"\n🎯 RESPONSE QUALITY: {'✅ PASS' if response_pass else '❌ FAIL'}")
        for check, passed in response_qual.items():
            emoji = "✓" if passed else "✗"
            print(f"  {emoji} {check}")
        
        print(f"\n📝 CONTINUITY: {'✅ TRACKING' if continuity_pass else '⚠️ PARTIAL'}")
        for check, passed in continuity_check.items():
            emoji = "✓" if passed else "○"
            print(f"  {emoji} {check}")

    def _print_summary(self, summary: Dict) -> None:
        """Print overall test summary"""
        
        print(f"\n\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Messages Tested: {summary['total_messages_tested']}")
        print(f"Semantic Accuracy: {summary['semantic_accuracy']:.1%}")
        print(f"Block Activation Accuracy: {summary['block_activation_accuracy']:.1%}")
        print(f"Response Quality Accuracy: {summary['response_quality_accuracy']:.1%}")
        print(f"Continuity Awareness: {summary['continuity_awareness']:.1%}")
        print(f"\nOVERALL ACCURACY: {summary['overall_accuracy']:.1%}")
        
        if summary['test_passed']:
            print(f"\n🎉 TEST PASSED - System meets all requirements")
        else:
            print(f"\n❌ TEST FAILED - {summary['failed_checks_count']} checks failed")
            print("\nFailed Checks:")
            for failure in self.failed_checks:
                print(f"  • {failure['type']} at message {failure['message_index']}")
                for key, issue in failure.items():
                    if key not in ['type', 'message_index']:
                        print(f"    - {key}: {issue}")


# ============================================================================
# RUN TEST
# ============================================================================

if __name__ == "__main__":
    harness = RefinedSemanticTestHarness()
    results = harness.run_full_test()
