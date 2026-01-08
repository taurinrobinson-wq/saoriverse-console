# SPINE v2 - Consolidated Application Structure

## Overview

SPINE v2 is now organized as a complete, self-contained application with NO duplicate code or orphaned scripts in the tools folder.

## Directory Structure

```
tools/
└── SPINE/                              # Main application (self-contained)
    ├── Core Modules
    │   ├── spine_parser.py             # Main extraction engine (472 lines)
    │   ├── multi_file_parser.py        # Multi-document processor (103 lines)
    │   ├── goodwin_phase2_processor.py # Phase 2 framework (255 lines)
    │   └── __init__.py                 # Package exports & version
    │
    ├── rebuild/                        # Text reconstruction submodule
    │   ├── __init__.py                 # Module exports
    │   ├── caption.py                  # Multi-line name reconstruction
    │   ├── case_number.py              # Case number reassembly
    │   ├── addresses.py                # Address line merging
    │   └── medical_history.py          # Medical narrative reconstruction
    │
    ├── debug/                          # Debug utilities submodule
    │   ├── __init__.py                 # Module exports
    │   └── inspect.py                  # Unified inspection utilities
    │       - inspect_case_section()    # Extract specific case
    │       - find_pattern_occurrences() # Find pattern matches
    │       - inspect_damages_section() # Show damages section
    │       - test_plaintiff_patterns()  # Test all patterns for plaintiff
    │       - compare_plaintiffs()       # Side-by-side comparison
    │       - validate_extraction_accuracy() # Validation against expected results
    │
    ├── tests/                          # Test suite submodule
    │   ├── __init__.py                 # Module exports
    │   └── test_extraction.py           # Comprehensive test suite
    │       - test_rebuild_caption()     # Rebuild functionality
    │       - test_pattern_matching()    # Pattern regex accuracy
    │       - test_extract_*()           # Field extraction tests
    │       - test_injury_extraction()   # Pattern matching tests
    │       - test_spatial_scoping()     # Critical fix verification
    │       - run_all_tests()            # Test runner
    │
    ├── Data Directories
    │   ├── Raw_Data_Docs/              # Input PDFs
    │   │   ├── JustSettlementStatements.pdf (37 plaintiffs)
    │   │   └── 17-cv-02775 - GoodwinConfSettlementStmt.pdf
    │   │
    │   └── Output/                     # Generated CSV files
    │       └── JustSettlementStatements_Complete.csv (38 rows)
    │
    └── Documentation
        ├── README_SPINE_v2.md                        # User guide
        ├── QUICK_REFERENCE.md                        # Command reference
        ├── SPINE_v2_PHASE1_COMPLETE.md              # Phase 1 report
        ├── SPINE_v2_IMPLEMENTATION.md               # Technical details
        ├── SPINE_v2_INTEGRATION_VERIFICATION.md     # Integration guide
        └── SPINE_v2_COMPLETE_PROJECT_INDEX.md       # Comprehensive index
```

## Module Organization

### 1. Core Modules (Execution)
**Location**: `tools/SPINE/`

| File | Lines | Purpose |
|------|-------|---------|
| spine_parser.py | 472 | Main extraction engine with 40+ injury patterns |
| multi_file_parser.py | 103 | Multi-document processor with boundary detection |
| goodwin_phase2_processor.py | 255 | Phase 2 medical records framework |
| __init__.py | 40 | Package initialization & exports |

**No dependencies between core files** - each can run independently

### 2. Rebuild Submodule (Text Preprocessing)
**Location**: `tools/SPINE/rebuild/`

Handles multi-line text fragments from PDF extraction:

| File | Purpose |
|------|---------|
| __init__.py | Module exports (clean imports) |
| caption.py | Plaintiff name reconstruction (o/b/o, deceased, etc.) |
| case_number.py | Case number reassembly |
| addresses.py | Address line merging |
| medical_history.py | Medical narrative reconstruction |

