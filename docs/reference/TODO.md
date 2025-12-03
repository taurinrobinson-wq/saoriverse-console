Repository TODO
==============

This file is an auto-saved, persistent todo list for the ongoing "move root scripts into tools/" refactor and test stabilization work. It's committed to the repo so you can pick up from any machine.

Status (last updated 2025-10-31):

- [x] Run test suite, ran earlier to verify changes
- [x] Add CI self-diagnostic workflow, added
- [x] Move next batch of root scripts to `tools/`, moved safe batch and created compatibility shims
- [x] Commit & push changes, latest changes pushed (includes restore of ritual processor)
- [x] Run pytest to verify, ran (partial/full) after fixes
- [ ] Plan next batch, not started
- [x] Run full pytest suite, ran; summary below

Latest test run summary:

- 20 passed, 1 failed, 8 warnings
- Failing test: `test_ritual_processor.py::test_glyph_creation`, AttributeError: `GlyphObject` object has no `to_dict`

Next recommended actions when you resume:

1. Fix `GlyphObject.to_dict` availability or ensure tests import the right class.
   - File to inspect: `tools/ritual_capsule_processor.py` and `ritual_capsule_processor.py` (root shim)
2. Run the full test suite from repo root (Windows PowerShell):

```powershell
Set-Location -Path "C:\Users\Admin\OneDrive\Desktop\Deleted_Emotional_OS_Folder\Emotional OS"
& ".\.venv\Scripts\Activate.ps1"  # if needed
& ".\.venv\Scripts\python.exe" -m pytest -q
```

3. If tests fail, run the single failing test to iterate faster:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q test_ritual_processor.py::test_glyph_creation -k test_glyph_creation -q
```

4. When making small fixes, commit and push with a clear message and re-run pytest.

Helpful notes:

- The `tools/` package now exists (`tools/__init__.py`) so moved modules are importable as `tools.<module>`.
- Root shims (e.g., `ritual_capsule_processor.py`) re-export or call into `tools.*` for backwards compatibility.
- If you want me to continue: I can either fix the remaining failing test, address warnings, or move the next batch of files.

Where this file lives:

- `TODO.md` at repository root: `c:/Users/Admin/OneDrive/Desktop/Deleted_Emotional_OS_Folder/Emotional OS/TODO.md`

If you'd like a different format (JSON, YAML, taskboard), tell me and I will create it instead.
