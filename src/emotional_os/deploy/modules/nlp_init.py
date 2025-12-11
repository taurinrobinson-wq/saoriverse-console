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

    # spaCy and model
    try:
        import spacy
        import subprocess
        import os

        NLP_STATE["spacy_available"] = True
        NLP_STATE["spacy_exc"] = None
        logger.info("spaCy import successful")
        try:
            # Attempt to load the model; this may raise if the model isn't installed
            logger.info(f"Attempting to load spaCy model '{model_name}'...")
            _nlp = spacy.load(model_name)
            NLP_STATE["spacy_model_loaded"] = True
            logger.info("spaCy model '%s' loaded successfully", model_name)
        except OSError:
            # Model not found - try to download
            logger.debug(f"Model '{model_name}' not found, attempting to download...")
            
            # Detect environment - if we can't write to home, probably Streamlit Cloud
            home_dir = os.path.expanduser("~")
            can_write = os.access(home_dir, os.W_OK)
            
            if not can_write:
                logger.warning(
                    f"spaCy model '{model_name}' not available. "
                    "Running in restricted environment (likely Streamlit Cloud) with limited write permissions. "
                    "NLP features will be partially available. For full NLP support, run locally."
                )
                NLP_STATE["spacy_model_loaded"] = False
                NLP_STATE["spacy_exc"] = "Model not available in restricted environment"
            else:
                # Try downloading on systems with write access
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "spacy", "download", model_name, "--quiet"], 
                        capture_output=True, 
                        timeout=120
                    )
                    if result.returncode == 0:
                        # Try loading again after download
                        _nlp = spacy.load(model_name)
                        NLP_STATE["spacy_model_loaded"] = True
                        logger.info("spaCy model '%s' downloaded and loaded successfully", model_name)
                    else:
                        stderr = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
                        logger.warning(f"spaCy model download failed: {stderr}")
                        NLP_STATE["spacy_model_loaded"] = False
                        NLP_STATE["spacy_exc"] = f"Download failed (code {result.returncode})"
                except subprocess.TimeoutExpired:
                    logger.warning(f"spaCy model download timed out after 120 seconds")
                    NLP_STATE["spacy_model_loaded"] = False
                    NLP_STATE["spacy_exc"] = "Download timeout"
                except Exception as download_err:
                    logger.warning(f"spaCy model download error: {download_err}")
                    NLP_STATE["spacy_model_loaded"] = False
                    NLP_STATE["spacy_exc"] = str(download_err)
        except Exception as me:
            logger.warning(f"spaCy model load error: {me}")
            NLP_STATE["spacy_model_loaded"] = False
            NLP_STATE["spacy_exc"] = str(me)
    except Exception as e:
        NLP_STATE["spacy_available"] = False
        NLP_STATE["spacy_model_loaded"] = False
        NLP_STATE["spacy_exc"] = repr(e)
        logger.error("spaCy import failed: %s", e)

    # NRC Lexicon - try multiple import strategies
    try:
        nrc = None
        import_error = None
        
        # Strategy 1: Direct import (works when sys.path includes src)
        try:
            from parser.nrc_lexicon_loader import nrc  # noqa: F401
            logger.debug("NRC loaded via parser.nrc_lexicon_loader")
        except ImportError as e:
            import_error = e
        
        # Strategy 2: Full module path
        if nrc is None:
            try:
                from emotional_os.parser.nrc_lexicon_loader import nrc  # noqa: F401
                logger.debug("NRC loaded via emotional_os.parser.nrc_lexicon_loader")
            except ImportError as e:
                import_error = e
        
        # Strategy 3: Search filesystem and add path
        if nrc is None:
            from pathlib import Path
            current_file = Path(__file__)
            src_dir = None
            
            # Search up to find parser/nrc_lexicon_loader.py
            for parent in current_file.parents:
                candidate = parent / "parser" / "nrc_lexicon_loader.py"
                if candidate.exists():
                    src_dir = parent
                    logger.debug(f"Found NRC at: {candidate}")
                    break
            
            if src_dir:
                if str(src_dir) not in sys.path:
                    sys.path.insert(0, str(src_dir))
                    logger.debug(f"Added {src_dir} to sys.path")
                
                try:
                    from parser.nrc_lexicon_loader import nrc  # noqa: F401
                    logger.debug("NRC loaded after filesystem search")
                except ImportError as e:
                    import_error = e
            else:
                import_error = ImportError("Could not find parser/nrc_lexicon_loader.py in parent directories")
        
        if nrc is not None:
            NLP_STATE["nrc_available"] = True
            NLP_STATE["nrc_exc"] = None
            logger.info("NRC lexicon available")
        else:
            raise import_error or ImportError("NRC lexicon import failed with unknown error")
            
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
