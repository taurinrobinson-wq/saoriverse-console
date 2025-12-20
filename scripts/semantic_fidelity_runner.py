#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / 'src'))

from DraftShift.core import split_sentences, detect_tone, shift_tone, TONES
from DraftShift.signal_parser import parse_signal
from DraftShift.glyph_mapper import map_signals_to_glyphs
from DraftShift.nuance_extractor import extract_nuance
from DraftShift.meaning_preserver import preserve_meaning
from DraftShift.smoothing import smooth_text

SAMPLES = [
    ("Aggressive Insult", "You're really awful. I'm done talking."),
    ("Professional Critique", "This report is insufficient and fails to address key points."),
    ("Empathetic", "I appreciate your effort, but I'm worried about the timeline."),
    ("Neutral Statement", "We met yesterday to discuss the proposal."),
    ("Friendly Request", "Could you please send the files? Thanks so much!"),
]


def evaluate_sample(name, text):
    print(f"\nSample: {name}")
    sentences = split_sentences(text)
    for s in sentences:
        print(f"  Sentence: {s}")
        sig_o = parse_signal(s)
        glyph_o = map_signals_to_glyphs(sig_o)
        nuance_o = extract_nuance(s)
        print(f"    Signals(orig): {sig_o}")
        print(f"    Glyph(orig):   {glyph_o}")
        print(f"    Nuance(orig):  {nuance_o}")

    for target in TONES:
        print(f"\n  -> Target tone: {target}")
        transformed_sentences = [shift_tone(s, target) for s in sentences]
        transformed = ' '.join(transformed_sentences)
        transformed = smooth_text(transformed)
        print(f"     Transformed: {transformed}")

        # analyze transformed
        sig_t = parse_signal(transformed)
        glyph_t = map_signals_to_glyphs(sig_t)
        nuance_t = extract_nuance(transformed)
        pm_passed, pm_details = preserve_meaning(text, transformed)

        print(f"     Signals(new): {sig_t}")
        print(f"     Glyph(new):   {glyph_t}")
        print(f"     Nuance(new):  {nuance_t}")
        print(f"     MeaningPreserved: {pm_passed} details={pm_details}")

    print('\n' + '-'*60)


if __name__ == '__main__':
    for name, text in SAMPLES:
        evaluate_sample(name, text)
