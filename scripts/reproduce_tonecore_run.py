#!/usr/bin/env python3
"""Reproduce ToneCore mapping and optionally generate audio for debugging.

Usage:
  python scripts/reproduce_tonecore_run.py --text "..." [--generate]

This script duplicates the mapping logic used by the Streamlit app without
starting Streamlit, so we can see the mapped emotion, rationale and controls.
If `--generate` is passed it will call `scripts/tonecore_midi.py` and
`fluidsynth` to create `demo_output/repro.mid` and `demo_output/repro.wav`.
"""
import sys as _sys
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
# Ensure repo root is on sys.path so imports resolve same as Streamlit run
_sys.path.insert(0, str(ROOT))
OUT = ROOT / 'demo_output'
OUT.mkdir(exist_ok=True)


def parse_input_text(text: str):
    try:
        from emotional_os.core.signal_parser import parse_input
        parsed = parse_input(text, 'emotional_os/parser/signal_lexicon.json')
        return parsed
    except Exception as e:
        print('Parser failed:', e)
        return None


def enhanced_analysis(text: str):
    try:
        from parser.enhanced_emotion_processor import EnhancedEmotionProcessor
        eproc = EnhancedEmotionProcessor()
        enhanced = eproc.analyze_emotion_comprehensive(text)
        return enhanced
    except Exception as e:
        print('Enhanced analysis failed:', e)
        return None


def map_enhanced_to_emotion(parsed: dict, enhanced: dict):
    # Copy of the heuristic from streamlit_app.py
    try:
        tones = set()
        for s in (parsed.get('signals') or []):
            t = s.get('tone')
            if t:
                tones.add(str(t).lower())
    except Exception:
        tones = set()

    nrc = enhanced.get('nrc_emotions') if enhanced else {}
    if not isinstance(nrc, dict):
        nrc = {}

    def n(name):
        try:
            return float(nrc.get(name, 0) or 0)
        except Exception:
            return 0.0

    joy = n('joy')
    sadness = n('sadness')
    trust = n('trust')
    surprise = n('surprise')
    positive = n('positive')
    polarity = 0.0
    try:
        polarity = float((enhanced.get('textblob_sentiment')
                         or {}).get('polarity', 0) or 0)
    except Exception:
        polarity = 0.0

    rationale_parts = []

    if 'intimacy' in tones:
        rationale_parts.append('parser detected "intimacy" tone')
        if sadness > 0 and joy > 0:
            rationale_parts.append(
                'mixed joy+sadness in NRC -> selecting "longing"')
            return 'longing', '; '.join(rationale_parts)
        return 'intimacy', '; '.join(rationale_parts)

    if 'love' in tones:
        rationale_parts.append('parser detected "love" tone')
        if sadness > 0 and joy > 0:
            rationale_parts.append(
                'mixed joy+sadness in NRC -> selecting "longing"')
            return 'longing', '; '.join(rationale_parts)
        if sadness > joy:
            rationale_parts.append('sadness > joy -> selecting "longing"')
            return 'longing', '; '.join(rationale_parts)
        if joy >= sadness and polarity > 0.2:
            rationale_parts.append(
                'positive polarity with dominant joy -> selecting "joy"')
            return 'joy', '; '.join(rationale_parts)

    if joy > 0 and sadness > 0:
        rationale_parts.append(
            'NRC includes both joy and sadness -> selecting "longing"')
        return 'longing', '; '.join(rationale_parts)

    if sadness > max(joy, trust, surprise) and sadness > 0:
        rationale_parts.append('sadness dominates NRC -> selecting "sadness"')
        return 'sadness', '; '.join(rationale_parts)

    if positive >= max(joy, sadness, trust) and positive > 0:
        rationale_parts.append(
            'NRC positive dominates -> selecting "contentment"')
        return 'contentment', '; '.join(rationale_parts)

    dom = (enhanced.get('dominant_emotion') if enhanced else None)
    if dom:
        rationale_parts.append(
            f'falling back to enhanced dominant_emotion: {dom}')
        return str(dom), '; '.join(rationale_parts)

    rationale_parts.append('no clear signal; defaulting to "neutral"')
    return 'neutral', '; '.join(rationale_parts)


