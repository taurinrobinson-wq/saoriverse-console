"""General medical record ingester for CaseGrid."""
from __future__ import annotations

import io
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

try:
    import pdfplumber  # type: ignore
except Exception:
    pdfplumber = None

try:
    from pypdf import PdfReader, PdfWriter  # type: ignore
except Exception:
    PdfReader = None
    PdfWriter = None


_DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b"),
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
]

_DOS_PATTERNS = [
    re.compile(r"\bdate of service[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bprocedure date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\breport date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bexam[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bservice[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
]

_DOC_TYPES = {
    "radiology": [
        "mri",
        "ct",
        "x-ray",
        "xray",
        "ultrasound",
        "us ",
        "radiology",
        "rima radiology",
        "renaissance imaging",
    ],
    "gastroenterology": ["egd", "colonoscopy", "gi "],
    "dermatology": ["dermatology", "epidermal inclusion cyst", "skin"],
    "optometry": ["optometry", "검안과", "dilation", "동공 확장"],
    "immunization": ["immunization", "vaccine", "influenza", "cvs/pharmacy"],
    "labs": ["cbc", "cmp", "labcorp", "quest", "laboratory"],
    "primary_care": ["clinic", "progress note", "follow up", "kheir 6th st clinic"],
    "admin": ["consent", "intake", "authorization", "fax transmission"],
}

_BODY_PART_TERMS = [
    "neck",
    "cervical",
    "thoracic",
    "lumbar",
    "back",
    "shoulder",
    "head",
    "brain",
    "thigh",
    "hamstring",
    "hip",
    "knee",
    "leg",
    "arm",
    "chest",
    "spine",
]

_DEFAULT_INJURY_TERMS = [
    "neck",
    "cervical",
    "thoracic",
    "lumbar",
    "back",
    "shoulder",
    "head",
    "concussion",
    "dizziness",
    "headache",
    "bruise",
    "bruising",
    "thigh",
    "hamstring",
    "left-sided",
    "left sided",
]

_MEDICATION_LINE = re.compile(
    r"([A-Za-z][A-Za-z0-9\- ]+)\s+(\d+ ?(?:mg|mcg|g|units|%))?\s*(PO|IV|IM|QD|BID|TID|QID|PRN)?",
    re.IGNORECASE,
)

_FOLLOW_UP_TERMS = ["follow up", "follow-up", "return visit", "repeat", "recheck"]


@dataclass
class Medication:
    name: str
    dose: str | None = None
    frequency: str | None = None
    purpose: str | None = None


@dataclass
class Encounter:
    dos: date | None
    page_start: int
    page_end: int
    document_type: str
    facility: str | None
    provider: str | None
    body_parts: list[str]
    symptoms: list[str]
    diagnoses: list[str]
    impression: str | None
    medications: list[Medication]
    follow_up: list[str]
    injury_related: bool
    injury_reasons: list[str]
    questions_for_client: list[str]


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
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                return [(page.extract_text() or "") for page in pdf.pages]
        except Exception:
            pass
    if PdfReader:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            return [(page.extract_text() or "") for page in reader.pages]
        except Exception:
            pass
    return []


def _detect_dos(text: str) -> date | None:
    for pattern in _DOS_PATTERNS:
        match = pattern.search(text)
        if match:
            parsed = _parse_date(match.group(1))
            if parsed:
                return parsed
    return None


def _classify_document(text: str) -> str:
    lower = text.lower()
    for doc_type, terms in _DOC_TYPES.items():
        if any(term in lower for term in terms):
            return doc_type
    return "unknown"


def _extract_body_parts(text: str) -> list[str]:
    lower = text.lower()
    return sorted({term for term in _BODY_PART_TERMS if term in lower})


def _extract_medications(text: str) -> list[Medication]:
    medications: list[Medication] = []
    for line in text.splitlines():
        match = _MEDICATION_LINE.search(line)
        if not match:
            continue
        medications.append(
            Medication(
                name=match.group(1).strip(),
                dose=(match.group(2) or "").strip() or None,
                frequency=(match.group(3) or "").strip() or None,
            )
        )
    return medications


def _extract_follow_up(text: str) -> list[str]:
    follow_up: list[str] = []
    for line in text.splitlines():
        if any(term in line.lower() for term in _FOLLOW_UP_TERMS):
            follow_up.append(line.strip())
    return follow_up


def _detect_injury_relevance(text: str, injury_terms: list[str]) -> tuple[bool, list[str]]:
    lower = text.lower()
    reasons = sorted({term for term in injury_terms if term in lower})
    return bool(reasons), reasons


def _generate_questions(encounter: Encounter) -> list[str]:
    questions: list[str] = []
    if any(term in encounter.body_parts for term in ["neck", "cervical"]):
        questions.append("Did you have any neck pain, numbness, or tingling before the incident")
    if any(term in encounter.body_parts for term in ["thoracic", "lumbar", "back"]):
        questions.append("Were you treated for back problems before this incident")
    if any(term in encounter.body_parts for term in ["head", "brain"]):
        questions.append("Have you experienced headaches, dizziness, or vision changes since the incident")
    if any(term in encounter.body_parts for term in ["thigh", "hamstring", "leg", "hip", "knee"]):
        questions.append("Do you have radiating pain, numbness, or weakness into the legs")
    if encounter.injury_related and not questions:
        questions.append("Did you have any prior injuries to these same body parts before the incident")
    return questions


def ingest_medical_record(
    file_bytes: bytes,
    patient_name: str | None = None,
    injury_terms: list[str] | None = None,
) -> dict[str, Any]:
    active_injury_terms = sorted(
        set(_DEFAULT_INJURY_TERMS + [term.lower() for term in (injury_terms or [])])
    )
    pages = _extract_pages(file_bytes)
    encounters: list[Encounter] = []

    if not pages:
        return {"patient_name": patient_name or "", "page_count": 0, "encounters": []}

    current_start = 1
    current_dos: date | None = None
    current_type = "unknown"
    current_facility: str | None = None
    current_provider: str | None = None
    body_parts: list[str] = []
    symptoms: list[str] = []
    diagnoses: list[str] = []
    impression_lines: list[str] = []
    medications: list[Medication] = []
    follow_up: list[str] = []
    injury_related = False
    injury_reasons: list[str] = []

    def flush(end_page: int) -> None:
        nonlocal current_start, current_dos, current_type
        nonlocal current_facility, current_provider
        nonlocal body_parts, symptoms, diagnoses, impression_lines
        nonlocal medications, follow_up, injury_related, injury_reasons

        if end_page < current_start:
            return

        encounter = Encounter(
            dos=current_dos,
            page_start=current_start,
            page_end=end_page,
            document_type=current_type,
            facility=current_facility,
            provider=current_provider,
            body_parts=sorted(set(body_parts)),
            symptoms=sorted(set(symptoms)),
            diagnoses=sorted(set(diagnoses)),
            impression="\n".join(impression_lines).strip() or None,
            medications=medications[:],
            follow_up=sorted(set(follow_up)),
            injury_related=injury_related,
            injury_reasons=sorted(set(injury_reasons)),
            questions_for_client=[],
        )
        encounter.questions_for_client = _generate_questions(encounter)
        encounters.append(encounter)

        current_start = end_page + 1
        current_dos = None
        current_type = "unknown"
        current_facility = None
        current_provider = None
        body_parts = []
        symptoms = []
        diagnoses = []
        impression_lines = []
        medications = []
        follow_up = []
        injury_related = False
        injury_reasons = []

    for idx, text in enumerate(pages, start=1):
        lower = text.lower()
        dos_here = _detect_dos(text)
        if dos_here and (current_dos is not None or idx > current_start):
            flush(idx - 1)
        if dos_here:
            current_dos = dos_here

        if current_type == "unknown":
            current_type = _classify_document(text)

        if "kheir 6th st clinic" in lower:
            current_facility = "KHEIR 6TH ST CLINIC"
        if "rima radiology" in lower:
            current_facility = "RIMA Radiology"
        if "renaissance imaging" in lower:
            current_facility = "Renaissance Imaging"
        if "california dermatology institute" in lower:
            current_facility = "California Dermatology Institute"

        signed_match = re.search(r"(Signed by,|Electronically Signed by:)\s*([A-Za-z .]+)", text)
        if signed_match:
            current_provider = signed_match.group(2).strip()

        body_parts.extend(_extract_body_parts(text))

        for line in text.splitlines():
            normalized = line.lower().strip()
            if normalized.startswith("clinical history") or normalized.startswith("history:"):
                symptoms.append(line.strip())
            if normalized.startswith("indication") or normalized.startswith("chief complaint"):
                symptoms.append(line.strip())
            if normalized.startswith("impression"):
                impression_lines.append(line.strip())
            if normalized.startswith("diagnosis") or normalized.startswith("final diagnosis"):
                diagnoses.append(line.strip())

        medications.extend(_extract_medications(text))
        follow_up.extend(_extract_follow_up(text))

        page_injury, reasons = _detect_injury_relevance(text, active_injury_terms)
        if page_injury:
            injury_related = True
            injury_reasons.extend(reasons)

    flush(len(pages))

    return {
        "patient_name": patient_name or "",
        "page_count": len(pages),
        "user_injury_terms": injury_terms or [],
        "encounters": [asdict(encounter) for encounter in encounters],
    }


def _coerce_encounter(encounter: Encounter | dict[str, Any]) -> tuple[date | None, int, int]:
    if isinstance(encounter, Encounter):
        return encounter.dos, encounter.page_start, encounter.page_end

    dos_value = encounter.get("dos")
    dos = _parse_date(dos_value) if isinstance(dos_value, str) else None
    return dos, int(encounter.get("page_start", 1)), int(encounter.get("page_end", 1))


def split_pdf_by_encounters(
    file_bytes: bytes,
    encounters: list[Encounter] | list[dict[str, Any]],
) -> dict[str, bytes]:
    if not PdfReader or not PdfWriter:
        return {}

    reader = PdfReader(io.BytesIO(file_bytes))
    outputs: dict[str, bytes] = {}
    for encounter in encounters:
        dos, start, end = _coerce_encounter(encounter)
        writer = PdfWriter()
        for page_index in range(start - 1, end):
            writer.add_page(reader.pages[page_index])

        label_date = dos.isoformat() if dos else "unknown"
        filename = f"encounter_{label_date}_p{start}-{end}.pdf"

        buffer = io.BytesIO()
        writer.write(buffer)
        outputs[filename] = buffer.getvalue()
    return outputs