#!/usr/bin/env python3
"""
Comprehensive TONE/REMNANTS system alignment
Maps old stat names to correct ones across all files

Old system (WRONG):
  - tone_empathy, tone_skepticism, tone_integration, tone_awareness
  
New system (CORRECT):
  - tone_trust, tone_observation, tone_empathy, tone_narrative_presence
  
Variable mapping:
  - tone_empathy (old) → tone_empathy (new)
  - tone_skepticism (old) → tone_observation (new)
  - tone_integration (old) → tone_narrative_presence (new)
  - tone_awareness (old) → tone_trust (new)

Function call mapping:
  - adjust_tone("empathy") → stays as adjust_tone("empathy")
  - adjust_tone("skepticism") → becomes adjust_tone("observation")
  - adjust_tone("integration") → becomes adjust_tone("empathy") [*requires care*]
  - adjust_tone("awareness") → becomes adjust_tone("observation")
"""

import os
import re

# Define all replacements
replacements = {
    # Variable references
    'tone_skepticism': 'tone_observation',
    'tone_integration': 'tone_narrative_presence',
    'tone_awareness': 'tone_trust',
    
    # Function call mappings - need to be careful with these
    'adjust_tone("skepticism"': 'adjust_tone("observation"',
    'adjust_tone("awareness"': 'adjust_tone("observation"',
    'adjust_tone("integration"': 'adjust_tone("narrative_presence"',
    
    # Return values from dominance checks
    '~ return "skepticism"': '~ return "observation"',
    '~ return "awareness"': '~ return "observation"',
    '~ return "integration"': '~ return "narrative_presence"',
    
    # Text descriptions
    'Skepticism:': 'Observation:',
    'Integration:': 'Narrative Presence:',
    'Awareness:': 'Trust:',
}

# Files to update
files_to_update = [
    'velinor-story/utilities.ink',
    'velinor-story/main.ink',
    'velinor-story/marketplace.ink',
    'velinor-story/gates.ink',
    'velinor-story/glyph_reveals.ink',
    'velinor-story/npc_profiles.ink',
    'INK_EVALUATION_AND_MIGRATION.md',
    'VELINOR_COMPREHENSIVE_DOCUMENTATION.md',
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        print(f'✗ Not found: {filepath}')
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ Updated: {filepath}')
    else:
        print(f'- No changes: {filepath}')

print('\n✅ System-wide alignment complete')
