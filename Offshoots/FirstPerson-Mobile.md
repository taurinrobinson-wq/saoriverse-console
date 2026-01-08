# 📱 FirstPerson Mobile – MVP Spec

### 🎯 Target Users

- Adults seeking deep relational witnessing and emotionally attuned conversation.
- Early adopters interested in privacy-first, human-centered AI companions.

### 🌟 Core Features (MVP Scope)

- Onboarding ritual (guided first-use flow).
- First-turn selector (ritual, casual, reflective).
- Multi-turn memory capsule (relational context stored locally).
- Clarification prompts for ambiguous input.
- Local transcripts with optional sync.
- Offline-first sync prototype.

### 📊 Success Metrics

- Retention (1-week, 1-month).
- Session length (avg minutes).
- Qualitative trust score.

### 🛠 Tech Stack Assumptions

- React Native frontend.
- Python FastAPI backend.
- Vector DB (Milvus/Weaviate/Pinecone).
- LLM responses + small local fallback model.

### 🗓 6–12 Week Roadmap

- Weeks 1–2: UX wireframes, onboarding ritual design, API scaffolding.
- Weeks 3–4: First-turn selector + ClarificationTrace.
- Weeks 5–6: Memory capsule + transcript storage.
- Weeks 7–8: Offline sync + vector DB integration.
- Weeks 9–10: Safety/adversarial testing.
- Weeks 11–12: Closed beta (~20 users).

### ✅ Acceptance Criteria

- Onboarding ritual complete.
- Conversations persist via capsule.
- Clarification prompts trigger reliably.
- Local transcripts accessible/private.
- Offline sync functional.
- ≥70% trust score, ≥50% 1-week retention.
