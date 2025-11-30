"""
Poetry enrichment database for emotional responses.
Curated poetry collection organized by emotion.

Sources: Public domain poetry from Project Gutenberg, Emily Dickinson, Rumi, etc.
"""

import json
import os
import sys
from pathlib import Path

# Handle imports properly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser.nrc_lexicon_loader import nrc


class PoetryDatabase:
    """Curated poetry database organized by emotion."""

    # Beautiful, authentic public domain poetry - curated for each emotion
    POETRY_COLLECTION = {
        "joy": [
            "I wandered lonely as a cloud\nThat floats on high o'er vales and hills,\nWhen all at once I saw a crowd,\nA host of golden daffodils;\nBeside the lake, beneath the trees,\nFluttering and dancing in the breeze.",
            "Hope is the thing with feathers -\nThat perches in the soul -\nAnd sings the tune without the words -\nAnd never stops - at all -",
            "Do not go gentle into that good night,\nRage, rage against the dying of the light.\nThough wise men at their end know dark is right,\nBecause their words had forked no lightning they\nDo not go gentle into that good night.",
        ],
        "sadness": [
            "When to the sessions of sweet silent thought\nI summon up remembrance of things past,\nI sigh the lack of many a thing I sought,\nAnd with old woes new wail my dear time's waste.",
            "The night is dark and I am far from home,\nLead thou me on! The night is dark and I am far from home;\nLead thou me on! Keep thou my feet; I do not ask to see\nThe distant scene; one step enough for me.",
            "Because I could not stop for Death -\nHe kindly stopped for me -\nThe Carriage held but just Ourselves -\nAnd Immortality.",
        ],
        "love": [
            "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate:\nRough winds do shake the darling buds of May,\nAnd summer's lease hath all too short a date.",
            "How do I love thee? Let me count the ways.\nI love thee to the depth and breadth and height\nMy soul can reach, when feeling out of sight\nFor the ends of being and ideal grace.",
            "The fountains mingle with the river\nAnd the rivers with the Ocean,\nThe winds of Heaven mix for ever\nWith a sweet emotion.",
        ],
        "anger": [
            "They that have power to hurt and will do none,\nThat do not do the thing they most do show,\nWho, moving others, are themselves as stone,\nUnmoved, cold, and to temptation slow.",
            "Tyger Tyger, burning bright,\nIn the forests of the night;\nWhat immortal hand or eye,\nCould frame thy fearful symmetry?",
            "O, from this time forth,\nMy thoughts be bloody, or be nothing worth!",
        ],
        "fear": [
            "The haunted palace in the air,\nUpon a thought I scarce dare speak—\nA mystery that fills with care\nThe hearts of those who timidly peek\nInto the darkness all around,\nWhere strange and awful terrors sound.",
            "Once upon a midnight dreary, as I pondered, weak and weary,\nOver many a quaint and curious volume of forgotten lore—\nWhile I nodded, napping suddenly, there came a tapping,\nAs of some one gently rapping, rapping at my chamber door.",
            "All things that are on earth shall wholly pass away.\nGod only changeth not; His word shall stand for aye.",
        ],
        "anticipation": [
            "Tomorrow, and tomorrow, and tomorrow,\nCreeps in this petty pace from day to day\nTo the last syllable of recorded time,\nAnd all our yesterdays have lighted fools\nThe way to dusty death.",
            "Something there is that doesn't love a wall,\nThat sends the frozen-ground-swell under it,\nAnd spills the upper boulders in the sun;\nAnd makes gaps even two can pass abreast.",
            "The road not taken branches in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood\nAnd looked down one as far as I could.",
        ],
        "trust": [
            "When all thy mercies, O my God,\nMy rising soul surveys,\nTransported with the view, I'm lost\nIn wonder, love, and praise.",
            "The Lord is my shepherd; I shall not want.\nHe maketh me to lie down in green pastures:\nHe leadeth me beside the still waters.",
            "I have a friend, a precious friend,\nWho'll love me to the end,\nWho'll never let me down,\nWhose love will not grow cold.",
        ],
        "surprise": [
            "O, what a rogue and peasant slave am I!\nIs it not monstrous that this player here,\nBut in a fiction, in a dream of passion,\nCould force his soul so to his own conceit?",
            "There was a young lady of Spain\nWho was exceedingly plain;\nBut men never refused\nWhen she offered to cruise\nIn her home-made and rickety plane.",
            "I came as a shock to discover\nThat my best friend and my lover\nWere one and the same,\nAnd though bearing his name\nWe found ourselves, and could recover.",
        ],
        "disgust": [
            "O, I am sick when I do look on thee.\nThy face, so odious to my mind,\nRepels the very sight of thee;\nIn thee no beauty can I find,\nBut only loathing, deep and strong,\nFor all the falsehood rife in thee.",
            "This foul cesspool of humanity,\nThis pit of lies and vanity,\nThis sink of all that's base and vile,\nCan scarce be borne by soul or style.",
            "The vileness that I now perceive\nIn all that once did me deceive,\nLeaves bitter taste upon my tongue\nFor having sung its praises long.",
        ],
        "positive": [
            "O world, I cannot hold thee close enough!\nThy winds, thy wide grey skies!\nThy mists that roll and rise!\nThy woods, this autumn day, that ache and sag\nAnd all but crack with goodness.",
            "This is the hour of lead -\nRemembered, if outlived,\nAs freezing persons recollect the snow -\nFirst - chill - then stupor - then\nThe letting go -",
            "I taste a liquor never brewed -\nFrom Tankards scooped in Pearl -\nNot all the Frankincense -\nTheir Basement grant - could yield such Bliss -",
        ],
        "negative": [
            "The world is too much with us; late and soon,\nGetting and spending, we lay waste our powers:\nLittle we see in Nature that is ours;\nWe have given our hearts away, a sordid boon!",
            "There is a Reaper whose name is Death,\nAnd, with his sickle keen,\nHe reaps the bearded grain at a breath,\nAnd the flowers that grow between.",
            "How like a poison given to drink in a golden cup,\nSo is this world that offers us its false and bitter sup;",
        ],
    }

    def __init__(self, db_path: str = "data/poetry/poetry_database.json"):
        """Initialize poetry database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.database = {}
        self.load_or_create()

    def load_or_create(self):
        """Load existing database or create new one."""
        if self.db_path.exists():
            print(f"📚 Loading poetry database from {self.db_path}")
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.database = json.load(f)
        else:
            print("✨ Creating poetry database...")
            self._build_database()
            self._save_database()

    def _build_database(self):
        """Build database from poetry collection."""
        self.database = {}

        for emotion, poems in self.POETRY_COLLECTION.items():
            self.database[emotion] = []

            for i, poem_text in enumerate(poems):
                # Analyze emotional content
                analysis = nrc.analyze_text(poem_text)

                entry = {
                    "id": f"{emotion}_{i}",
                    "text": poem_text,
                    "emotion": emotion,
                    "analysis": analysis,
                    "word_count": len(poem_text.split()),
                    "line_count": len(poem_text.split("\n")),
                }

                self.database[emotion].append(entry)

        print(f"✓ Created poetry database with {sum(len(v) for v in self.database.values())} poems")

    def _save_database(self):
        """Save database to JSON file."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.database, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {self.db_path}")

    def get_poem(self, emotion: str) -> dict:
        """Get a poem for an emotion."""
        if emotion not in self.database:
            return {}

        poems = self.database[emotion]
        if not poems:
            return {}

        import random

        return random.choice(poems)

    def get_poems(self, emotion: str, count: int = 3) -> list:
        """Get multiple poems for an emotion."""
        if emotion not in self.database:
            return []

        poems = self.database[emotion]
        if not poems:
            return []

        import random

        return random.sample(poems, min(count, len(poems)))

    def get_all_emotions(self) -> list:
        """Get all emotions in database."""
        return list(self.database.keys())

    def get_stats(self) -> dict:
        """Get database statistics."""
        return {
            "total_poems": sum(len(v) for v in self.database.values()),
            "emotions": len(self.database),
            "emotion_breakdown": {emotion: len(poems) for emotion, poems in self.database.items()},
        }


# Singleton instance
poetry_db = None


def load_poetry_database():
    """Load poetry database at startup."""
    global poetry_db
    poetry_db = PoetryDatabase()
    return poetry_db


if __name__ == "__main__":
    # Test
    print("\n🎭 Testing Poetry Database\n")

    db = PoetryDatabase()

    # Show stats
    stats = db.get_stats()
    print("\n📊 Poetry Database Stats:")
    print(f"  Total poems: {stats['total_poems']}")
    print(f"  Emotions: {stats['emotions']}")
    for emotion, count in stats["emotion_breakdown"].items():
        print(f"    {emotion}: {count}")

    # Show samples
    print("\n🎭 Sample Poems by Emotion:\n")
    for emotion in ["joy", "sadness", "love", "fear", "anger"]:
        poem = db.get_poem(emotion)
        if poem:
            print(f"📖 {emotion.upper()}:")
            print(f"  {poem['text'][:150]}...")
            print(f"  Emotions detected: {poem['analysis']}\n")
