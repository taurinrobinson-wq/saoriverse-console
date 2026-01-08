# SPINE v2 - Semantic Parsing & Ingestion Normalization Engine

## Overview

SPINE v2 is a comprehensive PDF document processor specifically designed for Cook IVC Filter settlement case litigation documents. It extracts injury data, settlement amounts, and case information from confidential settlement statements and generates litigation-grade injury summaries.

## Folder Structure

```
tools/SPINE/
├── Raw_Data_Docs/              # Source PDFs
│   ├── JustSettlementStatements.pdf
│   └── 17-cv-02775 - GoodwinConfSettlementStmt.pdf
├── Output/                     # Generated CSV files
│   └── JustSettlementStatements_Complete.csv
├── spine_parser.py             # Main extraction engine
├── multi_file_parser.py        # Multi-document processor
├── goodwin_phase2_processor.py # Medical records processor
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── QUICK_REFERENCE.md          # Quick start guide
├── SPINE_v2_IMPLEMENTATION.md  # Implementation details
└── Documentation files...
```

## Quick Start

### Single PDF Processing
```bash
cd tools/SPINE
python spine_parser.py Raw_Data_Docs/JustSettlementStatements.pdf Output/results.csv
```

### Multi-File Processing (includes individual case PDFs)
```bash
cd tools/SPINE
python multi_file_parser.py
# Output: Output/JustSettlementStatements_Complete.csv
```

### Phase 2 - Medical Records Processing
```bash
cd tools/SPINE
python goodwin_phase2_processor.py
# Extracts medical records and cross-validates against settlement statement
```

## Key Features

### Phase 1: Settlement Statement Extraction
- **Case Information**: Plaintiff name, case number, age, location, implant type & date
- **Injury Signals** (40+ patterns):
  - Mechanical failures: fracture, migration, embedment, tilt, occlusion, thrombosis
  - Perforation grades (1-4) with penetration depth
  - Organ involvement (9 types)
  - Retrieval status: complex, failed, against recommendation
  - **Open surgical retrieval** (only from damages section)
  - Death signals
  - Complications: pain, nerve, tachycardia, hypotension
  
- **Value-Based Priority Ordering**:
  1. Death (highest value)
  2. Open surgical retrieval (performed procedures only)
  3. Device fracture
  4. Perforation grade + mechanical failures
  5. Penetration + organ involvement
  6. Retrieval complexity
  7. Dangerous locations
  8. Complications

### Phase 2: Medical Records Processing (In Development)
- Patient demographics extraction
- Admission/discharge dates
- Treating physician identification
- Treatment timeline reconstruction
- Procedure extraction
- Cross-validation against settlement claims

## Processing Output

### CSV Columns
| Column | Description |
|--------|-------------|
| Plaintiff Name | Full legal name with designations (o/b/o, deceased) |
| Case Number | Federal case number (e.g., 1:17-cv-02775) |
| Injury Summary | Litigation-grade narrative of injuries (max 250 chars) |
| Product Brand | Cook device type (Celect, Gunther Tulip, etc.) |
| Total Demanded | Settlement amount in dollars |

### Example Row
```
"Teresa Whetstone","1:17-cv-02671","underwent open surgical retrieval Grade 4 perforation with embedded, tilted and migrated device into the duodenum; complex retrieval; retrieval attempt failed in dangerous proximity to organ with complications including hypotension, tachycardia","Cook Celect","781500"
```

## Extracted Dataset

**Current Coverage**: 38 plaintiffs
- 1 death case with open surgical retrieval
- 5 fracture cases
- 32 perforation cases (Grades 1-4)
- Multiple penetration cases with organ involvement
- 4 death cases (filter-related fatality)

## Critical Patterns

### Open Surgical Retrieval Detection
**Only matches in damages section** (after "following values represent"):
- "Open abdonimal surgery Procedure" (includes typo handling)
- "Open abdominal surgery Procedure"

This ensures accurate distinction between:
- ✅ Procedures PERFORMED (actual damages claim)
- ❌ Procedures RECOMMENDED but NOT DONE (narrative mention)

## Technical Stack

- **Language**: Python 3.12.10
- **PDF Processing**: pdfplumber
- **Data Processing**: pandas, csv module
- **Text Processing**: regex (re)
- **Text Reconstruction**: 4-layer preprocessor chain

## Error Handling

### Known Limitations
1. OCR-dependent accuracy (scanned documents)
2. Typos in source documents (e.g., "abdonimal" vs "abdominal")
3. Medical records extraction requires Phase 2 processing
4. Case-sensitive pattern matching (all patterns case-insensitive internally)

### Common Issues

**PDF file not found**:
```
Error: PDF not found: <path>
```
→ Ensure PDF is in Raw_Data_Docs/ folder

**Invalid output path**:
```
FileNotFoundError: [Errno 2] No such file or directory
```
→ Output directory will be created automatically

## Development Notes

### Pattern Library
All extraction patterns defined in `PATTERNS` dictionary (spine_parser.py lines 45-62):
```python
PATTERNS = {
    "fracture": r"\bfractur(?:e|ed|ing)\b",
    "retrieval_open": r"open\s+abdonimal\s+surgery\s+procedure|open\s+abdominal\s+surgery\s+procedure",
    # ... 13 more patterns
}
```

### Preprocessing Pipeline
1. **rebuild_caption_lines**: Multi-line plaintiff names
2. **rebuild_case_numbers**: Case number reassembly
3. **rebuild_addresses**: Address line merging
4. **rebuild_medical_history**: Narrative text merging

### Value Prioritization
build_summary() function implements severity-first ordering:
- Highest value signals appear first
- Litigation-grade language ("fractured device" vs "fracture")
- Grammar-aware list joining (no comma before "and" for 2 items)

## Future Enhancements (Phase 2+)

- [ ] Medical records OCR processing
- [ ] Treatment timeline extraction
- [ ] Procedure classification system
- [ ] Cross-document validation
- [ ] Imaging findings extraction
- [ ] Automated settlement benchmarking
- [ ] Batch processing with status tracking
- [ ] Database integration for case management

## Support & Maintenance

For issues or enhancements:
1. Check QUICK_REFERENCE.md for common tasks
2. Review SPINE_v2_IMPLEMENTATION.md for technical details
3. Examine extracted data in Output/ folder
4. Verify source PDFs in Raw_Data_Docs/

---

**Version**: 2.0.0  
**Last Updated**: January 7, 2026  
**Status**: Phase 1 Complete ✅ | Phase 2 In Development 🚀
