#!/usr/bin/env python3
"""
Multi-file PDF Parser for Cook IVC Filter Settlement Cases
Processes both JustSettlementStatements.pdf and individual case PDFs
"""

import pdfplumber
import pandas as pd
import csv
import re
from pathlib import Path
from typing import Dict, List, Any
import sys

sys.path.insert(0, str(Path(__file__).parent))
from spine_parser import (
    preprocess_text, split_cases, extract_plaintiff, extract_case_number,
    detect_brand, extract_amounts, extract_all_injuries, build_summary
)

def process_multi_file(main_pdf: str, additional_pdfs: List[str]) -> pd.DataFrame:
    """Process main PDF and additional individual case PDFs"""
    
    rows = []
    
    # Process main PDF
    print(f"Processing {main_pdf}...")
    with pdfplumber.open(main_pdf) as pdf:
        text = "\n\n".join(page.extract_text() for page in pdf.pages)
    
    text = preprocess_text(text)
    cases = split_cases(text)
    
    for case_text in cases:
        plaintiff = extract_plaintiff(case_text)
        if not plaintiff:
            continue
        
        case_num = extract_case_number(case_text)
        brand = detect_brand(case_text)
        amounts = extract_amounts(case_text)
        amount = max(amounts) if amounts else None
        injuries = extract_all_injuries(case_text)
        summary = build_summary(injuries)
        
        rows.append({
            'Plaintiff Name': plaintiff,
            'Case Number': case_num,
            'Injury Summary': summary,
            'Product Brand': brand,
            'Total Demanded': amount
        })
    
    # Process additional PDFs
    for pdf_path in additional_pdfs:
        print(f"Processing {pdf_path}...")
        if not Path(pdf_path).exists():
            print(f"  WARNING: File not found: {pdf_path}")
            continue
        
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n\n".join(page.extract_text() for page in pdf.pages)
        
        # For individual case PDFs, extract only the settlement statement (before medical records)
        exhibit_idx = text.find("EXHIBIT A")
        if exhibit_idx >= 0:
            text = text[:exhibit_idx]
        
        text = preprocess_text(text)
        cases = split_cases(text)
        
        for case_text in cases:
            plaintiff = extract_plaintiff(case_text)
            if not plaintiff:
                continue
            
            case_num = extract_case_number(case_text)
            brand = detect_brand(case_text)
            amounts = extract_amounts(case_text)
            amount = max(amounts) if amounts else None
            injuries = extract_all_injuries(case_text)
            summary = build_summary(injuries)
            
            rows.append({
                'Plaintiff Name': plaintiff,
                'Case Number': case_num,
                'Injury Summary': summary,
                'Product Brand': brand,
                'Total Demanded': amount
            })
    
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main_pdf = "Raw_Data_Docs/JustSettlementStatements.pdf"
    additional_pdfs = [
        "Raw_Data_Docs/17-cv-02775 - GoodwinConfSettlementStmt.pdf"
    ]
    
    df = process_multi_file(main_pdf, additional_pdfs)
    
    # Write to CSV
    output_file = "Output/JustSettlementStatements_Complete.csv"
    df.to_csv(output_file, quoting=csv.QUOTE_ALL, index=False)
    
    print(f"\nWrote {len(df)} rows to {output_file}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
