"""Download the NRC Emotion Lexicon into `data/lexicons/`.

Usage:
  python3 scripts/download_nrc_lexicon.py <URL>

Set `NRC_LEXICON_URL` environment variable to enable automatic download
from `main_v2.py` at startup.
"""
from pathlib import Path
import sys
import urllib.request
import shutil


def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix('.tmp')
    with urllib.request.urlopen(url, timeout=60) as resp, open(tmp, 'wb') as out:
        shutil.copyfileobj(resp, out)
    tmp.replace(dest)


def main():
    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        import os
        url = os.environ.get('NRC_LEXICON_URL')

    if not url:
        print('Usage: python3 scripts/download_nrc_lexicon.py <URL>')
        sys.exit(2)

    dest = Path('data/lexicons/nrc_emotion_lexicon.txt')
    try:
        print('Downloading NRC lexicon from', url)
        download(url, dest)
        print('Saved to', dest)
    except Exception as e:
        print('Download failed:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
