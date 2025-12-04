#!/usr/bin/env python3
"""
Simple workflow fixer:
- Remove literal code fences (```...)
- Normalize indentation inside simple `if [ -f ... ]; then` / `fi` blocks by ensuring inner lines are indented one level further than the `if` line.

This is conservative text processing (not a YAML parser).
"""
import sys
from pathlib import Path


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    out_lines = []
    in_if = False
    if_indent = ""
    changed = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        # remove code fences like ``` or ```github-actions-workflow
        if stripped.startswith("```"):
            changed = True
            i += 1
            continue

        # detect simple if ...; then
        import re

        m = re.match(r"^(?P<indent>\s*)(if \[\s*-f .*\]; then)\s*$", line)
        if m:
            in_if = True
            if_indent = m.group("indent")
            out_lines.append(line)
            i += 1
            # for subsequent lines until a line that is exactly fi (possibly indented) or until a blank line followed by next dedent,
            while i < len(lines):
                l = lines[i]
                # If this line is a closing fi, write it and break
                if re.match(r"^\s*fi\s*$", l) or re.match(r"^\s*else\s*$", l):
                    out_lines.append(l)
                    i += 1
                    # if it was fi, we're out of the block; if else, continue processing inside block
                    if re.match(r"^\s*fi\s*$", l):
                        in_if = False
                        break
                    else:
                        # else: continue, keep processing until fi
                        continue
                # If the line is empty, preserve empty line
                if l.strip() == "":
                    out_lines.append(l)
                    i += 1
                    continue
                # ensure the line is indented at least one additional level relative to if_indent
                # compute desired indent
                desired = if_indent + "  "
                if not l.startswith(desired):
                    new_l = desired + l.lstrip()
                    out_lines.append(new_l)
                    changed = True
                else:
                    out_lines.append(l)
                i += 1
            continue

        # fallback: copy line
        out_lines.append(line)
        i += 1

    new_text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_workflow.py <file1> [file2 ...]")
        sys.exit(2)
    total_changed = 0
    for p in sys.argv[1:]:
        path = Path(p)
        if not path.exists():
            print(f"Skipping missing: {p}", file=sys.stderr)
            continue
        try:
            r = fix_file(path)
            if r:
                print(f"Updated: {p}")
            else:
                print(f"No change: {p}")
            total_changed += r
        except Exception as e:
            print(f"Error processing {p}: {e}", file=sys.stderr)
    sys.exit(0 if total_changed == 0 else 0)