**Usage**: 
```python
from tools.SPINE.rebuild import rebuild_caption_lines, rebuild_addresses
# Or
from tools.SPINE import rebuild
text = rebuild.rebuild_caption_lines(raw_text)
```

### 3. Debug Submodule (Inspection & Validation)
**Location**: `tools/SPINE/debug/`

Consolidated utility functions for inspecting extraction results:

**File**: `inspect.py` (consolidated from 6 previous debug scripts)

**Functions**:
- `inspect_case_section(pdf_path, plaintiff_name)` - Extract case text
- `find_pattern_occurrences(pdf_path, plaintiff_name, pattern_key)` - Find pattern matches
- `inspect_damages_section(pdf_path, plaintiff_name)` - Show damages section
- `test_plaintiff_patterns(pdf_path, plaintiff_name)` - Test all patterns
- `compare_plaintiffs(pdf_path, plaintiff_names)` - Compare multiple cases
- `validate_extraction_accuracy(pdf_path, test_cases)` - Validate against expected

**Usage**:
```python
from tools.SPINE.debug import compare_plaintiffs, validate_extraction_accuracy
from pathlib import Path

pdf = Path("Raw_Data_Docs/JustSettlementStatements.pdf")

# Compare specific plaintiffs
compare_plaintiffs(pdf, ["Teresa Whetstone", "Robert Tavares", "Vonda Webb"])

# Validate extraction
test_cases = {
    "Teresa Whetstone": {"retrieval_open": True, "death": False},
    "Robert Tavares": {"retrieval_open": False, "death": False},
}
validate_extraction_accuracy(pdf, test_cases)
```

**Or directly**:
```bash
cd tools/SPINE
python -m debug.inspect
```

### 4. Tests Submodule (Test Suite)
**Location**: `tools/SPINE/tests/`

Consolidated test suite with comprehensive coverage:

**File**: `test_extraction.py` (unified from 4 previous test scripts)

**Test Functions**:
- `test_rebuild_caption()` - Caption reconstruction
- `test_pattern_matching()` - Regex accuracy
- `test_extract_*()` - Field extraction (5 tests)
- `test_injury_extraction()` - Pattern matching
- `test_summary_building()` - Summary generation
- `test_spatial_scoping()` - Critical fix verification
- `run_all_tests()` - Test runner

**Usage**:
```bash
cd tools/SPINE
python -m tests.test_extraction
```

**Or in code**:
```python
from tools.SPINE.tests import run_all_tests
success = run_all_tests()
```

## Consolidated vs. Previous Structure

### Files Removed from tools/ (Cleaned Up)
The following were consolidated and are **NO LONGER** in tools/ root:

- ❌ `advanced_parse_pdf.py` (old parser version)
- ❌ `parse_pdf_to_csv.py` (old parser version)
- ❌ `debug_extract.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `debug_rebuild.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `debug_whetstone.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `debug_goodwin_cases.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `debug_open_matches.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `check_all_open_surgery.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `check_whetstone_raw.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `test_extract.py` → ✅ `SPINE/tests/test_extraction.py`
- ❌ `test_rebuild.py` → ✅ `SPINE/tests/test_extraction.py`
- ❌ `test_pattern.py` → ✅ `SPINE/tests/test_extraction.py`
- ❌ `test_goodwin_extraction.py` → ✅ `SPINE/tests/test_extraction.py`
- ❌ `inspect_justsettlement.py` → ✅ `SPINE/debug/inspect.py`
- ❌ `rebuild_caption.py` → ✅ `SPINE/rebuild/caption.py`
- ❌ `rebuild_case_number.py` → ✅ `SPINE/rebuild/case_number.py`
- ❌ `rebuild_addresses.py` → ✅ `SPINE/rebuild/addresses.py`
- ❌ `rebuild_medical_history.py` → ✅ `SPINE/rebuild/medical_history.py`

### Files Remaining in tools/
Only SPINE folder:
- ✅ `tools/SPINE/` - Complete self-contained application

**tools/ root is now CLEAN** - no orphaned or duplicate scripts

## Usage Examples

### Standard Production Use
```bash
cd tools/SPINE
python multi_file_parser.py
# Output: Output/JustSettlementStatements_Complete.csv (38 rows)
```

### Debug Inspection (Compare Cases)
```python
from pathlib import Path
from tools.SPINE.debug import compare_plaintiffs

