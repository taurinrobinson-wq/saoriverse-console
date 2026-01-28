# DraftShift — Litigation Document Automation

> AI-powered platform for generating California civil pleadings with proper formatting, citation rules, and legal analysis.

## Features

- **Modular Architecture**: Separate YAML configs for formatting and citation rules
- **Multiple Pleading Types**: Motion, Opposition, Reply, Declaration
- **California Compliant**: 28-line pleading paper, proper caption tables, signature blocks
- **Factory Pattern**: Automatic pleading type detection from JSON input
- **CLI Ready**: Build pleadings from command line with single command
- **Extensible**: Easy to add new courts, jurisdictions, and pleading types

## Quick Start

### Installation

```bash
cd saoriverse-console
pip install -e .
```

Or for development:

```bash
pip install -e ".[dev]"
```

### Building a Pleading

#### From CLI

```bash
# Build motion from JSON fixture
draftshift draftshift/tests/fixtures/motion.json

# Build with custom output filename
draftshift draftshift/tests/fixtures/motion.json -o Motion_to_Compel.docx

# Verbose output
draftshift draftshift/tests/fixtures/reply.json -v
```

#### From Python

```python
from draftshift import PleadingFactory
import json

# Load data
with open("motion.json") as f:
    data = json.load(f)

# Create and build pleading
factory = PleadingFactory(
    "draftshift/formats/california_civil.yaml",
    "draftshift/formats/california_civil_citation.yaml"
)
pleading = factory.create(data)
pleading.build(data)
pleading.save("Motion.docx")
```

## Project Structure

```
draftshift/
├── pleadings/              # Core pleading classes
│   ├── base.py            # BaseDocument (formatting engine)
│   ├── builder.py         # DocumentBuilder (orchestrator)
│   ├── motion.py          # Motion class
│   ├── opposition.py      # Opposition class
│   ├── reply.py           # Reply class
│   ├── declaration.py     # Declaration class
│   ├── pleading_factory.py # Factory for type detection
│   ├── cli.py             # Command-line interface
│   └── __init__.py
├── formats/                # YAML configuration files
│   ├── california_civil.yaml           # Formatting rules
│   ├── california_civil_citation.yaml  # Citation rules
│   └── __init__.py
├── tests/                  # Test suite
│   ├── fixtures/           # JSON input files
│   │   ├── motion.json
│   │   ├── opposition.json
│   │   ├── reply.json
│   │   └── declaration.json
│   ├── test_pleadings.py   # pytest test suite
│   └── __init__.py
└── __init__.py
```

## Architecture

### Three-Layer Design

1. **BaseDocument** (Engine): Loads YAML configs, manages DOCX generation, provides helper methods
2. **DocumentBuilder/Pleading Classes** (Templates): Define pleading structure, orchestrate components
3. **PleadingFactory** (Router): Detects pleading type, instantiates correct class

### Configuration-Driven

- **california_civil.yaml**: Page geometry, margins, pleading paper, caption tables, headings, signature block
- **california_civil_citation.yaml**: Case name formatting, reporters, statutes, secondary sources, parentheticals

### Extensible

To add a new pleading type:

```python
# draftshift/pleadings/motion_in_limine.py
from .base import BaseDocument

class MotionInLimine(BaseDocument):
    def build(self, data):
        # Custom structure for motion in limine
        pass
```

Then register in `PleadingFactory.TYPES`:

```python
TYPES = {
    "motion": Motion,
    "motion_in_limine": MotionInLimine,
    ...
}
```

## JSON Input Format

### Required Fields

Every JSON input must have:
- `"type"`: One of `motion`, `opposition`, `reply`, `declaration`

### Standard Structure

```json
{
  "type": "motion",
  "attorney": {
    "name": "Attorney Name",
    "title": "Esq.",
    "bar_number": "123456",
    "firm": "Law Firm Name",
    "address": "Street Address",
    "city_state_zip": "City, ST 12345",
    "phone": "Tel: (123) 555-0199",
    "email": "attorney@example.com",
    "party": "Plaintiff"
  },
  "case": {
    "county": "Los Angeles",
    "case_number": "22STCV12345",
    "parties": {
      "plaintiff": "JOHN DOE, an individual",
      "defendant": "ACME CORPORATION, a Delaware corporation"
    }
  },
  "title": "MOTION FOR SUMMARY JUDGMENT",
  "arguments": [
    { "level": 1, "text": "INTRODUCTION" },
    { "paragraph": "This motion seeks..." },
    { "level": 1, "text": "ARGUMENT" },
    { "level": 2, "text": "I. No Triable Issue of Fact" },
    { "paragraph": "The evidence establishes..." }
  ],
  "pos": {
    "server_name": "John Smith",
    "server_county": "Los Angeles",
    "document_title": "Motion for Summary Judgment",
    "service_date": "January 28, 2026",
    "service_method": "electronic service via email",
    "service_location": "Los Angeles, California",
    "execution_date": "January 28, 2026",
    "execution_location": "Los Angeles"
  }
}
```

## Testing

Run the full test suite:

```bash
make test
```

Verbose output:

```bash
make test-verbose
```

Coverage report:

```bash
make test-coverage
```

Individual test file:

```bash
pytest draftshift/tests/test_pleadings.py::TestMotion -v
```

## Development

### Code Formatting

```bash
make format
```

### Linting

```bash
make lint
```

### Type Checking

```bash
make type-check
```

### Build Distribution

```bash
make build
```

## Usage Examples

### Motion to Compel

```bash
draftshift draftshift/tests/fixtures/motion.json -o Motion_to_Compel.docx
```

### Declaration Supporting Motion

```bash
draftshift draftshift/tests/fixtures/declaration.json -o Declaration_of_Jane_Doe.docx
```

### Opposition to Summary Judgment

```bash
draftshift draftshift/tests/fixtures/opposition.json -o Opposition_to_SJ.docx -v
```

### Reply to Opposition

```bash
draftshift draftshift/tests/fixtures/reply.json
```

## Formatting Specifications

### California Civil Pleading Paper

- **Lines**: 28 lines per page
- **Line Spacing**: Exactly 24pt
- **Font**: Times New Roman 12pt throughout
- **Margins**: 1 inch all sides
- **Caption**: Two-column table (left: 0.5pt right/bottom borders)

### Heading Hierarchy

- **Level 1**: Roman uppercase (I, II, III, IV)
- **Level 2**: Numeric (1, 2, 3)
- **Level 3**: Alpha uppercase (A, B, C)
- **Level 4**: Roman lowercase (i, ii, iii)

### Signature Block

Standard California format with attorney/declarant name, bar number, and proof of service.

## Citation Formatting

Supports California citation style:
- Case names: italicized, comma after
- Reporters: `123 Cal.App.4th 456`
- Statutes: `Cal. Code Civ. Proc. § 1234`
- Secondary sources: Title italic, author in parentheses, year

## Limitations

Currently supports:
- ✓ California state courts
- ✓ Motion, Opposition, Reply, Declaration
- ✓ California citation style

Future:
- Federal courts (District, Appellate, Supreme Court)
- Local rules (LA Superior, Orange County, San Diego)
- Bluebook citation style
- Declarations with multiple declarants
- Complex multi-part motions

## License

Proprietary — All rights reserved

## Author

Taurin Robinson  
DraftShift Legal  
trobinson@draftshiftlaw.com

## Contributing

Internal development only.

---

**Version**: 0.1.0  
**Last Updated**: January 28, 2026
