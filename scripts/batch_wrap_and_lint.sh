#!/bin/bash
# Comprehensive MD013 wrapper + lint pass

echo "Phase 1: Wrapping top problematic files..."
python3 scripts/md013_wrap.py --max 100 \
  velinor/markdowngameinstructions/Velinor_story_lines.md \
  velinor/markdowngameinstructions/Velinor_improvements_full.md \
  velinor/markdowngameinstructions/Velinor_improvements.md \
  tools/actionlint/docs/checks.md \
  velinor/markdowngameinstructions/player_arrival-first_encounters.md \
  tools/actionlint/docs/usage.md \
  velinor/markdowngameinstructions/MARKETPLACE_NPC_ROSTER.md \
  docs/GLYPH_MESSAGE_FLOW.md \
  velinor/markdowngameinstructions/additional_game_dev.md \
  docs/guides/phase_modulator.md \
  velinor/markdowngameinstructions/EXECUTIVE_SUMMARY_AND_QUICKSTART.md \
  data/firstperson_improvements.md \
  tools/actionlint/README.md \
  velinor/markdowngameinstructions/VELINOR_SAORI_FINAL_ARC.md \
  velinor/markdowngameinstructions/TONE_STAT_SYSTEM.md \
  deploy/README.md \
  docs/guides/GLYPH_SYSTEM_AUDIT.md \
  docs/SYSTEM_TEST_RESULTS_COMPLETE.md 2>&1

echo ""
echo "Phase 2: Running all remaining files through wrapper..."
find . -name "*.md" -type f ! -path "*/node_modules/*" ! -path "*/.venv/*" ! -path "*/archive/*" ! -path "*/MessageUIOverlayPrototype/*" ! -path "*/firstperson/*" ! -path "*/velinor-web/*" | xargs python3 scripts/md013_wrap.py --max 100 2>&1 | grep Wrapped | wc -l

echo ""
echo "Phase 3: Checking final error count..."
npx markdownlint-cli@0.28.1 "**/*.md" 2>&1 | grep -o "MD[0-9]*" | sort | uniq -c | sort -rn | head -10
