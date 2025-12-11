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

    # spaCy and model
    try:
        import spacy

        NLP_STATE["spacy_available"] = True
        NLP_STATE["spacy_exc"] = None
        logger.info("spaCy import successful")
        try:
            # Attempt to load the model; this may raise if the model isn't installed
            logger.info(f"Attempting to load spaCy model '{model_name}'...")
            _nlp = spacy.load(model_name)
            NLP_STATE["spacy_model_loaded"] = True
            logger.info("spaCy model '%s' loaded", model_name)
        except Exception as me:
            # Try to download the model if it's missing
            logger.debug(f"Model load failed: {me}, attempting to download...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, "-m", "spacy", "download", model_name], 
                                      capture_output=True, timeout=60)
                if result.returncode == 0:
                    # Try loading again after download
                    _nlp = spacy.load(model_name)
                    NLP_STATE["spacy_model_loaded"] = True
                    logger.info("spaCy model '%s' downloaded and loaded successfully", model_name)
                else:
                    raise Exception(f"Download failed with code {result.returncode}")
            except Exception as download_err:
                NLP_STATE["spacy_model_loaded"] = False
                NLP_STATE["spacy_exc"] = repr(me)
                logger.error("spaCy model '%s' could not be loaded or downloaded: %s", model_name, download_err)
    except Exception as e:
        NLP_STATE["spacy_available"] = False
        NLP_STATE["spacy_model_loaded"] = False
        NLP_STATE["spacy_exc"] = repr(e)
        logger.error("spaCy import failed: %s", e)

    # NRC Lexicon
    try:
        # Try multiple import paths for robustness
        nrc = None
        
        # Try direct import first (works when sys.path includes src)
        try:
            from parser.nrc_lexicon_loader import nrc  # noqa: F401
        except ImportError:
            pass
        
        # Try emotional_os.parser path
        if nrc is None:
            try:
                from emotional_os.parser.nrc_lexicon_loader import nrc  # noqa: F401
            except ImportError:
                pass
        
        # Try absolute sys.path manipulation
        if nrc is None:
            from pathlib import Path
            # Find the src directory by looking for parser/nrc_lexicon_loader.py
            current_file = Path(__file__)
            # nlp_init.py is at: src/emotional_os/deploy/modules/nlp_init.py
            # We need to find src directory
            src_dir = None
            for parent in current_file.parents:
                if (parent / "parser" / "nrc_lexicon_loader.py").exists():
                    src_dir = parent
                    break
            
            if src_dir:
                if str(src_dir) not in sys.path:
                    sys.path.insert(0, str(src_dir))
                from parser.nrc_lexicon_loader import nrc  # noqa: F401
            else:
                raise ImportError("Could not locate nrc_lexicon_loader.py by searching parent directories")
        
        NLP_STATE["nrc_available"] = True
        NLP_STATE["nrc_exc"] = None
        logger.info("NRC lexicon available")
    except Exception as e:
        NLP_STATE["nrc_available"] = False
        NLP_STATE["nrc_exc"] = repr(e)
        logger.error("NRC lexicon not available: %s", e)

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
