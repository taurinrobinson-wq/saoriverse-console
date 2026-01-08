"""Rebuild multi-line plaintiff names (o/b/o, estate, deceased, etc.)"""
import re


def rebuild_caption_lines(text: str) -> str:
    """Detect incomplete name lines and merge with continuation lines.
    
    Handles:
    - o/b/o / on behalf of
    - estate cases
    - minors represented by parents
    - hyphenated surnames
    - 'Deceased' on the next line
    - multi-line captions
    
    Args:
        text: Raw extracted PDF text
        
    Returns:
        Text with reconstructed plaintiff names
    """
    lines = text.split("\n")
    rebuilt = []
    skip_next = False

    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue

        line = lines[i].strip()

        # If this is the last line, just add it
        if i == len(lines) - 1:
            rebuilt.append(line)
            continue

        next_line = lines[i + 1].strip()

        # Conditions that indicate the current line is incomplete:
        # - ends with comma (especially "o/b/o," or a first name like "Heron,")
        # - contains "o/b/o" or "on behalf of" (and is not a complete phrase)
        # - ends with a short capitalized word (likely a first name)
        ends_with_comma = line.endswith(",")
        has_obfo = "o/b/o" in line.lower() or "on behalf of" in line.lower()
        last_word = line.split()[-1] if line.split() else ""
        ends_short_cap = (
            last_word.istitle() 
            and len(last_word) < 12
            and not last_word.lower() in ('plaintiff', 'defendant', 'deceased', 'case')
            and ':' not in last_word  # exclude words with colons like "Plaintiff:"
        )
        
        incomplete = ends_with_comma or has_obfo or ends_short_cap

        # Conditions that indicate the next line continues the name:
        # - starts with capital letter
        # - not a document header
        continuation = (
            next_line
            and next_line[0].isupper()
            and not next_line.lower().startswith("case no")
            and not next_line.lower().startswith("confidential")
            and not next_line.lower().startswith("to the honorable")
            and not next_line.lower().startswith("magistrate")
        )

        if incomplete and continuation:
            merged = f"{line} {next_line}"
            merged = re.sub(r"\s+", " ", merged)
            rebuilt.append(merged)
            skip_next = True
        else:
            rebuilt.append(line)

    return "\n".join(rebuilt)
