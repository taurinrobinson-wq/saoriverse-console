#!/usr/bin/env python3
"""Comprehensive TONE/REMNANTS system alignment across all Ink files and docs"""

import os

# Mapping dictionary
replacements = {
    'adjust_tone("skepticism"': 'adjust_tone("observation"',
    'adjust_tone("integration"': 'adjust_tone("narrative_presence"',
    'adjust_tone("awareness"': 'adjust_tone("observation"',
    'tone_skepticism': 'tone_observation',
    'tone_integration': 'tone_narrative_presence',
    'tone_awareness': 'tone_trust',
    '~ return "skepticism"': '~ return "observation"',
    '~ return "integration"': '~ return "narrative_presence"',
    '~ return "awareness"': '~ return "trust"',
}

files = [
    'velinor-story/npc_profiles.ink',
    'velinor-story/main.ink',
    'velinor-story/marketplace.ink',
    'velinor-story/glyph_reveals.ink',
    'velinor-story/gates.ink',
    'INK_EVALUATION_AND_MIGRATION.md',
    'VELINOR_COMPREHENSIVE_DOCUMENTATION.md',
]

for fpath in files:
    if not os.path.exists(fpath):
        print(f'✗ {fpath}')
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = original
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ {fpath}')
    else:
        print(f'- {fpath} (no changes)')

print('\n✅ All files aligned')
