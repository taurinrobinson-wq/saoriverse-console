# Project Structure & File Organization Guide

**Version**: Phase 10 Documentation Update
**Date**: December 3, 2025

---

## 📊 Complete Project File Map

### Root Level (2 Files - Clean!)

```
README.md                      Project overview & getting started
CONTRIBUTING.md                Contribution guidelines
```

**Note**: These are the only files that should be in root. Everything else is organized!

---

## 🔧 Core Application (core/)

**Purpose**: All essential Python files that power the application

```
core/
├── start.py                   Railway deployment entry point
├── main_v2.py                 Streamlit web application
├── main_response_engine.py    Core response pipeline (688 lines)
├── response_adapter.py        Emotional response translation
├── response_selector.py       Response selection logic
├── symbolic_tagger.py         Input parsing & tagging
├── tone_adapters.py          Tone adaptation system
├── enhanced_response_composer.py  Response composition
├── relational_memory.py       Relational memory system
├── glyph_generator.py        Compatibility shim
└── phase_modulator.py        Compatibility shim
```

**Total**: 11 core Python files
**Status**: ✅ All imports verified and working

---

## 📚 Documentation (docs/)

### guides/ - Design & Reference Documents

```
docs/guides/
├── MODULARIZATION_COMPLETE.md      ⭐ PRIMARY - Complete architecture guide (13 KB)
├── DELIVERABLES.md                 Project completion summary (9.1 KB)
├── PROJECT_INDEX.md                Project overview & file mapping (9.5 KB)
├── WINTER_CLEANING_PLAN.md        Original reorganization plan (5.9 KB)
├── WINTER_CLEANING_COMPLETION.md  Root cleanup execution report (7 KB)
├── GLYPH_SYSTEM_AUDIT.md          Glyph system detailed audit
├── MULTIMODAL_INTEGRATION_PLAN.md  Multi-modal integration design
├── UI_MODULARIZATION_ANALYSIS.md  UI component organization analysis
├── VOICE_INTERFACE_IMPLEMENTATION.md  Voice interface implementation
└── phase_modulator.md             Phase detection specs
```

**Total**: 10 comprehensive guides
**Purpose**: Architecture, design, and project references

### reports/ - Analysis & Reports

```
docs/reports/
├── FACTORIAL_EXPANSION_REPORT.json
├── GATE_DISTRIBUTION_ANALYSIS.json
├── GLYPH_TEST_REPORT.json
├── GLYPH_VALIDATION_REPORT.json
├── activation_signals_analysis.json
├── semantic_themes_analysis.json
├── review_manifest.json
├── commit_summary.txt
├── commit_summary_final.txt
├── legacy_references.txt
├── legacy_update_summary.txt
├── review_summary.txt
└── GATE_IMBALANCE_VISUAL.txt
```

**Total**: 13 analysis and test reports
**Purpose**: Test results, analysis outputs, audit trails

### archives/ - Phase & Sprint History

```
docs/archives/
├── FIRSTPERSON_PHASE_1_6_INTEGRATION.md
├── FIRSTPERSON_PHASE_1_COMPLETE.md
├── FIRSTPERSON_PHASE_1_SUMMARY.md
├── FIRSTPERSON_PHASE_2_1_COMPLETE.md
├── PHASE_2_2_2_ARCHITECTURE.md
├── PHASE_2_2_2_COMPLETION_REPORT.md
├── PHASE_2_2_2_DOCUMENTATION_INDEX.md
├── PHASE_2_2_2_QUICK_REFERENCE.md
├── PHASE_2_2_2_SESSION_SUMMARY.md
├── PHASE_2_3_INTEGRATION_COMPLETE.md
├── PHASE_2_3_SUMMARY.md
├── PHASE_3_1_SESSION_SUMMARY.md
├── PHASE_3_5_COMPLETION_SUMMARY.md
├── PHASES_2_3_2_4_2_5_INTEGRATION_COMPLETE.md
├── SESSIONEND_SUMMARY.md
├── SPRINT5_ENHANCEMENTS_SUMMARY.md
├── SPRINT5_IMPLEMENTATION_GUIDE.md
├── SPRINT5_INTEGRATION_GUIDE.md
└── SPRINT5_QUICK_REFERENCE.md
```

