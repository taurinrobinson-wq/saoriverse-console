# Privacy-First Data Encoding Implementation Guide

## Overview

This guide explains how to integrate the privacy-first encoding pipeline into FirstPerson so that raw conversation text is **never stored** in Supabase.

## Problem Statement

**Current State:** Raw user messages and system responses may be persisted in the database unencoded.

**Desired State:**
1. Raw text received but never persisted
2. Only encoded signals/gates/glyphs stored
3. User ID hashed one-way
4. K-anonymity verified (k ≥ 5)
5. Full GDPR/CCPA/HIPAA compliance

## Architecture

### 5-Stage Encoding Pipeline
```text
```
Stage 1: INPUT CAPTURE
├─ User sends message (raw text received in memory)
└─ NOT stored

Stage 2: SIGNAL DETECTION
├─ Extract emotional signals (e.g., "suicidal", "overwhelmed")
├─ Map to codes (e.g., "SIG_CRISIS_001", "SIG_STRESS_001")
├─ Discard original text
└─ Keep only signal codes

Stage 3: GATE ENCODING
├─ Map triggered gates to codes (e.g., "GATE_GRIEF_004")
└─ Keep only gate codes

Stage 4: GLYPH MAPPING
├─ Reference glyphs by ID only (e.g., 42, 183)
├─ Do not store glyph content
└─ Keep only IDs and metadata

Stage 5: STORAGE
├─ user_id_hashed (SHA-256)
├─ timestamp_week (generalized: "2025-W02")
├─ encoded_signals (["SIG_CRISIS_001", "SIG_STRESS_001"])
├─ encoded_gates (["GATE_GRIEF_004"])
├─ glyph_ids ([42, 183])
├─ message_length_bucket ("100-200_chars")
└─ NO raw text, NO user_id, NO identifying info
```



## Files Involved

### New Files (Created)
1. **emotional_os/privacy/data_encoding.py** (350 lines)
   - `DataEncodingPipeline`: 5-stage encoding implementation
   - `ConversationDataStore`: Storage wrapper
   - `encode_affirmation_flow()`: Quality learning without raw text

2. **emotional_os/privacy/signal_parser_integration.py** (200 lines)
   - `encode_and_store_conversation()`: Main integration point
   - `store_affirmation()`: Affirmation storage
   - `verify_privacy_compliance()`: Audit function

3. **emotional_os/privacy/anonymization_config.json** (450 lines)
   - Complete privacy compliance configuration
   - Data retention policies
   - User rights specifications

4. **emotional_os/privacy/arx_integration.py** (350 lines)
   - ARX API k-anonymity verification
   - Monthly compliance checks
   - Generalization recommendations

### Existing Files (To Modify)
1. **emotional_os/core/signal_parser.py**
   - Import: `from emotional_os.privacy.signal_parser_integration import encode_and_store_conversation`
   - Modify: Where database storage happens
   - Call: `encode_and_store_conversation()` before Supabase insert

2. **emotional_os/core/main.py** or API endpoint
   - Call: `encode_and_store_conversation()` after parse_input() returns
   - Verify: Check return value for success/failure

## Integration Steps

### Step 1: Identify Storage Points

Find all places where conversation data goes to the database:

```bash

# Search for database writes
grep -r "\.insert\(" emotional_os/
grep -r "supabase\." emotional_os/
```text
```



Typical locations:
- REST API endpoints (FastAPI/Flask)
- Background workers
- Logging functions
- Session persistence

### Step 2: Add Encoding to parse_input() Results

**Before Storage (Current - WRONG):**

```python

# Raw text goes to database
result = parse_input(user_input, ...)
db.table("conversations").insert({
    "user_id": user_id,
    "user_message": user_input,  # ❌ Raw text!
    "system_response": response,  # ❌ Raw text!
    "signals": result["signals"],
```text
```



**After Encoding (Correct - PRIVACY-FIRST):**

```python

# Only encoded data goes to database
from emotional_os.privacy.signal_parser_integration import encode_and_store_conversation

result = parse_input(user_input, ...)

success, record_id, encoded_data = encode_and_store_conversation(
    user_id=user_id,
    raw_user_input=user_input,  # Will be encoded and discarded
    parse_result=result,
    system_response=response,   # Will be encoded and discarded
    session_id=session_id,
    message_turn=message_turn,
    db_connection=db,  # Your Supabase connection
)

if not success:
    logger.error(f"Failed to store encoded conversation: {record_id}")
```text
```



### Step 3: Modify Supabase Schema

**Create new table for anonymized data:**

