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
    "textblob_available": False,
    "spacy_available": False,
    "spacy_model_loaded": False,
    "nrc_available": False,
    "textblob_exc": None,
    "spacy_exc": None,
    "nrc_exc": None,
    "python_executable": sys.executable,
}


def warmup_nlp(model_name: str = "en_core_web_sm") -> dict:
    """Try to import TextBlob and spaCy and load the requested spaCy model.

    Returns a dict describing which components are available and any
    exception messages captured. This function is safe to call repeatedly.
    """
    import os
    from pathlib import Path
    
    # Ensure src is in sys.path for imports - handle both local and Streamlit Cloud
    current_file = Path(__file__)
    # Navigate from: src/emotional_os/deploy/modules/nlp_init.py -> src
    src_path = current_file.parent.parent.parent.parent.resolve()
    
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        logger.debug(f"Added to sys.path: {src_path}")
    
    # Also add the app root to handle absolute imports
    app_root = current_file.parent.parent.parent.parent.parent.resolve()
    if str(app_root) not in sys.path:
        sys.path.insert(0, str(app_root))
        logger.debug(f"Added to sys.path: {app_root}")
    
    # TextBlob
    try:
        from textblob import TextBlob  # noqa: F401

        NLP_STATE["textblob_available"] = True
        NLP_STATE["textblob_exc"] = None
        logger.info("TextBlob available: %s", True)
    except Exception as e:
        NLP_STATE["textblob_available"] = False
        NLP_STATE["textblob_exc"] = repr(e)
        logger.debug("TextBlob not available: %s", e)

    # spaCy and model: use lazy loader to avoid importing spaCy at module import time
    try:
        try:
            from emotional_os.utils.nlp_loader import get_spacy_model
        except Exception:
            # fallback import path
            from src.emotional_os.utils.nlp_loader import get_spacy_model  # type: ignore

        NLP_STATE["spacy_available"] = True
        NLP_STATE["spacy_exc"] = None
        logger.info("spaCy lazy loader available")
        try:
            logger.info(f"Attempting to lazily load spaCy model '{model_name}'...")
            _nlp = get_spacy_model(model_name)
            NLP_STATE["spacy_model_loaded"] = bool(_nlp)
            logger.info("spaCy model '%s' loaded (lazy) -> %s", model_name, NLP_STATE["spacy_model_loaded"])
        except Exception as me:
            logger.warning(f"spaCy model lazy load error: {me}")
            NLP_STATE["spacy_model_loaded"] = False
            NLP_STATE["spacy_exc"] = str(me)
    except Exception as e:
        NLP_STATE["spacy_available"] = False
        NLP_STATE["spacy_model_loaded"] = False
        NLP_STATE["spacy_exc"] = repr(e)
        logger.warning("spaCy lazy loader not available: %s", e)

    # NRC Lexicon - try multiple import strategies
    try:
        nrc = None
        import_error = None

        # Avoid importing the stdlib 'parser' package by name; instead locate
        # the repository's 'nrc_lexicon_loader.py' and import it by file path.
        from importlib import util as _util
        from pathlib import Path

        current_file = Path(__file__)
        loader_path = None

        # Look for common locations (walk parents to find src/parser)
        for parent in current_file.parents:
            candidate = parent / "parser" / "nrc_lexicon_loader.py"
            if candidate.exists():
                loader_path = candidate
                logger.debug(f"Found NRC loader at: {candidate}")
                break

        # Also check project-level src/parser
        if loader_path is None:
            candidate = current_file.parents[3] / "parser" / "nrc_lexicon_loader.py"
            if candidate.exists():
                loader_path = candidate

        if loader_path is not None:
            try:
                spec = _util.spec_from_file_location("nrc_lexicon_loader", str(loader_path))
                module = _util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
                nrc = getattr(module, "nrc", None)
                logger.debug(f"Imported NRC loader from file: {loader_path}")
            except Exception as e:
                import_error = e
        else:
            import_error = ImportError("Could not locate nrc_lexicon_loader.py in repository")

        # As a final fallback, try the package import path that avoids the name 'parser'
        if nrc is None:
            try:
                from src.parser.nrc_lexicon_loader import nrc  # noqa: F401
                logger.debug("NRC loaded via src.parser.nrc_lexicon_loader")
            except Exception as e:
                # If this fails, capture the last error
                import_error = import_error or e

        if nrc is not None:
            # Verify the NRC lexicon has data (not just imported but empty)
            has_data = getattr(nrc, "lexicon", None) and len(getattr(nrc, "lexicon", {})) > 0
            if has_data:
                NLP_STATE["nrc_available"] = True
                NLP_STATE["nrc_exc"] = None
                logger.info(f"NRC lexicon available with {len(nrc.lexicon)} words")
            else:
                logger.warning("NRC lexicon module imported but contains no data. Check data/lexicons/nrc_emotion_lexicon.txt")
                NLP_STATE["nrc_available"] = False
                NLP_STATE["nrc_exc"] = "NRC module imported but lexicon data not loaded (file not found?)"
        else:
            raise import_error or ImportError("NRC lexicon import failed with unknown error")
            
    except Exception as e:
        NLP_STATE["nrc_available"] = False
        NLP_STATE["nrc_exc"] = repr(e)
        NLP_STATE["nrc_exc"] = repr(e)
        logger.warning("NRC lexicon not available: %s", e)

    # Record python executable for diagnostics (helps ensure Streamlit uses same env)
    NLP_STATE["python_executable"] = sys.executable

    # Provide a compact summary for logs
    summary = {
        "textblob_available": NLP_STATE["textblob_available"],
        "spacy_available": NLP_STATE["spacy_available"],
        "spacy_model_loaded": NLP_STATE["spacy_model_loaded"],
        "nrc_available": NLP_STATE["nrc_available"],
        "python_executable": NLP_STATE["python_executable"],
        "textblob_exc": NLP_STATE["textblob_exc"],
        "spacy_exc": NLP_STATE["spacy_exc"],
        "nrc_exc": NLP_STATE["nrc_exc"],
    }

    logger.info(
        "NLP warmup summary: %s",
        {k: summary[k] for k in ("textblob_available", "spacy_available", "spacy_model_loaded", "nrc_available")},
    )
    return summary
