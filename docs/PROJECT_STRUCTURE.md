# Project Structure Guide

## 📂 Directory Layout

```text
```

saoriverse-console/
│
├── README.md                 # Main project README (start here)
├── CONTRIBUTING.md           # Contribution guidelines
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules (prevents clutter)
│
├── src/                     # Main source code (already organized)
│   ├── emotional_os/        # FirstPerson system
│   ├── parser/              # NLP parsing modules
│   └── deploy/              # Deployment and UI modules
│
├── tests/                   # Unit tests
│
├── scripts/                 # Helper scripts and utilities
│   ├── RUN_WEB_DEV.sh      # Start Velinor web dev server
│   ├── RUN_FULL_STACK.sh   # Start frontend + backend together
│   └── *.py                # Utility scripts
│
├── docs/                    # Curated documentation (intentional only)
│   ├── PROJECT_STRUCTURE.md # This file
│   ├── QUICK_REFERENCE_*.md # Quick references for each system
│   ├── VELINOR_*.md        # Velinor game documentation
│   ├── FIRSTPERSON_*.md    # FirstPerson system docs
│   ├── LEARNING_*.md       # Learning system docs
│   ├── PRIVACY_*.md        # Privacy layer docs
│   ├── DEPLOYMENT_*.md     # Deployment guides
│   └── ...                 # Other curated guides
│
├── scratch/                 # Auto-generated clutter (NOT tracked in git)
│   ├── auto_summaries.md   # AI-generated summaries
│   ├── temp_notes.md       # Temporary work notes
│   └── ...                 # Other temporary files
│
├── velinor/                # Velinor game (Streamlit version)
│   ├── engine/            # Game logic
│   ├── stories/           # Story JSON files
│   ├── backgrounds/       # Background images
│   ├── npcs/             # NPC character portraits
│   └── markdowngameinstructions/
│
├── velinor-web/          # Velinor game (Next.js web version)
│   ├── src/
│   │   ├── app/         # Pages and routes
│   │   ├── components/  # React components
│   │   └── styles/      # CSS
│   ├── public/
│   │   └── assets/      # Graphics (backgrounds, NPCs, etc)
│   └── package.json
│
├── firstperson-web/      # FirstPerson web interface
│   ├── src/
│   └── public/
│
├── velinor_app.py        # Streamlit game app
├── velinor_api.py        # FastAPI backend
└── firstperson_api.py    # FirstPerson API

```



## 🎯 Guiding Principles

### 1. **Intentional Documentation**
- **docs/** = Curated guides you actively maintain
- **scratch/** = AI-generated summaries, temporary notes (auto-cleaned, not tracked)
- Root README.md = Single entry point, kept up-to-date

### 2. **Source Code Organization**
- All active source code lives in **src/**
- Avoids root "chaos" and keeps imports clean
- Tests in **tests/** mirror src structure

### 3. **Project-Specific Folders**
- **scripts/** = Reusable utilities and automation
- **velinor/** = Streamlit game implementation
- **velinor-web/** = Next.js web version
- **firstperson-web/** = FirstPerson chat interface

### 4. **Git Hygiene**
- scratch/ is in .gitignore (won't clutter history)
- .next/ build folders ignored
- Only committed files: source code, important docs, configs
##

## 🚀 Quick Start

### Start Development Servers

```bash


# Run just the web dev server
./scripts/RUN_WEB_DEV.sh

# Or run full stack (frontend + backend)

```text
```




### Install Dependencies

```bash
```text
```text
```



### Find What You Need
- **Game logic?** → Check `velinor/engine/` or `velinor-web/src/`
- **API endpoints?** → See `velinor_api.py` or `firstperson_api.py`
- **Story content?** → `velinor/stories/sample_story.json`
- **Setup instructions?** → Read `docs/QUICK_REFERENCE_*.md`
- **Deployment?** → See `docs/DEPLOYMENT_*.md`
##

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| `docs/QUICK_REFERENCE_*.md` | One-page cheat sheets for each system |
| `docs/VELINOR_*.md` | Game design, architecture, and setup |
| `docs/FIRSTPERSON_*.md` | Emotional analysis system docs |
| `docs/DEPLOYMENT_*.md` | Production deployment guides |
| `scratch/auto_summaries.md` | AI-generated overviews (temporary) |
##

## 🛠️ Development Workflow

### When AI Generates New Documentation
1. **Good docs** → Move to `docs/`
2. **Auto-summaries/clutter** → Stays in `scratch/` (auto-ignored by git)
3. **Temporary notes** → Keep in `scratch/` for reference, delete later

### Keeping It Clean

```bash


# Check what's in scratch (for cleanup decisions)
ls -la scratch/

# Remove temporary files safely
rm scratch/old_summary.md

# Verify .gitignore is working

```text
```




### Adding New Code
- Create files in `src/` or appropriate subfolder
- Add to `tests/` if it's a module with logic
- Update `requirements.txt` if adding dependencies
- Document in `docs/` (not root)
##

## 🌳 Why This Structure Matters

### Before (Root Chaos)

```
saoriverse-console/
├── PHASE_1_COMPLETE.md
├── IMPLEMENTATION_SUMMARY.md
├── BUG_FIX_REPORT.md
├── ANALYSIS_COMPLETE.md
├── ... 40+ more .md files
├── src/
```text
```text
```



❌ Hard to find what you need
❌ Git history cluttered with auto-generated files
❌ Can't tell important docs from summaries

### After (Clean Organization)

```

saoriverse-console/
├── README.md  (main entry point)
├── docs/      (intentional documentation)
├── scratch/   (temporary clutter, not tracked)
├── scripts/   (dev utilities)
├── src/       (source code)
└── velinor/   (game assets)

```



✅ Clear hierarchy
✅ Git tracks only what matters
✅ Easy to navigate and find things
✅ AI clutter contained
##

## 🔄 Maintenance Checklist

**Monthly:**
- [ ] Review `docs/` — keep it curated
- [ ] Clean `scratch/` — delete old temp notes
- [ ] Update root `README.md` if needed
- [ ] Run `git status` to verify no surprises

**Before Pushing:**
- [ ] No uncommitted changes in `src/`
- [ ] New dependencies added to `requirements.txt`
- [ ] Important docs moved to `docs/` (not root)
- [ ] `.gitignore` catches your junk
##

## 📖 Next Steps

1. **Explore the structure**: `ls -la` each folder to see what's there
2. **Read the quick references**: `docs/QUICK_REFERENCE_*.md`
3. **Start development**: `./scripts/RUN_WEB_DEV.sh`
4. **Keep it clean**: Use this structure as your guide
##

**Key Takeaway:** Treat `docs/` like a museum (curated, intentional) and `scratch/` like a junk drawer (temporary, disposable). Your git history stays clean. Your project stays sane. 🎯
