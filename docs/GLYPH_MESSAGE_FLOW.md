# Glyph / Message Processing Flow (from `main_v2.py`)

This document traces the runtime path a user message takes from the Streamlit entrypoint (`main_v2.py`) through the emotional parsing, glyph matching/creation, enrichment, fallback handling, and final response generation.

It is intended to restore architectural clarity and show the concrete functions, modules, and data shapes involved so you can follow the ritual of meaning flow through the codebase.

Sections

- Overview (quick path)
- Detailed step-by-step trace (call order + functions)
- Key data shapes and examples
- Fallbacks, caching, and safety gates
- Glyph learning & promotion
- Debugging tips and where to look for artifacts
##

## Overview (quick path)

- User interacts with the web UI served by `main_v2.py` (Streamlit).
- `main_v2.py` loads the UI renderer from `emotional_os.deploy.modules.ui_refactored` (either `render_main_app` or `render_main_app_safe`).
- The main chat input is rendered and when the user sends a message the UI pipeline:
  1. Optionally sanitizes text via `local_inference.preprocessor.Preprocessor` (if available).
  2. Calls the local parser: `emotional_os.glyphs.signal_parser.parse_input` (re-export of `emotional_os.core.signal_parser`).
  3. `parse_input` -> extracts signals, maps to ECM gates, queries the glyph DB, and scores glyphs.
  4. UI composes a payload for optional AI enhancement (saori function). If in `hybrid` mode, it sends local analysis + message to the remote AI endpoint.
  5. The AI reply (if any) is re-parsed locally to convert it into glyph-level signals and to produce the final local decoding.
  6. Optionally the `limbic` engine decorates/adjusts the reply.
  7. Fallback protocols are applied (safety/clarification flows).
  8. The assistant reply is emitted to the user with metadata (selected glyphs, scores, debug traces).

All of the above runs in `--dry-run` or demo mode when `supabase` secrets aren't configured; CI or production installs enable the hybrid AI endpoint and Supabase-backed persistence.
##

## Detailed step-by-step trace (call order + functions)

Below is a linear trace for the common `hybrid` pipeline. For `local` mode the AI call step is skipped.

1) Entry: `main_v2.py` -> `render_main_app()`
   - File: `main_v2.py`
   - The renderer imported from `emotional_os.deploy.modules.ui_refactored` is called.

2) UI: render chat input and wait for a submission
   - File: `emotional_os/deploy/modules/ui.py`
   - Function(s): chat input rendering (blocks around `input_col.chat_input(...)`) start the flow when `user_input` is non-empty.

3) Preprocessing (optional)
   - Module: `local_inference.preprocessor.Preprocessor` (best-effort; only if available)
   - Call: `p.preprocess(user_input, conversation_context)`
   - Output: `sanitized_text`, `intent`, `emotional_tags`, and `editorial_interventions`.

4) Select processing mode
   - `processing_mode` can be `local` or `hybrid` (session state / config). Default: `hybrid`.

5) Local parsing (always executed in both `local` and `hybrid` modes)
   - API: `from emotional_os.glyphs.signal_parser import parse_input`
   - Under the hood: `parse_input` forwards to `emotional_os.core.signal_parser` and returns a dict containing:
     - `glyphs`: list of candidate glyph dicts from DB
     - `voltage_response`: a short, local synthesized message
     - `ritual_prompt`: a short ritual or practice suggestion
     - `signals`: extracted emotional signals
     - `gates`: ECM gate activation list
     - `debug_sql`, `debug_glyph_rows` (optional debug info)

6) Inside `emotional_os.core.signal_parser` (key stages)
   - load signal lexicon: `load_signal_map(base_path)`
   - parse signals: `parse_signals(input_text, signal_map)`
       - tries: exact lexicon matches -> NRC lexicon fallback -> fuzzy matching
       - returns a list of signal dicts: { keyword, signal, voltage, tone }
   - evaluate gates: `evaluate_gates(signals)` maps signals to ECM gates (e.g., `Gate 2`, `Gate 4`, ...)
   - fetch glyphs: `fetch_glyphs(gates, db_path)` performs an SQLite query on `glyph_lexicon`
       - returns glyph rows with fields like `glyph_name`, `description`, `gate`, `display_name`, `response_template`
   - filter/prune artifact rows: `_looks_like_artifact(g)` and inline `_glyph_is_valid(g)` heuristics remove archive/pasted-document rows
   - select best glyph(s): `select_best_glyph_and_response(glyphs, signals, input_text, conversation_context)`
       - scoring boosts: signal-keyword matches, syntactic element matches (if `enhanced_emotion_processor` available), tone heuristics
       - returns: `best_glyph` (dict), `(response_text, feedback_data)` pair, `response_source`, and `glyphs_selected` (top N augmented glyphs)

