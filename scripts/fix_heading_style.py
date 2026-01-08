#!/usr/bin/env python3
"""
Fix MD003: Convert atx_closed headings (# Heading #) to atx format (# Heading)
"""
import sys
import re
from pathlib import Path

def fix_heading_style(file_path):
    """Convert atx_closed headings to atx format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern: # Heading # or ## Heading ## etc.
    # Match 1-6 hashes, then content, then same number of hashes at end
    content = re.sub(
        r'^(#{1,6})\s+(.+?)\s+\1\s*$',
        r'\1 \2',
        content,
        flags=re.MULTILINE
    )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fix_heading_style.py <file1> [file2] ...")
        sys.exit(1)
    
    for file_arg in sys.argv[1:]:
        path = Path(file_arg)
        if path.exists() and path.suffix == '.md':
            if fix_heading_style(path):
                print(f"Fixed: {path}")
            else:
                print(f"No changes: {path}")
        else:
            print(f"Skipped: {path}")
