"""Dynamic bridge that redirects `emotional_os.glyphs.*` imports to
`emotional_os_glyphs.*` implementations when available.

This avoids duplicating the large `emotional_os_glyphs` codebase while
making `emotional_os.glyphs.<module>` imports resolve cleanly to the
source implementation. The bridge uses an import hook so submodules
are loaded lazily and mapped into `sys.modules` under the expected
`emotional_os.glyphs.*` names.
"""
from __future__ import annotations
import importlib
import importlib.abc
import importlib.util
import sys
from typing import Optional


class _RedirectLoader(importlib.abc.Loader):
	def __init__(self, fullname: str, target_name: str):
		self.fullname = fullname
		self.target_name = target_name

	def create_module(self, spec):
		return None

	def exec_module(self, module):
		# Import the target module and copy its attributes into the
		# module object that Python expects for the original name.
		target = importlib.import_module(self.target_name)
		module.__dict__.clear()
		module.__dict__.update({k: v for k, v in target.__dict__.items() if k != "__name__"})
		# Ensure sys.modules maps the requested name to the actual module
		sys.modules[self.fullname] = target


class _RedirectFinder(importlib.abc.MetaPathFinder):
	def find_spec(self, fullname: str, path, target=None) -> Optional[importlib.machinery.ModuleSpec]:
		prefix = "emotional_os.glyphs."
		if not fullname.startswith(prefix):
			return None
		tail = fullname[len(prefix):]
		target_name = f"emotional_os_glyphs.{tail}"
		spec = importlib.util.find_spec(target_name)
		if spec is None:
			return None
		loader = _RedirectLoader(fullname, target_name)
		return importlib.util.spec_from_loader(fullname, loader)


# Install the finder early so subsequent imports resolve through it.
if not any(isinstance(f, _RedirectFinder) for f in sys.meta_path):
	sys.meta_path.insert(0, _RedirectFinder())

__all__ = []

