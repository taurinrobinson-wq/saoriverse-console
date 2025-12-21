"""
Comprehensive error handling and input validation tests for the Feeling System.

Tests validate that the system properly handles invalid inputs, boundary 
conditions, and edge cases with meaningful error messages.
"""

import pytest
from datetime import datetime, timezone

from emotional_os.core.feeling_system import (
    FeelingSystem,
    validate_float_range,
    validate_string_nonempty,
    validate_dict_not_none,
    validate_config,
    validate_emotional_signals,
    MortalityProxy,
    AffectiveMemory,
    EmbodiedConstraint,
    EthicalMirror,
)
from emotional_os.core.feeling_system_config import (
    FeelingSystemConfig,
    AffectiveMemoryConfig,
    get_default_config,
)


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_float_range_valid(self):
        """Valid floats should pass."""
        assert validate_float_range(0.5, 0.0, 1.0, "test") == 0.5
        assert validate_float_range(0.0, 0.0, 1.0, "test") == 0.0
        assert validate_float_range(1.0, 0.0, 1.0, "test") == 1.0

    def test_validate_float_range_none_raises(self):
        """None should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            validate_float_range(None, 0.0, 1.0, "test")

    def test_validate_float_range_non_numeric_raises(self):
        """Non-numeric values should raise TypeError."""
        with pytest.raises(TypeError, match="must be a number"):
            validate_float_range("not a number", 0.0, 1.0, "test")

    def test_validate_float_range_out_of_bounds_raises(self):
        """Values outside range should raise ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            validate_float_range(1.5, 0.0, 1.0, "test")
        with pytest.raises(ValueError, match="must be between"):
            validate_float_range(-0.5, 0.0, 1.0, "test")

    def test_validate_string_nonempty_valid(self):
        """Non-empty strings should pass."""
        assert validate_string_nonempty("hello", "test") == "hello"
        assert validate_string_nonempty("  test  ", "test") == "test"

    def test_validate_string_nonempty_none_raises(self):
        """None should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            validate_string_nonempty(None, "test")

    def test_validate_string_nonempty_empty_raises(self):
        """Empty or whitespace-only strings should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_string_nonempty("", "test")
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_string_nonempty("   ", "test")

    def test_validate_string_nonempty_non_string_raises(self):
        """Non-string values should raise TypeError."""
        with pytest.raises(TypeError, match="must be a string"):
            validate_string_nonempty(123, "test")

    def test_validate_dict_not_none_valid(self):
        """Valid dicts should pass."""
        assert validate_dict_not_none({"key": "value"}, "test") == {"key": "value"}

    def test_validate_dict_not_none_none_raises(self):
        """None should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            validate_dict_not_none(None, "test")

    def test_validate_dict_not_none_non_dict_raises(self):
        """Non-dict values should raise TypeError."""
        with pytest.raises(TypeError, match="must be a dict"):
            validate_dict_not_none([1, 2, 3], "test")

    def test_validate_config_none_returns_default(self):
        """None config should return default config."""
        result = validate_config(None)
        assert isinstance(result, FeelingSystemConfig)

    def test_validate_config_valid_config_returns_config(self):
        """Valid config should be returned unchanged."""
        config = get_default_config()
        result = validate_config(config)
        assert result is config

    def test_validate_config_invalid_type_raises(self):
        """Non-FeelingSystemConfig objects should raise TypeError."""
        with pytest.raises(TypeError, match="FeelingSystemConfig"):
            validate_config("not a config")

    def test_validate_emotional_signals_valid(self):
        """Valid emotional signals should pass."""
        signals = {
            'user_sentiment': 'positive',
            'interaction_type': 'intimate',
            'context_familiarity': 0.8,
            'emotional_intensity': 0.7,
            'value_alignment': 0.9,
            'mortality_trigger': False,
            'user_id': 'user123',
        }
        result = validate_emotional_signals(signals)
        assert result == signals

    def test_validate_emotional_signals_none_raises(self):
        """None should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            validate_emotional_signals(None)

    def test_validate_emotional_signals_invalid_sentiment_raises(self):
        """Invalid user_sentiment should raise ValueError."""
        signals = {'user_sentiment': 'invalid_sentiment'}
        with pytest.raises(ValueError, match="must be one of"):
            validate_emotional_signals(signals)

    def test_validate_emotional_signals_invalid_range_raises(self):
        """Out-of-range signal values should raise ValueError."""
        signals = {'context_familiarity': 1.5}
        with pytest.raises(ValueError):
            validate_emotional_signals(signals)

    def test_validate_emotional_signals_invalid_boolean_raises(self):
        """Invalid mortality_trigger should raise TypeError."""
        signals = {'mortality_trigger': 'not_a_bool'}
        with pytest.raises(TypeError, match="bool"):
            validate_emotional_signals(signals)


