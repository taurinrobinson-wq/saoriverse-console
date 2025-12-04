# Deployment Guide - Post-Reorganization

**Date**: December 3, 2025
**Platform**: Railway (Streamlit)
**Status**: Ready to Deploy

---

## Quick Answer

**Do you need to re-deploy?** 

✅ **YES** - But it's a 2-minute update:

1. Update Procfile (already done)
2. Push branch to GitHub
3. Railway auto-redeploys (or manually trigger)

---

## What Changed

### Procfile (Updated)
**Before:**
```
web: python core/start.py
```

**After:**
```
web: streamlit run app.py
```

That's the only deployment file change needed.

### Why
- `core/start.py` no longer exists (moved and consolidated)
- `app.py` is now the single Streamlit entry point
- Streamlit command is the standard way to run

---

## Deployment Steps

### Step 1: Verify Local Build
```bash
# Test that the new structure works locally
cd /Volumes/My\ Passport\ for\ Mac/saoriverse-console
streamlit run app.py

# Should launch at http://localhost:8501
# Test the UI briefly to confirm it works
```

### Step 2: Verify Procfile
```bash
cat Procfile
# Should show: web: streamlit run app.py
```

### Step 3: Commit & Push
```bash
git add Procfile
git commit -m "deployment: Update Procfile for reorganized structure

- Change entry point from core/start.py to app.py
- Use standard streamlit run command
- Ready for Railway deployment"

git push origin refactor/reorganization-master
```

### Step 4: Deploy to Railway

**Option A: Auto-deploy via GitHub (if connected)**
1. Go to Railway dashboard
2. Click your project
3. It should auto-detect the push and redeploy
4. Wait for deployment to complete (~2-3 min)

**Option B: Manual redeploy**
1. Go to Railway dashboard
2. Go to your deployment
3. Click "Redeploy"
4. Select the latest commit
5. Wait for deployment

**Option C: Via Railway CLI**
```bash
# If you have railway CLI installed
railway deploy --branch refactor/reorganization-master
```

### Step 5: Verify Deployment
1. Go to your Railway deployment URL
2. App should launch normally
3. Test basic functionality:
   - Text input works
   - Response generated
   - No import errors in logs

---

## Expected Result

After deployment:
- ✅ App launches at same URL
- ✅ All features work the same
- ✅ No UI changes for users
- ✅ Backend is cleaner (devs benefit)

---

## No Breaking Changes

### For Users
- Same app, same features
- Same URL to access
- No action needed on their part

### For Devs
- Cleaner code structure
- Easier to test locally
- Better organized modules

---

## Rollback (If Needed)

If something goes wrong:

```bash
# Revert to previous deployment
git revert HEAD
git push origin refactor/reorganization-master

# Or manually select previous commit in Railway dashboard
```

---

## Environment Variables

**No changes needed** - Railway will keep all existing env vars from `.env.template`:
- `NRC_LEXICON_URL`
- `SUPABASE_*` keys
- `OPENAI_API_KEY`
- `MAINTENANCE_MODE`
- `PORT` (defaults to 8501 for Streamlit)

All continue to work as before.

---

## Streamlit Config

The `.streamlit/config.toml` already has correct settings:
- Port: 8501 (Railway uses this)
- Headless mode: enabled (for production)
- CORS enabled: true (for APIs)
- XSRF protection: disabled (for API access)

**No changes needed** to Streamlit config.

---

## Troubleshooting

### If deployment fails after push:

**Problem**: Railway shows "module not found" errors
**Solution**: 
- Check Procfile has `web: streamlit run app.py`
- Verify `requirements.txt` has all dependencies
- Check Railway logs for specific error

**Problem**: App times out during deployment
**Solution**:
- Railway default timeout is 5 minutes
- Streamlit should start in < 30 seconds
- Check if dependencies are installing correctly

**Problem**: App works locally but fails in Railway
**Solution**:
- Compare local vs Railway environment
- Check if any env vars are missing
- Look at Railway logs: Project → Deployment → Logs

---

## Testing Before/After

### Before Deployment (Local)
```bash
streamlit run app.py
# Should work fine
```

### After Deployment (Railway)
1. Go to your Railway project URL
2. Wait for page to load
3. Click in text input
4. Type a test message
5. Verify response generates
6. Check logs for any errors

---

## CI/CD Updates Needed

If you have GitHub Actions or other CI/CD:

**Check**: `.github/workflows/` for any hardcoded paths to `core/start.py`

**Update**: Change to `app.py`

**Common places to check**:
- `.github/workflows/deploy.yml`
- `.github/workflows/test.yml`
- Any scripts that reference old paths

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| Verify Procfile | 1 min | ✅ Done |
| Commit & push | 1 min | Ready |
| Railway redeploy | 2-3 min | After push |
| Verify app works | 2 min | After deploy |
| **Total** | **~7 min** | |

---

## Summary

### What to do:
1. ✅ Procfile already updated
2. ⏳ Commit changes: `git add Procfile && git commit`
3. ⏳ Push: `git push origin refactor/reorganization-master`
4. ⏳ Railway redeploys automatically
5. ⏳ Verify at your Railway URL

### What stays the same:
- App URL (unchanged)
- Features (unchanged)
- Env vars (unchanged)
- User experience (unchanged)

### What improves:
- Backend code organization
- Developer experience
- Maintenance ease
- Code discoverability

---

## Next Steps

1. **Merge to main** (after PR review)
2. **Update main branch** on Railway to auto-deploy
3. **Archive old structure** (already done)
4. **Start development** with new clean structure

---

**Ready to deploy!** The reorganization is production-ready with just the Procfile update.

For any issues, check Railway logs or reach out to the team.
