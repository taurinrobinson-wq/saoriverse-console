Velinor — Deliverable Package

What this folder should contain (not all files are copied here automatically):
- `velinor_title_transparent.png` — the title image used in the demo
- `city_market.png` — sample background used by the demo
- `Mariel_nobg.png` (or another NPC image)
- `run_demo_instructions.txt` — simple commands to run the demo

Purpose
- A minimal, shareable package that demonstrates the project's title screen and a tiny interactive placeholder scene.

How to build the package locally (PowerShell)
1. From the repo root:

```powershell
mkdir -Force deliverable
copy-item velinor_title_transparent.png deliverable\
copy-item city_market.png deliverable\
copy-item Mariel_nobg.png deliverable\
copy-item tools\run_title_demo.py deliverable\
copy-item requirements_streamlit.txt deliverable\
```

2. Add a README and any small license or contact notes.

Run the demo (recipient instructions)
1. Install Python and pip.
2. From the `deliverable` folder:

```powershell
pip install -r requirements_streamlit.txt
streamlit run run_title_demo.py
```

Notes
- This is a tiny, shareable proof-of-concept. It is not the game — it shows the title screen and a placeholder scene.
- If you want, I can produce a ZIP of `deliverable/` ready for sharing.
