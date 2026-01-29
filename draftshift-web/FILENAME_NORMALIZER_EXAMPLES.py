"""
FilenameNormalizer Usage Examples

Quick start guide for integrating FilenameNormalizer into Draftshift
"""

from datetime import datetime
from filename_normalizer import FilenameNormalizer


# ============================================================================
# BASIC USAGE
# ============================================================================

# Initialize the normalizer
normalizer = FilenameNormalizer()

# Simple normalization
result = normalizer.normalize(
    filename_original="Declaration of Lead Trial Counsel.docx",
    user_provided_date=datetime(2026, 1, 28)
)

print(result)
# Output:
# {
#     "normalized_filename": "260128 – DeclLeadCounsel",
#     "date_used": "2026-01-28T00:00:00",
#     "slug_used": "DeclLeadCounsel",
#     "source_of_date": "user_provided",
#     "slug_confidence": 0.95,
#     "original_filename": "Declaration of Lead Trial Counsel.docx"
# }


# ============================================================================
# WITH AUTOMATIC DATE EXTRACTION
# ============================================================================

content = """
DECLARATION OF LEAD TRIAL COUNSEL

I, John Smith, declare as follows under penalty of perjury
that the following is true:

1. The events described herein occurred on January 28, 2026.
"""

result = normalizer.normalize(
    filename_original="declaration.pdf",
    content_text=content
)

print(result["normalized_filename"])
# Output: "260128 – DeclLeadCounsel"
# (date extracted from content, slug extracted from header)


# ============================================================================
# WITH DOCKET INTEGRATION
# ============================================================================

result = normalizer.normalize(
    filename_original="motion.pdf",
    docket_event_date=datetime(2026, 1, 21),
    user_provided_slug="MotionDismiss"
)

print(result["normalized_filename"])
# Output: "260121 – MotionDismiss"
# (docket date used, user slug respected)


# ============================================================================
# CUSTOM DOCUMENT DICTIONARIES
# ============================================================================

# Add custom documents
normalizer.add_custom_documents({
    "motion for protective order": "MotProtective",
    "motion for sanctions": "MotSanctions",
    "request for judicial notice": "RJN"
})

result = normalizer.normalize(
    filename_original="Motion for Sanctions.pdf",
    user_provided_date=datetime(2026, 1, 25)
)

print(result["normalized_filename"])
# Output: "260125 – MotSanctions"


# ============================================================================
# JURISDICTION-SPECIFIC MAPPINGS
# ============================================================================

# Register federal court documents
normalizer.register_jurisdiction(
    "federal",
    {
        "notice of intent to sue": "FedNoticeIntent",
        "certificate of appealability": "FedCertApp"
    }
)

# Register California-specific documents
normalizer.register_jurisdiction(
    "california",
    {
        "notice of motion and declaration": "NoMoDec",
        "request for continuance": "ReqCont"
    }
)

result = normalizer.normalize(
    filename_original="[california] Request for Continuance.pdf",
    user_provided_date=datetime(2026, 1, 30)
)

print(result["normalized_filename"])
# Output will use California-specific slug if matched


# ============================================================================
# ERROR HANDLING & FALLBACKS
# ============================================================================

# Unknown document type - uses fallback
result = normalizer.normalize(
    filename_original="xyz_random_document_12345.pdf",
    user_provided_date=datetime(2026, 1, 28)
)

print(result)
# slug_used: "Document" (fallback)
# slug_confidence: 0.5 (low confidence)


# Missing date - uses today
result = normalizer.normalize(
    filename_original="Proof of Service.pdf"
)

print(result["source_of_date"])
# Output: "fallback_today"


# ============================================================================
# INTEGRATION PATTERN
# ============================================================================

def upload_document_to_case(
    file_object,
    case_id: str,
    docket_event_date: datetime = None,
    user_provided_metadata: dict = None
):
    """
    Pattern for integrating FilenameNormalizer into upload workflow
    """
    normalizer = FilenameNormalizer()
    
    # Extract metadata
    original_filename = file_object.filename
    content_text = file_object.text  # if available from OCR
    created_at = file_object.metadata.created
    
    # Get user overrides if provided
    user_date = None
    user_slug = None
    if user_provided_metadata:
        user_date = user_provided_metadata.get("date")
        user_slug = user_provided_metadata.get("slug")
    
    # Normalize
    result = normalizer.normalize(
        filename_original=original_filename,
        content_text=content_text,
        metadata_created_at=created_at,
        docket_event_date=docket_event_date,
        user_provided_date=user_date,
        user_provided_slug=user_slug
    )
    
    # Store with normalized name
    normalized_filename = result["normalized_filename"]
    
    # Save file with normalized name in case docket
    # (pseudo-code)
    store_file(
        case_id=case_id,
        filename=normalized_filename,
        content=file_object.content,
        metadata=result  # Store result for auditing
    )
    
    return result


# ============================================================================
# BATCH PROCESSING
# ============================================================================

files_to_process = [
    ("Declaration of Soo Baik.pdf", datetime(2026, 1, 28)),
    ("Notice of Removal.pdf", datetime(2026, 1, 16)),
    ("Proof of Service.pdf", datetime(2026, 1, 21)),
]

normalizer = FilenameNormalizer()

for filename, date in files_to_process:
    result = normalizer.normalize(
        filename_original=filename,
        user_provided_date=date
    )
    print(f"{filename} → {result['normalized_filename']}")

# Output:
# Declaration of Soo Baik.pdf → 260128 – DeclSooBaik
# Notice of Removal.pdf → 260116 – NoticeRemoval
# Proof of Service.pdf → 260121 – ProofService
