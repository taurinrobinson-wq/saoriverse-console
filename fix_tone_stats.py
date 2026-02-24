#!/usr/bin/env python3
"""Fix TONE stat names in Ink files"""

import re

files_to_update = [
    'velinor-story/npc_profiles.ink',
    'velinor-story/gates.ink',
    'velinor-story/utilities.ink',
    'velinor-story/marketplace.ink',
    'velinor-story/main.ink'
]

replacements = {
    'adjust_tone("awareness"': 'adjust_tone("observation"',
    'adjust_tone("skepticism"': 'adjust_tone("observation"',
    'adjust_tone("integration"': 'adjust_tone("empathy"',
    'tone_awareness': 'tone_observation',
    'tone_skepticism': 'tone_observation',
    'tone_integration': 'tone_empathy',
}

for filepath in files_to_update:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f'✓ Updated {filepath}')
        else:
            print(f'- No changes needed in {filepath}')
    except FileNotFoundError:
        print(f'✗ File not found: {filepath}')