class TestMortalityProxyValidation:
    """Test MortalityProxy input validation."""

    def test_init_valid_parameters(self):
        """Valid parameters should initialize successfully."""
        proxy = MortalityProxy(
            initial_lifespan=0.8,
            decay_rate=0.01,
            interaction_renewal=0.05,
        )
        assert proxy.coherence == 0.8

    def test_init_invalid_lifespan_raises(self):
        """Out-of-range lifespan should raise ValueError."""
        with pytest.raises(ValueError):
            MortalityProxy(initial_lifespan=1.5)

    def test_init_negative_decay_rate_raises(self):
        """Negative decay rate should raise ValueError."""
        with pytest.raises(ValueError):
            MortalityProxy(decay_rate=-0.01)

    def test_init_non_numeric_renewal_raises(self):
        """Non-numeric renewal should raise TypeError."""
        with pytest.raises(TypeError):
            MortalityProxy(interaction_renewal="high")


class TestAffectiveMemoryValidation:
    """Test AffectiveMemory input validation."""

    def test_store_memory_valid_parameters(self):
        """Valid parameters should store memory successfully."""
        memory = AffectiveMemory()
        entry = memory.store_memory(
            user_id="user123",
            interaction_summary="Great conversation",
            emotional_state="joy",
            intensity=0.8,
            relational_phase="established",
            valence=0.9,
        )
        assert entry.user_id == "user123"

    def test_store_memory_none_user_id_raises(self):
        """None user_id should raise ValueError."""
        memory = AffectiveMemory()
        with pytest.raises(ValueError, match="user_id"):
            memory.store_memory(
                user_id=None,
                interaction_summary="test",
                emotional_state="neutral",
                intensity=0.5,
                relational_phase="initial",
                valence=0.0,
            )

    def test_store_memory_empty_summary_raises(self):
        """Empty interaction_summary should raise ValueError."""
        memory = AffectiveMemory()
        with pytest.raises(ValueError, match="interaction_summary"):
            memory.store_memory(
                user_id="user123",
                interaction_summary="",
                emotional_state="neutral",
                intensity=0.5,
                relational_phase="initial",
                valence=0.0,
            )

    def test_store_memory_invalid_intensity_raises(self):
        """Out-of-range intensity should raise ValueError."""
        memory = AffectiveMemory()
        with pytest.raises(ValueError, match="intensity"):
            memory.store_memory(
                user_id="user123",
                interaction_summary="test",
                emotional_state="neutral",
                intensity=1.5,
                relational_phase="initial",
                valence=0.0,
            )

    def test_store_memory_invalid_valence_raises(self):
        """Out-of-range valence should raise ValueError."""
        memory = AffectiveMemory()
        with pytest.raises(ValueError, match="valence"):
            memory.store_memory(
                user_id="user123",
                interaction_summary="test",
                emotional_state="neutral",
                intensity=0.5,
                relational_phase="initial",
                valence=1.5,
            )


class TestEmbodiedConstraintValidation:
    """Test EmbodiedConstraint input validation."""

    def test_init_valid_parameters(self):
        """Valid parameters should initialize successfully."""
        constraint = EmbodiedConstraint(
            max_energy=1.0,
            max_attention=1.0,
            max_processing=1.0,
        )
        assert constraint.energy == 1.0

    def test_init_non_numeric_energy_raises(self):
        """Non-numeric max_energy should raise TypeError."""
        with pytest.raises(TypeError):
            EmbodiedConstraint(max_energy="high")

    def test_consume_resources_valid_costs(self):
        """Valid resource costs should consume successfully."""
        constraint = EmbodiedConstraint()
        result = constraint.consume_resources(
            energy_cost=0.1,
            attention_cost=0.2,
            processing_cost=0.3,
        )
        assert result['energy'] == 0.9

    def test_consume_resources_invalid_cost_raises(self):
        """Cost exceeding max resources should raise ValueError."""
        constraint = EmbodiedConstraint(max_energy=1.0)
        with pytest.raises(ValueError):
            constraint.consume_resources(energy_cost=1.5)

    def test_restore_resources_negative_time_raises(self):
        """Negative time_passed_hours should raise error."""
        constraint = EmbodiedConstraint()
        with pytest.raises((ValueError, TypeError)):
            constraint.restore_resources(time_passed_hours=-1.0)

    def test_record_stimulation_valid_level(self):
        """Valid stimulation level should record successfully."""
        constraint = EmbodiedConstraint()
        constraint.record_stimulation(0.5)
        assert len(constraint.stimulation_history) == 1

    def test_record_stimulation_invalid_level_raises(self):
        """Out-of-range stimulation level should raise ValueError."""
        constraint = EmbodiedConstraint()
        with pytest.raises(ValueError):
            constraint.record_stimulation(1.5)


