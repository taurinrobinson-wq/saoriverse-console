# Development Setup Guide

## Prerequisites

- Python 3.9+
- pip or poetry
- Git

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
```



### 2. Set up Python environment

```bash

# Create virtual environment
python -m venv .venv

# Activate virtual environment

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```



### 3. Install dependencies

```bash
pip install -r requirements.txt
```



### 4. Set up pre-commit hooks (optional but recommended)

```bash
pip install pre-commit
pre-commit install
```



This will automatically run checks before each commit.

## Running Tests

### Quick test run

```bash
python tests/run_tests.py
```



### Run specific test category

```bash
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py performance
```



### Generate coverage report

```bash
pytest tests/ --cov=emotional_os --cov=parser --cov=learning --cov-report=html

# Open htmlcov/index.html in browser to view coverage
```



### Run with more verbose output

```bash
pytest tests/ -vv
```



### Run specific test file

```bash
pytest tests/unit/test_signal_matching.py -v
```



## Pre-commit Hooks

### View available hooks

```bash
pre-commit run --all-files  # Run all checks
```



### Run specific hook

```bash
pre-commit run ruff --all-files
pre-commit run trailing-whitespace --all-files
```



### Run tests as a pre-commit hook

```bash

# Uncomment the pytest stage in .pre-commit-config.yaml to enable on commit

# Then manually run:
pre-commit run --hook-id pytest
```



## Code Quality

### Linting with Ruff

```bash
ruff check . --fix
```



### Format code

```bash
ruff format .
```



### Type checking with mypy (manual)

```bash
pre-commit run mypy --all-files
```



## Common Workflows

### Create a feature branch

```bash
git checkout -b feature/my-feature
```



### Commit changes

```bash

# Pre-commit hooks will run automatically if configured
git add .
git commit -m "feat: description of changes"
```



### Push to remote

```bash
git push origin feature/my-feature
```



### Create pull request

1. Go to GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR description
5. Submit

## Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- All pull requests

View results in GitHub Actions: https://github.com/taurinrobinson-wq/saoriverse-console/actions

## Troubleshooting

### Virtual environment not activating

```bash

# Make sure you're in the project root
cd /path/to/saoriverse-console

# Try with explicit path
source /path/to/.venv/bin/activate
```



### Tests failing with import errors

```bash

# Ensure all dependencies are installed
pip install -r requirements.txt

# Reinstall in case of issues
pip install --force-reinstall -r requirements.txt
```



### Pre-commit hooks not running

```bash

# Reinstall hooks
pre-commit install --install-hooks
```



### Coverage report not generating

```bash

# Install coverage tools
pip install pytest-cov

# Generate manually
pytest tests/ --cov=emotional_os --cov-report=html
```



## Questions?

- Check the [main README.md](README.md)
- Read the [test suite guide](tests/README.md)
- Review [existing issues](https://github.com/taurinrobinson-wq/saoriverse-console/issues)