def map_signals_to_music(parsed: dict, enhanced: dict, mapped_emotion: str):
    # Copy of mapping logic
    controls = {
        'emotion': mapped_emotion or 'neutral',
        'velocity_min': 48,
        'velocity_max': 88,
        'chord_length_beats': 4,
        'acc_program': 0,
        'lead_program': 40,
        'reverb': 48,
        'rhythm_profile': 'moderate',
        'post_reverb': False,
    }

    try:
        voltages = []
        for s in (parsed.get('signals') or []):
            v = s.get('voltage')
            if isinstance(v, (int, float)):
                voltages.append(float(v))
            elif isinstance(v, str):
                lv = v.lower()
                if lv == 'low':
                    voltages.append(0.25)
                elif lv == 'medium':
                    voltages.append(0.5)
                elif lv == 'high':
                    voltages.append(0.9)
    except Exception:
        voltages = []

    avg_v = float(sum(voltages) / len(voltages)) if voltages else 0.5

    if avg_v < 0.33:
        controls['velocity_min'] = 36
        controls['velocity_max'] = 64
        controls['chord_length_beats'] = 6
    elif avg_v < 0.66:
        controls['velocity_min'] = 54
        controls['velocity_max'] = 88
        controls['chord_length_beats'] = 4
    else:
        controls['velocity_min'] = 84
        controls['velocity_max'] = 110
        controls['chord_length_beats'] = 3

    gates = parsed.get('gates') or []
    density = 'moderate'
    if any(str(g).endswith('4') or str(g).lower().find('grief') != -1 for g in gates):
        density = 'sparse'
    if any(str(g).endswith('6') or str(g).lower().find('urgency') != -1 for g in gates):
        density = 'dense'
    if any(str(g).endswith('9') or str(g).lower().find('reflection') != -1 for g in gates):
        density = 'irregular'
    controls['rhythm_profile'] = density

    me = (mapped_emotion or '').lower()
    if me == 'longing':
        controls['acc_program'] = 48
        controls['lead_program'] = 52
        controls['reverb'] = 96
        controls['post_reverb'] = True
        controls['chord_length_beats'] = max(controls['chord_length_beats'], 6)
    elif me == 'intimacy':
        controls['acc_program'] = 0
        controls['lead_program'] = 40
        controls['reverb'] = 100
        controls['post_reverb'] = True
    elif me == 'joy':
        controls['acc_program'] = 0
        controls['lead_program'] = 24
        controls['reverb'] = 36
    elif me == 'sadness':
        controls['acc_program'] = 48
        controls['lead_program'] = 42
        controls['reverb'] = 110
        controls['post_reverb'] = True

    try:
        polarity = float((enhanced.get('textblob_sentiment')
                         or {}).get('polarity', 0) or 0)
        if polarity > 0.4:
            controls['velocity_min'] = min(controls['velocity_min'] + 6, 127)
            controls['velocity_max'] = min(controls['velocity_max'] + 10, 127)
        elif polarity < -0.3:
            controls['velocity_min'] = max(8, controls['velocity_min'] - 8)
            controls['velocity_max'] = max(16, controls['velocity_max'] - 12)
    except Exception:
        pass

    return controls


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--text', required=True)
    p.add_argument('--generate', action='store_true')
    args = p.parse_args()

    parsed = parse_input_text(args.text)
    print('\nParsed signals:')
    print(json.dumps(parsed or {}, indent=2))

    enhanced = enhanced_analysis(args.text)
    print('\nEnhanced analysis:')
    print(json.dumps(enhanced or {}, indent=2))

    mapped, rationale = map_enhanced_to_emotion(parsed or {}, enhanced or {})
    print('\nMapped emotion:', mapped)
    print('Rationale:', rationale)

    controls = map_signals_to_music(parsed or {}, enhanced or {}, mapped)
    print('\nMusic controls:')
    print(json.dumps(controls, indent=2))

    controls_path = OUT / 'tonecore_controls_repro.json'
    controls_path.write_text(json.dumps(controls), encoding='utf8')
    print('\nWrote controls to', controls_path)

    if args.generate:
        midi_out = OUT / 'repro.mid'
        wav_out = OUT / 'repro.wav'
        # call the existing MIDI generator
        cmd = [sys.executable, str(ROOT / 'scripts' / 'tonecore_midi.py'),
               '--emotion', mapped, '--out', str(midi_out), '--controls', str(controls_path)]
        print('Running:', ' '.join(shlex.quote(x) for x in cmd))
        subprocess.check_call(cmd)
        sf2 = ROOT / 'Offshoots' / 'ToneCore' / 'sf2' / 'FluidR3_GM.sf2'
        if not sf2.exists():
            print('Warning: SF2 not found at', sf2)
        else:
            fs_cmd = ['fluidsynth', '-ni',
                      str(sf2), str(midi_out), '-F', str(wav_out), '-r', '44100']
            print('Running:', ' '.join(shlex.quote(x) for x in fs_cmd))
            subprocess.check_call(fs_cmd)
            print('Rendered WAV:', wav_out)


if __name__ == '__main__':
    main()
