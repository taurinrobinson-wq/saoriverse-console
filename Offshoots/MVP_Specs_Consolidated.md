# Offshoots, Consolidated MVP Specs

This document consolidates and extends the MVP specs in `/Offshoots`. Each offshoot below has a 1-page MVP spec, acceptance criteria, success metrics, a 6–12 week roadmap, key risks, and recommended next actions.

---

## 1) FirstPerson Mobile (Flagship)

Target users

- Adults seeking deep relational witnessing and privacy-first conversational AI.

MVP scope

- Guided onboarding ritual with explicit norms and consent flow.
- First-turn selector (POS + fuzzy classifier) and ClarificationTrace integration.
- Multi-turn relational memory (local capsule store + optional encrypted sync).
- Clarification prompts & lightweight confirmation flows.
- Local transcripts with export controls.
- Offline-first sync prototype (periodic encrypted sync to user-owned storage).

Success metrics

- 1-week retention ≥50%; 1-month retention ≥25%.
- Average session length (minutes) increase vs baseline.
- Qualitative trust score ≥70% in initial pilot.
- Clarification detection precision ≥85%.

Acceptance criteria

- Onboarding ritual implemented and tested with 10 users.
- First-turn selector chooses initiatory phrasing ≥80% when appropriate.
- Memory capsules persist and are retrievable.
- Clarification prompts appear and store corrections reliably.
- Offline sync works for basic conflict cases.

6–12 week roadmap (example)

- Wk1–2: UX wireframes, onboarding ritual copy, API scaffolding.
- Wk3–4: Implement first-turn selector + ClarificationTrace; unit tests.
- Wk5–6: Memory capsule store + local transcripts + basic UI.
- Wk7–8: Offline-first sync + vector DB sync prototype.
- Wk9–10: Safety testing, adversarial inputs, accessibility QA.
- Wk11–12: Closed beta with 20 users and data collection.

Key risks

- Privacy requirements and accidental PII storage, mitigations: local-first, encryption, strict retention.
- Model hallucination, mitigations: prompt engineering, guardrail rules, human-review sampling.

Next actions

- Finalize onboarding narrative & UX flows.
- Prototype first-turn selector integration with current codebase.
- Prepare privacy/security checklist and storage plan.

---

## 2) Lightpath (Childlike / Sensitive UX)

Target users

- Younger people and emotionally sensitive contexts; caregivers monitoring.

MVP scope

- Simplified glyph UI with a constrained vocabulary.
- Animated onboarding ritual and short micro-rituals.
- Content filters (safety) and caregiver controls (read-only, consented access).
- Age-appropriate language model prompts and guardrails.

Success metrics

- Filter/classifier FPR/FNR targets to prioritize safety; filter accuracy ≥90%.
- Caregiver satisfaction ≥80% in pilot.
- Engagement duration appropriate to age group (short sessions).

Acceptance criteria

- Animations for core ritual completed (Lottie or native).
- Vocabulary limiter enforced by classifier.
- Caregiver control panel with permissions tested.

6–12 week roadmap

- Wk1–2: Design glyphs + animation prototypes.
- Wk3–4: Implement vocab limiter & content filters.
- Wk5–6: Caregiver control panel + testing flows.
- Wk7–8: Integrate with shared core.
- Wk9–12: Safety audits with child-safety expert.

Key risks

- Regulatory constraints for minors, require careful legal review.
- Over-simplification may misrepresent complex emotions, include escalation path.

Next actions

- Convene child-safety review and UX workshop.
- Build constrained prompt templates and classifier tests.

---

## 3) Message UI Overlay (iOS/Android)

Target users

- Messaging app users who want in-line detection of manipulation, gaslighting and quick reframes.

MVP scope

- Real-time classifier for manipulative language.
- Inline heatmap / cue overlay showing message-level emotional risk.
- Single-tap reframes and suggested responses (editable by the user).
- Local-first processing where possible (privacy-preserving).

Success metrics

- Classifier detection precision ≥80% (recall balanced to user preference).
- User adoption of suggested reframes ≥20% of flagged interactions.
- Reduction in self-reported manipulative incidents in pilot.

Acceptance criteria

- Live classifier runs in a demo overlay with acceptable latency (<200ms on modern devices, or graceful degrade).
- Heatmap visually reflects predicted severity and explanation tokens.
- Reframe suggestions editable & inserted into message composer.

6–12 week roadmap

- Wk1–2: Train/validate small classifier on annotated manipulative/gaslighting dataset.
- Wk3–4: Develop overlay UI prototype in webview or keyboard extension.
- Wk5–6: Implement reframe suggestion engine & UX.
- Wk7–8: Local-optimizations & privacy-first tuning.
- Wk9–10: Adversarial robustness testing.
- Wk11–12: Pilot with small user group.

Key risks

- False positives causing user frustration; mitigation: conservative thresholds and undo.
- Platform constraints (keyboard extensions limitations on iOS), produce webview and native variants.

Next actions

- Gather sample dataset for manipulation/gaslighting.
- Prototype classifier and simple overlay proof-of-concept.

---

## 4) Threshold Enterprise (Therapist / Case Worker Edition)

Target users

- Clinicians, case workers, and helper organizations requiring anonymized insights and burnout prevention.

MVP scope

- Anonymized journaling ingestion (PII redaction & hashing).
- Batch ritual suggestions for caseloads (multiple-case view).
- Burnout monitoring dashboard (team-level risk signals).
- Role-based access control, audit logs, and export controls.

Success metrics

- Burnout detection accuracy ≥80% (early warning precision prioritized).
- Clinician pilot satisfaction ≥75%.
- Compliance & documentation ready for HIPAA review.