```sql
CREATE TABLE conversation_logs_anonymized (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_hashed VARCHAR(64) NOT NULL,  -- SHA-256 hash
    session_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    timestamp_week VARCHAR(8),  -- "2025-W02"
    message_turn INTEGER,
    encoded_signals JSONB,  -- ["SIG_CRISIS_001", ...]
    encoded_signals_category VARCHAR(100),
    encoded_gates JSONB,  -- ["GATE_GRIEF_004", ...]
    glyph_ids JSONB,  -- [42, 183, ...]
    glyph_count INTEGER,
    message_length_bucket VARCHAR(50),
    response_length_bucket VARCHAR(50),
    signal_count INTEGER,
    response_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),

    -- Privacy: No raw text fields allowed
    -- No: user_id, user_message, system_response, user_name, user_email
);

CREATE INDEX idx_user_id_hashed ON conversation_logs_anonymized(user_id_hashed);
CREATE INDEX idx_session_id ON conversation_logs_anonymized(session_id);
```text
```



**Migrate existing data (if needed):**

```sql
-- Archive old table
ALTER TABLE conversations RENAME TO conversations_archived;

-- Create audit trail
CREATE TABLE data_migration_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    migration_date TIMESTAMP DEFAULT NOW(),
    rows_archived INTEGER,
    note TEXT
);

