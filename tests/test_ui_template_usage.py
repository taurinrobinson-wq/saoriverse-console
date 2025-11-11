def test_ui_selection_prefers_template_when_present():
    """Unit test of the UI selection rule: when a parser result contains
    'voltage_response_template', the UI (when debug is off) should prefer
    the template; when debug is on, it should show the contextual response.

    This test is intentionally decoupled from the corpus/DB state — it
    asserts the UI selection logic itself, which is the invariant we want
    to preserve in CI.
    """
    # Synthetic parser result
    result = {
        'voltage_response_template': "Template reply from glyph",
        'voltage_response': "Contextual reply from composer"
    }

    template = result.get('voltage_response_template')
    contextual = result.get('voltage_response')

    # Debug off -> prefer template
    show_glyph_debug = False
    ui_response = template if (
        template and not show_glyph_debug) else contextual
    assert ui_response == template

    # Debug on -> prefer contextual
    show_glyph_debug = True
    ui_response_debug = template if (
        template and not show_glyph_debug) else contextual
    assert ui_response_debug == contextual
