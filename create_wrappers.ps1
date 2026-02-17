# create_wrappers.ps1
# Run from repo root (D:\saoriverse-console)
$base = "src\emotional_os\learning"
if (-not (Test-Path $base)) {
  Write-Error "Path $base not found. Run this from the repo root."
  exit 1
}

# Helper to write a file from here-string (overwrites)
function Write-File($path, $content) {
  $dir = Split-Path $path -Parent
  if (-not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
  }
  $content | Out-File -Encoding utf8 -FilePath $path -Force
  Write-Host "Wrote $path"
}

# Wrapper contents
$proto = @'
#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.proto_glyph_manager`."""
try:
    from emotional_os_learning.proto_glyph_manager import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.proto_glyph_manager; ensure src/emotional_os_learning is present"
    ) from exc
'@

$subordinate = @'
#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.subordinate_bot_responder`."""
try:
    from emotional_os_learning.subordinate_bot_responder import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.subordinate_bot_responder; ensure src/emotional_os_learning is present"
    ) from exc
'@

$dominant = @'
#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.dominant_bot_orchestrator`."""
try:
    from emotional_os_learning.dominant_bot_orchestrator import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.dominant_bot_orchestrator; ensure src/emotional_os_learning is present"
    ) from exc
'@

$glyph = @'
#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.glyph_synthesizer`."""
try:
    from emotional_os_learning.glyph_synthesizer import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.glyph_synthesizer; ensure src/emotional_os_learning is present"
    ) from exc
'@

$pipeline = @'
#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.learning_pipeline`."""
try:
    from emotional_os_learning.learning_pipeline import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.learning_pipeline; ensure src/emotional_os_learning is present"
    ) from exc
'@

# Write wrappers
Write-File "$base\proto_glyph_manager.py" $proto
Write-File "$base\subordinate_bot_responder.py" $subordinate
Write-File "$base\dominant_bot_orchestrator.py" $dominant
Write-File "$base\glyph_synthesizer.py" $glyph
Write-File "$base\learning_pipeline.py" $pipeline

# Append re-exports to __init__.py only if not already present
$initPath = "$base\__init__.py"
if (-not (Test-Path $initPath)) {
  New-Item -ItemType File -Path $initPath -Force | Out-Null
}
$linesToAdd = @(
  "from .proto_glyph_manager import *  # noqa: F401,F403",
  "from .subordinate_bot_responder import *  # noqa: F401,F403",
  "from .dominant_bot_orchestrator import *  # noqa: F401,F403",
  "from .glyph_synthesizer import *  # noqa: F401,F403",
  "from .learning_pipeline import *  # noqa: F401,F403"
)
foreach ($ln in $linesToAdd) {
  $exists = Get-Content $initPath -ErrorAction SilentlyContinue | Where-Object { $_ -eq $ln }
  if (-not $exists) {
    Add-Content -Path $initPath -Value $ln
    Write-Host "Appended to __init__.py: $ln"
  } else {
    Write-Host "Line already present in __init__.py: $ln"
  }
}

# Show results
Get-ChildItem $base\*.py | Select-Object Name,Length
git status --porcelain 2>$null | ForEach-Object { Write-Host "git status: $_" }
Write-Host "Done. If permissions errors occur, run PowerShell as Administrator and re-run this script."
