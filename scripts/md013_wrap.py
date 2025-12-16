#!/usr/bin/env python3
"""Conservative MD013 wrapper: soft-wrap narrative paragraphs at a given width.

Usage: python3 scripts/md013_wrap.py --max 100 file1.md file2.md ...

Behavior:
- Soft-wraps plain paragraph text to the given width.
- Skips fenced code blocks, tables (lines containing '|'), YAML front matter, lines starting
  with list markers (-, *, +, >) and ASCII-art bullets (├, └, │).
- Respects a marker `<!-- md013:ignore -->` placed immediately before a paragraph to skip wrapping.
"""
import argparse
import sys
import textwrap
from pathlib import Path


def should_skip_line(line: str) -> bool:
    s = line.lstrip()
    if not s:
        return False
    if s.startswith(('#', '`', '    ', '\t')):
        return True
    if s[0] in ('-', '*', '+', '>', '├', '└', '│'):
        return True
    if '|' in line:
        return True
    return False


def process_text(text: str, width: int) -> str:
    lines = text.splitlines()
    out_lines = []
    in_fence = False
    in_mdignore = False
    table_block = False
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if not para_buf:
            return
        para = ' '.join(l.strip() for l in para_buf)
        wrapped = textwrap.fill(para, width=width, replace_whitespace=True,
                                break_long_words=False, break_on_hyphens=False)
        out_lines.extend(wrapped.splitlines())
        para_buf = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # fence toggle
        if stripped.startswith('```'):
            flush_para()
            in_fence = not in_fence
            out_lines.append(line)
            i += 1
            continue

        if in_fence:
            out_lines.append(line)
            i += 1
            continue

        # md013 ignore marker: skip next paragraph until blank line
        if stripped == '<!-- md013:ignore -->':
            flush_para()
            out_lines.append(line)
            in_mdignore = True
            i += 1
            # copy following lines until blank line
            while i < len(lines) and lines[i].strip() != '':
                out_lines.append(lines[i])
                i += 1
            # don't consume the blank line here; let loop handle it
            in_mdignore = False
            continue

        # tables detection: simple heuristic
        if '|' in line:
            flush_para()
            out_lines.append(line)
            i += 1
            continue

        # blank line: flush paragraph buffer
        if stripped == '':
            flush_para()
            out_lines.append('')
            i += 1
            continue

        # skip wrapping for list-like or special lines
        if should_skip_line(line):
            flush_para()
            out_lines.append(line)
            i += 1
            continue

        # accumulate paragraph lines
        para_buf.append(line)
        i += 1

    flush_para()
    # ensure single trailing newline
    return '\n'.join(out_lines).rstrip() + '\n'


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--max', type=int, default=100, help='soft wrap width')
    p.add_argument('files', nargs='+')
    args = p.parse_args(argv)

    for fp in args.files:
        path = Path(fp)
        if not path.exists():
            print(f"Skipping missing file: {fp}")
            continue
        text = path.read_text(encoding='utf-8')
        new = process_text(text, width=args.max)
        if new != text:
            path.write_text(new, encoding='utf-8')
            print(f"Wrapped: {fp}")
        else:
            print(f"No changes: {fp}")


if __name__ == '__main__':
    main(sys.argv[1:])
