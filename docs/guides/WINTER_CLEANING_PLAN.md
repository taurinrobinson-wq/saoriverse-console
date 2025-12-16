# Phase 7: Operation Winter Cleaning - Root Directory Reorganization

## Status: IN PROGRESS

This document outlines the comprehensive reorganization of root-level Python files into appropriate directories for better project maintainability.
##

## Analysis of Root Python Files (30 files)

### Category 1: MAIN APPLICATION ENTRY POINTS ✅ **KEEP IN ROOT**

- `start.py` - Railway deployment startup script
- `main_v2.py` - Primary Streamlit app entry point (~736 lines)

**Action**: Keep in root. These are the application entry points.
##

### Category 2: CORE GLYPH SYSTEM (moved to emotional_os/glyphs/) ✅ **SHIMS EXIST**

- `glyph_generator.py` - ✅ Shim file (compatibility layer pointing to emotional_os/glyphs/)
- `glyph_response_helpers.py` - Part of core glyph infrastructure
- `glyph_response_templates.py` - Glyph response templates
- `glyph_conversation_test_harness.py` - Testing glyph conversation flows
- `glyph_effectiveness_validator.py` - Testing glyph effectiveness

**Action**:

- `glyph_generator.py` - Already a shim, leave as-is ✅
- Move others to: `tools/glyph_testing/` or `emotional_os/glyphs/`
##

### Category 3: GLYPH GENERATION PHASES (Legacy phase infrastructure)

- `phase_1_generator.py`
- `phase_2_pruner.py`
- `phase_3_generator.py`
- `phase_3_integrator.py`
- `phase_4_id_deduplicator.py`
- `phase_4_ritual_tester.py`
- `phase_modulator.py`

**Action**: Move to `archive/phase_infrastructure/` (historical but referenced in code)
##

### Category 4: ANALYSIS & REPORTING TOOLS

- `gate_distribution_analyzer.py` - Analyzes gate distribution
- `generate_scenario_report.py` - Scenario reporting
- `symbolic_tagger.py` - Symbolic tagging analysis
- `evolving_glyph_integrator.py` - Glyph evolution analysis

**Action**: Move to `tools/analysis/`
##

### Category 5: DOCUMENT PROCESSING & VIEWERS

- `docx_reader.py` - DOCX file reading
- `docx_viewer.py` - DOCX file viewing
- `docx_web_viewer.py` - Web-based DOCX viewer

**Action**: Move to `tools/document_processing/` or keep in root if used frequently
##

### Category 6: RESPONSE SYSTEM (Likely refactored into modules/)

- `main_response_engine.py` - Response composition engine
- `response_adapter.py` - Response adaptation
- `response_selector.py` - Response selection logic
- `enhanced_response_composer.py` - Enhanced response composition
- `tone_adapters.py` - Tone adaptation

**Action**: These should be imported from `emotional_os/` modularization or moved to `src/response_system/`
##

### Category 7: RELATIONAL & MEMORY SYSTEMS

- `relational_memory.py` - Relational memory implementation

**Action**: Move to `src/memory_systems/` or integrate into main modules
##

### Category 8: TESTING & DEBUGGING

- `test_scenarios.py` - Test scenario definitions
- `tmp_run_mre.py` - Temporary MRE (Minimal Reproducible Example)
- `sprint5_integration.py` - Sprint integration testing

**Action**: Move to `tests/integration/`
##

## Reorganization Plan

### Step 1: Archive Historical Phase Infrastructure ✅
```text
```
archive/phase_infrastructure/
├── phase_1_generator.py
├── phase_2_pruner.py
├── phase_3_generator.py
├── phase_3_integrator.py
├── phase_4_id_deduplicator.py
├── phase_4_ritual_tester.py
└── phase_modulator.py
```



### Step 2: Consolidate Analysis Tools ✅
```text
```
tools/analysis/
├── gate_distribution_analyzer.py
├── generate_scenario_report.py
├── symbolic_tagger.py
└── evolving_glyph_integrator.py
```



### Step 3: Organize Document Processing ✅
```text
```
tools/document_processing/
├── docx_reader.py
├── docx_viewer.py
└── docx_web_viewer.py
```



### Step 4: Move Glyph Testing Tools ✅
```text
```
tools/glyph_testing/
├── glyph_response_helpers.py
├── glyph_response_templates.py
├── glyph_conversation_test_harness.py
├── glyph_effectiveness_validator.py
```



### Step 5: Verify and Update Imports

- Check which files import from root
- Update import paths in main_v2.py and other entry points
- Verify all module imports resolve correctly

### Step 6: Integration Testing

- Test main_v2.py startup
- Verify all features work after reorganization
- Check CI/CD pipeline

### Step 7: Clean Root Directory

After moving all files, root will contain only:

- `start.py` (Railway entry point)
- `main_v2.py` (Streamlit entry point)
- `glyph_generator.py` (compatibility shim)
- Core config/build files (Makefile, pyproject.toml, etc.)
- Markdown docs (README, CONTRIBUTING, etc.)
- Root .json and .txt files (data/config)
##

## Files to Keep in Root

✅ **Application Entry Points:**

- `start.py`
- `main_v2.py`
- `glyph_generator.py` (shim)

✅ **Configuration Files:**

- `pyproject.toml`
- `setup.cfg`
- `package.json`
- `requirements*.txt`
- `Makefile`
- `Dockerfile`

✅ **Documentation:**

- `README.md`
- `CONTRIBUTING.md`
- Various markdown files

✅ **Data/Output Files:**

- `*.json` files (data exports)
- `*.txt` files (reports)
- `*.sql` files

✅ **Deployment Config:**

- `Procfile`
- `runtime.txt`
- `railway.env.template`
##

## Migration Checklist

- [ ] Create `archive/phase_infrastructure/` directory
- [ ] Move phase_*.py files to archive
- [ ] Create `tools/analysis/` directory
- [ ] Move analysis tools
- [ ] Create `tools/document_processing/` directory
- [ ] Move document processing tools
- [ ] Create `tools/glyph_testing/` directory
- [ ] Move glyph testing tools
- [ ] Update imports in main_v2.py
- [ ] Test application startup
- [ ] Verify all imports resolve
- [ ] Commit changes with clear message
- [ ] Remove moved files from root
- [ ] Final verification
##

## Notes

- Some response system files might already be integrated into the `emotional_os/` modularization
- Check if relational_memory.py has been moved to modules/
- Verify that test scenario files are properly moved to tests/
- Ensure backward compatibility shims are in place where needed
##

**Last Updated**: During Phase 7 - Operation Winter Cleaning
