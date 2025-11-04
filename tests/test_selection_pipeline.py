from emotional_os.glyphs import signal_parser


def make_glyph(name, desc, gate='Gate 5'):
    return {'glyph_name': name, 'description': desc, 'gate': gate}


def test_glyph_pruning_filters():
    # Artifact-like and deprecated rows should be excluded; valid glyph should be selected
    glyphs = [
        make_glyph('[DEPRECATED] Old Entry', 'old description'),
        make_glyph('📜 Markdown Export — README v1', '### header\ncontent here'),
        make_glyph('Still Recognition', "Being seen without reaction. A gaze that doesn't grasp, just receives.")
    ]

    signals = []
    best_glyph, (response, feedback), source = signal_parser.select_best_glyph_and_response(glyphs, signals, input_text='test')

    assert best_glyph is not None
    assert best_glyph['glyph_name'] == 'Still Recognition'
    assert source in ('dynamic_composer', 'llm')


def test_selection_scores_with_signals():
    # When signal keywords indicate anxiety, glyph names with 'still'+'insight' should be preferred
    glyphs = [
        make_glyph('Containment Shield', 'Creates boundary'),
        make_glyph('Still Insight', 'Quiet revelation and noticing'),
        make_glyph('Still Ache', 'Neutral ache')
    ]
    signals = [{'keyword': 'anxious', 'signal': 'θ', 'tone': 'grief'}]

    best_glyph, (response, feedback), source = signal_parser.select_best_glyph_and_response(glyphs, signals, input_text='I feel anxious')

    assert best_glyph is not None
    # Still Insight gets bonus for 'still' and 'insight' per scoring rules
    assert best_glyph['glyph_name'] == 'Still Insight'


def test_fallback_when_no_glyphs():
    # With no glyphs and no fallback matches, should return a fallback_message
    best_glyph, (response, feedback), source = signal_parser.select_best_glyph_and_response([], [], input_text="I'm not sure")
    assert best_glyph is None
    assert source == 'fallback_message'
    assert isinstance(response, str)
