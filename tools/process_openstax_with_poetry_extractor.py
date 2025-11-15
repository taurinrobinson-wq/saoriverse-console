#!/usr/bin/env python3
"""
Run the poetry signal extractor over cleaned OpenStax texts and produce CSV/JSON summaries.

Outputs:
 - data/processed_poetry_signals/openstax_signals.csv
 - data/processed_poetry_signals/openstax_signals_summary.json

This script is conservative: it runs extraction in chunks to avoid very long inputs
and safely skips files it cannot read or when the extractor isn't available.
"""

import csv
import json
import logging
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Ensure repo root is on sys.path so imports like `emotional_os` resolve
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def split_into_chunks(text: str, chunk_size: int = 500):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    words = 0
    for s in sentences:
        wc = len(s.split())
        if words + wc > chunk_size and current:
            chunks.append(' '.join(current))
            current = [s]
            words = wc
        else:
            current.append(s)
            words += wc
    if current:
        chunks.append(' '.join(current))
    return chunks


def find_cleaned_files(base_dir: Path):
    # match *_cleaned.txt under data/openstax/<slug>/
    return sorted(base_dir.rglob('*_cleaned.txt'))


def main():
    base = Path('data/openstax')
    out_dir = Path('data/processed_poetry_signals')
    out_dir.mkdir(parents=True, exist_ok=True)

    files = find_cleaned_files(base)
    if not files:
        logger.error(
            f"No cleaned OpenStax files found under {base}. Did you run the crawler?")
        return 1

    # Try to import the poetry extractor
    try:
        from emotional_os.learning.poetry_signal_extractor import get_poetry_extractor
    except Exception as e:
        logger.error(f"Failed to import poetry extractor: {e}")
        return 2

    extractor = get_poetry_extractor()

    csv_path = out_dir / 'openstax_signals.csv'
    summary_path = out_dir / 'openstax_signals_summary.json'

    # Prepare CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=[
                                'file', 'chunk_index', 'keyword', 'signal', 'confidence', 'source'])
        writer.writeheader()

        aggregate = defaultdict(Counter)
        total_files = 0

        for filepath in files:
            total_files += 1
            try:
                text = filepath.read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Skipping {filepath}: {e}")
                continue

            logger.info(f"Processing {filepath} ({len(text.split())} words)")
            chunks = split_into_chunks(text, chunk_size=500)

            for idx, chunk in enumerate(chunks, 1):
                try:
                    signals = extractor.extract_signals(chunk)
                except Exception as e:
                    logger.warning(
                        f"Extractor failed on chunk {idx} of {filepath}: {e}")
                    signals = []

                for sig in signals:
                    keyword = sig.get('keyword') or sig.get('name') or ''
                    name = sig.get('signal') or sig.get('name') or ''
                    confidence = sig.get('confidence', '')
                    source = sig.get('source', '')

                    writer.writerow({
                        'file': str(filepath),
                        'chunk_index': idx,
                        'keyword': keyword,
                        'signal': name,
                        'confidence': confidence,
                        'source': source,
                    })

                    aggregate[str(filepath)][name] += 1

    # Save summary
    summary = {
        'files_processed': total_files,
        'unique_files': len(aggregate),
        'per_file_counts': {f: dict(cnt) for f, cnt in aggregate.items()},
    }

    with open(summary_path, 'w', encoding='utf-8') as sf:
        json.dump(summary, sf, indent=2)

    logger.info(f"Wrote CSV: {csv_path}")
    logger.info(f"Wrote summary: {summary_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
