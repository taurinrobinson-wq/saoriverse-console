import importlib
import sys

# Reload module to pick up recent edits
try:
    import main_response_engine as mre

    importlib.reload(mre)
except Exception as e:
    print("IMPORT ERROR:", e)
    sys.exit(1)

# Dummy ClarificationTrace to avoid blocking


class DummyTrace:
    def lookup(self, *a, **k):
        return None

    def detect_and_store(self, *a, **k):
        return {"stored": False}

    def __getattr__(self, name):
        return lambda *a, **k: None


mre._clarify_trace = DummyTrace()
# Short, local-only gesture/closing functions
mre.add_comfort_gesture = lambda emotion_key, text, position="prepend": text
mre.get_closing_prompt = lambda: "If you'd like, we can pause here."

samples = [
    ("I just met someone who really sees me.", {"emotion": "longing", "intensity": "high"}),
    ("I've been trying to understand my dad's silence lately.", {"emotion": "tender", "intensity": "gentle"}),
    ("Everything just changed. I feel like I'm spinning.", {"emotion": "overwhelm", "intensity": "high"}),
]

for text, ctx in samples:
    print("INPUT:", text)
    try:
        out = mre.process_user_input(text, ctx)
    except Exception as e:
        out = f"ERROR: {e}"
    print("OUTPUT:")
    print(out)
    print("---")