**Total**: 19 historical phase/sprint documents
**Purpose**: Development history and context

### INDEX.md - Navigation Guide

```
docs/INDEX.md                 ⭐ START HERE - Complete documentation index & navigation
```

**Total**: 1 navigation document
**Purpose**: Help users find what they need

---

## 📊 Data (data/)

### glyphs/ - Glyph Generation & Validation

```
data/glyphs/
├── phase_1_complete_glyphs.json
├── phase_1_new_glyphs.json
├── phase_1_validated_glyphs.json
├── phase_3_generated_glyphs.json
├── phase_4_test_results.json
├── glyph_lexicon_rows_before_dedup.json
├── glyph_lexicon_rows_before_phase2.json
├── glyph_lexicon_rows_before_phase3.json
├── temp_phase_1_validate.json
└── glyphs_rows.sql
```

**Total**: 10 glyph data files + 1 SQL file
**Purpose**: Glyph generation, validation, and database

### lexicons/ - NLP Lexicon Data

```
data/lexicons/
├── lexicon_enhanced.json
├── nrc_lexicon_cleaned.json
├── antonym_glyphs.txt
└── antonym_glyphs_indexed.json
```

**Total**: 4 lexicon files
**Purpose**: NLP processing and antonym mapping

### analysis/ - Analysis Outputs

```
data/analysis/
└── [Analysis output files go here]
```

**Purpose**: Expansion directory for analysis results

### exports/ - Export Files

```
data/exports/
└── [Export files go here]
```

**Purpose**: Expansion directory for exported data

---

## ⚙️ Configuration (config/)

```
config/
├── package.json              Node.js dependencies
├── package-lock.json         Locked dependency versions
├── requirements.txt          Core Python dependencies
├── requirements-dev.txt      Development dependencies
├── requirements-nlp.txt      NLP-specific dependencies
├── requirements-voice.txt    Voice interface dependencies
└── runtime.txt               Python runtime specification
```

**Total**: 7 configuration files
**Purpose**: Dependency management and environment setup

---

## 📜 Scripts (scripts/)

```
scripts/
├── deploy.sh                 Production deployment script
└── run_local.sh             Local development script
```

**Total**: 2 shell scripts
**Purpose**: Automation for deployment and local setup

---

## 🔍 Logs (logs/)

```
logs/
├── debug_chat.log
├── fastapi.log
├── glyph_generation.log
├── streamlit.log
└── streamlit_tonecore.log
```

**Total**: 5 log files
**Purpose**: Application debugging and monitoring

---

## 🎨 Frontend (frontend/)

```
frontend/
└── test.js                   Frontend test file
```

**Total**: 1 JavaScript file
**Purpose**: Frontend asset organization

---

## 🏛️ Modularized Application (emotional_os/)

### emotional_os/utils/

```
emotional_os/utils/
├── svg_loader.py
├── css_injector.py
└── styling_utils.py
```

**Purpose**: Shared utility functions

### emotional_os/session/

```
emotional_os/session/
└── session_manager.py        Session state management
```

**Purpose**: User session handling

### emotional_os/ui/

```
emotional_os/ui/
├── ui_refactored.py          Consolidated UI module (~200 lines)
├── header_ui.py              Header rendering
├── sidebar_ui.py             Sidebar navigation
└── chat_display.py           Chat message display
```

**Purpose**: UI component organization

### emotional_os/response/

```
emotional_os/response/
├── response_handler.py
└── glyph_handler.py
```

**Purpose**: Response processing logic

### emotional_os/features/

```
emotional_os/features/
├── document_processor.py
├── learning_tracker.py
├── journal_center.py
└── theme_manager.py
```

**Purpose**: Optional feature modules

### emotional_os/glyphs/

```
emotional_os/glyphs/
├── glyph_generator.py
├── glyph_lexicon_rows.sql
├── glyph_lexicon_rows.json
└── glyph_lexicon_rows_validated.json
```

**Purpose**: Glyph system implementation

### emotional_os/parser/

```
emotional_os/parser/
└── [NLP parsing modules]
```

