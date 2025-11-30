"""Simple Streamlit demo: Dance Mode 🕺

This lightweight demo provides an ASCII dance animation with an
accessibility-conscious alternation of background colors and a
``gentle_mode`` toggle to disable flashing.

Usage:
    streamlit run demos/streamlit_dance_mode.py

The animation intentionally uses a relatively slow 500ms frame delay
and neutral greys for background flashing to reduce photosensitivity
risk. Consumers may adjust `cycles` or `delay_s` as needed.
"""

from __future__ import annotations

import time
from typing import Iterable

import streamlit as st


def dance_mode(frames: Iterable[str] | None = None, cycles: int = 10, delay_s: float = 0.5, gentle_mode: bool = False):
    """Run a short ASCII dance animation in Streamlit.

    - `frames`: iterable of ASCII frames. Default is a small 4-frame loop.
    - `cycles`: number of loop cycles to perform.
    - `delay_s`: seconds between frames (default 0.5s).
    - `gentle_mode`: if True, disable background flashing (use a single neutral bg).

    This function writes HTML into the Streamlit page and updates it
    in-place using a placeholder. It returns once the animation finishes.
    """
    default_frames = [
        "(>'-')>   <('-'<)   ^('-')^   v('-')v",
        "<('-'<)   (>'-')>   ^('-')^   v('-')v",
        "^('-')^   v('-')v   (>'-')>   <('-'<)",
        "(>'-')>   ^('-')^   <('-'<)   v('-')v",
    ]
    frames = list(frames or default_frames)
    colors = ["#333333", "#DDDDDD"]  # dark grey, light grey

    placeholder = st.empty()

    for i in range(cycles * len(frames)):
        frame = frames[i % len(frames)]
        if gentle_mode:
            bg = "#F8F8F8"
        else:
            bg = colors[i % len(colors)]

        html = (
            f"<div style='background-color:{bg};padding:16px;border-radius:8px;'>"
            f"<pre style='font-size:22px;margin:0;padding:0;font-family:monospace;'>{frame}</pre>"
            "</div>"
        )

        placeholder.markdown(html, unsafe_allow_html=True)

        # Respect the Streamlit execution model; short sleep is okay for demo.
        time.sleep(max(0.1, float(delay_s)))


def main():
    st.title("Dance Mode 🕺 — Demo")

    st.write("Press the button to run a short celebratory ASCII dance.")

    gentle_mode = st.checkbox("Gentle mode (no flashing)", value=True)
    cycles = st.slider("Cycles", min_value=1, max_value=20, value=6)
    delay_s = st.slider("Frame delay (s)", min_value=0.1, max_value=1.5, value=0.5)

    if st.button("Dance Mode 🕺"):
        dance_mode(cycles=cycles, delay_s=delay_s, gentle_mode=gentle_mode)


if __name__ == "__main__":
    main()
