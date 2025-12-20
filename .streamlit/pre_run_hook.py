#!/usr/bin/env python3
"""
Pre-run hook for Streamlit deployment
Ensures spaCy model is downloaded before app starts
This avoids runtime permission errors on Streamlit Cloud/shared servers
"""
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def ensure_spacy_model(model_name: str = "en_core_web_sm"):
    """Ensure spaCy model is available before Streamlit starts"""
    try:
        import spacy
        spacy.load(model_name)
        logger.info(f"✓ spaCy model '{model_name}' already available")
        return True
    except OSError:
        logger.info(f"📥 Downloading spaCy model '{model_name}'...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", model_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(f"✓ spaCy model '{model_name}' downloaded successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Failed to download spaCy model: {e}")
            logger.warning("App will use blank 'en' pipeline instead")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Error checking spaCy model: {e}")
        return False

# Run on import
if __name__ != "__main__":
    ensure_spacy_model()
