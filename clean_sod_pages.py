#!/usr/bin/env python3
"""
Clean extracted pages - remove line numbers and fix formatting issues
"""

from pathlib import Path
import re

pages_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages")
cleaned_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages_Cleaned")

# Create cleaned directory
cleaned_dir.mkdir(parents=True, exist_ok=True)

# Process each page
page_files = sorted(pages_dir.glob("Page_*.txt"))
print(f"Found {len(page_files)} page files to clean")

for page_file in page_files:
    with open(page_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract page number from filename
    page_num = page_file.stem.split('_')[1]
    
    # Remove the header/footer markers
    lines = content.split('\n')
    
    # Find where the actual content starts (skip line number section at top)
    content_lines = []
    skip_line_numbers = True
    
    for line in lines:
        # Skip the page markers and line number section
        if '===== PAGE' in line or '===== END PAGE' in line:
            continue
        
        # Skip lines that are just numbers 1-28
        if skip_line_numbers and re.match(r'^\s*\d+\s*$', line):
            continue
        
        # Once we hit actual content, stop skipping
        if line.strip() and not re.match(r'^\s*\d+\s*$', line):
            skip_line_numbers = False
        
        if not skip_line_numbers or line.strip():
            content_lines.append(line)
    
    # Join and clean up
    cleaned_content = '\n'.join(content_lines).strip()
    
    # Fix common OCR/formatting issues
    cleaned_content = cleaned_content.replace('withinterruptions', 'with interruptions')
    cleaned_content = cleaned_content.replace('Angel_es', 'Angeles')
    cleaned_content = cleaned_content.replace('presiding ,', 'presiding,')
    cleaned_content = cleaned_content.replace('thereafter ,', 'thereafter,')
    cleaned_content = cleaned_content.replace('testimony ,', 'testimony,')
    cleaned_content = cleaned_content.replace('Norris, ', 'Norris, ')
    cleaned_content = cleaned_content.replace('Greenfield .', 'Greenfield.')
    cleaned_content = cleaned_content.replace('Decision .', 'Decision.')
    cleaned_content = cleaned_content.replace('Pak on the objections raised by plaintiffs.', 'Pak on the objections raised by plaintiffs.')
    cleaned_content = cleaned_content.replace('/Cross-comp lainants', '/Cross-complainants')
    cleaned_content = cleaned_content.replace('cross-comp laint', 'cross-complaint')
    cleaned_content = cleaned_content.replace('defendant s', 'defendants')
    cleaned_content = cleaned_content.replace('plaintiff s', 'plaintiffs')
    cleaned_content = cleaned_content.replace('Conversion ;', 'Conversion;')
    cleaned_content = cleaned_content.replace('Advantage ;', 'Advantage;')
    cleaned_content = cleaned_content.replace('Duty.', 'Duty.')
    cleaned_content = cleaned_content.replace('successfu l', 'successful')
    cleaned_content = cleaned_content.replace('defendant s', 'defendants')
    cleaned_content = cleaned_content.replace('white defendant s', 'white defendants')
    
    # Save cleaned version
    output_file = cleaned_dir / page_file.name
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Cleaned Page {page_num}")

print(f"\nCleaning complete: {len(page_files)} pages saved to {cleaned_dir}")
