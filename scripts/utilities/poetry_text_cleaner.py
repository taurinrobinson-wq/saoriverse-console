#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poetry Text Cleaner & Validator

Ensures extracted poetry text is:
- Clean (removes all artifacts and formatting issues)
- Complete (no fragmentation)
- Consistent (standardized formatting)
- Usable (ready for all processing modes)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PoetryTextCleaner:
    """Clean and validate poetry text for processing."""

    # Common Project Gutenberg artifacts
    GUTENBERG_MARKERS = [
        r"\*\*\* START OF THIS PROJECT GUTENBERG.*?\n",
        r"\*\*\* END OF THIS PROJECT GUTENBERG.*?\n",
        r"Gutenberg",
        r"Project Gutenberg",
        r"http[s]?://www\.gutenberg\.org",
        r"gutenberg@gutenberg\.org",
    ]

    # Common OCR/encoding artifacts
    OCR_ARTIFACTS = [
        (r"_+", " "),  # Multiple underscores to space
        (r"\[Page.*?\]", ""),  # Page markers
        (r"\[Illustration.*?\]", ""),  # Illustration markers
        (r"\[footnote.*?\]", ""),  # Footnote markers
        (r"\[.*?\]", ""),  # Generic bracket content
        (r"¯", "-"),  # Overline to dash
        (r"—", "-"),  # Em dash to dash
        (r"–", "-"),  # En dash to dash
        (r"…", "..."),  # Ellipsis character
        (r"[\"\"\"]", '"'),  # Smart quotes to regular
        (r"[\'\']", "'"),  # Smart apostrophes
    ]

    # Line-level cleanup
    EXTRA_WHITESPACE = [
        (r"[ \t]+", " "),  # Multiple spaces/tabs to one
        (r" +\n", "\n"),  # Trailing spaces
        (r"\n +", "\n"),  # Leading spaces after newline
    ]

    def __init__(self):
        """Initialize cleaner."""
        self.stats = {
            "total_chars_before": 0,
            "total_chars_after": 0,
            "artifacts_removed": 0,
            "empty_lines_removed": 0,
            "fragmented_lines_fixed": 0,
            "encoding_issues_fixed": 0,
        }

    def clean_text(self, text: str, verbose: bool = False) -> str:
        """
        Clean poetry text completely.

        Args:
            text: Raw poetry text
            verbose: Print detailed cleaning info

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        original_length = len(text)

        # Step 1: Decode common encoding issues
        text = self._fix_encoding(text)

        # Step 2: Remove Project Gutenberg markers
        text = self._remove_gutenberg_markers(text)

        # Step 3: Fix OCR artifacts
        text = self._fix_ocr_artifacts(text)

        # Step 4: Clean whitespace
        text = self._clean_whitespace(text)

        # Step 5: Fix fragmented lines
        text = self._fix_fragmented_lines(text)

        # Step 6: Remove excessive empty lines
        text = self._clean_empty_lines(text)

        # Step 7: Final validation
        text = self._validate_text(text)

        self.stats["total_chars_before"] = original_length
        self.stats["total_chars_after"] = len(text)

        if verbose:
            logger.info(
                f"Cleaning: {original_length} → {len(text)} chars ({100*(1-len(text)/original_length):.1f}% removed)"
            )

        return text.strip()

    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues."""
        # Replace common encoding problems
        replacements = {
            "\r\n": "\n",  # CRLF to LF
            "\r": "\n",  # CR to LF
            "\x00": "",  # Null bytes
            "\ufeff": "",  # BOM
        }

        for old, new in replacements.items():
            if old in text:
                count = text.count(old)
                text = text.replace(old, new)
                self.stats["encoding_issues_fixed"] += count

        return text

    def _remove_gutenberg_markers(self, text: str) -> str:
        """Remove Project Gutenberg metadata and markers."""
        for pattern in self.GUTENBERG_MARKERS:
            before = len(re.findall(pattern, text))
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
            if before > 0:
                self.stats["artifacts_removed"] += before

        return text

    def _fix_ocr_artifacts(self, text: str) -> str:
        """Fix OCR scanning artifacts."""
        for pattern, replacement in self.OCR_ARTIFACTS:
            matches = len(re.findall(pattern, text))
            text = re.sub(pattern, replacement, text)
            if matches > 0:
                self.stats["artifacts_removed"] += matches

        return text

    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace issues."""
        for pattern, replacement in self.EXTRA_WHITESPACE:
            text = re.sub(pattern, replacement, text)

        return text

    def _fix_fragmented_lines(self, text: str) -> str:
        """
        Fix lines that should be connected.

        Detects:
        - Hyphenation at line ends
        - Poetry continuations
        - Broken sentence fragments
        """
        lines = text.split("\n")
        fixed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                fixed_lines.append("")
                i += 1
                continue

            # Check for line-ending hyphenation
            if line.endswith("-") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line[0].isupper():
                    # Probably hyphenated word - join without hyphen
                    line = line[:-1] + next_line
                    self.stats["fragmented_lines_fixed"] += 1
                    i += 2
                    fixed_lines.append(line)
                    continue

            # Check for poetry that should stay on separate lines
            # (preserve line breaks for poetry formatting)
            fixed_lines.append(line)
            i += 1

        return "\n".join(fixed_lines)

    def _clean_empty_lines(self, text: str) -> str:
        """Remove excessive empty lines while preserving poetry formatting."""
        lines = text.split("\n")
        cleaned = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()

            # Keep max 1 consecutive empty line
            if is_empty:
                if not prev_empty:
                    cleaned.append("")
                    self.stats["empty_lines_removed"] += 1
                else:
                    self.stats["empty_lines_removed"] += 1
            else:
                cleaned.append(line)

            prev_empty = is_empty

        # Remove leading/trailing empty lines
        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()

        return "\n".join(cleaned)

    def _validate_text(self, text: str) -> str:
        """Final validation pass."""
        # Ensure minimum text length
        if len(text) < 100:
            logger.warning(f"Text too short after cleaning: {len(text)} chars")
            return ""

        # Check for common issues
        if text.count("\n") < 5:
            logger.warning("Very few lines - may be fragmented")

        # Remove any remaining control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

        return text

    def get_stats(self) -> Dict:
        """Get cleaning statistics."""
        return self.stats.copy()

    def validate_completeness(self, text: str, min_lines: int = 10, min_words: int = 100) -> Tuple[bool, str]:
        """
        Validate that text appears complete and not fragmented.

        Args:
            text: Cleaned text
            min_lines: Minimum expected lines
            min_words: Minimum expected words

        Returns:
            (is_valid, message)
        """
        lines = text.strip().split("\n")
        words = text.split()

        issues = []

        if len(lines) < min_lines:
            issues.append(f"Too few lines ({len(lines)} < {min_lines})")

        if len(words) < min_words:
            issues.append(f"Too few words ({len(words)} < {min_words})")

        # Check for suspicious patterns indicating fragmentation
        if text.count("\n") == 0:
            issues.append("No line breaks - may be single line")

        if text.count('"') % 2 != 0:
            issues.append("Unmatched quotes - possible fragmentation")

        if text.count("(") != text.count(")"):
            issues.append("Unmatched parentheses - possible fragmentation")

        if issues:
            return False, "; ".join(issues)

        return True, "Text appears complete"


class PoetryTextValidator:
    """Validate poetry text quality and completeness."""

    def __init__(self):
        """Initialize validator."""
        self.validation_results = []

    def validate_file(self, filepath: Path) -> Dict:
        """
        Validate a poetry text file.

        Args:
            filepath: Path to poetry file

        Returns:
            Validation results dict
        """
        results = {
            "file": filepath.name,
            "status": "unknown",
            "size_bytes": 0,
            "size_words": 0,
            "size_lines": 0,
            "checks": {},
            "issues": [],
        }

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            results["status"] = "error"
            results["issues"].append(f"Failed to read file: {e}")
            return results

        results["size_bytes"] = len(text)
        results["size_words"] = len(text.split())
        results["size_lines"] = len(text.split("\n"))

        # Check 1: Minimum size
        results["checks"]["minimum_size"] = {
            "pass": results["size_bytes"] > 5000,
            "details": f"{results['size_bytes']} bytes",
        }
        if not results["checks"]["minimum_size"]["pass"]:
            results["issues"].append("File too small (< 5000 bytes)")

        # Check 2: Line distribution
        avg_line_length = results["size_bytes"] / max(1, results["size_lines"])
        results["checks"]["line_length"] = {"pass": 20 < avg_line_length < 200, "avg_length": avg_line_length}
        if not results["checks"]["line_length"]["pass"]:
            results["issues"].append(f"Unusual average line length: {avg_line_length:.1f}")

        # Check 3: UTF-8 validity
        try:
            text.encode("utf-8")
            results["checks"]["utf8_valid"] = {"pass": True}
        except UnicodeError as e:
            results["checks"]["utf8_valid"] = {"pass": False, "error": str(e)}
            results["issues"].append("Invalid UTF-8 encoding")

        # Check 4: No excessive special characters
        special_count = len(re.findall(r"[^a-zA-Z0-9\s\n\t\'\"-.,;:!?()]", text))
        special_ratio = special_count / max(1, len(text))
        results["checks"]["special_chars"] = {
            "pass": special_ratio < 0.1,
            "count": special_count,
            "ratio": special_ratio,
        }
        if not results["checks"]["special_chars"]["pass"]:
            results["issues"].append(f"High special character ratio: {special_ratio:.2%}")

        # Check 5: No excessive fragmentation markers
        frag_markers = len(re.findall(r"\[.*?\]", text))
        results["checks"]["fragmentation"] = {"pass": frag_markers < 50, "marker_count": frag_markers}
        if not results["checks"]["fragmentation"]["pass"]:
            results["issues"].append(f"Many fragmentation markers: {frag_markers}")

        # Determine overall status
        if results["issues"]:
            results["status"] = "warning"
        else:
            results["status"] = "valid"

        self.validation_results.append(results)
        return results

    def validate_directory(self, dirpath: Path) -> List[Dict]:
        """Validate all files in directory."""
        results = []

        if not dirpath.exists():
            logger.error(f"Directory not found: {dirpath}")
            return results

        files = sorted(dirpath.glob("*.txt"))
        logger.info(f"Validating {len(files)} files in {dirpath}")

        for filepath in files:
            result = self.validate_file(filepath)
            results.append(result)

            status_emoji = "✓" if result["status"] == "valid" else "⚠" if result["status"] == "warning" else "✗"
            logger.info(f"{status_emoji} {result['file']}: {result['size_words']} words, {result['size_lines']} lines")

            if result["issues"]:
                for issue in result["issues"]:
                    logger.warning(f"  - {issue}")

        return results

    def get_summary(self) -> Dict:
        """Get validation summary."""
        total = len(self.validation_results)
        valid = sum(1 for r in self.validation_results if r["status"] == "valid")
        warnings = sum(1 for r in self.validation_results if r["status"] == "warning")
        errors = sum(1 for r in self.validation_results if r["status"] == "error")

        return {
            "total_files": total,
            "valid": valid,
            "warnings": warnings,
            "errors": errors,
            "total_words": sum(r.get("size_words", 0) for r in self.validation_results),
            "total_bytes": sum(r.get("size_bytes", 0) for r in self.validation_results),
        }


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Clean and validate poetry text")
    parser.add_argument("--file", type=str, help="File to clean")
    parser.add_argument("--dir", type=str, help="Directory to validate")
    parser.add_argument("--output", type=str, help="Output file for cleaned text")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't clean")

    args = parser.parse_args()

    cleaner = PoetryTextCleaner()
    validator = PoetryTextValidator()

    if args.validate_only:
        # Validation only mode
        if args.dir:
            results = validator.validate_directory(Path(args.dir))
            summary = validator.get_summary()

            print("\n" + "=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)
            print(f"Total files: {summary['total_files']}")
            print(f"Valid: {summary['valid']} ✓")
            print(f"Warnings: {summary['warnings']} ⚠")
            print(f"Errors: {summary['errors']} ✗")
            print(f"Total words: {summary['total_words']:,}")
            print(f"Total bytes: {summary['total_bytes']:,}")
            print("=" * 80)

        elif args.file:
            result = validator.validate_file(Path(args.file))
            print(json.dumps(result, indent=2))

    else:
        # Clean and validate mode
        if args.file:
            logger.info(f"Cleaning file: {args.file}")

            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()

            cleaned = cleaner.clean_text(text, verbose=True)
            stats = cleaner.get_stats()

            logger.info("\nCleaning statistics:")
            logger.info(f"  Artifacts removed: {stats['artifacts_removed']}")
            logger.info(f"  Empty lines removed: {stats['empty_lines_removed']}")
            logger.info(f"  Fragmented lines fixed: {stats['fragmented_lines_fixed']}")
            logger.info(f"  Encoding issues fixed: {stats['encoding_issues_fixed']}")

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                logger.info(f"Cleaned text saved to: {args.output}")
            else:
                print(cleaned)

        elif args.dir:
            logger.info(f"Cleaning directory: {args.dir}")
            dirpath = Path(args.dir)

            for filepath in sorted(dirpath.glob("*.txt")):
                logger.info(f"\nCleaning {filepath.name}...")

                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

                cleaned = cleaner.clean_text(text)
                stats = cleaner.get_stats()

                # Save cleaned version
                output_path = filepath.parent / f"{filepath.stem}_cleaned.txt"
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(cleaned)

                logger.info(f"  ✓ Saved to: {output_path.name}")
                logger.info(f"  Stats: {stats['total_chars_before']} → {stats['total_chars_after']} chars")


if __name__ == "__main__":
    import json

    main()
