"""CI smoke test for ToneCore pipeline

This script is intentionally small and has no external test deps.
It runs the two smoke commands used in development and ensures the
expected MIDI outputs are created. Intended to be run from CI.
"""
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'demo_output'
OUT_DIR.mkdir(exist_ok=True)


def run(cmd):
    print('>',' '.join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode != 0:
        print('Command failed:', cmd)
        sys.exit(res.returncode)


def assert_file(path: Path):
    if not path.exists():
        print('Missing expected file:', path)
        sys.exit(2)
    print('OK:', path)


def main():
    # 1) emotion-driven midi
    emotion_out = OUT_DIR / 'demo_joy.mid'
    run([sys.executable, 'scripts/tonecore_midi.py', '--emotion', 'joy', '--out', str(emotion_out)])
    assert_file(emotion_out)

    # 2) glyph cascade demo
    glyph_out = OUT_DIR / 'demo_chain.mid'
    run([sys.executable, 'scripts/glyph_cascade_demo.py', '--glyphs', '🌙', '💧', '🌞', '--out', str(glyph_out)])
    assert_file(glyph_out)

    print('\nSmoke tests passed')


if __name__ == '__main__':
    main()
