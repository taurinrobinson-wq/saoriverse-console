import os
import re
import requests
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Import enhanced analysis components
try:
    from .enhanced_affect_parser import (
        EnhancedAffectParser,
        create_enhanced_affect_parser,
        EnhancedAffectAnalysis,
    )
    HAS_ENHANCED_AFFECT_PARSER = True
    logger.info("✅ Enhanced Affect Parser loaded")
except Exception as e:
    HAS_ENHANCED_AFFECT_PARSER = False
    logger.warning(f"❌ Enhanced Affect Parser failed to load: {e}")
    create_enhanced_affect_parser = None

try:
    from .tone_analysis_composer import (
        ToneAnalysisComposer,
        create_tone_analysis_composer,
    )
    HAS_TONE_ANALYSIS_COMPOSER = True
    logger.info("✅ Tone Analysis Composer loaded")
except Exception as e:
    HAS_TONE_ANALYSIS_COMPOSER = False
    logger.warning(f"❌ Tone Analysis Composer failed to load: {e}")
    create_tone_analysis_composer = None

# Initialize composer instances (optional, lazy-loaded)
_affect_parser: Optional[EnhancedAffectParser] = None
_tone_composer: Optional[ToneAnalysisComposer] = None

# Optional NLP integrations (NRC lexicon, spaCy, TextBlob)
HAS_NRC = False
HAS_SPACY = False
HAS_TEXTBLOB = False
NRC_ERROR = None
SPACY_ERROR = None
TEXTBLOB_ERROR = None

# Try multiple paths for NRC lexicon
try:
    from src.parser.nrc_lexicon_loader import nrc  # type: ignore
    HAS_NRC = True
    logger.info("✅ NRC lexicon loaded successfully (src.parser)")
except Exception as e1:
    try:
        from parser.nrc_lexicon_loader import nrc  # type: ignore
        HAS_NRC = True
        logger.info("✅ NRC lexicon loaded successfully (parser)")
    except Exception as e2:
        NRC_ERROR = f"Tried src.parser and parser: {e2}"
        logger.warning(f"❌ NRC lexicon failed to load: {NRC_ERROR}")
        HAS_NRC = False

try:
    import spacy
    _nlp = None
    try:
        _nlp = spacy.load("en_core_web_sm")
        HAS_SPACY = True
        logger.info("✅ spaCy model loaded successfully")
    except Exception as e:
        # Try to download the model automatically, then fall back to a blank pipeline
        try:
            try:
                from spacy import cli as spacy_cli
            except Exception:
                spacy_cli = None

            if spacy_cli is not None:
                logger.info("spaCy model not found; attempting to download en_core_web_sm...")
                download_success = False
                # Try regular download first
                try:
                    spacy_cli.download("en_core_web_sm")
                    _nlp = spacy.load("en_core_web_sm")
                    HAS_SPACY = True
                    download_success = True
                    logger.info("✅ spaCy model downloaded and loaded successfully")
                except PermissionError as perm_e:
                    # Try download with --user flag for permission-denied errors
                    logger.info(f"Regular download failed with permission error; trying --user flag...")
                    try:
                        import subprocess
                        subprocess.run([
                            "python", "-m", "spacy", "download", 
                            "en_core_web_sm", "--user"
                        ], check=True, capture_output=True, timeout=120)
                        _nlp = spacy.load("en_core_web_sm")
                        HAS_SPACY = True
                        download_success = True
                        logger.info("✅ spaCy model downloaded (with --user) and loaded successfully")
                    except Exception as user_download_e:
                        logger.warning(f"Download with --user flag also failed: {user_download_e}")
                except Exception as e2:
                    logger.warning(f"Failed to download spaCy model: {e2}")
            
            # If download not available or failed, use a minimal blank English pipeline
            if _nlp is None:
                try:
                    _nlp = spacy.blank("en")
                    HAS_SPACY = True
                    SPACY_ERROR = f"Using blank 'en' pipeline (original error: {e})"
                    logger.warning("⚠️ spaCy model not available; using blank 'en' pipeline")
                except Exception as e3:
                    SPACY_ERROR = f"spaCy load failed: {e3}"
                    logger.warning(f"❌ spaCy blank model failed: {e3}")
                    _nlp = None
                    HAS_SPACY = False
        except Exception as outer_e:
            SPACY_ERROR = str(outer_e)
            logger.warning(f"❌ spaCy model failed to load: {outer_e}")
except Exception as e:
    SPACY_ERROR = str(e)
    logger.warning(f"❌ spaCy import failed: {e}")
    HAS_SPACY = False

