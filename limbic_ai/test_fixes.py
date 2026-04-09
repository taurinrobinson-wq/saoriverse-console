#!/usr/bin/env python3
"""Test the fixed NLP parser and limbic mapping on user scenarios."""

from limbic_ai.models import EmotionalFeatures
from limbic_ai.nlp_parser import EmotionalFeatureExtractor
from limbic_ai.mapping import map_features_to_limbic
from limbic_ai.analyzer import LimbicAnalyzer

def test_scenarios():
    """Test the three user-provided scenarios."""
    
    extractor = EmotionalFeatureExtractor()
    analyzer = LimbicAnalyzer()
    
    scenarios = [
        {
            "name": "Scenario 1: Self-blame & Relationship Anxiety",
            "text": "I feel ashamed and embarrassed because my partner said I never listen. I got defensive. Now I'm scared she might leave me. I keep thinking about all the times I messed up. I feel guilty and overwhelmed.",
            "expected": "High self_blame, high threat_to_identity, high ACC/amygdala/dlPFC"
        },
        {
            "name": "Scenario 2: Betrayal & Other-blame",
            "text": "My coworker took credit for my work and I'm furious. I feel betrayed and disrespected.",
            "expected": "High other_blame, high social_rejection, high amygdala"
        },
        {
            "name": "Scenario 3: Low Empathy & Rationalization",
            "text": "My friend is devastated about losing her job. I don't understand why it's such a big deal.",
            "expected": "Low empathy, high rationalization, low insula"
        }
    ]
    
    print("=" * 80)
    print("LIMBIC AI - SCENARIO VALIDATION TEST")
    print("=" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{scenario['name']}")
        print("-" * 80)
        print(f"Scenario: {scenario['text']}")
        print(f"Expected: {scenario['expected']}")
        print()
        
        # Extract features
        features = extractor.extract_features(scenario['text'])
        
        print("Extracted Emotional Features:")
        print(f"  • Social Rejection:     {features.social_rejection:.3f}")
        print(f"  • Self-Blame:           {features.self_blame:.3f}")
        print(f"  • Other-Blame:          {features.other_blame:.3f}")
        print(f"  • Empathy for Other:    {features.empathy_for_other:.3f}")
        print(f"  • Rationalization:      {features.rationalization:.3f}")
        print(f"  • Threat to Identity:   {features.threat_to_identity:.3f}")
        print(f"  • Loss of Reward:       {features.loss_of_reward:.3f}")
        
        # Map to limbic activations
        limbic_state = map_features_to_limbic(features)
        
        print("\nLimbic System Activations:")
        print(f"  • Amygdala:             {limbic_state.amygdala:.3f}")
        print(f"  • Hippocampus:          {limbic_state.hippocampus:.3f}")
        print(f"  • ACC:                  {limbic_state.acc:.3f}")
        print(f"  • Insula:               {limbic_state.insula:.3f}")
        print(f"  • vmPFC:                {limbic_state.vmPFC:.3f}")
        print(f"  • dlPFC:                {limbic_state.dlPFC:.3f}")
        print(f"  • Nucleus Accumbens:    {limbic_state.nucleus_accumbens:.3f}")
        
        # Get guidance/explanations
        analysis = analyzer.analyze(scenario['text'])
        print("\nBrain Region Activation Explanations:")
        for region, explanation in analysis.explanations.items():
            print(f"  • {region}: {explanation}")
        
        # Check validity
        all_near_zero = all([
            features.social_rejection < 0.01,
            features.self_blame < 0.01,
            features.other_blame < 0.01,
            features.empathy_for_other < 0.01,
            features.rationalization < 0.01,
            features.threat_to_identity < 0.01,
            features.loss_of_reward < 0.01,
        ])
        
        if all_near_zero:
            print("\n⚠️  WARNING: All features are near-zero (normalization issue not fully resolved)")
        else:
            feature_count = sum([
                1 for f in [
                    features.social_rejection,
                    features.self_blame,
                    features.other_blame,
                    features.empathy_for_other,
                    features.rationalization,
                    features.threat_to_identity,
                    features.loss_of_reward,
                ] if f > 0.01
            ])
            print(f"\n✓ PASS: {feature_count} emotional features detected with meaningful values")

if __name__ == "__main__":
    test_scenarios()
