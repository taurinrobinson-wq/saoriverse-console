#!/usr/bin/env python
"""
DraftShift Quick Start Example

Demonstrates how to use the DraftShift platform to build pleadings
from JSON input files.
"""

import json
from pathlib import Path
from draftshift import PleadingFactory

def main():
    """Build all four pleading types from fixtures."""
    
    # Define paths
    base = Path(__file__).parent
    config_dir = base / "draftshift" / "formats"
    fixtures_dir = base / "draftshift" / "tests" / "fixtures"
    output_dir = base / "draftshift" / "tests" / "output"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Config files
    config_path = config_dir / "california_civil.yaml"
    citation_path = config_dir / "california_civil_citation.yaml"
    
    # Pleading fixtures to build
    fixtures = {
        "motion.json": "Motion.docx",
        "opposition.json": "Opposition.docx",
        "reply.json": "Reply.docx",
        "declaration.json": "Declaration.docx",
    }
    
    print("=" * 70)
    print("DraftShift — Building California Civil Pleadings")
    print("=" * 70)
    print()
    
    # Initialize factory
    factory = PleadingFactory(str(config_path), str(citation_path))
    
    # Build each pleading
    for fixture_name, output_name in fixtures.items():
        fixture_path = fixtures_dir / fixture_name
        output_path = output_dir / output_name
        
        print(f"Building: {fixture_name}")
        
        # Load JSON data
        with open(fixture_path, "r") as f:
            data = json.load(f)
        
        # Create pleading via factory
        pleading = factory.create(data)
        
        # Build document
        pleading.build(data)
        
        # Save output
        pleading.save(str(output_path))
        
        print(f"  ✓ Generated: {output_path}")
        print()
    
    print("=" * 70)
    print("All pleadings built successfully!")
    print(f"Output directory: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
