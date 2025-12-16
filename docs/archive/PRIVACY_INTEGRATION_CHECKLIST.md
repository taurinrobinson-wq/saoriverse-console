# Privacy Integration Checklist

Use this checklist to track your integration progress.

##

## Pre-Integration (Before You Start)

- [ ] Read PRIVACY_QUICK_REFERENCE.md (5 min)
- [ ] Run `python verify_privacy_encoding.py` and confirm all tests pass
- [ ] Read PRIVACY_DEPLOYMENT_GUIDE.md (20 min)
- [ ] Review IMPLEMENTATION_GUIDE.md data retention section (10 min)

**Estimated Time:** 35 minutes

##

## Phase 1: Preparation (Day 1)

### 1.1 Identify Storage Points

- [ ] Search signal_parser.py for `db.table(` or database operations
- [ ] Search for Supabase insert operations in API layer
- [ ] Document locations where conversations are stored
- [ ] Note: Are there multiple places? (common)

**Checklist:**

```bash
grep -r "\.insert(" emotional_os/core/signal_parser.py
grep -r "supabase\." emotional_os/
grep -r "conversation" emotional_os/core/signal_parser.py
```

- [ ] Create a list: `STORAGE_LOCATIONS.txt`
- [ ] Example format:

  ```
  File: emotional_os/core/signal_parser.py
  Line: 1234
  Code: db.table("conversations").insert({...})

  File: emotional_os/api/main.py
  Line: 567
  Code: db.table("conversations").insert({...})
  ```

**Estimated Time:** 30 minutes

### 1.2 Verify You Have All Files

- [ ] Confirm `emotional_os/privacy/data_encoding.py` exists
- [ ] Confirm `emotional_os/privacy/signal_parser_integration.py` exists
- [ ] Confirm `emotional_os/privacy/arx_integration.py` exists
- [ ] Confirm `emotional_os/privacy/anonymization_config.json` exists

**Estimated Time:** 5 minutes

### 1.3 Set Up Test Environment

- [ ] Clone or create test branch: `git checkout -b privacy-integration`
- [ ] Or create snapshot: backup existing code
- [ ] Plan where to test: staging database recommended

**Estimated Time:** 10 minutes

**Phase 1 Total Time:** ~45 minutes

##

## Phase 2: Code Integration (Day 1-2)

### 2.1 Update First Storage Location

For the **first** location you identified:

- [ ] Open the file containing the storage operation
- [ ] Add import at top of file:

  ```python
  from emotional_os.privacy.signal_parser_integration import encode_and_store_conversation
  ```

- [ ] Find the database insert operation
- [ ] Replace raw storage with encoding wrapper

**Before:**

```python
result = parse_input(user_input, ...)
db.table("conversations").insert({
    "user_id": user_id,
    "user_message": user_input,        # ❌ Raw text
    "system_response": response,       # ❌ Raw text
    "signals": result["signals"],
}).execute()
```

**After:**

```python
result = parse_input(user_input, ...)

success, record_id, _ = encode_and_store_conversation(
    user_id=user_id,
    raw_user_input=user_input,
    parse_result=result,
    system_response=response,
    session_id=session_id or "unknown",
    message_turn=message_turn or 1,
    db_connection=db,
)

if not success:
    logger.error(f"Failed to encode/store conversation: {record_id}")
    # Handle error appropriately
else:
    logger.info(f"Stored encoded conversation: {record_id}")
```

- [ ] Test locally with `python -m pytest emotional_os/privacy/test_data_encoding.py`

**Estimated Time:** 20-30 minutes

### 2.2 Repeat for Other Storage Locations

- [ ] For **each additional** storage location found in Phase 1.1:
  - [ ] Repeat 2.1 process
  - [ ] Test after each change

**Estimated Time:** 15-20 minutes per location

### 2.3 Verify No Regressions

- [ ] Run existing test suite: `python -m pytest emotional_os/` (if available)
- [ ] Test crisis response still works
- [ ] Test glyph selection still works
- [ ] Test signal parsing still works

**Estimated Time:** 15 minutes

**Phase 2 Total Time:** ~1 hour + 15-20 min per additional storage location

##

## Phase 3: Database Schema (Day 2)

### 3.1 Create New Table in Supabase

Execute this SQL in your Supabase SQL editor:

```sql
-- Create anonymized conversation logs table
CREATE TABLE conversation_logs_anonymized (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_hashed VARCHAR(64) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    timestamp_week VARCHAR(8),
    message_turn INTEGER,
    encoded_signals JSONB,
    encoded_signals_category VARCHAR(100),
    encoded_gates JSONB,
    glyph_ids JSONB,
    glyph_count INTEGER,
    message_length_bucket VARCHAR(50),
    response_length_bucket VARCHAR(50),
    signal_count INTEGER,
    response_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_user_id_hashed ON conversation_logs_anonymized(user_id_hashed);
CREATE INDEX idx_session_id ON conversation_logs_anonymized(session_id);
CREATE INDEX idx_timestamp_week ON conversation_logs_anonymized(timestamp_week);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE conversation_logs_anonymized ENABLE ROW LEVEL SECURITY;

-- Create policy: users can only see records with their user_id_hashed
CREATE POLICY "Users can view own conversations"
  ON conversation_logs_anonymized
  FOR SELECT
  USING (user_id_hashed = (
    -- This assumes you hash user_id the same way
    -- Implement actual user ID hashing logic
    encode(digest(auth.uid()::text, 'sha256'), 'hex')
  ));
```

