"""
FilenameNormalizer — Draftshift Module

Automatically normalizes uploaded filenames to litigation-grade format:
YYMMDD – Slug

Local-only operation. No external API calls.
"""

from datetime import datetime
from typing import Optional, Dict, Tuple
import re
from difflib import SequenceMatcher
import string


class FilenameNormalizer:
    """
    Core normalizer for Draftshift documents.
    
    Converts arbitrary filenames into: YYMMDD – Slug
    """

    # Document type dictionary with common litigation documents
    DEFAULT_DOCUMENT_DICTIONARY = {
        "declaration of lead trial counsel": "DeclLeadCounsel",
        "declaration of lead counsel": "DeclLeadCounsel",
        "declaration of soo baik": "DeclSooBaik",
        "notice of removal": "NoticeRemoval",
        "notice of pendency": "NoticePendency",
        "notice of reassignment": "ReassignmentDJ",
        "magistrate assignment": "MagAssignmentDecline",
        "proof of service": "ProofService",
        "proof of electronic service": "ProofService",
        "joint report": "JointReport",
        "scheduling order": "SchedulingOrder",
        "order to show cause": "OrderShowCause",
        "motion to dismiss": "MotionDismiss",
        "motion for summary judgment": "MotionSJ",
        "motion for leave to amend": "MotLeaveAmend",
        "opposition": "Opposition",
        "reply": "Reply",
        "declaration": "Declaration",
        "affidavit": "Affidavit",
        "stipulation": "Stipulation",
        "settlement agreement": "SettlementAgreement",
        "complaint": "Complaint",
        "answer": "Answer",
        "demurrer": "Demurrer",
        "cross-complaint": "CrossComplaint",
        "subpoena": "Subpoena",
        "notice": "Notice",
        "order": "Order",
        "judgment": "Judgment",
    }

    # Stopwords for fallback slug generation
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "of", "to", "for",
        "by", "with", "from", "on", "at", "is", "was", "are", "be",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "should", "could", "may", "might", "must", "can"
    }

    def __init__(self, custom_dictionary: Optional[Dict[str, str]] = None):
        """
        Initialize the normalizer.
        
        Args:
            custom_dictionary: Optional custom document type mappings
        """
        self.dictionary = self.DEFAULT_DOCUMENT_DICTIONARY.copy()
        if custom_dictionary:
            self.dictionary.update(custom_dictionary)

    def normalize(
        self,
        filename_original: str,
        filetype: Optional[str] = None,
        metadata_created_at: Optional[datetime] = None,
        metadata_modified_at: Optional[datetime] = None,
        content_text: Optional[str] = None,
        user_provided_date: Optional[datetime] = None,
        user_provided_slug: Optional[str] = None,
        docket_event_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Normalize a filename to litigation-grade format.
        
        Args:
            filename_original: Original filename
            filetype: File extension/type
            metadata_created_at: File creation timestamp
            metadata_modified_at: File modification timestamp
            content_text: Optional extracted text from file
            user_provided_date: User-supplied date override
            user_provided_slug: User-supplied slug override
            docket_event_date: Associated docket entry date
            
        Returns:
            Dictionary with normalized filename and metadata
        """
        # Resolve date
        resolved_date, date_source = self._resolve_date(
            user_provided_date=user_provided_date,
            docket_event_date=docket_event_date,
            extracted_date=self._extract_date_from_content(content_text),
            created_at=metadata_created_at,
            modified_at=metadata_modified_at,
        )

        # Resolve slug
        if user_provided_slug:
            slug = user_provided_slug[:40]  # Enforce length limit even for user input
            slug_source = "user_provided"
            confidence = 1.0
        else:
            slug, confidence = self._generate_slug(
                filename_original, content_text
            )
            slug_source = "extracted" if confidence > 0.7 else "fallback"

        # Compose normalized filename
        yymmdd = resolved_date.strftime("%y%m%d")
        normalized_filename = f"{yymmdd} – {slug}"

        return {
            "normalized_filename": normalized_filename,
            "date_used": resolved_date.isoformat(),
            "slug_used": slug,
            "source_of_date": date_source,
            "slug_confidence": round(confidence, 2),
            "original_filename": filename_original,
        }

    # ========================================================================
    # DATE RESOLUTION
    # ========================================================================

    def _resolve_date(
        self,
        user_provided_date: Optional[datetime] = None,
        docket_event_date: Optional[datetime] = None,
        extracted_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ) -> Tuple[datetime, str]:
        """
        Resolve the document date with priority ordering.
        
        Priority:
        1. user_provided_date
        2. docket_event_date
        3. extracted_date
        4. created_at
        5. modified_at
        6. today()
        """
        if user_provided_date:
            return user_provided_date, "user_provided"
        if docket_event_date:
            return docket_event_date, "docket"
        if extracted_date:
            return extracted_date, "extracted"
        if created_at:
            return created_at, "metadata_created"
        if modified_at:
            return modified_at, "metadata_modified"
        return datetime.now(), "fallback_today"

    def _extract_date_from_content(self, content_text: Optional[str]) -> Optional[datetime]:
        """
        Extract date from document content using regex patterns.
        
        Supports: MM/DD/YYYY, YYYY-MM-DD, Month Day, Year formats
        """
        if not content_text:
            return None

        patterns = [
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",  # MM/DD/YYYY or MM-DD-YYYY
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",  # YYYY-MM-DD
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, content_text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        # Try numeric format
                        if groups[0].isdigit():
                            if len(groups[0]) == 4:  # YYYY-MM-DD
                                return datetime(
                                    int(groups[0]), int(groups[1]), int(groups[2])
                                )
                            else:  # MM/DD/YYYY
                                return datetime(
                                    int(groups[2]), int(groups[0]), int(groups[1])
                                )
                        else:  # Month Day, Year
                            month_map = {
                                "january": 1, "february": 2, "march": 3,
                                "april": 4, "may": 5, "june": 6,
                                "july": 7, "august": 8, "september": 9,
                                "october": 10, "november": 11, "december": 12
                            }
                            month = month_map.get(groups[0].lower())
                            if month:
                                return datetime(
                                    int(groups[2]), month, int(groups[1])
                                )
                except (ValueError, IndexError):
                    continue

        return None

    # ========================================================================
    # SLUG GENERATION
    # ========================================================================

    def _generate_slug(
        self, filename: str, content_text: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Generate a normalized slug for the document.
        
        Returns:
            Tuple of (slug, confidence_score)
        """
        # Try dictionary-based matching first (filename + content)
        slug, confidence = self._dictionary_match(filename, content_text)
        if confidence >= 0.65:  # Accept good content matches
            return slug, confidence

        # Fallback: build slug from remaining keywords
        slug = self._fallback_slug_builder(filename)
        return slug, 0.5

    def _dictionary_match(
        self, filename: str, content_text: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Match filename against document dictionary using fuzzy matching.
        """
        # Clean filename
        cleaned = self._clean_text(filename)

        best_match = None
        best_score = 0.0

        # Try matching against dictionary keys
        for doc_type, slug in self.dictionary.items():
            score = self._fuzzy_match(cleaned, doc_type)
            if score > best_score:
                best_score = score
                best_match = slug

        # If content available, also try matching content
        if content_text and best_score < 0.85:
            cleaned_content = self._clean_text(content_text[:500])
            for doc_type, slug in self.dictionary.items():
                score = self._fuzzy_match(cleaned_content, doc_type)
                if score > best_score:
                    best_score = score
                    best_match = slug

        return best_match or "Document", best_score

    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """
        Fuzzy match two strings using SequenceMatcher.
        
        Returns score 0.0-1.0
        """
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    def _fallback_slug_builder(self, filename: str) -> str:
        """
        Build slug from filename by extracting meaningful words.
        
        Process:
        1. Clean filename
        2. Extract words
        3. Remove stopwords
        4. Capitalize and concatenate
        """
        # Remove extension and clean
        name_only = re.sub(r'\.[^.]+$', '', filename)
        cleaned = self._clean_text(name_only)

        # Split into words
        words = cleaned.split()

        # Filter stopwords
        meaningful = [w for w in words if w.lower() not in self.STOPWORDS]

        if not meaningful:
            return "Document"

        # Capitalize and concatenate
        slug = "".join(word.capitalize() for word in meaningful)

        # Limit to 40 chars
        return slug[:40]

    def _clean_text(self, text: str) -> str:
        """
        Clean text for matching: lowercase, remove punctuation/symbols.
        """
        # Remove file extensions
        text = re.sub(r'\.[a-zA-Z0-9]+$', '', text)
        # Lowercase
        text = text.lower()
        # Replace punctuation with spaces
        text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
        # Collapse whitespace
        text = ' '.join(text.split())
        return text

    # ========================================================================
    # FILENAME COMPOSITION
    # ========================================================================

    def _compose_filename(self, yymmdd: str, slug: str) -> str:
        """
        Compose final normalized filename.
        
        Rules:
        - Format: YYMMDD – Slug
        - ASCII only
        - No trailing spaces
        - Max 60 chars
        """
        # Limit slug length before composition
        if len(slug) > 40:
            slug = slug[:40]

        filename = f"{yymmdd} – {slug}"

        # Ensure ASCII
        filename = filename.encode('ascii', errors='ignore').decode('ascii')

        # Strip trailing spaces
        filename = filename.rstrip()

        return filename

    def add_custom_documents(self, mappings: Dict[str, str]):
        """
        Add custom document type mappings.
        
        Args:
            mappings: Dict of document_type -> slug_name
        """
        self.dictionary.update(mappings)

    def register_jurisdiction(self, jurisdiction: str, mappings: Dict[str, str]):
        """
        Register jurisdiction-specific document mappings.
        
        Args:
            jurisdiction: Jurisdiction name (e.g., "federal", "california")
            mappings: Jurisdiction-specific mappings
        """
        prefixed = {f"[{jurisdiction}] {k}": v for k, v in mappings.items()}
        self.dictionary.update(prefixed)
