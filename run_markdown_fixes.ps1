# Run markdown fixes: heading style, blank lines, line wrapping

$ErrorActionPreference = "SilentlyContinue"

# Get all .md files excluding certain directories
$files = @(Get-ChildItem -Path "." -Recurse -Filter "*.md" -Exclude archive,node_modules,firstperson | 
    Where-Object { 
        $_.FullName -notmatch "velinor-web|MessageUIOverlayPrototype|\.git" 
    }).FullName

Write-Host "Found $($files.Count) markdown files to process"

# Phase 1: Fix heading style (MD003)
Write-Host "`n=== Phase 1: Fixing MD003 (heading style) ==="
$fixed_count = 0
foreach ($file in $files) {
    $result = & python scripts/fix_heading_style.py $file 2>&1
    if ($result -match "Fixed:") {
        $fixed_count++
    }
}
Write-Host "Fixed $fixed_count files with MD003 issues"

# Phase 2: Fix blank lines and spacing (MD022, MD032, MD012)
Write-Host "`n=== Phase 2: Fixing MD022/032/012 (blank lines & spacing) ==="
$result = & python scripts/markdown_fixer.py $files 2>&1
Write-Host $result

# Phase 3: Fix line length (MD013) - wrap to 100 chars
Write-Host "`n=== Phase 3: Fixing MD013 (line length) ==="
$wrap_count = 0
foreach ($file in $files) {
    $result = & python scripts/md013_wrap.py --max 100 $file 2>&1
    if ($result -match "Wrapped") {
        $wrap_count++
    }
}
Write-Host "Wrapped $wrap_count files to 100 char limit"

Write-Host "`nAll fixes complete!"
