# Privacy Layer Database Schema

This document specifies the database tables needed for the encryption + retention + dream engine model.

## Table: `conversations_encrypted`

Stores full encrypted conversations with user-configurable retention.

```sql
CREATE TABLE conversations_encrypted (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User identification
    user_id_hashed VARCHAR(64) NOT NULL,  -- PBKDF2 hashed user_id
    session_id VARCHAR(255),              -- Session identifier

    -- Encrypted content
    encrypted_content BYTEA NOT NULL,     -- AES-256 encrypted conversation

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,  -- When to delete
    retention_days INT NOT NULL DEFAULT 30,        -- User's retention preference

    -- Indexing
    FOREIGN KEY (user_id_hashed) REFERENCES user_retention_preferences(user_id_hashed),
    INDEX idx_user_expiration (user_id_hashed, expires_at)
);
```


**Purpose:** Store full conversations with all context, encrypted so only the authenticated user can read them.

**Access Pattern:**

- On user login: Decrypt recent conversations for context
- On conversation storage: Encrypt and save with user's retention period
- On daily cleanup: Delete where `expires_at < NOW()`
- On GDPR deletion: Delete all rows where `user_id_hashed = X`

**Retention Examples:**

- expires_at = created_at + 7 days → Recent support (keep 1 week)
- expires_at = created_at + 30 days → Default (keep 1 month)
- expires_at = created_at + 90 days → Extended (keep 3 months)
- expires_at = created_at + 365 days → Long-term (keep 1 year)

##

## Table: `dream_summaries`

Stores lightweight daily summaries of emotional patterns and themes.

```sql
CREATE TABLE dream_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User identification
    user_id_hashed VARCHAR(64) NOT NULL,  -- Same hash as conversations_encrypted
    date DATE NOT NULL,                    -- Which day (YYYY-MM-DD)

    -- Encrypted summary content
    encrypted_summary BYTEA NOT NULL,     -- AES-256 encrypted dream summary

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,  -- Usually 90-180 days later

    -- Unique constraint (one summary per day per user)
    UNIQUE(user_id_hashed, date),

    -- Indexing
    FOREIGN KEY (user_id_hashed) REFERENCES user_retention_preferences(user_id_hashed),
    INDEX idx_user_date (user_id_hashed, date)
);
```


**Purpose:** Store lightweight daily summaries that survive longer than full conversations.

**Summary Contents (all encrypted):**

```json
{
  "date": "2024-01-15",
  "primary_emotions": ["anxiety", "hope"],
  "secondary_emotions": ["grief"],
  "key_themes": ["work", "relationships", "self-worth"],
  "recurring_concerns": ["boundary issues", "perfectionism"],
  "user_stated_needs": ["support", "validation", "perspective"],
  "glyph_effectiveness": {
    "ACCEPTANCE": 0.85,
    "GROUNDING": 0.72,
    "PERSPECTIVE": 0.68
  },
  "most_effective_glyphs": ["ACCEPTANCE", "GROUNDING"],
  "session_count": 3,
  "total_messages": 24,
  "engagement_level": "high",
  "crisis_flags": false,
  "concerning_patterns": [],
  "narrative_summary": "Today you experienced anxiety and hope. Key themes included work, relationships, and self-worth. You expressed needs for support, validation, and perspective. You had 3 conversations today."
}
```


**Why Separate?**

- Size: Summary is ~1KB vs full conversation ~10-50KB
- Retention: Summaries kept 90-180 days, full conversations 7-30 days
- Performance: Can load patterns without decrypting months of data
- Privacy: Summaries can't reconstruct exact words, only patterns

##

## Table: `user_retention_preferences`

Stores user settings for data retention and privacy controls.

```sql
CREATE TABLE user_retention_preferences (
    user_id_hashed VARCHAR(64) PRIMARY KEY,  -- Links to auth system

    -- Retention settings
    full_conversation_retention_days INT NOT NULL DEFAULT 30,  -- 7/30/90/365/custom
    dream_summary_retention_days INT NOT NULL DEFAULT 90,       -- Longer for patterns

    -- User controls
    allow_export BOOLEAN NOT NULL DEFAULT true,                 -- Can download data
    allow_archive BOOLEAN NOT NULL DEFAULT true,                -- Can archive manually
    deleted_at TIMESTAMP WITH TIME ZONE,                        -- GDPR deletion timestamp

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    INDEX idx_deleted (deleted_at)
);
```


**Purpose:** User configuration for privacy and retention. Single record per user.

**Retention Options:**

- `7`: Short-term (week) - for highly sensitive users
- `30`: Default (month) - standard personalization
- `90`: Extended (quarter) - long-term pattern recognition
- `365`: Long-term (year) - comprehensive history
- `custom_N`: User-specified days (documented in field or separate table)

##

## Table: `audit_log_privacy`

Audit trail for all encryption/decryption/deletion operations.

