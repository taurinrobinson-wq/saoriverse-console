#!/usr/bin/env python3
"""
Validate `velinor/markdowngameinstructions/Glyph_Organizer.json` against
`velinor/markdowngameinstructions/Glyph_Organizer.schema.json` using jsonschema.

Usage: from repo root run:
  py -3 scripts\validate_glyph_json.py
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
SCHEMA_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Organizer.schema.json'))
DATA_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Organizer.json'))

def main():
    try:
        import jsonschema
    except Exception:
        print('jsonschema is not installed. Please run: py -3 -m pip install jsonschema', file=sys.stderr)
        return 2

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as fh:
        schema = json.load(fh)
    with open(DATA_PATH, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if not errors:
        print('Validation successful: no errors found.')
        return 0

    print(f'Validation failed: {len(errors)} errors')
    for err in errors:
        path = '.'.join([str(p) for p in err.absolute_path]) if err.absolute_path else '(root)'
        print(f'- Path: {path}\n  Message: {err.message}\n')
    return 1

if __name__ == '__main__':
    code = main()
    sys.exit(code)
