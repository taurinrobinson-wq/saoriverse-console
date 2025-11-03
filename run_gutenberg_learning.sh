#!/bin/bash
# -*- coding: utf-8 -*-
# Run Project Gutenberg poetry processing in background with logging to external drive

EXTERNAL_DRIVE="/Volumes/My Passport for Mac/saoriverse_data"
LOG_FILE="$EXTERNAL_DRIVE/gutenberg_learning_$(date +%Y%m%d_%H%M%S).log"

echo "[$(date)] Starting Project Gutenberg poetry processing..."
echo "[$(date)] Logging to: $LOG_FILE"
echo "[$(date)] Data directory: $EXTERNAL_DRIVE"
echo ""

/Users/taurinrobinson/saoriverse-console/venv/bin/python /Users/taurinrobinson/saoriverse-console/gutenberg_fetcher.py >> "$LOG_FILE" 2>&1

echo ""
echo "[$(date)] Processing complete!"
echo "[$(date)] Results saved to: $LOG_FILE"
echo "[$(date)] Lexicon results: $EXTERNAL_DRIVE/gutenberg_processing_results.json"
