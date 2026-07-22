# Darwin Document Pipeline v2

**Legal Document Formatting & Analysis Pipeline**

Convert messy legal documents into court-ready formatted files with one click.

## Features

✨ **Document Analysis**
- Detects 8+ types of legal headings (interrogatories, requests, admissions, etc.)
- Analyzes current formatting inconsistencies
- Provides improvement recommendations

🎨 **Template-Based Reformatting**
- **California Discovery** - Discovery documents (interrogatories, requests, admissions)
- **California Pleading** - Court pleadings (complaints, answers, motions)
- **Generic Contract** - Professional contract formatting

📥 **Upload & Download**
- Upload .docx files for analysis
- One-click reformatting with selected template
- Download reformatted documents immediately

## Getting Started

### Installation

```bash
cd Darwin/document-pipeline
npm install
```

### Running the Server

```bash
npm start
```

Server runs on `http://localhost:3000`

### Development (with auto-reload)

```bash
npm run dev
```

## How It Works

1. **Upload** a Word document (.docx)
2. **Analyze** - Darwin detects headings and formatting issues
3. **Select Template** - Choose California Discovery, Pleading, or Contract
4. **Reformat** - One click applies consistent formatting
5. **Download** - Get your court-ready document

## Project Structure

```
Darwin/document-pipeline/
├── backend/
│   ├── server.js              # Express API server
│   ├── templates.js           # Formatting templates (CA Discovery, Pleading, Contract)
│   ├── headingPatterns.js     # Legal heading detection patterns
│   ├── docxProcessor.js       # DOCX parsing and formatting
│   └── package.json
├── public/
│   └── index.html            # Web interface
├── uploads/                  # Temporary uploaded files
├── output/                   # Reformatted documents for download
└── package.json
```

## API Endpoints

### GET `/api/templates`
Returns list of available formatting templates

**Response:**
```json
[
  {
    "id": "ca_discovery",
    "name": "California Discovery",
    "description": "California discovery document formatting..."
  }
]
```

### POST `/api/analyze`
Upload and analyze a document

**Request:** multipart/form-data with `document` file

**Response:**
```json
{
  "fileName": "contract.docx",
  "fileSize": 15234,
  "paragraphs": 24,
  "detectedHeadings": [
    { "type": "Topic Section", "text": "Topic 1: Background" }
  ],
  "recommendations": [...]
}
```

### POST `/api/reformat`
Reformat document with selected template

**Request:**
```json
{
  "template": "ca_pleading"
}
```

**Response:**
```json
{
  "success": true,
  "fileName": "darwin-reformatted-ca_pleading-1721692800000.docx",
  "template": "California Pleading",
  "downloadUrl": "/download/darwin-reformatted-ca_pleading-1721692800000.docx"
}
```

### GET `/download/:fileName`
Download a reformatted document

## Templates

### California Discovery
- **Font:** Times New Roman 12pt
- **Line Spacing:** Double (2.0)
- **Margins:** 1 inch all sides
- **Headings:** Bold, uppercase numbers, double-spaced
- **Use for:** Interrogatories, Requests for Production, Requests for Admission

### California Pleading
- **Font:** Times New Roman 12pt
- **Line Spacing:** Double (2.0)
- **Margins:** 1 inch all sides
- **First Line Indent:** 0.5 inch
- **Headings:** Bold, underlined, section numbering
- **Use for:** Complaints, Answers, Motions, Court filings

### Generic Contract
- **Font:** Arial 11pt
- **Line Spacing:** 1.5
- **Margins:** 1 inch all sides
- **Headings:** Bold and underlined
- **Use for:** Contracts, agreements, professional documents

## Legal Heading Detection

Automatically detects and formats:
1. Interrogatory No. X
2. Special Interrogatory No. X
3. Form Interrogatory No. X
4. Request for Production No. X
5. Request for Admission No. X
6. Topic X sections
7. Document Request No. X
8. ALL CAPS section headings

## Future Enhancements

- **v2.1:** Custom template upload/creation
- **v2.2:** Document history and saved projects
- **v2.3:** Batch document processing
- **v2.4:** Advanced linting engine (formatting validation)
- **v2.5:** API key authentication for headless usage
- **v3.0:** Desktop application (Electron)

## Technology Stack

- **Backend:** Node.js + Express
- **Document Processing:** docx, mammoth
- **File Upload:** multer
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Storage:** Local filesystem (disk)

## License

ISC

## Author

Taurin Robinson

---

**Darwin: Making legal documents beautiful, one template at a time.** ✨
