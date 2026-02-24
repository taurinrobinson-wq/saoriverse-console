import sys, os
ROOT = os.getcwd()
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
srcp = os.path.join(ROOT, 'src')
toolsp = os.path.join(ROOT, 'tools')
if srcp not in sys.path:
    sys.path.insert(0, srcp)
if toolsp not in sys.path:
    sys.path.insert(0, toolsp)

try:
    from interactive_learning_ui import load_glyphs, simple_emotion_parser
    from responder_factory import make_responder_and_orchestrator
except Exception as e:
    print('IMPORT_FAILED', e)
    raise

glyphs = load_glyphs()
responder, orchestrator, proto_mgr = make_responder_and_orchestrator(glyphs)
ui = 'Feeling overwhelmed'
ev = simple_emotion_parser(ui)
resp = responder.respond(ui, {'user':'smoke'}, ev)
print('SMOKE_RESPONSE_START')
print(resp.response_text)
print('SMOKE_RESPONSE_END')
