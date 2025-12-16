# Testing Guide - SaoriVerse Console

**Date**: December 3, 2025
##

## Quick Start

### Run All Tests

```bash
pytest tests/
```



### Run Only Unit Tests

```bash
pytest tests/unit/
```



### Run Only Integration Tests

```bash
pytest tests/integration/
```



### Run Specific Test File

```bash
pytest tests/unit/test_signal_parser.py -v
```



### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html

# Open htmlcov/index.html to view coverage
```


##

## Test Organization

### tests/unit/ (26 test files)
Unit tests for individual modules. Each test file focuses on one `src/` module.

**Examples:**
- `test_signal_parser.py` → Tests `src/signal_parser.py`
- `test_response_generator.py` → Tests `src/response_generator.py`
- `test_voice_interface.py` → Tests `src/voice_interface.py`

**Characteristics:**
- Fast (< 100ms per test)
- Isolated (mock external dependencies)
- Comprehensive coverage of individual functions
- No I/O operations (use fixtures)

### tests/integration/ (11 test files)
Integration tests for module interactions and end-to-end flows.

**Examples:**
- `test_e2e_integration.py` → Full text-to-response pipeline
- `test_voice_to_response.py` → Full audio-to-response pipeline
- `test_learning_integration.py` → Learning system with persistence

**Characteristics:**
- Slower (can take seconds)
- Test real module interactions
- May use real files or fixture data
- Validate contracts between modules
##

## Pytest Configuration

### pytest.ini
Located at project root. Controls:
- Test discovery: `tests/` directory
- Test naming: Files `test_*.py`, functions `test_*`
- Output verbosity: `-v` flag for detailed output
- Error display: `--tb=short` for readable tracebacks

### tests/conftest.py
Shared pytest configuration:
- Fixtures for common test data
- Project root setup (sys.path)
- CWD management for test isolation

### Example Fixtures

```python
@pytest.fixture
def sample_signal():
    return {
        "voltage": 0.6,
        "tone": "Yearning",
        "attunement": 0.7,
    }

@pytest.fixture
def sample_user_input():
    return "I've been feeling lost lately."
```



**Usage in tests:**

```python
def test_parser(sample_user_input):
    result = parse_input(sample_user_input)
    assert result is not None
```


##

## Writing New Tests

### Unit Test Template

```python
"""Tests for src/my_module.py"""

import pytest
from src.my_module import my_function


class TestMyFunction:
    """Tests for my_function."""

    def test_happy_path(self):
        """Test normal operation."""
        result = my_function("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case."""
        result = my_function("")
        assert result is not None

    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function(None)
```



### Integration Test Template

```python
"""Integration tests for response pipeline."""

import pytest
from src.signal_parser import parse_input
from src.response_generator import process_user_input


def test_full_pipeline():
    """Test end-to-end: input → signal → response."""
    user_input = "I'm feeling overwhelmed"

    # Parse input
    signal = parse_input(user_input)
    assert signal is not None

    # Generate response
    response = process_user_input(user_input)
    assert response is not None
    assert len(response) > 0
```


##

## Common Test Patterns

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('src.module.external_function') as mock_func:
        mock_func.return_value = "mocked"
        result = my_function()
        assert result == "mocked"
        mock_func.assert_called_once()
```



### Fixture Usage

```python
@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary directory for test data."""
    return tmp_path / "test_data"

def test_file_operations(temp_data_dir):
    """Test with temporary directory."""
    file_path = temp_data_dir / "test.json"
    # Use file_path for testing
```



### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("happy", "positive"),
    ("sad", "negative"),
    ("neutral", "neutral"),
])
def test_emotion_detection(input, expected):
    result = detect_emotion(input)
    assert result == expected
```


##

## Running Tests in Different Ways

### By Directory

```bash
pytest tests/unit/              # All unit tests
pytest tests/integration/       # All integration tests
```



### By Module

```bash
pytest tests/ -k signal_parser  # Tests mentioning "signal_parser"
pytest tests/ -k "test_parse"   # Tests with "test_parse" in name
```



### By Marker

```bash

