# Parallel Folder Maintenance - Quick Reference

## Current Status

✅ **Both folders are now synchronized:**
- `velinor/` (Python engine) - Source of truth for data & assets
- `velinor-web/` (Next.js frontend) - Consumer of synced data & assets

## What's Synced

### Data Files (JSON)
- `npc_profiles.json` - NPC trait definitions (25 copies synced)
- `influence_map.json` - NPC relationship graph (21 copies synced)

### Image Assets
- `backgrounds/` - 25 environment images
- `npcs/` - 21 character portraits
- `overlays/` - 4 UI overlay graphics

**Total:** 50 files synced across both folders

## Quick Commands

### Sync Everything
```powershell
cd velinor-web
powershell -ExecutionPolicy Bypass -File sync-parallel.ps1
```

### Verify Sync Status
```bash
# Check if files match
diff velinor/data/npc_profiles.json velinor-web/src/data/npc_profiles.json

# List all backgrounds in web
ls -1 velinor-web/public/assets/backgrounds/ | wc -l
```

### After Any Update
1. Make changes in `velinor/` (engine logic, data, or images)
2. Run sync script: `sync-parallel.ps1`
3. Commit both folders together

## Folder Structure

```
velinor/                               ← Engine (Python, source of truth)
├── data/
│   ├── npc_profiles.json             ← Source
│   └── influence_map.json            ← Source
├── backgrounds/ ← Source of backgrounds
├── npcs/        ← Source of character images
└── overlays/    ← Source of UI graphics

velinor-web/                           ← Frontend (Next.js, synced copy)
├── src/data/
│   ├── npc_profiles.json             ← Synced copy
│   └── influence_map.json            ← Synced copy
└── public/assets/
    ├── backgrounds/                  ← Synced images
    ├── npcs/                         ← Synced images
    └── overlays/                     ← Synced images
```

## Common Tasks

### Adding a New NPC Portrait
1. Save PNG to `velinor/npcs/`
2. Update `velinor/data/npc_profiles.json` if needed
3. Run: `sync-parallel.ps1`
4. Verify in web: `http://localhost:3000`

### Updating NPC Traits
1. Edit `velinor/data/npc_profiles.json`
2. Run: `sync-parallel.ps1`
3. Test in Python engine: `python -m velinor.engine.quickstart`
4. Verify in web frontend

### Adding New Background
1. Save PNG to `velinor/backgrounds/`
2. Run: `sync-parallel.ps1`
3. Reference in game scenes
4. Verify loads in web

### Updating Game Logic
1. Edit `velinor/engine/npc_manager.py` etc.
2. If data changes, run: `sync-parallel.ps1`
3. Test Python engine
4. Web auto-reflects data changes on next load

## Sync Statistics

| Category | Count | Last Synced |
|----------|-------|-------------|
| Backgrounds | 25 | 2025-12-16 17:17 |
| NPCs | 21 | 2025-12-16 17:17 |
| Overlays | 4 | 2025-12-16 17:17 |
| Data Files | 2 | 2025-12-16 17:17 |
| **Total** | **52** | **Ready** |

## Troubleshooting

### Assets not loading in web
```powershell
# Re-sync
cd velinor-web
powershell -File sync-parallel.ps1

# Clear Next.js cache
rm -r .next

# Restart dev server
npm run dev
```

### Out of sync after merge
```bash
cd velinor-web
powershell -File sync-parallel.ps1
git add -A
git commit -m "chore: Resync parallel folders"
```

### Check sync status
```bash
# List all synced files
ls velinor/data/*.json
ls velinor-web/src/data/*.json

# Compare file counts
ls -1 velinor/backgrounds/*.png | wc -l
ls -1 velinor-web/public/assets/backgrounds/*.png | wc -l
```

## Git Workflow

When making changes affecting synced files:

```bash
# 1. Make changes
# Edit velinor/engine/npc_manager.py or data files

# 2. Sync
cd velinor-web
powershell -File sync-parallel.ps1

# 3. Test both
cd ../velinor
python -m velinor.engine.quickstart  # Test engine

cd ../velinor-web
npm run dev                          # Test web

# 4. Commit both
git add -A
git commit -m "feat: Update NPC system and sync web

- Engine: Enhanced dialogue in npc_dialogue.py
- Data: Updated npc_profiles.json with new traits
- Web: Synced to velinor-web/src/data/"
```

## File Integrity

All synced files are verified using MD5 checksums:
- Files with unchanged hash are skipped (faster sync)
- Only changed files are copied
- Verification step confirms all files present

## Next Updates

When you make changes, remember to:

1. ✅ Update source in `velinor/`
2. ✅ Run `sync-parallel.ps1`
3. ✅ Test both engine and web
4. ✅ Commit both folders

This keeps everything in sync and prevents frontend/backend mismatches.

---

**Last Updated:** December 16, 2025  
**Sync Status:** ✅ Ready  
**Next Sync:** After any NPC/data changes
