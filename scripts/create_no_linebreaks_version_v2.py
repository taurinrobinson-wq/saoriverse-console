#!/usr/bin/env python3
"""
Create clean version with lines joined within paragraphs and remaining artifacts removed
"""

from pathlib import Path
import re

sod_file = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_FINAL_CLEANED.txt")
output_file = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_FINAL_NO_LINEBREAKS.txt")

with open(sod_file, 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')

# Process lines to join them within paragraphs
processed_lines = []
current_paragraph = []

for line in lines:
    stripped = line.strip()
    
    # Empty line = paragraph break
    if not stripped:
        if current_paragraph:
            # Join the paragraph lines with spaces
            paragraph_text = ' '.join(current_paragraph)
            processed_lines.append(paragraph_text)
            current_paragraph = []
        processed_lines.append('')  # Preserve the blank line
    else:
        # Add to current paragraph
        current_paragraph.append(stripped)

# Don't forget last paragraph if file doesn't end with blank line
if current_paragraph:
    paragraph_text = ' '.join(current_paragraph)
    processed_lines.append(paragraph_text)

# Join all lines back together
result = '\n'.join(processed_lines)

# Remove remaining line number artifacts (28 at start of paragraphs)
result = re.sub(r'^28 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^27 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^26 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^25 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^24 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^23 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^22 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^21 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^20 ', '', result, flags=re.MULTILINE)
result = re.sub(r'^1[0-9] ', '', result, flags=re.MULTILINE)

# Fix some remaining artifacts
result = result.replace('treatment s ', 'treatments ')
result = result.replace('occasiona lly', 'occasionally')
result = result.replace('Norris(Id.)', 'Norris (Id.)')
result = result.replace('plajntiff s', 'plaintiffs')
result = result.replace('masstort', 'mass tort')
result = result.replace('compens ation', 'compensation')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"✓ Created: SOD_FINAL_NO_LINEBREAKS.txt")
print(f"  Size: {len(result):,} characters")
print(f"\nFirst 30 lines:")
print('=' * 80)
result_lines = result.split('\n')
for i, line in enumerate(result_lines[:30], 1):
    if line:
        display = line if len(line) <= 75 else line[:75] + "..."
        print(f"{i:2d}: {display}")
    else:
        print(f"{i:2d}: [PARAGRAPH BREAK]")
