# Quick Reference - Deployment

**TL;DR: No new app needed. Just push to Railway and it auto-redeploys.**

---

## The One File That Changed

**Procfile** (this is what Railway reads):

```diff
- web: python core/start.py
+ web: streamlit run app.py
```

That's it. Everything else stays the same.

---

## Why

- Old path (`core/start.py`) doesn't exist after reorganization
- New path (`app.py`) is the single Streamlit entry point
- Railway auto-detects Procfile changes and redeploys

---

## What You Do

```bash
# Already done:
# 1. ✅ Procfile updated

# Still needed:
# 2. git push origin refactor/reorganization-master
# 3. Railway auto-redeploys (~2-3 minutes)
# 4. Visit your Railway URL
# 5. Verify it works
```

---

## What Users See

Exactly the same app at the exact same URL. No difference.

---

## What Devs Get

Cleaner code organization. Better for maintenance.

---

## Rollback

If something goes wrong:
```bash
git revert HEAD
git push origin refactor/reorganization-master
```

Railway redeploys to previous version.

---

## Full Details

See: `docs/DEPLOYMENT_GUIDE.md`

---

**Status**: ✅ Ready to deploy
**Time**: ~10 minutes total
**Risk**: Very low (one-line Procfile change)