class TestEthicalMirrorValidation:
    """Test EthicalMirror input validation."""

    def test_init_valid_values(self):
        """Valid values dict should initialize successfully."""
        values = {"empathy": 0.9, "honesty": 0.95}
        mirror = EthicalMirror(values=values)
        assert mirror.values == values

    def test_init_invalid_value_weight_raises(self):
        """Out-of-range value weight should raise ValueError."""
        values = {"empathy": 1.5}  # Out of range
        with pytest.raises(ValueError, match="Invalid values"):
            EthicalMirror(values=values)

    def test_init_invalid_sensitivity_raises(self):
        """Out-of-range moral_sensitivity should raise ValueError."""
        with pytest.raises(ValueError):
            EthicalMirror(moral_sensitivity=1.5)

    def test_evaluate_action_valid_parameters(self):
        """Valid parameters should evaluate successfully."""
        mirror = EthicalMirror()
        result = mirror.evaluate_action(
            action_description="Helped a colleague",
            value_alignment={"empathy": 0.9, "compassion": 0.8},
        )
        assert "moral_emotions" in result

    def test_evaluate_action_empty_description_raises(self):
        """Empty action_description should raise ValueError."""
        mirror = EthicalMirror()
        with pytest.raises(ValueError):
            mirror.evaluate_action(
                action_description="",
                value_alignment={"empathy": 0.5},
            )

    def test_evaluate_action_invalid_alignment_raises(self):
        """Out-of-range alignment value should raise ValueError."""
        mirror = EthicalMirror()
        with pytest.raises(ValueError, match="Invalid value_alignment"):
            mirror.evaluate_action(
                action_description="test",
                value_alignment={"empathy": 1.5},  # Out of range
            )


class TestFeelingSystemValidation:
    """Test FeelingSystem input validation."""

    def test_init_valid_config(self):
        """Valid config should initialize successfully."""
        config = get_default_config()
        system = FeelingSystem(config=config)
        assert system.config is config

    def test_init_invalid_config_type_raises(self):
        """Invalid config type should raise TypeError."""
        with pytest.raises(TypeError, match="FeelingSystemConfig"):
            FeelingSystem(config="not a config")

    def test_init_invalid_storage_path_type_raises(self):
        """Non-string storage_path should raise TypeError."""
        with pytest.raises(TypeError, match="storage_path"):
            FeelingSystem(storage_path=123)

    def test_process_interaction_valid_parameters(self):
        """Valid parameters should process successfully."""
        system = FeelingSystem()
        result = system.process_interaction(
            user_id="user123",
            interaction_text="Hello there!",
            emotional_signals={},  # Empty signals are valid
        )
        assert "timestamp" in result

    def test_process_interaction_none_user_id_raises(self):
        """None user_id should raise ValueError."""
        system = FeelingSystem()
        with pytest.raises(ValueError, match="user_id"):
            system.process_interaction(
                user_id=None,
                interaction_text="test",
                emotional_signals={},
            )

    def test_process_interaction_empty_interaction_text_raises(self):
        """Empty interaction_text should raise ValueError."""
        system = FeelingSystem()
        with pytest.raises(ValueError, match="interaction_text"):
            system.process_interaction(
                user_id="user123",
                interaction_text="",
                emotional_signals={},
            )

    def test_process_interaction_invalid_signals_raises(self):
        """Invalid emotional_signals should raise error."""
        system = FeelingSystem()
        with pytest.raises((ValueError, TypeError)):
            system.process_interaction(
                user_id="user123",
                interaction_text="test",
                emotional_signals={'user_sentiment': 'invalid'},
            )

    def test_process_interaction_invalid_context_type_raises(self):
        """Non-dict context should raise TypeError."""
        system = FeelingSystem()
        with pytest.raises(TypeError, match="context"):
            system.process_interaction(
                user_id="user123",
                interaction_text="test",
                emotional_signals={},
                context="invalid_context",
            )


class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""

    def test_memory_with_zero_max_memories(self):
        """Zero max_memories should be handled gracefully."""
        config = AffectiveMemoryConfig(max_memories=0)
        memory = AffectiveMemory(config=config)
        # Should not crash, but memories are immediately pruned
        memory.store_memory(
            user_id="user123",
            interaction_summary="test",
            emotional_state="neutral",
            intensity=0.5,
            relational_phase="initial",
            valence=0.0,
        )
        # Memory pruning should keep it at or near 0
        assert len(memory.memories) <= 1

    def test_very_long_strings(self):
        """Very long strings should be handled."""
        system = FeelingSystem()
        long_text = "test " * 1000  # Very long message
        result = system.process_interaction(
            user_id="user123",
            interaction_text=long_text,
            emotional_signals={},
        )
        assert "timestamp" in result

    def test_unicode_in_strings(self):
        """Unicode characters should be handled properly."""
        system = FeelingSystem()
        result = system.process_interaction(
            user_id="用户123",
            interaction_text="你好世界🌍",
            emotional_signals={},
        )
        assert "timestamp" in result

    def test_numeric_edge_values(self):
        """Numeric edge values (0.0, 1.0) should be handled."""
        memory = AffectiveMemory()
        entry = memory.store_memory(
            user_id="user123",
            interaction_summary="test",
            emotional_state="neutral",
            intensity=0.0,  # Minimum
            relational_phase="initial",
            valence=-1.0,  # Minimum
        )
        assert entry.intensity == 0.0
        assert entry.valence == -1.0

        entry2 = memory.store_memory(
            user_id="user123",
            interaction_summary="test2",
            emotional_state="neutral",
            intensity=1.0,  # Maximum
            relational_phase="initial",
            valence=1.0,  # Maximum
        )
        assert entry2.intensity == 1.0
        assert entry2.valence == 1.0
