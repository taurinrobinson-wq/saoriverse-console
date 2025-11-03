#!/bin/bash
# -*- coding: utf-8 -*-
# Run Project Gutenberg poetry processing in background with logging

LOG_FILE="gutenberg_learning_$(date +%Y%m%d_%H%M%S).log"

echo "[$(date)] Starting Project Gutenberg poetry processing..."
echo "[$(date)] Logging to: $LOG_FILE"
echo ""

/Users/taurinrobinson/saoriverse-console/venv/bin/python gutenberg_fetcher.py >> "$LOG_FILE" 2>&1

echo ""
echo "[$(date)] Processing complete!"
echo "[$(date)] Results saved to: $LOG_FILE"
echo "[$(date)] Lexicon results: gutenberg_processing_results.json"