7) Compose local response
   - `generate_contextual_response(best_glyph, signal_keywords, input_text, conversation_context)` builds a locally-composed empathetic response. This includes correction/feedback detection (`detect_feedback_correction`).

8) (Hybrid-only) Call AI enhancement service
   - If `processing_mode == 'hybrid'` and `saori_url`/`supabase_key` are configured, the UI posts a payload to `saori_url` (serverless function).
   - Payload includes: `message`, `mode`, `user_id`, `local_voltage_response`, `local_glyphs`, and optional `document_context`.
   - The remote returns `reply` and metadata.

9) Re-parse AI reply locally (SECOND PASS)
   - Purpose: preserve local decoding and ensure replies are grounded in local glyph logic.
   - Call: `parse_input(ai_reply, signal_lexicon_path, db_path, conversation_context)`
   - Merge: Compose final response combining `ai_reply` + `local decoding` (`ai_voltage`, `Resonant Glyph: ...`).

10) Limbic decoration (optional)
    - If `limbic_engine` present in session: `engine.process_emotion_with_limbic_mapping(user_input)` returns limbic mapping.
    - Decorator: `emotional_os.glyphs.limbic_decorator.decorate_reply(response, limbic_result)` may adjust tone/phrasing.

11) Fallback protocols (safety)
    - Module: `emotional_os.safety.fallback_protocols.FallbackProtocol`
    - Call: `fallback_protocol.process_exchange(user_text=user_input, detected_triggers=...)`
    - Result can trigger clarification behaviors (`should_ask_clarification`) or emergency escalation.

12) Avoid repetition and finalize
    - The UI guards against repeating the exact same assistant reply back-to-back and appends a small follow-up if needed.
    - Response (+ debug context) is appended to `st.session_state[conversation_key]` and displayed.

13) Learning / Logging (background)
    - The `HybridLearner` / `GlyphLearner` components record exchanges, update learned lexicons, and optionally create `glyph_candidates` when the system couldn't find a strong match.
    - Files / modules: `emotional_os/learning/hybrid_learner.py`, `emotional_os/glyphs/glyph_learner.py`
##

## Key functions & files (quick index)

- Entry UI: `main_v2.py` -> `emotional_os.deploy.modules.ui.render_main_app`
- Auth: `emotional_os.deploy.modules.auth.SaoynxAuthentication` (session token creation/validation)
- Local parse API: `emotional_os.glyphs.signal_parser.parse_input` (re-export) -> core implementation `emotional_os.core.signal_parser`
- Signal parsing: `parse_signals` in `core/signal_parser.py`
- Gate mapping: `evaluate_gates` in `core/signal_parser.py`
- DB lookup: `fetch_glyphs` reads `glyph_lexicon` from `emotional_os/glyphs/glyphs.db` (SQLite)
- Glyph selection/scoring: `select_best_glyph_and_response` (core)
- Response composition: `generate_contextual_response` (core)
- Glyph creation/learning: `emotional_os.glyphs.glyph_learner.GlyphLearner`
- Limbic decoration: `emotional_os.glyphs.limbic_decorator.decorate_reply`
- Fallback safety: `emotional_os.safety.fallback_protocols.FallbackProtocol`
##

## Key data shapes (examples)

- Signal (from `parse_signals`):

```json
{
  "keyword": "overwhelmed",
  "signal": "θ",
  "voltage": "high",
  "tone": "grief"
}
```



- Glyph row (from `fetch_glyphs` / DB):

```json
{
  "glyph_name": "Still Recognition",
  "description": "A practice of naming the ache and letting it be held.",
  "gate": "Gate 5",
  "display_name": "Still Recognition",
  "response_template": "I hear the ache you’re describing..."
}
```



- `parse_input` return (high-level):

```json
{
  "glyphs": [ ... ],
  "voltgage_response": "I notice a tightening in your chest...",
  "ritual_prompt": "Try a three-breath grounding...",
  "signals": [ ... ],
  "gates": ["Gate 4", "Gate 5"],
  "debug_sql": "SELECT ...",
  "debug_glyph_rows": [ ... ]
}
```


##

