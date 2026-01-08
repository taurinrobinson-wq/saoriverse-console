# SPINE v2 Parser
## Semantic Parsing & Ingestion Normalization Engine

Comprehensive injury extraction and legal settlement statement parsing for IVC filter litigation and related medical-legal documents.

### Features

**Mechanical Failure Detection**
- Fracture / fragmentation
- Migration patterns
- Embedment depth
- Tilt / angulation
- Occlusion / thrombosis
- Discontinuous limb detection

**Perforation & Penetration Analysis**
- Grade 1-4 perforation classification
- Penetration depth (mm) with sanity checks (1-50mm)
- Multi-organ involvement tracking
- Dangerous location flagging (adjacent to, abutting, contacting)

**Retrieval Status Signals**
- Retrieval attempt failed / unsuccessful
- Complex retrieval (multiple techniques attempted)
- Open surgical removal required
- Retrieval not recommended
- Firmly embedded / irretrievable

**Complications & Clinical Impact**
- Chronic pain (back, abdominal)
- Nerve involvement
- Vital organ impact
- Tachycardia / hypotension during retrieval
- Multiple complication tracking

**Organ Involvement**
- Right/left kidney
- Aorta
- Duodenum
- Vertebra / spine
- Psoas
- Retroperitoneum
- Peritoneal fat
- Hip

### Architecture

```
spine_parser.py (main extraction engine)
├── extract_all_injuries()     → Semantic sweep of text for all injury signals
├── build_summary()             → Litigation-grade narrative assembly
├── join_list_clean()           → Grammar-aware list joining
├── PATTERNS dict               → Comprehensive regex + keyword library
└── PDF extraction pipeline
    ├── extract_text()          → pdfplumber + preprocessing
    ├── preprocess_text()       → 4-layer text reconstruction
    ├── split_cases()           → Case-by-case splitting
    ├── extract_plaintiff()     → Multi-pattern name extraction
    ├── extract_case_number()   → Federal docket pattern matching
    ├── detect_brand()          → Cook IVC filter brand detection
    └── extract_amounts()       → Dollar amount extraction

rebuild_*.py modules           → Text reconstruction for fragmented PDFs
├── rebuild_caption.py         → Multi-line plaintiff name reconstruction
├── rebuild_case_number.py     → Case number reassembly
├── rebuild_addresses.py       → Address line merging
└── rebuild_medical_history.py → Narrative text reconstruction
```

### Usage

```bash
python spine_parser.py <input_pdf> <output_csv>
```

Example:
```bash
python spine_parser.py JustSettlementStatements.pdf output_clean.csv
```

### Output Format

CSV with columns:
- **Plaintiff Name**: Full plaintiff name (including o/b/o, deceased designations)
- **Case Number**: Federal docket number (e.g., 1:16-cv-02989)
- **Injury Summary**: Litigation-grade narrative covering:
  - Perforation grade
  - Device mechanical state
  - Penetration depth + organ involvement
  - Retrieval complexity
  - Complications
- **Product Brand**: Cook Celect or Cook Gunther Tulip
- **Total Demanded**: Maximum settlement amount in dollars

### Example Output

```
"Robert Tavares","1:16-cv-02989","Grade 4 perforation with fractured, embedded, tilted and migrated device with ~13 mm strut penetration into the right kidney; irretrievable","Cook Celect","273000"

"Derrill Everette","1:17-cv-02799","Grade 4 perforation with embedded device into the psoas and vertebra","Cook Celect","185500"

"Vonda Webb","1:19-cv-03387","Grade 4 perforation with fractured device with ~6 mm strut penetration into multiple structures (aorta, duodenum, vertebra)","Cook Celect","182500"
```

### SPINE v2 Extraction Categories

#### A. Mechanical Failures
- `fracture` / `fractured` / `discontinuous limb`
- `fragment` / `fragment location`
- `migration` / `migrated`
- `tilt` / `tilted`
- `embedment` / `embedded`
- `occlusion` / `occluded`
- `thrombosis` / `thrombosed`
- `clog` / `clot burden`

#### B. Perforation & Penetration
- Grade 1–4 perforation (clinical severity marker)
- Perforation without grade
- Penetration depth (mm with sanity checks)
- Organ involvement (kidney, aorta, duodenum, vertebra, psoas, retroperitoneum, peritoneal fat, spine, hip)
- Multi-organ involvement
- Abutting / contacting signals

#### C. Retrieval-Related
- Unsuccessful / failed retrieval
- Retrieval attempt failed / aborted
- Complex retrieval (multiple techniques)
- Open surgical removal required
- Retrieval not recommended
- Firmly embedded
- Irretrievable

#### D. Complications & Impact
- Chronic back / abdominal pain
- Nerve involvement
- Vital organ impact
- Tachycardia / hypotension
- Multiple complication tracking

### Dependencies

- `pdfplumber` — PDF text extraction
- `pandas` — DataFrame and CSV operations
- `rapidfuzz` — Optional fuzzy matching (not currently used)
- Python 3.7+

### Installation

```bash
pip install pdfplumber pandas
```

### Architecture Notes

1. **Text Preprocessing**: The parser applies 4 sequential reconstruction layers to handle fragmented text common in PDFs:
   - Caption rebuilding (multi-line plaintiff names)
   - Case number reassembly
   - Address reconstruction
   - Medical history merging

2. **Semantic Extraction**: `extract_all_injuries()` performs a comprehensive sweep of the entire plaintiff block, returning a structured dictionary of all injury signals found.

3. **Litigation-Grade Summarization**: `build_summary()` assembles the extracted signals into expert-report-style prose using severity-first ordering:
   - Perforation grade (clinical severity)
   - Mechanical failures (device state)
   - Penetration + organs
   - Dangerous locations
   - Retrieval complexity
   - Complications

4. **Production-Ready Output**: All summaries are capped at 250 characters, properly punctuated, and formatted for legal use.

### Notes

- SPINE v2 captures all major injury categories from Cook IVC filter litigation documents
- Extensible pattern library for additional injury types
- Organ lists are automatically deduplicated and sorted
- Penetration measurements are sanity-checked (1-50mm valid range)
- No trailing periods in summaries (user preference for legal narrative style)
