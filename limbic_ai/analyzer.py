"""
Main LimbicAI analyzer that orchestrates the full pipeline.

This module ties together NLP parsing, feature mapping, and explanation generation.
"""

from limbic_ai.nlp_parser import EmotionalFeatureExtractor
from limbic_ai.mapping import map_features_to_limbic, get_region_explanation
from limbic_ai.models import LimbicAnalysis


class LimbicAnalyzer:
    """Main analyzer for converting scenarios to limbic activations and explanations."""
    
    def __init__(self):
        """Initialize the analyzer with NLP extractor."""
        self.extractor = EmotionalFeatureExtractor()
    
    def analyze(self, scenario: str) -> LimbicAnalysis:
        """Analyze a scenario and generate limbic state with explanations.
        
        Args:
            scenario: User-provided emotional scenario
            
        Returns:
            LimbicAnalysis with features, limbic state, and region explanations
        """
        if not scenario or len(scenario.strip()) < 10:
            raise ValueError("Scenario must be at least 10 characters")
        
        # Extract emotional features from text
        features = self.extractor.extract_features(scenario)
        
        # Map features to limbic activations
        limbic_state = map_features_to_limbic(features)
        
        # Generate explanations for each region
        explanations = self._generate_explanations(limbic_state)
        
        return LimbicAnalysis(
            scenario=scenario,
            emotional_features=features,
            limbic_state=limbic_state,
            explanations=explanations,
        )
    
    def _generate_explanations(self, limbic_state) -> dict:
        """Generate explanations for active limbic regions.
        
        Args:
            limbic_state: LimbicState instance
            
        Returns:
            Dictionary mapping region names to explanation strings
        """
        regions = limbic_state.as_dict()
        explanations = {}
        
        for region_name, activation in regions.items():
            explanations[region_name] = get_region_explanation(region_name, activation)
        
        return explanations
    
    def get_summary(self, analysis: LimbicAnalysis) -> str:
        """Generate a narrative summary of the limbic analysis.
        
        Args:
            analysis: LimbicAnalysis instance
            
        Returns:
            Formatted summary string
        """
        state = analysis.limbic_state
        features = analysis.emotional_features
        
        # Find most activated regions
        regions_sorted = sorted(
            state.as_dict().items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        top_regions = regions_sorted[:3]
        
        summary = f"""
## Emotional Analysis

Your scenario appears to activate several emotional/cognitive systems:

"""
        for region, activation in top_regions:
            if activation > 0.2:  # Only mention regions with meaningful activation
                summary += f"\n**{region.upper()}** (Activation: {activation:.1%})\n"
                summary += f"{analysis.explanations[region]}\n"
        
        # Add synthesis
        summary += f"""
## What This Tells Us

Based on the language and themes in your scenario, here are the key insights:

- **Emotional Intensity**: {self._get_intensity_description(features)}
- **Primary Focus**: {self._get_focus_description(features)}
- **Coping Strategy**: {self._get_strategy_description(features)}

"""
        return summary
    
    @staticmethod
    def _get_intensity_description(features) -> str:
        """Describe overall emotional intensity."""
        avg_activation = sum([
            features.social_rejection,
            features.threat_to_identity,
            features.loss_of_reward,
        ]) / 3
        
        if avg_activation > 0.7:
            return "This situation appears highly emotionally significant"
        elif avg_activation > 0.4:
            return "This situation carries moderate emotional weight"
        else:
            return "This situation has mild emotional resonance for you"
    
    @staticmethod
    def _get_focus_description(features) -> str:
        """Describe whether focus is on self or others."""
        self_focus = features.self_blame
        other_focus = features.other_blame
        
        if self_focus > other_focus + 0.2:
            return "Internal focus (self-directed thoughts/responsibility)"
        elif other_focus > self_focus + 0.2:
            return "External focus (others' behavior/responsibility)"
        else:
            return "Balanced perspective"
    
    @staticmethod
    def _get_strategy_description(features) -> str:
        """Describe apparent coping strategy."""
        if features.rationalization > 0.6:
            return "Cognitive reframing/rationalization"
        elif features.empathy_for_other > 0.6:
            return "Empathic engagement"
        else:
            return "Emotional processing"
