#!/usr/bin/env python3
"""Fix remaining MD003 and MD033 issues"""
import re
from pathlib import Path
from collections import defaultdict


def fix_md003_atx_closed(content: str) -> str:
    """Convert # Heading # to # Heading."""
    return re.sub(
        r'^(#{1,6})\s+(.+?)\s+\1\s*$',
        r'\1 \2',
        content,
        flags=re.MULTILINE
    )


def fix_md033_comprehensive(content: str) -> str:
    """Convert HTML tags to markdown."""
    replacements = [
        (r'<br\s*/?>', '\n', re.IGNORECASE),
        (r'<b>([^<]*)</b>', r'**\1**', re.IGNORECASE),
        (r'<i>([^<]*)</i>', r'*\1*', re.IGNORECASE),
        (r'<strong>([^<]*)</strong>', r'**\1**', re.IGNORECASE),
        (r'<em>([^<]*)</em>', r'*\1*', re.IGNORECASE),
        (r'<u>([^<]*)</u>', r'_\1_', re.IGNORECASE),
        (r'<code>([^<]*)</code>', r'`\1`', re.IGNORECASE),
        (r'<kbd>([^<]*)</kbd>', r'`\1`', re.IGNORECASE),
        (r'<hr\s*/?>', '\n---\n', re.IGNORECASE),
        (r'<small>([^<]*)</small>', r'\1', re.IGNORECASE),
    ]
    
    for pattern, replacement, flags in replacements:
        content = re.sub(pattern, replacement, content, flags=flags)
    
    return content


def process_file(file_path: Path) -> tuple:
    """Process file, return (changed, fixes_applied)."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        fixes = []
        
        # Check MD003
        md003_before = len(re.findall(r'^#+\s+.+\s+#+\s*$', content, re.MULTILINE))
        content = fix_md003_atx_closed(content)
        md003_after = len(re.findall(r'^#+\s+.+\s+#+\s*$', content, re.MULTILINE))
        if md003_before > md003_after:
            fixes.append(f"MD003: {md003_before - md003_after}")
        
        # Check MD033
        html_before = len(re.findall(r'<[^>]+>', content))
        content = fix_md033_comprehensive(content)
        html_after = len(re.findall(r'<[^>]+>', content))
        if html_before > html_after:
            fixes.append(f"MD033: {html_before - html_after}")
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes
        return False, []
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return False, []


def main():
    target_files = [
        'docs/TIER_3_ACHIEVEMENT_SUMMARY.md',
        'docs/guides/MODULARIZATION_COMPLETE.md',
        'velinor/markdowngameinstructions/velinorian_lexicon/10_lexicon.md',
        'velinor/markdowngameinstructions/velinorian_lexicon/final_expansion.md',
        'velinor/markdowngameinstructions/velinorian_lexicon/joy_ach_expansion.md',
        'docs/EMOTION_INTEGRATION_GUIDE.md',
        'DraftShift/Docs/CalBar_Buildout_Plan.md',
        'tools/actionlint/docs/checks.md',
        'velinor-web/VELINOR_WEB_MASTER_DOC.md',
        'velinor/markdowngameinstructions/design/new_features.md',
    ]
    
    root = Path('.')
    changed = 0
    total_fixes = defaultdict(int)
    
    print("=" * 70)
    print("FIXING REMAINING ISSUES (MD003, MD033)")
    print("=" * 70)
    
    for target in target_files:
        file_path = root / target
        if file_path.exists():
            was_changed, fixes = process_file(file_path)
            if was_changed:
                changed += 1
                for fix_msg in fixes:
                    rule, count = fix_msg.split(': ')
                    total_fixes[rule] += int(count)
                    print(f"✓ {target}: {fix_msg}")
            else:
                print(f"• {target}: No changes")
        else:
            print(f"✗ {target}: Not found")
    
    print("\n" + "=" * 70)
    print(f"✓ Fixed {changed} files")
    for rule in sorted(total_fixes.keys()):
        print(f"  - {rule}: {total_fixes[rule]} issues")
    print("=" * 70)


if __name__ == '__main__':
    main()
