#!/usr/bin/env python3
"""
Target highest-impact markdown fixes
Focus on the top 5 MD033 files: ~393 HTML tags total
"""
import re
from pathlib import Path
from collections import defaultdict


def fix_html_in_file(file_path: Path) -> int:
    """Fix HTML tags in a file. Return count of fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Convert common patterns
        # <br> → blank line
        content = re.sub(r'<br\s*/?>\s*\n', '\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        
        # Tables and list items
        content = re.sub(r'<li>([^<]*)</li>', r'\n- \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<\/li>', '', content, flags=re.IGNORECASE)
        
        # Bold/Italic
        content = re.sub(r'<b>([^<]*?)</b>', r'**\1**', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<strong>([^<]*?)</strong>', r'**\1**', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<i>([^<]*?)</i>', r'*\1*', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<em>([^<]*?)</em>', r'*\1*', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Code
        content = re.sub(r'<code>([^<]*?)</code>', r'`\1`', content, flags=re.IGNORECASE)
        content = re.sub(r'<tt>([^<]*?)</tt>', r'`\1`', content, flags=re.IGNORECASE)
        
        # Line breaks
        content = re.sub(r'<hr\s*/?>', '\n---\n', content, flags=re.IGNORECASE)
        
        # Other formatting
        content = re.sub(r'<u>([^<]*?)</u>', r'_\1_', content, flags=re.IGNORECASE)
        content = re.sub(r'<s>([^<]*?)</s>', r'~~\1~~', content, flags=re.IGNORECASE)
        content = re.sub(r'<del>([^<]*?)</del>', r'~~\1~~', content, flags=re.IGNORECASE)
        content = re.sub(r'<mark>([^<]*?)</mark>', r'**\1**', content, flags=re.IGNORECASE)
        
        # Empty/wrapper tags
        content = re.sub(r'<span>([^<]*?)</span>', r'\1', content, flags=re.IGNORECASE)
        content = re.sub(r'<div>([^<]*?)</div>', r'\1', content, flags=re.IGNORECASE)
        
        fixes = original.count('<') - content.count('<')
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes
        
        return 0
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return 0


def main():
    # Top 5 files with most MD033 issues
    target_files = [
        'docs/EMOTION_INTEGRATION_GUIDE.md',
        'DraftShift/Docs/CalBar_Buildout_Plan.md',
        'tools/actionlint/docs/checks.md',
        'velinor-web/VELINOR_WEB_MASTER_DOC.md',
        'velinor/markdowngameinstructions/design/new_features.md',
    ]
    
    root = Path('.')
    total_fixed = 0
    
    print("=" * 70)
    print("FIXING TOP 5 MD033 FILES (~393 HTML tags)")
    print("=" * 70)
    
    for target in target_files:
        file_path = root / target
        if file_path.exists():
            fixes = fix_html_in_file(file_path)
            if fixes > 0:
                print(f"✓ {target}: {fixes} HTML tags fixed")
                total_fixed += fixes
            else:
                print(f"• {target}: No changes")
        else:
            print(f"✗ {target}: Not found")
    
    print("\n" + "=" * 70)
    print(f"✓ Total HTML tags fixed: {total_fixed}")
    print("=" * 70)


if __name__ == '__main__':
    main()
