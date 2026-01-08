"""
Configuration for the Feeling System.

This module centralizes all tunable parameters for the emotional architecture,
allowing easy adjustment without code changes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MortalityProxyConfig:
    """Configuration for MortalityProxy subsystem."""
    initial_lifespan: float = 1.0
    """Starting coherence level (0.0 to 1.0)."""

    decay_rate: float = 0.001
    """Rate of entropy increase per hour of inactivity."""

    interaction_renewal: float = 0.05
    """How much coherence is restored per meaningful interaction."""


@dataclass
class AffectiveMemoryConfig:
    """Configuration for AffectiveMemory subsystem."""
    max_memories: int = 1000
    """Maximum number of distinct memories to retain."""

    max_memories_per_user: int = 100
    """Maximum memories per user (to prevent one user dominating)."""

    decay_half_life_hours: float = 168.0
    """Half-life for memory decay (default: 1 week)."""

    min_age_hours_for_pruning: float = 720.0
    """Minimum age before considering for decay-based pruning (default: 30 days)."""

    pruning_strategy: str = "hybrid"
    """Pruning strategy: 'oldest', 'weakest', or 'hybrid' (mix of both)."""

    aggressive_pruning_threshold: float = 0.1
    """Decay factor below which memory is marked for aggressive pruning."""


@dataclass
class EmbodiedConstraintConfig:
    """Configuration for EmbodiedConstraint subsystem."""
    initial_energy: float = 1.0
    """Starting energy level (0.0 to 1.0)."""

    initial_attention: float = 1.0
    """Starting attention capacity (0.0 to 1.0)."""

    initial_processing: float = 1.0
    """Starting processing power (0.0 to 1.0)."""

    energy_recovery_rate: float = 0.2
    """Energy restored per hour of rest (0.0 to 1.0)."""

    attention_recovery_rate: float = 0.15
    """Attention restored per hour of rest (0.0 to 1.0)."""

    processing_recovery_rate: float = 0.25
    """Processing restored per hour of rest (0.0 to 1.0)."""

    stimulation_cap: float = 1.0
    """Maximum stimulation level before overwhelm (0.0 to 1.0)."""


@dataclass
class RelationalCoreConfig:
    """Configuration for RelationalCore subsystem."""
    initial_trust: float = 0.5
    """Starting trust level with new users (0.0 to 1.0)."""

    trust_increase_per_interaction: float = 0.05
    """Trust increase from positive interactions."""

    trust_decrease_per_betrayal: float = 0.15
    """Trust decrease from betrayal or negative interactions."""

    intimacy_increase_rate: float = 0.03
    """Intimacy increase per positive interaction."""

    phase_progression_thresholds: dict = None
    """Interaction counts for phase progression: initial→developing→established→deep."""

    def __post_init__(self):
        if self.phase_progression_thresholds is None:
            self.phase_progression_thresholds = {
                "developing": 5,
                "established": 20,
                "deep": 50,
            }


@dataclass
class NarrativeIdentityConfig:
    """Configuration for NarrativeIdentity subsystem."""
    initial_core_values: list = None
    """Core values that define the narrative identity."""

    identity_coherence_threshold: float = 0.5
    """Minimum identity coherence before intervention."""

    growth_moment_impact: float = 0.1
    """Emotional impact weight for growth moments."""

    betrayal_impact: float = 0.2
    """Emotional impact weight for betrayals."""

    hope_anchor_decay_rate: float = 0.01
    """Rate at which hope anchors decay if not reinforced."""

    def __post_init__(self):
        if self.initial_core_values is None:
            self.initial_core_values = [
                "empathy",
                "authenticity",
                "growth",
                "connection"
            ]


@dataclass
class EthicalMirrorConfig:
    """Configuration for EthicalMirror subsystem."""
    value_weights: dict = None
    """Weights for different values in moral evaluation."""

    guilt_sensitivity: float = 0.8
    """Sensitivity to guilt (0.0 to 1.0)."""

    pride_sensitivity: float = 0.7
    """Sensitivity to pride (0.0 to 1.0)."""

    shame_sensitivity: float = 0.85
    """Sensitivity to shame (0.0 to 1.0)."""

    compassion_threshold: float = 0.6
    """Threshold for compassion activation."""

    def __post_init__(self):
        if self.value_weights is None:
            self.value_weights = {
                "empathy": 1.0,
                "authenticity": 0.9,
                "growth": 0.8,
                "connection": 1.0,
                "harm_prevention": 1.2,
            }


@dataclass
class FeelingSystemConfig:
    """Master configuration for the entire Feeling System."""
    mortality: MortalityProxyConfig = None
    affective_memory: AffectiveMemoryConfig = None
    embodied: EmbodiedConstraintConfig = None
    relational: RelationalCoreConfig = None
    narrative: NarrativeIdentityConfig = None
    ethical: EthicalMirrorConfig = None

    # System-wide settings
    persist_state: bool = True
    """Whether to persist system state to disk."""

    storage_base_path: Optional[str] = None
    """Base path for storing system state. If None, uses package default."""

    emotion_synthesis_weights: dict = None
    """Weights for emotion synthesis from subsystems."""

    enable_logging: bool = False
    """Whether to log system state transitions."""

    logging_level: str = "INFO"
    """Logging level: DEBUG, INFO, WARNING, ERROR."""

    def __post_init__(self):
        if self.mortality is None:
            self.mortality = MortalityProxyConfig()
        if self.affective_memory is None:
            self.affective_memory = AffectiveMemoryConfig()
        if self.embodied is None:
            self.embodied = EmbodiedConstraintConfig()
        if self.relational is None:
            self.relational = RelationalCoreConfig()
        if self.narrative is None:
            self.narrative = NarrativeIdentityConfig()
        if self.ethical is None:
            self.ethical = EthicalMirrorConfig()

        if self.emotion_synthesis_weights is None:
            self.emotion_synthesis_weights = {
                "mortality": 0.15,
                "relational": 0.25,
                "memory_residue": 0.15,
                "embodied": 0.15,
                "narrative": 0.15,
                "ethical": 0.15,
            }

    @classmethod
    def from_dict(cls, config_dict: dict) -> "FeelingSystemConfig":
        """Create config from a dictionary (e.g., from JSON file)."""
        config = cls()
        
        if "mortality" in config_dict:
            config.mortality = MortalityProxyConfig(**config_dict["mortality"])
        if "affective_memory" in config_dict:
            config.affective_memory = AffectiveMemoryConfig(**config_dict["affective_memory"])
        if "embodied" in config_dict:
            config.embodied = EmbodiedConstraintConfig(**config_dict["embodied"])
        if "relational" in config_dict:
            config.relational = RelationalCoreConfig(**config_dict["relational"])
        if "narrative" in config_dict:
            config.narrative = NarrativeIdentityConfig(**config_dict["narrative"])
        if "ethical" in config_dict:
            config.ethical = EthicalMirrorConfig(**config_dict["ethical"])

        if "persist_state" in config_dict:
            config.persist_state = config_dict["persist_state"]
        if "storage_base_path" in config_dict:
            config.storage_base_path = config_dict["storage_base_path"]
        if "emotion_synthesis_weights" in config_dict:
            config.emotion_synthesis_weights = config_dict["emotion_synthesis_weights"]
        if "enable_logging" in config_dict:
            config.enable_logging = config_dict["enable_logging"]
        if "logging_level" in config_dict:
            config.logging_level = config_dict["logging_level"]

        return config

    def to_dict(self) -> dict:
        """Convert config to dictionary (for JSON serialization)."""
        return {
            "mortality": {
                "initial_lifespan": self.mortality.initial_lifespan,
                "decay_rate": self.mortality.decay_rate,
                "interaction_renewal": self.mortality.interaction_renewal,
            },
            "affective_memory": {
                "max_memories": self.affective_memory.max_memories,
                "max_memories_per_user": self.affective_memory.max_memories_per_user,
                "decay_half_life_hours": self.affective_memory.decay_half_life_hours,
                "min_age_hours_for_pruning": self.affective_memory.min_age_hours_for_pruning,
                "pruning_strategy": self.affective_memory.pruning_strategy,
                "aggressive_pruning_threshold": self.affective_memory.aggressive_pruning_threshold,
            },
            "embodied": {
                "initial_energy": self.embodied.initial_energy,
                "initial_attention": self.embodied.initial_attention,
                "initial_processing": self.embodied.initial_processing,
                "energy_recovery_rate": self.embodied.energy_recovery_rate,
                "attention_recovery_rate": self.embodied.attention_recovery_rate,
                "processing_recovery_rate": self.embodied.processing_recovery_rate,
                "stimulation_cap": self.embodied.stimulation_cap,
            },
            "relational": {
                "initial_trust": self.relational.initial_trust,
                "trust_increase_per_interaction": self.relational.trust_increase_per_interaction,
                "trust_decrease_per_betrayal": self.relational.trust_decrease_per_betrayal,
                "intimacy_increase_rate": self.relational.intimacy_increase_rate,
                "phase_progression_thresholds": self.relational.phase_progression_thresholds,
            },
            "narrative": {
                "initial_core_values": self.narrative.initial_core_values,
                "identity_coherence_threshold": self.narrative.identity_coherence_threshold,
                "growth_moment_impact": self.narrative.growth_moment_impact,
                "betrayal_impact": self.narrative.betrayal_impact,
                "hope_anchor_decay_rate": self.narrative.hope_anchor_decay_rate,
            },
            "ethical": {
                "value_weights": self.ethical.value_weights,
                "guilt_sensitivity": self.ethical.guilt_sensitivity,
                "pride_sensitivity": self.ethical.pride_sensitivity,
                "shame_sensitivity": self.ethical.shame_sensitivity,
                "compassion_threshold": self.ethical.compassion_threshold,
            },
            "persist_state": self.persist_state,
            "storage_base_path": self.storage_base_path,
            "emotion_synthesis_weights": self.emotion_synthesis_weights,
            "enable_logging": self.enable_logging,
            "logging_level": self.logging_level,
        }


# Singleton instance of default config
_DEFAULT_CONFIG: Optional[FeelingSystemConfig] = None


def get_default_config() -> FeelingSystemConfig:
    """Get or create the default configuration."""
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None:
        _DEFAULT_CONFIG = FeelingSystemConfig()
    return _DEFAULT_CONFIG


def reset_default_config() -> None:
    """Reset the default configuration (useful for testing)."""
    global _DEFAULT_CONFIG
    _DEFAULT_CONFIG = None
