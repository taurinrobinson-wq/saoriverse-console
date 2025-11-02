"""
Load NRC Emotion Lexicon for local emotional processing.
14,182 words mapped to 10 emotion categories + sentiment.

Data source: http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm
Free for research use.
"""

import os
from collections import defaultdict


class NRCLexicon:
    """Load and query the NRC Emotion Lexicon locally."""

    def __init__(self, filepath: str = "data/lexicons/nrc_emotion_lexicon.txt"):
        """
        Initialize NRC Lexicon loader.
        
        Format of lexicon file:
        word    emotion    association
        good    trust    1
        good    joy    1
        bad    sadness    1
        """
        self.word_emotions = defaultdict(list)
        self.emotion_words = defaultdict(list)
        self.loaded = False
        self.source = "bootstrap"

        # Try primary path first
        if os.path.exists(filepath):
            self._load_lexicon(filepath)
            self.source = "full"
        # Then try bootstrap lexicon
        else:
            bootstrap_path = "data/lexicons/nrc_emotion_lexicon_bootstrap.txt"
            if os.path.exists(bootstrap_path):
                self._load_lexicon(bootstrap_path)
                self.source = "bootstrap"
            else:
                print(f"⚠️ Neither {filepath} nor {bootstrap_path} found")

    def _load_lexicon(self, filepath: str):
        """Load lexicon from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if not lines:
                print(f"⚠️ Lexicon file is empty: {filepath}")
                return

            # Determine header - check if first line is header
            first_line_parts = lines[0].strip().split('\t')
            is_header = len(first_line_parts) >= 3 and first_line_parts[0].lower() == 'word'
            start_idx = 1 if is_header else 0

            loaded_count = 0
            for line in lines[start_idx:]:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    word = parts[0].lower()
                    emotion = parts[1].lower()
                    try:
                        association = int(parts[2])
                    except ValueError:
                        continue

                    if association == 1:
                        if emotion not in self.word_emotions[word]:
                            self.word_emotions[word].append(emotion)
                        if word not in self.emotion_words[emotion]:
                            self.emotion_words[emotion].append(word)
                        loaded_count += 1

            self.loaded = True
            word_count = len(self.word_emotions)
            emotion_count = len(self.emotion_words)
            print(f"✓ NRC Lexicon loaded: {word_count} words across {emotion_count} emotions ({self.source}) [{loaded_count} entries]")
        except Exception as e:
            print(f"⚠️ Error loading NRC lexicon: {e}")
            self.loaded = False

    def get_emotions(self, word: str) -> list:
        """Get emotions for a word."""
        return self.word_emotions.get(word.lower(), [])

    def get_words_for_emotion(self, emotion: str) -> list:
        """Get all words for an emotion."""
        return self.emotion_words.get(emotion, [])

    def analyze_text(self, text: str) -> dict:
        """Analyze text and return emotion frequencies."""
        words = text.lower().split()
        emotions = defaultdict(int)

        for word in words:
            word_clean = word.strip('.,!?;:\'"')
            word_emotions = self.get_emotions(word_clean)
            for emotion in word_emotions:
                emotions[emotion] += 1

        return dict(emotions)

    def get_all_emotions(self) -> list:
        """Get list of all emotion categories."""
        return list(self.emotion_words.keys())

    def to_dict(self) -> dict:
        """Export lexicon as dictionary."""
        return {
            "word_emotions": dict(self.word_emotions),
            "emotion_words": {k: list(v) for k, v in self.emotion_words.items()},
            "loaded": self.loaded,
            "source": self.source,
            "word_count": len(self.word_emotions),
            "emotion_count": len(self.emotion_words)
        }


# Singleton instance - load once at startup
nrc = NRCLexicon()

if __name__ == "__main__":
    # Test
    print("\n🧪 Testing NRC Lexicon Loader\n")

    # Test 1: Analyze text
    emotions = nrc.analyze_text("I feel happy and grateful for this moment")
    print("Test 1 - Text analysis:")
    print("  Input: 'I feel happy and grateful for this moment'")
    print(f"  Emotions: {emotions}\n")

    # Test 2: Get emotions for word
    word_emotions = nrc.get_emotions("happy")
    print("Test 2 - Word emotions:")
    print("  Word: 'happy'")
    print(f"  Emotions: {word_emotions}\n")

    # Test 3: Get all emotion categories
    all_emotions = nrc.get_all_emotions()
    print("Test 3 - All emotions:")
    print(f"  Categories: {all_emotions}\n")

    # Test 4: Status
    stats = nrc.to_dict()
    print("Test 4 - Lexicon Status:")
    print(f"  Loaded: {stats['loaded']}")
    print(f"  Source: {stats['source']}")
    print(f"  Words: {stats['word_count']}")
    print(f"  Emotions: {stats['emotion_count']}")
