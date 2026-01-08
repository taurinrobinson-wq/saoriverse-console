"""Rebuild multi-line medical histories and narrative text."""


def rebuild_medical_history(text: str) -> str:
    """Detect continuation lines in medical histories and merge.
    
    Handles:
    - Sentences broken across lines
    - Medical fact descriptions split mid-phrase
    
    Args:
        text: Raw extracted PDF text
        
    Returns:
        Text with reconstructed medical histories
    """
    lines = text.split("\n")
    rebuilt = []

    for line in lines:
        stripped = line.strip()
        
        # If we have a previous line and this line starts with lowercase,
        # it's a continuation of the previous narrative
        if (
            rebuilt
            and stripped
            and stripped[0].islower()
            and not stripped.startswith(("case", "confidential", "to the honorable", "magistrate"))
        ):
            rebuilt[-1] += " " + stripped
            continue
        
        rebuilt.append(stripped)

    return "\n".join(rebuilt)
