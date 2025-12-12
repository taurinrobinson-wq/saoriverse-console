# Automatic Git Commit & Push Script for PowerShell
# This script commits and pushes changes periodically
# Usage: .\scripts\auto-commit.ps1

param(
    [int]$IntervalMinutes = 30,
    [string]$CommitMessage = "auto: periodic commit and push"
)

Write-Host "🔄 Starting automatic git commit & push service..." -ForegroundColor Cyan
Write-Host "Interval: every $IntervalMinutes minutes" -ForegroundColor Yellow
Write-Host "Type Ctrl+C to stop`n" -ForegroundColor Gray

$repoPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoPath

while ($true) {
    try {
        # Check for changes
        $status = git status --short
        
        if ($status) {
            $changeCount = ($status | Measure-Object -Line).Lines
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Found $changeCount modified file(s)" -ForegroundColor Yellow
            
            # Stage all changes
            git add -A
            Write-Host "  ✓ Staged changes" -ForegroundColor Green
            
            # Create timestamped commit message
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $fullMessage = "$CommitMessage ($timestamp)"
            
            # Commit
            git commit -m $fullMessage
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Committed: $fullMessage" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ Commit failed or nothing to commit" -ForegroundColor Yellow
            }
            
            # Push
            git push origin main 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Pushed to remote" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ Push failed (may require PR)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] No changes to commit" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  ✗ Error: $_" -ForegroundColor Red
    }
    
    # Wait for next interval
    Write-Host "  Waiting $IntervalMinutes minutes until next check..." -ForegroundColor Gray
    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