- [ ] Execute SQL
- [ ] Verify table created: Check "Tables" in Supabase dashboard
- [ ] Confirm indexes created: Check "Indexes" section

**Estimated Time:** 10 minutes

### 3.2 Archive Old Data (Optional but Recommended)

```sql
-- Backup old conversations table
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
);
```

- [ ] Execute SQL if you have existing conversations table
- [ ] Verify: Check that old table is renamed
- [ ] Backup: Ensure you have database backup before this step

**Estimated Time:** 5 minutes

### 3.3 Update Connection String

- [ ] Verify your Supabase connection is set to `conversation_logs_anonymized` table
- [ ] Or: Code already uses dynamic table names (check in Phase 2)

**Estimated Time:** 5 minutes

**Phase 3 Total Time:** ~20 minutes

##

## Phase 4: Testing (Day 2)

### 4.1 Local Testing

```bash

# Run privacy encoding tests
python emotional_os/privacy/verify_privacy_encoding.py
```

Expected output:

```
✓ No raw text found in encoded record
✓ User ID properly hashed
✓ All required fields present
READY FOR INTEGRATION
```

- [ ] Verify all tests pass

**Estimated Time:** 5 minutes

### 4.2 Integration Testing (Local)

Create a test script:

```python

# test_integration.py
import sys
sys.path.insert(0, '.')

from emotional_os.core.signal_parser import parse_input
from emotional_os.privacy.signal_parser_integration import encode_and_store_conversation

# Test parse_input with encoding
result = parse_input("I'm overwhelmed and anxious", "...")
print(f"Parse result keys: {result.keys()}")

# Test encoding
success, record_id, encoded = encode_and_store_conversation(
    user_id="test@example.com",
    raw_user_input="I'm overwhelmed and anxious",
    parse_result=result,
    system_response="I understand you're feeling overwhelmed",
    session_id="test_sess_001",
    message_turn=1,
    db_connection=None,  # No DB connection = logging only
)

print(f"Encoding success: {success}")
print(f"Record ID: {record_id}")
print(f"Encoded data keys: {encoded.keys() if encoded else 'None'}")

# Verify no raw text
if encoded:
    encoded_str = str(encoded)
    if "I'm overwhelmed" in encoded_str:
        print("❌ FAIL: Raw text found in encoded record!")
    else:
        print("✓ PASS: No raw text in encoded record")
```

- [ ] Run test script
- [ ] Verify: Success = True
- [ ] Verify: No raw text in output

**Estimated Time:** 10 minutes

### 4.3 Staging Deployment

- [ ] Deploy code changes to staging environment
- [ ] Deploy new Supabase table to staging
- [ ] Run integration test in staging
- [ ] Monitor for errors

**Estimated Time:** 30 minutes

### 4.4 7-Day Compliance Verification

Set up automated check for staging:

```python

# Run daily for 7 days
from emotional_os.privacy.arx_integration import ARXAnonymityVerifier

verifier = ARXAnonymityVerifier(k_threshold=5)
report = verifier.run_monthly_compliance_check(db_staging)

# Check report.k_value >= 5
```

- [ ] Set up for 7 days in staging
- [ ] Verify k ≥ 5 daily
- [ ] Check no errors in logs
- [ ] Review compliance report

**Estimated Time:** 5 min setup, then automated

**Phase 4 Total Time:** ~50 minutes + 7 days staging verification

##

## Phase 5: Production Deployment (Day 5+)

### 5.1 Pre-Deployment Checklist

- [ ] All staging tests passed for 7 days ✓
- [ ] K-anonymity verified (k ≥ 5) ✓
- [ ] No errors in staging logs ✓
- [ ] Backup: Full database backup taken ✓
- [ ] Rollback plan documented ✓
- [ ] Team notified ✓

**Estimated Time:** 15 minutes

### 5.2 Production Deployment

```bash

# 1. Deploy code
git merge privacy-integration
git push origin main

# Wait for CI/CD to complete

# 2. Create table in production

# Execute same SQL from Phase 3.1 on production database

# 3. Verify deployment

# Run final test:
python emotional_os/privacy/verify_privacy_encoding.py

# 4. Monitor

# Watch logs for [ENCODING] messages

# Verify no errors
```

- [ ] Code deployed
- [ ] Database table created in production
- [ ] Verification test passed
- [ ] Team notified

**Estimated Time:** 30 minutes

### 5.3 Post-Deployment Monitoring (24 Hours)

- [ ] Monitor error logs for issues
- [ ] Verify conversations storing to new table
- [ ] Check k-anonymity (run compliance check)
- [ ] Verify no raw text in stored records