**Purpose**: Input parsing and NLP

### emotional_os/learning/

```
emotional_os/learning/
└── [Learning system modules]
```

**Purpose**: Learning and memory management

### emotional_os/core/

```
emotional_os/core/
└── [Core system modules]
```

**Purpose**: Core application logic

---

## 🗜️ Organized Tools (tools/)

### tools/analysis/

```
tools/analysis/
├── gate_distribution_analyzer.py
├── generate_scenario_report.py
├── evolving_glyph_integrator.py
└── __init__.py
```

**Purpose**: Analysis and reporting utilities

### tools/document_processing/

```
tools/document_processing/
├── docx_reader.py
├── docx_viewer.py
├── docx_web_viewer.py
└── __init__.py
```

**Purpose**: Document handling utilities

### tools/glyph_testing/

```
tools/glyph_testing/
├── glyph_conversation_test_harness.py
├── glyph_effectiveness_validator.py
└── __init__.py
```

**Purpose**: Glyph testing and validation

---

## 📦 Organized Archives (archive/)

### archive/phase_infrastructure/

```
archive/phase_infrastructure/
├── phase_1_generator.py
├── phase_2_pruner.py
├── phase_3_generator.py
├── phase_3_integrator.py
├── phase_4_id_deduplicator.py
├── phase_4_ritual_tester.py
├── phase_modulator.py
└── __init__.py
```

**Purpose**: Historical phase infrastructure (preserved for reference)

---

## 🧪 Tests (tests/)

```
tests/
├── test_*.py                 Comprehensive test files
├── integration/
│   ├── test_scenarios.py
│   ├── tmp_run_mre.py
│   └── sprint5_integration.py
└── [Other test modules]
```

**Purpose**: Test suites and integration tests

---

## 📈 Organization Statistics

| Category | Count | Location |
|----------|-------|----------|
| Root files | 2 | root/ |
| Core Python files | 11 | core/ |
| Documentation guides | 10 | docs/guides/ |
| Analysis reports | 13 | docs/reports/ |
| Historical docs | 19 | docs/archives/ |
| Glyph data files | 10 | data/glyphs/ |
| Lexicon files | 4 | data/lexicons/ |
| Configuration files | 7 | config/ |
| Scripts | 2 | scripts/ |
| Log files | 5 | logs/ |
| Frontend files | 1 | frontend/ |
| **TOTAL** | **~84** | **Organized** |

---

## 🎯 Quick Reference: Where to Find Things

| Looking for... | Location | File |
|---|---|---|
| Project overview | root/ | README.md |
| Getting started | root/ | DEVELOPER_QUICKSTART.md |
| Architecture guide | docs/guides/ | MODULARIZATION_COMPLETE.md |
| Navigation help | docs/ | INDEX.md |
| Phase history | docs/archives/ | Various phase docs |
| Application code | core/ | main_v2.py or start.py |
| Response system | core/ | main_response_engine.py |
| Glyph data | data/glyphs/ | *.json files |
| Lexicon data | data/lexicons/ | *.json files |
| Deployment config | config/ | *.txt files |
| Deployment scripts | scripts/ | deploy.sh |
| Application logs | logs/ | *.log files |
| Analysis tools | tools/analysis/ | analyzer.py files |
| Tests | tests/ | test_*.py files |

---

## ✅ Verification Checklist

- [x] Root directory cleaned (-95% files)
- [x] Core Python files organized (core/)
- [x] Documentation organized (docs/ with guides/reports/archives)
- [x] Data organized (data/glyphs, data/lexicons)
- [x] Configuration grouped (config/)
- [x] Scripts centralized (scripts/)
- [x] Logs organized (logs/)
- [x] All imports verified and working
- [x] Directory structure complete
- [x] Navigation guides created

---

## 🚀 Next Steps

1. **Phase 11**: Deployment Testing
   - Test with new file structure
   - Verify deployment scripts work
   - Test in production-like environment

2. **Ongoing**: Maintain organization
   - Keep new files in appropriate directories
   - Reference this guide when adding new functionality

---

**For detailed information about any section, see**: `docs/INDEX.md` ⭐
