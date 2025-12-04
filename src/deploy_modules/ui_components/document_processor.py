"""
Document Processing Component.

Handles file uploads and multi-format document extraction.
Supports: txt, docx, pdf, md, html, csv, xlsx, json
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def process_uploaded_file(uploaded_file) -> str:
    """Extract text from uploaded file based on format.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        Extracted text or error message
    """
    if not uploaded_file:
        return None

    try:
        file_ext = uploaded_file.name.lower().split(".")[-1]

        if file_ext == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore")

        elif file_ext == "docx":
            try:
                from docx import Document
                doc = Document(uploaded_file)
                return "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                return f"Error reading Word document: {e}"

        elif file_ext == "pdf":
            try:
                import pdfplumber
                with pdfplumber.open(uploaded_file) as pdf:
                    return "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
            except Exception as e:
                return f"Error reading PDF: {e}"

        elif file_ext == "md":
            try:
                import markdown
                from bs4 import BeautifulSoup
                raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
                html = markdown.markdown(raw_text)
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text()
            except Exception as e:
                return f"Error reading Markdown: {e}"

        elif file_ext in ["html", "htm"]:
            try:
                from bs4 import BeautifulSoup
                raw_html = uploaded_file.read().decode("utf-8", errors="ignore")
                soup = BeautifulSoup(raw_html, "html.parser")
                return soup.get_text()
            except Exception as e:
                return f"Error reading HTML: {e}"

        elif file_ext == "csv":
            try:
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                return df.to_string(index=False)
            except Exception as e:
                return f"Error reading CSV: {e}"

        elif file_ext in ["xlsx", "xls"]:
            try:
                import pandas as pd
                df = pd.read_excel(uploaded_file)
                return df.to_string(index=False)
            except Exception as e:
                return f"Error reading Excel: {e}"

        elif file_ext == "json":
            try:
                import json
                raw_json = uploaded_file.read().decode("utf-8", errors="ignore")
                data = json.loads(raw_json)
                return json.dumps(data, indent=2)
            except Exception as e:
                return f"Error reading JSON: {e}"

        else:
            return f"Unsupported file format: {file_ext}"

    except Exception as e:
        logger.error(f"File processing error: {e}")
        return f"Error processing file: {e}"


def display_document_info(file_name: str, file_text: str):
    """Display information about uploaded document.

    Args:
        file_name: Original file name
        file_text: Extracted text content
    """
    try:
        file_ext = file_name.lower().split(".")[-1].upper()
        char_count = len(file_text) if file_text else 0
        word_count = len(file_text.split()) if file_text else 0

        first_line = file_text.split(
            "\n", 1)[0][:60] if file_text else "Document"

        st.success(f"✅ {file_ext} document uploaded successfully!")
        st.info(f"📄 {first_line}...")
        st.caption(f"Size: {char_count} characters, ~{word_count} words")

    except Exception as e:
        logger.debug(f"Error displaying document info: {e}")


def store_document_in_session(document_text: str):
    """Store uploaded document in session state.

    Args:
        document_text: Document text content
    """
    try:
        st.session_state["uploaded_text"] = document_text
        st.session_state["has_document"] = True
    except Exception as e:
        logger.debug(f"Error storing document: {e}")


def get_stored_document() -> str:
    """Retrieve stored document from session.

    Returns:
        Document text or empty string
    """
    return st.session_state.get("uploaded_text", "")


def clear_stored_document():
    """Clear stored document from session."""
    try:
        st.session_state.pop("uploaded_text", None)
        st.session_state.pop("has_document", None)
    except Exception as e:
        logger.debug(f"Error clearing document: {e}")


def is_document_available() -> bool:
    """Check if a document is currently stored.

    Returns:
        True if document is available
    """
    return st.session_state.get("has_document", False)
