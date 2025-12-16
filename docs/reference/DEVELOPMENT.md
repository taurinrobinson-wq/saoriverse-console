# Development Setup Guide

## Prerequisites

- Python 3.9+
- pip or poetry
- Git

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
```text
```



### 2. Set up Python environment

```bash

# Create virtual environment
python -m venv .venv

# Activate virtual environment

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
```text
```



### 3. Install dependencies

```bash
```text
```



### 4. Set up pre-commit hooks (optional but recommended)

```bash
pip install pre-commit
```text
```



This will automatically run checks before each commit.

## Running Tests

### Quick test run

```bash
```text
```



### Run specific test category

```bash
python tests/run_tests.py unit
python tests/run_tests.py integration
```text
```



### Generate coverage report

```bash
pytest tests/ --cov=emotional_os --cov=parser --cov=learning --cov-report=html

```text
```



### Run with more verbose output

```bash
```text
```



### Run specific test file

```bash
```text
```



## Pre-commit Hooks

### View available hooks

```bash
```text
```



### Run specific hook

```bash
pre-commit run ruff --all-files
```text
```



### Run tests as a pre-commit hook

```bash

# Uncomment the pytest stage in .pre-commit-config.yaml to enable on commit

# Then manually run:
```text
```



## Code Quality

### Linting with Ruff

```bash
```text
```



### Format code

```bash
```text
```



### Type checking with mypy (manual)

```bash
```text
```



## Common Workflows

### Create a feature branch

```bash
```text
```



### Commit changes

```bash

# Pre-commit hooks will run automatically if configured
git add .
```text
```



### Push to remote

```bash
```text
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
```text
```



### Tests failing with import errors

```bash

# Ensure all dependencies are installed
pip install -r requirements.txt

# Reinstall in case of issues
```text
```



### Pre-commit hooks not running

```bash

# Reinstall hooks
```text
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
