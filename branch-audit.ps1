#!/usr/bin/env powershell
# Branch Audit - Analyze all branches for safety

Write-Host "============================================================"
Write-Host "BRANCH AUDIT REPORT"
Write-Host "============================================================"
Write-Host ""

# Get all local branches
$branches = @(git branch --format='%(refname:short)')
$safeToDelete = @()
$needsReview = @()

Write-Host "Analyzing $($branches.Count) branches..."
Write-Host ""

foreach ($branch in $branches) {
    # Get last commit info
    $log = git log -1 --format='%H%n%ci%n%s' $branch
    $lines = $log -split "`n"
    $hash = $lines[0].Substring(0, 7)
    $date = [DateTime]::Parse($lines[1])
    $msg = $lines[2]
    $daysOld = [Math]::Floor(((Get-Date) - $date).TotalDays)
    
    # Commits ahead
    $ahead = @(git log main..$branch --oneline 2>$null)
    
    Write-Host "[$branch]"
    Write-Host "  Commit: $hash - $msg"
    Write-Host "  Days old: $daysOld, Commits ahead: $($ahead.Count)"
    
    # Categorize
    if ($daysOld -gt 180 -or $ahead.Count -eq 0) {
        $safeToDelete += $branch
        Write-Host "  SAFE TO DELETE"
    } else {
        $needsReview += $branch  
        Write-Host "  REVIEW NEEDED"
    }
    Write-Host ""
}

Write-Host "============================================================"
Write-Host "SUMMARY"
Write-Host "============================================================"
Write-Host ""
Write-Host "Safe to delete: $($safeToDelete.Count)"
$safeToDelete | ForEach-Object { Write-Host "  - $_" }
Write-Host ""
Write-Host "Needs review: $($needsReview.Count)"
$needsReview | ForEach-Object { Write-Host "  - $_" }
Write-Host ""

if ($safeToDelete.Count -gt 0) {
    Write-Host "============================================================"
    Write-Host "TO DELETE ALL SAFE BRANCHES:"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host ($safeToDelete -join " " | ForEach-Object { "git branch -D $_" })
    Write-Host ""
}
