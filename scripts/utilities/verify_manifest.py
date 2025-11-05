#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_manifest.py

Check that all Phase 2 deliverable files are present in the repository.
Prints a concise present/missing report and exits with code 0 on success,
or 2 when files are missing.
"""
import os
import sys

FILES = {
	'Code': [
		'emotional_os/glyphs/glyph_learner.py',
		'emotional_os/glyphs/learning_response_generator.py',
		'emotional_os/glyphs/shared_glyph_manager.py',
		'test_glyph_learning_pipeline.py',
	],
	'Docs': [
		'emotional_os/PHASE_2_README.md',
		'emotional_os/PHASE_2_QUICK_REFERENCE.md',
		'emotional_os/PHASE_2_LEARNING_SYSTEM_ARCHITECTURE.md',
		'emotional_os/INTEGRATION_GUIDE_PHASE_2.md',
		'emotional_os/PHASE_2_VISUAL_DIAGRAMS.md',
		'emotional_os/PHASE_2_IMPLEMENTATION_CHECKLIST.md',
		'emotional_os/PHASE_2_DELIVERY_SUMMARY.md',
		'emotional_os/PHASE_2_DELIVERABLES_MANIFEST.md',
	],
}


def verify():
	missing = []
	print('\nPhase 2 verification report')
	print('=' * 40)
	for category, paths in FILES.items():
		print("\n{}:".format(category))
		for p in paths:
			ok = os.path.exists(p)
			mark = '✓' if ok else '✗'
			print("  {} {}".format(mark, p))
			if not ok:
				missing.append(p)

	print('\n' + '=' * 40)
	if not missing:
		print('✅ All manifest files present.')
		return 0
	else:
		print('❌ Missing files:')
		for m in missing:
			print('  -', m)
		return 2


if __name__ == '__main__':
	rc = verify()
	sys.exit(rc)
