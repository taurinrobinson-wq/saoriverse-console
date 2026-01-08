#!/bin/sh
# Helper to enable the included repository hooks for this clone
set -e
git config core.hooksPath .githooks
echo "Enabled hooks: core.hooksPath set to .githooks"
