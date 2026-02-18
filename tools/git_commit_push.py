import subprocess, sys
cmds = [
    ['git','add','tools/dominant_batch_processor.py','tools/feedback_store.py','tools/streamlit_chat_ui.py'],
    ['git','commit','-m','learning: dominant batch processor - match feedback to turns and emit training data'],
    ['git','push','origin','main'],
]
for c in cmds:
    print('RUN:', ' '.join(c))
    p = subprocess.run(c, capture_output=True, text=True)
    print('EXIT', p.returncode)
    if p.stdout:
        print(p.stdout)
    if p.stderr:
        print(p.stderr)
    if p.returncode != 0:
        sys.exit(p.returncode)
print('ALL_DONE')
