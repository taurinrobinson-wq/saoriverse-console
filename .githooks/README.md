This folder contains recommended repository hooks.

## Usage

To enable the hooks locally for your clone, run:
```text
```
git config core.hooksPath .githooks
```



The repository includes a `pre-commit` hook that rejects staged files larger than 5 MB.

Note: Git does not automatically enable hooks from the repository for security reasons — each contributor must opt-in by setting `core.hooksPath` or by installing hooks through an automation script.
