## Development

This file contains a few developer-facing notes for contributors working on the repository.

### Workflow Linting

All GitHub Actions workflows are validated automatically in CI using `actionlint`.

- **CI version:** The CI runs `actionlint` v1.6.26 on every push and pull request.
- **Failure behavior:** If any issues are found, the `lint-actions` job will fail and prevent the `tests` job from running until the workflow YAML is fixed.

### Running locally

You can run the same linter before committing to catch issues early:

```bash
./tools/actionlint/actionlint .github/workflows/*.yml
```



Running the command above mirrors what CI runs and helps ensure consistent workflow quality.

If you prefer using a system package or a different release of `actionlint`, make sure to run the same (or a compatible) version as the CI job to avoid false positives/negatives.
