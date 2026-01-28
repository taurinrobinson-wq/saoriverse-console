# DraftShift Web UI - Replit Deployment Guide

## Overview

Deploy DraftShift Web UI to Replit for free hosting at `https://draftshift.replit.dev` (or your custom subdomain).

## Prerequisites

- GitHub repository with DraftShift code committed
- Replit account (free: https://replit.com)
- No credit card required for free tier

## Step-by-Step Deployment

### Step 1: Create Replit Project

1. Go to [replit.com](https://replit.com)
2. Click "Create" → "Import from GitHub"
3. Paste your GitHub repository URL
4. Click "Import"
5. Replit clones your repo and auto-detects environment

### Step 2: Verify Configuration Files

Replit reads these files from `draftshift-web/`:

**`.replit`** — Run configuration
```
run = "python -m uvicorn api:app --host 0.0.0.0 --port 8000"
```

**`replit.nix`** — Dependency specification
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs_20
  ];
}
```

Both files should exist in `draftshift-web/` directory.

### Step 3: Install Dependencies (Auto or Manual)

Replit should auto-install, but if needed, click Shell and run:

```bash
# Install Node dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
pip install -r ../requirements-backend.txt
```

### Step 4: Build React Frontend

The React frontend must be built before serving. In Replit Shell:

```bash
npm run build
```

This creates `draftshift-web/dist/` with production-optimized files.

### Step 5: Configure Environment (Optional)

If DraftShift engine needs special configuration, create `.env`:

```bash
# In Replit Shell
echo "DEBUG=false" > .env
echo "LOG_LEVEL=info" >> .env
```

### Step 6: Start Application

Click "Run" button in Replit. You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 7: Access Web UI

Replit displays a "Webview" panel showing your app. Click the domain link:

- **Format**: `https://[replit-project].replit.dev`
- **Example**: `https://draftshift.replit.dev`

The React UI loads, proxied through FastAPI backend.

## How It Works on Replit

```
┌─────────────────────────────────────────┐
│         Browser at replit.dev           │
└─────────────────┬───────────────────────┘
                  │
       ┌──────────▼──────────┐
       │ HTTP Request to API │
       └──────────┬──────────┘
                  │
       ┌──────────▼──────────────────────┐
       │   FastAPI (port 8000)           │
       │  ┌────────────────────────────┐ │
       │  │ /api/* endpoints           │ │
       │  │  ├─ /api/health            │ │
       │  │  ├─ /api/build             │ │
       │  │  └─ /api/fixtures/{name}   │ │
       │  └────────────────────────────┘ │
       │  ┌────────────────────────────┐ │
       │  │ Static Files (React)       │ │
       │  │ Serves dist/ on GET /      │ │
       │  └────────────────────────────┘ │
       └──────────┬───────────────────────┘
                  │
       ┌──────────▼──────────┐
       │ DraftShift Engine   │
       │ (Python modules)    │
       │  ├─ pleadings/      │
       │  ├─ formats/        │
       │  └─ tests/          │
       └─────────────────────┘
```

## File Structure (Deployed)

```
Replit Workspace Root
├── draftshift/                # DraftShift engine (Python)
│   ├── pleadings/
│   ├── formats/
│   └── tests/
├── draftshift-web/            # Web UI (React + FastAPI)
│   ├── api.py                 # FastAPI backend
│   ├── package.json           # Node deps
│   ├── vite.config.js         # Vite config
│   ├── index.html             # HTML entry
│   ├── .replit                # Replit config
│   ├── replit.nix             # Replit deps
│   ├── src/                   # React source
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   └── components/
│   └── dist/                  # Built React (generated)
└── ...
```

## Troubleshooting

### Issue: "Port 8000 already in use"

**Solution**: Replit closes old processes. Click "Stop" then "Run" to restart.

### Issue: "Module 'draftshift' not found"

**Solution**: The `draftshift` package must be importable. Either:

Option A: Install as package
```bash
pip install -e ../draftshift
```

Option B: Ensure PYTHONPATH includes parent directory
```bash
# Add to api.py at top:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Issue: "React not building"

**Solution**: Verify build output
```bash
npm run build
ls -la dist/
```

Should show: `index.html`, `assets/`, etc. in `dist/` folder.

### Issue: "Fixtures not loading"

**Solution**: Verify fixture files exist
```bash
ls draftshift/tests/fixtures/
```

Should show: `motion.json`, `opposition.json`, `reply.json`, `declaration.json`

### Issue: "CORS errors in browser console"

**Solution**: The backend should have CORS enabled. In `api.py`, verify:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Replit times out after 1 hour"

**Solution**: Replit free tier hibernates after inactivity. To keep alive:
- Keep browser tab open
- Or upgrade to Replit paid tier
- Or set up a monitoring service (e.g., UptimeRobot)

## Monitoring & Logs

View application logs in Replit:

1. Click "Tools" → "Shell"
2. View logs:
```bash
# Recent logs
tail -f .replit.log

# Or run app in foreground
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

## Performance Tips

- **Vite is fast** for React development
- **FastAPI is lightweight** — minimal overhead
- **Replit free tier** — good for prototyping, consider upgrade for production traffic
- **Consider caching** — generated DOCX files rarely change for same input

## Updating Code

To deploy updates:

1. Commit changes to GitHub:
```bash
git add -A
git commit -m "Update UI components"
git push origin main
```

2. In Replit, click "Pull" to sync latest code

3. If dependencies changed, reinstall:
```bash
npm install
pip install -r requirements.txt
```

4. Click "Run" to restart app

## Custom Domain (Optional)

To use custom domain instead of `replit.dev`:

1. Go to Replit project → "Tools" → "Domain"
2. Enter custom domain (e.g., `draftshift.yourdomain.com`)
3. Update DNS records per Replit instructions
4. SSL certificate auto-provisioned

## Security Considerations

**Current setup (for prototyping):**
- ✅ CORS allows all origins (for testing)
- ✅ No authentication (public API)
- ✅ No rate limiting (free tier)
- ✅ No input validation

**For production deployment:**
- [ ] Restrict CORS to known domains
- [ ] Add API key authentication
- [ ] Implement rate limiting
- [ ] Validate & sanitize all inputs
- [ ] Add request logging/monitoring
- [ ] Consider upgrading to Replit paid for better uptime

## Next Steps

After deployment:

1. **Test thoroughly**
   - Load fixtures
   - Edit JSON
   - Build pleadings
   - Download DOCX files

2. **Monitor usage**
   - Check Replit logs
   - Monitor response times
   - Track errors

3. **Iterate**
   - Add new features
   - Improve UX
   - Optimize performance

4. **Scale** (if needed)
   - Move to paid Replit
   - Upgrade to dedicated server
   - Add database/caching layer

## Support

- **DraftShift Issues**: See main repository
- **Replit Help**: [replit.com/support](https://replit.com/support)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React Docs**: [react.dev](https://react.dev)

## Summary

You now have:
- ✅ DraftShift Web UI deployed on Replit
- ✅ FastAPI backend generating pleadings
- ✅ React frontend for user interaction
- ✅ Free hosting at `draftshift.replit.dev`
- ✅ Auto-SSL and monitoring from Replit
- ✅ Easy code updates via GitHub sync

Enjoy using DraftShift! 🎉
