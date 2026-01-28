"""
Test suite for DraftShift pleadings module.
"""

import pytest
import json
from pathlib import Path
from draftshift.pleadings import (
    Motion,
    Opposition,
    Reply,
    Declaration,
    PleadingFactory,
)


# Fixture for config paths
@pytest.fixture
def config_paths():
    """Return paths to config YAML files."""
    base = Path(__file__).parent
    return {
        "config": str(base / "../formats/california_civil.yaml"),
        "citation": str(base / "../formats/california_civil_citation.yaml"),
    }


# Fixture for loading test data
@pytest.fixture
def motion_data():
    """Load motion.json fixture."""
    fixture_path = Path(__file__).parent / "fixtures/motion.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def opposition_data():
    """Load opposition.json fixture."""
    fixture_path = Path(__file__).parent / "fixtures/opposition.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def reply_data():
    """Load reply.json fixture."""
    fixture_path = Path(__file__).parent / "fixtures/reply.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def declaration_data():
    """Load declaration.json fixture."""
    fixture_path = Path(__file__).parent / "fixtures/declaration.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


# ============================================================
# FACTORY TESTS
# ============================================================
class TestPleadingFactory:
    """Test PleadingFactory instantiation."""

    def test_factory_creates_motion(self, config_paths):
        """Factory should create Motion instance for 'motion' type."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        pleading = factory.create({"type": "motion"})
        assert isinstance(pleading, Motion)

    def test_factory_creates_opposition(self, config_paths):
        """Factory should create Opposition instance for 'opposition' type."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        pleading = factory.create({"type": "opposition"})
        assert isinstance(pleading, Opposition)

    def test_factory_creates_reply(self, config_paths):
        """Factory should create Reply instance for 'reply' type."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        pleading = factory.create({"type": "reply"})
        assert isinstance(pleading, Reply)

    def test_factory_creates_declaration(self, config_paths):
        """Factory should create Declaration instance for 'declaration' type."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        pleading = factory.create({"type": "declaration"})
        assert isinstance(pleading, Declaration)

    def test_factory_raises_on_missing_type(self, config_paths):
        """Factory should raise ValueError if 'type' field missing."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        with pytest.raises(ValueError):
            factory.create({})

    def test_factory_raises_on_unknown_type(self, config_paths):
        """Factory should raise ValueError for unknown pleading type."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        with pytest.raises(ValueError):
            factory.create({"type": "invalid_type"})


# ============================================================
# MOTION TESTS
# ============================================================
class TestMotion:
    """Test Motion class."""

    def test_motion_build_creates_document(self, config_paths, motion_data, tmp_path):
        """Motion.build() should create a valid DOCX document."""
        motion = Motion(config_paths["config"], config_paths["citation"])
        motion.build(motion_data)
        
        # Save and verify file exists
        output = tmp_path / "test_motion.docx"
        motion.save(str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0

    def test_motion_includes_notice(self, config_paths, motion_data, tmp_path):
        """Motion with notice section should build successfully."""
        assert "notice" in motion_data
        
        motion = Motion(config_paths["config"], config_paths["citation"])
        motion.build(motion_data)
        
        output = tmp_path / "motion_with_notice.docx"
        motion.save(str(output))
        
        assert output.exists()


# ============================================================
# OPPOSITION TESTS
# ============================================================
class TestOpposition:
    """Test Opposition class."""

    def test_opposition_build_creates_document(self, config_paths, opposition_data, tmp_path):
        """Opposition.build() should create a valid DOCX document."""
        opposition = Opposition(config_paths["config"], config_paths["citation"])
        opposition.build(opposition_data)
        
        output = tmp_path / "test_opposition.docx"
        opposition.save(str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0


# ============================================================
# REPLY TESTS
# ============================================================
class TestReply:
    """Test Reply class."""

    def test_reply_build_creates_document(self, config_paths, reply_data, tmp_path):
        """Reply.build() should create a valid DOCX document."""
        reply = Reply(config_paths["config"], config_paths["citation"])
        reply.build(reply_data)
        
        output = tmp_path / "test_reply.docx"
        reply.save(str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0


# ============================================================
# DECLARATION TESTS
# ============================================================
class TestDeclaration:
    """Test Declaration class."""

    def test_declaration_build_creates_document(self, config_paths, declaration_data, tmp_path):
        """Declaration.build() should create a valid DOCX document."""
        declaration = Declaration(config_paths["config"], config_paths["citation"])
        declaration.build(declaration_data)
        
        output = tmp_path / "test_declaration.docx"
        declaration.save(str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0

    def test_declaration_includes_attestation(self, config_paths, declaration_data):
        """Declaration should include mandatory attestation as paragraph 1."""
        declaration = Declaration(config_paths["config"], config_paths["citation"])
        declaration.build(declaration_data)
        
        # Check that document has paragraphs
        assert len(declaration.doc.paragraphs) > 0
        
        # First numbered paragraph should contain attestation
        paragraphs_text = [p.text for p in declaration.doc.paragraphs]
        attestation_found = any("personal knowledge" in p for p in paragraphs_text)
        assert attestation_found


# ============================================================
# INTEGRATION TESTS
# ============================================================
class TestIntegration:
    """Integration tests for full workflow."""

    def test_build_all_pleading_types(self, config_paths, motion_data, opposition_data, reply_data, declaration_data, tmp_path):
        """Should successfully build all four pleading types."""
        test_data = [
            (Motion, motion_data, "motion.docx"),
            (Opposition, opposition_data, "opposition.docx"),
            (Reply, reply_data, "reply.docx"),
            (Declaration, declaration_data, "declaration.docx"),
        ]
        
        for pleading_class, data, filename in test_data:
            pleading = pleading_class(config_paths["config"], config_paths["citation"])
            pleading.build(data)
            
            output = tmp_path / filename
            pleading.save(str(output))
            
            assert output.exists(), f"Failed to create {filename}"
            assert output.stat().st_size > 0, f"{filename} is empty"

    def test_factory_workflow(self, config_paths, motion_data, tmp_path):
        """Factory workflow: create -> build -> save."""
        factory = PleadingFactory(config_paths["config"], config_paths["citation"])
        
        # Create pleading via factory
        pleading = factory.create(motion_data)
        
        # Build document
        pleading.build(motion_data)
        
        # Save output
        output = tmp_path / "factory_motion.docx"
        pleading.save(str(output))
        
        assert output.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