pdf = Path("tools/SPINE/Raw_Data_Docs/JustSettlementStatements.pdf")
compare_plaintiffs(pdf, [
    "Teresa Whetstone",   # Should have open surgery
    "Robert Tavares",     # Should NOT have open surgery
    "Vonda Webb",         # Should NOT have open surgery
])
```

### Run Test Suite
```bash
cd tools/SPINE
python -m tests.test_extraction
```

### Validate Extraction Accuracy
```python
from pathlib import Path
from tools.SPINE.debug import validate_extraction_accuracy

pdf = Path("tools/SPINE/Raw_Data_Docs/JustSettlementStatements.pdf")

test_cases = {
    "Teresa Whetstone": {"retrieval_open": True},
    "Robert Tavares": {"retrieval_open": False},
    "Penney Goodwin": {"death": False},
}

validate_extraction_accuracy(pdf, test_cases)
```

### Use as Library
```python
from tools.SPINE import (
    extract_text, split_cases, extract_plaintiff,
    extract_all_injuries, build_summary
)

# Extract and analyze single PDF
from pathlib import Path
pdf_path = Path("tools/SPINE/Raw_Data_Docs/JustSettlementStatements.pdf")
text = extract_text(pdf_path)
cases = split_cases(text)

for case_text in cases:
    plaintiff = extract_plaintiff(case_text)
    injuries = extract_all_injuries(case_text)
    summary = build_summary(injuries)
    print(f"{plaintiff}: {summary}")
```

## Key Improvements

### 1. NO Code Duplication
- **Before**: 6 debug scripts with overlapping functionality
- **After**: 1 unified `debug/inspect.py` with 6 focused functions

- **Before**: 4 test scripts with redundant test cases
- **After**: 1 unified `tests/test_extraction.py` with 9 comprehensive tests

### 2. Clean Module Structure
- **Before**: Rebuild functions scattered in tools/ root
- **After**: Organized in `rebuild/` submodule with clean imports

- **Before**: Core modules imported rebuild functions from parent directory
- **After**: Clean relative imports from submodule

### 3. Self-Contained Application
- **Before**: SPINE folder + loose scripts in tools/
- **After**: Everything in SPINE/ - one folder to deploy/backup

### 4. Proper Submodule Organization
All submodules have:
- ✅ `__init__.py` with clean exports
- ✅ Focused single-purpose modules
- ✅ Documentation in docstrings
- ✅ Example usage in module

## Maintainability

### Adding New Functionality
1. **New extraction pattern**: Add to `PATTERNS` dict in `spine_parser.py`
2. **New debug utility**: Add to `debug/inspect.py`
3. **New test**: Add to `tests/test_extraction.py`
4. **New rebuilder**: Create in `rebuild/`, add to `__init__.py`

### Code Navigation
- **Extraction**: `spine_parser.py` (single entry point)
- **Debugging**: `debug/inspect.py` (all utilities)
- **Testing**: `tests/test_extraction.py` (all tests)
- **Preprocessing**: `rebuild/` (modular, each has single purpose)

## Version & Status

- **Version**: 2.0.0
- **Status**: ✅ Phase 1 Complete | 🚀 Phase 2 Ready
- **Quality**: Zero duplication | Clean structure | Production-ready
- **Deployment**: Single SPINE folder with all dependencies self-contained

---

**Last Updated**: January 7, 2026  
**Structure Completed**: ✅ Consolidation complete, no orphaned scripts
