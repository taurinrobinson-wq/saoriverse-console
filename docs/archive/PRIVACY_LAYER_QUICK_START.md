# Privacy Layer Quick Start Checklist

## ✅ Phase 1: Design & Implementation (COMPLETE)

- [x] Design encryption + retention + dream engine architecture
- [x] Implement `EncryptionManager` class (AES-256, PBKDF2)
- [x] Implement `DreamEngine` class (pattern extraction)
- [x] Create database schema with retention support
- [x] Document integration guide with examples
- [x] Create test suite

**Status:** Foundation complete, ready for testing

##

## ⏳ Phase 2: Dependencies & Database (NEXT - 1 hour)

### Step 1: Install Dependencies (5 minutes)

```bash

# Install cryptography for AES-256 encryption
pip install cryptography

# Optional: Install pytest for running tests
pip install pytest
```


**Verify installation:**

```bash
python -c "from cryptography.fernet import Fernet; print('Cryptography installed ✓')"
```


### Step 2: Create Database Tables (25 minutes)

**Connection:** Get your Supabase connection string

**Run these SQL commands:**

```sql
-- 1. User retention preferences (one per user)
CREATE TABLE user_retention_preferences (
    user_id_hashed VARCHAR(64) PRIMARY KEY,
    full_conversation_retention_days INT NOT NULL DEFAULT 30,
    dream_summary_retention_days INT NOT NULL DEFAULT 90,
    allow_export BOOLEAN NOT NULL DEFAULT true,
    allow_archive BOOLEAN NOT NULL DEFAULT true,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 2. Encrypted full conversations
CREATE TABLE conversations_encrypted (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_hashed VARCHAR(64) NOT NULL,
    session_id VARCHAR(255),
    encrypted_content BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    retention_days INT NOT NULL DEFAULT 30,
    FOREIGN KEY (user_id_hashed) REFERENCES user_retention_preferences(user_id_hashed)
);

CREATE INDEX idx_conversations_user_expiration
ON conversations_encrypted(user_id_hashed, expires_at);

-- 3. Encrypted daily dream summaries
CREATE TABLE dream_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_hashed VARCHAR(64) NOT NULL,
    date DATE NOT NULL,
    encrypted_summary BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(user_id_hashed, date),
    FOREIGN KEY (user_id_hashed) REFERENCES user_retention_preferences(user_id_hashed)
);

CREATE INDEX idx_dream_summaries_user_date
ON dream_summaries(user_id_hashed, date);

-- 4. Audit log for compliance
CREATE TABLE audit_log_privacy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_hashed VARCHAR(64) NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    record_count INT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user_action
ON audit_log_privacy(user_id_hashed, action);

-- 5. Daily dream batch (staging, temporary)
CREATE TABLE daily_dream_batch (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_hashed VARCHAR(64) NOT NULL,
    date DATE NOT NULL,
    batch_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id_hashed, date)
);
```


**Verify tables created:**

```bash

# In Supabase console, check that all 5 tables exist

# - user_retention_preferences

# - conversations_encrypted

# - dream_summaries

# - audit_log_privacy

# - daily_dream_batch
```


### Step 3: Run Encryption Tests (15 minutes)

```bash

# Test the EncryptionManager
pytest test_privacy_layer.py::TestEncryptionManager -v

# Expected output: 6 tests passed
```


**If tests fail:**

- Verify cryptography installed: `pip install cryptography --upgrade`
- Check Python version: `python --version` (requires 3.8+)

### Step 4: Run Dream Engine Tests (15 minutes)

```bash

# Test the DreamEngine
pytest test_privacy_layer.py::TestDreamEngine -v

# Expected output: 5 tests passed
```


##

## ⏳ Phase 3: Signal Parser Integration (2-3 hours)

### Step 1: Update Login Flow (1 hour)

**File:** `signal_parser_integration.py`

**Add this class:**

```python
from emotional_os.privacy.encryption_manager import EncryptionManager

class UserAuthenticationManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.encryption = EncryptionManager()

    def login_user(self, user_id: str, password: str) -> dict:
        """
        Login and decrypt user profile + conversations.
        """
        # Derive encryption key
        key = self.encryption.derive_key_from_password(user_id, password)

        # Load and decrypt user profile
        # Load and decrypt recent conversations
        # Load dream summaries

        return {
            'success': True,
            'user_profile': {...},
            'recent_conversations': [...],
            'dream_summaries': [...],
            'greeting': f"Welcome back, {profile['first_name']}!"
        }
```


**See:** `PRIVACY_LAYER_INTEGRATION_GUIDE.md` Section 1

### Step 2: Update Conversation Storage (1 hour)

**File:** `signal_parser_integration.py`

**Add this class:**

```python
class ConversationStorageManager:
    def store_conversation(
        self,
        user_id: str,
        user_id_hashed: str,
        password: str,
        conversation_data: dict,
        encryption_key = None
    ) -> bool:
        """
        Encrypt and store conversation with user's retention setting.
        """
        # Encrypt conversation
        # Store to conversations_encrypted with expiration
        # Add to daily_dream_batch for end-of-day processing
        # Audit log

        return True
```


