# Contributing

Thank you for contributing to this lineage-preserving system.

## Workflow

- Use feature branches (e.g., `feat/glyph-scoring`, `fix/db-loader`) for changes.
- Open pull requests to `main` for review and CI validation.
- All code must pass `make test` and respect `make format`.

## Setup

```bash
make env        # Load safe defaults
make install    # Set up environment
make test       # Run tests
make format     # Format code
```


## Processing Modes

See [processing_modes.md](./processing_modes.md) for details on local, hybrid, and premium modes.
