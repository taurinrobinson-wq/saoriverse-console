# IFY — Technical Architecture & Glyph Remediation

This document outlines a practical, implementable architecture for IFY (Emotional Music Engine), focusing first on glyph data quality and remediation so your emotional OS can be functional.

## Goals
- Define a clear system architecture for IFY MVP
- Provide a strict glyph JSON schema to prevent extraneous data
- Supply a safe glyph-cleaning script to normalize existing glyphs
- Map components to low-cost ($5K) vs. full prototype ($50K) implementation

---

## System Overview (high level)

Components:
- Ingestion Layer
  - Audio embedding service (faiss/llm embedding API)
  - Metadata fetcher (Spotify/Apple APIs, lyrics APIs)
  - LLM classifier for emotional tagging
- Glyph Service (core)
  - Canonical glyph store (JSON documents in DB / S3)
  - Glyph validation & sanitizer (this repo's cleaning script)
  - Glyph indexing (Elasticsearch or Postgres+pg_trgm)
- Playlist Engine
  - Emotional state model (user profile + current input)
  - Sequence generator (transitions, arcs, glyph mapping)
- Integration Layer
  - OAuth connectors for Spotify/Apple
  - Playback connectors (deep links, Spotify playback API)
- Frontend / UX
  - Minimal prototype UI: select mood, review playlist arc, play externally
- Analytics & Personalization
  - Preference store, incremental training signals

Data flows:
1. Ingest song metadata and audio embeddings
2. Classify emotional features via LLM + audio model
3. Map song features -> glyphs (via glyph metadata)
4. Playlist engine composes emotional arcs using glyph transitions
5. User plays tracks via external service, feedback loops update model

---

## Glyph Data: Problem & Fix

Problem observed: glyph JSON documents contain extraneous, loosely-typed fields that break pipeline code expecting a stable schema.

Solution summary:
1. Define a canonical glyph JSON schema (strict fields + types)
2. Run a non-destructive cleaning process over existing glyph files to:
   - Remove unknown fields
   - Normalize types and key names
   - Fill missing required fields with safe defaults
   - Produce backups for auditing
3. Enforce schema at ingestion time (reject or quarantine non-conformant glyphs)

### Canonical Glyph Schema (high level)
- `id` (string, uuid)
- `name` (string)
- `description` (string)
- `primary_emotions` (array of strings, e.g., ["sadness","longing"]) - limited vocabulary
- `intensity` (number 0.0-1.0)
- `tags` (array of strings)
- `glyph_type` (string: "emotion", "transition", "artifact")
- `version` (string)
- `provenance` (object: {source: string, source_id?: string, created_at?: ISO8601})
- `assets` (array of objects: {type, url})
- `metadata` (object - allowed keys are explicitly listed)

The schema must set `additionalProperties:false` to avoid silent propagation of broken fields.

---

## File Locations & Strategy
- Keep canonical glyph JSONs in a dedicated repo folder `src/emotional_os_glyphs/canonical/` or an S3 bucket for runtime.
- Use `Offshoots/IFY/glyph_schema.json` as the authoritative schema file in the repo.
- Use `Offshoots/IFY/clean_glyphs.py` to scan existing folders (`src/emotional_os_glyphs/`, `archive/.../glyphs/`) and write normalized copies to a `canonical_cleaned/` folder.

---

## Minimal Viable Implementation (5K)
Target: prototype that proves mapping songs→glyphs→playlists
- Hosted backend: single small VPS (DigitalOcean) or serverless functions
- Use open-source audio embeddings (OpenAI/CLAP/Whisper embeddings) via APIs
- Use LLM (OpenAI/GPT) for classification (cost-light during prototyping)
- Store glyphs as JSON files in S3 or Git (small scale)
- Implement playlist generator as a simple rule-based sequencer that uses glyph transitions
- Build a small React UI to accept mood input and output Spotify playlist links

Deliverables in ~4 weeks (solo dev + contractor):
- `glyph_schema.json`
- `clean_glyphs.py` script
- Minimal ingestion + classifier glue
- Playlist sequencing engine (rule-based)
- Basic UI + Spotify OAuth integration

---

## Full Prototype (50K)
Adds:
- Production-grade ingestion pipeline
- Full personalization loop (analytics + retraining)
- Better UX and mobile-ready frontend
- Licensing/partnership workflows
- Scalable datastore (Postgres + vector index)

---

## Next Technical Tasks (recommended order)
1. Run `clean_glyphs.py` in dry-run mode over all glyphs (audit output)
2. Review audit artifacts and adjust schema vocabulary
3. Commit cleaned glyphs to `src/emotional_os_glyphs/canonical_cleaned/`
4. Implement ingestion validation to quarantine nonconformant glyphs
5. Build the emotional tagging pipeline (LLM + audio embeddings)

---

## Security & Privacy
- OAuth tokens never stored plaintext in repo
- Personalization data stored per-user with opt-in and deletion workflows

---

## Where this sits relative to Velinor/Draftshift
- IFY is an independent product but can reuse `emotional OS` artifacts (glyphs, arcs)
- Start with the shared canonical glyph store; make Velinor consume via a well-defined API

---

## Ready to proceed
I will now create the authoritative `glyph_schema.json` and a safe cleaning script `clean_glyphs.py` in `Offshoots/IFY`. After that I can run a dry-run audit over the repository glyph folders if you want. Do you want me to proceed and run the auditor now?