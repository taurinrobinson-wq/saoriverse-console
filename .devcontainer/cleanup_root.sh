#!/bin/bash

# Move markdown docs to docs/ if it exists, otherwise create it
mkdir -p docs
for f in *.md; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" docs/ 2>/dev/null || true
done

# Move text reports to reports/ if it exists, otherwise create it
mkdir -p reports
for f in *.txt; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" reports/ 2>/dev/null || true
done

# Move CSV data to data/ if it exists, otherwise create it
mkdir -p data
for f in *.csv; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" data/ 2>/dev/null || true
done

# Move Python scripts to scripts/ if it exists, otherwise create it
mkdir -p scripts
for f in *.py; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" scripts/ 2>/dev/null || true
done

# Move shell / batch / PowerShell scripts to scripts/
for f in *.sh *.ps1 *.cmd *.bat; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" scripts/ 2>/dev/null || true
done

# Move Docker / Compose / Nginx / Makefiles / configs to config/
mkdir -p config
for f in Dockerfile* docker-compose* nginx* Makefile* *.ini *.toml *.yaml *.yml *.conf; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" config/ 2>/dev/null || true
done

# Move media files to media/
mkdir -p media
for f in *.mid *.docx; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" media/ 2>/dev/null || true
done

# Move JSON config files to config/
for f in *.json; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" config/ 2>/dev/null || true
done

# Move patch files to patches/
mkdir -p patches
for f in *.patch; do
    [ -e "$f" ] && [ ! -d "$f" ] && mv "$f" patches/ 2>/dev/null || true
done
