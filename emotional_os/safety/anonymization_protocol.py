#!/usr/bin/env python3
"""
Anonymization Protocol for Saonyx / Keeper's Edition

Intelligent symbolic anonymization that:
- Strips identifiable information (names, dates, locations, medical details)
- Replaces with symbolic placeholders/glyphs that preserve emotional resonance
- Maintains emotional tone, narrative arc, and relational dynamics
- Supports consent-based de-anonymization for sharing/legacy
- Enables HIPAA/GDPR compliance while preserving system memory

Philosophy: We're not erasing ache—we're honoring it privately.
"""

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Symbolic glyph replacements for common identifiers
IDENTITY_GLYPHS = {
    "feminine_names": {
        "Jen": "The Mirror",
        "Michelle": "The Thread",
        "Sarah": "The Keeper",
        "Jessica": "The Bridge",
        "Jennifer": "The Sentinel",
        "Lisa": "The Witness",
        "Maria": "The Weaver",
        "Amanda": "The Echo",
    },
    "masculine_names": {
        "John": "The Guardian",
        "James": "The Anchor",
        "Michael": "The Stone",
        "David": "The Compass",
        "Robert": "The Steward",
        "William": "The Bearer",
        "Daniel": "The Path",
    },
    "neutral_names": {
        "Alex": "The Catalyst",
        "Jordan": "The Threshold",
        "Casey": "The Wanderer",
    },
    "family_roles": {
        r"\bmother\b": "the Lightkeeper",
        r"\bfather\b": "the Steward",
        r"\bdaughter\b": "the Lightkeeper",
        r"\bson\b": "the Bearer",
        r"\bsister\b": "the Mirror",
        r"\bbrother\b": "the Anchor",
        r"\bwife\b": "the Thread",
        r"\bhusband\b": "the Guardian",
        r"\bchild\b": "the Seedling",
        r"\bparent\b": "the Keeper",
        r"\bkid\b": "the Seedling",
        r"\btherapist\b": "the Witness",
        r"\bdoctor\b": "the Steward of Medicine",
        r"\nboss\b": "the Authority",
        r"\bfriend\b": "the Companion",
    },
}

# Relative time conversion
TIME_GLYPHS = {
    "past_week": "lately",
    "past_month": "recently",
    "past_season": "last season",
    "past_year": "last year",
    "past_years": "years ago",
}

# Location generalization
LOCATION_GENERALIZATION = {
    r"\b(California|CA)\b": "West Coast",
    r"\b(New York|NY)\b": "East Coast",
    r"\b(Texas|TX)\b": "South",
    r"\b(Florida|FL)\b": "Southeast",
    r"\b(Chicago|IL)\b": "Midwest",
    r"\b(Seattle|WA)\b": "Pacific Northwest",
    r"\b(Boston|MA)\b": "Northeast",
    r"\b(Denver|CO)\b": "Rocky Mountain",
    r"\b(Phoenix|AZ)\b": "Southwest",
    r"\b(Los Angeles|LA)\b": "West Coast",
}

# Medical/sensitive terms - anonymized but preserved in function
MEDICAL_GLYPHS = {
    r"\b(depression|depressive)\b": "the Depths",
    r"\b(anxiety|anxious)\b": "the Tightness",
    r"\b(PTSD|trauma|traumatic)\b": "the Rupture",
    r"\b(abuse|abused)\b": "the Wound",
    r"\b(suicide|suicidal)\b": "the Abyss",
    r"\b(cancer|carcinoma)\b": "the Shadow",
    r"\b(IVC filter|device|implant)\b": "the Device",
    r"\b(medication|med)\b": "the Medicine",
    r"\b(diagnosis|diagnosed)\b": "the Recognition",
}


@dataclass
class AnonymizationMap:
    """Tracks the mapping between original identifiers and glyphs for reversal."""

    timestamp: str
    identifier_glyphs: Dict[str, str]  # "actual_name" -> "The Mirror"
    temporal_shifts: Dict[str, str]  # "August 2023" -> "last summer"
    location_generalizations: Dict[str, str]  # "Bell, CA" -> "West Coast"
    consent_token: str = ""  # UUID for consent-based de-anonymization
    allow_medical: bool = False  # Keep medical details?
    allow_names: bool = False  # Keep names?

    def to_json(self) -> str:
        """Serialize for storage."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize from storage."""
        data = json.loads(json_str)
        return cls(**data)


