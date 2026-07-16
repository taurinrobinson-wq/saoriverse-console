#!/bin/bash

mkdir -p repo_index

ls -1A > repo_index/root_files.txt
tree -d > repo_index/folder_structure.txt 2>/dev/null || find . -type d -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/.pytest_cache/*' 2>/dev/null | sort > repo_index/folder_structure.txt
tree -a > repo_index/full_index.txt 2>/dev/null || find . -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/.pytest_cache/*' 2>/dev/null | sort > repo_index/full_index.txt
