import json
import os
import time

from local_inference.preprocessor import Preprocessor

SAMPLE_PATH = os.path.join(os.getcwd(), "local_inference", "emotional_taxonomy_sample.json")


def test_determine_escalation_tier1():
    p = Preprocessor(test_mode=True, taxonomy_path=SAMPLE_PATH)
    action, reason = p._determine_escalation(["panic"], 0.9, [])
    assert action == "force_escalation"
    assert reason == "tier_1_detected"


def test_determine_escalation_tier2_cluster_and_confidence():
    p = Preprocessor(test_mode=True, taxonomy_path=SAMPLE_PATH)
    # cluster behavior: default cluster_size == 2 in this Preprocessor implementation
    action_cluster, reason_cluster = p._determine_escalation(["conflict", "longing"], 0.9, [])
    assert action_cluster == "conditional_escalation"
    assert reason_cluster == "cluster_escalation"

    # confidence-based escalation when single tier-2 tag and low confidence
    action_conf, reason_conf = p._determine_escalation(["conflict"], 0.4, [])
    assert action_conf == "conditional_escalation"
    assert reason_conf == "confidence_escalation"


def test_preprocess_and_record_audit_creates_log_entry(tmp_path):
    # Use a Preprocessor instance but override logs_dir to a tmp path for test isolation
    p = Preprocessor(test_mode=True, taxonomy_path=SAMPLE_PATH)
    p.logs_dir = str(tmp_path)
    os.makedirs(p.logs_dir, exist_ok=True)

    # Call record_audit and ensure a log file is written
    payload = {"test": "record_audit_entry", "value": 123}
    p.record_audit(payload)

    # small sleep to allow file write timestamp ordering where FS is delayed
    time.sleep(0.01)

    log_path = os.path.join(p.logs_dir, "preprocessor.log")
    assert os.path.exists(log_path), "preprocessor.log should be created by record_audit"

    # Ensure at least one line contains the kind 'preprocessor_audit'
    found = False
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if "preprocessor_audit" in line:
                found = True
                break
    assert found, "record_audit should write a preprocessor_audit entry"


def test_pii_redaction_and_edits():
    p = Preprocessor(test_mode=True, taxonomy_path=SAMPLE_PATH)
    sample = "Call me at +1 (555) 123-4567 or email john.doe@example.com. SSN 123-45-6789"
    redacted, edits = p._pii_redact(sample)

    # Check redaction placeholders
    assert "[REDACTED_PHONE]" in redacted or "[REDACTED_EMAIL]" in redacted or "[REDACTED_SSN]" in redacted
    # Ensure edits capture at least one redaction label
    assert any(e.startswith("redacted_") for e in edits)


def test_lexical_emotional_tags_and_normalization():
    p = Preprocessor(test_mode=True, taxonomy_path=SAMPLE_PATH)
    text = "I feel joy and happy about this reunion"
    raw_tags = p._lexical_emotional_tags(text)
    norm = p._normalize_tags(raw_tags)

    # Using the sample taxonomy, 'joy' should map to canonical 'joy'
    assert "joy" in norm


def test_preprocess_end_to_end_sanitization_and_escalation(tmp_path):
    p = Preprocessor(test_mode=True, taxonomy_path=SAMPLE_PATH)
    # Isolate logs
    p.logs_dir = str(tmp_path)
    os.makedirs(p.logs_dir, exist_ok=True)

    user_text = "Hi, contact me at alice@example.com. I'm feeling conflict and longing right now."
    result = p.preprocess(user_text)

    # Sanitization
    assert "[REDACTED_EMAIL]" in result.get("sanitized_text", "")
    assert "redacted_email" in result.get("edit_log", [])

    # Tagging
    tags = result.get("emotional_tags", [])
    # Should include canonical tags for conflict and longing
    assert any(t in ("conflict", "longing") for t in tags)

    # Escalation should be triggered by cluster of tier-2 tags (default cluster_size == 2)
    assert result.get("escalation_action") == "conditional_escalation"
    assert result.get("escalation_reason") in ("cluster_escalation", "confidence_escalation")
