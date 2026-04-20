#!/usr/bin/env python3
"""
Fix MD024 (duplicate headings) and MD033 (HTML tags)

MD024: Makes duplicate heading text unique by adding context
MD033: Converts <br> tags to markdown equivalents
"""
import re
from pathlib import Path
from collections import defaultdict


def fix_md033(content: str) -> str:
    """Convert HTML tags to markdown equivalents."""
    # Convert <br> and <br/> and <br /> to markdown (empty line)
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
    
    # Convert <b>text</b> to **text**
    content = re.sub(r'<b>(.*?)</b>', r'**\1**', content, flags=re.IGNORECASE)
    
    # Convert <i>text</i> to *text*
    content = re.sub(r'<i>(.*?)</i>', r'*\1*', content, flags=re.IGNORECASE)
    
    # Convert <strong>text</strong> to **text**
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content, flags=re.IGNORECASE)
    
    # Convert <em>text</em> to *text*
    content = re.sub(r'<em>(.*?)</em>', r'*\1*', content, flags=re.IGNORECASE)
    
    return content


def fix_md024(content: str) -> str:
    """Make duplicate headings unique by adding numeric suffixes or context."""
    lines = content.split('\n')
    heading_counts = defaultdict(int)
    fixed_lines = []
    
    for i, line in enumerate(lines):
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = match.group(1)
            heading_text = match.group(2).strip()
            
            # Track occurrences
            heading_key = (level, heading_text)
            heading_counts[heading_key] += 1
            count = heading_counts[heading_key]
            
            # If this is a duplicate, add context or number
            if count > 1:
                # Try to get context from surrounding lines
                prev_line = lines[i-1].strip() if i > 0 else ""
                
                # Add a numeric suffix or context
                if prev_line and not prev_line.startswith('#'):
                    # Use previous line for context if it's not empty
                    fixed_lines.append(f"{level} {heading_text} ({count})")
                else:
                    # Just add a numeric suffix
                    fixed_lines.append(f"{level} {heading_text} ({count})")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_file(file_path: Path) -> bool:
    """Process a single markdown file. Returns True if changed."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply fixes
        content = fix_md033(content)
        content = fix_md024(content)
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    # List of problematic files to target
    target_files = [
        "GLYPH_ENHANCEMENTS_FROM_TRANSCRIPT.md",
        "INTEGRATED_PIPELINE_IMPLEMENTATION.md",
        "LOCAL_LLM_AND_DEPENDENCIES.md",
        "MEMORY_LAYER_ARCHITECTURE.md",
        "MODULE_INTEGRATION_MAP.md",
        "firstperson/docs/MEMORY_LAYER_QUICK_REFERENCE.md",
        "firstperson/docs/MEMORY_LAYER_VISUAL_ARCHITECTURE.md",
    ]
    
    root = Path(".")
    changed = 0
    
    for target in target_files:
        file_path = root / target
        if file_path.exists():
            if process_file(file_path):
                print(f"Fixed: {target}")
                changed += 1
            else:
                print(f"No changes: {target}")
        else:
            print(f"Not found: {target}")
    
    print(f"\n✓ Fixed {changed} files")


if __name__ == '__main__':
    main()