try:
    from textblob import TextBlob  # type: ignore
    HAS_TEXTBLOB = True
    logger.info("✅ TextBlob loaded successfully")
except Exception as e:
    TEXTBLOB_ERROR = str(e)
    logger.warning(f"❌ TextBlob failed to load: {e}")
    HAS_TEXTBLOB = False

TONES = ["Very Formal", "Formal", "Neutral", "Friendly", "Empathetic"]

# Track which NLP tools are actually used during analysis
_active_tools_last_run = {"nrc": False, "spacy": False, "textblob": False}


def get_active_tools() -> dict:
    """Return which NLP tools were used in the last analysis run."""
    return _active_tools_last_run.copy()


def get_tool_status() -> dict:
    """Return status of all NLP tools (loaded, errors, etc)."""
    return {
        "nrc": {"loaded": HAS_NRC, "error": NRC_ERROR},
        "spacy": {"loaded": HAS_SPACY, "error": SPACY_ERROR},
        "textblob": {"loaded": HAS_TEXTBLOB, "error": TEXTBLOB_ERROR},
        "enhanced_affect_parser": {"loaded": HAS_ENHANCED_AFFECT_PARSER},
        "tone_analysis_composer": {"loaded": HAS_TONE_ANALYSIS_COMPOSER},
    }


def get_affect_parser() -> Optional[EnhancedAffectParser]:
    """Lazily instantiate and return the enhanced affect parser."""
    global _affect_parser
    if _affect_parser is None and HAS_ENHANCED_AFFECT_PARSER and create_enhanced_affect_parser:
        try:
            _affect_parser = create_enhanced_affect_parser(
                use_nrc=True,
                use_textblob=HAS_TEXTBLOB,
                use_spacy=HAS_SPACY,
            )
            logger.info("✅ Enhanced Affect Parser instantiated")
        except Exception as e:
            logger.warning(f"Failed to instantiate affect parser: {e}")
            return None
    return _affect_parser


def get_tone_composer() -> Optional[ToneAnalysisComposer]:
    """Lazily instantiate and return the tone analysis composer."""
    global _tone_composer
    if _tone_composer is None and HAS_TONE_ANALYSIS_COMPOSER and create_tone_analysis_composer:
        try:
            _tone_composer = create_tone_analysis_composer()
            logger.info("✅ Tone Analysis Composer instantiated")
        except Exception as e:
            logger.warning(f"Failed to instantiate tone composer: {e}")
            return None
    return _tone_composer


def get_tool_status_legacy() -> dict:
    """Return status of legacy NLP tools."""


