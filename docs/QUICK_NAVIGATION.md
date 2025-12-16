# Quick Navigation Guide

Welcome to SaoriVerse Console! This guide helps you find what you need quickly.

##

## 🚀 Getting Started (5 Minutes)

**First Time Here?** Start here:

1. Read `DEVELOPER_QUICKSTART.md` - Everything you need to know
2. Explore `docs/INDEX.md` - Navigation guide for all documentation
3. Check `FILE_ORGANIZATION_GUIDE.md` - Where everything is located

**Just Need to Run It?**

```bash
python core/main_v2.py        # Start Streamlit dev app
bash scripts/run_local.sh      # Run with full setup
```text
```text
```

##

## 📚 Documentation Map

| Need | Look Here | File |
|------|-----------|------|
| Project overview | Root | README.md |
| How to contribute | Root | CONTRIBUTING.md |
| Developer 101 | Root | DEVELOPER_QUICKSTART.md |
| Where is everything? | Root | FILE_ORGANIZATION_GUIDE.md |
| All documentation | docs/ | docs/INDEX.md |
| Architecture details | docs/guides/ | MODULARIZATION_COMPLETE.md |
| Design documents | docs/guides/ | Multiple guides |
| Test & analysis reports | docs/reports/ | Various JSON & text files |
| Historical context | docs/archives/ | Phase & sprint docs |

##

## 🔧 Core Application Files

Located in `core/` directory:

| File | Purpose |
|------|---------|
| main_v2.py | Streamlit web application (start here for UI) |
| start.py | Railway deployment entry point |
| main_response_engine.py | Core response pipeline |
| response_adapter.py | Emotional response translation |
| symbolic_tagger.py | Input parsing and analysis |
| tone_adapters.py | Tone adjustment system |
| enhanced_response_composer.py | Response composition |
| relational_memory.py | Memory system |
| And 3 more modules... | (See FILE_ORGANIZATION_GUIDE.md) |

##

## 📊 Data Organization

Located in `data/` directory:

| Subfolder | Contains | Count |
|-----------|----------|-------|
| glyphs/ | Glyph definitions and validation | 10 files |
| lexicons/ | NLP lexicon data | 4 files |
| analysis/ | Analysis output files | Expandable |
| exports/ | Export files | Expandable |

##

## ⚙️ Configuration & Deployment

| Location | Purpose | Count |
|----------|---------|-------|
| config/ | Python requirements, package.json, etc. | 7 files |
| scripts/ | Deployment and setup scripts | 2 files |
| logs/ | Application runtime logs | 5 files |

##

## 🎨 Features & Extensions

Located in `emotional_os/` directory:

9 modularized packages for features like:

- UI components (emotional_os/ui/)
- NLP parsing (emotional_os/parser/)
- Learning system (emotional_os/learning/)
- And more...

See `FILE_ORGANIZATION_GUIDE.md` for complete breakdown.

##

## 🧪 Testing & Tools

| Location | Purpose |
|----------|---------|
| tests/ | Test suites and integration tests |
| tools/analysis/ | Analysis utilities |
| tools/document_processing/ | Document handling tools |
| tools/glyph_testing/ | Glyph validation tools |

##

## 📖 Common Tasks

### I want to

**Start the application**

```bash

```text
```

**Find where a specific feature is**
→ Check `FILE_ORGANIZATION_GUIDE.md` or `DEVELOPER_QUICKSTART.md`

**Understand the architecture**
→ Read `docs/guides/MODULARIZATION_COMPLETE.md`

**Check test reports**
→ Look in `docs/reports/`

**Find old documentation**
→ Check `docs/archives/`

**Deploy to production**

```bash
```text
```text
```

**Set up locally**

```bash

```text
```

**Add a new feature**
→ See `DEVELOPER_QUICKSTART.md` New Developer Checklist

**Debug an issue**
→ Check `logs/` directory for application logs

##

## 🎯 Project Structure at a Glance

```
saoriverse-console/
├── README.md                 ← Project overview
├── CONTRIBUTING.md           ← Contribution guidelines
├── DEVELOPER_QUICKSTART.md   ← New developer guide ⭐
├── FILE_ORGANIZATION_GUIDE.md ← Complete file reference ⭐
├── DEPLOYMENT_READINESS_REPORT.md ← Deployment status ⭐
│
├── core/                     ← Essential application modules
├── docs/                     ← Documentation (guides, reports, archives)
├── data/                     ← Data files (glyphs, lexicons, etc.)
├── config/                   ← Configuration files
├── scripts/                  ← Deployment scripts
├── logs/                     ← Application logs
├── emotional_os/             ← Feature modules
├── tools/                    ← Analysis and testing tools
├── tests/                    ← Test suites
```text
```text
```

##

## ❓ Need Help?

1. **New to the project?** → `DEVELOPER_QUICKSTART.md`
2. **Need to find a file?** → `FILE_ORGANIZATION_GUIDE.md`
3. **Want architecture details?** → `docs/INDEX.md`
4. **Need to deploy?** → `DEPLOYMENT_READINESS_REPORT.md`
5. **Need documentation?** → `docs/INDEX.md` for complete navigation

##

## ✅ Quick Verification

Everything working? Run this:

```bash

python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from core.main_response_engine import translate_emotional_response
print('✅ All systems operational!')
"

```

##

**Last Updated**: December 3, 2025
**Status**: ✅ Deployment Ready
