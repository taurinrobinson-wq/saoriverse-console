#!/usr/bin/env python3
"""
Final cleanup - remove remaining artifacts more intelligently
"""

from pathlib import Path
import re

sod_file = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_FINAL_CLEANED.txt")

with open(sod_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the problematic page break artifacts
# "1 l" or "1 I" (number + letter) followed by line number
text = re.sub(r'^\s*1\s*[lI]\s*$\n', '', text, flags=re.MULTILINE)
text = re.sub(r'^\s*1\s*[lI]\s*\n', '', text, flags=re.MULTILINE)

# Remove standalone line numbers at the start of a paragraph that are clearly artifacts
# Pattern: line starts with number 28 or 1 but next word shows it's mid-sentence
text = re.sub(r'^28\s+([a-z])', r'\1', text, flags=re.MULTILINE)  # "28 has been" -> "has been"
text = re.sub(r'^7\s*I\s*$\n', '', text, flags=re.MULTILINE)  # "7 I" artifact
text = re.sub(r'^9\s*I\s*$\n', '', text, flags=re.MULTILINE)  # "9 I" artifact
text = re.sub(r'^11\s*I\s*$\n', '', text, flags=re.MULTILINE)  # "11 I" artifact
text = re.sub(r'^4\s+Although', r'Although', text, flags=re.MULTILINE)  # "4 Although" -> "Although"
text = re.sub(r'^3\s+Although', r'Although', text, flags=re.MULTILINE)  # "3 Although" -> "Although"
text = re.sub(r'^2\s+Around', r'Around', text, flags=re.MULTILINE)  # "2 Around" -> "Around"

# Clean up other OCR artifacts
text = text.replace('de1:1entia', 'dementia')
text = text.replace('oneoftheir', 'one of their')
text = text.replace('3Mm_ilitary e_arbuds', '3M military earbuds')
text = text.replace('didacknowledge', 'did acknowledge')
text = text.replace('Ma ', 'May ')  # Fix "Ma" at end of line that should be "May"
text = text.replace('deni_ed', 'denied')
text = text.replace('Lombard believed if he had de1:1entia', 'Lombard believed if he had dementia')

# Remove any remaining lines that are JUST numbers 1-28
text = re.sub(r'^(?:1[0-9]|2[0-8]|\d)\s*$\n', '', text, flags=re.MULTILINE)

# Normalize line endings and excessive blank lines
text = re.sub(r'\n\n\n+', '\n\n', text)

# Strip leading/trailing whitespace
text = text.strip()

with open(sod_file, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"✓ Final cleanup complete")
print(f"  File size: {len(text):,} characters")

# Show first 30 lines
lines = text.split('\n')
print(f"\nFirst 30 lines:")
print('='*70)
for i, line in enumerate(lines[:30], 1):
    print(f"{i:2d}: {line}")
