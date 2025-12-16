# 📄 DOCX Reader Support

Your codespace now has full DOCX (Word document) reading and viewing capabilities!

## What's Available

### ✅ Installed Packages
- **python-docx** (1.1.0) - Read and parse DOCX files
- **docx2txt** (0.9) - Convert DOCX to plain text
- **lxml** (5.3.0) - XML processing for document structure

## Usage Options

### 1. **Command Line Tool** (`docx_reader.py`)

View a DOCX file in the terminal:

```bash
python3 docx_reader.py document.docx view
```




Extract plain text:

```bash
python3 docx_reader.py document.docx text
```




Export as JSON:

```bash
python3 docx_reader.py document.docx json
python3 docx_reader.py document.docx json output.json
```




**Features:**
- 📋 Displays document metadata (title, author, created date, etc.)
- 📝 Shows all paragraphs with formatting info
- 📊 Displays tables in readable format
- 🎨 Highlights bold text with markers
- 📌 Shows document structure clearly

### 2. **Interactive Streamlit Viewer** (`docx_viewer.py`)

Launch the web viewer:

```bash
streamlit run docx_viewer.py
```




Then open the local URL in your browser.

**Features:**
- 👁️ **Document View** - Read formatted documents
- 🔍 **Raw Content** - Inspect JSON structure
- ℹ️ **Metadata** - View document properties
- 💾 **Export** - Download as JSON or TXT

### 3. **Python API** (Import in your code)

```python
from docx_reader import read_docx, docx_to_text, export_docx_json

# Read and parse DOCX
data = read_docx("document.docx")
print(data['paragraphs'])
print(data['tables'])
print(data['core_properties'])

# Extract plain text
text = docx_to_text("document.docx")
print(text)

# Export as JSON
export_docx_json("document.docx", "output.json")
```




## What Gets Extracted

From each DOCX file, we extract:

- **Metadata**
  - Title, author, subject
  - Created and modified dates

- **Paragraphs**
  - Text content
  - Style/heading level
  - Formatting flags (bold, italic)

- **Tables**
  - All cell contents
  - Row and column counts
  - Cell-by-cell data

## Quick Example

If you have a `sample.docx`:

```bash

# View formatted
python3 docx_reader.py sample.docx

# Output:

# ============================================================

# Document: sample.docx

# ============================================================
#

# 📋 DOCUMENT PROPERTIES

# ----------------------------------------
#   Title: My Document
#   Author: John Doe
#   Subject: Testing
#   Created: 2024-01-15 10:30:00
#   Modified: 2024-01-15 14:45:00
#

# 📝 CONTENT (3 paragraphs)

# ----------------------------------------

# 📌 This is the heading
#    This is a paragraph.
#    Another line.
#

# 📊 TABLES (1 table)

# ----------------------------------------
#

# Table 1 (2×3):
#   Header 1 | Header 2 | Header 3
#   Cell 1   | Cell 2   | Cell 3
```




## Integration into Your Apps

You can integrate DOCX reading into your Streamlit apps:

```python
import streamlit as st
from docx_reader import read_docx, print_docx_content

uploaded_file = st.file_uploader("Upload a DOCX file")
if uploaded_file:
    with open("temp.docx", "wb") as f:
        f.write(uploaded_file.getbuffer())

    data = read_docx("temp.docx")
    st.json(data)
```




## Notes

- DOCX files are actually ZIP archives containing XML - we're reading the content directly from the XML
- Complex formatting (fonts, colors, styles) are identified but returned as metadata
- Images embedded in documents are not extracted (only text and tables)
- All content is extracted programmatically - no document conversion needed

## Next Steps

1. **Try it out** with any DOCX file:
   ```bash
   python3 docx_reader.py your_file.docx
   ```

2. **Launch the viewer**:
   ```bash
   streamlit run docx_viewer.py
   ```

3. **Integrate into your apps** using the Python API

Happy document reading! 📚
