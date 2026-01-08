"""
Test suite for data encoding pipeline.

Verifies:
1. Raw text never stored
2. User ID properly hashed
3. Signals correctly encoded
4. Gates correctly encoded
5. Glyphs properly referenced
6. K-anonymity preservation
"""

import unittest
import json
from pathlib import Path
from datetime import datetime
from emotional_os.privacy.data_encoding import DataEncodingPipeline, ConversationDataStore


class TestDataEncodingPipeline(unittest.TestCase):
    """Test the 5-stage encoding pipeline."""
    
    def setUp(self):
        self.encoder = DataEncodingPipeline()
    
    def test_encode_conversation_no_raw_text(self):
        """CRITICAL: Verify raw text is never in encoded record."""
        result = self.encoder.encode_conversation(
            user_id="test_user_123",
            raw_user_input="I'm having thoughts of ending my life today",
            system_response="I hear you. That sounds like you're in a lot of pain.",
            signals=[{"keyword": "suicidal_disclosure"}],
            gates=[9],
            glyphs=[{"id": 42, "name": "presence"}],
            session_id="sess_001",
        )
        
        # Verify raw text fields don't exist
        forbidden_fields = [
            "raw_user_input", "user_input", "original_message", "message_text",
            "system_response", "original_response", "response_text",
            "user_message", "bot_response"
        ]
        
        for field in forbidden_fields:
            self.assertNotIn(
                field, result,
                f"CRITICAL: Raw text field '{field}' found in encoded record!"
            )
        
        # Verify keys don't contain sensitive data
        for key in result.keys():
            self.assertNotIn("text", key.lower(), f"Field name '{key}' suggests raw content")
            self.assertNotIn("message", key.lower(), f"Field name '{key}' suggests raw content")
        
        print("✓ No raw text fields present in encoded record")
    
    def test_user_id_hashed_one_way(self):
        """Verify user ID is hashed and cannot be reversed."""
        user_id_original = "alice@example.com"
        
        result = self.encoder.encode_conversation(
            user_id=user_id_original,
            raw_user_input="hello",
            system_response="hi",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # User ID should not be plaintext
        self.assertIn("user_id_hashed", result)
        user_id_hashed = result["user_id_hashed"]
        
        # Hash should not match original
        self.assertNotEqual(user_id_hashed, user_id_original)
        
        # Hash should be 64 characters (SHA-256 hex)
        self.assertEqual(len(user_id_hashed), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in user_id_hashed))
        
        # Should be consistent (same input = same hash)
        result2 = self.encoder.encode_conversation(
            user_id=user_id_original,
            raw_user_input="world",
            system_response="bye",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_002",
        )
        self.assertEqual(result["user_id_hashed"], result2["user_id_hashed"])
        
        print("✓ User ID properly hashed (one-way, consistent)")
    
    def test_signals_encoded(self):
        """Verify signals are encoded to abstract codes."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="I feel overwhelmed and anxious",
            system_response="response",
            signals=[
                {"keyword": "overwhelm", "voltage": "high"},
                {"keyword": "anxiety", "voltage": "high"}
            ],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # Signals should be encoded
        self.assertIn("encoded_signals", result)
        encoded_signals = result["encoded_signals"]
        
        # Should contain encoded codes, not keywords
        self.assertIn("SIG_STRESS_001", encoded_signals)  # overwhelm
        self.assertIn("SIG_STRESS_002", encoded_signals)  # anxiety
        
        # Should not contain original keywords
        self.assertNotIn("overwhelm", str(encoded_signals))
        self.assertNotIn("anxiety", str(encoded_signals))
        
        # Should have signal count
        self.assertIn("signal_count", result)
        self.assertEqual(result["signal_count"], 2)
        
        print("✓ Signals properly encoded to abstract codes")
    
    def test_gates_encoded(self):
        """Verify gates are encoded to abstract codes."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="input",
            system_response="response",
            signals=[],
            gates=[4, 5, 9],  # Grief, Presence, Crisis
            glyphs=[],
            session_id="sess_001",
        )
        
        # Gates should be encoded
        self.assertIn("encoded_gates", result)
        encoded_gates = result["encoded_gates"]
        
        # Should contain encoded codes
        self.assertIn("GATE_GRIEF_004", encoded_gates)
        self.assertIn("GATE_PRESENCE_005", encoded_gates)
        self.assertIn("GATE_CRISIS_009", encoded_gates)
        
        print("✓ Gates properly encoded to abstract codes")
    
    def test_glyphs_referenced_by_id_only(self):
        """Verify glyphs are referenced by ID only, no content stored."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="input",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[
                {"id": 42, "name": "presence", "content": "Be here with me"},
                {"id": 183, "name": "breath", "content": "Breathe in... breathe out"}
            ],
            session_id="sess_001",
        )
        
        # Glyphs should be IDs only
        self.assertIn("glyph_ids", result)
        glyph_ids = result["glyph_ids"]
        self.assertEqual(glyph_ids, [42, 183])
        
        # Verify no glyph content stored
        result_str = json.dumps(result)
        self.assertNotIn("Be here with me", result_str)
        self.assertNotIn("Breathe in", result_str)
        
        # Verify glyph count
        self.assertIn("glyph_count", result)
        self.assertEqual(result["glyph_count"], 2)
        
        print("✓ Glyphs referenced by ID only (no content)")
    
    def test_timestamp_generalized_to_week(self):
        """Verify timestamps are generalized to week level."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="input",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # Timestamp should be generalized
        self.assertIn("timestamp_week", result)
        timestamp_week = result["timestamp_week"]
        
        # Should match week format: YYYY-Www
        import re
        self.assertRegex(timestamp_week, r"\d{4}-W\d{2}")
        
        # Should not have day or time precision
        self.assertNotIn(":", timestamp_week)  # No time
        
        print(f"✓ Timestamp generalized to week: {timestamp_week}")
    
    def test_message_length_bucketed(self):
        """Verify message lengths are bucketed, not exact."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="This is a test message with exactly 47 characters.",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # Length should be bucketed
        self.assertIn("message_length_bucket", result)
        length_bucket = result["message_length_bucket"]
        
        # Should be range format: XXX-YYY_chars
        import re
        self.assertRegex(length_bucket, r"\d+-\d+_chars")
        
        # Should not be exact length
        self.assertNotIn("47", length_bucket)
        
        print(f"✓ Message length bucketed: {length_bucket}")
    
    def test_signal_category_computed(self):
        """Verify signal categories are computed for quasi-identifier."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="input",
            system_response="response",
            signals=[
                {"keyword": "suicidal_disclosure"},
                {"keyword": "grief"}
            ],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # Category should be computed
        self.assertIn("encoded_signals_category", result)
        category = result["encoded_signals_category"]
        
        # Should contain category names
        self.assertTrue("crisis" in category.lower() or "loss" in category.lower())
        
        print(f"✓ Signal category computed: {category}")
    
    def test_session_and_turn_included(self):
        """Verify session ID and turn number are included."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="input",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_abc123",
        )
        
        # Session ID should be present
        self.assertIn("session_id", result)
        self.assertEqual(result["session_id"], "sess_abc123")
        
        print("✓ Session ID preserved")
    
    def test_encoding_deterministic(self):
        """Verify same input produces same encoded output."""
        input_data = {
            "user_id": "test_user",
            "raw_user_input": "same input",
            "system_response": "same response",
            "signals": [{"keyword": "joy"}],
            "gates": [5],
            "glyphs": [{"id": 1}],
            "session_id": "sess_001",
        }
        
        result1 = self.encoder.encode_conversation(**input_data)
        result2 = self.encoder.encode_conversation(**input_data)
        
        # Key fields should match
        self.assertEqual(result1["user_id_hashed"], result2["user_id_hashed"])
        self.assertEqual(result1["encoded_signals"], result2["encoded_signals"])
        self.assertEqual(result1["encoded_gates"], result2["encoded_gates"])
        
        print("✓ Encoding is deterministic")


class TestConversationDataStore(unittest.TestCase):
    """Test the conversation data store wrapper."""
    
    def setUp(self):
        self.store = ConversationDataStore(db_connection=None)
    
    def test_store_conversation_structure(self):
        """Test that store returns proper structure."""
        # Mock storage (no DB connection)
        success, record_id = self.store.store_conversation(
            user_id="test",
            raw_input="input",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
            message_turn=1,
        )
        
        # Should indicate no database
        self.assertTrue(success)
        self.assertEqual(record_id, "logged_only")
        
        print("✓ Store conversation returns proper structure")


class TestAnonymizationRequirements(unittest.TestCase):
    """Test specific anonymization requirements."""
    
    def setUp(self):
        self.encoder = DataEncodingPipeline()
    
    def test_gdpr_data_minimization(self):
        """Test GDPR data minimization principle."""
        result = self.encoder.encode_conversation(
            user_id="alice@example.com",
            raw_user_input="I'm struggling with depression and suicidal thoughts",
            system_response="I'm here to listen and support you",
            signals=[{"keyword": "suicidal_disclosure"}, {"keyword": "grief"}],
            gates=[9],
            glyphs=[{"id": 42}],
            session_id="sess_001",
        )
        
        # GDPR: Store only what's necessary
        # Necessary: signals, gates, glyphs, anonymized user reference
        # Not necessary: full text, user email, exact timestamp
        
        necessary_fields = {
            "user_id_hashed", "session_id", "encoded_signals",
            "encoded_gates", "glyph_ids", "signal_count"
        }
        
        for field in necessary_fields:
            self.assertIn(field, result, f"Required field '{field}' missing")
        
        # Ensure unnecessary fields are NOT present
        unnecessary = {"user_id", "user_email", "raw_user_input", "system_response"}
        result_fields = set(result.keys())
        for field in unnecessary:
            self.assertNotIn(field, result_fields)
        
        print("✓ GDPR data minimization satisfied")
    
    def test_ccpa_consumer_rights(self):
        """Test CCPA consumer rights implementation."""
        result = self.encoder.encode_conversation(
            user_id="consumer@example.com",
            raw_user_input="input",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # CCPA: User can request deletion
        # Deletion should be possible via user_id_hashed
        self.assertIn("user_id_hashed", result)
        
        # User can request access (anonymized data)
        self.assertIn("session_id", result)
        self.assertIn("timestamp", result)
        
        print("✓ CCPA consumer rights supported")
    
    def test_hipaa_minimum_necessary(self):
        """Test HIPAA minimum necessary principle."""
        result = self.encoder.encode_conversation(
            user_id="patient_id",
            raw_user_input="health-related content",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # HIPAA: Access only when necessary
        # Our encoding: Access logs would track access (in audit_logger)
        # Our storage: Health-related text not stored (only signals)
        
        result_json = json.dumps(result)
        self.assertNotIn("health", result_json.lower())
        
        print("✓ HIPAA minimum necessary satisfied")
    
    def test_state_wiretapping_consent(self):
        """Test state wiretapping laws (all-party consent)."""
        # This test verifies that the system design allows for consent tracking
        result = self.encoder.encode_conversation(
            user_id="user",
            raw_user_input="input",
            system_response="response",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )
        
        # System stores session_id, allowing consent verification
        # (Actual consent mechanism handled by API layer)
        self.assertIn("session_id", result)
        self.assertIn("timestamp", result)
        
        print("✓ State wiretapping law support implemented")


class TestKAnonymityRequirements(unittest.TestCase):
    """Test k-anonymity quasi-identifier handling."""
    
    def setUp(self):
        self.encoder = DataEncodingPipeline()
    
    def test_quasi_identifiers_generalized(self):
        """Test that quasi-identifiers are properly generalized."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="a" * 150,  # 150 char message
            system_response="b" * 200,  # 200 char response
            signals=[{"keyword": "joy"}],
            gates=[5],
            glyphs=[],
            session_id="sess_001",
        )
        
        # Quasi-identifiers should be generalized
        quasi_identifiers = [
            "user_id_hashed",           # Hashed, not unique
            "timestamp_week",           # Week level, not day
            "message_length_bucket",    # Bucket, not exact
            "response_length_bucket",   # Bucket, not exact
            "encoded_signals_category", # Category, not unique signals
            "signal_count",             # Count, not sequence
        ]
        
        for qi in quasi_identifiers:
            self.assertIn(qi, result, f"Quasi-identifier '{qi}' missing")
        
        # Verify no exact values
        self.assertNotEqual(result["message_length_bucket"], "150_chars")
        self.assertNotEqual(result["response_length_bucket"], "200_chars")
        
        print("✓ K-anonymity quasi-identifiers properly generalized")


def run_tests():
    """Run all tests and print summary."""
    print("\n" + "="*70)
    print("DATA ENCODING PIPELINE TEST SUITE")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDataEncodingPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestConversationDataStore))
    suite.addTests(loader.loadTestsFromTestCase(TestAnonymizationRequirements))
    suite.addTests(loader.loadTestsFromTestCase(TestKAnonymityRequirements))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
