"""
Build Story System
==================

Complete pipeline for story management:
  1. Parse Markdown → Generate Python scaffold (optional)
  2. Build Python definitions → Generate JSON
  3. Validate JSON → Check for errors/warnings

Usage:
    python build_story.py                    # Build from story_definitions.py
    python build_story.py --validate         # Build + validate
    python build_story.py --parse-markdown   # Regenerate from Markdown
    python build_story.py --watch            # Watch for changes and rebuild
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class StoryBuilder:
    """Orchestrate story building pipeline."""
    
    def __init__(self, story_dir: str = "velinor/stories"):
        self.story_dir = Path(story_dir)
        self.definitions_file = self.story_dir / "story_definitions.py"
        self.output_file = self.story_dir / "sample_story.json"
        self.npc_state_file = self.story_dir / "npc_state.json"
        self.validator_file = self.story_dir / "story_validator.py"
        self.markdown_file = Path("velinor/story_map_velinor.md")
    
    def build(self) -> bool:
        """Build story JSON from Python definitions."""
        print("📖 Building story...")
        print(f"   Input:  {self.definitions_file}")
        print(f"   Output: {self.output_file}")
        
        try:
            # Run story definitions script
            result = subprocess.run(
                [sys.executable, str(self.definitions_file)],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode != 0:
                print(f"❌ Build failed:")
                print(result.stderr)
                return False
            
            print(result.stdout)
            
            # Check if NPC state was generated
            if self.npc_state_file.exists():
                print(f"   NPC state: {self.npc_state_file}")
                self._show_npc_summary()
            
            return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _show_npc_summary(self) -> None:
        """Display summary of NPC REMNANTS state."""
        try:
            with open(self.npc_state_file, 'r') as f:
                npc_data = json.load(f)
            
            if 'npc_profiles' in npc_data:
                print("\n🧑‍🤝‍🧑 NPC REMNANTS Evolution:")
                profiles = npc_data['npc_profiles']
                for npc_name, npc_info in profiles.items():
                    remnants = npc_info.get('remnants', {})
                    # Show top 3 traits
                    sorted_traits = sorted(remnants.items(), key=lambda x: x[1], reverse=True)[:3]
                    traits_str = ", ".join([f"{t[0]}: {t[1]:.2f}" for t in sorted_traits])
                    print(f"   • {npc_name}: {traits_str}")
        except Exception as e:
            # Silently fail if can't show summary
            pass
    
    def validate(self) -> bool:
        """Validate generated story JSON."""
        print()
        print("🔍 Validating story...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.validator_file), str(self.output_file)],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print("⚠️  Validation issues found (see above)")
                return False
            
            return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def parse_markdown(self) -> bool:
        """Parse Markdown story map to generate Python scaffold."""
        print("📝 Parsing Markdown story map...")
        print(f"   Input: {self.markdown_file}")
        
        try:
            parser_script = self.story_dir / "story_map_parser.py"
            result = subprocess.run(
                [sys.executable, str(parser_script), 
                 "--input", str(self.markdown_file),
                 "--output", str(self.definitions_file)],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print(result.stderr)
                return False
            
            return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def watch(self, interval: int = 2):
        """Watch definitions file for changes and rebuild."""
        print("👀 Watching for changes (Ctrl+C to stop)...")
        print()
        
        last_mtime = self.definitions_file.stat().st_mtime
        
        try:
            while True:
                time.sleep(interval)
                
                try:
                    current_mtime = self.definitions_file.stat().st_mtime
                    
                    if current_mtime != last_mtime:
                        print()
                        print("=" * 60)
                        print(f"[{time.strftime('%H:%M:%S')}] Changes detected")
                        print("=" * 60)
                        
                        last_mtime = current_mtime
                        
                        if self.build():
                            self.validate()
                        
                        print()
                        print("Ready for changes...")
                
                except FileNotFoundError:
                    print("⚠️  Definitions file was deleted")
                    break
        
        except KeyboardInterrupt:
            print("\n👋 Stopped watching")
    
    def full_pipeline(self, validate: bool = False) -> bool:
        """Run complete build pipeline."""
        print("🚀 Story Build Pipeline")
        print("=" * 60)
        
        # Build
        if not self.build():
            return False
        
        # Validate (optional)
        if validate:
            if not self.validate():
                return False
        
        print()
        print("✅ Build complete!")
        print()
        print("Next steps:")
        print(f"  • Edit {self.definitions_file} to add/modify story")
        print(f"  • Run: python build_story.py --validate")
        print(f"  • Watch: python build_story.py --watch")
        
        return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Build story from Python definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_story.py
  python build_story.py --validate
  python build_story.py --watch
  python build_story.py --parse-markdown --validate
        """
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate story after building'
    )
    parser.add_argument(
        '--parse-markdown',
        action='store_true',
        help='Parse Markdown story map and generate Python definitions'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch for changes and rebuild'
    )
    
    args = parser.parse_args()
    
    builder = StoryBuilder()
    
    try:
        if args.parse_markdown:
            if builder.parse_markdown():
                if args.validate:
                    builder.validate()
        
        elif args.watch:
            builder.watch()
        
        else:
            success = builder.full_pipeline(validate=args.validate)
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n👋 Cancelled")


if __name__ == "__main__":
    main()
