"""Medical record normalization utilities for CaseGrid."""
from __future__ import annotations

import io
import re
from datetime import date, datetime
from typing import Any

_DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b"),
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
]

_DOB_PATTERNS = [
    re.compile(r"\b(?:dob|date\s*of\s*birth)\s*[:\-]\s*([A-Za-z0-9, /-]+)", re.IGNORECASE),
]

_DIAG_PATTERNS = [
    re.compile(r"\b(?:diagnosis\s*date|date\s*of\s*diagnosis)\s*[:\-]\s*([A-Za-z0-9, /-]+)", re.IGNORECASE),
]

_PATHOLOGY_TERMS = [
    "pathology",
    "biopsy",
    "specimen",
    "histology",
    "operative pathology",
]

_OVARIAN_TERMS = [
    "ovarian carcinoma",
    "ovarian cancer",
    "metastatic ovarian carcinoma",
    "peritoneal carcinomatosis",
    "malignant ascites",
]

_CHEMO_TERMS = [
    "carboplatin",
    "paclitaxel",
    "taxol",
    "carbo/taxol",
    "carbo taxol",
]

_BRCA_PATTERNS = [
    re.compile(r"\bbrca\s*positive\b", re.IGNORECASE),
    re.compile(r"\bbrca\s*negative\b", re.IGNORECASE),
    re.compile(r"\bbrca\s*1\b|\bbrca1\b", re.IGNORECASE),
    re.compile(r"\bbrca\s*2\b|\bbrca2\b", re.IGNORECASE),
]

