#!/usr/bin/env python3
"""
Repo-wide replacer: change the brain emoji (FP) to a safer branded fallback.

Rules:
- For HTML/Markdown files (`.html`, `.htm`, `.md`, `.markdown`) replace with `<strong>FP</strong>`
- For all other text files replace with plain `FP`
- Skip binary and large asset folders and extensions (images, fonts, .ipynb, .git, virtualenvs)

This script makes a `.bak` backup of every file it modifies.
Run from the repository root. Use `--apply` (default) to write changes; use `--dry-run` to only list matches.
"""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(".").resolve()
EMOJI = "FP"

HTML_EXTS = {".html", ".htm", ".md", ".markdown"}
SKIP_DIRS = {".git", "node_modules", ".venv", ".venv3", "venv", "__pycache__", "dist", "build", ".docker"}
SKIP_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".db",
    ".bin",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".mp4",
    ".mp3",
    ".mov",
    ".exe",
    ".dll",
    ".so",
    ".pyc",
    ".ipynb",
}


def should_skip(path: Path):
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    if path.suffix.lower() in SKIP_EXTS:
        return True
    return False


def replacement_for(path: Path) -> str:
    if path.suffix.lower() in HTML_EXTS:
        return "<strong>FP</strong>"
    return "FP"


def is_text_file(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
            if b"\x00" in chunk:
                return False
    except Exception:
        return False
    return True


def process_file(path: Path, dry_run: bool) -> int:
    try:
        if not is_text_file(path):
            return 0
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    except Exception:
        return 0

    if EMOJI not in text:
        return 0

    repl = replacement_for(path)
    new_text = text.replace(EMOJI, repl)
    if new_text == text:
        return 0

    if dry_run:
        print(f"[DRY] Would change: {path}")
        return 1

    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    path.write_text(new_text, encoding="utf-8")
    print(f"Modified: {path}  (backup: {bak.name})")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Don't write files; just list candidates")
    ap.add_argument("--root", default=".", help="Root directory to process")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    total = 0
    matched = 0

    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if should_skip(p.relative_to(root)):
            continue
        total += 1
        try:
            changed = process_file(p, args.dry_run)
            matched += changed
        except Exception as e:
            print(f"Error processing {p}: {e}")

    print("\nSummary:")
    print(f"  Files scanned: {total}")
    print(f"  Files changed: {matched}")
    if args.dry_run:
        print("Run without `--dry-run` to apply changes (script creates .bak files).")


if __name__ == "__main__":
    main()
