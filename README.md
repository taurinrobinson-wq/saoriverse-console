# Saoriverse Console

Minimal project README. For developer-oriented configuration details, see the docs.

➡️ See [processing_modes.md](./docs/processing_modes.md) for details on local, hybrid, and premium modes.

Quickstart

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

### 🎵 SoundFont Setup

ToneCore requires a valid SF2 soundfont (for example, `FluidR3_GM.sf2`) for MIDI rendering.

By default, the app looks for `Offshoots/ToneCore/sf2/FluidR3_GM.sf2` in the project tree. If missing
or invalid, the app will attempt to download a fallback soundfont automatically and cache it locally.

You can customize the download source by setting:

```bash
export TONECORE_SF2_URL="https://your.cdn.com/FluidR3_GM.sf2"
```

For integrity validation, you may optionally set the expected SHA256 checksum:

```bash
export TONECORE_SF2_SHA256="your_expected_checksum"
```

If the downloaded file does not match the checksum, the app will discard it and log a warning.
