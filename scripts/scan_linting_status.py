#!/usr/bin/env python3
"""
Scan markdown files for remaining linting issues
"""
import re
from pathlib import Path
from collections import defaultdict


def check_md024(content: str) -> int:
    """Count duplicate headings (MD024)."""
    headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
    count_map = defaultdict(int)
    duplicates = 0
    for h in headings:
        count_map[h] += 1
        if count_map[h] > 1:
            duplicates += 1
    return duplicates


def check_md033(content: str) -> int:
    """Count HTML tags (MD033)."""
    html_tags = len(re.findall(r'<[^>]+>', content))
    return html_tags


def check_md003(content: str) -> int:
    """Count atx_closed headings (MD003) - # Heading #."""
    closed = len(re.findall(r'^#+\s+.+\s+#+\s*$', content, re.MULTILINE))
    return closed


def check_md013(content: str) -> int:
    """Count lines over 100 chars (MD013), excluding code blocks."""
    lines = content.split('\n')
    count = 0
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
        elif not in_code and len(line) > 100:
            count += 1
    return count


def check_md025(content: str) -> int:
    """Count multiple h1s in same file (MD025)."""
    h1_count = len(re.findall(r'^# [^#]', content, re.MULTILINE))
    return max(0, h1_count - 1)  # More than 1 is an issue


def scan_file(file_path: Path) -> dict:
    """Scan a file for linting issues."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'md003': check_md003(content),
            'md013': check_md013(content),
            'md024': check_md024(content),
            'md025': check_md025(content),
            'md033': check_md033(content),
        }
    except Exception:
        return {}


def main():
    # Exclude directories
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'archive', 'legacy'}
    
    root = Path('.')
    md_files = [p for p in root.rglob('*.md') 
                if not any(x in p.parts for x in exclude_dirs)]
    
    totals = defaultdict(int)
    problem_files = defaultdict(list)
    
    for md_file in md_files:
        issues = scan_file(md_file)
        if not issues:
            continue
            
        for rule, count in issues.items():
            totals[rule] += count
            if count > 0:
                problem_files[rule].append((str(md_file.relative_to('.')), count))
    
    print("=" * 70)
    print("MARKDOWN LINTING STATUS (after automated fixes)")
    print("=" * 70)
    
    print("\n📊 TOTALS BY RULE:")
    print("-" * 70)
    for rule in ['md003', 'md013', 'md024', 'md025', 'md033']:
        count = totals[rule]
        bar = "█" * min(count // 100, 50)
        print(f"  {rule.upper():8} {count:6d}  {bar}")
    
    print("\n🔴 TOP PROBLEM FILES (by rule):")
    print("-" * 70)
    
    for rule in sorted(problem_files.keys()):
        if problem_files[rule]:
            files = sorted(problem_files[rule], key=lambda x: x[1], reverse=True)[:5]
            print(f"\n  {rule.upper()}:")
            for filepath, count in files:
                print(f"    - {filepath:50} ({count})")
    
    print("\n" + "=" * 70)
    print(f"Total files scanned: {len(md_files)}")
    print(f"Files with issues: {len(set(f for files in problem_files.values() for f, _ in files))}")
    print("=" * 70)


if __name__ == '__main__':
    main()
