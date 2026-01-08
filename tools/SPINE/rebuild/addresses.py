"""Rebuild multi-line addresses."""
import re


def rebuild_addresses(text: str) -> str:
    """Detect broken addresses and merge with next line.
    
    Handles:
    - Street addresses broken across lines
    - City/State pairs on separate lines
    
    Args:
        text: Raw extracted PDF text
        
    Returns:
        Text with reconstructed addresses
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

            # If this line ends with comma and next line looks like a city/state or address continuation
            if (
                line.endswith(",")
                and re.search(r"[A-Za-z]+,\s?[A-Za-z]+", next_line)
            ):
                merged = f"{line} {next_line}"
                rebuilt.append(merged)
                skip_next = True
                continue

        rebuilt.append(line)

    return "\n".join(rebuilt)
