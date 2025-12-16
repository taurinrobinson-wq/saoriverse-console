# FirstPerson deployment notes — Nginx + Streamlit

This document describes a simple deployment pattern that keeps the public static site
at the root of `firstperson.chat` while proxying the Streamlit application to `/app/`.

Files added in this repo:
- `deploy/nginx.conf` — Nginx server block template (adjust paths and enable on your server)
- `.streamlit/config.toml` — Streamlit config (already added) with `baseUrlPath = "/app"` recommended

Goals:
- Public site (static) served at `https://firstperson.chat/` (no Streamlit UI controls exposed)
- Streamlit app served at `https://firstperson.chat/app/` behind Basic Auth (optional)

## Step-by-step

1) Prepare your static site

   - Build or copy the `static/` folder to your server, e.g. `/var/www/firstperson/static/`.
   - Ensure `index.html` is at `/var/www/firstperson/index.html` (or adjust `root` in `deploy/nginx.conf`).

2) Configure Streamlit

   - In the repo we include `.streamlit/config.toml`. Ensure it contains:

     ```toml
     [server]
     headless = true
     baseUrlPath = "/app"
     port = 8501
     enableCORS = false
     enableXsrfProtection = true
     ```

   - Deploy Streamlit on the host and bind to localhost (127.0.0.1) so it is only reachable via the proxy.
     Example systemd unit should set `WorkingDirectory` to the repo and run `streamlit run main_v2.py`.

3) Enable Basic Auth for `/app/` (optional but recommended)

   - Install `apache2-utils` (Debian/Ubuntu):

     ```bash
     sudo apt update && sudo apt install -y apache2-utils
     sudo htpasswd -c /etc/nginx/.htpasswd deployer
     # supply a secure password when prompted
     ```

   - The `deploy/nginx.conf` template references `/etc/nginx/.htpasswd`. You can disable `auth_basic`
     lines if you prefer another auth mechanism (OAuth, Cloudflare Access, etc.).

4) Install the Nginx config

   - Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/firstperson` and enable it:

     ```bash
     sudo cp deploy/nginx.conf /etc/nginx/sites-available/firstperson
     sudo ln -s /etc/nginx/sites-available/firstperson /etc/nginx/sites-enabled/firstperson
     sudo nginx -t && sudo systemctl reload nginx
     ```

5) Point DNS / CNAME

   - Point your domain `firstperson.chat` (and optionally `www.firstperson.chat`) to the server IP.
   - If you use a static site host (Netlify/Cloudflare Pages/GitHub Pages), point the root to that host
     and configure your proxy to use the same domain for the `/app/` path (see hosting docs for rewrites).

6) Switching Streamlit off the root domain

   - Do not bind Streamlit to 0.0.0.0 on port 80. Keep it on `127.0.0.1:8501` and let Nginx proxy `/app/` to it.
   - This ensures the root domain is controlled by static files and any Streamlit hosting UI remains hidden.

7) Troubleshooting the logo / SVG assets

   Problem: logo SVG or image not appearing when Streamlit is served under `/app/`.

   Cause: image `src` paths may be relative (e.g., `static/graphics/logo.svg`) which become `/app/static/...` when
   the page is under `/app/`. If your static files are served at root (`/static/...`), the missing leading slash
   causes 404s.

   Fixes:
  - Use absolute paths for static assets in Streamlit templates, e.g. `/static/graphics/FirstPerson-Logo-normalized.svg`.
     We updated the app to reference `/static/...` so the browser fetches assets from the public root instead of `/app`.
   - Ensure Nginx `location /static/` serves the `static/` folder and has correct MIME types (Nginx does this by default).
   - If SVGs are still served with incorrect content-type, add in the nginx conf inside `http {}`:

     ```nginx
     types { image/svg+xml svg; }
     ```

   - Check browser devtools network tab for 404 or other errors and validate the requested URL.

8) Final checks

   - Start Streamlit: `streamlit run main_v2.py` (ensure it's using `.streamlit/config.toml`) and check `http://127.0.0.1:8501/app/`.
   - Visit `https://firstperson.chat/` for the static site and `https://firstperson.chat/app/` for the proxied Streamlit app.

   ## Railway-specific notes

   If you deploy on Railway, the repo includes a `railway.json` and a small helper `emotional_os/deploy/railway_start.sh`.

   - By default the Railway start command will run the `railway_start.sh` script which sets `SERVE_STATIC_CHAT=1` and starts Uvicorn.
   - Make sure to set the following Railway environment variables in the Railway project settings (Settings → Variables):
      - `SUPABASE_URL` = your Supabase URL
      - `SUPABASE_KEY` = your Supabase anon or service key (follow least-privilege; prefer anon+Edge Functions)
      - `SECRET_KEY` = a 32-byte hex string (use `python -c "import secrets; print(secrets.token_hex(32))"`)
      - (optional) `CURRENT_SAORI_URL` = override for AI function URL

   - The Railway container will serve the static site at `/` (templates/index.html) and `/app` will return `templates/chat.html` as long as `SERVE_STATIC_CHAT=1` is set. This makes Railway act as the public host for the static site. If you prefer to host static files separately (Netlify/Vercel), set `SERVE_STATIC_CHAT=0` and instead publish static assets to your static host, while using Railway for dev/admin APIs.

   Security reminder:
   - If you keep Streamlit or admin endpoints on Railway, secure them (OAuth, basic auth, or restrict by IP). The static site should use Supabase Auth and Edge Functions for any server-side operations.

## Security notes
- Prefer an OAuth proxy (Cloudflare Access, oauth2-proxy) over basic auth for production.
- Ensure TLS/HTTPS termination at Nginx (Let's Encrypt / Certbot) before exposing the site publicly.