# Define in test: @pytest.mark.slow
pytest tests/ -m slow           # Only marked tests
pytest tests/ -m "not slow"     # Skip marked tests
```



### Specific Test

```bash
pytest tests/unit/test_signal_parser.py::TestParser::test_happy_path
```


##

## Continuous Integration

### GitHub Actions Workflow
`.github/workflows/tests.yml` runs:
1. `pytest tests/unit/` - Fast unit test suite
2. `pytest tests/integration/` - Integration tests
3. Coverage report generation

**Triggered on:**
- Push to `refactor/*` branches
- Pull requests to `main`

### Local Pre-commit Check

```bash

# Before committing
pytest tests/unit/ --tb=short

# If all pass:
git commit -m "..."
```


##

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -v                # Show all test names
pytest tests/ -vv               # Even more detail
pytest tests/ -vvv              # Maximum verbosity
```



### Print Debug Info

```python
def test_something():
    result = my_function()
    print(f"Result: {result}")  # Will show with -s flag
    pytest.set_trace()           # Drop into debugger
```



Run with:

```bash
pytest tests/ -s                # Show print() output
pytest tests/ --pdb             # Drop into debugger on failure
```



### Show Local Variables

```bash
pytest tests/ -l                # Show locals on failure
pytest tests/ --tb=long         # Longer traceback
```


##

## Coverage Reports

### Generate Coverage

```bash
pytest tests/ --cov=src
```



### View HTML Report

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```



### Coverage by Module

```bash
pytest tests/ --cov=src.response_generator
```


##

## Common Issues and Solutions

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'src'`
**Solution**: Ensure pytest.ini is in project root and conftest.py adds project to sys.path

### Fixture Not Found
**Problem**: `fixture 'my_fixture' not found`
**Solution**: Check fixture is defined in conftest.py or same test file

### Tests Pass Locally but Fail in CI
**Problem**: Different environment or missing dependencies
**Solution**: Check requirements.txt includes all test dependencies

### Slow Tests
**Problem**: Tests taking too long
**Solution**: Use @pytest.mark.slow to mark slow tests, run with -m "not slow"
##

## Best Practices

1. **One assertion per test** (when possible)
   - Makes failures clear
   - Easier to debug

2. **Descriptive test names**
   ```python
   # Good:
   def test_parser_extracts_emotional_signal_from_text():

   # Bad:
   def test_parse():
   ```

3. **Arrange-Act-Assert pattern**
   ```python
   def test_something():
       # Arrange
       input_data = prepare_data()

       # Act
       result = function_under_test(input_data)

       # Assert
       assert result == expected
   ```

4. **Use fixtures for common setup**
   ```python
   # Instead of repeating in every test:
   @pytest.fixture
   def sample_data():
       return {"key": "value"}
   ```

5. **Test both happy path and errors**
   ```python
   def test_happy_path():
       # Normal operation
       pass

   def test_error_handling():
       # Error conditions
       pass
   ```
##

## Test Metrics Target

After reorganization:
- **Unit tests**: 26 test files
- **Integration tests**: 11 test files
- **Target coverage**: > 80% of src/
- **Test execution time**: < 30 seconds for unit tests
##

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pytest tests/` | Run all tests |
| `pytest tests/unit/` | Run unit tests only |
| `pytest tests/ -v` | Verbose output |
| `pytest tests/ -s` | Show print() output |
| `pytest tests/ -k test_parse` | Run tests matching "test_parse" |
| `pytest tests/ --cov=src` | Show coverage |
| `pytest tests/ -m slow` | Run only slow tests |
| `pytest tests/ -x` | Stop on first failure |
##

**For architecture information, see**: `docs/ARCHITECTURE.md`
**For API reference, see**: `docs/API_REFERENCE.md`
