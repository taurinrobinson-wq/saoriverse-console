"""
Story Validator
===============

Validates story structure for:
- Broken links (choices pointing to non-existent passages)
- Missing start passage
- Dead ends (passages with no choices)
- Unreachable passages
- Duplicate passage names/IDs
- Required fields

Usage:
    python story_validator.py story_definitions.py
    python story_validator.py --json  # Output JSON format
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class StoryValidator:
    """Validate story structure and integrity."""
    
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.story_data = self._load_story(json_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passages: Dict[str, Dict] = {}
        self.choices: List[Dict] = []
        
        # Build lookup tables
        if self.story_data and 'passages' in self.story_data:
            for passage in self.story_data['passages']:
                pid = passage.get('pid')
                name = passage.get('name')
                if pid:
                    self.passages[pid] = passage
                if name:
                    self.passages[name] = passage
    
    def _load_story(self, json_path: str) -> Dict:
        """Load story JSON."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"✗ Error: Story file not found: {json_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON: {e}")
            sys.exit(1)
    
    def validate(self) -> Tuple[int, int]:
        """Run all validations. Returns (error_count, warning_count)."""
        self._check_required_fields()
        self._check_start_passage()
        self._check_duplicate_ids()
        self._check_passage_links()
        self._check_dead_ends()
        self._check_unreachable_passages()
        
        return len(self.errors), len(self.warnings)
    
    def _check_required_fields(self):
        """Verify all passages have required fields."""
        for passage in self.story_data.get('passages', []):
            pid = passage.get('pid')
            name = passage.get('name')
            text = passage.get('text', '')
            
            if not pid:
                self.errors.append("Passage missing 'pid'")
            if not name:
                self.errors.append(f"Passage (pid={pid}) missing 'name'")
            if not text or text.strip() == '':
                self.warnings.append(f"Passage '{name}' (pid={pid}) has empty text")
    
    def _check_start_passage(self):
        """Verify story has a start passage."""
        start_pid = self.story_data.get('startnode')
        
        if not start_pid:
            self.errors.append("Story missing 'startnode' - define which passage starts the game")
            return
        
        # Check if start passage exists
        found = False
        for passage in self.story_data.get('passages', []):
            if passage.get('pid') == start_pid:
                found = True
                break
        
        if not found:
            self.errors.append(f"Start passage (pid={start_pid}) does not exist")
    
    def _check_duplicate_ids(self):
        """Check for duplicate PIDs or names."""
        pids: Set[str] = set()
        names: Set[str] = set()
        
        for passage in self.story_data.get('passages', []):
            pid = passage.get('pid')
            name = passage.get('name')
            
            if pid:
                if pid in pids:
                    self.errors.append(f"Duplicate pid: '{pid}'")
                pids.add(pid)
            
            if name:
                if name in names:
                    self.errors.append(f"Duplicate passage name: '{name}'")
                names.add(name)
    
    def _check_passage_links(self):
        """Check that all passage links (from choices) exist."""
        for passage in self.story_data.get('passages', []):
            passage_name = passage.get('name')
            text = passage.get('text', '')
            
            # Look for Twine link syntax: [[Text->target]]
            import re
            links = re.findall(r'\[\[.*?->(\w+)\]\]', text)
            
            for target in links:
                if target not in self.passages:
                    self.errors.append(
                        f"Passage '{passage_name}' has broken link to non-existent passage '{target}'"
                    )
    
    def _check_dead_ends(self):
        """Warn about passages with no way to continue."""
        for passage in self.story_data.get('passages', []):
            name = passage.get('name')
            text = passage.get('text', '')
            is_end = passage.get('is_end', False)
            
            # Check for Twine links
            import re
            has_choices = len(re.findall(r'\[\[.*?->', text)) > 0
            
            if not has_choices and not is_end:
                self.warnings.append(
                    f"Passage '{name}' is a dead end (no choices, not marked as ending)"
                )
    
    def _check_unreachable_passages(self):
        """Warn about passages that can't be reached from start."""
        reachable: Set[str] = set()
        to_visit: List[str] = [self.story_data.get('startnode')]
        visited: Set[str] = set()
        
        while to_visit:
            current_pid = to_visit.pop(0)
            
            if not current_pid or current_pid in visited:
                continue
            
            visited.add(current_pid)
            reachable.add(current_pid)
            
            # Find passage by pid
            current_passage = None
            for p in self.story_data.get('passages', []):
                if p.get('pid') == current_pid:
                    current_passage = p
                    break
            
            if not current_passage:
                continue
            
            # Extract links from text
            import re
            text = current_passage.get('text', '')
            links = re.findall(r'\[\[.*?->(\w+)\]\]', text)
            
            for target in links:
                # Find target passage pid
                target_pid = None
                for p in self.story_data.get('passages', []):
                    if p.get('name') == target:
                        target_pid = p.get('pid')
                        break
                
                if target_pid and target_pid not in visited:
                    to_visit.append(target_pid)
        
        # Check for unreachable
        all_pids = {p.get('pid') for p in self.story_data.get('passages', [])}
        unreachable = all_pids - reachable
        
        for unreachable_pid in unreachable:
            # Find passage name
            passage_name = None
            for p in self.story_data.get('passages', []):
                if p.get('pid') == unreachable_pid:
                    passage_name = p.get('name')
                    break
            
            self.warnings.append(
                f"Passage '{passage_name}' (pid={unreachable_pid}) is unreachable from start"
            )
    
    def print_report(self):
        """Print validation report."""
        print()
        print("=" * 60)
        print("STORY VALIDATION REPORT")
        print("=" * 60)
        print()
        
        # Story metadata
        print(f"Story: {self.story_data.get('name', 'Unknown')}")
        print(f"Total passages: {len(self.story_data.get('passages', []))}")
        print()
        
        # Errors
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
            print()
        else:
            print("✓ No structural errors")
            print()
        
        # Warnings
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        else:
            print("✓ No warnings")
            print()
        
        # Summary
        if not self.errors:
            print("✅ STORY IS VALID")
        else:
            print(f"❌ STORY HAS {len(self.errors)} ERROR(S)")
        
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate story structure")
    parser.add_argument(
        'story_file',
        nargs='?',
        default='velinor/stories/sample_story.json',
        help='Path to story JSON file'
    )
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    validator = StoryValidator(args.story_file)
    error_count, warning_count = validator.validate()
    
    if args.json:
        report = {
            'story': validator.story_data.get('name'),
            'passages': len(validator.story_data.get('passages', [])),
            'errors': validator.errors,
            'warnings': validator.warnings,
            'valid': error_count == 0 and (not args.strict or warning_count == 0)
        }
        print(json.dumps(report, indent=2))
    else:
        validator.print_report()
    
    # Exit with appropriate code
    if error_count > 0 or (args.strict and warning_count > 0):
        sys.exit(1)


if __name__ == "__main__":
    main()
