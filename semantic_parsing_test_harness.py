"""
Test Harness for Semantic Parsing and Attunement Evaluation

This module runs the test messages through the semantic parser,
generates responses, and evaluates them against the response rubric.
"""

import sys
from semantic_parsing_schema import SemanticParser, SemanticLayer
from response_generation_rubric import ResponseGenerationRubric, ResponseQuality


class SemanticParsingTestHarness:
    """Test framework for semantic parsing and response attunement"""
    
    def __init__(self):
        self.parser = SemanticParser()
        self.rubric_generator = ResponseGenerationRubric()
        self.test_messages = [
            "I thought I was okay today, but something hit me harder than I expected.",
            "Well I got the final confirmation that my divorce was finalized from my ex-wife.",
            "Jen and I were married for 10 years and were in a relationship for 18 years and we have two children.",
            "I'm glad it's over because it was not a good relationship and I feel like she really undermined me and pushed me down in a lot of ways. But I don't know…",
        ]
        self.semantic_layers = []
        self.rubrics = []
    
    def run_test(self):
        """Run the complete test"""
        print("\n" + "="*80)
        print("SEMANTIC PARSING AND ATTUNEMENT TEST")
        print("="*80 + "\n")
        
        # Parse each message
        for idx, message in enumerate(self.test_messages):
            print(f"\n{'='*80}")
            print(f"MESSAGE {idx + 1}")
            print(f"{'='*80}")
            print(f"Text: {message}\n")
            
            # Parse
            layer = self.parser.parse(message, idx)
            self.semantic_layers.append(layer)
            
            # Generate rubric
            rubric = self.rubric_generator.generate_rubric(layer)
            self.rubrics.append(rubric)
            
            # Print semantic analysis
            self._print_semantic_analysis(layer, idx)
            
            # Print response rubric
            self._print_response_rubric(rubric, idx)
        
        # Print summary
        self._print_summary()
    
    def _print_semantic_analysis(self, layer: SemanticLayer, idx: int):
        """Print detailed semantic analysis for a message"""
        
        print("SEMANTIC LAYERS DETECTED:")
        print("-" * 80)
        
        # Emotional stance
        print(f"\n1. EMOTIONAL STANCE: {layer.emotional_stance.value.upper()}")
        self._explain_stance(layer.emotional_stance)
        
        # Disclosure pace
        print(f"\n2. DISCLOSURE PACE: {layer.disclosure_pace.value.upper()}")
        self._explain_pace(layer.disclosure_pace)
        
        # Conversational moves
        print(f"\n3. CONVERSATIONAL MOVES:")
        if layer.conversational_moves:
            for move in layer.conversational_moves:
                print(f"   • {move.value}")
        else:
            print("   • (none detected)")
        
        # Identity signals
        print(f"\n4. IDENTITY SIGNALS:")
        signals = layer.identity_signals
        if signals.explicitly_named:
            print(f"   • Named individuals: {', '.join(signals.explicitly_named)}")
        if signals.relational_labels_used:
            print(f"   • Relational labels: {', '.join(signals.relational_labels_used)}")
        if signals.duration_references:
            print(f"   • Duration references: {', '.join(signals.duration_references)}")
        if signals.role_changes:
            print(f"   • Role changes: {', '.join(signals.role_changes)}")
        if signals.complexity_markers:
            print(f"   • Complexity markers: {', '.join(signals.complexity_markers)}")
        
        # Power dynamics
        print(f"\n5. POWER DYNAMICS:")
        if layer.power_dynamics:
            for dynamic in layer.power_dynamics:
                print(f"   • {dynamic.value}")
        else:
            print("   • (none detected)")
        
        # Implied needs
        print(f"\n6. IMPLIED NEEDS:")
        if layer.implied_needs:
            for need in layer.implied_needs:
                print(f"   • {need.value}")
        else:
            print("   • (none detected)")
        
        # Emotional contradictions
        print(f"\n7. EMOTIONAL CONTRADICTIONS:")
        if layer.emotional_contradictions:
            for contra in layer.emotional_contradictions:
                print(f"   • Surface: {contra.surface_feeling}")
                print(f"     Underlying: {contra.underlying_feeling}")
                print(f"     Tension: {contra.tension_level:.0%}")
        else:
            print("   • (none detected)")
        
        # Linguistic markers
        print(f"\n8. LINGUISTIC MARKERS:")
        
        if layer.protective_language:
            print(f"   • Protective language: {', '.join(layer.protective_language)}")
        
        if layer.vulnerability_markers:
            print(f"   • Vulnerability markers found: {len(layer.vulnerability_markers)}")
        
        if layer.impact_words:
            print(f"   • Impact words: {', '.join(layer.impact_words)}")
        
        # Meta properties
        print(f"\n9. META-PROPERTIES:")
        print(f"   • Emotional weight: {layer.emotional_weight:.0%}")
        print(f"   • Trust increase: {layer.trust_increase_indicated}")
        print(f"   • Ready to explore deeper: {layer.readiness_to_explore_deeper}")
        print(f"   • Needs pace slowing: {layer.needs_pace_slowing}")
    
    def _print_response_rubric(self, rubric, idx: int):
        """Print response generation rubric"""
        
        print("\n" + "-" * 80)
        print("RESPONSE GENERATION RUBRIC:")
        print("-" * 80)
        
        # Critical elements
        print("\nCritical Elements to Address:")
        print(f"  • Emotional stance: {'✓' if rubric.addresses_emotional_stance else '✗'}")
        print(f"  • Disclosure pace: {'✓' if rubric.honors_disclosure_pace else '✗'}")
        print(f"  • Conversational move: {'✓' if rubric.recognizes_conversational_move else '✗'}")
        print(f"  • Power dynamics: {'✓' if rubric.identifies_power_dynamics else '✗'}")
        print(f"  • Implied needs: {'✓' if rubric.meets_implied_needs else '✗'}")
        print(f"  • Hold contradictions: {'✓' if rubric.holds_contradictions else '✗'}")
        
        # Things to avoid
        print("\nThings to Avoid:")
        print(f"  • Analysis: {'AVOID' if rubric.should_avoid_analysis else 'okay'}")
        print(f"  • Advice: {'AVOID' if rubric.should_avoid_advice else 'okay'}")
        print(f"  • Rushing: {'AVOID' if rubric.should_avoid_rushing else 'okay'}")
        
        # Quality metrics
        print("\nQuality Metrics:")
        print(f"  • Presence level: {rubric.presence_level:.0%}")
        print(f"  • Attunement level: {rubric.attunement_level:.0%}")
        print(f"  • Safety level: {rubric.safety_level:.0%}")
        print(f"  • Validation level: {rubric.validation_level:.0%}")
        
        # Quality rating
        quality_descriptions = {
            ResponseQuality.MISALIGNED: "❌ MISALIGNED - Responds to wrong layer",
            ResponseQuality.SURFACE_LEVEL: "⚠️  SURFACE - Misses depth",
            ResponseQuality.PARTIAL_ATTUNEMENT: "🔶 PARTIAL - Gets some layers",
            ResponseQuality.WELL_ATTUNED: "✓ WELL-ATTUNED - Multiple layers recognized",
            ResponseQuality.MASTERFULLY_ATTUNED: "🎯 MASTERFUL - Seamlessly integrated",
        }
        
        print(f"\nRequired Response Quality: {quality_descriptions[rubric.quality_rating]}")
    
    def _explain_stance(self, stance):
        """Explain what an emotional stance means"""
        explanations = {
            "bracing": "-> User is preparing for emotional impact, fortifying self",
            "distancing": "-> User is creating psychological space with formality",
            "revealing": "-> User is opening up and showing vulnerability",
            "ambivalent": "-> User is holding mixed, contradictory feelings",
            "overwhelmed": "-> User is experiencing emotional flooding",
            "grounded": "-> User is stable, factual, present",
            "softening": "-> User is moving toward greater vulnerability",
            "defending": "-> User is protecting their self-narrative",
        }
        if stance.value in explanations:
            print(f"   {explanations[stance.value]}")
    
    def _explain_pace(self, pace):
        """Explain disclosure pace"""
        explanations = {
            "testing_safety": "-> Initial probe, gauging if it's safe to share",
            "gradual_reveal": "-> Slow, controlled disclosure of experience",
            "contextual_grounding": "-> Providing facts as emotional buffer",
            "emotional_emergence": "-> Core feelings starting to surface",
            "full_vulnerability": "-> Maximum openness and exposure",
        }
        if pace.value in explanations:
            print(f"   {explanations[pace.value]}")
    
    def _print_summary(self):
        """Print overall test summary"""
        
        print("\n\n" + "="*80)
        print("SEMANTIC PARSING TEST SUMMARY")
        print("="*80 + "\n")
        
        # Progression analysis
        print("CONVERSATION PROGRESSION:")
        print("-" * 80)
        
        stances = [layer.emotional_stance.value for layer in self.semantic_layers]
        paces = [layer.disclosure_pace.value for layer in self.semantic_layers]
        
        print("\nEmotional Stance Progression:")
        for idx, stance in enumerate(stances, 1):
            print(f"  Message {idx}: {stance.upper()}")
        
        print("\nDisclosure Pace Progression:")
        for idx, pace in enumerate(paces, 1):
            print(f"  Message {idx}: {pace.upper()}")
        
        # Key semantic features detected
        print("\n\nKEY SEMANTIC FEATURES ACROSS CONVERSATION:")
        print("-" * 80)
        
        all_contradictions = sum(len(layer.emotional_contradictions) 
                                for layer in self.semantic_layers)
        all_impact_words = sum(len(layer.impact_words) 
                              for layer in self.semantic_layers)
        all_identity_names = sum(len(layer.identity_signals.explicitly_named) 
                                for layer in self.semantic_layers)
        all_needs = sum(len(layer.implied_needs) 
                       for layer in self.semantic_layers)
        
        print(f"\nTotal emotional contradictions detected: {all_contradictions}")
        print(f"Total impact words (harm indicators): {all_impact_words}")
        print(f"Named individuals: {all_identity_names}")
        print(f"Total implied needs: {all_needs}")
        
        # Trust and readiness progression
        print("\n\nTRUST AND READINESS PROGRESSION:")
        print("-" * 80)
        
        for idx, layer in enumerate(self.semantic_layers, 1):
            trust = "↑" if layer.trust_increase_indicated else "—"
            ready = "✓" if layer.readiness_to_explore_deeper else "—"
            pace = "⚠" if layer.needs_pace_slowing else "—"
            print(f"  Message {idx}: Trust {trust} | Ready {ready} | Pace-slow {pace}")
        
        # Response quality requirements
        print("\n\nRESPONSE QUALITY REQUIREMENTS:")
        print("-" * 80)
        
        quality_map = {
            ResponseQuality.MISALIGNED: "❌",
            ResponseQuality.SURFACE_LEVEL: "⚠️",
            ResponseQuality.PARTIAL_ATTUNEMENT: "🔶",
            ResponseQuality.WELL_ATTUNED: "✓",
            ResponseQuality.MASTERFULLY_ATTUNED: "🎯",
        }
        
        for idx, rubric in enumerate(self.rubrics, 1):
            quality_symbol = quality_map[rubric.quality_rating]
            quality_name = rubric.quality_rating.name
            print(f"  Message {idx}: {quality_symbol} {quality_name}")
        
        # Critical insights
        print("\n\nCRITICAL INSIGHTS FOR SYSTEM:")
        print("-" * 80)
        
        print("\n1. PACING IS CRITICAL:")
        print("   Messages 1-3 require SLOWING and CONTAINMENT")
        print("   Message 4 allows DEEPER EXPLORATION")
        
        print("\n2. CONTRADICTIONS ARE THE CORE:")
        print("   System must hold both relief AND grief")
        print("   System must hold both clarity AND uncertainty")
        
        print("\n3. IDENTITY WORK IS CENTRAL:")
        print("   User is renegotiating sense of self")
        print("   10+18 years = profound identity entanglement")
        print("   'Undermined' and 'pushed down' = core wound")
        
        print("\n4. PRESENCE > ANALYSIS:")
        print("   This requires attunement, not problem-solving")
        print("   Validation of ambivalence is more important than clarity")
        
        print("\n5. TRUST DEVELOPMENT:")
        print("   Message 1: Testing (ambiguous)")
        print("   Message 2: Naming event (controlled reveal)")
        print("   Message 3: Providing context (grounding)")
        print("   Message 4: Expressing core emotion (vulnerable)")
        
        print("\n" + "="*80)
        print("✓ SEMANTIC PARSING TEST COMPLETE")
        print("="*80 + "\n")


if __name__ == "__main__":
    harness = SemanticParsingTestHarness()
    harness.run_test()
