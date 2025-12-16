# FirstPerson Test Suite

Organized test suite for the FirstPerson / Emotional OS system.

## Structure

```text
```

tests/
├── conftest.py                 # Pytest configuration (shared fixtures)
├── run_tests.py               # Test runner script
├── pytest.ini                 # Pytest configuration
├── unit/                      # Unit tests (individual components)
│   ├── test_signal_matching.py
│   ├── test_glyph_messages.py
│   ├── test_local_mode.py
│   └── test_improvements.py
├── integration/               # Integration & E2E tests
│   ├── test_enhanced_system.py
│   ├── test_glyph_learning_pipeline.py
│   ├── test_poetry_enrichment_e2e.py
│   ├── test_ritual_processor.py
│   ├── test_overwhelm_fix.py
│   └── test_full_25_messages.py
└── performance/               # Performance & evolution tests
    ├── test_evolution_trigger.py
    └── test_evolving_glyphs.py

```



## Running Tests

### Using the test runner script

```bash


# Run all tests
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py unit

# Run only integration tests
python tests/run_tests.py integration

# Run only performance tests
python tests/run_tests.py performance

# Run with verbose output

```text
```

### Using pytest directly

```bash

# Run all tests
pytest tests/

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run specific test file
pytest tests/unit/test_signal_matching.py

# Run specific test function
pytest tests/unit/test_signal_matching.py::test_signal_matching

# Run with verbose output
pytest -v tests/

# Run with markers
```text
```text
```

## Test Categories

### Unit Tests (`tests/unit/`)

Individual component tests focusing on isolated functionality:

- **test_signal_matching.py**: Tests glyph signal matching against test messages
- **test_glyph_messages.py**: Comprehensive test message suite covering emotional states
- **test_local_mode.py**: Tests local emotional processing (NRC Lexicon + spaCy + Signal Parser)
- **test_improvements.py**: Tests improved emotional glyph matching

### Integration Tests (`tests/integration/`)

End-to-end tests verifying system components work together:

- **test_enhanced_system.py**: Tests expanded glyph processing system
- **test_glyph_learning_pipeline.py**: Tests real-time glyph learning (Phase 2)
- **test_poetry_enrichment_e2e.py**: Tests poetry enrichment and local mode (no external API)
- **test_ritual_processor.py**: Tests ritual capsule processor
- **test_overwhelm_fix.py**: Tests improved overwhelm processing
- **test_full_25_messages.py**: Full 25-message coverage test (>85% glyph coverage)

### Performance Tests (`tests/performance/`)

Tests focused on system evolution and performance:

- **test_evolution_trigger.py**: Tests glyph evolution triggering
- **test_evolving_glyphs.py**: Tests auto-evolving glyph generation system

## Installation & Setup

### Prerequisites

```bash

pip install -r requirements.txt

```text
```

### First Run

```bash
cd /workspaces/saoriverse-console
```text
```text
```

## Expected Results

### Unit Tests

✅ Should pass: Tests individual components in isolation

### Integration Tests

⚠️ May require: Local database setup, NRC lexicon files, poetry database
⚠️ Some tests: Skip gracefully if dependencies unavailable (designed for offline mode)

### Performance Tests

⚠️ May require: Supabase configuration for full functionality
✅ Offline mode: Includes fallbacks for testing without external APIs

## Troubleshooting

### Import Errors

If tests fail with import errors, ensure:

1. You're running from the project root: `cd /workspaces/saoriverse-console`
2. Dependencies are installed: `pip install -r requirements.txt`
3. Python path is correct (conftest.py handles this automatically)

### Database Errors

Some integration tests require local database setup:

```bash


# Initialize glyphs database

```text
```

### Missing Modules

Tests are designed with graceful fallbacks for optional dependencies (poetry, spaCy, etc.)
If you see warnings, it's expected and tests will skip that functionality.

## Adding New Tests

1. Create test file in appropriate subdirectory
2. Follow naming convention: `test_*.py`
3. Add test functions starting with `test_`
4. Import from project root (conftest.py handles path)

Example:

```python

# tests/unit/test_my_feature.py
def test_something():
    from emotional_os.glyphs import some_function
    result = some_function()
```text
```text
```

5. Run: `pytest tests/unit/test_my_feature.py`

## CI/CD Integration

For GitHub Actions or other CI systems:

```yaml

- name: Run tests
  run: python tests/run_tests.py

```

## Continuous Integration Setup

See `.github/workflows/` for example GitHub Actions configuration.
