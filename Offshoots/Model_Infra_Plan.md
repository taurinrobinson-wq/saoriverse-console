# Model & Infrastructure Plan

Goals

- Provide a pragmatic path from prototype → production that balances privacy, latency, cost, and quality.

Model Choices

- Classifiers & Heuristics: small distilled models (DistilBERT / tiny transformers) for device/on-edge inference.
- Embeddings: open models (e.g., text-embedding-3 or SBERT variants) for vector DB store.
- Generative LLMs: start with open checkpoints for prototyping (Llama 2 family / Mistral) hosted in private infra or managed provider.
- Audio: MIDI/parametric generator initially; consider small neural audio models later.

Inference Strategy

- Local-First: run small classifiers and selection logic on-device for overlays and privacy-sensitive flows.
- Hybrid: offload heavy generation to hosted LLMs with cached prompts/outputs for repeatability.
- Fallbacks: deterministic template-based fallback when model unavailable.

Embedding & Vector DB

- Options: Pinecone (managed), Weaviate, Milvus (self-hosted).
- Use-cases: similarity search for relational memory, nearest-neighbor policy lookup.
- Retention & TTL: configurable retention per product (enterprise may require longer retention, demos short-lived).

Serving & Latency

- Target latencies:
  - Classifier (on-device): <100ms
  - First-turn select: <200ms
  - LLM generation: <1s for short outputs (when hosted), degrade gracefully for mobile.
- Use autoscaling and warm pools for model servers.

Evaluation & Monitoring

- Continuous eval: run small holdout tests on new model versions for toxic outputs, hallucination rates, and intent-mapping accuracy.
- Logging: store anonymized logs for drift analysis, with opt-out and retention policies.

Cost Considerations

- Use smaller models for high-traffic, low-latency workloads; reserve large models for heavy synthesis tasks.
- Consider spot instances / GPU scheduling for batch tasks.

Dev / Ops Tooling

- Model registry (versions + metadata), CI for model validation, and deployment (canary deployments).
- Embed tests in CI to validate safety / hallucination / regression.

Roadmap

- Phase 1 (prototype): local classifier + hosted LLM for generation.
- Phase 2 (scale): add vector DB and caching, implement model registry and automated validation.
- Phase 3 (enterprise): hardened on-prem options and BAAs for HIPAA workloads.
