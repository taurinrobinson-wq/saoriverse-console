"""Top-level `emotional_os` package loader.

This file delegates the package to the canonical implementation under
`src/emotional_os`. It ensures the `src/` layout is authoritative and
prevents the project-root copy of `emotional_os` from shadowing the
source package during imports.

This is a reversible, minimal change intended to make the repository
behave as a proper `src`-layout package during test collection and
local development. Remove this wrapper if you reorganize the repo.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_INIT = ROOT / "src" / "emotional_os" / "__init__.py"

if SRC_INIT.exists():
	# Ensure src/ is first on sys.path for any imports performed by the
	# loaded package implementation.
	src_dir = str(ROOT / "src")
	if src_dir not in sys.path:
		sys.path.insert(0, src_dir)

	spec = importlib.util.spec_from_file_location("emotional_os._src", str(SRC_INIT))
	_module = importlib.util.module_from_spec(spec)
	loader = spec.loader
	assert loader is not None
	loader.exec_module(_module)

	# Re-export public attributes from the loaded src package module.
	for _name in dir(_module):
		if not _name.startswith("_"):
			globals()[_name] = getattr(_module, _name)

	# Ensure sys.modules maps the canonical package name to the loaded
	# module so subsequent imports use the src implementation.
	sys.modules["emotional_os"] = _module
else:
	# Fallback: keep package minimal to avoid breaking imports.
	__all__ = []