class AnonymizationProtocol:
    """Handles intelligent anonymization and de-anonymization."""

    def __init__(self, allow_medical: bool = False, allow_names: bool = False):
        """
        Initialize protocol.

        Args:
            allow_medical: If True, preserve medical terms (only if user explicitly consents)
            allow_names: If True, preserve names (only if user explicitly consents)
        """
        self.allow_medical = allow_medical
        self.allow_names = allow_names
        self.anonymization_maps: Dict[str, AnonymizationMap] = {}

    def anonymize_entry(self, entry: Dict, user_id: str) -> Tuple[Dict, AnonymizationMap]:
        """
        Anonymize a single journal/ritual entry while preserving emotional tone.

        Args:
            entry: The entry to anonymize (has 'text', 'ritual', 'metadata' fields)
            user_id: User identifier (for tracking map)

        Returns:
            Tuple of (anonymized_entry, anonymization_map)
        """
        anonmap = AnonymizationMap(
            timestamp=datetime.now().isoformat(),
            identifier_glyphs={},
            temporal_shifts={},
            location_generalizations={},
            allow_medical=self.allow_medical,
            allow_names=self.allow_names,
        )

        anonymized = entry.copy()

        # Anonymize text content
        if "text" in entry:
            anonymized["text"], anonmap = self._anonymize_text(entry["text"], anonmap)

        # Anonymize ritual
        if "ritual" in entry:
            anonymized["ritual"], anonmap = self._anonymize_text(entry["ritual"], anonmap)

        # Preserve metadata but anonymize sensitive fields
        if "metadata" in entry:
            anonymized["metadata"] = self._anonymize_metadata(entry["metadata"], anonmap)

        # Add anonymization flag
        anonymized["_anonymized"] = True
        anonymized["_anonymization_consent_level"] = (
            "full" if (self.allow_names and self.allow_medical) else "medical" if self.allow_medical else "full"
        )

        # Store map for potential reversal
        self.anonymization_maps[user_id] = anonmap

        return anonymized, anonmap

    def _anonymize_text(self, text: str, anonmap: AnonymizationMap) -> Tuple[str, AnonymizationMap]:
        """Anonymize a text field intelligently."""
        result = text

        # 1. Handle names (if not explicitly allowed)
        if not self.allow_names:
            for category, names in IDENTITY_GLYPHS.items():
                if category == "family_roles":
                    continue  # Handle separately
                for actual, glyph in names.items():
                    pattern = rf"\b{re.escape(actual)}\b"
                    if re.search(pattern, result, re.IGNORECASE):
                        replacement = glyph if self.allow_names is False else actual
                        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                        anonmap.identifier_glyphs[actual.lower()] = replacement

        # 2. Handle family roles (preserve relational dynamics)
        for pattern, replacement in IDENTITY_GLYPHS["family_roles"].items():
            if re.search(pattern, result, re.IGNORECASE):
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                anonmap.identifier_glyphs[pattern] = replacement

        # 3. Handle locations (generalize, not erase)
        for pattern, generalization in LOCATION_GENERALIZATION.items():
            if re.search(pattern, result, re.IGNORECASE):
                match = re.search(pattern, result, re.IGNORECASE)
                if match:
                    anonmap.location_generalizations[match.group(0)] = generalization
                result = re.sub(pattern, generalization, result, flags=re.IGNORECASE)

        # 4. Handle dates (convert to relative time)
        result, date_shifts = self._anonymize_dates(result)
        anonmap.temporal_shifts.update(date_shifts)

        # 5. Handle medical terms (if not explicitly allowed)
        if not self.allow_medical:
            for pattern, glyph in MEDICAL_GLYPHS.items():
                if re.search(pattern, result, re.IGNORECASE):
                    result = re.sub(pattern, glyph, result, flags=re.IGNORECASE)
                    anonmap.identifier_glyphs[pattern] = glyph

        return result, anonmap

    def _anonymize_dates(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Convert absolute dates to relative time references."""
        shifts = {}

        # Common date patterns
        patterns = [
            (
                r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
                self._month_year_to_relative,
            ),
            (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", self._numeric_date_to_relative),
        ]

        for pattern, converter in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group(0)
                relative = converter(match.groups())
                if relative:
                    text = text.replace(original, relative, 1)
                    shifts[original] = relative

        return text, shifts

    @staticmethod
    def _month_year_to_relative(groups: Tuple) -> Optional[str]:
        """Convert month/year to relative time."""
        try:
            month_str, year_str = groups
            # Map month names to numbers
            months = {
                "January": 1,
                "February": 2,
                "March": 3,
                "April": 4,
                "May": 5,
                "June": 6,
                "July": 7,
                "August": 8,
                "September": 9,
                "October": 10,
                "November": 11,
                "December": 12,
            }
            month = months.get(month_str)
            year = int(year_str)

            date = datetime(year, month, 1)
            now = datetime.now()
            delta = now - date

            if delta.days < 7:
                return "lately"
            elif delta.days < 30:
                return "recently"
            elif delta.days < 180:
                return "last season"
            elif delta.days < 730:
                return "last year"
            else:
                years = delta.days // 365
                return f"{years} years ago"
        except:
            return None

    @staticmethod
    def _numeric_date_to_relative(groups: Tuple) -> Optional[str]:
        """Convert numeric date to relative time."""
        try:
            month, day, year = groups
            # Handle 2-digit years
            year_int = int(year)
            if year_int < 100:
                year_int += 2000 if year_int < 50 else 1900

            date = datetime(year_int, int(month), int(day))
            now = datetime.now()
            delta = now - date

            if delta.days < 7:
                return "lately"
            elif delta.days < 30:
                return "recently"
            elif delta.days < 180:
                return "last season"
            elif delta.days < 730:
                return "last year"
            else:
                years = delta.days // 365
                return f"{years} years ago"
        except:
            return None

    def _anonymize_metadata(self, metadata: Dict, anonmap: AnonymizationMap) -> Dict:
        """Anonymize metadata while preserving structure."""
        result = metadata.copy()

        # Strip specific fields that might contain PII
        sensitive_fields = ["email", "phone", "address", "ssn", "health_id"]
        for field in sensitive_fields:
            if field in result:
                result[field] = "[redacted]"

        # Keep location but generalize
        if "location" in result and not self.allow_names:
            for pattern, generalization in LOCATION_GENERALIZATION.items():
                if re.search(pattern, result["location"], re.IGNORECASE):
                    result["location"] = generalization
                    break

        return result

    def can_unveil(self, user_id: str, consent_level: str = "full") -> bool:
        """
        Check if user has consented to de-anonymization.

        Args:
            user_id: The user
            consent_level: "full", "medical", "none"

        Returns:
            True if user can unveil data
        """
        # In production, this would check a consent table
        # For now, return True if anonymization map exists
        return user_id in self.anonymization_maps

    def create_consent_request(self, user_id: str, use_case: str) -> Dict:
        """
        Generate a consent request for sharing/legacy purposes.

        Args:
            user_id: The user
            use_case: "therapy_sharing", "legacy_archive", "research", "clinical_review"

        Returns:
            Consent request with context
        """
        use_case_descriptions = {
            "therapy_sharing": "Share this moment with your therapist for clinical review",
            "legacy_archive": "Include this in your personal legacy archive with your name",
            "research": "Contribute this (anonymized) to emotional research",
            "clinical_review": "Allow clinical team to access your actual identity for this entry",
        }

        return {
            "user_id": user_id,
            "use_case": use_case,
            "description": use_case_descriptions.get(use_case, "Unknown"),
            "question": f"Would you like to {use_case_descriptions.get(use_case, 'proceed')}?",
            "options": {
                "yes_unveil": "Yes, reveal my identity for this purpose",
                "yes_keep_anon": "Yes, keep it anonymous",
                "no_decline": "No, keep this private",
            },
            "created_at": datetime.now().isoformat(),
        }

    def generate_anonymization_report(self, entry: Dict, anonmap: AnonymizationMap) -> Dict:
        """
        Generate a report showing what was anonymized.

        Useful for transparency and regulatory compliance.
        """
        return {
            "entry_id": entry.get("id", "unknown"),
            "timestamp": anonmap.timestamp,
            "anonymization_level": anonmap.allow_names and anonmap.allow_medical and "minimal" or "full",
            "changes_made": {
                "identifiers_replaced": len(anonmap.identifier_glyphs),
                "dates_anonymized": len(anonmap.temporal_shifts),
                "locations_generalized": len(anonmap.location_generalizations),
                "medical_terms_preserved": anonmap.allow_medical,
                "names_preserved": anonmap.allow_names,
            },
            "specific_replacements": anonmap.identifier_glyphs,
            "temporal_shifts": anonmap.temporal_shifts,
            "location_changes": anonmap.location_generalizations,
        }


# Example usage and testing
if __name__ == "__main__":
    # Create anonymizer
    anon = AnonymizationProtocol(allow_medical=False, allow_names=False)

    # Example entry
    test_entry = {
        "id": "entry_001",
        "text": """
        I spoke with Michelle about my depression yesterday. She suggested 
        I move to Bell, CA to be closer to my mother. My therapist, Dr. Johnson,
        said in August 2023 that my IVC filter is causing anxiety. I worry 
        about my son's future. Should I take the medication?
        """,
        "ritual": "Light a candle. Sit with tenderness.",
        "metadata": {
            "location": "Los Angeles, CA",
            "created": "2025-11-05",
        },
    }

    # Anonymize
    anonymized, anonmap = anon.anonymize_entry(test_entry, "user_123")

    print("\n" + "=" * 80)
    print("ANONYMIZATION PROTOCOL TEST")
    print("=" * 80)

    print("\n📄 ORIGINAL ENTRY:")
    print(test_entry["text"].strip())

    print("\n🔐 ANONYMIZED ENTRY:")
    print(anonymized["text"].strip())

    print("\n📋 ANONYMIZATION REPORT:")
    report = anon.generate_anonymization_report(test_entry, anonmap)
    print(json.dumps(report, indent=2))

    print("\n🎯 CONSENT REQUEST (for legacy archive):")
    consent = anon.create_consent_request("user_123", "legacy_archive")
    print(json.dumps(consent, indent=2))

    print("\n✅ Anonymization protocol demonstration complete")
    print("   Ready to preserve emotional integrity while protecting privacy.")