def split_sentences(text: str) -> List[str]:
    # Very simple sentence splitter — keeps punctuation.
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def detect_tone(sentence: str) -> str:
    """Detect tone of a sentence with enhanced professional/critical detection.
    
    Uses multiple strategies in order of preference:
    1. Sapling API (if configured)
    2. Enhanced Affect Parser (multi-method NLP)
    3. NRC lexicon
    4. TextBlob sentiment
    5. spaCy linguistic features
    6. Heuristic fallback
    """
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

    # Try Enhanced Affect Parser if available
    try:
        parser = get_affect_parser()
        if parser:
            analysis: EnhancedAffectAnalysis = parser.analyze_affect(sentence)
            _active_tools_last_run["nrc"] = True  # Affect parser uses NRC internally
            
            # Map affect analysis to tone palette
            if analysis.valence > 0.5 and analysis.primary_emotion in ("joy", "trust", "anticipation"):
                return "Friendly"
            elif analysis.valence < -0.5 and analysis.primary_emotion == "sadness":
                return "Empathetic"
            elif analysis.valence < -0.3 and analysis.primary_emotion in ("anger", "disgust"):
                return "Professionally Critical"
            elif analysis.sentiment_subjectivity > 0.7:
                return "Empathetic"
            elif analysis.dominance > 0.6 and analysis.primary_emotion != "sadness":
                return "Formal"
    except Exception as e:
        logger.debug(f"Enhanced affect parser analysis failed: {e}")

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
    """Transform sentence tone appropriately for legal correspondence."""
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

    # Smart heuristic transformations for legal text
    s = sentence.strip()
    s_lower = s.lower()
    
    if target_tone == "Very Formal":
        # Maximum formality: replace all contractions, use formal language
        s = _replace_contractions(s)
        # Replace casual words with formal equivalents
        s = re.sub(r"\bi'm\b", 'I am', s, flags=re.IGNORECASE)
        s = re.sub(r"\byou're\b", 'you are', s, flags=re.IGNORECASE)
        s = re.sub(r'\bso\b', 'therefore', s, flags=re.IGNORECASE)
        s = re.sub(r'\bfails to\b', 'fails to', s, flags=re.IGNORECASE)  # Keep strong
        s = re.sub(r'\bdid not\b', 'failed to', s, flags=re.IGNORECASE)  # Strengthen
        # Ensure sentence ends with period
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
        return s

    if target_tone == "Formal":
        # Formal: replace contractions, remove hedging, maintain professional tone
        s = _replace_contractions(s)
        # Replace very casual language
        s = re.sub(r'\bso\b', 'therefore', s, flags=re.IGNORECASE)
        s = re.sub(r'\bkinda\b|\bsorta\b', '', s, flags=re.IGNORECASE)
        # Remove excessive hedging
        s = re.sub(r'\b(maybe|might|could|perhaps|seems|appears to be)\b', '', s, flags=re.IGNORECASE)
        # Clean up extra spaces from removals
        s = re.sub(r'\s+', ' ', s).strip()
        # Ensure proper ending
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
        return s

    if target_tone == "Neutral":
        # Neutral: remove emotional language, be objective
        s = _replace_contractions(s)
        # Remove exclamations and emotional intensifiers
        s = re.sub(r'\bvery\b|\bextremely\b|\babsolutely\b|\bclearly\b', '', s, flags=re.IGNORECASE)
        # Tone down critical language
        s = re.sub(r'\bfails to\b', 'does not', s, flags=re.IGNORECASE)
        s = re.sub(r'\boverlooks\b', 'does not fully consider', s, flags=re.IGNORECASE)
        # Replace exclamation with period
        s = s.rstrip('!') + ('.' if not s.rstrip('!').endswith(('.', '?')) else '')
        # Clean up extra spaces
        s = re.sub(r'\s+', ' ', s).strip()
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
        return s

    if target_tone == "Friendly":
        # Friendly: warm but still professional, soften critical language
        # Replace very formal phrases with friendlier equivalents
        s = re.sub(r'\bshall\b', 'will', s, flags=re.IGNORECASE)
        s = re.sub(r'\bthus\b|\btherefore\b', 'so', s, flags=re.IGNORECASE)
        s = re.sub(r'\bnevertheless\b', 'however', s, flags=re.IGNORECASE)
        
        # Soften critical words
        s = re.sub(r'\boverlooks\b', 'may not fully consider', s, flags=re.IGNORECASE)
        s = re.sub(r'\bfails to\b', 'did not', s, flags=re.IGNORECASE)
        s = re.sub(r'\bundue weight\b', 'significant weight', s, flags=re.IGNORECASE)
        s = re.sub(r'\binadequate\b', 'insufficient', s, flags=re.IGNORECASE)
        s = re.sub(r'\bunacceptable\b', 'not ideal', s, flags=re.IGNORECASE)
        
        # Keep contractions for warmth (don't replace)
        
        # Add warmth with exclamation where appropriate
        if any(word in s_lower for word in ["thank", "appreciate", "grateful"]):
            if not s.endswith('!'):
                s = s.rstrip('.?!') + '!'
        
        # Ensure proper ending
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
        return s

    if target_tone == "Empathetic":
        # Empathetic: acknowledge feelings, soften critical tone, show understanding
        
        # Add empathetic opening to critical or challenging statements
        if any(word in s_lower for word in ["fails", "inadequate", "unfair", "undue", "problem", "issue", "overlooks"]):
            if not s_lower.startswith(("i understand", "i recognize", "i appreciate", "certainly", "i see")):
                # Add empathetic opening that flows naturally
                if s[0].isupper():
                    s = "I understand that " + s[0].lower() + s[1:]
                else:
                    s = "I understand that " + s
        
        # Replace harsh words with gentler equivalents
        s = re.sub(r'\bfails? to\b', 'did not', s, flags=re.IGNORECASE)
        s = re.sub(r'\bunacceptable\b', 'concerning', s, flags=re.IGNORECASE)
        s = re.sub(r'\bunfair\b', 'challenging', s, flags=re.IGNORECASE)
        s = re.sub(r'\boverlooks\b', 'may have overlooked', s, flags=re.IGNORECASE)
        s = re.sub(r'\binadequate\b', 'insufficient', s, flags=re.IGNORECASE)
        
        # Keep contractions for warmth
        
        # Ensure proper ending
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
        return s

    # Default fallback (shouldn't reach here with valid tones)
    if not s.endswith(('.', '!', '?')):
        s = s + '.'
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
