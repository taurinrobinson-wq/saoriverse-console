#!/usr/bin/env python3
"""Fix npc_profiles.ink comprehensively"""

content = open('velinor-story/npc_profiles.ink', 'r').read()

# Replace all old stat references
replacements = {
    'adjust_tone("skepticism"': 'adjust_tone("observation"',
    'adjust_tone("integration"': 'adjust_tone("narrative_presence"',
    'adjust_tone("awareness"': 'adjust_tone("observation"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

open('velinor-story/npc_profiles.ink', 'w').write(content)
print('✓ Fixed npc_profiles.ink')
