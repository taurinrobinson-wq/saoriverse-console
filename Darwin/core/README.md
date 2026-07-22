# Core Module: Shared Formatting Logic

Shared formatting engines, configuration management, and utilities used across Darwin components.

## Components

### Formatting Engines

- **TextTransformer** - Case conversion, whitespace handling, special character processing
- **StyleFormatter** - Bold, italic, underline, color, font handling
- **StructureFormatter** - Indentation, alignment, list formatting
- **PatternMatcher** - Regex-based formatting rules

### Configuration

- Rule definitions
- Format presets
- Environment-specific configurations
- User preferences

### Utilities

- Logging and debugging
- Error handling
- Data validation
- Caching mechanisms

## Tech Stack

- **Language**: Python 3.9+ and TypeScript
- **Testing**: pytest (Python), Jest (TypeScript)

## Project Structure

```
core/
├── formatting/
│   ├── text_transformer.py
│   ├── style_formatter.py
│   ├── structure_formatter.py
│   └── pattern_matcher.py
├── config/
│   ├── rules.py
│   ├── presets.py
│   └── defaults.py
├── utils/
│   ├── logger.py
│   ├── error_handler.py
│   └── validators.py
├── tests/
└── requirements.txt
```

## Usage

```python
from core.formatting.text_transformer import TextTransformer

transformer = TextTransformer()
result = transformer.to_title_case("hello world")
```

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest tests/
```