# Patterns for service/admit/discharge/print dates found in medical records
_DIAGNOSIS_DATE_PATTERNS = [
    re.compile(r"\bservice\s*date(?:/time)?\s*[:\-]\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\badmit(?:ted)?(?:\s*date)?\s*[:\-]\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\badmission\s*date\s*[:\-]\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bdischarge\s*date\s*[:\-]\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bprint\s*date(?:/time)?\s*[:\-]\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\breport\s*request\s*id[^\n]{0,60}(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bdate\s*of\s*service\s*[:\-]\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
]


def _extract_snippet(page_text: str, keyword: str) -> str:
    """Return 1-2 sentences surrounding keyword in page_text (max 300 chars)."""
    lower = page_text.lower()
    pos = lower.find(keyword.lower())
    if pos == -1:
        return page_text[:200].strip()

    start = max(0, pos - 150)
    end = min(len(page_text), pos + len(keyword) + 150)
    snippet = page_text[start:end].strip()

    # Try to trim to a clean sentence start
    boundary = re.search(r'(?:[.!?]\s+)([A-Z])', snippet)
    if boundary and boundary.start() < 80:
        snippet = snippet[boundary.start() + 1:].strip()

    # Trim at last sentence end
    last_end = max(
        snippet.rfind("."),
        snippet.rfind("!"),
        snippet.rfind("?"),
    )
    if 0 < last_end < len(snippet) - 1:
        snippet = snippet[: last_end + 1]

    return snippet[:300]


def _extract_diagnosis_date(pages: list[str]) -> date | None:
    """
    Scan all pages for service/admit/discharge/print date patterns.
    Returns the earliest valid date found (most likely the diagnosis encounter).
    """
    candidates: list[date] = []
    for page_text in pages:
        for pattern in _DIAGNOSIS_DATE_PATTERNS:
            for match in pattern.finditer(page_text):
                dt = _parse_date(match.group(1))
                if dt:
                    candidates.append(dt)
    return min(candidates) if candidates else None


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    value = raw.strip().replace(",", "")
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%B %d %Y", "%b %d %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    for pattern in _DATE_PATTERNS:
        match = pattern.search(value)
        if not match:
            continue
        token = match.group(1)
        for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(token, fmt).date()
            except ValueError:
                continue
    return None


def _extract_pages(file_bytes: bytes) -> list[str]:
    pages: list[str] = []
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [(p.extract_text() or "") for p in pdf.pages]
    except Exception:
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [(p.extract_text() or "") for p in reader.pages]
        except Exception:
            pages = []
    return pages


def _find_first_by_patterns(text: str, patterns: list[re.Pattern[str]]) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def normalize_medical_record(file_bytes: bytes) -> dict[str, Any]:
    """Normalize a medical record PDF into structured fields plus page evidence."""
    pages = _extract_pages(file_bytes)
    full_text = "\n".join(pages)
    lower_text = full_text.lower()

    evidence: list[dict[str, Any]] = []

    def add_evidence(page_number: int, page_text: str, normalized: str, keyword: str = "") -> None:
        snippet = _extract_snippet(page_text, keyword or normalized)
        evidence.append(
            {
                "page": page_number,
                "text": snippet,
                "normalized": normalized,
            }
        )

    primary_cancer: str | None = None
    metastatic = False

    for idx, page_text in enumerate(pages, start=1):
        page_lower = page_text.lower()
        for term in _OVARIAN_TERMS:
            if term in page_lower:
                primary_cancer = "ovarian cancer"
                if "metastatic" in term:
                    metastatic = True
                add_evidence(idx, page_text, "ovarian cancer", keyword=term)
                break

        if (
            "metastatic adenocarcinoma" in page_lower
            and ("ovarian" in page_lower or "peritoneal" in page_lower)
        ):
            primary_cancer = "ovarian cancer"
            metastatic = True
            add_evidence(idx, page_text, "metastatic ovarian cancer context", keyword="metastatic adenocarcinoma")

        for chemo in _CHEMO_TERMS:
            if chemo in page_lower:
                if primary_cancer is None:
                    primary_cancer = "possible ovarian cancer"
                add_evidence(idx, page_text, f"chemo evidence: {chemo}", keyword=chemo)
                break

        for term in _PATHOLOGY_TERMS:
            if term in page_lower:
                add_evidence(idx, page_text, "pathology", keyword=term)
                break

        for brca_pattern in _BRCA_PATTERNS:
            m = brca_pattern.search(page_text)
            if m:
                add_evidence(idx, page_text, "brca", keyword=m.group(0))
                break

    pathology_present = any(e["normalized"] == "pathology" for e in evidence)

    if re.search(r"\bmetastatic\b", lower_text):
        metastatic = True

    brca_result = "Unknown"
    if re.search(r"\bbrca\s*positive\b", lower_text):
        brca_result = "Positive"
    elif re.search(r"\bbrca\s*negative\b", lower_text):
        brca_result = "Negative"
    elif re.search(r"\bbrca\s*1\b|\bbrca1\b", lower_text):
        brca_result = "BRCA1 Mentioned"
    elif re.search(r"\bbrca\s*2\b|\bbrca2\b", lower_text):
        brca_result = "BRCA2 Mentioned"

    dob_raw = _find_first_by_patterns(full_text, _DOB_PATTERNS)
    dob_date = _parse_date(dob_raw)

    # Try explicit diagnosis date patterns first, then service/admit dates, then fallback
    diagnosis_raw = _find_first_by_patterns(full_text, _DIAG_PATTERNS)
    diagnosis_date = _parse_date(diagnosis_raw)
    if diagnosis_date is None:
        diagnosis_date = _extract_diagnosis_date(pages)
    if diagnosis_date is None:
        # Last resort: earliest date anywhere in document
        all_dates: list[date] = []
        for match in re.finditer(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b", full_text):
            dt = _parse_date(match.group(0))
            if dt:
                all_dates.append(dt)
        if all_dates:
            diagnosis_date = min(all_dates)

    age_at_diagnosis: int | None = None
    if dob_date and diagnosis_date and diagnosis_date >= dob_date:
        age_at_diagnosis = int((diagnosis_date - dob_date).days / 365.25)

    return {
        "dob": dob_date.isoformat() if dob_date else None,
        "age_at_diagnosis": age_at_diagnosis,
        "primary_cancer": primary_cancer,
        "metastatic": metastatic,
        "pathology_present": pathology_present,
        "brca_result": brca_result,
        "diagnosis_date": diagnosis_date.isoformat() if diagnosis_date else None,
        "page_count": len(pages),
        "evidence": evidence,
    }
