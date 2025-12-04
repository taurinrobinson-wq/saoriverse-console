# Privacy Layer Architecture Reference

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     FirstPerson Sanctuary                        │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │ User Login  │
                        └─────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            │                                     │
            ▼                                     ▼
    ┌────────────────┐             ┌──────────────────────┐
    │  Password      │             │ PBKDF2 Key          │
    │ (from user)    │──KDF───────→│ Derivation          │
    └────────────────┘             └──────────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Encryption Key  │
                                   │ (256-bit AES)   │
                                   └─────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
        ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────┐
        │ Decrypt Profile   │  │ Load Conversations │  │ Load Dream       │
        │ (name, email)     │  │ (last 7 days)      │  │ Summaries        │
        └───────────────────┘  └────────────────────┘  └──────────────────┘
                    │                       │                       │
                    └───────────────────────┴───────────────────────┘
                                      │
                                      ▼
                    ┌──────────────────────────────────┐
                    │  System Ready for Interaction    │
                    │ "Welcome back, Taurin!"          │
                    └──────────────────────────────────┘
                                      │
                    ┌─────────────────┴──────────────────┐
                    │                                    │
                    ▼                                    ▼
        ┌──────────────────────┐          ┌──────────────────────┐
        │ User Conversation    │          │ Dream Summaries      │
        │ - Feelings           │          │ - Patterns           │
        │ - Concerns           │          │ - Themes             │
        │ - Signals            │          │ - Emotions           │
        └──────────────────────┘          │ - Effective Glyphs   │
                    │                     └──────────────────────┘
                    ▼
        ┌──────────────────────┐
        │ Signal Parsing       │
        │ Glyph Selection      │
        │ Response Generation  │
        └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────────────────┐
        │ Conversation Structure:          │
        │ {                                │
        │   session_id,                    │
        │   messages: [user, assistant],   │
        │   signals: [...],                │
        │   glyphs: [...],                 │
        │   best_glyph,                    │
        │   created_at                     │
        │ }                                │
        └──────────────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────────────┐
        │ Encrypt with User's Key (AES256) │
        └──────────────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────────────┐
        │ Store Encrypted Conversation     │
        │ conversations_encrypted table    │
        │ {                                │
        │   user_id_hashed,                │
        │   encrypted_content (BYTEA),     │
        │   created_at,                    │
        │   expires_at: now + 30 days      │
        │ }                                │
        └──────────────────────────────────┘
                    │
                    ├─→ Add to Daily Batch
                    │
                    └─→ Audit Log
                         (action: "encrypt_conversation")

                     [End of Day - 3 AM]
                               │
                    ┌──────────▼────────────┐
                    │ Dream Engine Task     │
                    └──────────┬────────────┘
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
    ┌─────────────────┐                   ┌─────────────────────┐
    │ Retrieve Daily  │                   │ Process Batch Data  │
    │ Batch Data      │                   │ (already plaintext) │
    └─────────────────┘                   └─────────────────────┘
        │                                        │
        └────────────────────┬────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Extract:        │
                    │ - Emotions      │
                    │ - Themes        │
                    │ - Concerns      │
                    │ - Effectiveness │
                    └────────┬────────┘
                             │
                    ┌────────▼────────────┐
                    │ Create Dream        │
                    │ Summary Object      │
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │ Encrypt Summary     │
                    │ (AES256 with key)   │
                    └────────┬────────────┘
                             │
                    ┌────────▼──────────────────┐
                    │ Store in dream_summaries  │
                    │ {                        │
                    │   user_id_hashed,        │
                    │   date,                  │
                    │   encrypted_summary,     │
                    │   expires_at: +90 days   │
                    │ }                        │
                    └────────┬──────────────────┘
                             │
                    ┌────────▼────────────┐
                    │ Clear Daily Batch   │
                    │ (for this user)     │
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │ Cleanup Job (4 AM)  │
                    └────────┬────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
    DELETE FROM                            DELETE FROM
    conversations_encrypted                 dream_summaries
    WHERE expires_at < NOW()                WHERE expires_at < NOW()
    (removes 30-day old convos)             (removes 90-day old dreams)
