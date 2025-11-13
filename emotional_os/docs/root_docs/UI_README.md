UI choices — public static site vs private Streamlit dev

Overview
- This repository includes two user interfaces:
  1. A static HTML/JS frontend served from `emotional_os/deploy/templates/chat.html` and static assets in `static/`. This is intended to be deployed as a static site (Netlify, Vercel, S3+CloudFront) and talk to your backend via Supabase Edge Functions and Supabase Auth.
  2. A Streamlit-based developer UI (`main_v2.py`) used for fast iteration and admin/dev workflows. Keep Streamlit private and run it locally or behind an authenticated/proxied path (for example `/app/` behind basic auth).

Which to run when
- Local development / fast iteration: run the Streamlit UI

  ```bash
  # create venv, install deps, then
  streamlit run main_v2.py
  ```

- Production static public site: build/deploy the files under `emotional_os/deploy/templates/` and `static/` to your static host.

Making the static site talk to your backend (Supabase)
- Configure your Supabase Edge Function URL by embedding a meta tag on the static host, or by providing a small inline config object before the page loads. Example meta tags to add to the host's HTML headers:

  <meta name="edge-function-url" content="https://<REGION>.functions.supabase.co/saori-fixed">
  <meta name="validate-session-url" content="https://your-admin-host/api/validate-session">

- The static site defaults to `/api/chat` and `/api/validate-session` for convenience during local dev where you might run the FastAPI server. For production, set those meta tags or set `window.__FP_CONFIG` before the chat page loads.

Keeping Streamlit private
- Do not expose Streamlit on the root domain. Best practice:
  - Serve static site at `https://firstperson.chat/` (Netlify/Vercel/S3)
  - Proxy Streamlit behind `/app/` and protect with basic auth, VPN, or an internal-only host. Example Nginx: proxy `/app/` to `127.0.0.1:8501` and require auth.

Notes
- We intentionally gate `/app` on the FastAPI server with `SERVE_STATIC_CHAT` so production containers do not accidentally serve the static site.

If you'd like, I can add a GitHub Actions workflow to publish `templates/chat.html` and `static/` to Netlify automatically on push.
