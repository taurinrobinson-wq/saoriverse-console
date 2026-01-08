#!/usr/bin/env python3
"""
SPINE v2 Parser
Semantic Parsing & Ingestion Normalization Engine

Comprehensive injury extraction from legal settlement PDFs with:
- Mechanical failure detection (fracture, migration, embedment, tilt, occlusion, thrombosis)
- Perforation & penetration analysis
- Retrieval status signals
- Complications & impact assessment
- Multi-organ involvement tracking
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any
import pdfplumber
import pandas as pd
import csv

# Import text rebuilders from rebuild submodule
try:
    from .rebuild import (
        rebuild_caption_lines,
        rebuild_case_numbers,
        rebuild_addresses,
        rebuild_medical_history,
    )
except ImportError:
    # Fallback for standalone execution
    def rebuild_caption_lines(text):
        return text
    def rebuild_case_numbers(text):
        return text
    def rebuild_addresses(text):
        return text
    def rebuild_medical_history(text):
        return text


# =========================================================================
# PATTERN LIBRARY: Comprehensive injury signal extraction
# =========================================================================

PATTERNS = {
    "fracture": r"\bfractur(?:e|ed|ing)\b",
    "migration": r"\bmigrat(?:ed|ion)\b",
    "embedment": r"\bembed(?:ded|ment)\b",
    "tilt": r"\btilt(?:ed)?\b",
    "occlusion": r"\bocclusion\b|\boccluded\b",
    "thrombosis": r"\bthrombos(?:is|ed)\b",
    "death": r"\b(?:death|deceased|fatal|fatality|died)\b",
    "retrieval_open": r"open\s+abdonimal\s+surgery\s+procedure|open\s+abdominal\s+surgery\s+procedure",
    "dangerous_location": r"dangerous\s+location|abutting\s+(?:kidney|aorta|duodenum|vertebra|spine)",
    "perforation_grade": r"grade\s*(\d)",
    "perforation": r"\bperforat(?:ion|ing)\b",
    "penetration_mm": r"(\d+)\s*mm",
    "organs": r"(?:right\s+|left\s+)?(kidney|aorta|duodenum|vertebra|psoas|retroperitoneum|peritoneal\s+fat|spine|hip)",
    "retrieval_failed": r"unsuccessful|failed\s+retrieval|could\s+not\s+be\s+released|retrieval\s+aborted",
    "retrieval_complex": r"complex\s+retrieval|multiple\s+techniques|extremely\s+challenging",
    "recommend_against_retrieval": r"recommend(?:ation)?\s+against\s+retrieval",
    "complications": r"chronic\s+(?:back\s+)?pain|chronic\s+abdominal\s+pain|nerve\s+involvement|tachycardia|hypotension",
}


def extract_all_injuries(text: str) -> Dict[str, Any]:
    """Extract all injury signals from plaintiff text block.
    
    Performs comprehensive semantic scan for:
    - Mechanical failures (fracture, migration, embedment, tilt, occlusion, thrombosis)
    - Perforation grade (1-4) and penetration depth (mm)
    - Organ involvement (kidney, aorta, duodenum, vertebra, psoas, retroperitoneum)
    - Retrieval status (failed, complex, open surgery, not recommended)
    - Complications (pain, nerve involvement, vital organ impact)
    - Dangerous locations (abutting organs)
    
    Args:
        text: Full plaintiff text block from settlement statement
        
    Returns:
        Dictionary with keys:
        - fracture, migration, embedment, tilt, occlusion, thrombosis (bool)
        - perforation_grade (1-4 or None)
        - perforation (bool)
        - penetration_mm (int or None)
        - organs (list of str)
        - retrieval_failed, retrieval_complex, retrieval_open, recommend_against_retrieval (bool)
        - dangerous_locations (list)
        - complications (list)
    """
    injuries = {
        "fracture": False,
        "migration": False,
        "embedment": False,
        "tilt": False,
        "occlusion": False,
        "thrombosis": False,
        "death": False,
        "dangerous_locations": [],
        "perforation_grade": None,
        "perforation": False,
        "penetration_mm": None,
        "organs": [],
        "retrieval_failed": False,
        "retrieval_complex": False,
        "retrieval_open": False,
        "recommend_against_retrieval": False,
        "complications": [],
    }

    t = text.lower()

    # Extract boolean flags
    if re.search(PATTERNS["fracture"], t):
        injuries["fracture"] = True
    if re.search(PATTERNS["migration"], t):
        injuries["migration"] = True
    if re.search(PATTERNS["embedment"], t):
        injuries["embedment"] = True
    if re.search(PATTERNS["tilt"], t):
        injuries["tilt"] = True
    if re.search(PATTERNS["occlusion"], t):
        injuries["occlusion"] = True
    if re.search(PATTERNS["thrombosis"], t):
        injuries["thrombosis"] = True
    if re.search(PATTERNS["death"], t):
        injuries["death"] = True
    if re.search(PATTERNS["retrieval_failed"], t):
        injuries["retrieval_failed"] = True
    if re.search(PATTERNS["retrieval_complex"], t):
        injuries["retrieval_complex"] = True
    
    # Extract retrieval_open ONLY from damages section (after "following values represent")
    damages_idx = t.find("following values represent")
    if damages_idx >= 0:
        damages_section = t[damages_idx:damages_idx+1500]
        if re.search(PATTERNS["retrieval_open"], damages_section):
            injuries["retrieval_open"] = True
    
    if re.search(PATTERNS["recommend_against_retrieval"], t):
        injuries["recommend_against_retrieval"] = True

    # Extract perforation grade (max if multiple found)
    grade_matches = re.findall(PATTERNS["perforation_grade"], t)
    if grade_matches:
        injuries["perforation_grade"] = max(int(m) for m in grade_matches)
        injuries["perforation"] = True
    elif re.search(PATTERNS["perforation"], t):
        injuries["perforation"] = True

    # Extract penetration mm (max in valid range)
    mm_matches = re.findall(PATTERNS["penetration_mm"], t)
    if mm_matches:
        mm_list = [int(m) for m in mm_matches if 1 <= int(m) <= 50]
        if mm_list:
            injuries["penetration_mm"] = max(mm_list)

    # Extract organs (deduplicate, normalize)
    organ_matches = re.findall(PATTERNS["organs"], t, re.IGNORECASE)
    if organ_matches:
        # Normalize and deduplicate
        organs = set()
        for organ in organ_matches:
            organ_clean = organ.lower().strip()
            # Normalize right/left kidney to just "kidney"
            if organ_clean in ["right kidney", "left kidney"]:
                organs.add("kidney")
            else:
                organs.add(organ_clean)
        injuries["organs"] = sorted(list(organs))

    # Extract dangerous locations (more specific)
    if re.search(PATTERNS["dangerous_location"], t):
        injuries["dangerous_locations"].append("organ abutment")

    # Extract complications (only if clear signal)
    comp_matches = re.findall(PATTERNS["complications"], t)
    if comp_matches:
        injuries["complications"] = list(set(comp_matches))

    return injuries


def join_list_clean(items: List[str]) -> str:
    """Join list items with proper grammar (no comma before 'and' for 2 items).
    
    Examples:
        ["a"] -> "a"
        ["a", "b"] -> "a and b"
        ["a", "b", "c"] -> "a, b, and c"
    """
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return ", ".join(items[:-1]) + f", and {items[-1]}"


def build_summary(inj: Dict[str, Any], max_len: int = 250) -> str:
    """Build litigation-grade injury summary with value-based priority ordering.
    
    Uses severity AND value-priority ordering:
    1. DEATH (highest value signal)
    2. RETRIEVAL_OPEN (open surgical retrieval method)
    3. DEVICE FRACTURE (high value, permanent damage)
    4. Perforation grade + mechanical failures
    5. Penetration depth + organ involvement
    6. Retrieval complexity + dangerous locations
    7. Complications
    
    Args:
        inj: Dictionary from extract_all_injuries()
        max_len: Max character length (default 250)
        
    Returns:
        Narrative summary in expert-report style with value-based priority
    """
    parts = []

    # 1. HIGHEST VALUE: Death/fatality (if present, leads)
    if inj["death"]:
        parts.append("filter-related death")

    # 2. HIGH VALUE: Open surgical retrieval
    if inj["retrieval_open"]:
        parts.append("underwent open surgical retrieval")

    # 3. HIGH VALUE: Device fracture (permanent mechanical failure)
    if inj["fracture"]:
        parts.append("with fractured device")

    # 4. Perforation grade (clinical severity marker)
    if inj["perforation_grade"]:
        parts.append(f"Grade {inj['perforation_grade']} perforation")
    elif inj["perforation"] and not inj["retrieval_open"]:
        parts.append("perforation")

    # 5. Remaining mechanical failures (excluding fracture which was above)
    mech = []
    if inj["embedment"]:
        mech.append("embedded")
    if inj["tilt"]:
        mech.append("tilted")
    if inj["migration"]:
        mech.append("migrated")
    if inj["occlusion"]:
        mech.append("occluded")
    if inj["thrombosis"]:
        mech.append("thrombosed")

    if mech:
        parts.append("with " + join_list_clean(mech) + " device")

    # 6. Penetration depth + organs (anatomical involvement)
    organ_phrase = None

    if inj["organs"]:
        organs = sorted(inj["organs"])
        if len(organs) == 1:
            organ_phrase = f"into the {organs[0]}"
        elif len(organs) == 2:
            organ_phrase = f"into the {organs[0]} and {organs[1]}"
        else:
            organ_phrase = "into multiple structures (" + ", ".join(organs) + ")"

    if inj["penetration_mm"]:
        if organ_phrase:
            organ_phrase = f"with ~{inj['penetration_mm']} mm strut penetration " + organ_phrase
        else:
            organ_phrase = f"with ~{inj['penetration_mm']} mm strut penetration"

    if organ_phrase:
        parts.append(organ_phrase)

    # 7. Retrieval complexity and status
    retrieval_bits = []
    if inj["retrieval_complex"]:
        retrieval_bits.append("complex retrieval")
    if inj["retrieval_failed"]:
        retrieval_bits.append("retrieval attempt failed")
    if inj["recommend_against_retrieval"]:
        retrieval_bits.append("retrieval not recommended")

    if retrieval_bits:
        parts.append("; " + "; ".join(retrieval_bits))
    elif inj["embedment"] and not inj["death"]:
        # Default to irretrievable if mechanical failures but no successful retrieval (and not death)
        parts.append("; irretrievable")

    # 8. Dangerous locations (only if found)
    if inj["dangerous_locations"]:
        parts.append("in dangerous proximity to organ")

    # 9. Complications (lowest priority)
    if inj["complications"]:
        comp = ", ".join(inj["complications"])
        parts.append(f"with complications including {comp}")

    # Final assembly and cleanup
    summary = " ".join(parts)
    summary = summary.replace(" ,", ",")
    summary = summary.replace(", and", " and")
    summary = summary.replace(" ;", ";")
    summary = summary.rstrip(".")
    summary = re.sub(r"\s+", " ", summary).strip()

    return summary[:max_len]


# =========================================================================
# PDF EXTRACTION PIPELINE
# =========================================================================

def extract_text(pdf_path: Path) -> str:
    """Extract text from PDF using pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n\n".join(page.extract_text() for page in pdf.pages)
    return preprocess_text(text)


