#!/usr/bin/env python3
"""
Create final cleaned SOD - all 41 pages in clean format with OCR fixes
"""

from pathlib import Path
import re

pages_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages")
output_file = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_FINAL_CLEANED.txt")

# OCR fixes mapping
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
    'cross­\nplainant': 'cross-complainant',
}

all_pages = []

page_files = sorted(pages_dir.glob("Page_*.txt"))
print(f"Processing {len(page_files)} pages...")

for page_file in page_files:
    with open(page_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove page markers
    content = content.replace('===== PAGE 1 =====\n\n', '')
    content = content.replace('\n===== END PAGE 1 =====', '')
    for i in range(2, 42):
        content = content.replace(f'===== PAGE {i} =====\n\n', '')
        content = content.replace(f'\n===== END PAGE {i} =====', '')
    
    lines = content.split('\n')
    
    # Remove line numbers section (1-28 at top of each page)
    cleaned_lines = []
    skip_numbers = True
    
    for line in lines:
        stripped = line.strip()
        
        # Skip pure number lines
        if skip_numbers and stripped and re.match(r'^[\d\s]+$', stripped):
            nums = re.findall(r'\d+', stripped)
            if nums and all(int(n) <= 28 for n in nums):
                continue
        
        # Once we hit real content, stop skipping
        if stripped and not re.match(r'^[\d\s]+$', stripped):
            skip_numbers = False
        
        if not skip_numbers:
            cleaned_lines.append(line)
    
    page_text = '\n'.join(cleaned_lines).strip()
    
    # Apply OCR fixes
    for old, new in ocr_fixes.items():
        page_text = page_text.replace(old, new)
    
    all_pages.append(page_text)
    page_num = page_file.stem.split('_')[1]
    print(f"  Processed page {page_num}")

# Combine all pages
final_text = '\n\n'.join(all_pages)

# Write to output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(final_text)

print(f"\n✓ Final cleaned SOD created: {output_file}")
print(f"  Total size: {len(final_text):,} characters")
print(f"  Total pages: {len(all_pages)}")
