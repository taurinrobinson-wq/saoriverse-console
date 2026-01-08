# Parallel Folder Structure Synchronization

This document defines how `velinor/` (Python game engine) and `velinor-web/` (Next.js frontend) folders are kept in parallel.

## Folder Structure

```
saoriverse-console/
├── velinor/                          # Python game engine
│   ├── engine/                       # Core game logic (Python)
│   │   ├── npc_manager.py           # NPC trait system
│   │   ├── npc_dialogue.py          # Dialogue generation
│   │   ├── npc_encounter.py         # Scene composition
│   │   └── resonance.py             # Trait resonance
│   ├── data/                         # Game data (JSON)
│   │   ├── npc_profiles.json        # ← SYNCED →
│   │   └── influence_map.json       # ← SYNCED →
│   ├── backgrounds/                 # Background images
│   │   ├── Velhara_background_title(blur).png  # ← SYNCED →
│   │   ├── Velhara_background_title.png        # ← SYNCED →
│   │   └── velinor_title_eyes_closed.png       # ← SYNCED →
│   ├── npcs/                         # NPC portrait images
│   │   ├── velinor_eyesclosed2.png  # ← SYNCED →
│   │   ├── velinor_eyesclosed.png   # ← SYNCED →
│   │   └── [other NPC images]
│   ├── overlays/                     # UI overlay graphics
│   │   ├── velinor_title_transparent2.png  # ← SYNCED →
│   │   └── velinor_title_transparent.png   # ← SYNCED →
│   ├── stories/                      # Test & demo files (Python)
│   ├── tests/                        # Test suites
│   └── README.md
│
└── velinor-web/                      # Next.js web frontend
    ├── src/
    │   ├── app/                      # Next.js app routing
    │   ├── components/               # React components
    │   │   └── TitleScreen.tsx       # Title screen (uses synced assets)
    │   ├── data/                     # Game data (JSON)
    │   │   ├── npc_profiles.json    # ← SYNCED ← (copy from velinor/data/)
    │   │   └── influence_map.json   # ← SYNCED ← (copy from velinor/data/)
    │   └── lib/                      # Utilities
    ├── public/
    │   └── assets/                   # Served images (symlinked or copied)
    │       ├── backgrounds/          # ← SYNCED ← (from velinor/backgrounds/)
    │       ├── npcs/                 # ← SYNCED ← (from velinor/npcs/)
    │       └── overlays/             # ← SYNCED ← (from velinor/overlays/)
    ├── sync-parallel.ps1             # Sync script (PowerShell)
    ├── sync-parallel.sh              # Sync script (Bash)
    └── README.md
```

## Synchronization Strategy

### Files that are SYNCED (One Source of Truth)

| Item | Source | Target | Type | Frequency |
|------|--------|--------|------|-----------|
| NPC Profiles | `velinor/data/npc_profiles.json` | `velinor-web/src/data/npc_profiles.json` | Data | After NPC updates |
| Influence Map | `velinor/data/influence_map.json` | `velinor-web/src/data/influence_map.json` | Data | After relationship updates |
| Backgrounds | `velinor/backgrounds/` | `velinor-web/public/assets/backgrounds/` | Images | After art changes |
| NPC Images | `velinor/npcs/` | `velinor-web/public/assets/npcs/` | Images | After character updates |
| Overlay Graphics | `velinor/overlays/` | `velinor-web/public/assets/overlays/` | Images | After UI changes |

### Files that are INDEPENDENT

| Folder | Purpose | Dependencies |
|--------|---------|--------------|
| `velinor/engine/` | Python game logic | Reads from `velinor/data/` |
| `velinor/stories/` | Test scenarios | Uses `velinor/engine/` |
| `velinor/tests/` | Unit tests | Uses `velinor/engine/` |
| `velinor-web/src/components/` | React UI | Reads from `velinor-web/src/data/` and public assets |
| `velinor-web/src/app/` | Next.js routing | Uses components |

## Sync Scripts

### PowerShell (Windows)

