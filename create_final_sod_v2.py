#!/usr/bin/env python3
"""
Create final SOD with aggressive line number removal
"""

from pathlib import Path
import re

pages_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages")
output_file = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_FINAL_CLEANED.txt")

ocr_fixes = {
    'Angel_es': 'Angeles',
    'withinterruptions': 'with interruptions',
    'INTROD UCTION': 'INTRODUCTION',
    'presiding ,': 'presiding,',
    'thereafter ,': 'thereafter,',
    'testimony ,': 'testimony,',
    'Greenfield .': 'Greenfield.',
    'Decision .': 'Decision.',
    '/Cross-comp lainants': '/Cross-complainants',
    'Defendants /Cross': 'Defendants/Cross',
    'cross-comp laint': 'cross-complaint',
    'defendant s': 'defendants',
    'plaintiff s': 'plaintiffs',
    'Conversion ;': 'Conversion;',
    'Advantage ;': 'Advantage;',
    'successfu l': 'successful',
    'comp laint': 'complaint',
}

all_pages = []
page_files = sorted(pages_dir.glob("Page_*.txt"))

for page_file in page_files:
    with open(page_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove ALL page markers and headers/footers
    content = re.sub(r'===== PAGE \d+ =====\n*', '', content)
    content = re.sub(r'\n*===== END PAGE \d+ =====', '', content)
    
    lines = content.split('\n')
    
    # Filter out lines that are ONLY numbers/whitespace
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        
        # Skip if it's empty
        if not stripped:
            filtered_lines.append('')
            continue
        
        # Skip if it's ONLY numbers or common line numbering patterns
        if re.match(r'^[\d\s]+$', stripped):
            continue
        
        # Skip lines that are common footer/header artifacts
        if re.match(r'^l+\s*l+$', stripped):  # l l (letter l's from page breaks)
            continue
        
        # Skip lines that look like page numbers at bottom
        if re.match(r'^\d+$', stripped) and len(stripped) <= 2:
            continue
        
        filtered_lines.append(line)
    
    page_text = '\n'.join(filtered_lines).strip()
    
    # Apply OCR fixes
    for old, new in ocr_fixes.items():
        page_text = page_text.replace(old, new)
    
    all_pages.append(page_text)

# Join pages and clean up excessive blank lines
final_text = '\n\n'.join(all_pages)

# Normalize multiple blank lines to just 2
final_text = re.sub(r'\n\n\n+', '\n\n', final_text)

# Write output
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(final_text)

print(f"✓ Final SOD created: {output_file}")
print(f"  Characters: {len(final_text):,}")
print(f"  Pages: {len(all_pages)}")

# Show first 50 lines
lines = final_text.split('\n')
print(f"\nFirst 20 lines:")
print('-' * 60)
for i, line in enumerate(lines[:20], 1):
    print(f"{i}: {line}")
