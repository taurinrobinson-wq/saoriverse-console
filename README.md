# Saoriverse Console

Minimal project README. For developer-oriented configuration details, see the docs.

➡️ See [processing_modes.md](./docs/processing_modes.md) for details on local, hybrid, and premium modes.

Quickstart
---------

- Install project dependencies (see `requirements.txt`)
- Run tests: `pytest -q`

Bootstrap local env:

```bash
cp .env.template .env  # Load safe defaults for local-only mode
```

Git LFS
--------

This repository stores some large binary assets with Git LFS (soundfonts, database backups, and deploy binaries). On developer machines and in CI make sure Git LFS is installed and initialized before fetching/pushing large files.

Install (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y git-lfs
git lfs install
```

Fetch LFS objects for all refs:

```bash
git lfs fetch --all
git lfs checkout
```

If you added or updated large files locally, push objects to the remote by running:

```bash
git lfs push --all origin <branch>
```
