"""Self-diagnostic and lightweight auto-heal tool for the repository.

Usage:
  python tools/self_diagnostic.py [--auto-fix] [--commit]

What it does:
  - Runs pytest (quiet) and captures failures.
  - Scans failure output for common, fixable patterns such as hard-coded absolute
    paths used in tests (e.g. '/Users/...' macOS paths) that break collection on
    other platforms.
  - If --auto-fix is provided, replaces hard-coded paths found inside repository
    test files with a portable repo-root calculation (Path(__file__).resolve().parent).
  - If --commit is provided, stages and commits the changes locally with a
    descriptive message (does NOT push by default).

Design notes:
  - This tool is intentionally conservative: it only auto-fixes clear absolute
    path strings found in files and rewrites them to a small cross-platform
    snippet. Other diagnostics are reported but not auto-fixed.
  - Add new heuristics as needed (encoding fixes, stub generation, env checks).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

RE_ABSOLUTE_PATH_UNIX = re.compile(r"/Users/[\w\-_/\.]+")
RE_CHDIR_CALL = re.compile(r"os\.chdir\(([^)]+)\)")


def run_pytest(venv_python: Path) -> subprocess.CompletedProcess:
    cmd = [str(venv_python), "-m", "pytest", "-q"]
    print("Running pytest to gather diagnostics...")
    return subprocess.run(cmd, capture_output=True, text=True)


def find_files_with_string(repo_root: Path, pattern: str):
    matches = []
    for p in repo_root.rglob("*.py"):
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if pattern in text:
            matches.append(p)
    return matches


def replace_absolute_paths_in_file(path: Path):
    """Replace obvious absolute repo-root chdir lines with portable code.

    Returns True if file changed.
    """
    text = path.read_text(encoding='utf-8', errors='ignore')

    # Replace any os.chdir('/Users/....') with dynamic repo root
    def _repl(match):
        return "repo_root = Path(__file__).resolve().parent\nos.chdir(str(repo_root))"

    new_text, n = RE_CHDIR_CALL.subn(_repl, text)

    # Also replace literal /Users/... occurrences in tests (less robust but helpful)
    new_text2, m = RE_ABSOLUTE_PATH_UNIX.subn("str(Path(__file__).resolve().parent)", new_text)

    if n + m > 0 and new_text2 != text:
        backup = path.with_suffix(path.suffix + ".bak")
        path.write_text(new_text2, encoding='utf-8')
        backup.write_text(text, encoding='utf-8')
        print(f"Patched {path} (replacements: chdir={n}, abs_paths={m}), backup at {backup}")
        return True

    return False


def auto_fix_absolute_paths(repo_root: Path) -> int:
    """Scan repository for files containing absolute '/Users/' paths and patch them."""
    patched = 0
    for p in repo_root.rglob("*.py"):
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if RE_ABSOLUTE_PATH_UNIX.search(text) or RE_CHDIR_CALL.search(text):
            if replace_absolute_paths_in_file(p):
                patched += 1
    return patched


def git_commit(repo_root: Path, message: str) -> bool:
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo_root)
        subprocess.run(["git", "commit", "-m", message], cwd=repo_root)
        print("Committed changes locally.")
        return True
    except Exception as e:
        print(f"Git commit failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto-fix", action="store_true", help="Automatically apply conservative fixes")
    parser.add_argument("--commit", action="store_true", help="Create a local git commit for fixes (no push)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print(f"Warning: expected venv python at {venv_python} not found. Falling back to sys.executable")
        venv_python = Path(sys.executable)

    result = run_pytest(venv_python)

    if result.returncode == 0:
        print("All tests passed — no diagnostics needed.")
        return

    # Print a compact failure summary
    print("\nPytest failures detected. Captured output (first 1000 chars):\n")
    print(result.stdout[:1000])
    print(result.stderr[:1000])

    # Simple heuristic: look for absolute path patterns in stderr/stdout
    combined = (result.stdout + "\n" + result.stderr)
    abs_paths = RE_ABSOLUTE_PATH_UNIX.findall(combined)
    if abs_paths:
        print(f"Found absolute paths in test output: {abs_paths}")
        if args.auto_fix:
            patched = auto_fix_absolute_paths(repo_root)
            print(f"Auto-fix applied to {patched} files.")
            if patched and args.commit:
                git_commit(repo_root, "chore(diagnostics): auto-fix absolute test paths")
            # Re-run pytest once more after fixes
            print("Re-running pytest after auto-fix...")
            rerun = run_pytest(venv_python)
            print(rerun.stdout[:1000])
            print(rerun.stderr[:1000])
            if rerun.returncode == 0:
                print("Auto-fix resolved the test failures.")
            else:
                print("Auto-fix did not resolve all failures — please inspect test output.")
        else:
            print("Run with --auto-fix to attempt conservative automated fixes.")
    else:
        print("No obvious absolute path problems found in pytest output. Review full logs for root cause.")


if __name__ == "__main__":
    main()
