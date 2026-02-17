#!/usr/bin/env python3
"""
Create version of SOD with lines joined - breaks only at paragraphs
"""

from pathlib import Path

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

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"✓ Created: SOD_FINAL_NO_LINEBREAKS.txt")
print(f"  Size: {len(result):,} characters")
print(f"\nFirst 50 lines:")
print('=' * 70)
for i, line in enumerate(result.split('\n')[:50], 1):
    if line:
        print(f"{i:3d}: {line[:70]}")
    else:
        print(f"{i:3d}: [PARAGRAPH BREAK]")
