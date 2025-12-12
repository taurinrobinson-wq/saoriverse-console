#!/bin/bash
# Automatic Git Commit & Push Script for Bash
# This script commits and pushes changes periodically
# Usage: bash scripts/auto-commit.sh [interval_minutes]

INTERVAL=${1:-30}  # Default 30 minutes
COMMIT_MESSAGE="auto: periodic commit and push"

echo "🔄 Starting automatic git commit & push service..."
echo "Interval: every $INTERVAL minutes"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    # Check for changes
    CHANGES=$(git status --short)
    
    if [ -n "$CHANGES" ]; then
        CHANGE_COUNT=$(echo "$CHANGES" | wc -l)
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] Found $CHANGE_COUNT modified file(s)"
        
        # Stage all changes
        git add -A
        echo "  ✓ Staged changes"
        
        # Commit with timestamp
        FULL_MESSAGE="$COMMIT_MESSAGE ($TIMESTAMP)"
        git commit -m "$FULL_MESSAGE"
        
        if [ $? -eq 0 ]; then
            echo "  ✓ Committed: $FULL_MESSAGE"
        else
            echo "  ⚠ Commit failed or nothing to commit"
        fi
        
        # Push
        git push origin main 2>&1 > /dev/null
        
        if [ $? -eq 0 ]; then
            echo "  ✓ Pushed to remote"
        else
            echo "  ⚠ Push failed (may require PR)"
        fi
    else
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] No changes to commit"
    fi
    
    echo "  Waiting $INTERVAL minutes until next check..."
    sleep $((INTERVAL * 60))
done
