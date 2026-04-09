"""
Core data models for the LimbicAI system.

Models represent emotional features and limbic brain region activations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EmotionalFeatures:
    """Represents extracted emotional features from a scenario.
    
    Attributes:
        social_rejection: Level of social rejection/exclusion (0-1)
        self_blame: Level of self-attribution of blame (0-1)
        other_blame: Level of blaming others (0-1)
        empathy_for_other: Level of empathy/perspective-taking (0-1)
        rationalization: Level of cognitive rationalization/downregulation (0-1)
        threat_to_identity: Level of identity threat/challenge (0-1)
        loss_of_reward: Level of loss of expected positive outcome (0-1)
    """
    social_rejection: float = 0.0
    self_blame: float = 0.0
    other_blame: float = 0.0
    empathy_for_other: float = 0.0
    rationalization: float = 0.0
    threat_to_identity: float = 0.0
    loss_of_reward: float = 0.0

    def __post_init__(self):
        """Validate that all features are in [0, 1] range."""
        for field_value in [
            self.social_rejection,
            self.self_blame,
            self.other_blame,
            self.empathy_for_other,
            self.rationalization,
            self.threat_to_identity,
            self.loss_of_reward,
        ]:
            if not 0 <= field_value <= 1:
                raise ValueError(f"Feature values must be between 0 and 1, got {field_value}")


@dataclass
class LimbicState:
    """Represents activation levels of major limbic brain regions.
    
    Attributes:
        amygdala: Threat, fear, social rejection, anger (0-1)
        hippocampus: Memory, context formation (0-1)
        acc: Emotional pain, conflict monitoring, guilt (0-1)
        insula: Interoception, disgust, empathy (0-1)
        vmPFC: Valuation, moral weighing, emotional significance (0-1)
        dlPFC: Rationalization, cognitive control (0-1)
        nucleus_accumbens: Reward, motivation, loss aversion (0-1)
    """
    amygdala: float = 0.0
    hippocampus: float = 0.0
    acc: float = 0.0
    insula: float = 0.0
    vmPFC: float = 0.0
    dlPFC: float = 0.0
    nucleus_accumbens: float = 0.0

    def __post_init__(self):
        """Validate that all activations are in [0, 1] range."""
        for field_value in [
            self.amygdala,
            self.hippocampus,
            self.acc,
            self.insula,
            self.vmPFC,
            self.dlPFC,
            self.nucleus_accumbens,
        ]:
            if not 0 <= field_value <= 1:
                raise ValueError(f"Activation values must be between 0 and 1, got {field_value}")

    def as_dict(self) -> dict:
        """Convert to dictionary for easy serialization."""
        return {
            "amygdala": self.amygdala,
            "hippocampus": self.hippocampus,
            "acc": self.acc,
            "insula": self.insula,
            "vmPFC": self.vmPFC,
            "dlPFC": self.dlPFC,
            "nucleus_accumbens": self.nucleus_accumbens,
        }


@dataclass
class LimbicAnalysis:
    """Complete analysis result from user scenario."""
    scenario: str
    emotional_features: EmotionalFeatures
    limbic_state: LimbicState
    explanations: dict  # Maps brain region name to explanation text


def clamp_01(value: float) -> float:
    """Clamp a value to [0, 1] range."""
    return max(0.0, min(1.0, value))
