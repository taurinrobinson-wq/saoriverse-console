#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from analyze_template import analyze_docx

# Analyze the properly formatted template
print("=" * 80)
print("ANALYZING: Cho,HaMobilitasRespRFA.docx (PROPER FORMAT - THE TEMPLATE)")
print("=" * 80)
analyze_docx('docs/Cho,HaMobilitasRespRFA.docx')

print("\n\n")
print("=" * 80)
print("ANALYZING: Test.docx (INPUT TO REFORMAT)")
print("=" * 80)
analyze_docx('docs/Test.docx')