def preprocess_text(text: str) -> str:
    """Apply all text reconstruction layers in sequence."""
    text = rebuild_caption_lines(text)
    text = rebuild_case_numbers(text)
    text = rebuild_addresses(text)
    text = rebuild_medical_history(text)
    return text


def split_cases(text: str) -> List[str]:
    """Split document into per-case sections using anchor."""
    anchor = "This Document Relates to Plaintiff:"
    parts = text.split(anchor)
    return [anchor + p for p in parts[1:]]  # Skip header


def clean_name(name: str) -> str:
    """Clean plaintiff name by removing case numbers and normalizing."""
    name = re.sub(r'Case\s*[Nn]o\.?.*', '', name).strip()
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def extract_plaintiff(text: str) -> str:
    """Extract plaintiff name using multi-pattern matching with continuation lookahead."""
    # Pattern 1: "This Document Relates to Plaintiff: Name"
    m1 = re.search(r"This Document Relates to Plaintiff:\s*([^\n\r]+)", text, re.IGNORECASE)
    if m1:
        name = clean_name(m1.group(1))
        if name and len(name) > 2:
            return name

    # Pattern 2: "Plaintiff: Name"
    m2 = re.search(r"^Plaintiff:\s*([^\n\r]+)", text, re.MULTILINE | re.IGNORECASE)
    if m2:
        return clean_name(m2.group(1))

    # Pattern 3: Title-based (Mr., Ms., etc.)
    m3 = re.search(r"(Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
    if m3:
        return m3.group(2)

    # Pattern 4: "o/b/o" or "on behalf of"
    m4 = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:o/b/o|on behalf of)\s*,?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
    if m4:
        head = clean_name(m4.group(1))
        tail = m4.group(2)
        if tail and re.search(r"[A-Z][a-z]", tail):
            return clean_name(head + ' ' + tail)
        # Lookahead for continuation
        idx = m4.end()
        look = text[idx: idx+300]
        mcont = re.search(r"[\n\r\s,]*([A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)+)", look)
        if mcont:
            return clean_name(head + ' ' + mcont.group(1))

    # Fallback: first capitalized line
    for line in text.splitlines():
        s = line.strip()
        if not s or s.isupper():
            continue
        if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', s):
            return clean_name(s.split(',')[0].strip())

    return ""