```powershell
# velinor-web/sync-parallel.ps1
# Usage: cd velinor-web; powershell -ExecutionPolicy Bypass -File sync-parallel.ps1
```

### Bash (macOS/Linux)

```bash
# velinor-web/sync-parallel.sh
# Usage: cd velinor-web; bash sync-parallel.sh
```

## Development Workflow

### When Updating NPCs in Python

1. Edit `velinor/engine/npc_manager.py` or `velinor/data/npc_profiles.json`
2. Run sync script: `powershell -File sync-parallel.ps1`
3. Verify changes in web frontend
4. Commit both changes together

### When Adding New Background Images

1. Add image to `velinor/backgrounds/`
2. Update velinor code if needed
3. Run sync script: `powershell -File sync-parallel.ps1`
4. Verify image loads in web frontend
5. Commit both changes together

### When Modifying UI Overlays

1. Edit image in `velinor/overlays/`
2. Run sync script: `powershell -File sync-parallel.ps1`
3. Web frontend auto-refreshes
4. Commit changes

## Git Strategy

### Recommended .gitignore Rules

**In `velinor/.gitignore`:**
```
__pycache__/
*.pyc
.pytest_cache/
```

**In `velinor-web/.gitignore`:**
```
node_modules/
.next/
.env*.local
```

### Commit Strategy

Keep sync'd files in both repositories with a unified commit message:

```bash
git add -A
git commit -m "feat: Update NPC dialogue system and sync web assets

Changes:
- Enhanced Velinor dialogue lexicon in npc_dialogue.py
- Updated influence_map.json with new relationships
- Synced data to velinor-web for frontend use

Engine: velinor/engine/npc_dialogue.py
Data: velinor/data/influence_map.json
Web: velinor-web/src/data/influence_map.json"
```

## Verification Checklist

After syncing, verify:

- [ ] `velinor-web/src/data/npc_profiles.json` matches `velinor/data/npc_profiles.json`
- [ ] `velinor-web/src/data/influence_map.json` matches `velinor/data/influence_map.json`
- [ ] All images in `velinor-web/public/assets/backgrounds/` exist
- [ ] All images in `velinor-web/public/assets/npcs/` exist
- [ ] All images in `velinor-web/public/assets/overlays/` exist
- [ ] Web frontend loads without 404 errors
- [ ] Python engine still runs: `python -m velinor.engine.quickstart`

## Troubleshooting

### Web images not loading

1. Check browser console for 404 errors
2. Verify sync script ran successfully
3. Check file exists: `ls velinor-web/public/assets/backgrounds/`
4. Restart dev server: `npm run dev`

### JSON data not updating

1. Verify file was copied: `diff velinor/data/npc_profiles.json velinor-web/src/data/npc_profiles.json`
2. Re-run sync script
3. Clear Next.js cache: `rm -rf .next`
4. Restart dev server

### Out of sync after merge

If you see conflicts after merging:

```bash
# Re-run sync to ensure parallel consistency
cd velinor-web
powershell -File sync-parallel.ps1

# Commit the sync
git add -A
git commit -m "chore: Resync parallel folders after merge"
```

## Future Enhancements

1. **Automated sync on file watch** - Watch `velinor/data/` and auto-sync on changes
2. **TypeScript NPC types** - Generate `.d.ts` from npc_profiles.json
3. **Asset optimization** - Automatic image compression before sync
4. **Continuous sync** - GitHub Actions workflow to sync on commit
5. **Conflict detection** - Script to detect out-of-sync files

## Monitoring

Keep these commands bookmarked for quick checks:

```bash
# Check if data is in sync
diff velinor/data/npc_profiles.json velinor-web/src/data/npc_profiles.json

# Find missing images in web
diff <(ls -1 velinor/backgrounds/) <(ls -1 velinor-web/public/assets/backgrounds/)

# Check all sync'd files
find velinor/data -name "*.json" -exec diff {} velinor-web/src/data/{} \;
```

---

**Last Updated:** December 16, 2025  
**Status:** Active  
**Sync Frequency:** As needed (typically after NPC/data changes)
