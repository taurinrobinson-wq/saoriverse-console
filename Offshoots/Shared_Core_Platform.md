# Shared Core Platform, Emotion Core

Purpose

- A minimal, reusable microservice suite that provides common functionality for all offshoots (detection, selection, memory, generation, and storage).

Design Principles

- Small, well-documented HTTP/gRPC APIs.
- Local-first where latency or privacy matters; cloud-hosted for heavy tasks.
- Clear separation of concerns: Detection, Memory, Generation, Policy.
- Extensible plugin surface for product-specific hooks.

Core Services & Endpoints

1. Detection Service

- POST /detect
  - Input: {text, context?:{conversation_id,user_id,last_user_input,last_system_response}}
  - Output: {category, confidence, tags, matches}
- POST /fuzzy_classify
  - Input: {text}
  - Output: {category_scores}

2. Selector Service

- POST /select_first_turn
  - Input: {text, context}
  - Output: {response_template, category}

3. ClarificationTrace Service

- POST /detect_and_store
  - Input: {user_input, context}
  - Output: {stored:bool, rowid:int?, inferred_intent?:str, needs_confirmation:bool}
- GET /lookup?phrase=...&conversation_id=...&user_id=...
  - Output: {record|null}

4. Memory Capsule Service

- POST /capsules
  - Input: {symbolic_tags, relational_phase, voltage_marking, user_input, response_summary, metadata}
  - Output: {capsule_id}
- GET /capsules?conversation_id=&limit=
  - Output: [capsule]

5. Generation Wrapper

- POST /generate
  - Input: {prompt_template, system_output_context, policy_flags}
  - Output: {text, metadata}

6. Auth & Audit

- OAuth2 / JWT-based auth with RBAC
- Audit log: immutable append-only event stream (for admin & compliance)

Data Schema (core objects)

- Capsule: {id, symbolic_tags:[str], relational_phase:str, voltage_marking:str, user_input:str, response_summary:str, timestamp, metadata}
- ClarificationRecord: {id, original_input, user_clarification, system_response, corrected_intent, trigger, conversation_id?, user_id?, first_seen, last_seen}

Plugin & Hook Surface

- Pre-detect Hook: allow product-specific normalizers (e.g., Lightpath vocab limiter).
- Post-detect Hook: product-specific intent mapping.
- Pre-generate Policy: injection point for enterprise guardrails (e.g., legal redaction).

Operational considerations

- Deploy as small microservices (Docker + K8s / ECS) with horizontal scaling.
- Metrics: request latency, error rate, detection precision/recall, DB insert latency, fallback JSONL usage.
- Local SDK: lightweight Python/JS SDK to call Emotion Core with offline handlers.

Security

- TLS everywhere, JWT for service-to-service auth.
- Encrypt sensitive fields at rest (PII fields, transcripts) using KMS-managed keys.
- Key rotation policy and access controls.

Notes

- This service is intentionally minimal; specialized features (music generation, legal templates) live in product modules that call into Emotion Core.
