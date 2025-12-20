import re

CONTRACTIONS = {
    "i'm": "i am",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "it's": "it is",
    "that's": "that is",
    "there's": "there is",
    "can't": "cannot",
    "won't": "will not",
    "don't": "do not",
    "doesn't": "does not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "couldn't": "could not",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "i'll": "i will",
    "you'll": "you will",
    "we'll": "we will",
    "they'll": "they will",
    "i'd": "i would",
    "you'd": "you would",
    "we'd": "we would",
    "they'd": "they would",
    "ain't": "is not",
}

_pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in CONTRACTIONS.keys()) + r")\b", flags=re.IGNORECASE)


def expand_contractions(text: str, mapping: dict = CONTRACTIONS) -> str:
    """Expand common English contractions using a mapping.

    Preserves initial capitalization of the matched token.
    """

    def _replace(match):
        word = match.group(0)
        expanded = mapping[word.lower()]
        if word[0].isupper():
            expanded = expanded.capitalize()
        return expanded

    return _pattern.sub(_replace, text)
