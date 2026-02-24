import sys, os
ROOT = os.getcwd()
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
srcp = os.path.join(ROOT, 'src')
if srcp not in sys.path:
    sys.path.insert(0, srcp)

from src.emotional_os.deploy.modules.ui_components.session_manager import (
    initialize_session_state, get_conversation_context, add_exchange_to_history
)
from src.emotional_os.deploy.modules.ui_components.response_handler import handle_response_pipeline

# Initialize session state
initialize_session_state()

transcript = [
    "ugh",
    "I don't know just kind of over things lately. could use a little pep and fortune flowing in.",
    "Since my divorce, I just feel like my life has been filled with struggles week after week. I'm in a great relationship now with an amazing person and that helps but my mood is just dragging",
    "Yah basically. I'm stretched thin, but I feel like I can't give myself any grace in it, you know?",
    "I don't know. I feel like it would just be like some of the tension in my body melted away. Right now I'm frozen in place",
    "you already asked me that. not helpful",
]

for ui in transcript:
    ctx = get_conversation_context()
    resp, t = handle_response_pipeline(ui, ctx)
    print('\nUSER:', ui)
    print('ASSISTANT:', resp)
    add_exchange_to_history(ui, resp, metadata={"processing_time": f"{t:.2f}s"})
