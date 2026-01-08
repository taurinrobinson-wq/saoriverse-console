"""
Story Map Parser
================

Converts Markdown story map (story_map_velinor.md) into Python story definitions.

This tool reads your Markdown notes and generates Python boilerplate that you can 
then refine with actual story text.

Usage:
    python story_map_parser.py --input story_map_velinor.md --output story_definitions_auto.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class MarkdownStoryParser:
    """Parse story map Markdown into Python definitions."""
    
    def __init__(self, markdown_path: str):
        self.markdown_path = Path(markdown_path)
        self.content = self.markdown_path.read_text(encoding='utf-8')
        self.passages: List[Dict] = []
        self.choices: List[Dict] = []
        self.passage_counter = 1
        
    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        """Parse Markdown and extract passages and choices."""
        lines = self.content.split('\n')
        current_passage = None
        passage_text = []
        in_passage = False
        
        for i, line in enumerate(lines):
            # Look for H3 headers as passage starts (### Passage Name)
            if line.startswith('### '):
                # Save previous passage if exists
                if current_passage:
                    current_passage['text'] = '\n'.join(passage_text).strip()
                    self.passages.append(current_passage)
                
                # Start new passage
                passage_name = line.replace('### ', '').strip()
                current_passage = {
                    'pid': str(self.passage_counter),
                    'name': self._slugify(passage_name),
                    'original_name': passage_name,
                    'text': '',
                    'tags': []
                }
                self.passage_counter += 1
                passage_text = []
                in_passage = True
                
            elif in_passage and line.startswith('#### '):
                # Sub-section within passage (might be choices)
                passage_text.append(line)
                
            elif in_passage and line.startswith('- '):
                # Bullet point - likely a choice
                choice_text = line.replace('- ', '').strip()
                if current_passage:
                    self.choices.append({
                        'from_passage': current_passage['name'],
                        'text': choice_text,
                        'to_passage': self._extract_target(choice_text)
                    })
            else:
                if in_passage and line.strip():
                    passage_text.append(line)
        
        # Save last passage
        if current_passage:
            current_passage['text'] = '\n'.join(passage_text).strip()
            self.passages.append(current_passage)
        
        return self.passages, self.choices
    
    def _slugify(self, text: str) -> str:
        """Convert text to snake_case."""
        text = re.sub(r'[^\w\s]', '', text).lower()
        text = re.sub(r'\s+', '_', text)
        return text
    
    def _extract_target(self, choice_text: str) -> str:
        """Try to extract target passage from choice text."""
        # Look for patterns like "-> passage_name" or "→ passage_name"
        match = re.search(r'[→->]\s*(\w+)', choice_text)
        if match:
            return match.group(1)
        
        # Otherwise guess based on choice text
        return self._slugify(choice_text[:30])
    
    def generate_python(self) -> str:
        """Generate Python story definitions from parsed data."""
        lines = [
            '"""',
            'Generated Story Definitions',
            '============================',
            '',
            'This file was auto-generated from story_map_velinor.md.',
            'Edit the passages below and add your story text.',
            '',
            'To rebuild from Markdown:',
            '    python story_map_parser.py --input story_map_velinor.md --output story_definitions.py',
            '"""',
            '',
            'from velinor.engine.twine_adapter import StoryBuilder',
            '',
            '',
            'def build_velinor_story():',
            '    """Build Velinor: Remnants of the Tone story."""',
            '    ',
            '    story = StoryBuilder("Velinor: Remnants of the Tone")',
            '    ',
        ]
        
        # Add passages
        first_passage = True
        for passage in self.passages:
            is_start = "start" in passage['original_name'].lower() or first_passage
            first_passage = False
            
            lines.append(f'    # {passage["original_name"]}')
            lines.append(f'    story.add_passage(')
            lines.append(f'        pid="{passage["pid"]}",')
            lines.append(f'        name="{passage["name"]}",')
            lines.append(f'        text="""')
            lines.append(f'{passage["text"]}')
            lines.append(f'        """,')
            if is_start:
                lines.append(f'        is_start=True,')
            lines.append(f'        tags=[]')
            lines.append(f'    )')
            lines.append('')
        
        # Add choices
        for choice in self.choices:
            if choice['to_passage']:
                lines.append(f'    # Choice in {choice["from_passage"]}')
                lines.append(f'    story.add_choice(')
                lines.append(f'        from_passage="{choice["from_passage"]}",')
                lines.append(f'        text="{choice["text"]}",')
                lines.append(f'        to_passage="{choice["to_passage"]}",')
                lines.append(f'        stat_effects={{}}')
                lines.append(f'    )')
                lines.append('')
        
        lines.append('    return story')
        lines.append('')
        lines.append('')
        lines.append('if __name__ == "__main__":')
        lines.append('    story = build_velinor_story()')
        lines.append('    story.export_json("velinor/stories/sample_story.json")')
        lines.append('    print("✓ Story exported")')
        
        return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse Markdown story map into Python definitions")
    parser.add_argument('--input', default='velinor/story_map_velinor.md', help='Input Markdown file')
    parser.add_argument('--output', default='velinor/stories/story_definitions_auto.py', help='Output Python file')
    parser.add_argument('--preview', action='store_true', help='Print preview instead of saving')
    
    args = parser.parse_args()
    
    try:
        markdown_parser = MarkdownStoryParser(args.input)
        passages, choices = markdown_parser.parse()
        
        print(f"✓ Parsed {len(passages)} passages")
        print(f"✓ Found {len(choices)} choices")
        print()
        
        python_code = markdown_parser.generate_python()
        
        if args.preview:
            print(python_code)
        else:
            output_path = Path(args.output)
            output_path.write_text(python_code, encoding='utf-8')
            print(f"✓ Generated: {output_path}")
            print()
            print("Next steps:")
            print(f"  1. Edit {output_path} to add story text")
            print(f"  2. Run: python story_definitions.py")
            print(f"  3. Validate: python story_validator.py")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
