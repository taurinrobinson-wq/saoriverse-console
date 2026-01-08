"""Tests for Response Templates Module."""

import pytest
from emotional_os.core.firstperson.response_templates import (
    ResponseTemplates,
    get_clarifying_prompt,
    get_frequency_reflection,
    add_custom_clarifier,
    add_custom_reflection,
    Template,
    TemplateBank,
)


class TestTemplateDataclass:
    """Test Template dataclass."""

    def test_template_creation(self):
        """Test creating a template."""
        template = Template(
            text="Sample template",
            category="test",
            weight=1.5,
        )

        assert template.text == "Sample template"
        assert template.category == "test"
        assert template.weight == 1.5
        assert template.times_used == 0

    def test_template_default_values(self):
        """Test template default values."""
        template = Template(
            text="Test",
            category="test",
        )

        assert template.frequency_threshold is None
        assert template.weight == 1.0
        assert template.times_used == 0
        assert template.last_used_at is None


class TestTemplateBank:
    """Test TemplateBank class."""

    def test_bank_creation(self):
        """Test creating a template bank."""
        bank = TemplateBank(name="test_bank")

        assert bank.name == "test_bank"
        assert bank.templates == []
        assert bank.rotation_index == 0

    def test_add_template(self):
        """Test adding templates to bank."""
        bank = TemplateBank(name="test")
        bank.add_template("Template 1")
        bank.add_template("Template 2", weight=2.0)

        assert len(bank.templates) == 2
        assert bank.templates[0].text == "Template 1"
        assert bank.templates[1].weight == 2.0

    def test_get_next_template_rotation(self):
        """Test round-robin rotation."""
        bank = TemplateBank(name="test")
        bank.add_template("Template 1")
        bank.add_template("Template 2")
        bank.add_template("Template 3")

        # Should cycle through templates
        t1 = bank.get_next_template(use_rotation=True)
        t2 = bank.get_next_template(use_rotation=True)
        t3 = bank.get_next_template(use_rotation=True)
        t4 = bank.get_next_template(use_rotation=True)  # Should wrap around

        assert t1.text == "Template 1"
        assert t2.text == "Template 2"
        assert t3.text == "Template 3"
        assert t4.text == "Template 1"  # Back to start

    def test_get_next_template_empty_bank(self):
        """Test getting template from empty bank."""
        bank = TemplateBank(name="empty")
        template = bank.get_next_template()

        assert template is None

    def test_get_next_template_weighted_random(self):
        """Test weighted random selection."""
        bank = TemplateBank(name="test")
        bank.add_template("Common", weight=10.0)
        bank.add_template("Rare", weight=0.1)

        # Run multiple selections and check distribution
        selections = []
        for _ in range(100):
            template = bank.get_next_template(use_rotation=False)
            selections.append(template.text)

        # Common should appear more often
        common_count = selections.count("Common")
        rare_count = selections.count("Rare")

        assert common_count > rare_count


class TestResponseTemplates:
    """Test ResponseTemplates class."""

    @pytest.fixture
    def templates(self):
        """Create a ResponseTemplates instance."""
        return ResponseTemplates()

    def test_initialization(self, templates):
        """Test initialization of template banks."""
        assert templates.pronoun_clarifiers is not None
        assert templates.temporal_clarifiers is not None
        assert templates.combined_clarifiers is not None
        assert templates.low_freq_reflections is not None
        assert templates.medium_freq_reflections is not None
        assert templates.high_freq_reflections is not None
        assert templates.very_high_freq_reflections is not None

    def test_pronoun_clarifiers_populated(self, templates):
        """Test that pronoun clarifier bank is populated."""
        assert len(templates.pronoun_clarifiers.templates) > 0

    def test_temporal_clarifiers_populated(self, templates):
        """Test that temporal clarifier bank is populated."""
        assert len(templates.temporal_clarifiers.templates) > 0

    def test_combined_clarifiers_populated(self, templates):
        """Test that combined clarifier bank is populated."""
        assert len(templates.combined_clarifiers.templates) > 0

    def test_get_clarifying_prompt_pronoun(self, templates):
        """Test getting pronoun clarifying prompt."""
        prompt = templates.get_clarifying_prompt("pronoun")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "?" in prompt  # Should be a question

    def test_get_clarifying_prompt_temporal(self, templates):
        """Test getting temporal clarifying prompt."""
        prompt = templates.get_clarifying_prompt("temporal")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "?" in prompt

    def test_get_clarifying_prompt_combined(self, templates):
        """Test getting combined clarifying prompt."""
        prompt = templates.get_clarifying_prompt("combined")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "?" in prompt

    def test_get_clarifying_prompt_rotation(self, templates):
        """Test that rotation produces different prompts."""
        prompts = []
        for _ in range(5):
            prompt = templates.get_clarifying_prompt(
                "pronoun", use_rotation=True)
            prompts.append(prompt)

        # Should have at least 2 different prompts in 5 calls
        unique_prompts = len(set(prompts))
        assert unique_prompts >= 2

    def test_get_frequency_reflection_low(self, templates):
        """Test reflection for low frequency (2)."""
        reflection = templates.get_frequency_reflection(2, "family_conflict")

        assert isinstance(reflection, str)
        assert "family_conflict" in reflection
        assert "?" in reflection

    def test_get_frequency_reflection_medium(self, templates):
        """Test reflection for medium frequency (3)."""
        reflection = templates.get_frequency_reflection(3, "work_stress")

        assert isinstance(reflection, str)
        assert "work_stress" in reflection

    def test_get_frequency_reflection_high(self, templates):
        """Test reflection for high frequency (4)."""
        reflection = templates.get_frequency_reflection(4, "anxiety")

        assert isinstance(reflection, str)
        assert "anxiety" in reflection

    def test_get_frequency_reflection_very_high(self, templates):
        """Test reflection for very high frequency (5+)."""
        reflection = templates.get_frequency_reflection(6, "grief_loss")

        assert isinstance(reflection, str)
        assert "grief_loss" in reflection

    def test_add_custom_clarifier(self, templates):
        """Test adding custom clarifier."""
        original_count = len(templates.pronoun_clarifiers.templates)
        templates.add_custom_clarifier(
            "pronoun", "Who are you talking about specifically?")

        assert len(templates.pronoun_clarifiers.templates) == original_count + 1

    def test_add_custom_reflection(self, templates):
        """Test adding custom reflection."""
        original_count = len(templates.low_freq_reflections.templates)
        templates.add_custom_reflection(2, "There's a pattern with {theme}.")

        assert len(templates.low_freq_reflections.templates) == original_count + 1

    def test_usage_tracking(self, templates):
        """Test that usage is tracked."""
        assert len(templates.usage_history) == 0

        templates.get_clarifying_prompt("pronoun")
        assert len(templates.usage_history) == 1

        templates.get_frequency_reflection(3, "anxiety")
        assert len(templates.usage_history) == 2

    def test_get_usage_statistics(self, templates):
        """Test getting usage statistics."""
        templates.get_clarifying_prompt("pronoun")
        templates.get_frequency_reflection(3, "work_stress")

        stats = templates.get_usage_statistics()

        assert stats["total_uses"] == 2
        assert "response_types" in stats
        assert stats["response_types"]["clarifier"] == 1
        assert stats["response_types"]["reflection"] == 1

    def test_usage_history_size_limit(self, templates):
        """Test that usage history is capped."""
        # Add more than 1000 entries
        for i in range(1500):
            templates.get_clarifying_prompt("pronoun")

        # Should be capped at 1000
        assert len(templates.usage_history) <= 1000