```

---

## Data Flow: User Retention Changes

```
User Sets Retention to 7 Days
        │
        ▼
    POST /api/user/retention-settings
        │
        ▼
    Update user_retention_preferences
    retention_days: 30 → 7
        │
        ▼
    ┌─────────────────────────────────────┐
    │ New Conversations (after change)    │
    │ expires_at = now + 7 days           │
    └─────────────────────────────────────┘
        │
        │ (existing conversations unchanged)
        ▼
    ┌─────────────────────────────────────┐
    │ Old Conversations (before change)   │
    │ expires_at = original (e.g., +30d)  │
    └─────────────────────────────────────┘
        │
        │ After 30 days
        ▼
    All old conversations deleted
    New conversations still valid (< 7 days old)
        │
        │ After 7 days
        ▼
    All conversations deleted
    Only dream summaries remain (90-day retention)
```

---

## Data Flow: GDPR Deletion Request

```
User Clicks "Delete All My Data"
        │
        ▼
    DELETE /api/user/data-delete
        │
        ▼
    Mark user_retention_preferences
    deleted_at = NOW()
        │
        │ [30-Day Grace Period]
        │ User can still login during grace period
        │ User can cancel deletion if needed
        │
        └─────────────────→ [After 30 days]
                                   │
                                   ▼
                        Permanent Deletion Task
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
                DELETE FROM   DELETE FROM   DELETE FROM
                conversations dream_        user_
                _encrypted    summaries     retention_
                WHERE user_   WHERE user_   preferences
                id_hashed=X   id_hashed=X   WHERE user_
                                            id_hashed=X
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Keep Audit Log       │
                        │ (for compliance)     │
                        │ Deletion recorded    │
                        └──────────────────────┘
```

---

## Data Flow: User Export Request

```
User Clicks "Export My Data"
        │
        ▼
    GET /api/user/data-export
        │
        ▼
    ┌──────────────────────────────────────┐
    │ Retrieve All User's Encrypted Data   │
    └──────────────────────────────────────┘
        │
        ├─→ conversations_encrypted (BYTEA)
        ├─→ dream_summaries (BYTEA)
        ├─→ user_profile (encrypted)
        └─→ user_retention_preferences
        │
        ▼
    ┌──────────────────────────────────────┐
    │ Package as ZIP or JSON               │
    │ - metadata.json                      │
    │ - conversations.json (encrypted)     │
    │ - dreams.json (encrypted)            │
    │ - README (decryption instructions)   │
    └──────────────────────────────────────┘
        │
        ▼
    Download to User's Computer
        │
        ▼
    User Decrypts Offline
    (User has password, can decrypt with EncryptionManager locally)
        │
        ▼
    ┌──────────────────────────────────────┐
    │ User Has Full Access to Their Data   │
    │ Can import to backup, other systems, │
    │ or archive for personal records      │
    └──────────────────────────────────────┘
```

---

## Database Schema Relationship Diagram

```
┌────────────────────────────────────────┐
│  user_retention_preferences            │
│  (1 per user, retention config)        │
│                                        │
│  PK: user_id_hashed (VARCHAR 64)      │
│  - retention_days                      │
│  - dream_retention_days                │
│  - allow_export                        │
│  - allow_archive                       │
│  - deleted_at (NULLABLE)               │
└────────────────────────────────────────┘
        │ (one-to-many)
        │ user_id_hashed
        ├─────────────┬──────────────┐
        │             │              │
        ▼             ▼              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ conversations_   │ │ dream_summaries  │ │ audit_log_       │
