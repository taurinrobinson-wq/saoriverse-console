"""
Poetry Enrichment Engine - Maps poetry to emotional glyphs.
Blends NRC emotion analysis with beautiful poetic language.

Creates responses enriched with poetry and metaphor from the glyph collection.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from parser.nrc_lexicon_loader import nrc
from parser.poetry_database import PoetryDatabase


class PoetryEnrichment:
    """Enriches emotional responses with poetry and glyphs."""

    # Map emotions to glyph categories from the 292-glyph collection
    EMOTION_TO_GLYPHS = {
        'joy': ['✨', '🌟', '💫', '🎉', '🎊', '🌞', '🦋', '🌸', '🌺', '🌻'],
        'sadness': ['💔', '🌧️', '😢', '🍂', '🌙', '⛓️', '🖤', '😔'],
        'love': ['💕', '💖', '💗', '💝', '🌹', '✨', '💞', '👑'],
        'fear': ['😨', '😱', '⚡', '🌪️', '🔥', '👻', '⚫', '🌑'],
        'anger': ['🔴', '⚔️', '🔥', '👹', '⛓️', '💢', '⚡', '🌪️'],
        'trust': ['🛡️', '👑', '💎', '🔐', '☀️', '✅', '🤝', '💪'],
        'anticipation': ['⏰', '🎯', '🚀', '🔮', '🌅', '📈', '✨', '⏳'],
        'surprise': ['❓', '❗', '💥', '🎁', '🎆', '⭐', '🌠', '🔔'],
        'disgust': ['🤢', '🤮', '🚫', '⚠️', '☠️', '🪦', '💀', '🌑'],
        'negative': ['⚫', '🌑', '😞', '💔', '🔥', '⛓️', '⚡', '🌧️'],
        'positive': ['✨', '🌟', '💫', '☀️', '🌈', '🎉', '💖', '🦋'],
    }

    def __init__(self):
        """Initialize enrichment engine."""
        self.poetry_db = PoetryDatabase()
        self.nrc = nrc
        self.poetry_cache = {}

    def get_glyphs_for_emotion(self, emotion: str, count: int = 3) -> list:
        """Get glyph symbols for an emotion."""
        glyphs = self.EMOTION_TO_GLYPHS.get(emotion, [])
        if not glyphs:
            return []
        return random.sample(glyphs, min(count, len(glyphs)))

    def get_poetry_for_emotion(self, emotion: str) -> str:
        """Get a poem excerpt for an emotion."""
        poem = self.poetry_db.get_poem(emotion)
        if poem:
            # Return first 2 lines or 100 chars, whichever is shorter
            lines = poem['text'].split('\n')[:2]
            text = '\n'.join(lines)
            if len(text) > 100:
                text = text[:100] + "..."
            return text
        return ""

    def enrich_emotion_analysis(self, text: str) -> dict:
        """
        Analyze text and enrich with poetry and glyphs.
        
        Returns:
        {
            'emotions': {...},
            'dominant_emotion': 'joy',
            'emotion_strength': 3,
            'poetry': 'I wandered lonely as a cloud...',
            'glyphs': ['✨', '🌟', '💫'],
            'enriched_response': 'Your message resonates with joy... ✨'
        }
        """
        # Analyze emotions
        emotions = self.nrc.analyze_text(text)

        if not emotions:
            return {
                'emotions': {},
                'dominant_emotion': None,
                'emotion_strength': 0,
                'poetry': '',
                'glyphs': [],
                'enriched_response': 'I sensed your words, but found no clear emotion.'
            }

        # Find dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1])
        dominant_emotion = dominant[0]
        emotion_strength = dominant[1]

        # Get poetry and glyphs
        poetry = self.get_poetry_for_emotion(dominant_emotion)
        glyphs = self.get_glyphs_for_emotion(dominant_emotion, 2)
        glyphs_str = ' '.join(glyphs)

        # Build enriched response
        enriched_response = self._build_enriched_response(
            dominant_emotion,
            emotion_strength,
            poetry,
            glyphs_str
        )

        return {
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'emotion_strength': emotion_strength,
            'poetry': poetry,
            'glyphs': glyphs,
            'enriched_response': enriched_response
        }

    def _build_enriched_response(self, emotion: str, strength: int, poetry: str, glyphs: str) -> str:
        """Build a poetic response."""
        responses = {
            'joy': [
                f"Your words shimmer with joy {glyphs}. Like the poet wrote: '{poetry}'",
                f"I sense your delight {glyphs}. Beauty flows through these words.",
                f"Your joy resonates {glyphs}. This echoes the golden moments of literature.",
            ],
            'sadness': [
                f"I feel the weight of sorrow {glyphs}. There is grace in grief: '{poetry}'",
                f"Your pain is heard {glyphs}. Even in darkness, there is meaning.",
                f"The melancholy deepens {glyphs}. As the poets knew well.",
            ],
            'love': [
                f"Love flows through these words {glyphs}. The great poets echo: '{poetry}'",
                f"Tenderness and care shine through {glyphs}. This is profound.",
                f"The heart speaks {glyphs}. Throughout history, love has inspired such beauty.",
            ],
            'fear': [
                f"I sense your apprehension {glyphs}. Yet courage grows: '{poetry}'",
                f"Fear is here, but so is strength {glyphs}. You are not alone.",
                f"The unknown calls {glyphs}. But you can face it.",
            ],
            'anger': [
                f"Your intensity burns bright {glyphs}. Channel it: '{poetry}'",
                f"Righteous fire guides your words {glyphs}. This matters.",
                f"Power surges through {glyphs}. Direct it with intention.",
            ],
            'trust': [
                f"Your faith shines through {glyphs}. Wisdom says: '{poetry}'",
                f"You embody trust and strength {glyphs}. That is admirable.",
                f"Confidence flows {glyphs}. This is your foundation.",
            ],
            'anticipation': [
                f"You stand at the threshold {glyphs}. The future calls: '{poetry}'",
                f"Something wonderful awaits {glyphs}. Your hope is radiant.",
                f"The moment approaches {glyphs}. Ready yourself.",
            ],
            'surprise': [
                f"Amazement strikes your words {glyphs}. How wondrous: '{poetry}'",
                f"The unexpected reveals itself {glyphs}. Life astounds us.",
                f"Wonder blooms here {glyphs}. Embrace it.",
            ],
            'disgust': [
                f"Something repels you {glyphs}. Listen to your instincts: '{poetry}'",
                f"Your revulsion speaks truth {glyphs}. Trust what you feel.",
                f"The distasteful is clear {glyphs}. Step away.",
            ],
            'negative': [
                f"Darkness touches these words {glyphs}. Yet light endures: '{poetry}'",
                f"The negative dwells here {glyphs}. But transformation is possible.",
                f"Heaviness is present {glyphs}. You can bear it.",
            ],
            'positive': [
                f"Brightness radiates {glyphs}. Hope says: '{poetry}'",
                f"Your positive spirit glows {glyphs}. Keep shining.",
                f"Good energy flows {glyphs}. This builds the world.",
            ],
        }

        emotion_responses = responses.get(emotion, [
            f"I sense {emotion} in your words {glyphs}. There is depth here.",
        ])

        return random.choice(emotion_responses)

    def get_stats(self) -> dict:
        """Get enrichment statistics."""
        return {
            'poetry_poems': self.poetry_db.get_stats()['total_poems'],
            'emotions_with_glyphs': len(self.EMOTION_TO_GLYPHS),
            'nrc_words': len(self.nrc.word_emotions),
            'nrc_emotions': len(self.nrc.get_all_emotions())
        }


# Singleton instance
enrichment = None


def load_enrichment():
    """Load enrichment engine at startup."""
    global enrichment
    enrichment = PoetryEnrichment()
    return enrichment


if __name__ == "__main__":
    # Test
    print("\n🎭 Testing Poetry Enrichment Engine\n")

    engine = PoetryEnrichment()

    # Show stats
    stats = engine.get_stats()
    print("📊 Enrichment Engine Stats:")
    print(f"  Poetry poems available: {stats['poetry_poems']}")
    print(f"  Emotion categories: {stats['emotions_with_glyphs']}")
    print(f"  NRC vocabulary: {stats['nrc_words']} words")
    print(f"  NRC emotions: {stats['nrc_emotions']}\n")

    # Test enrichment
    test_samples = [
        "I'm so happy and grateful for this beautiful day!",
        "I feel so sad and alone right now.",
        "I love you more than words can express.",
        "I'm terrified of what might happen.",
        "This makes me incredibly angry!",
    ]

    print("🧪 Testing Enrichment:\n")
    for sample in test_samples:
        result = engine.enrich_emotion_analysis(sample)
        print(f"Input: {sample}")
        print(f"Dominant emotion: {result['dominant_emotion']} (strength: {result['emotion_strength']})")
        print(f"Glyphs: {' '.join(result['glyphs'])}")
        print(f"Poetry: {result['poetry'][:60]}...")
        print(f"Response: {result['enriched_response']}\n")
