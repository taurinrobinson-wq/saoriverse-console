"""
CLI — Command-Line Interface for Building California Pleadings

Loads a JSON input file, instantiates the correct pleading class via PleadingFactory,
builds the document, and saves it as a DOCX file.

Usage:
    python -m draftshift.pleadings.cli motion.json
    python -m draftshift.pleadings.cli motion.json -o Motion_to_Compel.docx
    python -m draftshift.pleadings.cli declaration.json -c path/to/config.yaml
"""

import json
import argparse
import sys
from pathlib import Path
from .pleading_factory import PleadingFactory


def build_from_json():
    """
    Main CLI entry point for building pleadings from JSON input.
    """
    parser = argparse.ArgumentParser(
        description="Build California-compliant pleadings from JSON input files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m draftshift.pleadings.cli motion.json
  python -m draftshift.pleadings.cli motion.json -o Motion_to_Compel.docx
  python -m draftshift.pleadings.cli declaration.json \\
    -c formats/california/california_civil.yaml
        """
    )

    parser.add_argument(
        "input",
        help="Path to JSON input file (must contain 'type' field)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output DOCX file path. Defaults to <type>.docx (e.g., Motion.docx)",
        default=None
    )

    parser.add_argument(
        "-c", "--config",
        help="Path to california_civil.yaml formatting config",
        default="draftshift/formats/california_civil.yaml"
    )

    parser.add_argument(
        "-t", "--citation",
        help="Path to california_civil_citation.yaml citation rules",
        default="draftshift/formats/california_civil_citation.yaml"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print verbose output"
    )

    args = parser.parse_args()

    try:
        # Validate input file exists
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        # Load JSON data
        if args.verbose:
            print(f"Loading JSON from: {args.input}")

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate required 'type' field
        if "type" not in data:
            print(
                "Error: JSON input must contain a 'type' field "
                "(motion, opposition, reply, or declaration)",
                file=sys.stderr
            )
            sys.exit(1)

        # Determine output filename
        if args.output:
            output_path = args.output
        else:
            pleading_type = data.get("type", "pleading").lower()
            output_path = f"{pleading_type.capitalize()}.docx"

        if args.verbose:
            print(f"Pleading type: {data['type']}")
            print(f"Config file: {args.config}")
            print(f"Citation rules: {args.citation}")
            print(f"Output file: {output_path}")

        # Validate config files exist
        config_path = Path(args.config)
        citation_path = Path(args.citation)

        if not config_path.exists():
            print(f"Error: Config file not found: {args.config}", file=sys.stderr)
            sys.exit(1)

        if not citation_path.exists():
            print(f"Error: Citation file not found: {args.citation}", file=sys.stderr)
            sys.exit(1)

        # Build document
        if args.verbose:
            print("Instantiating pleading class...")

        factory = PleadingFactory(str(config_path), str(citation_path))
        pleading = factory.create(data)

        if args.verbose:
            print(f"Building {data['type']}...")

        pleading.build(data)

        if args.verbose:
            print(f"Saving to: {output_path}")

        pleading.save(output_path)

        print(f"✓ Generated: {output_path}")

        if args.verbose:
            print("Document build completed successfully.")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    build_from_json()
