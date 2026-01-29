# DraftShift Renamer

**Automated batch file renaming for litigation documents**

## Overview

DraftShift Renamer is a web-based tool that intelligently renames litigation document files to a standardized format: `YYMMDD – Document_Type.ext`

The system automatically:
- Extracts dates from file content and metadata
- Identifies document types (Motion, Declaration, Notice, etc.)
- Generates clean, professional filenames
- Allows custom overrides before download
- Exports as a ZIP file for easy integration into case management systems

## Features

### 🚀 Smart Auto-Detection
- **Date Extraction**: Parses dates from document content, docket numbers, and file metadata
- **Document Classification**: Recognizes 25+ litigation document types using dictionary matching + fuzzy matching
- **Confidence Scoring**: Shows how confident the system is about each detection (useful for QA)

### 📤 Batch Processing
- Upload up to 100 files at once
- Drag-and-drop interface
- Real-time preview before download
- Support for: PDF, DOCX, DOC, TXT, JPG, PNG

### ✏️ Custom Overrides
- Manually adjust detected dates if needed
- Override auto-detected document types
- Apply changes to entire batch at once

### 📦 ZIP Download
- All renamed files exported in single ZIP
- Preserves original file extensions
- Ready for immediate use in case management systems

## Supported Document Types

The system recognizes 25+ document types including:
- **Motions**: Motion for Summary Judgment, Motion to Compel, Motion in Limine, etc.
- **Pleadings**: Complaint, Answer, Amended Complaint
- **Declarations**: Declaration (Valdez), Declaration (Barkley), Sworn Declaration
- **Notices**: Notice of Motion, Notice of Deposition, Notice of Hearing
- **Oppositions & Replies**: Opposition to Motion, Reply to Opposition
- **Orders & Judgments**: Order, Judgment, Minute Order
- **Correspondence**: Letter, Email, Correspondence
- **Exhibits**: Exhibit A, Exhibit B, etc.

Custom document types can be added via the API.

## API Endpoints

### Base URL
```
/api/renamer
```

### Endpoints

#### 1. Analyze Files (Preview Only)
```
POST /api/renamer/analyze
```
Analyzes files without creating download. Useful for previewing results.

**Request**: Form data with `files` field (multipart/form-data)

**Response**:
```json
{
  "files": [
    {
      "original_name": "motion_2024.pdf",
      "renamed_to": "240115 – Motion for Summary Judgment.pdf",
      "detected_date": "2024-01-15",
      "detected_type": "Motion for Summary Judgment",
      "confidence": 0.95
    }
  ],
  "total_files": 1,
  "successful": 1,
  "errors": []
}
```

#### 2. Rename & Download
```
POST /api/renamer/rename-and-download
```
Analyzes files and returns ZIP download.

**Request**: Form data with `files` field (multipart/form-data)

**Response**: ZIP file (binary)

**Limit**: 100 files per request

#### 3. Preview with Details
```
POST /api/renamer/preview
```
Detailed preview including why each detection was made.

**Request**: Form data with `files` field (multipart/form-data)

**Response**:
```json
{
  "previews": [
    {
      "original_name": "motion_2024.pdf",
      "renamed_to": "240115 – Motion for Summary Judgment.pdf",
      "detected_date": "2024-01-15",
      "detected_type": "Motion for Summary Judgment",
      "confidence": 0.95,
      "date_sources": ["content"],
      "type_match_reason": "dictionary_match"
    }
  ]
}
```

#### 4. Custom Rename with Overrides
```
POST /api/renamer/custom-rename
```
Apply custom date/type overrides to files.

**Request**:
```json
{
  "files": [
    {
      "original_name": "motion.pdf",
      "override_date": "2024-01-15",
      "override_type": "Motion for Summary Judgment"
    }
  ]
}
```

**Response**: Same as analyze (with overrides applied)

#### 5. List Supported Document Types
```
GET /api/renamer/supported-types
```

**Response**:
```json
{
  "types": [
    "Motion for Summary Judgment",
    "Motion to Compel",
    "Declaration",
    "Notice of Motion",
    ...
  ],
  "total": 25
}
```

#### 6. Add Custom Document Type
```
POST /api/renamer/add-custom-type
```

**Request**:
```json
{
  "type_name": "Expert Report",
  "keywords": ["expert", "report", "declaration"],
  "jurisdiction": "SDCA"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Custom type 'Expert Report' added for SDCA"
}
```

## Usage Examples

### JavaScript/React

```javascript
// Upload files and get renamed versions
const files = [...]; // Array of File objects from input
const formData = new FormData();
files.forEach(file => formData.append('files', file));

const response = await fetch('/api/renamer/rename-and-download', {
  method: 'POST',
  body: formData
});

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'renamed-files.zip';
a.click();
```

### Python

