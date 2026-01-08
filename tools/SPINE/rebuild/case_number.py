"""Rebuild multi-line case numbers."""
import re


def rebuild_case_numbers(text: str) -> str:
    """Detect broken case numbers and merge with next line.
    
    Handles:
    - Case No: followed by number on next line
    - Case # followed by number on next line
    
    Args:
        text: Raw extracted PDF text
        
    Returns:
        Text with reconstructed case numbers
    """
    lines = text.split("\n")
    rebuilt = []
    skip_next = False

    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue

        line = lines[i].strip()

        if i < len(lines) - 1:
            next_line = lines[i + 1].strip()

            # If this line ends with "Case No" or "Case #" and next has a case number pattern
            if (
                re.search(r"Case\s*(?:No\.?|#)\s*[:]*\s*$", line, flags=re.IGNORECASE)
                and re.search(r"\d{1,2}:\d{2}-cv-\d{4,6}", next_line)
            ):
                merged = f"{line} {next_line}"
                rebuilt.append(merged)
                skip_next = True
                continue

        rebuilt.append(line)

    return "\n".join(rebuilt)
