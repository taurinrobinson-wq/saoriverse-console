"""General medical record ingester for CaseGrid."""
from __future__ import annotations

import io
import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Iterator

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
    # Full phrases
    re.compile(r"\bdate of service[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bdate of visit[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bdate of treatment[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bdate of injury[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bdate seen[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bencounter date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bvisit date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\btreatment date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bappointment date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bappt\.? date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\boffice visit[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bseen on[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bprocedure date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\breport date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bexam date[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bexam[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    # Common abbreviations (DOS, DOV, DOT, DOI, DX)
    re.compile(r"\bD\.?O\.?S\.?[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bD\.?O\.?V\.?[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bD\.?O\.?T\.?[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    re.compile(r"\bD\.?O\.?I\.?[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE),
    # Generic fallbacks
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

_MW_MEDICAL_API_KEY_ENV = "MW_MEDICAL_API_KEY"
_MW_DICTIONARY_API_KEY_ENV = "MW_DICTIONARY_API_KEY"
_MW_MEDICAL_API_KEY_ALIASES = (
    _MW_MEDICAL_API_KEY_ENV,
    "MERRIAM_WEBSTER_MEDICAL_API_KEY",
    "MERIAM_WEBSTER_MEDICAL_API_KEY",
)
_MW_DICTIONARY_API_KEY_ALIASES = (
    _MW_DICTIONARY_API_KEY_ENV,
    "MERRIAM_WEBSTER_DICTIONARY_API_KEY",
    "MERIAM_WEBSTER_DICTIONARY_API_KEY",
)
_MW_MEDICAL_BASE_URL = "https://www.dictionaryapi.com/api/v3/references/medical/json"
_MW_DICTIONARY_BASE_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
_API_EXPANSION_SEEDS = [
    "neck",
    "back",
    "shoulder",
    "head",
    "concussion",
    "dizziness",
    "headache",
    "hamstring",
    "knee",
]

_STOPWORD_TOKENS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}

_TERM_EXPANSION_CACHE: dict[tuple[str, str], set[str]] = {}

# Safety rails for very large or pathological PDFs.
_DEFAULT_MAX_PROCESS_PAGES = 400
_DEFAULT_MAX_PAGE_TEXT_CHARS = 25_000

_NEGATION_TERMS = {"denies", "no", "none", "negative", "not", "without", "absent"}
_NORMALIZED_INJURY_KEYWORDS = [
    "neck",
    "back",
    "shoulder",
    "head",
    "thigh",
    "hamstring",
    "dizziness",
    "headache",
    "bruising",
    "pain",
]


def _resolve_api_key(medical: bool) -> str:
    aliases = _MW_MEDICAL_API_KEY_ALIASES if medical else _MW_DICTIONARY_API_KEY_ALIASES
    for env_name in aliases:
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return ""


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
    negated_injury_terms: list[str]
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


def _truncate_page_text(text: str, max_chars_per_page: int | None) -> str:
    if max_chars_per_page is None or max_chars_per_page <= 0:
        return text
    return text[:max_chars_per_page]


def _extract_pages(
    file_bytes: bytes,
    *,
    max_pages: int | None = None,
    max_chars_per_page: int | None = None,
) -> list[str]:
    if PdfReader:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            pages: list[str] = []
            for page_index, page in enumerate(reader.pages, start=1):
                if max_pages is not None and max_pages > 0 and page_index > max_pages:
                    break
                text = page.extract_text() or ""
                pages.append(_truncate_page_text(text, max_chars_per_page))
            return pages
        except Exception:
            pass
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = []
                for page_index, page in enumerate(pdf.pages, start=1):
                    if max_pages is not None and max_pages > 0 and page_index > max_pages:
                        break
                    text = page.extract_text() or ""
                    pages.append(_truncate_page_text(text, max_chars_per_page))
                return pages
        except Exception:
            pass
    return []


def chunk_pdf(
    file_bytes: bytes,
    pages_per_chunk: int = 10,
    max_pages: int | None = None,
) -> Iterator[tuple[int, int, bytes]]:
    """Yield (start_page, end_page, chunk_bytes) for each PDF chunk.

    Streaming chunk generation avoids holding every chunk in memory at once.
    """
    if not PdfReader or not PdfWriter or pages_per_chunk <= 0:
        return

    reader = PdfReader(io.BytesIO(file_bytes))
    total_pages = len(reader.pages)
    if max_pages is not None and max_pages > 0:
        total_pages = min(total_pages, max_pages)

    for start in range(0, total_pages, pages_per_chunk):
        end = min(start + pages_per_chunk, total_pages)
        writer = PdfWriter()
        for page_index in range(start, end):
            writer.add_page(reader.pages[page_index])
        buffer = io.BytesIO()
        writer.write(buffer)
        yield start + 1, end, buffer.getvalue()


def _iter_page_texts(
    file_bytes: bytes,
    *,
    enable_chunking: bool,
    chunk_pages: int,
    chunk_threshold_pages: int,
    max_pages: int,
    max_chars_per_page: int,
) -> Iterator[tuple[int, str]]:
    """Yield (global_page_number, page_text) in processing order."""
    if max_pages <= 0:
        return

    if not enable_chunking or chunk_pages <= 0 or not PdfReader or not PdfWriter:
        pages = _extract_pages(
            file_bytes,
            max_pages=max_pages,
            max_chars_per_page=max_chars_per_page,
        )
        for page_index, text in enumerate(pages, start=1):
            yield page_index, text
        return

    try:
        total_pages = len(PdfReader(io.BytesIO(file_bytes)).pages)
        total_pages = min(total_pages, max_pages)
    except Exception:
        pages = _extract_pages(
            file_bytes,
            max_pages=max_pages,
            max_chars_per_page=max_chars_per_page,
        )
        for page_index, text in enumerate(pages, start=1):
            yield page_index, text
        return

    if total_pages < chunk_threshold_pages:
        pages = _extract_pages(
            file_bytes,
            max_pages=max_pages,
            max_chars_per_page=max_chars_per_page,
        )
        for page_index, text in enumerate(pages, start=1):
            yield page_index, text
        return

    for start_page, _end_page, chunk_bytes in chunk_pdf(
        file_bytes,
        pages_per_chunk=chunk_pages,
        max_pages=max_pages,
    ):
        pages = _extract_pages(
            chunk_bytes,
            max_chars_per_page=max_chars_per_page,
        )
        for offset, text in enumerate(pages):
            yield start_page + offset, text


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


def _normalize_term(raw: str) -> str:
    cleaned = raw.replace("*", " ").strip().lower()
    cleaned = re.sub(r"[^a-z0-9\-\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _extract_terms_from_dictionary_payload(payload: Any) -> set[str]:
    expanded: set[str] = set()
    if not isinstance(payload, list):
        return expanded

    for item in payload:
        if isinstance(item, str):
            normalized = _normalize_term(item)
            if normalized:
                expanded.add(normalized)
            continue

        if not isinstance(item, dict):
            continue

        meta = item.get("meta")
        if isinstance(meta, dict):
            stems = meta.get("stems")
            if isinstance(stems, list):
                for stem in stems:
                    if isinstance(stem, str):
                        normalized = _normalize_term(stem)
                        if normalized:
                            expanded.add(normalized)

        hwi = item.get("hwi")
        if isinstance(hwi, dict):
            headword = hwi.get("hw")
            if isinstance(headword, str):
                normalized = _normalize_term(headword)
                if normalized:
                    expanded.add(normalized)

    return expanded


def _lookup_mw_terms(term: str, *, medical: bool, force_refresh: bool = False) -> set[str]:
    normalized_term = _normalize_term(term)
    if not normalized_term:
        return set()

    cache_key = ("medical" if medical else "dictionary", normalized_term)
    cached = _TERM_EXPANSION_CACHE.get(cache_key)
    if cached is not None and not force_refresh:
        return set(cached)

    api_key = _resolve_api_key(medical)
    if not api_key:
        return set()

    base_url = _MW_MEDICAL_BASE_URL if medical else _MW_DICTIONARY_BASE_URL
    quoted_term = urllib.parse.quote(normalized_term)
    url = f"{base_url}/{quoted_term}?key={urllib.parse.quote(api_key)}"

    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return set()

    expanded = _extract_terms_from_dictionary_payload(payload)
    if normalized_term:
        expanded.add(normalized_term)

    _TERM_EXPANSION_CACHE[cache_key] = set(expanded)
    return expanded


def _expand_injury_terms_with_api(
    injury_terms: list[str], *, force_refresh: bool = False
) -> list[str]:
    seeds = set(_API_EXPANSION_SEEDS)
    seeds.update(_normalize_term(term) for term in injury_terms)
    seeds.discard("")

    expanded: set[str] = set(_normalize_term(term) for term in injury_terms)
    expanded.discard("")

    for term in sorted(seeds):
        medical_terms = _lookup_mw_terms(term, medical=True, force_refresh=force_refresh)
        if medical_terms:
            expanded.update(medical_terms)

    # Keep terms reasonably specific to reduce broad false positives in page text.
    base_terms = {_normalize_term(term) for term in injury_terms if _normalize_term(term)}
    medical_suffixes = (
        "algia",
        "cele",
        "emia",
        "itis",
        "oma",
        "opathy",
        "osis",
        "pathy",
        "spasm",
        "uria",
    )

    anchor_tokens: set[str] = set()
    for base_term in seeds:
        for token in base_term.split():
            if token and token not in _STOPWORD_TOKENS and len(token) >= 3:
                anchor_tokens.add(token)

    filtered: set[str] = set()
    for term in expanded:
        if not term or not re.search(r"[a-z]", term):
            continue
        words = term.split()
        if len(words) > 2:
            continue
        if any(word in _STOPWORD_TOKENS for word in words):
            continue
        if len(words) == 1 and term not in base_terms and not term.endswith(medical_suffixes):
            continue
        if anchor_tokens and not any(token in term for token in anchor_tokens):
            continue
        filtered.add(term)

    # Preserve all original user/default terms even if they fail strict filtering.
    filtered.update(_normalize_term(term) for term in injury_terms if _normalize_term(term))

    return sorted(filtered)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip() for part in parts if part and part.strip()]


def _keyword_pattern(term: str) -> re.Pattern[str]:
    return re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)


