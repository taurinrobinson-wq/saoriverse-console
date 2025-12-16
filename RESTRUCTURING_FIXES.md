# FirstPerson App Restructuring Fixes - Complete

## Problem
After the repository restructuring that moved files from root to `src/` directory and split modules into separate packages (e.g., `emotional_os_glyphs`, `emotional_os_lexicon`, etc.), the FirstPerson app was broken because:

1. `app.py` couldn't import `emotional_os.deploy.modules.ui_refactored`
2. The new package structure had text-based symlink stubs that didn't work
3. Import paths expected `emotional_os.glyphs`, `emotional_os.lexicon`, etc. but the actual packages were named `emotional_os_glyphs`, `emotional_os_lexicon`, etc.

## Solution Implemented

### 1. Fixed `app.py` Import Path (lines 7-11)
Added `src/` to `sys.path` so Python can find the modules:

```python
sys.path.insert(0, str(Path(__file__).parent / "src"))
```



This ensures that when `from emotional_os.deploy.modules.ui_refactored import main` is executed, Python looks in the correct location.

### 2. Updated Package Configuration

**pyproject.toml**: Changed from flat package layout to src-layout

```toml
[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
include = ["emotional_os*", "emotional_os_*"]
```



**setup.cfg**: Updated to point packages to src directory

```ini
[options]
package_dir = {= src}

[options.packages.find]
where = src
```



### 3. Converted Text-Based Symlinks to Directory Stubs

The following were converted from 22-byte text files to proper directories:
- `src/emotional_os/glyphs/`
- `src/emotional_os/lexicon/`
- `src/emotional_os/parser/`
- `src/emotional_os/safety/`
- `src/emotional_os/feedback/`
- `src/emotional_os/learning/`
- `src/emotional_os/privacy/`

### 4. Created Re-export __init__.py Files

Each directory now contains an `__init__.py` that:
1. Adds parent path to sys.path
2. Imports the corresponding `emotional_os_*` module
3. **Crucially**: Uses `sys.modules` manipulation to map all submodules to the expected namespace

Example for `src/emotional_os/glyphs/__init__.py`:

```python

# Register all submodules from the sibling in sys.modules
for key, module in list(sys.modules.items()):
    if key.startswith('emotional_os_glyphs'):
        # Map emotional_os_glyphs.X to emotional_os.glyphs.X
        new_key = key.replace('emotional_os_glyphs', 'emotional_os.glyphs')
        sys.modules[new_key] = module
```



This allows code like `from emotional_os.glyphs.learning_response_generator import X` to work even though the actual module is `emotional_os_glyphs.learning_response_generator`.

## Verification

All critical imports now work:
- ✓ `emotional_os`
- ✓ `emotional_os.core`
- ✓ `emotional_os.deploy.modules.ui_refactored`
- ✓ `emotional_os.glyphs` (and submodules like `.learning_response_generator`)
- ✓ `emotional_os.lexicon`
- ✓ `emotional_os.parser`
- ✓ `emotional_os.safety`
- ✓ `emotional_os.feedback`
- ✓ `emotional_os.learning`
- ✓ `emotional_os.privacy`

## How to Run

```bash
cd d:\saoriverse-console
streamlit run app.py
```



The app should now start without import errors.

## Files Modified

1. `app.py` - Updated import handling
2. `pyproject.toml` - Fixed package configuration
3. `setup.cfg` - Fixed package discovery
4. `src/emotional_os/glyphs/__init__.py` - Created re-export stub
5. `src/emotional_os/lexicon/__init__.py` - Created re-export stub
6. `src/emotional_os/parser/__init__.py` - Created re-export stub
7. `src/emotional_os/safety/__init__.py` - Created re-export stub
8. `src/emotional_os/feedback/__init__.py` - Created re-export stub
9. `src/emotional_os/learning/__init__.py` - Created re-export stub
10. `src/emotional_os/privacy/__init__.py` - Created re-export stub