class TestResponseTemplatesModuleLevelFunctions:
    """Test module-level functions."""

    def test_get_clarifying_prompt_function(self):
        """Test module-level get_clarifying_prompt."""
        prompt = get_clarifying_prompt("pronoun")

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_get_frequency_reflection_function(self):
        """Test module-level get_frequency_reflection."""
        reflection = get_frequency_reflection(3, "work_stress")

        assert isinstance(reflection, str)
        assert "work_stress" in reflection

    def test_add_custom_clarifier_function(self):
        """Test module-level add_custom_clarifier."""
        # Should not raise exception
        add_custom_clarifier("pronoun", "Custom clarifier?")
        assert True

    def test_add_custom_reflection_function(self):
        """Test module-level add_custom_reflection."""
        # Should not raise exception
        add_custom_reflection(2, "Custom reflection with {theme}.")
        assert True


class TestResponseTemplatesVariety:
    """Test variety and non-repetition in templates."""

    def test_pronoun_prompt_variety(self):
        """Test that pronoun prompts have variety."""
        templates = ResponseTemplates()
        prompts = []

        for _ in range(len(templates.pronoun_clarifiers.templates)):
            prompt = templates.get_clarifying_prompt(
                "pronoun", use_rotation=True)
            prompts.append(prompt)

        # Should have all different prompts in one cycle
        unique_prompts = len(set(prompts))
        assert unique_prompts == len(prompts)

    def test_reflection_variety_by_frequency(self):
        """Test that reflections vary by frequency level."""
        templates = ResponseTemplates()

        r2 = templates.get_frequency_reflection(2, "anxiety")
        r3 = templates.get_frequency_reflection(3, "anxiety")
        r4 = templates.get_frequency_reflection(4, "anxiety")
        r5 = templates.get_frequency_reflection(5, "anxiety")

        # Different frequency levels might produce same template due to rotation,
        # but should all contain the theme
        assert "anxiety" in r2
        assert "anxiety" in r3
        assert "anxiety" in r4
        assert "anxiety" in r5


class TestResponseTemplatesEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_signal_type(self):
        """Test handling of invalid signal type."""
        templates = ResponseTemplates()
        prompt = templates.get_clarifying_prompt("invalid_signal_type")

        # Should return fallback prompt
        assert prompt == "Could you clarify that for me?"

    def test_empty_theme_name(self):
        """Test reflection with empty theme."""
        templates = ResponseTemplates()
        reflection = templates.get_frequency_reflection(3, "")

        assert isinstance(reflection, str)

    def test_frequency_zero(self):
        """Test reflection with frequency 0."""
        templates = ResponseTemplates()
        reflection = templates.get_frequency_reflection(0, "anxiety")

        # Should default to low frequency
        assert isinstance(reflection, str)

    def test_frequency_one(self):
        """Test reflection with frequency 1."""
        templates = ResponseTemplates()
        reflection = templates.get_frequency_reflection(1, "work_stress")

        # Should default to low frequency (2)
        assert isinstance(reflection, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
