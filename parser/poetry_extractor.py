"""
Extract and organize poetry from Project Gutenberg.
Enriches emotional responses with poetic language.

Uses gutendex API (Project Gutenberg catalog):
https://gutendex.com/
"""

from parser.nrc_lexicon_loader import nrc
import json
import os
import sys
import re
from collections import defaultdict
from pathlib import Path

import requests
import concurrent.futures

# Handle imports properly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PoetryExtractor:
    """Extract and organize poetry by emotional themes."""

    # Well-known poetry book IDs from Project Gutenberg
    POETRY_IDS = [
        1342,  # Emily Dickinson - Complete Poems
        1661,  # Sherlock Holmes stories (some verse)
        4850,  # William Wordsworth - Complete Poetical Works
        21379,  # William Blake - Complete Poetry
        6787,  # John Keats - Complete Poetical Works
        51013,  # Robert Frost - Poetry collection
        1545,  # Edgar Allan Poe - The Raven and Other Poems
        28421,  # Walt Whitman - Leaves of Grass
    ]

    def __init__(self, output_dir: str = "data/poetry"):
        """Initialize poetry extractor."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.poetry_by_emotion = defaultdict(list)
        self.all_poems = []

    def download_project_gutenberg_book(self, book_id: int) -> str:
        """
        Download a book from Project Gutenberg.

        Gutendex provides free access to Project Gutenberg catalog.
        """
        try:
            print(f"📖 Downloading Project Gutenberg book #{book_id}...")

            # Get book metadata from Gutendex
            api_url = f"https://gutendex.com/books/{book_id}"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Find the text format URL
            formats = data.get('formats', {})
            text_url = formats.get('text/plain')

            if not text_url:
                print(f"  ⚠️ No text format available for book #{book_id}")
                return ""

            # Download the actual book text
            print(f"  Fetching text from {text_url}...")
            text_response = requests.get(text_url, timeout=30)
            text_response.raise_for_status()

            return text_response.text

        except Exception as e:
            print(f"  ⚠️ Error downloading book #{book_id}: {e}")
            return ""

    def extract_poems(self, text: str, book_id: int) -> list:
        """
        Extract individual poems from text.
        Split by blank lines and heuristics.
        """
        poems = []

        # Simple extraction: split by double newlines (poem breaks)
        sections = text.split('\n\n')

        current_poem = []
        for section in sections:
            section = section.strip()

            # Skip very short sections and Project Gutenberg headers
            if len(section) < 50:
                continue

            if 'Project Gutenberg' in section or '***' in section:
                continue

            # Count lines to identify poems (poems are typically 4-200 lines)
            lines = section.split('\n')
            if 4 <= len(lines) <= 100:
                current_poem.append(section)

                # Group 1-3 stanzas together as a poem
                if len(current_poem) >= 1:
                    poem_text = '\n\n'.join(current_poem)
                    if len(poem_text) > 100:
                        poems.append({
                            'text': poem_text,
                            'book_id': book_id,
                            'lines': len(lines)
                        })
                        current_poem = []

        return poems

    def extract_text_chunks(self, text: str, book_id: int, chunk_lines: int = 200, overlap_lines: int = 20) -> list:
        """
        Split a long text into overlapping chunks by lines. Returns list of chunk dicts:
        {'text': chunk_text, 'book_id': book_id, 'lines': n}
        """
        lines = text.splitlines()
        if not lines:
            return []

        chunks = []
        start = 0
        total_lines = len(lines)
        while start < total_lines:
            end = min(start + chunk_lines, total_lines)
            chunk_lines_list = lines[start:end]
            chunk_text = '\n'.join(chunk_lines_list).strip()
            if chunk_text and len(chunk_lines_list) >= 4:
                chunks.append(
                    {'text': chunk_text, 'book_id': book_id, 'lines': len(chunk_lines_list)})

            # advance by chunk_lines - overlap_lines
            if end >= total_lines:
                break
            start = end - overlap_lines

        return chunks

    def _get_nlp(self):
        if not hasattr(self, '_nlp') or self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
            except Exception:
                # If model missing, attempt to load and let exception surface on use
                self._nlp = None
        return self._nlp

    def _is_proper_noun_phrase(self, span) -> bool:
        for tok in span:
            if tok.pos_ == "PROPN":
                return True
        return False

    def extract_affective_phrases(self, text: str, top_n: int = 30):
        """Extract candidate affective phrases from text with NRC scoring.

        Returns list of tuples: (phrase_text, score, emotions_dict)
        """
        nlp = self._get_nlp()
        if nlp is None:
            raise RuntimeError(
                "spaCy model not available for phrase extraction")

        doc = nlp(text)
        candidates = []

        for sent in doc.sents:
            sent_text = sent.text.strip()
            if not sent_text:
                continue
            try:
                sent_emotions = nrc.analyze_text(sent_text) or {}
                sent_strength = sum(sent_emotions.values())
            except Exception:
                sent_emotions = {}
                sent_strength = 0

            for chunk in sent.noun_chunks:
                phrase = chunk.text.strip()
                if len(phrase) < 3 or len(phrase) > 120:
                    continue
                if self._is_proper_noun_phrase(chunk):
                    continue

                try:
                    phrase_emotions = nrc.analyze_text(phrase) or {}
                except Exception:
                    phrase_emotions = {}

                phrase_strength = sum(phrase_emotions.values())

                score = (phrase_strength * 2.0) + (sent_strength * 0.5)
                for tok in chunk:
                    if tok.pos_ == "ADJ":
                        score += 0.5

                if phrase_strength > 0 or sent_strength > 0:
                    candidates.append((phrase, float(score), phrase_emotions))

        # deduplicate, keep max score
        best = {}
        for phrase, score, em in candidates:
            key = phrase.strip().lower()
            if not key:
                continue
            if key not in best or score > best[key][0]:
                best[key] = (score, phrase, em)

        deduped = [(v[1], v[0], v[2]) for v in best.values()]
        deduped.sort(key=lambda x: x[1], reverse=True)
        return deduped[:top_n]

    def analyze_poem_emotion(self, poem_text: str) -> dict:
        """Analyze emotional content of a poem."""
        emotions = nrc.analyze_text(poem_text)

        # Calculate dominant emotion
        if emotions:
            dominant = max(emotions.items(), key=lambda x: x[1])
            return {
                'emotions': emotions,
                'dominant': dominant[0],
                'strength': dominant[1]
            }
        return {'emotions': {}, 'dominant': None, 'strength': 0}

    def build_poetry_database(self, use_cache: bool = True, source: str = "gutenberg") -> dict:
        """
        Build complete poetry database from Project Gutenberg.

        Structure:
        {
            'emotion_name': [
                {
                    'text': 'poem text...',
                    'book_id': 1342,
                    'strength': 5,
                    'lines': 20
                },
                ...
            ]
        }
        """
        cache_path = self.output_dir / (f"poetry_database_{source}.json")

        # Use cached database if available
        if use_cache and cache_path.exists():
            print("📚 Loading cached poetry database...")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        print("📚 Building poetry database...\n")

        # Two supported sources: 'gutenberg' (default POETRY_IDS list) and 'gutenberg_md' (markdown manifest)
        poetry_db = defaultdict(list)
        total_poems = 0

        if source == "gutenberg":
            for book_id in self.POETRY_IDS:
                # Download book
                text = self.download_project_gutenberg_book(book_id)
                if not text:
                    continue

                # Extract poems
                poems = self.extract_poems(text, book_id)
                print(f"  Found {len(poems)} poems in book #{book_id}")

                # Analyze each poem
                for poem in poems:
                    analysis = self.analyze_poem_emotion(poem['text'])

                    if analysis['dominant']:
                        poem_entry = {
                            'text': poem['text'][:500],  # First 500 chars
                            'book_id': book_id,
                            'lines': poem['lines'],
                            'strength': analysis['strength'],
                            'emotions': analysis['emotions']
                        }

                        poetry_db[analysis['dominant']].append(poem_entry)
                        total_poems += 1

                # Limit total poems for reasonable database size
                if total_poems > 500:
                    break

        elif source == "gutenberg_md":
            md_path = Path("data/poetry/classic_literature.md")
            if not md_path.exists():
                print(
                    f"⚠️ Markdown file for Gutenberg links not found: {md_path}")
                return {}

            text = md_path.read_text(encoding="utf-8")
            # find all URLs
            urls = re.findall(r"https?://[^\s)]+", text)
            ids = []
            for u in urls:
                # try to extract /ebooks/ID
                m = re.search(r"/ebooks/(\d+)", u)
                if m:
                    ids.append(int(m.group(1)))
                    continue
                # try gutendex id pattern or numeric in url
                m2 = re.search(r"(\d{3,6})", u)
                if m2:
                    ids.append(int(m2.group(1)))

            ids = [i for i in ids if i]
            ids = sorted(set(ids))

            print(
                f"📚 Found {len(ids)} Gutenberg IDs in markdown; building database from them...")

            # Per-book processing with timeout to avoid hangs on slow downloads or heavy NLP
            # seconds per book (including download + analysis)
            book_timeout = 60

            def _process_book(book_id: int):
                """Download and process a single book; return list of (dominant, entry) tuples."""
                entries = []
                text = self.download_project_gutenberg_book(book_id)
                if not text:
                    return entries

                poems = self.extract_poems(text, book_id)
                # If poems were found, analyze them
                if poems:
                    for poem in poems:
                        analysis = self.analyze_poem_emotion(poem['text'])
                        if analysis.get('dominant'):
                            poem_entry = {
                                'text': poem['text'][:500],
                                'book_id': book_id,
                                'lines': poem['lines'],
                                'strength': analysis['strength'],
                                'emotions': analysis['emotions']
                            }
                            entries.append((analysis['dominant'], poem_entry))
                    return entries

                # No poems found; chunk and extract affective phrases
                chunks = self.extract_text_chunks(
                    text, book_id, chunk_lines=200, overlap_lines=20)
                for chunk in chunks:
                    try:
                        phrases = self.extract_affective_phrases(
                            chunk['text'], top_n=20)
                    except Exception:
                        phrases = []

                    for phrase_text, score, phrase_emotions in phrases:
                        if not phrase_emotions:
                            continue
                        dominant = max(phrase_emotions.items(),
                                       key=lambda x: x[1])[0]
                        entry = {
                            'text': phrase_text,
                            'book_id': book_id,
                            'lines': chunk.get('lines', 0),
                            'strength': score,
                            'emotions': phrase_emotions
                        }
                        entries.append((dominant, entry))

                    # keep per-book work reasonable
                    if len(entries) > 2000:
                        break

                return entries

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                for book_id in ids:
                    print(
                        f"⏳ Submitting book #{book_id} for processing (timeout {book_timeout}s)")
                    future = executor.submit(_process_book, book_id)
                    try:
                        results = future.result(timeout=book_timeout)
                    except concurrent.futures.TimeoutError:
                        print(
                            f"  ⚠️ Book #{book_id} processing timed out after {book_timeout}s; skipping")
                        continue
                    except Exception as e:
                        print(f"  ⚠️ Error processing book #{book_id}: {e}")
                        continue

                    print(
                        f"  Processed book #{book_id}: extracted {len(results)} entries")
                    for dominant, entry in results:
                        poetry_db[dominant].append(entry)
                        total_poems += 1

                    # global cap to keep database reasonable
                    if total_poems > 2000:
                        break

        else:
            print(f"⚠️ Unknown source '{source}' requested")
            return {}

        print(
            f"\n✓ Built poetry database: {total_poems} poems across {len(poetry_db)} emotions")

        # Convert defaultdict to regular dict and save
        poetry_db_regular = dict(poetry_db)

        # Save to JSON
        print(f"💾 Saving to {cache_path}...")
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(poetry_db_regular, f, indent=2, ensure_ascii=False)

        return poetry_db_regular

    def get_poem_for_emotion(self, emotion: str) -> str:
        """
        Get a random poem snippet for an emotion.
        """
        self.poetry_db = self.build_poetry_database()

        if emotion in self.poetry_db and self.poetry_db[emotion]:
            # Return a random poem for this emotion
            import random
            poem_entry = random.choice(self.poetry_db[emotion])
            return poem_entry['text']

        return ""


# Singleton instance
poetry = None


def load_poetry_database():
    """Load poetry database at startup."""
    global poetry
    poetry = PoetryExtractor()
    return poetry.build_poetry_database(use_cache=True)


if __name__ == "__main__":
    # Test
    print("\n🧪 Testing Poetry Extractor\n")

    extractor = PoetryExtractor()

    # Build database
    db = extractor.build_poetry_database(use_cache=False)

    # Show stats
    print("\n📊 Poetry Database Stats:")
    for emotion, poems in db.items():
        print(f"  {emotion}: {len(poems)} poems")

    # Test retrieval
    print("\n🎭 Sample Poems by Emotion:")
    for emotion in ['joy', 'sadness', 'love', 'fear']:
        poem = extractor.get_poem_for_emotion(emotion)
        if poem:
            print(f"\n{emotion.upper()}:")
            print(f"  {poem[:200]}...")