Acceptance criteria

- Anonymization pipeline demonstrably removes PII in test suite.
- Dashboard surfaces cohort-level burnout signals with drill-down.
- RBAC and audit logging match spec and pass basic security review.

6–12 week roadmap

- Wk1–2: Design anonymization & consent flows.
- Wk3–4: Implement journaling ingestion & redaction tests.
- Wk5–6: Build ritual suggestion engine (batch mode).
- Wk7–8: Burnout dashboard & RBAC.
- Wk9–10: Compliance hardening; BAA / legal intake.
- Wk11–12: Pilot with partner clinicians.

Key risks

- Legal / compliance burden (HIPAA), schedule early legal review and infra controls.
- Data misclassification, include human-in-loop review for flagged cases.

Next actions

- Draft HIPAA engineering checklist and risk register.
- Implement anonymization test harness and synthetic dataset.

---

## 5) Tonecore (Emotional Soundscaping)

Target users

- Users who want audio augmentation for emotional exploration and ritual accompaniment.

MVP scope

- Map emotion metadata → short chord progressions / ambience.
- Exportable audio loop (MIDI → synth or simple audio render).
- Controls for intensity, tempo, and resolution.

Success metrics

- User audio engagement (plays, exports) ≥ target.
- Subjective satisfaction ≥70% in pilot.

Acceptance criteria

- Emotion→MIDI mapping implemented and validated with test inputs.
- Audio loop exports working across platforms (web/mobile).

6–12 week roadmap

- Wk1–2: Define mapping rules (emotion → scale/mode/chord progressions).
- Wk3–4: Implement MIDI generator + simple synth (WebAudio or native libs).
- Wk5–6: Export loop functionality (wav/mp3).
- Wk7–8: UX for controlling intensity/tempo.
- Wk9–12: User testing & iteration.

Key risks

- Cultural interpretation of music differs, test with diverse user groups.
- Licensing and quality for synth engines, prefer open-source synth packages initially.

Next actions

- Prototype mapping rules and a small MIDI demo playable in browser.

---

## 6) CoreLex (Legal Services / CoreLex)

Target users

- Attorneys and legal teams seeking anonymized intake, emotion-aware summarization, and document generation.

MVP scope

- Anonymized intake pipeline.
- Emotion-aware summarization of narratives (short case summaries).
- Templated document generation (intake forms, basic letters).
- Ethical guardrails, consent UI, role-based access.

Success metrics

- Intake processing time reduced by ≥30%.
- Anonymization accuracy ≥95% per test cases.
- Emotional cues present in summaries ≥80% accuracy.

Acceptance criteria

- Intake pipeline anonymizes correctly across sample datasets.
- Summaries include emotional cues and key facts reliably.
- Templates generate compliant documents.

6–12 week roadmap

- Wk1–2: Build anonymization pipeline & tests.
- Wk3–4: Implement summarization & evaluation harness.
- Wk5–6: Doc generation module + templates.
- Wk7–8: Role-based access + consent flows.
- Wk9–12: Security hardening and pilot.

Key risks

- Legal compliance beyond HIPAA (state-level rules); require legal review.
- Summarization errors with sensitive data, human-in-loop required.

Next actions

- Line up legal advisor and pilot partner firm.

---

## 7) AffectIQ (Industry Chat Overlays)

Target users

- Customer support teams and chat operators who want emotion detection and de-escalation in real-time.

MVP scope

- Live emotion classification in chat streams.
- Inline de-escalation suggestions for agents.
- Escalation flags with human routing.
- Integration with 1 major chat platform (e.g., Intercom or Zendesk).

Success metrics

- Classification accuracy ≥85%.
- 20% reduction in escalations in pilot.
- Agent satisfaction ≥70%.

Acceptance criteria

- Classifier integrated into overlay UI and one chat platform.
- Suggestions fire reliably and route flagged chats.

6–12 week roadmap

- Wk1–2: Prototype classifier + overlay.
- Wk3–4: Suggestion engine development.
- Wk5–6: Escalation routing & analytics.
- Wk7–8: Local-first optimization and caching.
- Wk9–12: Pilot with support team.

Key risks

- False positives leading to unnecessary escalations, conservative thresholds + overrides.
- Platform integration friction; prefer a single platform initially.

Next actions

- Prepare sample chat datasets and agent UX flows.

---

# Shared Core Recommendations

Design a shared "Emotion Core" microservice exposing:

- Detection API (classify_signal, select_first_turn_response)
- ClarificationTrace store API (detect_and_store, lookup)
- Memory capsule API (store/retrieve/list)
- Response generation wrapper (policy/LLM prompt layer)
- Auth + RBAC and audit logging

Infrastructure

- Vector DB: choose managed service (Pinecone) or Weaviate for local/hybrid.
- Models: open LLMs for prototyping, consider hosted endpoints for heavy tasks; small distilled classifiers run on-device for overlays.
- Security: encryption at rest/in transit, role-based access, audit logs; HIPAA controls for enterprise products.

# Next steps (recommendation)

1. Confirm priority order of offshoots (which MVP to build first).
2. For first-priority product, produce a 2-week sprint plan and begin the prototype (code scaffold + endpoint mock).
3. Assemble small cross-functional team (ML eng, backend, mobile, UX, compliance advisor).

---

If you'd like, I can now:

- Commit this consolidated spec to `/Offshoots/MVP_Specs_Consolidated.md` and push (yes/no?), or
- Start a prioritized 2-week sprint plan for whichever offshoot you pick first (recommended: FirstPerson Mobile).

Tell me which next action you want me to take.
