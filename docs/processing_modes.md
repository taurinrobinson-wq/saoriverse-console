### 🔀 Processing Modes: Local vs Hybrid

This system supports multiple processing modes, controlled via environment variables:

| Mode | Description |
|------|-------------|
| `local` | Fully offline. No remote AI calls allowed. Default mode. |
| `hybrid` | Enables remote AI (e.g., OpenAI, Supabase hybrid processors). |
| `premium` | Optional tier for image/music generation or advanced hybrid features. |

#### 🔐 Remote AI Opt-In

To enable remote AI calls (e.g., OpenAI, Supabase hybrid processors):

```bash
export PROCESSING_MODE=hybrid
export ALLOW_REMOTE_AI=1
```

Behavior notes:

- In `local` mode the codebase defaults to privacy-first behaviour. Any attempt to initialize or call remote AI clients from guarded factory functions will either:
  - raise a `RuntimeError` in Python (when explicit config or env vars are provided), or
  - return `None` from factory functions so local-only fallbacks continue to work.
- In edge functions (serverless/TypeScript), guarded functions will return a 403 response when remote AI is disabled.

This pattern ensures that hybrid/OpenAI code remains present for opt-in usage, but cannot
accidentally run (and incur cost or leak data) in default local development environments.

If you need to enable remote AI temporarily for testing, set `ALLOW_REMOTE_AI=1` in your
environment. For production deployments, prefer setting `PROCESSING_MODE=hybrid` and ensure the
appropriate secrets (e.g., `OPENAI_API_KEY`, `SUPABASE_*`) are set in your deployment environment.