│ encrypted        │ │                  │ │ privacy          │
│                  │ │                  │ │                  │
│ id (UUID)        │ │ id (UUID)        │ │ id (UUID)        │
│ user_id_hashed   │ │ user_id_hashed   │ │ user_id_hashed   │
│ encrypted_cont.  │ │ encrypted_summ.  │ │ action           │
│ created_at       │ │ date (YYYYMMDD)  │ │ created_at       │
│ expires_at       │ │ expires_at       │ │                  │
│ retention_days   │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                     │                     │
        │ (TTL based)         │ (TTL based)        │ (Indefinite)
        │ Default: 30 days    │ Default: 90 days   │ For compliance
        │                     │                    │
        └─────────────────────┴────────────────────┘
```

---

## Encryption Key Management Flow

```
User Registration / Password Set
        │
        ▼
    user_id: "taurin@example.com"
    password: "super_secret_123"
        │
        ▼
    ┌──────────────────────────────┐
    │ PBKDF2 Key Derivation        │
    │ - Input: user_id + password  │
    │ - Iterations: 100,000        │
    │ - Salt: per-user (embedded)  │
    │ - Output: 256-bit key        │
    └──────────────────────────────┘
        │
        ▼
    Encryption Key (in memory only)
        │
        ├─→ Encrypt user profile
        │   → Store encrypted blob
        │
        ├─→ Encrypt conversations
        │   → Store encrypted blobs
        │
        └─→ Encrypt dream summaries
            → Store encrypted blobs
        │
        │ [After request completes]
        ▼
    Key Destroyed (memory released)


User Logs In
        │
        ▼
    user_id: "taurin@example.com"
    password: "super_secret_123"
        │
        ▼
    ┌──────────────────────────────┐
    │ PBKDF2 Key Derivation        │
    │ Same inputs → Same key       │
    │ (deterministic)              │
    └──────────────────────────────┘
        │
        ▼
    Encryption Key (in memory only)
        │
        ├─→ Decrypt user profile
        │   ← Read name for greeting
        │
        ├─→ Decrypt recent conversations
        │   ← Load for context
        │
        └─→ Access dream summaries
            (already in decrypted form in app)
        │
        │ [After request completes]
        ▼
    Key Destroyed (memory released)


Key Properties
        │
        ├─→ NEVER stored anywhere
        │   (derived on-demand)
        │
        ├─→ NEVER written to logs
        │   (would leak data)
        │
        ├─→ NEVER transmitted
        │   (derived locally)
        │
        ├─→ NEVER persisted to disk
        │   (only in RAM during session)
        │
        └─→ Deterministic
            (same password always produces same key
             enables consistent encryption/decryption)
```

---

## Security Model: Threat Scenarios

```
Scenario 1: Server Breach - Attacker Accesses Database
        │
        ├─→ Finds conversations_encrypted table
        │   → Gets BYTEA blobs (encrypted)
        │   → Can't read (need user's key)
        │
        ├─→ Tries to brute-force encryption
        │   → Would need to try 2^256 keys
        │   → Not feasible
        │
        ├─→ Tries to brute-force password
        │   → PBKDF2 has 100,000 iterations
        │   → Each attempt: ~100ms
        │   → 10,000 attempts: ~1000 seconds
        │   → Not feasible for high-entropy passwords
        │
        └─→ Result: Data remains secure
            (encryption protects)


