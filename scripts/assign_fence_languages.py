#!/usr/bin/env python3
"""Assign languages to fenced code blocks without a language (heuristic).

Rules:
- Skip `node_modules`, `archive`, and large files.
- For fences with no language, inspect the first non-empty line inside the block
  and heuristically choose from: json, python, bash, javascript, xml, sql, text.
- Default to `text` when uncertain.
"""
import os
import re
from pathlib import Path


def guess_language(sample: str) -> str:
    s = sample.lstrip()
    low = s.lower()
    if not s:
        return "text"
    if s.startswith("{") or s.startswith("["):
        return "json"
    if low.startswith("<") and ("html" in low or low.startswith("<!doctype") or low.startswith("<svg") or "<?xml" in low):
        return "xml"
    if re.search(r"^\s*(def |class |import |from |async |await |print\(|self\.)", s):
        return "python"
    if s.startswith("$ ") or s.startswith("#!/") or re.search(r"\b(npm|yarn|pip|docker|curl|ssh|sudo|systemctl|apt|brew)\b", s):
        return "bash"
    if re.search(r"\b(console\.log|function |var |let |const )", s):
        return "javascript"
    if re.search(r"\bselect\b|\binsert\b|\bupdate\b|\bfrom\b", low):
        return "sql"
    return "text"


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    # Find fences that are opening fence with no language: ```\s*$
    pattern = re.compile(r"(^```+)(\s*)$", re.MULTILINE)
    changed = 0

    lines = text.splitlines(keepends=True)
    out_lines = []
    i = 0
    n = len(lines)
    while i < n:
        m = pattern.match(lines[i])
        if m:
            fence = m.group(1)
            out_lines.append(fence + "\n")
            # collect block lines
            j = i + 1
            # find first non-empty sample line inside block
            sample = ""
            while j < n and not lines[j].startswith(fence):
                if not sample and lines[j].strip():
                    sample = lines[j]
                out_lines.append(lines[j])
                j += 1
            # j now at closing fence or EOF
            if j < n and lines[j].startswith(fence):
                # We opened with ``` and closing is ``` — but we didn't write language.
                # Replace the opening fence we already wrote (last appended) with language-aware one.
                lang = guess_language(sample)
                # replace last appended (opening) with fence+lang
                out_lines[-( (j - i) + 1 )] = fence + lang + "\n"
                changed += 1
                # append closing fence
                out_lines.append(lines[j])
                i = j + 1
                continue
            else:
                # unterminated fence; leave as-is
                i = j
                continue
        else:
            out_lines.append(lines[i])
            i += 1

    if changed:
        path.write_text(''.join(out_lines), encoding="utf-8")
    return changed


def main():
    repo = Path('.')
    total_changed = 0
    files_scanned = 0
    for root, dirs, files in os.walk(repo):
        # skip large dirs
        if 'node_modules' in root or '/archive' in root or root.startswith('./archive') or 'backup_' in root:
            continue
        for fn in files:
            if not fn.endswith('.md'):
                continue
            path = Path(root) / fn
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                files_scanned += 1
                changed = process_file(path)
                total_changed += changed
            except Exception:
                continue

    print(f"Scanned {files_scanned} markdown files, updated {total_changed} fenced blocks (heuristic)")


if __name__ == '__main__':
    main()
