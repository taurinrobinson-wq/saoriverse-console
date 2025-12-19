import os
import re
import requests
from typing import List

# Optional NLP integrations (NRC lexicon, spaCy, TextBlob)
HAS_NRC = False
HAS_SPACY = False
HAS_TEXTBLOB = False
try:
    from parser.nrc_lexicon_loader import nrc  # type: ignore
    HAS_NRC = True
except Exception:
    HAS_NRC = False

try:
    import spacy
    try:
        _nlp = spacy.load("en_core_web_sm")
        HAS_SPACY = True
    except Exception:
        # Model might not be installed
        _nlp = None
        HAS_SPACY = False
except Exception:
    HAS_SPACY = False

try:
    from textblob import TextBlob  # type: ignore
    HAS_TEXTBLOB = True
except Exception:
    HAS_TEXTBLOB = False

TONES = ["Very Formal", "Formal", "Neutral", "Friendly", "Empathetic"]

# Track which NLP tools are actually used during analysis
_active_tools_last_run = {"nrc": False, "spacy": False, "textblob": False}


def get_active_tools() -> dict:
    """Return which NLP tools were used in the last analysis run."""
    return _active_tools_last_run.copy()


def split_sentences(text: str) -> List[str]:
    # Very simple sentence splitter — keeps punctuation.
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def detect_tone(sentence: str) -> str:
    """Detect tone of a sentence with enhanced professional/critical detection."""
    global _active_tools_last_run
    _active_tools_last_run = {"nrc": False, "spacy": False, "textblob": False}
    
    s = sentence.lower()
    
    # Optional Sapling integration if configured
    api_key = os.environ.get("SAPLING_API_KEY")
    api_url = os.environ.get("SAPLING_API_URL")
    if api_key and api_url:
        try:
            resp = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"text": sentence, "task": "tone_detection"},
                timeout=5,
            )
            if resp.ok:
                j = resp.json()
                tone = j.get("tone") or j.get("label")
                if tone:
                    return tone
        except Exception:
            pass

    # Professional-critical detection (mildly critical, professionally critical)
    critical_markers = ["overlooks", "fails to", "insufficient", "inadequate", "misconstrued", "misunderstood", "questionable", "appears to have given undue weight"]
    uncertain_markers = ["appears", "seems", "arguably", "questionable", "potentially"]
    
    if any(marker in s for marker in critical_markers):
        if any(marker in s for marker in uncertain_markers):
            return "Professionally Critical"
        return "Professionally Critical"
    
    # Try NRC lexicon if available
    try:
        if HAS_NRC:
            scores = nrc.get_emotion_score(sentence)
            _active_tools_last_run["nrc"] = True
            if scores:
                if scores.get("joy", 0) > 0 or scores.get("positive", 0) > 0 or scores.get("trust", 0) > 0:
                    return "Friendly"
                if scores.get("sadness", 0) > 0 or scores.get("fear", 0) > 0:
                    return "Empathetic"
                if scores.get("anger", 0) > 0 or scores.get("disgust", 0) > 0:
                    return "Formal"
    except Exception:
        pass

    # Use TextBlob polarity when available
    try:
        if HAS_TEXTBLOB:
            tb = TextBlob(sentence)
            _active_tools_last_run["textblob"] = True
            if tb.sentiment.polarity > 0.2:
                return "Friendly"
            if tb.sentiment.polarity < -0.2:
                return "Formal"
    except Exception:
        pass

    # Minimal spaCy-based heuristics (politeness markers / sentence structure)
    try:
        if HAS_SPACY and _nlp is not None:
            doc = _nlp(sentence)
            _active_tools_last_run["spacy"] = True
            if s.startswith("please") or "thank you" in s or "thanks" in s:
                return "Friendly"
            if any(tok.tag_ in ("MD",) for tok in doc):
                return "Formal"
    except Exception:
        pass

    # Heuristic fallback
    if any(w in s for w in ["please", "thanks", "thank you", "appreciate"]):
        return "Friendly"
    if s.endswith("?"):
        return "Neutral"
    if any(w in s for w in ["maybe", "might", "could", "perhaps"]):
        return "Formal"
    if any(w in s for w in ["i'm sorry", "i apologize", "sorry"]):
        return "Empathetic"
    if any(w in s for w in ["best regards", "sincerely", "regards"]):
        return "Very Formal"
    return "Neutral"


def _replace_contractions(text: str) -> str:
    contractions = {
        "I'm": "I am",
        "you're": "you are",
        "can't": "cannot",
        "won't": "will not",
        "it's": "it is",
    }
    for k, v in contractions.items():
        text = re.sub(re.escape(k), v, text, flags=re.IGNORECASE)
    return text


