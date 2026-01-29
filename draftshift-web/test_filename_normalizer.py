"""
Tests for FilenameNormalizer module.
"""

import unittest
from datetime import datetime, timedelta
from filename_normalizer import FilenameNormalizer


class TestFilenameNormalizer(unittest.TestCase):
    """Test suite for FilenameNormalizer"""

    def setUp(self):
        """Initialize normalizer for each test"""
        self.normalizer = FilenameNormalizer()

    # ========================================================================
    # BASIC NORMALIZATION TESTS
    # ========================================================================

    def test_basic_normalization(self):
        """Test basic filename normalization"""
        result = self.normalizer.normalize(
            filename_original="Declaration of Lead Trial Counsel.docx",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert result["normalized_filename"] == "260128 – DeclLeadCounsel"
        assert result["date_used"] == "2026-01-28T00:00:00"
        assert result["slug_used"] == "DeclLeadCounsel"
        assert result["source_of_date"] == "user_provided"

    def test_notice_removal(self):
        """Test Notice of Removal normalization"""
        result = self.normalizer.normalize(
            filename_original="Notice_of_Removal_FINAL.pdf",
            user_provided_date=datetime(2026, 1, 16)
        )

        assert result["normalized_filename"] == "260116 – NoticeRemoval"
        assert result["slug_used"] == "NoticeRemoval"

    def test_proof_of_service(self):
        """Test Proof of Service normalization"""
        result = self.normalizer.normalize(
            filename_original="POS_electronic_service.docx",
            user_provided_date=datetime(2026, 1, 21)
        )

        assert "ProofService" in result["normalized_filename"]
        assert "260121" in result["normalized_filename"]

    # ========================================================================
    # DATE RESOLUTION TESTS
    # ========================================================================

    def test_date_priority_user_provided(self):
        """User provided date takes highest priority"""
        user_date = datetime(2026, 1, 28)
        created_date = datetime(2026, 1, 1)

        result = self.normalizer.normalize(
            filename_original="test.docx",
            user_provided_date=user_date,
            metadata_created_at=created_date
        )

        assert result["source_of_date"] == "user_provided"
        assert "260128" in result["normalized_filename"]

    def test_date_priority_docket(self):
        """Docket date is second priority"""
        docket_date = datetime(2026, 1, 20)
        created_date = datetime(2026, 1, 1)

        result = self.normalizer.normalize(
            filename_original="test.docx",
            docket_event_date=docket_date,
            metadata_created_at=created_date
        )

        assert result["source_of_date"] == "docket"
        assert "260120" in result["normalized_filename"]

    def test_date_priority_metadata(self):
        """Created date used if no user/docket date"""
        created_date = datetime(2026, 1, 15)

        result = self.normalizer.normalize(
            filename_original="test.docx",
            metadata_created_at=created_date
        )

        assert result["source_of_date"] == "metadata_created"
        assert "260115" in result["normalized_filename"]

    def test_date_fallback_today(self):
        """Falls back to today if no date provided"""
        result = self.normalizer.normalize(
            filename_original="test.docx"
        )

        assert result["source_of_date"] == "fallback_today"
        # Check that it has a valid YYMMDD format
        assert len(result["normalized_filename"]) >= 8

    # ========================================================================
    # SLUG GENERATION TESTS
    # ========================================================================

    def test_slug_dictionary_match(self):
        """Test dictionary-based slug matching"""
        filenames = [
            ("Declaration of Lead Trial Counsel.docx", "DeclLeadCounsel"),
            ("Notice of Removal.pdf", "NoticeRemoval"),
            ("Proof of Electronic Service.docx", "ProofService"),
            ("Scheduling Order.pdf", "SchedulingOrder"),
        ]

        for filename, expected_slug in filenames:
            result = self.normalizer.normalize(
                filename_original=filename,
                user_provided_date=datetime(2026, 1, 28)
            )
            self.assertEqual(result["slug_used"], expected_slug)

    def test_slug_fallback_builder(self):
        """Test fallback slug generation from filename"""
        result = self.normalizer.normalize(
            filename_original="Very Important Legal Document About Stuff.pdf",
            user_provided_date=datetime(2026, 1, 28)
        )

        # Should build slug from meaningful words
        assert "Important" in result["slug_used"] or "Legal" in result["slug_used"]

    def test_slug_confidence_high(self):
        """Test high confidence score for dictionary matches"""
        result = self.normalizer.normalize(
            filename_original="Declaration of Lead Trial Counsel.docx",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert result["slug_confidence"] >= 0.85

    def test_slug_confidence_low_fallback(self):
        """Test lower confidence for fallback slugs"""
        result = self.normalizer.normalize(
            filename_original="xyz123random.pdf",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert result["slug_confidence"] <= 0.5

    def test_user_provided_slug_override(self):
        """User provided slug overrides automatic generation"""
        result = self.normalizer.normalize(
            filename_original="Declaration of Lead Trial Counsel.docx",
            user_provided_slug="CustomSlug",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert result["slug_used"] == "CustomSlug"
        assert result["normalized_filename"] == "260128 – CustomSlug"

    # ========================================================================
    # CONTENT-BASED SLUG TESTS
    # ========================================================================

    def test_slug_from_content(self):
        """Test slug generation from document content"""
        content = """
        DECLARATION OF LEAD TRIAL COUNSEL

        I, John Smith, declare as follows...
        """

        result = self.normalizer.normalize(
            filename_original="document.pdf",
            content_text=content,
            user_provided_date=datetime(2026, 1, 28)
        )

        # Should match from content
        assert "Decl" in result["slug_used"] or "Lead" in result["slug_used"]

    # ========================================================================
    # FILENAME COMPOSITION TESTS
    # ========================================================================

    def test_filename_format(self):
        """Test final filename format"""
        result = self.normalizer.normalize(
            filename_original="test.docx",
            user_provided_date=datetime(2026, 1, 28),
            user_provided_slug="TestSlug"
        )

        # Check format: YYMMDD – Slug
        assert result["normalized_filename"] == "260128 – TestSlug"
        assert "–" in result["normalized_filename"]

    def test_filename_length_limit(self):
        """Test filename length limitation"""
        long_slug = "A" * 100

        result = self.normalizer.normalize(
            filename_original="test.docx",
            user_provided_date=datetime(2026, 1, 28),
            user_provided_slug=long_slug
        )

        # Should be truncated to max 40 chars for slug
        assert len(result["slug_used"]) <= 40
        assert len(result["normalized_filename"]) <= 55  # "260128 – " + 40 char slug

    # ========================================================================
    # CUSTOM DICTIONARY TESTS
    # ========================================================================

    def test_custom_dictionary(self):
        """Test adding custom document mappings"""
        custom = {
            "motion for protective order": "MotProtective"
        }

        normalizer = FilenameNormalizer(custom_dictionary=custom)

        result = normalizer.normalize(
            filename_original="Motion for Protective Order.pdf",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert "MotProtective" in result["slug_used"]

    def test_add_custom_documents(self):
        """Test adding custom documents after initialization"""
        self.normalizer.add_custom_documents({
            "motion for sanctions": "MotSanctions"
        })

        result = self.normalizer.normalize(
            filename_original="Motion for Sanctions.pdf",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert "MotSanctions" in result["slug_used"]

    def test_jurisdiction_registration(self):
        """Test jurisdiction-specific document registration"""
        self.normalizer.register_jurisdiction(
            "federal",
            {"notice of intent to sue": "FedNoticeIntent"}
        )

        result = self.normalizer.normalize(
            filename_original="[federal] Notice of Intent to Sue.pdf",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert "Federal" in result["slug_used"] or "Intent" in result["slug_used"]

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_empty_filename(self):
        """Handle empty filename gracefully"""
        result = self.normalizer.normalize(
            filename_original="",
            user_provided_date=datetime(2026, 1, 28)
        )

        assert result["slug_used"] == "Document"

    def test_special_characters_in_filename(self):
        """Handle special characters in filename"""
        result = self.normalizer.normalize(
            filename_original="@#$%Declaration&*()of Lead.pdf",
            user_provided_date=datetime(2026, 1, 28)
        )

        # Should still extract and match
        assert "Decl" in result["slug_used"] or "Lead" in result["slug_used"]

    def test_multiple_extensions(self):
        """Handle multiple file extensions"""
        result = self.normalizer.normalize(
            filename_original="Document.backup.old.docx",
            user_provided_date=datetime(2026, 1, 28),
            user_provided_slug="Test"
        )

        assert result["slug_used"] == "Test"

    # ========================================================================
    # DATE EXTRACTION TESTS
    # ========================================================================

    def test_extract_date_mmddyyyy(self):
        """Test extracting date in MM/DD/YYYY format"""
        content = "Filed on 01/28/2026 by counsel"

        result = self.normalizer.normalize(
            filename_original="test.pdf",
            content_text=content,
            user_provided_slug="Test"
        )

        assert result["source_of_date"] == "extracted"
        assert "260128" in result["normalized_filename"]

    def test_extract_date_yyyymmdd(self):
        """Test extracting date in YYYY-MM-DD format"""
        content = "Document dated 2026-01-28"

        result = self.normalizer.normalize(
            filename_original="test.pdf",
            content_text=content,
            user_provided_slug="Test"
        )

        assert result["source_of_date"] == "extracted"
        assert "260128" in result["normalized_filename"]


if __name__ == "__main__":
    unittest.main()
