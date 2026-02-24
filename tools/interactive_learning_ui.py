"""Interactive CLI to test learning flow and show running logs.

Usage:
  python tools/interactive_learning_ui.py        # start interactive loop
  python tools/interactive_learning_ui.py demo  # run a short scripted demo

The script attempts to load existing glyphs if available, otherwise falls
back to a small sample glyph set. It logs events to `learning/interactive_log.jsonl`.
"""
import sys
import os
import json
from types import SimpleNamespace
from datetime import datetime

# Ensure repo src is on path
ROOT = os.getcwd()
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

LOG_PATH = os.path.join(ROOT, "learning", "interactive_log.jsonl")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def append_log(entry: dict):
    entry["timestamp"] = datetime.now().isoformat()
    with open(LOG_PATH, "a", encoding="utf8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_glyphs():
    # Try common loader points
    try:
        import emotional_os_learning
        if hasattr(emotional_os_learning, "get_glyph_library"):
            return emotional_os_learning.get_glyph_library()
    except Exception:
        pass

    # Prefer the curated lexicon file if present
    lex_path = os.path.join(ROOT, "emotional_os", "glyphs", "glyph_lexicon_rows.json")
    if os.path.exists(lex_path):
        try:
            with open(lex_path, "r", encoding="utf8") as f:
                rows = json.load(f)

            # Convert rows to glyph library with simple heuristic emotional vectors
            def compute_vector(text, activation_signals):
                # indices: 0:anger,1:joy,2:trust,3:fear,4:surprise,5:sadness,6:disgust,7:anticipation
                vec = [0.0] * 8
                t = (text or "").lower()
                # keywords
                if any(w in t for w in ("angry", "anger", "mad", "furious")):
                    vec[0] = 1.0
                if any(w in t for w in ("joy", "joyful", "jubilant", "bliss", "happy", "delight")):
                    vec[1] = 1.0
                if any(w in t for w in ("trust", "safe", "seen", "recognized", "recognition")):
                    vec[2] = 1.0
                if any(w in t for w in ("fear", "scared", "afraid", "panic")):
                    vec[3] = 1.0
                if any(w in t for w in ("surprise", "surprising", "astonish")):
                    vec[4] = 0.7
                if any(w in t for w in ("sad", "grief", "mourning", "ache", "sorrow")):
                    vec[5] = 1.0
                if any(w in t for w in ("disgust", "disgusting", "repel")):
                    vec[6] = 0.9
                if any(w in t for w in ("anticipat", "anticipation", "yearn", "longing", "yearning")):
                    vec[7] = 0.9

                # boost from activation_signals hints (simple mapping)
                sig = (activation_signals or "").lower()
                if "λ" in sig or "lambda" in sig:
                    vec[1] = max(vec[1], 0.9)
                if "θ" in sig:
                    vec[5] = max(vec[5], 0.9)
                if "γ" in sig:
                    vec[7] = max(vec[7], 0.6)
                if "α" in sig:
                    vec[2] = max(vec[2], 0.6)

                # normalize to sum 1-ish
                s = sum(vec)
                if s > 0:
                    vec = [v / s for v in vec]
                else:
                    vec[1] = 0.1
                return vec

            glyphs = {}
            for row in rows:
                name = row.get("glyph_name") or f"glyph_{row.get('id')}"
                desc = row.get("description", "")
                sigs = row.get("activation_signals", "")
                vec = compute_vector(name + " " + desc, sigs)
                glyphs[name] = {
                    "emotional_vector": vec,
                    "response_template": row.get("description", "{user_input}"),
                }
            return glyphs
        except Exception:
            pass

    # Try other JSON file locations
    possible = [
        os.path.join(SRC, "emotional_os", "glyphs", "glyphs.json"),
        os.path.join(SRC, "emotional_os", "glyphs", "glyphs.db"),
    ]
    for p in possible:
        if os.path.exists(p) and p.endswith(".json"):
            try:
                with open(p, "r", encoding="utf8") as f:
                    return json.load(f)
            except Exception:
                pass

    # Fallback sample glyphs
    return {
        "warm": {
            "emotional_vector": [0.05, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "response_template": "I sense warmth when you say: {user_input}",
        },
        "sad": {
            "emotional_vector": [0.0, 0.0, 0.0, 0.1, 0.0, 0.9, 0.0, 0.0],
            "response_template": "I'm sorry to hear that. Tell me more about {user_input}",
        },
    }


def simple_emotion_parser(text: str):
    # Return 8-dim vector for [anger,joy,trust,fear,surprise,sadness,disgust,anticipation]
    vec = [0.0] * 8
    t = text.lower()
    if any(w in t for w in ("happy", "love", "lovely", "joy", "great")):
        vec[1] = 0.9
    if any(w in t for w in ("angry", "mad", "furious", "upset")):
        vec[0] = 0.9
    if any(w in t for w in ("sorry", "sad", "upset", "unhappy", "grief")):
        vec[5] = 0.9
    if any(w in t for w in ("scared", "afraid", "fear", "panic")):
        vec[3] = 0.9
    # Heuristic: short questions asking about mood/feeling indicate
    # curiosity/anticipation rather than a strong primary emotion.
    # This helps prompts like "If you had a mood right now, what would it be?"
    # avoid returning all-zero vector which makes downstream processing unreliable.
    question_terms = ("mood", "feel", "feeling", "how are you", "what would", "if you had")
    is_question = "?" in t or any(q in t for q in question_terms)
    if is_question and sum(vec) == 0:
        vec[7] = 0.6  # anticipation / curiosity
        vec[2] = 0.2  # trust / openness
    # small baseline
    if sum(vec) == 0:
        vec[1] = 0.1
    return vec


def make_responder_and_orchestrator(glyphs):
    from emotional_os_learning.subordinate_bot_responder import SubordinateBotResponder
    from emotional_os_learning.dominant_bot_orchestrator import DominantBotOrchestrator

    # Dummy tiers
    class DummyTier:
        def wrap_response(self, text, ctx):
            return text
        def attune_presence(self, text, ctx):
            return text
        def enrich_with_poetry(self, text, ctx):
            return text

    responder = SubordinateBotResponder(DummyTier(), DummyTier(), DummyTier(), glyph_library=glyphs)

    # Proto manager stub: use simple in-memory manager for creation
    class SimpleProtoManager:
        def __init__(self):
            self.proto_glyphs = {}
            self.clusters = {}

        def create_proto(self, data):
            # backward-compatible alias if orchestrator calls create_proto
            return self.create_proto_glyph(data)

        def create_proto_glyph(self, user_input_or_data=None, subordinate_response=None, emotional_vector=None, metadata=None, **kwargs):
            # Accept either a dict or separate args; accept extra kwargs from orchestrator
            pid = f"p{len(self.proto_glyphs)+1}"
            # Example text may be provided as 'example_text' or inside a dict
            text = ""
            if isinstance(user_input_or_data, dict):
                text = user_input_or_data.get("text", "")
            elif user_input_or_data is not None:
                text = str(user_input_or_data)
            if not text:
                text = kwargs.get("example_text") or kwargs.get("text") or ""
            self.proto_glyphs[pid] = SimpleNamespace(id=pid, promoted=False, example_texts=[text])
            return pid

        def cluster_proto_glyphs(self, **kwargs):
            return []

        def get_stable_clusters(self, **kwargs):
            return []

        def promote_to_glyph(self, cluster, glyph_name, glyph_symbol, gate_logic=None):
            return {"name": glyph_name, "symbol": glyph_symbol}

    proto_mgr = SimpleProtoManager()
    orchestrator = DominantBotOrchestrator(proto_mgr)

    return responder, orchestrator, proto_mgr


def run_loop():
    glyphs = load_glyphs()
    responder, orchestrator, proto_mgr = make_responder_and_orchestrator(glyphs)
    from emotional_os_learning.hybrid_learner import get_hybrid_learner
    hybrid = get_hybrid_learner()

    # Adjustable threshold for dominant triggering (can be overridden via /set_threshold)
    dominant_threshold = 0.4

    print("Interactive learning UI. Type '/help' for commands.")
    while True:
        try:
            txt = input('\nYou: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting')
            break

        if not txt:
            continue
        if txt.startswith("/"):
            cmd = txt.lstrip("/")
            parts = cmd.split()
            verb = parts[0]
            args = parts[1:]
            if verb in ("quit", "exit"):
                break
            if verb == "consolidate":
                from emotional_os_learning.learning_pipeline import BackgroundLearningPipeline
                blp = BackgroundLearningPipeline(proto_mgr, glyph_synthesizer=None, consolidation_interval_hours=0)
                res = blp.consolidate_once()
                print("[BLP]", res)
                append_log({"event":"consolidate", "result": res})
                continue
            if verb == "help":
                print("Commands: /consolidate /exit /quit /show_glyphs /show_protos /set_threshold <value> /show_threshold /load_lexicon")
                continue
            # New commands
            if verb == "show_glyphs":
                print(f"Loaded {len(glyphs)} glyphs")
                for i, (name, g) in enumerate(list(glyphs.items())[:50], start=1):
                    vec = g.get("emotional_vector", [])
                    top_idx = max(range(len(vec)), key=lambda k: vec[k]) if vec else None
                    print(f"{i}. {name} - top:{top_idx} conf:{(vec[top_idx] if vec else 0):.2f}")
                continue
            if verb == "show_protos":
                print("Proto manager proto_glyphs:")
                for pid, obj in proto_mgr.proto_glyphs.items():
                    ex = getattr(obj, 'example_texts', [])
                    print(f"{pid}: promoted={getattr(obj,'promoted',False)} examples={ex}")
                continue
            if verb == "set_threshold":
                try:
                    dominant_threshold = float(args[0])
                    print(f"dominant_threshold set to {dominant_threshold}")
                except Exception:
                    print("Usage: /set_threshold 0.4")
                continue
            if verb == "show_threshold":
                print(f"dominant_threshold={dominant_threshold}")
                continue
            if verb == "load_lexicon":
                glyphs = load_glyphs()
                responder.glyph_library = glyphs
                print(f"Reloaded glyphs: {len(glyphs)} entries")
                continue
            print("Unknown command; try /help")
            continue

        # Parse emotions
        emotional_vector = simple_emotion_parser(txt)

        # Subordinate responds
        resp = responder.respond(txt, {"user":"interactive"}, emotional_vector)
        print(f"[SUB] glyph={resp.glyph_name} conf={resp.confidence:.2f} -> {resp.response_text}")
        append_log({"event":"subordinate_response","user_input":txt,"glyph":resp.glyph_name,"confidence":resp.confidence})

        # Dominant observes
        dom_analysis = orchestrator.observe_exchange(txt, {"response": resp.response_text, "confidence": resp.confidence}, emotional_vector)
        # Use adjustable threshold override: if mismatch > dominant_threshold => trigger
        mismatch = getattr(dom_analysis, 'mismatch_degree', getattr(dom_analysis, 'confidence', 0.0))
        if mismatch > dominant_threshold:
            print(f"[DOM] Triggered proto creation (mismatch={mismatch:.2f}, threshold={dominant_threshold:.2f})")
            append_log({"event":"dominant_trigger","mismatch":mismatch})
        else:
            print(f"[DOM] No action (mismatch={mismatch:.2f}, threshold={dominant_threshold:.2f})")
            append_log({"event":"dominant_observe","mismatch":mismatch})

        # Hybrid learner
        try:
            ok = hybrid.learn_from_exchange(txt, resp.response_text, emotional_signals=None, glyphs=[{"glyph_name": resp.glyph_name}])
            print(f"[HYB] learned={ok}")
            append_log({"event":"hybrid_learn","ok": ok})
        except Exception as e:
            print("[HYB] error:", e)
            append_log({"event":"hybrid_error","error": str(e)})


def run_demo():
    samples = [
        "I had a lovely morning and I feel so happy",
        "I'm really scared about the results",
        "I'm angry at what happened yesterday",
    ]
    glyphs = load_glyphs()
    responder, orchestrator, proto_mgr = make_responder_and_orchestrator(glyphs)
    from emotional_os_learning.hybrid_learner import get_hybrid_learner
    hybrid = get_hybrid_learner()

    for s in samples:
        print('\n>>', s)
        ev = simple_emotion_parser(s)
        resp = responder.respond(s, {"user":"demo"}, ev)
        print(f"[SUB] glyph={resp.glyph_name} conf={resp.confidence:.2f} -> {resp.response_text}")
        dom = orchestrator.observe_exchange(s, {"response": resp.response_text, "confidence": resp.confidence}, ev)
        if dom.should_create_proto:
            print(f"[DOM] triggered (mismatch {dom.mismatch_degree:.2f})")
        else:
            print(f"[DOM] quiet (mismatch {dom.mismatch_degree:.2f})")
        ok = hybrid.learn_from_exchange(s, resp.response_text, emotional_signals=None, glyphs=[{"glyph_name": resp.glyph_name}])
        print(f"[HYB] learned={ok}")
        append_log({"event":"demo_step","input":s,"glyph":resp.glyph_name,"dom_mismatch": dom.mismatch_degree, "learned": ok})


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        run_loop()