**See:** `PRIVACY_LAYER_INTEGRATION_GUIDE.md` Section 2

### Step 3: Test Integration (30 minutes)

```python

# test_integration.py
def test_login_and_store():
    manager = UserAuthenticationManager(db)

    # 1. User logs in
    login = manager.login_user("taurin@example.com", "password123")
    assert login['success'] == True
    assert login['greeting'].startswith("Welcome back")

    # 2. Store conversation
    storage = ConversationStorageManager(db, encryption)
    stored = storage.store_conversation(
        user_id="taurin@example.com",
        user_id_hashed=login['user_id_hashed'],
        password="password123",
        conversation_data={...}
    )
    assert stored == True

    # 3. Verify it's encrypted in DB
    # Query DB directly, verify encrypted_content is bytes
    # Can't read it without password
```


##

## ⏳ Phase 4: Scheduled Tasks (1-2 hours)

### Step 1: Create Daily Dream Generation Task

**File:** `scheduled_tasks.py`

```python
from emotional_os.privacy.dream_engine import DreamEngine
from datetime import datetime, timedelta

def generate_daily_dreams():
    """
    Run this daily at 3 AM (off-peak).
    Creates dream summaries from conversations.
    """
    # Get all users with conversations yesterday
    # For each user:
    #   - Retrieve conversations from daily_dream_batch
    #   - Create summary with DreamEngine
    #   - Store encrypted summary
    #   - Clear batch
```


### Step 2: Create Cleanup Task

```python
def cleanup_expired_conversations():
    """Run daily. Delete conversations past retention date."""
    # DELETE FROM conversations_encrypted WHERE expires_at < NOW()
    # DELETE FROM dream_summaries WHERE expires_at < NOW()

def cleanup_deleted_users():
    """Run daily. Permanently delete after grace period."""
    # DELETE FROM conversations_encrypted WHERE user marked deleted 30+ days ago
```


### Step 3: Set Up Scheduler

**Option A: APScheduler (simple)**

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(generate_daily_dreams, 'cron', hour=3, minute=0)
scheduler.add_job(cleanup_expired_conversations, 'cron', hour=4, minute=0)
scheduler.start()
```


**Option B: Celery (production)**

```python
from celery import Celery

app = Celery('firstperson')

@app.task
def generate_daily_dreams():
    # ...

# celery beat schedule
app.conf.beat_schedule = {
    'generate-dreams': {
        'task': 'tasks.generate_daily_dreams',
        'schedule': crontab(hour=3, minute=0),
    }
}
```


##

## ⏳ Phase 5: User API Endpoints (1-2 hours)

### Create User Settings Endpoints

**File:** `api_privacy_endpoints.py`

```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api/user", tags=["privacy"])

@router.get("/retention-settings")
async def get_retention_settings(user_id_hashed: str = Depends(get_current_user)):
    """Show current retention setting."""
    return {"retention_days": 30, "options": [7, 30, 90, 365]}

@router.post("/retention-settings")
async def set_retention_settings(
    user_id_hashed: str = Depends(get_current_user),
    retention_days: int
):
    """Update retention preference."""
    # Validate and save
    return {"success": True, "retention_days": retention_days}

@router.get("/data-export")
async def export_user_data(user_id_hashed: str = Depends(get_current_user)):
    """Download all encrypted user data."""
    # Return ZIP with conversations + metadata
    return {"status": "Ready", "download_url": "..."}

@router.delete("/data-delete")
async def request_data_deletion(user_id_hashed: str = Depends(get_current_user)):
    """GDPR deletion request (30-day grace period)."""
    # Mark for deletion
    return {"status": "Deletion requested", "grace_period_days": 30}

@router.get("/conversation-history")
async def get_history(user_id_hashed: str = Depends(get_current_user)):
    """Browse conversations + dream summaries."""
    # Return recent conversations with dream summaries for older ones
    return [...]
```


##

## ✅ Phase 6: Testing & Launch (2-3 hours)

### Manual End-to-End Test

1. **User signs up**

   ```
   POST /api/auth/signup
   → user_id hashed, profile encrypted, retention pref stored
   ```

2. **User logs in**

   ```
   POST /api/auth/login
   → profile decrypted, conversations loaded
   → greeting shows name
   ```

3. **User has conversation**

   ```
   POST /api/conversation
   → signals extracted, glyphs generated
   → conversation encrypted, stored
   → added to daily batch
   ```

4. **Check encryption (Query DB directly)**

   ```sql
   SELECT encrypted_content FROM conversations_encrypted LIMIT 1;
   -- Returns: \x80236f...d4f (binary, unreadable)
   ```

5. **End of day - Generate dream**

   ```
   TRIGGER: 3 AM scheduled task
   → retrieves daily_dream_batch
   → creates summary
   → stores encrypted summary
   → clears batch
   ```

6. **User browses history**

   ```
   GET /api/user/conversation-history
   → recent encrypted conversations (metadata)
   → older dream summaries (patterns)
   ```

7. **User changes retention to 7 days**

   ```
   POST /api/user/retention-settings
   → new conversations expire in 7 days
   → old conversations keep original expiration
   ```

8. **User exports data**

   ```
   GET /api/user/data-export
   → download ZIP with encrypted conversations
   → user decrypts offline with password
   ```

9. **User deletes account**

   ```
   DELETE /api/user/data-delete
   → marked for deletion, grace period 30 days
   → after 30 days: automatic permanent deletion
   ```

### Load Testing

```bash

