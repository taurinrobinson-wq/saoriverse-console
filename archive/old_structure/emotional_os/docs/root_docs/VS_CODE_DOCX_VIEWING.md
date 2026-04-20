# 📄 DOCX Viewing in VS Code - Your Complete Guide

## ⚡ QUICK START

When you have a DOCX file open or selected in VS Code:

1. **Press Ctrl+Shift+P** (or Cmd+Shift+P on Mac) 2. **Type "Run Task"** and select it 3. **Choose
one of these:**
   - **"View DOCX in Browser"** → Opens in web viewer (best for reading)
   - **"View DOCX as Text"** → Shows in terminal (quick preview)
   - **"Export DOCX to JSON"** → Extracts all data (for processing)

## 🔧 VS Code Extensions Installed

You also have two extensions that provide additional viewing options:

### **OpenXml Package Explorer** (View document structure)

- Right-click any `.docx` file → "Open with OpenXml Package Explorer"
- Shows XML structure, styles, numbering, metadata
- Best for: Inspecting document internals

### **LibreOffice Preview** (Preview rendered layout)

- Right-click any `.docx` file → "Open with LibreOffice Preview"
- Shows document as it appears in Word
- Best for: Seeing actual formatting and layout

## 🐍 Python Tools (For scripting/automation)

You also have command-line tools:

```bash

# View formatted in terminal
python3 docx_reader.py document.docx

# Extract plain text
python3 docx_reader.py document.docx text

# Export as JSON
python3 docx_reader.py document.docx json

# Interactive Streamlit viewer
streamlit run docx_viewer.py

# Web-based viewer (opens in browser)
python3 docx_web_viewer.py document.docx
```


## 📋 What Each Method Does

| Method | Best For | How |
|--------|----------|-----|
| **Tasks (Run Task menu)** | Quick viewing | Ctrl+Shift+P → Run Task |
| **Web Viewer** | Reading formatted docs | "View DOCX in Browser" task |
| **Terminal Preview** | Quick text extraction | "View DOCX as Text" task |
| **JSON Export** | Data processing | "Export DOCX to JSON" task |
| **OpenXml Explorer** | Inspecting structure | Right-click → Open with |
| **LibreOffice Preview** | Rendered layout | Right-click → Open with |

## 🎯 Try It Now

1. **Find a DOCX file** in your workspace (try the one you mentioned) 2. **Right-click it** or have
it active in the editor 3. **Press Ctrl+Shift+P** and type "Run Task" 4. **Select "View DOCX in
Browser"** 5. A browser tab will open showing the document!

## � What You Get
