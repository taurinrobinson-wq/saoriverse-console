import pdfplumber
import re

pdf_path = r"DraftShift\Docs\BrownVacateMtn\BrownNorrisFinalStatementDecision(only).pdf"

extracted_text = []

with pdfplumber.open(pdf_path) as pdf:
    # Skip first page (index 0), start from page 2 (index 1)
    for page_num, page in enumerate(pdf.pages[1:], start=2):
        # Extract text from page
        page_text = page.extract_text()
        
        if page_text:
            # Remove line numbers from left margin (1-28 or similar)
            # Pattern: start of line with numbers followed by space/tab, typically 1-3 digits
            cleaned_text = re.sub(r'^\s*\d{1,2}\s+', '', page_text, flags=re.MULTILINE)
            
            # Add page break marker
            extracted_text.append(f"\n===== PAGE {page_num} =====\n")
            extracted_text.append(cleaned_text)

# Write to output file
output_path = r"DraftShift\Docs\BrownVacateMtn\SOD_EXTRACTED_TEXT.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(extracted_text))

print(f"Extraction complete! Output saved to: {output_path}")
print(f"Total pages extracted: {len(pdf.pages) - 1}")