```bash

# Monitor:

# 1. Check error logs

# 2. Verify row count increasing in conversation_logs_anonymized

# 3. Run compliance check

# 4. Alert if any issues
```

- [ ] No errors ✓
- [ ] Rows being added ✓
- [ ] K-anonymity verified ✓

**Estimated Time:** 30 minutes daily for 1-3 days

**Phase 5 Total Time:** ~1.5 hours + monitoring

##

## Phase 6: Ongoing Operations (Monthly)

### 6.1 Monthly Compliance Report

Schedule monthly task:

```bash

# First day of each month:
python emotional_os/privacy/arx_integration.py  # Or your runner

# Generates: compliance_reports/[YYYY-MM-DD]_compliance_report.json
```

- [ ] Set up scheduled job
- [ ] Review report
- [ ] Verify k ≥ 5
- [ ] Verify no violations
- [ ] Archive report

**Estimated Time:** 10 minutes monthly

### 6.2 Quarterly Security Audit

- [ ] Review access logs
- [ ] Verify encryption
- [ ] Check user rights requests
- [ ] Update compliance documentation

**Estimated Time:** 30 minutes quarterly

**Phase 6 Total Time:** ~10 min/month + 30 min/quarter

##

## Troubleshooting Checklist

### Issue: TypeError in encode_and_store_conversation

**Solution:**

```python

# Check that parse_result has expected keys:
result = parse_input(...)
assert "signals" in result
assert "gates" in result
assert "glyphs" in result
```

- [ ] Verify parse_input returns expected keys
- [ ] Check signal format

### Issue: No Records in conversation_logs_anonymized

**Debug:**

```sql
-- Check if table exists
SELECT COUNT(*) FROM conversation_logs_anonymized;

-- Check if connection is correct
-- Verify table name in code
```

- [ ] Verify table exists in Supabase
- [ ] Verify db_connection parameter passed
- [ ] Check logs for errors

### Issue: K-Anonymity Below 5

**Possible causes:**

1. Too few users in test environment
2. Too specific quasi-identifiers
3. Bucket sizes too small

**Solutions:**

```python

# Increase test data

# Or adjust bucket sizes in anonymization_config.json

# Or increase k_threshold for testing only
```

- [ ] Check test data volume
- [ ] Review bucket configuration
- [ ] Consult IMPLEMENTATION_GUIDE.md

### Issue: Raw Text Appears in Database

**CRITICAL:** This should not happen.

**Debug:**

```sql
SELECT * FROM conversation_logs_anonymized
WHERE user_id_hashed LIKE '%@%' OR encoded_signals LIKE '%I%';
```

- [ ] Stop all writes immediately
- [ ] Check encoding pipeline
- [ ] Review recent code changes
- [ ] Rollback if needed

##

## Success Verification Checklist

Final verification that everything is working:

- [ ] ✓ Privacy encoding tests pass (`python verify_privacy_encoding.py`)
- [ ] ✓ No raw text in conversation_logs_anonymized table
- [ ] ✓ User ID hashed in all records
- [ ] ✓ K-anonymity ≥ 5 (verified by ARX)
- [ ] ✓ GDPR compliance verified
- [ ] ✓ CCPA compliance verified
- [ ] ✓ HIPAA compliance verified
- [ ] ✓ Crisis response still working
- [ ] ✓ Glyph selection still working
- [ ] ✓ Signal parsing still working
- [ ] ✓ Zero errors in production logs (24 hours)
- [ ] ✓ Monthly compliance report generated
- [ ] ✓ Users can export data
- [ ] ✓ Users can delete data

##

## Time Estimate Summary

| Phase | Task | Time |
|-------|------|------|
| 1 | Preparation | 45 min |
| 2 | Code Integration | 1-2 hours |
| 3 | Database Schema | 20 min |
| 4 | Testing | 50 min + 7 days |
| 5 | Production Deployment | 1.5 hours |
| 6 | Ongoing (Monthly) | 10 min/month |
| **TOTAL** | **Setup** | **~4-5 hours** |

##

## Emergency Rollback (If Needed)

If something goes wrong:

```sql
-- 1. Stop using new table
-- 2. Revert code changes
-- 3. Delete new table
DROP TABLE conversation_logs_anonymized;
DROP TABLE data_migration_audit;

-- 4. Restore old table (if you renamed it)
ALTER TABLE conversations_archived RENAME TO conversations;

-- 5. Deploy previous code version
git revert <commit>
git push origin main
```

- [ ] Code reverted
- [ ] Database reverted
- [ ] Monitoring resumed
- [ ] Incident documented

##

## Sign-Off

When complete, sign off:

- [ ] Privacy integration complete
- [ ] All tests passing
- [ ] Production verified
- [ ] Compliance confirmed
- [ ] Team notified

**Integration Complete Date:** _______________

**Completed By:** _______________

**Verified By:** _______________

##

**Remember:**

- Start with Phase 1 (Preparation)
- Follow phases in order
- Don't skip testing
- Contact support if stuck

**Goal:** FirstPerson protects user privacy from day one. You're almost there! 🔒
