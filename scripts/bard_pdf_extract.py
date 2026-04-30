#!/usr/bin/env python3
"""
Pure logic module for Bard settlement PDF extraction, renaming, and batch processing.

No UI, no side effects outside temp dirs passed in by the caller.

Dependencies:
    pdfplumber

Install:
    pip install pdfplumber
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path


def extract_fields_from_text(text: str) -> tuple[str | None, str | None, float | None, str | None]:
    """Parse extracted PDF text and return (claim_number, client_name, award_float, award_formatted).

    Returns None for any field that cannot be found.
    """
    # Claim Number: e.g. "Claim Number   CL-1327252"
    claim_match = re.search(r"Claim Number\s+([A-Z]{2}-\d+)", text)
    claim_number: str | None = claim_match.group(1).strip() if claim_match else None

    # Claimant name: e.g. "Claimant   James A. Nelson"
    name_match = re.search(r"Claimant\s+([A-Za-z .'-]+)", text)
    raw_name: str | None = name_match.group(1).strip() if name_match else None

    client_name: str | None = None
    if raw_name:
        parts = raw_name.split()
        if len(parts) >= 2:
            last = parts[-1]
            first_middle = " ".join(parts[:-1])
            client_name = f"{last}, {first_middle}"
        else:
            client_name = raw_name

    # Total Award: e.g. "Total Award   $50,231.25"
    award_match = re.search(r"Total Award\s+\$([\d,]+\.\d{2})", text)
    raw_award: str | None = award_match.group(1).strip() if award_match else None

    award_float: float | None = None
    award_formatted: str | None = None
    if raw_award:
        award_float = float(raw_award.replace(",", ""))
        award_formatted = f"${award_float:,.2f}"

    return claim_number, client_name, award_float, award_formatted


def extract_fields_from_pdf(path: Path) -> tuple[str | None, str | None, float | None, str | None]:
    """Open *path* with pdfplumber and extract settlement fields."""
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return extract_fields_from_text(full_text)


def build_new_pdf_name(client_name: str, claim_number: str, award_formatted: str) -> str:
    """Build the standardised output filename.

    Format: ``{client_name} - {claim_number} - {award_formatted}.pdf``
    Uses plain hyphens only (no en/em dashes).
    """
    return f"{client_name} - {claim_number} - {award_formatted}.pdf"


def unique_path(path: Path) -> Path:
    """Return *path* unchanged if it does not exist, otherwise append ``_1``, ``_2``, …"""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    idx = 1
    while True:
        candidate = parent / f"{stem}_{idx}{suffix}"
        if not candidate.exists():
            return candidate
        idx += 1


def process_pdf_file(src_path: Path, output_dir: Path) -> tuple[Path, dict]:
    """Extract fields from *src_path*, rename, copy to *output_dir*, and return metadata.

    Returns:
        (new_path, {claim_number, client_name, award_float, award_formatted})

    Raises:
        ValueError: if any required field cannot be extracted.
    """
    claim_number, client_name, award_float, award_formatted = extract_fields_from_pdf(src_path)

    missing = [
        name
        for name, val in (
            ("claim_number", claim_number),
            ("client_name", client_name),
            ("award_float", award_float),
            ("award_formatted", award_formatted),
        )
        if val is None
    ]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    new_name = build_new_pdf_name(client_name, claim_number, award_formatted)  # type: ignore[arg-type]
    new_path = unique_path(output_dir / new_name)
    shutil.copy2(src_path, new_path)

    return new_path, {
        "claim_number": claim_number,
        "client_name": client_name,
        "award_float": award_float,
        "award_formatted": award_formatted,
    }