```python
import requests

files = [
    ('files', open('motion.pdf', 'rb')),
    ('files', open('declaration.pdf', 'rb')),
]

response = requests.post(
    'http://localhost:8000/api/renamer/rename-and-download',
    files=files
)

with open('renamed-files.zip', 'wb') as f:
    f.write(response.content)
```

### cURL

```bash
curl -X POST \
  -F "files=@motion.pdf" \
  -F "files=@declaration.pdf" \
  http://localhost:8000/api/renamer/rename-and-download \
  -o renamed-files.zip
```

## Filename Format

All files are renamed to:
```
YYMMDD – Document_Type.ext
```

**Components**:
- **YYMMDD**: Two-digit year, month, day (e.g., 240115 = January 15, 2024)
- **–**: Separator (en dash)
- **Document_Type**: Normalized document type (spaces, capitalization preserved)
- **.ext**: Original file extension

**Examples**:
- `240115 – Motion for Summary Judgment.pdf`
- `240220 – Declaration (Valdez).docx`
- `240305 – Opposition to Motion in Limine.pdf`

## Date Detection Priority

Dates are detected in this priority order:

1. **User-provided date** (if given)
2. **Docket number** (parses dates from court filings)
3. **Content extraction** (regex patterns in document text)
4. **File metadata** (created_at, modified_at timestamps)
5. **Default** (today's date)

## Behind the Scenes: FilenameNormalizer

DraftShift Renamer is built on the `FilenameNormalizer` module:

```python
from filename_normalizer import FilenameNormalizer

normalizer = FilenameNormalizer()

result = normalizer.normalize(
    original_filename="motion_jan2024.pdf",
    file_content="...",  # Raw file text/content
    jurisdiction="SDCA"  # Optional
)

print(result.renamed_filename)  # "240115 – Motion for Summary Judgment.pdf"
print(result.confidence)         # 0.95
print(result.detected_date)      # datetime(2024, 1, 15)
print(result.detected_type)      # "Motion for Summary Judgment"
```

## Configuration

### Environment Variables

```bash
# Port for API server
PORT=8000

# Max files per request
MAX_FILES_PER_REQUEST=100

# Temp directory for file processing
TEMP_DIR=/tmp/draftshift-renamer

# Jurisdiction (affects date/document patterns)
JURISDICTION=SDCA
```

### Adding Custom Document Types

```python
from filename_normalizer import FilenameNormalizer

normalizer = FilenameNormalizer()

# Add custom document type
normalizer.add_custom_documents({
    "Expert Report": {
        "keywords": ["expert", "report", "declaration", "testify"],
        "slug": "expert_report"
    }
})

# Register jurisdiction-specific patterns
normalizer.register_jurisdiction("SDCA", {
    "date_patterns": [...],
    "document_types": {...}
})
```

## Testing

### Run Unit Tests

```bash
python -m pytest test_filename_normalizer.py -v

# With coverage
python -m pytest test_filename_normalizer.py --cov=filename_normalizer
```

### Test with API

```bash
# Start server
python run_server.py

# Test in another terminal
curl -X POST \
  -F "files=@test.pdf" \
  http://localhost:8000/api/renamer/analyze
```

## Performance

- **Single file**: < 100ms
- **10 files**: < 500ms  
- **100 files**: < 2s
- **ZIP creation**: Adds ~100ms per file

All processing is **local** - no cloud dependencies, no external API calls.

## Privacy & Security

- ✅ **Local processing only** - files never leave your server
- ✅ **No external APIs** - FilenameNormalizer is self-contained
- ✅ **Temporary storage** - files deleted immediately after processing
- ✅ **No logging** - sensitive filenames not logged to disk

## Deployment

### Replit
```bash
python run_server.py
```

### Docker
```bash
docker build -f Dockerfile.renamer -t draftshift-renamer .
docker run -p 8000:8000 draftshift-renamer
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python run_server.py

# Open browser to http://localhost:8000
```

## Roadmap

- [ ] OCR support for scanned documents (date/type extraction from images)
- [ ] Batch processing with webhook notifications
- [ ] Integration with Box, OneDrive, Google Drive
- [ ] Machine learning refinement (learning from corrections)
- [ ] Jurisdiction-specific abbreviations in filenames
- [ ] Automatic upload to case management systems (LexisNexis, Everlaw, etc.)

## Support

For bugs, feature requests, or questions:
1. Check [GitHub Issues](https://github.com/taurinrobinson/saoriverse-console/issues)
2. Review [FilenameNormalizer documentation](FILENAME_NORMALIZER_EXAMPLES.py)
3. Check [test examples](test_filename_normalizer.py)

## License

DraftShift Renamer is part of the DraftShift platform. See [LICENSE](../LICENSE) for details.

---

**Built for litigators. Used daily by law firms.**
