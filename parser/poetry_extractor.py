"""
Extract and organize poetry from Project Gutenberg.
Enriches emotional responses with poetic language.

Uses gutendex API (Project Gutenberg catalog):
https://gutendex.com/
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import requests

# Handle imports properly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser.nrc_lexicon_loader import nrc


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
            formats = data.get("formats", {})
            text_url = formats.get("text/plain")

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
        sections = text.split("\n\n")

        current_poem = []
        for section in sections:
            section = section.strip()

            # Skip very short sections and Project Gutenberg headers
            if len(section) < 50:
                continue

            if "Project Gutenberg" in section or "***" in section:
                continue

            # Count lines to identify poems (poems are typically 4-200 lines)
            lines = section.split("\n")
            if 4 <= len(lines) <= 100:
                current_poem.append(section)

                # Group 1-3 stanzas together as a poem
                if len(current_poem) >= 1:
                    poem_text = "\n\n".join(current_poem)
                    if len(poem_text) > 100:
                        poems.append({"text": poem_text, "book_id": book_id, "lines": len(lines)})
                        current_poem = []

        return poems

    def analyze_poem_emotion(self, poem_text: str) -> dict:
        """Analyze emotional content of a poem."""
        emotions = nrc.analyze_text(poem_text)

        # Calculate dominant emotion
        if emotions:
            dominant = max(emotions.items(), key=lambda x: x[1])
            return {"emotions": emotions, "dominant": dominant[0], "strength": dominant[1]}
        return {"emotions": {}, "dominant": None, "strength": 0}

    def build_poetry_database(self, use_cache: bool = True) -> dict:
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
        cache_path = self.output_dir / "poetry_database.json"

        # Use cached database if available
        if use_cache and cache_path.exists():
            print("📚 Loading cached poetry database...")
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        print("📚 Building poetry database from Project Gutenberg...\n")

        poetry_db = defaultdict(list)
        total_poems = 0

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
                analysis = self.analyze_poem_emotion(poem["text"])

                if analysis["dominant"]:
                    poem_entry = {
                        "text": poem["text"][:500],  # First 500 chars
                        "book_id": book_id,
                        "lines": poem["lines"],
                        "strength": analysis["strength"],
                        "emotions": analysis["emotions"],
                    }

                    poetry_db[analysis["dominant"]].append(poem_entry)
                    total_poems += 1

            # Limit total poems for reasonable database size
            if total_poems > 500:
                break

        print(f"\n✓ Built poetry database: {total_poems} poems across {len(poetry_db)} emotions")

        # Convert defaultdict to regular dict and save
        poetry_db_regular = dict(poetry_db)

        # Save to JSON
        print(f"💾 Saving to {cache_path}...")
        with open(cache_path, "w", encoding="utf-8") as f:
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
            return poem_entry["text"]

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
    for emotion in ["joy", "sadness", "love", "fear"]:
        poem = extractor.get_poem_for_emotion(emotion)
        if poem:
            print(f"\n{emotion.upper()}:")
            print(f"  {poem[:200]}...")
