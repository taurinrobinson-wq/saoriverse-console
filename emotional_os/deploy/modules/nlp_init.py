"""
NLP warmup helper

Attempt to import optional NLP libraries (TextBlob, spaCy) and load the
spaCy model. This provides clearer diagnostics and a single place to
run initialization at app startup so Streamlit's runtime has warmed
models and modules available.

This module is best-effort and never raises: callers should treat it as
an information/logging helper.
"""

import logging
import sys

logger = logging.getLogger(__name__)

NLP_STATE = {
    'textblob_available': False,
    'spacy_available': False,
    'spacy_model_loaded': False,
    'textblob_exc': None,
    'spacy_exc': None,
    'python_executable': sys.executable,
}


def warmup_nlp(model_name: str = 'en_core_web_sm') -> dict:
    """Try to import TextBlob and spaCy and load the requested spaCy model.

    Returns a dict describing which components are available and any
    exception messages captured. This function is safe to call repeatedly.
    """
    # TextBlob
    try:
        from textblob import TextBlob  # noqa: F401
        NLP_STATE['textblob_available'] = True
        NLP_STATE['textblob_exc'] = None
        logger.info("TextBlob available: %s", True)
    except Exception as e:
        NLP_STATE['textblob_available'] = False
        NLP_STATE['textblob_exc'] = repr(e)
        logger.warning("TextBlob not available: %s", e)

    # spaCy and model
    try:
        import spacy
        NLP_STATE['spacy_available'] = True
        NLP_STATE['spacy_exc'] = None
        try:
            # Attempt to load the model; this may raise if the model isn't installed
            _nlp = spacy.load(model_name)
            NLP_STATE['spacy_model_loaded'] = True
            logger.info("spaCy model '%s' loaded", model_name)
        except Exception as me:
            NLP_STATE['spacy_model_loaded'] = False
            NLP_STATE['spacy_exc'] = repr(me)
            logger.warning(
                "spaCy model '%s' could not be loaded: %s", model_name, me)
    except Exception as e:
        NLP_STATE['spacy_available'] = False
        NLP_STATE['spacy_model_loaded'] = False
        NLP_STATE['spacy_exc'] = repr(e)
        logger.warning("spaCy not available: %s", e)

    # Record python executable for diagnostics (helps ensure Streamlit uses same env)
    NLP_STATE['python_executable'] = sys.executable

    # Provide a compact summary for logs
    summary = {
        'textblob_available': NLP_STATE['textblob_available'],
        'spacy_available': NLP_STATE['spacy_available'],
        'spacy_model_loaded': NLP_STATE['spacy_model_loaded'],
        'python_executable': NLP_STATE['python_executable'],
        'textblob_exc': NLP_STATE['textblob_exc'],
        'spacy_exc': NLP_STATE['spacy_exc'],
    }

    logger.info("NLP warmup summary: %s", {k: summary[k] for k in (
        'textblob_available', 'spacy_available', 'spacy_model_loaded')})
    return summary
