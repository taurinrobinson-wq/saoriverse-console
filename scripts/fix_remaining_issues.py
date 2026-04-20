#!/usr/bin/env python3
"""
Fix MD025: Multiple h1 headings - convert extras to h2
Fix MD033: HTML tags - convert to markdown
Fix MD024: Duplicate headings - append context/number
"""
import re
from pathlib import Path
from collections import defaultdict


def fix_md025_multiple_h1(content: str) -> str:
    """Convert extra h1s to h2s (keep only first h1)."""
    lines = content.split('\n')
    h1_found = False
    fixed_lines = []
    
    for line in lines:
        if re.match(r'^# [^#]', line):
            if h1_found:
                # Convert this h1 to h2
                line = '#' + line
            else:
                h1_found = True
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_md033_html_tags(content: str) -> str:
    """Convert HTML tags to markdown equivalents."""
    # <br>, <br/>, <br />  → blank line
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
    
    # <b>text</b> → **text**
    content = re.sub(r'<b>([^<]*)</b>', r'**\1**', content, flags=re.IGNORECASE)
    
    # <i>text</i> → *text*
    content = re.sub(r'<i>([^<]*)</i>', r'*\1*', content, flags=re.IGNORECASE)
    
    # <strong>text</strong> → **text**
    content = re.sub(r'<strong>([^<]*)</strong>', r'**\1**', content, flags=re.IGNORECASE)
    
    # <em>text</em> → *text*
    content = re.sub(r'<em>([^<]*)</em>', r'*\1*', content, flags=re.IGNORECASE)
    
    # <u>text</u> → text (just remove underline)
    content = re.sub(r'<u>([^<]*)</u>', r'\1', content, flags=re.IGNORECASE)
    
    # <code>text</code> → `text`
    content = re.sub(r'<code>([^<]*)</code>', r'`\1`', content, flags=re.IGNORECASE)
    
    # <pre>...</pre> → ``` code block
    content = re.sub(r'<pre>([^<]*)</pre>', r'```\n\1\n```', content, flags=re.IGNORECASE)
    
    # <hr>, <hr/>, <hr /> → ---
    content = re.sub(r'<hr\s*/?>', '\n---\n', content, flags=re.IGNORECASE)
    
    # <p>text</p> → just text (paragraph breaks)
    content = re.sub(r'<p>([^<]*)</p>', r'\1\n', content, flags=re.IGNORECASE)
    
    # <li>text</li> → - text
    content = re.sub(r'<li>([^<]*)</li>', r'- \1', content, flags=re.IGNORECASE)
    
    return content


def fix_md024_duplicates(content: str) -> str:
    """Make duplicate headings unique."""
    lines = content.split('\n')
    heading_map = defaultdict(int)
    fixed_lines = []
    
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+?)(\s*\(\d+\))?\s*$', line)
        if match:
            level = match.group(1)
            heading_text = match.group(2).strip()
            
            # Track count
            heading_map[heading_text] += 1
            count = heading_map[heading_text]
            
            # Add suffix if duplicate
            if count > 1:
                # Remove existing suffix if any
                heading_text = re.sub(r'\s*\(\d+\)\s*$', '', heading_text)
                line = f"{level} {heading_text} ({count})"
            
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_file(file_path: Path, verbose: bool = False) -> tuple:
    """Process a single markdown file. Returns (changed, issues_fixed)."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        issues_fixed = []
        
        # Check and fix each issue type
        before_md025 = len(re.findall(r'^# [^#]', content, re.MULTILINE))
        content = fix_md025_multiple_h1(content)
        after_md025 = len(re.findall(r'^# [^#]', content, re.MULTILINE))
        if before_md025 != after_md025:
            issues_fixed.append(f"MD025: {before_md025} → {after_md025} h1s")
        
        # Check HTML tags before/after
        before_html = len(re.findall(r'<[^>]+>', content))
        content = fix_md033_html_tags(content)
        after_html = len(re.findall(r'<[^>]+>', content))
        if before_html > after_html:
            issues_fixed.append(f"MD033: {before_html} → {after_html} HTML tags")
        
        # Check duplicates before/after
        before_dup = sum(1 for _ in re.finditer(r'^#+\s+', content, re.MULTILINE))
        content = fix_md024_duplicates(content)
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            if verbose:
                print(f"✓ {file_path.relative_to('.')}: {', '.join(issues_fixed)}")
            return True, issues_fixed
        return False, []
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False, []


def main():
    root = Path('.')
    
    # Exclude directories
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'archive', 'legacy', 'external'}
    
    md_files = [p for p in root.rglob('*.md') 
                if not any(x in p.parts for x in exclude_dirs)]
    
    print("=" * 70)
    print("FIXING MD024, MD025, MD033 in markdown files...")
    print("=" * 70)
    
    changed = 0
    total_fixes = defaultdict(int)
    
    for md_file in md_files:
        was_changed, fixes = process_file(md_file, verbose=True)
        if was_changed:
            changed += 1
            for fix_msg in fixes:
                rule = fix_msg.split(':')[0]
                total_fixes[rule] += 1
    
    print("\n" + "=" * 70)
    print(f"✓ Fixed {changed} files")
    print(f"✓ Total fixes applied: {sum(total_fixes.values())}")
    for rule, count in sorted(total_fixes.items()):
        print(f"  - {rule}: {count}")
    print("=" * 70)


if __name__ == '__main__':
    main()