## Fallbacks, caching, and safety gates

- Preprocessor: `local_inference.preprocessor.Preprocessor` can sanitize, redact, or apply editorial interventions before parsing.
- Caching:
  - Inline SVG cache: `_SVG_CACHE` in `emotional_os.deploy.modules.ui._load_inline_svg` avoids repeated disk reads.
  - Session caching: `st.session_state` holds preprocessor, limbic engine, fallback protocol, and conversation history.
- AI/Hybrid fallback: If AI endpoint responds, the system always runs a SECOND local parse pass to re-anchor the AI text back into glyphs/signals.
- Fallback protocols: `emotional_os.safety.fallback_protocols` can intercept exchanges to ask clarifying questions or trigger safe messaging if input appears sensitive.
- Artifact filtering: `_looks_like_artifact` in `core/signal_parser.py` prunes pasted documents/archive rows from DB results before scoring.
##

## Glyph learning & promotion (how glyphs are created)

1. When `select_best_glyph_and_response` cannot find a suitable glyph, the learning pipeline can be triggered.
2. `GlyphLearner.analyze_input_for_glyph_generation` builds a candidate using:
   - Emotional language extraction
   - NRC lexicon (if available)
   - Semantic similarity to existing glyphs
   - Gate mapping from signals
3. Candidate glyphs are stored in `glyph_candidates` (SQLite) with `validation_status='pending'`.
4. Human review / offline heuristics may `promote_candidate_to_production(glyph_name)` which inserts into `glyph_lexicon`.

Notes:

- Glyph learning is conservative: confidence scores are capped below 1.0 and promotion requires explicit action.
- Usage is logged in `glyph_usage_log` so candidates with repeated usefulness can be promoted.
##

## Where to look for debugging info and artifacts

- Session-level debug variables (populated by the UI): `st.session_state['protocol_result_*']`, `debug_sql`, `debug_glyph_rows`.
- SQLite debug: `emotional_os/glyphs/glyphs.db` contains `glyph_lexicon`, `glyph_candidates`, and `glyph_usage_log`.
- Local preview/debugging helpers: `_last_glyphs_debug` global in `core/signal_parser.py` contains the last SQL and a preview of rows returned by `fetch_glyphs`.
- **Telemetry events (NEW)**: Enable via `signal_parser.set_telemetry(True)` or UI toggle to see JSON-formatted events like `select_best_start`, `generate_contextual_start`, `select_best_done` with detailed metrics.
- Reported artifacts from the cleanup pipeline (outside of runtime): `dev_tools/cleaned_glyphs.json`, `dev_tools/cleaned_glyphs_upsert.csv`, `dev_tools/cleanup_report.md`, and `dev_tools/fragments_to_review.json`.
##

## Edge cases and recommended hardening

- Sensitive input detection: ensure `emotional_os.safety.sanctuary.is_sensitive_input` is robust and invoked early to avoid leaking private content to remote AI.
- Artifact detection: tune `_looks_like_artifact` heuristics to avoid false negatives for valid long-form glyphs.
- Re-entrancy & DB locks: `GlyphLearner.log_glyph_candidate` uses retries and WAL mode — keep this pattern for other writers.
- Determinism: the `hybrid` second-pass ensures AI replies are always grounded locally. Never surface raw AI text without local decoding in production.
##

## Quick 'follow-the-message' checklist (for code readers)

1. `main_v2.py` -> `render_main_app()` (UI mount)
2. UI input handler in `emotional_os/deploy/modules/ui.py` (search for `chat_input("Share what you're feeling...")`)
3. Optional preprocessor (`local_inference.preprocessor.Preprocessor`)
4. `emotional_os.glyphs.signal_parser.parse_input` -> core parser
5. `parse_signals` -> `evaluate_gates` -> `fetch_glyphs`
6. `select_best_glyph_and_response` -> `generate_contextual_response`
7. (hybrid) post to `saori_url` and re-parse AI reply
8. (optional) limbic decoration and `FallbackProtocol` handling
9. Append to `st.session_state` and display
10. (background) `GlyphLearner` invoked when no suitable glyph found; writes to `glyph_candidates`
##

If you'd like, I can now:

- Generate a sequence diagram (Mermaid) for this flow.
- Produce a smaller developer cheat-sheet focused on the functions you should instrument for observability (logs/metrics/traces).
- Add code comments or in-source telemetry points at the key function boundaries above.

Which would you like next? (I can create the diagram or add instrumentation in a follow-up patch.)