def shift_tone(sentence: str, target_tone: str) -> str:
    # Optional Sapling paraphrase if configured
    api_key = os.environ.get("SAPLING_API_KEY")
    api_url = os.environ.get("SAPLING_API_URL")
    if api_key and api_url:
        try:
            resp = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"text": sentence, "task": "paraphrase", "tone": target_tone},
                timeout=6,
            )
            if resp.ok:
                j = resp.json()
                para = j.get("paraphrase") or j.get("text")
                if para:
                    return para
        except Exception:
            pass

    # Heuristic transformations
    s = sentence.strip()
    if target_tone == "Very Formal":
        s = _replace_contractions(s)
        if not s.endswith('.') and not s.endswith('!') and not s.endswith('?'):
            s = s + '.'
        return s

    if target_tone == "Formal":
        s = _replace_contractions(s)
        s = re.sub(r"\bmaybe\b|\bmight\b|\bcould\b|\bperhaps\b", "", s, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", s).strip()

    if target_tone == "Friendly":
        if not (s.startswith("Hey") or s.startswith("Hi") or s.startswith("Hello")):
            s = "Hi — " + s[0].lower() + s[1:]
        if not s.endswith(('!', '?')):
            s = s + '!'
        return s

    if target_tone == "Empathetic":
        lower = s.lower()
        if not (lower.startswith("i understand") or lower.startswith("i'm sorry") or lower.startswith("i apologize")):
            s = "I understand. " + s
        return s

    # Neutral
    return s


def map_slider_to_tone(value: int) -> str:
    idx = max(0, min(len(TONES) - 1, int(value)))
    return TONES[idx]


def classify_sentence_structure(sentence: str) -> str:
    """Classify sentence structure: Introduction, Conclusion, Reasoning, Supporting, or Statement."""
    s = sentence.lower()
    
    # Introduction markers
    intro_markers = ["the judge", "the court", "the defendant", "the plaintiff", "it is", "it appears", "it seems"]
    if any(marker in s for marker in intro_markers):
        return "Introduction"
    
    # Conclusion markers
    conclusion_markers = ["therefore", "in conclusion", "thus", "as a result", "consequently", "in summary", "it follows"]
    if any(marker in s for marker in conclusion_markers):
        return "Conclusion"
    
    # Reasoning/Argument markers
    reasoning_markers = ["because", "since", "as", "due to", "on the grounds that", "given that"]
    if any(marker in s for marker in reasoning_markers):
        return "Reasoning"
    
    # Supporting/Evidence markers
    supporting_markers = ["testimony", "evidence", "documented", "on record", "as shown", "clear from"]
    if any(marker in s for marker in supporting_markers):
        return "Supporting"
    
    return "Statement"


def assess_overall_message(sentences: List[str], tones: List[str]) -> str:
    """Assess overall message character: Persuasive, Argumentative, Aggressive, Neutral, Friendly, Professional, Casual."""
    if not sentences:
        return "Neutral"
    
    # Count tone occurrences
    tone_counts = {}
    for tone in tones:
        tone_counts[tone] = tone_counts.get(tone, 0) + 1
    
    # Detect structural characteristics
    full_text = " ".join(sentences).lower()
    
    # Check for argumentative markers
    argumentative_markers = ["overlooks", "fails to", "misconstrued", "undue weight", "despite", "however", "but"]
    argumentative_count = sum(1 for marker in argumentative_markers if marker in full_text)
    
    # Check for persuasive markers (evidence, reasoning, logic)
    persuasive_markers = ["evidence", "testimony", "documented", "clear", "proven", "therefore", "thus", "because"]
    persuasive_count = sum(1 for marker in persuasive_markers if marker in full_text)
    
    # Check for aggressive markers
    aggressive_markers = ["demand", "must", "fail to", "inexcusable", "unacceptable", "outrageous"]
    aggressive_count = sum(1 for marker in aggressive_markers if marker in full_text)
    
    # Determine overall assessment
    if aggressive_count > len(sentences) / 3:
        return "Aggressive"
    if argumentative_count >= persuasive_count and argumentative_count > len(sentences) / 4:
        return "Argumentative"
    if persuasive_count >= argumentative_count and persuasive_count > len(sentences) / 4:
        return "Persuasive"
    if "Friendly" in tone_counts and tone_counts["Friendly"] > len(sentences) / 2:
        return "Friendly"
    if "Empathetic" in tone_counts and tone_counts["Empathetic"] > len(sentences) / 2:
        return "Empathetic"
    if "Very Formal" in tone_counts or "Formal" in tone_counts:
        formal_total = tone_counts.get("Very Formal", 0) + tone_counts.get("Formal", 0)
        if formal_total > len(sentences) / 2:
            return "Professional"
    
    return "Neutral"
