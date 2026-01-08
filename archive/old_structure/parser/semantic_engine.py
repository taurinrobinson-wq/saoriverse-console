"""
Semantic engine for emotional text analysis.
Uses spaCy for entity extraction, tokenization, and semantic relationships.
"""

from typing import Dict, List, Tuple

import spacy


class SemanticEngine:
    """Local semantic analysis without external APIs."""

    def __init__(self):
        """Initialize spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.loaded = True
            print("✓ spaCy NLP model loaded (en_core_web_sm)")
        except OSError:
            print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.loaded = False

    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities from text."""
        if not self.loaded:
            return []

        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def get_noun_chunks(self, text: str) -> List[str]:
        """Extract noun chunks (key noun phrases)."""
        if not self.loaded:
            return []

        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if not self.loaded:
            return text.lower().split()

        doc = self.nlp(text)
        return [token.text for token in doc]

    def get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """Get part-of-speech tags."""
        if not self.loaded:
            return []

        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words (0-1)."""
        if not self.loaded:
            return 0.0

        try:
            doc1 = self.nlp(word1)
            doc2 = self.nlp(word2)
            return doc1.similarity(doc2)
        except:
            return 0.0

    def find_similar_words(self, word: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Find semantically similar words from text (limited)."""
        # Note: This is a simplified version. Full implementation would need Word2Vec.
        # For now, we use spaCy's vector similarity for words that have vectors.

        if not self.loaded:
            return []

        similar_words = []
        common_words = [
            "happy",
            "sad",
            "angry",
            "fear",
            "love",
            "hate",
            "trust",
            "disgust",
            "joy",
            "sorrow",
            "peace",
            "chaos",
            "calm",
            "anxious",
            "grateful",
            "resentful",
        ]

        for other_word in common_words:
            sim = self.similarity(word, other_word)
            if sim > threshold and sim < 1.0:  # Exclude exact matches
                similar_words.append((other_word, sim))

        return sorted(similar_words, key=lambda x: x[1], reverse=True)

    def extract_adjectives(self, text: str) -> List[str]:
        """Extract adjectives (emotional descriptors)."""
        if not self.loaded:
            return []

        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADJ"]

    def extract_verbs(self, text: str) -> List[str]:
        """Extract verbs (actions)."""
        if not self.loaded:
            return []

        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "VERB"]

    def get_dependency_parse(self, text: str) -> List[Dict]:
        """Get syntactic dependencies."""
        if not self.loaded:
            return []

        doc = self.nlp(text)
        deps = []
        for token in doc:
            deps.append({"text": token.text, "pos": token.pos_, "dep": token.dep_, "head": token.head.text})
        return deps

    def analyze_emotional_language(self, text: str) -> Dict:
        """Comprehensive emotional language analysis."""
        return {
            "entities": self.extract_entities(text),
            "noun_chunks": self.get_noun_chunks(text),
            "adjectives": self.extract_adjectives(text),
            "verbs": self.extract_verbs(text),
            "pos_tags": self.get_pos_tags(text),
            "tokens": self.tokenize(text),
        }


# Singleton instance
semantic = SemanticEngine()

if __name__ == "__main__":
    # Test
    print("\n🧪 Testing Semantic Engine\n")

    test_text = "I am deeply sad and angry about what happened to my family"

    print(f"Input: '{test_text}'\n")

    # Test 1: Entities
    entities = semantic.extract_entities(test_text)
    print(f"1. Named Entities: {entities}")

    # Test 2: Noun chunks
    chunks = semantic.get_noun_chunks(test_text)
    print(f"2. Noun Chunks: {chunks}")

    # Test 3: Adjectives (emotional words)
    adjectives = semantic.extract_adjectives(test_text)
    print(f"3. Adjectives: {adjectives}")

    # Test 4: Verbs (actions)
    verbs = semantic.extract_verbs(test_text)
    print(f"4. Verbs: {verbs}")

    # Test 5: Similarity
    sim = semantic.similarity("sad", "grief")
    print(f"5. Similarity (sad vs grief): {sim:.2f}")

    # Test 6: Full analysis
    analysis = semantic.analyze_emotional_language(test_text)
    print("6. Full Analysis:")
    for key, value in analysis.items():
        print(f"   {key}: {value}")