def _has_negation_within_window(sentence: str, match_start: int, window: int = 5) -> bool:
    prefix = sentence[:match_start].lower()
    tokens = re.findall(r"[a-z0-9']+", prefix)
    prior_tokens = tokens[-window:]
    return any(token in _NEGATION_TERMS for token in prior_tokens)


def _detect_injury_relevance(
    text: str, injury_terms: list[str]
) -> tuple[bool, list[str], list[str]]:
    matched_terms: set[str] = set()
    negated_terms: set[str] = set()
    sentences = _split_sentences(text)

    for sentence in sentences:
        for term in injury_terms:
            pattern = _keyword_pattern(term)
            for match in pattern.finditer(sentence):
                if _has_negation_within_window(sentence, match.start(), window=5):
                    negated_terms.add(term)
                    continue
                matched_terms.add(term)

    return bool(matched_terms), sorted(matched_terms), sorted(negated_terms)


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
    force_dictionary_refresh: bool = False,
    enable_chunking: bool = True,
    chunk_pages: int = 10,
    chunk_threshold_pages: int = 40,
    max_pages: int = _DEFAULT_MAX_PROCESS_PAGES,
    max_chars_per_page: int = _DEFAULT_MAX_PAGE_TEXT_CHARS,
) -> dict[str, Any]:
    active_injury_terms = list(_NORMALIZED_INJURY_KEYWORDS)
    encounters: list[Encounter] = []
    total_processed_pages = 0

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
    negated_injury_terms: list[str] = []

    def flush(end_page: int) -> None:
        nonlocal current_start, current_dos, current_type
        nonlocal current_facility, current_provider
        nonlocal body_parts, symptoms, diagnoses, impression_lines
        nonlocal medications, follow_up, injury_related, injury_reasons
        nonlocal negated_injury_terms

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
            negated_injury_terms=sorted(set(negated_injury_terms)),
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
        negated_injury_terms = []

    for idx, text in _iter_page_texts(
        file_bytes,
        enable_chunking=enable_chunking,
        chunk_pages=chunk_pages,
        chunk_threshold_pages=chunk_threshold_pages,
        max_pages=max_pages,
        max_chars_per_page=max_chars_per_page,
    ):
        total_processed_pages = idx
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

        page_injury, reasons, negated_terms = _detect_injury_relevance(text, active_injury_terms)
        if page_injury:
            injury_related = True
            injury_reasons.extend(reasons)
        if negated_terms:
            negated_injury_terms.extend(negated_terms)

    if total_processed_pages == 0:
        return {
            "patient_name": patient_name or "",
            "page_count": 0,
            "encounters": [],
            "page_limit_hit": False,
        }

    flush(total_processed_pages)

    return {
        "patient_name": patient_name or "",
        "page_count": total_processed_pages,
        "user_injury_terms": active_injury_terms,
        "page_limit_hit": total_processed_pages >= max_pages,
        "encounters": [_encounter_to_serializable(encounter) for encounter in encounters],
    }


def _encounter_to_serializable(encounter: Encounter) -> dict[str, Any]:
    payload = asdict(encounter)
    payload["dos"] = encounter.dos.isoformat() if encounter.dos else None
    return payload


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