def extract_case_number(text: str) -> str:
    """Extract case number using federal docket pattern."""
    m = re.search(r"(\d{1,2}:\d{2}-cv-\d{4,6})", text)
    return m.group(1) if m else ""


def detect_brand(text: str) -> str:
    """Detect Cook IVC filter brand."""
    if re.search(r'Celect', text, flags=re.IGNORECASE):
        return 'Cook Celect'
    if re.search(r'Gunther|Günther|Gunther Tulip', text, flags=re.IGNORECASE):
        return 'Cook Gunther Tulip'
    return ''


def extract_amounts(text: str) -> List[float]:
    """Extract all dollar amounts from text."""
    amts = re.findall(r"\$\s?[\d,]+(?:\.\d{2})?", text)
    nums = []
    for a in amts:
        s = a.replace('$', '').replace(',', '').strip()
        try:
            nums.append(float(s))
        except Exception:
            continue
    return nums


def process_pdf(path_in: Path) -> List[Dict[str, Any]]:
    """Main extraction pipeline: PDF -> cases -> fields -> rows."""
    text = extract_text(path_in)
    parts = split_cases(text)
    rows = []

    for p in parts:
        plaintiff = extract_plaintiff(p)
        case_no = extract_case_number(p)
        brand = detect_brand(p)
        amounts = extract_amounts(p)
        total = int(max(amounts)) if amounts else ''
        
        # SPINE v2: Comprehensive injury extraction
        injuries = extract_all_injuries(p)
        injury = build_summary(injuries)
        
        # Skip rows with no plaintiff name
        if plaintiff:
            rows.append({
                'Plaintiff Name': plaintiff,
                'Case Number': case_no,
                'Injury Summary': injury,
                'Product Brand': brand,
                'Total Demanded': total,
            })

    return rows


def write_csv(rows: List[Dict[str, Any]], outpath: Path):
    """Write rows to CSV with consistent quoting."""
    df = pd.DataFrame(rows)
    df.to_csv(outpath, quoting=csv.QUOTE_ALL, index=False)


def main():
    if len(sys.argv) < 3:
        print("Usage: python spine_parser.py <pdf_input> <csv_output>")
        sys.exit(1)

    pdf_in = Path(sys.argv[1])
    csv_out = Path(sys.argv[2])

    if not pdf_in.exists():
        print(f"Error: PDF not found: {pdf_in}")
        sys.exit(1)

    rows = process_pdf(pdf_in)
    write_csv(rows, csv_out)
    print(f"Wrote {len(rows)} rows to {csv_out}")


if __name__ == '__main__':
    main()