# Test encryption/decryption performance
pytest test_privacy_layer.py::TestPerformance -v

# Expected: encrypt/decrypt <100ms per 10KB conversation
```


### Security Review

- [ ] Review encryption_manager.py for key material leaks
- [ ] Verify keys never written to logs/disk
- [ ] Check HTTPS everywhere
- [ ] Verify audit logging working
- [ ] Test GDPR deletion workflow
- [ ] Review database access controls

### Deploy to Staging

```bash
git add emotional_os/privacy/
git add *.md
git add test_privacy_layer.py
git add scheduled_tasks.py
git add api_privacy_endpoints.py
git commit -m "feat: privacy layer with encryption + retention + dreams"
git push origin privacy-layer
```


### User Acceptance Testing

- [ ] Test with real users (staging)
- [ ] Verify personalization working ("Welcome back, [name]!")
- [ ] Verify retention settings working
- [ ] Verify data export working
- [ ] Verify no data in logs/monitoring
- [ ] Gather feedback

### Deploy to Production

- [ ] Run migration on production DB
- [ ] Update API with new endpoints
- [ ] Start scheduled task runner
- [ ] Monitor encryption/decryption performance
- [ ] Monitor audit logs

##

## 📊 Implementation Metrics

| Component | Status | Lines | Tests |
|-----------|--------|-------|-------|
| EncryptionManager | ✅ | 350 | 6 |
| DreamEngine | ✅ | 400 | 5 |
| Database Schema | ✅ | 300 (SQL) | - |
| Integration Guide | ✅ | 400 | - |
| Test Suite | ✅ | 400 | 15 |
| **Total** | | **1850** | **26** |

##

## 📋 Pre-Launch Verification

Before going live, verify:

- [ ] Dependencies installed: `cryptography`, `pytest`
- [ ] Database tables created: 5 tables with correct indices
- [ ] Encryption tests pass: `pytest test_privacy_layer.py::TestEncryptionManager`
- [ ] Dream engine tests pass: `pytest test_privacy_layer.py::TestDreamEngine`
- [ ] Integration tests pass: `pytest test_privacy_layer.py::TestIntegration`
- [ ] Login decrypts profile correctly
- [ ] Conversations store encrypted
- [ ] Daily dreams generate (3 AM task)
- [ ] Cleanup removes expired (4 AM task)
- [ ] Export endpoint works
- [ ] Deletion endpoint works
- [ ] Audit logs populated
- [ ] No plaintext in DB
- [ ] No keys in logs
- [ ] HTTPS everywhere
- [ ] GDPR documentation updated
- [ ] Privacy policy updated

##

## 🎯 Success Criteria

✅ **Personalization:** System greets user by name ("Welcome back, Taurin!")
✅ **History:** User can reference past conversations (encrypted)
✅ **Memory:** System understands long-term patterns (dream summaries)
✅ **Privacy:** Conversations encrypted with user's password
✅ **Control:** User can set retention (7/30/90/365 days)
✅ **Compliance:** GDPR export/deletion working
✅ **Security:** No plaintext in database, keys never stored
✅ **Performance:** Encryption/decryption <100ms

##

## 💡 Tips & Troubleshooting

### Issue: "ImportError: No module named cryptography"

**Solution:**

```bash
pip install cryptography
python -c "from cryptography.fernet import Fernet; print('OK')"
```


### Issue: Database constraints failing

**Solution:** Ensure user_retention_preferences rows exist before inserting conversations

```sql
INSERT INTO user_retention_preferences (user_id_hashed)
VALUES (?) ON CONFLICT DO NOTHING;
```


### Issue: Decrypt failing after password change

**Solution:** Intentional. New password = new key = old data inaccessible. User should export before password reset.

### Issue: Daily dreams not generating

**Solution:** Check scheduled task is running

```python

# Verify scheduler is active
scheduler.print_jobs()
```


### Issue: Audit logs not showing

**Solution:** Ensure audit_log calls aren't catching exceptions

```python
try:
    self._audit_log(...)
except Exception as e:
    logger.error(f"Audit log failed: {e}")  # Don't silently fail
```


##

**Ready to proceed? Start with Phase 2: Install dependencies!**
