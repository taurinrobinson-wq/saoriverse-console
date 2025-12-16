Polishing and fallback response behavior

Summary

The UI and edge functions use a small reply "polishing" step to:

- Collapse duplicated short lines (e.g., repeated "I'm here to listen.")
- Replace short generic fallbacks with a deterministic rotated alternative so responses feel less repetitive
- Keep local-debug annotations ("Local decoding", glyphs) out of the main reply unless a developer explicitly enables them

Where the logic lives

- Python (UI & server-side): `emotional_os/deploy/reply_utils.py` exposes `polish_ai_reply(text: str) -> str`.
- Streamlit UI: the main renderer uses `polish_ai_reply` (or a local polish variant) to present user-facing replies.
- TypeScript/Deno edge functions: these contain a small `_stableChoice` helper and a short list of `_fallbackAlternatives`. Keep these in sync if you change alternatives.

Flags and toggles

- FP_SHOW_LOCAL_DECODING=1
  - When set (or the session flag `st.session_state['show_local_decoding'] = True`), the UI appends a compact bracketed debug line: `[Local decoding: ... | Resonant Glyph: ...]`.
  - Default: disabled (hidden from end users).

- FP_SHOW_PROCESSING_MODE=1
  - When set (or the session flag `st.session_state['show_processing_mode'] = True`), captions will show the Mode in addition to processing time.
  - Default: disabled (to avoid noisy UI captions).

How to change the fallback alternatives

- Python: edit `emotional_os/deploy/reply_utils.py` -> `alternatives` list.
- TypeScript/Deno: edit the `_fallbackAlternatives` array in edge functions (e.g., `enhanced_learning_edge_function.ts`, `optimized_edge_function.ts`, `authenticated-saori/index.ts`).

Testing

- The repo includes `tests/test_reply_polish.py` which verifies:
  - collapsing duplicate lines
  - replacing generic fallbacks with one of the alternatives
  - preserving long substantive replies

Local dev commands

- Run the single test file quickly:

```bash
pytest -q tests/test_reply_polish.py
```

- Run the Streamlit UI locally (optionally enable debug flags):

```bash
export FP_SHOW_LOCAL_DECODING=1
streamlit run emotional_os/deploy/modules/ui.py
```

Notes

- For cross-platform consistency we updated the main Deno edge functions and the web template. There are a few internal scripts (backups, logs) that still contain the literal fallback; they are non-user-facing and can be updated as needed.

If you'd like, I can centralize the TypeScript fallback logic into a shared module next so the same alternatives are reused across all functions.
