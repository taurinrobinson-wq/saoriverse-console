#!/usr/bin/env python3
"""Batch markdown fixer - runs all fixes sequentially on all .md files"""

import subprocess
import sys
from pathlib import Path

def run_fixes():
    repo_root = Path('.')
    
    # Find all .md files (exclude archive, node_modules, etc.)
    exclude_dirs = {'archive', 'node_modules', 'firstperson', 'velinor-web', 'MessageUIOverlayPrototype', '.git'}
    
    md_files = [
        str(f) for f in repo_root.rglob('*.md')
        if not any(part in f.parts for part in exclude_dirs)
    ]
    
    print(f"Found {len(md_files)} markdown files to process\n")
    
    # Phase 1: Fix heading style (MD003)
    print("=" * 60)
    print("PHASE 1: Fixing MD003 (heading style - atx_closed to atx)")
    print("=" * 60)
    
    fixed = 0
    for f in md_files:
        result = subprocess.run([sys.executable, 'scripts/fix_heading_style.py', f], 
                              capture_output=True, text=True)
        if "Fixed:" in result.stdout:
            fixed += 1
    print(f"✓ Fixed {fixed} files with MD003 issues\n")
    
    # Phase 2: Fix blank lines around headings/code blocks (MD022, MD032, MD012)
    print("=" * 60)
    print("PHASE 2: Fixing MD022/032/012 (blank lines & spacing)")
    print("=" * 60)
    
    # Run markdown_fixer on all files at once
    result = subprocess.run([sys.executable, 'scripts/markdown_fixer.py'] + md_files,
                          capture_output=True, text=True)
    print(result.stdout if result.stdout else "✓ Processed all files")
    print()
    
    # Phase 3: Fix line length (MD013) - wrap to 100 chars
    print("=" * 60)
    print("PHASE 3: Fixing MD013 (line length - wrap to 100 chars)")
    print("=" * 60)
    
    wrapped = 0
    for f in md_files:
        result = subprocess.run([sys.executable, 'scripts/md013_wrap.py', '--max', '100', f],
                              capture_output=True, text=True)
        if "Wrapped" in result.stdout:
            wrapped += 1
    print(f"✓ Wrapped {wrapped} files to 100 char limit\n")
    
    print("=" * 60)
    print("ALL FIXES COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    run_fixes()