```sql
CREATE TABLE audit_log_privacy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Who and what
    user_id_hashed VARCHAR(64) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'encrypt_conversation', 'decrypt_conversation', 'delete_all', 'export_data', 'set_retention'

    -- Details
    resource_type VARCHAR(50),    -- 'conversation', 'dream_summary', 'profile', 'all'
    record_count INT,             -- How many records affected

    -- Context
    ip_address INET,              -- User's IP
    user_agent VARCHAR(500),      -- Browser/client info

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Indexing
    INDEX idx_user_action (user_id_hashed, action),
    INDEX idx_timestamp (created_at)
);
```


**Purpose:** Compliance auditing for privacy operations.

**Examples:**

- "decrypt_conversation" - User read a past conversation
- "delete_all" - User exercised right to be forgotten
- "export_data" - User downloaded their data
- "set_retention" - User changed retention preference

##

## Integration with Existing Tables

### `users` or `auth_users`

When creating/updating a user, ensure `user_retention_preferences` is created:

```sql
INSERT INTO user_retention_preferences (user_id_hashed)
VALUES (PBKDF2_HASH(user_id))
ON CONFLICT DO NOTHING;
```


### Relationship Diagram

```
users (auth system)
  ↓
user_retention_preferences (retention settings, one per user)
  ↓
├── conversations_encrypted (full convos, user-controlled TTL)
│   └── Deleted after retention_days
│
├── dream_summaries (daily patterns, longer retention)
│   └── Deleted after dream_retention_days
│
└── audit_log_privacy (all encryption/deletion events)
```


##

## Migration Path (From Current System)

### Phase 1: Add New Tables

1. Create `conversations_encrypted` table
2. Create `dream_summaries` table
3. Create `user_retention_preferences` table
4. Create `audit_log_privacy` table

### Phase 2: Initialize User Preferences

```sql
INSERT INTO user_retention_preferences (user_id_hashed, full_conversation_retention_days)
SELECT DISTINCT user_id_hashed, 30
FROM conversations_encrypted
WHERE user_id_hashed NOT IN (SELECT user_id_hashed FROM user_retention_preferences);
```


### Phase 3: Migrate Existing Conversations

For each existing conversation:

1. Decrypt current storage (if any)
2. Re-encrypt with `EncryptionManager.encrypt_conversation()`
3. Insert into `conversations_encrypted` with calculated `expires_at`
4. Delete from old table after verification

### Phase 4: Enable Dream Engine

1. Start daily summary generation at end-of-day
2. Store summaries in `dream_summaries`
3. Use summaries for context instead of loading all conversations

### Phase 5: Clean Up Old Storage

1. Once all conversations migrated and verified
2. Drop old conversation storage table
3. Keep audit logs forever for compliance

##

## Privacy & Compliance Notes

### GDPR Compliance

- **Right to Access:** User can export all decrypted data via `/user/data-export`
- **Right to Deletion:** User can delete all data via `/user/data-delete`, triggers cleanup of all tables and creates audit record
- **Data Minimization:** Only store what's needed for personalization + required retention
- **Lawful Basis:** User consent (through retention settings), necessity (for service)

### CCPA Compliance

- **Consumer Rights:** Delete request removes all rows with user_id_hashed
- **Opt-Out:** User can set retention_days to 0 (immediate deletion after processing)
- **Sale Prohibition:** Never sell user data
- **Transparency:** Privacy policy explains storage and encryption

### HIPAA (if applicable)

- **Encryption at Rest:** AES-256 with Fernet
- **Encryption in Transit:** HTTPS only
- **Access Controls:** Only user can decrypt with their password
- **Audit Trail:** All access logged in audit_log_privacy

### State Wiretapping Laws

- **Consent:** User opted-in to storage during onboarding
- **Notice:** Privacy policy discloses storage and monitoring
- **Termination:** User can delete at any time
- **No Interception:** Data only stored after user submits, not intercepted

##

## Performance Considerations

### Indexing Strategy

- Index on `(user_id_hashed, expires_at)` for cleanup queries
- Index on `(user_id_hashed, date)` for dream summary retrieval
- Index on `(user_id_hashed, action)` for audit queries

### Query Optimization

```sql
-- Fast cleanup (runs daily)
DELETE FROM conversations_encrypted
WHERE expires_at < NOW();

-- Fast user context retrieval
SELECT encrypted_content
FROM conversations_encrypted
WHERE user_id_hashed = ?
AND created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Fast dream summary retrieval
SELECT encrypted_summary
FROM dream_summaries
WHERE user_id_hashed = ?
ORDER BY date DESC
LIMIT 30;
```


### Storage Estimates

- Full conversation: ~20KB encrypted (grows with length)
- Dream summary: ~2KB encrypted (fixed size)
- Per user per year:
  - Full conversations: ~200GB (if 30-day retention)
  - Dream summaries: ~730KB (if 365-day retention)
  - Ratio: Dream summaries are ~0.3% the size
