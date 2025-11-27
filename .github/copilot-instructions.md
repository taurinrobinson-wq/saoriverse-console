# Copilot Instructions for Saoriverse Console

This document provides instructions for GitHub Copilot when working in this repository.

## Project Overview

Saoriverse Console is a Python-based application that uses Streamlit for the web interface. It features glyph-based emotional response systems with support for local, hybrid, and premium processing modes.

## Tech Stack

- **Language**: Python 3.9+
- **Web Framework**: Streamlit
- **Testing**: pytest
- **Linting/Formatting**: Black, Ruff
- **Database**: Supabase (with local SQLite fallback)
- **Dependencies**: See `requirements.txt`

## Development Commands

Use the Makefile for common development tasks:

```bash
make env        # Copy .env.template to .env for local configuration
make install    # Create virtual environment and install dependencies
make test       # Run tests with pytest -q
make format     # Format code with Black and fix issues with Ruff
```

### Running Tests

```bash
pytest -q                    # Run all tests quietly
pytest tests/test_*.py       # Run specific test files
pytest -q --tb=short         # Run tests with short tracebacks
```

### Linting

- GitHub Actions workflows are validated with `actionlint`
- Python code is formatted with Black and checked with Ruff

```bash
black . && ruff check . --fix    # Format and lint Python code
./tools/actionlint/actionlint .github/workflows/*.yml   # Lint workflows
```

## Project Structure

```
├── .github/                    # GitHub configuration and workflows
│   └── workflows/              # CI/CD workflow definitions
├── config/                     # Application configuration
├── docs/                       # Documentation
├── emotional_os/               # Emotional processing modules
├── lexicons/                   # Glyph and emotion lexicons
├── parser/                     # Input parsing utilities
├── scripts/                    # Utility scripts
├── src/                        # Source code
│   └── ui/                     # UI components
├── supabase/                   # Supabase configuration
├── tests/                      # Test files
│   ├── fixtures/               # Test fixtures
│   ├── integration/            # Integration tests
│   ├── performance/            # Performance tests
│   └── unit/                   # Unit tests
└── tools/                      # Development tools
```

## Coding Conventions

### Python Style

- Follow PEP 8 guidelines
- Use Black for code formatting (default settings)
- Use Ruff for linting
- Use type hints where appropriate
- Write docstrings for public functions and classes

### Testing

- Write tests for new functionality
- Place tests in the `tests/` directory with `test_` prefix
- Use pytest fixtures from `tests/conftest.py`
- Integration tests go in `tests/integration/`
- Unit tests go in `tests/unit/`

### Commit Messages

- Use descriptive commit messages
- Use feature branches (e.g., `feat/glyph-scoring`, `fix/db-loader`)
- Open pull requests to `main` for review

## File Boundaries

### Do Not Modify

- `.env*` files containing secrets or credentials
- `.streamlit/secrets.toml`
- Database files (`*.db`, `*.sqlite3`)
- Large binary files or archives

### Do Not Commit

- Virtual environment directories (`.venv/`, `env/`, `venv/`)
- Cache directories (`__pycache__/`, `.pytest_cache/`)
- Build artifacts (`build/`, `dist/`, `*.egg-info/`)
- Log files (`*.log`, `logs/`)
- Node modules (`node_modules/`)

## Processing Modes

The application supports multiple processing modes. See `docs/processing_modes.md` for details:

- **Local mode**: Offline processing with SQLite
- **Hybrid mode**: Mixed local and cloud processing
- **Premium mode**: Full cloud processing with Supabase

## Security Guidelines

- Never commit secrets, API keys, or credentials to source code
- Use `.env.template` as a reference for required environment variables
- Keep sensitive configuration in `.env.local` or `.env.production` (gitignored)
- Follow the patterns in `.secret-allowlist` for any exceptions

## Additional Resources

- [Contributing Guidelines](/CONTRIBUTING.md)
- [Processing Modes Documentation](/docs/processing_modes.md)
- [Development Notes](/docs/DEVELOPMENT.md)
