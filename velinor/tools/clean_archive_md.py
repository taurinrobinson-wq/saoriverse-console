#!/usr/bin/env python3
"""Clean FULL extracted archive into a curated markdown:
- Remove null bytes and control characters
- Collapse multiple blank lines
- Heuristically convert lines ending with ':' or in Title Case to headings
- Preserve paragraphs
"""
import re
from pathlib import Path

inp = Path("velinor/markdowngameinstructions/20251216_extracted.txt")
out = Path("velinor/markdowngameinstructions/20251216_Game_Dev_Archive.md")

def is_title_line(s: str) -> bool:
    s_stripped = s.strip()
    if not s_stripped:
        return False
    # headings often end with ':' or are short and capitalized words
    if s_stripped.endswith(":"):
        return True
    # All caps (allow punctuation)
    alpha = re.sub(r"[^A-Za-z ]+", "", s_stripped)
    if alpha and alpha.strip() and alpha.strip().upper() == alpha.strip() and len(alpha.strip()) <= 60 and len(alpha.strip())>0:
        return True
    # Title case heuristic: contains at least two words and many capitalized words
    words = s_stripped.split()
    if len(words) <= 6 and sum(1 for w in words if w and w[0].isupper()) >= max(1, len(words)//2):
        return True
    return False


def clean_text(raw: str) -> str:
    # remove nulls and weird control chars, normalize spaces
    text = raw.replace('\x00', '')
    # replace replacement characters often from docx extraction
    text = text.replace('\ufffd', '')
    # collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)
    # normalize CRLF to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # split into lines and process
    lines = text.split('\n')
    out_lines = []
    prev_blank = False
    for i, line in enumerate(lines):
        line = line.rstrip()  # keep leading spaces trimmed later
        # strip stray non-printables
        line = ''.join(ch for ch in line if ord(ch) >= 32 or ch=='\t')
        if not line.strip():
            if not prev_blank:
                out_lines.append('')
            prev_blank = True
            continue
        prev_blank = False
        # Heuristic heading detection
        if is_title_line(line):
            # choose level by content: long (<=30 chars) -> H2, else H3
            lvl = '##' if len(line.strip())<=60 else '###'
            heading = line.strip().rstrip(':')
            out_lines.append(f"{lvl} {heading}")
            continue
        out_lines.append(line)
    # join and collapse more than 2 blank lines
    cleaned = '\n'.join(out_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # ensure file ends with newline
    if not cleaned.endswith('\n'):
        cleaned += '\n'
    return cleaned


def main():
    raw = inp.read_text(encoding='utf-8', errors='replace')
    cleaned = clean_text(raw)
    out.write_text(cleaned, encoding='utf-8')
    print(f"Wrote cleaned markdown to {out} ({len(cleaned.splitlines())} lines)")

if __name__ == '__main__':
    main()
