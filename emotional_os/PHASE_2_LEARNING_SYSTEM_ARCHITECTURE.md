# Phase 2, Learning System Architecture (Placeholder)

This placeholder describes the high-level architecture used in Phase 2 for the learning/limbic subsystem.

Sections to expand

- Data flow (client → server extractor → limbic decorator)
- Storage: conversation history table, deletion audit
- Key modules and responsibilities:
  - `learning/lexicon_learner.py`, learning and updates
  - `emotional_os/glyphs/limbic_integration.py`, decorator and telemetry
  - `supabase/functions/saori-fixed/index.ts`, extractor and glyph parsing

Next steps

- Add diagrams and sequence flows
- Add scaling and monitoring notes (metrics to collect)
