import importlib
import logging

logger = logging.getLogger(__name__)


# Prefer Streamlit's cache_resource when available to integrate with Streamlit
# session lifecycle. Fall back to functools.lru_cache when Streamlit is not
# importable (e.g., non-UI test environments).
try:
    import streamlit as _st  # type: ignore

    def _cache_decorator():
        return _st.cache_resource
except Exception:
    from functools import lru_cache as _lru_cache

    def _cache_decorator():
        def _inner(func):
            return _lru_cache(maxsize=1)(func)

        return _inner


@_cache_decorator()
def get_spacy_model(model_name: str = "en_core_web_sm"):
    """Lazily load and cache a spaCy model.

    Returns the loaded model, a blank 'en' pipeline if model load fails,
    or None if spaCy isn't installed.
    """
    try:
        spacy = importlib.import_module("spacy")
    except Exception:
        logger.debug("spaCy not installed (get_spacy_model)")
        return None

    try:
        model = spacy.load(model_name)
        logger.info("Loaded spaCy model: %s", model_name)
        return model
    except Exception as e:
        logger.debug("Could not load spaCy model '%s': %s. Falling back to blank('en')", model_name, e)
        try:
            return spacy.blank("en")
        except Exception:
            logger.debug("Failed to create blank spaCy pipeline")
            return None
