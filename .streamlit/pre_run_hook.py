#!/usr/bin/env python3
"""
Pre-run hook for Streamlit deployment
Ensures spaCy model is downloaded before app starts
This avoids runtime permission errors on Streamlit Cloud/shared servers
"""
import subprocess
import sys
import logging
import os

logger = logging.getLogger(__name__)

def ensure_spacy_model(model_name: str = "en_core_web_sm"):
    """Ensure spaCy model is available before Streamlit starts.

    For environments without network access (Streamlit Cloud, restricted CI, etc.)
    the function will NOT attempt to download the model unless the
    `FIRSTPERSON_ALLOW_SPACY_DOWNLOAD` environment variable is set to
    `1`, `true`, or `yes`.
    """
    try:
        import spacy
        spacy.load(model_name)
        logger.info(f"✓ spaCy model '{model_name}' already available")
        return True
    except OSError:
        # Only attempt to download if explicitly allowed via env var
        allow_download = os.environ.get("FIRSTPERSON_ALLOW_SPACY_DOWNLOAD", "").lower()
        if allow_download in ("1", "true", "yes"):
            logger.info(f"📥 Downloading spaCy model '{model_name}'...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "spacy", "download", model_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info(f"✓ spaCy model '{model_name}' downloaded successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ Failed to download spaCy model: {e}")
                logger.warning("App will use blank 'en' pipeline instead")
                return False
        else:
            logger.info(
                "spaCy model not available and automatic download is disabled; "
                "using blank 'en' pipeline instead"
            )
            return False
    except Exception as e:
        logger.warning(f"⚠️ Error checking spaCy model: {e}")
        return False

# Do not run on import by default. Control invocation with env var
# `FIRSTPERSON_RUN_PRE_RUN_HOOK` (set to 1/true/yes to enable).
if __name__ != "__main__":
    run_hook = os.environ.get("FIRSTPERSON_RUN_PRE_RUN_HOOK", "").lower()
    if run_hook in ("1", "true", "yes"):
        ensure_spacy_model()
    else:
        logger.info("pre_run_hook disabled on import (set FIRSTPERSON_RUN_PRE_RUN_HOOK=1 to enable)")
