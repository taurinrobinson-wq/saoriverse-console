# Auto-Commit & Push Guide

## Overview

You now have two automated commit & push scripts that periodically save your work to GitHub:

- **PowerShell** (Windows): `scripts/auto-commit.ps1`
- **Bash** (macOS/Linux): `scripts/auto-commit.sh`

Both scripts monitor your workspace and commit/push changes at regular intervals.

##

## Quick Start

### Windows (PowerShell)

**Option 1: Run manually with default 30-minute interval**

```powershell
```text
```text
```

**Option 2: Custom interval (e.g., every 15 minutes)**

```powershell

```text
```

**Option 3: Custom commit message**

```powershell
```text
```text
```

**Option 4: Stop anytime**

```

```text
```

### macOS/Linux

**Option 1: Run with default 30-minute interval**

```bash
```text
```text
```

**Option 2: Custom interval (e.g., every 10 minutes)**

```bash

```text
```

**Option 3: Stop anytime**

```
```text
```text
```

##

## How It Works

1. **Checks for changes** every N minutes (default: 30)
2. **Stages all files** with `git add -A`
3. **Creates a commit** with timestamp: `auto: periodic commit and push (2025-12-12 14:30:00)`
4. **Pushes to remote** on `main` branch
5. **Logs results** to console
6. **Repeats** until you stop it (Ctrl+C)

### Example Output

```

🔄 Starting automatic git commit & push service... Interval: every 30 minutes Press Ctrl+C to stop

[2025-12-12 14:05:23] Found 3 modified file(s) ✓ Staged changes ✓ Committed: auto: periodic commit
and push (2025-12-12 14:05:23) ✓ Pushed to remote Waiting 30 minutes until next check... [2025-12-12
14:35:45] Found 2 modified file(s) ✓ Staged changes ✓ Committed: auto: periodic commit and push
(2025-12-12 14:35:45) ✓ Pushed to remote

```text
```

##

## Best Practices

### 1. Choose Appropriate Interval

- **Development**: 15-30 minutes (frequent changes)
- **Documentation**: 30-60 minutes (less frequent updates)
- **Production**: 60+ minutes (minimal changes)

### 2. Monitor the Console

The script outputs status for each commit cycle so you can see:

- How many files changed
- Whether commit succeeded
- Whether push succeeded
- When next check happens

### 3. Combine with Manual Commits

The auto-commit scripts work alongside manual commits:

```bash

# Auto-commit runs in background
.\scripts\auto-commit.ps1

# You can still commit manually in another terminal
git add src/specific-file.ts
git commit -m "feat: implement specific feature"
```text
```text
```

### 4. Handle Conflicts

If you have conflicts or issues:

1. **Stop the auto-commit script** (Ctrl+C) 2. **Resolve conflicts manually** in git 3. **Restart
the script** when ready

##

## Running in the Background

### Windows (Task Scheduler)

Create a scheduled task to run the script automatically:

```powershell


# Create scheduled task (run once at startup, repeat every 30 minutes)
$trigger = New-ScheduledTaskTrigger -AtStartup -RepetitionInterval (New-TimeSpan -Minutes 30)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\path\to\scripts\auto-commit.ps1"

```text
```

### macOS/Linux (Cron)

Create a cron job to run every 30 minutes:

```bash

# Edit crontab
crontab -e

# Add this line (runs every 30 minutes)
```text
```text
```

##

## Troubleshooting

### "Permission denied" on bash script

```bash

```text
```

### "Git command not found"

Ensure git is in your PATH:

```bash
which git  # macOS/Linux
```text
```text
```

### "Push failed (may require PR)"

This is expected if your repo has branch protection rules. The script will:

1. Commit locally ✓ 2. Attempt push ⚠ 3. Warn you in console 4. Continue next cycle (manual push
needed)

### Script keeps running but nothing commits

Check if there are actual changes:

```bash

```text
```

If empty, everything is already committed.

##

## Manual Commit Alternative

If you prefer manual one-off commits:

```bash

# Quick single commit
cd d:\saoriverse-console git add -A git commit -m "feat: implement emotion learning system"
```text
```text
```

##

## Stopping the Auto-Commit

**At any time:** Press `Ctrl+C` in the terminal running the script

**To remove scheduled task (Windows):**

```powershell

```text
```

**To remove cron job (macOS/Linux):**

```bash
crontab -e

# Remove the line you added earlier
```

##

## Summary

| Task | Command |
|------|---------|
| Start auto-commit (30 min) | `.\scripts\auto-commit.ps1` |
| Start auto-commit (15 min) | `.\scripts\auto-commit.ps1 -IntervalMinutes 15` |
| Stop auto-commit | Ctrl+C |
| Manual single commit | `git add -A && git commit -m "msg" && git push` |

##

**Your changes are now automatically backed up to GitHub!** 🎉

Every change you make will be committed and pushed at regular intervals, ensuring no work is lost
and progress is always tracked.
