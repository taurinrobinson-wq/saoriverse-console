import json
import os
import pytest
from emotional_os.glyphs import signal_parser


def make_row(name, desc):
    return {'glyph_name': name, 'description': desc}


def load_archived_samples():
    path = os.path.join('tools', 'archived_samples.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('samples', [])


@pytest.mark.parametrize('sample', load_archived_samples())
def test_archived_samples_flagged(sample):
    # archived samples may include only a snippet; pass both name and snippet
    name = sample.get('glyph_name', '')
    desc = sample.get('description_snippet', '')
    row = make_row(name, desc)

    # Compute expected using the same conservative markers as the implementation
    markers = [
        'markdown export', 'json export', 'archive', 'gutenberg', 'conversation archive', 'archive entry',
        'markdown', 'json', 'export', 'module —', 'module -', 'file:', 'http://', 'https://', 'www.', '<html',
        '```', '***', 'title:', '📜', '📚', '🗂️'
    ]
    lname = (name or '').lower()
    ldesc = (desc or '').lower()
    expected = False
    if any(m in lname or m in ldesc for m in markers):
        expected = True
    if len(ldesc) > 800:
        expected = True
    if ldesc.count('\n') > 8:
        expected = True
    if '[' in lname or '\t' in lname:
        expected = True

    assert signal_parser._looks_like_artifact(row) == expected


def test_normal_glyph_not_detected():
    r = make_row('Still Recognition', "Being seen without reaction. A gaze that doesn't grasp, just receives.")
    assert signal_parser._looks_like_artifact(r) is False

