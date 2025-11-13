# Custom Internal Token Usage

This project uses a small custom token format for internal edge function authentication.
The token is intentionally simple (base64 payload + signature) and is NOT a standard JWT.

Format

- token = base64(payload).signature
- payload JSON keys: `user_id`, `username`, `issued_at` (ms epoch), `expires_at` (ms epoch)
- signature = base64(user_id + '_' + issued_at)

Why we use a custom header

- Supabase / Cloudflare may validate `Authorization` headers and expect Supabase-issued JWTs.
- To avoid platform-level JWT rejection for our internal tokens, functions accept them in the
  `X-Custom-Token` header (format: `Bearer <token>`).
- Platform-level API keys (anon/service role) should still be sent in `Authorization` or `apikey` headers
  so Supabase middleware can allow the request through.

Usage (curl)

Anonymous (platform anon key):

curl -X POST "<https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/authenticated-saori>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <PROJECT_ANON_KEY>" \
  -d '{"message":"Hello","mode":"quick"}'

Authenticated (custom token):

curl -X POST "<https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/authenticated-saori>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <PROJECT_ANON_KEY>" \
  -H "X-Custom-Token: Bearer <CUSTOM_TOKEN>" \
  -d '{"message":"Hello","mode":"quick","user_id":"<USER_ID>"}'

Security notes and recommendations

- This custom token format is convenient for prototyping but not cryptographically secure.
- Recommended improvements:
  - Use proper signed JWTs (RS256/HS256) and have `auth-manager` sign tokens with a private key
    that the functions can verify (or use Supabase Auth to mint tokens).
  - Add rotation and revocation (store a short-lived token table or use a revocation list).
  - Use `X-Custom-Token` only over HTTPS and avoid logging the raw token. Log only token presence or user id.
  - Limit accepted token life and validate `issued_at` and `expires_at` strictly (a small clock skew is tolerated).

Files changed

- `supabase/functions/authenticated-saori/index.ts` — accepts `X-Custom-Token` and improved validation
- `supabase/functions/saori-fixed/index.ts` — same behavior and improved validation

If you want, I can replace this with proper signed JWT issuance and verification (recommended).