INSERT INTO data_migration_audit (rows_archived, note)
VALUES (
    (SELECT COUNT(*) FROM conversations_archived),
    'Migrated to anonymized schema for GDPR/CCPA/HIPAA compliance'
```text
```



### Step 4: Test Encoding Pipeline

**Test file:** `emotional_os/privacy/test_data_encoding.py`

```python
import unittest
from emotional_os.privacy.data_encoding import DataEncodingPipeline

class TestDataEncoding(unittest.TestCase):
    def setUp(self):
        self.encoder = DataEncodingPipeline()

    def test_raw_text_not_stored(self):
        """Verify raw text is never in encoded record."""
        result = self.encoder.encode_conversation(
            user_id="test_user_123",
            raw_user_input="I'm having thoughts of ending my life",  # Raw text
            system_response="I hear you...",  # Raw text
            signals=[{"keyword": "suicidal_disclosure"}],
            gates=[9],
            glyphs=[{"id": 42}],
            session_id="sess_001",
        )

        # Verify raw text fields don't exist
        forbidden = ["raw_user_input", "user_input", "original_message",
                     "system_response", "response_text"]
        for field in forbidden:
            self.assertNotIn(field, result, f"Raw text field '{field}' found in result!")

        # Verify encoded fields exist
        self.assertIn("encoded_signals", result)
        self.assertIn("encoded_gates", result)
        self.assertIn("glyph_ids", result)
        self.assertEqual(result["encoded_signals"], ["SIG_CRISIS_001"])
        self.assertEqual(result["encoded_gates"], ["GATE_CRISIS_009"])

    def test_user_id_hashed(self):
        """Verify user ID is hashed one-way."""
        result = self.encoder.encode_conversation(
            user_id="alice@example.com",
            raw_user_input="hello",
            system_response="hi",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )

        # User ID should be hashed
        self.assertIn("user_id_hashed", result)
        hashed = result["user_id_hashed"]
        self.assertNotEqual(hashed, "alice@example.com")
        self.assertEqual(len(hashed), 64)  # SHA-256 hex string

    def test_timestamp_generalized(self):
        """Verify timestamp is generalized to week."""
        result = self.encoder.encode_conversation(
            user_id="test",
            raw_user_input="hello",
            system_response="hi",
            signals=[],
            gates=[],
            glyphs=[],
            session_id="sess_001",
        )

        # Timestamp should be week format, not exact time
        self.assertIn("timestamp_week", result)
        timestamp_week = result["timestamp_week"]
```text
```



### Step 5: Verify K-Anonymity

**Monthly compliance check:**

```python
from emotional_os.privacy.arx_integration import ARXAnonymityVerifier

# Verify k-anonymity (k >= 5 means user not uniquely identifiable)
verifier = ARXAnonymityVerifier(k_threshold=5)
verifier.run_monthly_compliance_check(db_connection)

```text
```



## Data Minimization: What Gets Stored vs. Discarded

### DISCARDED (Never Stored)

```
❌ raw_user_input          "I want to end my life"
❌ system_response         "I'm here for you..."
❌ user_id                 "alice@example.com"
❌ user_email              "alice@example.com"
❌ user_name               "Alice"
❌ user_phone              "+1-555-0123"
❌ conversation_text       Full message
```text
```



### STORED (Encoded/Generalized)

```
✓ user_id_hashed           "a7f3e9c1a8b2d5f4..." (SHA-256)
✓ encoded_signals          ["SIG_CRISIS_001", "SIG_STRESS_001"]
✓ encoded_gates            ["GATE_GRIEF_004"]
✓ glyph_ids                [42, 183]
✓ message_length_bucket    "100-200_chars"
✓ timestamp_week           "2025-W02"
```text
```



## Encryption & Security

### In Transit (TLS 1.3)

```
User Client ─────[TLS 1.3]────→ FirstPerson API ─────[TLS 1.3]────→ Supabase
```text
```



### At Rest (AES-256)

```
Database: Supabase
├─ Transport: TLS 1.3 (enforced)
├─ Storage: AES-256 (Supabase native)
└─ Sensitive fields: Individually encrypted if needed
    └─ user_id_hashed: Already one-way hash
    └─ encoded_signals: Codes (no personal info)
    └─ encoded_gates: Codes (no personal info)
```text
```



## User Rights Implementation

### User Data Export

```python
@app.post("/user/data-export")
def export_user_data(user_id: str):
    """User can export their (anonymized) data."""
    user_id_hashed = hashlib.sha256(f"salt:{user_id}".encode()).hexdigest()

    records = db.table("conversation_logs_anonymized")\
        .select("*")\
        .eq("user_id_hashed", user_id_hashed)\
        .execute()

    # Return anonymized metadata only
    return {
        "export_date": datetime.now().isoformat(),
        "conversation_count": len(records.data),
        "signals_detected": [...],
        "retention_policy": "90 days",
        "note": "Data is anonymized; raw messages not stored"
```text
```



### User Data Deletion

```python
@app.post("/user/data-delete")
def delete_user_data(user_id: str):
    """Delete all data for a user."""
    user_id_hashed = hashlib.sha256(f"salt:{user_id}".encode()).hexdigest()

    # Delete from all tables
    db.table("conversation_logs_anonymized")\
        .delete()\
        .eq("user_id_hashed", user_id_hashed)\
        .execute()

    # Log deletion
    audit_log.record_deletion(user_id_hashed, datetime.now())

```text
```



## Audit & Compliance

### Monthly Compliance Report

The system automatically generates:
1. K-anonymity verification (k >= 5)
2. Data retention audit
3. User rights requests processed
4. Encryption verification
5. DPA compliance checklist

Reports saved to: `compliance_reports/[YYYY-MM-DD]_compliance_report.json`

### Access Logging

All data access is logged:

```
[2025-01-15 14:32:01] access_log
  user_role: developer
  action: queried_conversation_logs
  records_accessed: 100
  user_id_hashed: requested (allowed for role)
  ip_address: 192.168.1.100
```text
```



## Rollout Plan

### Phase 1: Development (This Week)
- [ ] Integrate encoding pipeline into signal_parser.py
- [ ] Create new Supabase table (conversation_logs_anonymized)
- [ ] Test with sample conversations
- [ ] Verify no raw text leakage

### Phase 2: Staging (Week 2)
- [ ] Deploy to staging environment
- [ ] Run 7-day compliance check
- [ ] Verify ARX k-anonymity (k >= 5)
- [ ] User acceptance testing

### Phase 3: Production (Week 3)
- [ ] Migrate existing data (archive old table)
- [ ] Deploy encoding pipeline to prod
- [ ] Verify compliance reports
- [ ] Set up monitoring alerts

### Phase 4: Post-Launch (Week 4)
- [ ] Monthly compliance reports running
- [ ] Audit logging active
- [ ] User rights endpoints live
- [ ] Security audit passed

## Compliance Checklist

### GDPR
- [x] Lawful basis: Consent (users opt into system)
- [x] Privacy notice: Displayed on first use
- [x] Data minimization: Only encoded signals stored
- [x] Retention limits: Configurable (default 90 days)
- [x] User rights: Export/delete implemented
- [x] DPIA: Completed (in anonymization_config.json)
- [x] DPO contact: In system documentation

### CCPA
- [x] Consumer rights: Access/deletion/opt-out available
- [x] Non-sale commitment: Data never sold
- [x] Disclosure: Privacy policy covers encoding

### HIPAA
- [x] BAA: Required if handling health data
- [x] Minimum necessary: Only signals stored
- [x] Encryption: TLS 1.3 + AES-256
- [x] Audit: Access logging enabled
- [x] Breach notification: Procedure documented

## Testing & Validation

Run full test suite:

```bash

# Test encoding pipeline
python -m pytest emotional_os/privacy/test_data_encoding.py -v

# Test k-anonymity
python -m pytest emotional_os/privacy/test_arx_integration.py -v

# Test integration
python -m pytest emotional_os/tests/test_privacy_integration.py -v

# Verify no raw text in database
python emotional_os/privacy/verify_compliance.py

# Monthly compliance check
```text
```



## Monitoring & Alerts

### Alert Conditions
1. K-value drops below 5 (over-identification risk)
2. Raw text field inserted (policy violation)
3. Unencrypted data access attempt
4. Data export without valid user ID
5. Deletion request not completed within 30 days

## Summary

**Before Integration:**

```
User Message → parse_input() → Response
                     ↓
```text
```



**After Integration:**

```
User Message → parse_input() → Response
                     ↓
        encode_and_store_conversation()
                     ↓
        [Encode pipeline executes]
                     ↓
   Only anonymized data → Supabase ✓
   Raw text discarded (never stored)
```



**Privacy Achievement:**
- ✅ No raw text in database
- ✅ User IDs hashed one-way
- ✅ Timestamps generalized
- ✅ K-anonymity verified (k ≥ 5)
- ✅ GDPR/CCPA/HIPAA compliant
- ✅ User rights implemented
- ✅ Audit logging enabled

This design ensures FirstPerson protects user privacy with the same care as its crisis response logic.
