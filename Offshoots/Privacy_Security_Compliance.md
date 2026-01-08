# Privacy, Security & Compliance Checklist

Scope

- Enterprise products (Threshold Enterprise, CoreLex) must meet HIPAA-style controls.
- All products should follow privacy-by-design: minimal data collection, user control, and encryption.

Core Controls

- Access & Identity
  - OAuth2 / SSO integration for enterprise users.
  - RBAC for feature access; least privilege principle.
- Data Protection
  - TLS in transit, AES-256 at rest with KMS management.
  - Field-level encryption for PII (names, emails, transcripts) when stored.
- Audit & Monitoring
  - Immutable audit logs for admin actions and data exports.
  - Incident detection + alerting (suspicious access patterns).

HIPAA-specific

- Business Associate Agreements (BAAs) with cloud providers.
- Breach notification procedures and timelines.
- Data residency controls (if required by client jurisdiction).
- Formal risk assessment and documentation.

Anonymization & Redaction

- Tokenization/hashing of direct identifiers during ingestion.
- Redaction rules: regex-based for common PII patterns + ML NER for more complex content.
- Re-identification risk assessment: store cryptographic salts separately and audit re-linking.

Retention & Deletion

- Configurable retention policies per product and tenant.
- Secure deletion (logical + physical where required).
- Export data and consented exports only.

Consent & UX

- Explicit consent screens, especially for enterprise/clinical users.
- Clear settings for opt-out, data export, and data deletion.

Testing & Validation

- Penetration testing for production infra.
- Privacy-preserving synthetic data for QA and model retraining.
- Regular audits and compliance readiness exercises.

Developer Guidance

- Avoid logging raw user content in non-secure logs.
- Use secure libraries and avoid rolling your own crypto.

Next actions

- Draft a HIPAA-specific implementation plan for Threshold Enterprise.
- Identify preferred cloud vendors and gather BAA templates.
