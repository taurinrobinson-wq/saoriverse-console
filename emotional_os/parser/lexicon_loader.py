import json
import os

HERE = os.path.dirname(__file__)
RUNTIME_FILENAME = os.path.join(HERE, 'signal_lexicon_runtime.json')
FULL_FILENAME = os.path.join(HERE, 'signal_lexicon.json')


def load_lexicon(prefer_runtime=True):
    """Load compact runtime lexicon if present, otherwise fall back to full lexicon.

    Returns the parsed JSON object.
    """
    if prefer_runtime and os.path.exists(RUNTIME_FILENAME):
        path = RUNTIME_FILENAME
    else:
        path = FULL_FILENAME
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def load_runtime_if_available():
    return load_lexicon(prefer_runtime=True)


def get_signals(lib=None):
    if lib is None:
        lib = load_lexicon()
    return lib.get('signals', {})


def get_token_mappings(lib=None):
    if lib is None:
        lib = load_lexicon()
    # token mappings are stored at top-level keys other than 'signals'
    return {k: v for k, v in lib.items() if k != 'signals'}
