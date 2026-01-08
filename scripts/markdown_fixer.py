#!/usr/bin/env python3
"""Simple repo-wide Markdown fixer.

Fixes applied:
- Trim trailing spaces
- Convert setext headings (=== / --- underlines) to ATX headings
- Ensure one blank line before ATX headings
- Ensure blank lines surrounding fenced code blocks

Safe: does not guess fenced-code languages or wrap lines.
"""
import re
from pathlib import Path


def fix_content(text: str) -> str:
    original = text

    # Trim trailing spaces on each line
    lines = [l.rstrip() for l in text.splitlines()]

    # Convert setext underlines to ATX
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            if re.match(r"^=+\s*$", nxt):
                out_lines.append(f"# {line.strip()}")
                i += 2
                continue
            if re.match(r"^-+\s*$", nxt):
                out_lines.append(f"## {line.strip()}")
                i += 2
                continue
        out_lines.append(line)
        i += 1

    # Ensure blank line before ATX headings
    fixed = []
    for idx, l in enumerate(out_lines):
        if re.match(r"^#{1,6} \S", l):
            if fixed and fixed[-1].strip() != "":
                fixed.append("")
        fixed.append(l)

    # Ensure blank lines around fenced code blocks
    final = []
    in_block = False
    fence_re = re.compile(r"^```")
    for l in fixed:
        if fence_re.match(l):
            if not in_block:
                # opening fence: ensure previous line blank
                if final and final[-1].strip() != "":
                    final.append("")
                final.append(l)
                in_block = True
                continue
            else:
                # closing fence: append fence and ensure a blank line after
                final.append(l)
                final.append("")
                in_block = False
                continue
        final.append(l)

    # Ensure file ends with a single newline
    result = "\n".join(final).rstrip() + "\n"
    return result if result != original else original


def main():
    root = Path(".")
    md_files = list(root.rglob("*.md"))
    changed = 0
    for p in md_files:
        # skip files in .git and node_modules
        if ".git" in p.parts or "node_modules" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new = fix_content(text)
        if new != text:
            p.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Processed {len(md_files)} markdown files, modified {changed}.")


if __name__ == "__main__":
    main()