Scenario 2: Attacker Gets User's Password
        │
        ├─→ Can derive user's encryption key
        │   (same as user)
        │
        ├─→ Can decrypt user's conversations
        │   (but only that user's data)
        │
        ├─→ Other users unaffected
        │   (each user has unique key)
        │
        └─→ Mitigation: Password reset
            → New password → new key
            → Old data inaccessible
            → User should export before reset


Scenario 3: Attacker Intercepts Encrypted Data in Transit
        │
        ├─→ Gets encrypted BYTEA blob
        │   (useless without key)
        │
        ├─→ Can't intercept key
        │   (derived locally, not transmitted)
        │
        └─→ Result: Secure even in transit
            (but HTTPS used anyway)


Scenario 4: Rogue FirstPerson Employee
        │
        ├─→ Can access server and database
        │   → Sees encrypted blobs (useless)
        │   → Sees user_id_hashed (one-way)
        │
        ├─→ Can't link hash back to user
        │   (irreversible hash)
        │
        ├─→ Can't read conversations
        │   (need password)
        │
        ├─→ Can check audit logs
        │   (but all access logged)
        │
        └─→ Result: Limited damage
            (logging catches misuse)


Scenario 5: Forgotten Password
        │
        ├─→ User can't access conversations
        │   (can't derive old key)
        │
        ├─→ Password reset creates new key
        │   → New key can't decrypt old data
        │
        ├─→ User should export before reset
        │   (get encrypted data while can still access)
        │
        └─→ After reset: old data inaccessible
            → Treated as retention expiry
            → Eventually deleted per policy
```

---

## Performance Characteristics

```
Operation                    | Time      | Notes
────────────────────────────────────────────────────────────
PBKDF2 Key Derivation        | ~100ms    | 100,000 iterations
Encrypt 10KB Data            | ~10ms     | AES-256 with Fernet
Decrypt 10KB Data            | ~10ms     | Fernet auth + decrypt
Hash User ID (SHA256)        | <1ms      | One-way function
Create Daily Summary         | ~50ms     | Processing 20 convos
Store Encrypted (DB)         | ~50ms     | Depends on connection
Login (full flow)            | ~500ms    | KDF + decrypt + load
Cleanup Task (daily)         | ~1s       | DELETE + indices
────────────────────────────────────────────────────────────

Database Queries
────────────────────────────────────────────────────────────
Load recent conversations    | ~100ms    | Index on user+expires
(7 days)                     |           |
Load dream summaries (30)    | ~50ms     | Index on user+date
Cleanup expired data         | ~500ms    | Index on expires_at
────────────────────────────────────────────────────────────

Storage
────────────────────────────────────────────────────────────
Per conversation             | ~20KB     | Encrypted
Per dream summary            | ~2KB      | Encrypted
Per user per month (30-day   | ~600KB    | 30 conversations
retention)                   |           |
Per user per month (dreams)  | ~60KB     | 30 summaries
────────────────────────────────────────────────────────────
```

---

## Compliance Mapping

```
GDPR
├─→ Right to Access: /api/user/data-export ✅
├─→ Right to Deletion: /api/user/data-delete ✅
├─→ Right to Portability: Export in standard format ✅
├─→ Data Minimization: Only store necessary data ✅
├─→ Purpose Limitation: Only use for personalization ✅
├─→ Storage Limitation: Auto-delete per retention policy ✅
└─→ Integrity & Confidentiality: AES-256 encryption ✅

CCPA
├─→ Consumer Rights: Delete/access/opt-out ✅
├─→ Business Transparency: Privacy policy discloses ✅
├─→ Security: Encryption at rest ✅
└─→ No Sale: Never sell user data ✅

HIPAA (if handling PHI)
├─→ Encryption at Rest: AES-256 ✅
├─→ Encryption in Transit: HTTPS ✅
├─→ Access Controls: Only user + minimal staff ✅
├─→ Audit Controls: Audit log for all access ✅
├─→ Integrity: HMAC in Fernet ✅
└─→ Availability: Data retention + backup ✅

State Wiretapping Laws
├─→ Consent: User consents during signup ✅
├─→ Notice: Privacy policy discloses ✅
├─→ Single Party: User consents to own monitoring ✅
└─→ Termination: Can delete at any time ✅
```

---

**This architecture ensures FirstPerson provides both:**
- **Personalization** (data stored & accessible)
- **Privacy** (data encrypted with user's password)
- **Compliance** (automatic retention, deletion, audit logging)
- **User Control** (configurable retention, export, deletion)
