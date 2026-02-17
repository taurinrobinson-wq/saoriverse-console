#!/usr/bin/env python3
"""
Extract Statement of Decision PDF - One page per file
Creates 41 individual text files (pages 2-42 of 42-page PDF)
"""

import PyPDF2
from pathlib import Path

# PDF path
pdf_path = r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\BrownNorrisFinalStatementDecision(only).pdf"
output_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages")

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

# Open and extract PDF
try:
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        print(f"Total pages in PDF: {total_pages}")
        
        # Extract pages 2-42 (indices 1-41 in zero-based indexing)
        # Skip page 1 (index 0)
        for page_num in range(1, total_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Save to individual file
            # Page 2 of PDF = page 1 of our numbering (since we skip cover)
            our_page_num = page_num  # This will be 1-41
            output_file = output_dir / f"Page_{our_page_num:02d}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"===== PAGE {our_page_num} =====\n\n")
                f.write(text)
                f.write(f"\n\n===== END PAGE {our_page_num} =====")
            
            print(f"Extracted page {our_page_num} ({page_num + 1} of PDF) -> {output_file.name}")
        
        print(f"\nExtraction complete: {total_pages - 1} pages saved to {output_dir}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
