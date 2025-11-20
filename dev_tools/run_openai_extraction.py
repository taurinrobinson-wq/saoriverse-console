#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
import re

# Gate remote AI usage
try:
    from scripts.local_integration import remote_ai_allowed, remote_ai_error
except Exception:
    # Fallback: if helper not available, be conservative and disallow remote AI
    def remote_ai_allowed():
        return False

    def remote_ai_error(msg: str = None):
        raise RuntimeError(
            msg or "Remote AI usage is not allowed in this environment")

if not remote_ai_allowed():
    remote_ai_error(
        "OpenAI calls are disabled by default. Set PROCESSING_MODE!=local or ALLOW_REMOTE_AI=1 to enable."
    )

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise SystemExit("OPENAI_API_KEY not found in environment")

messages = [
    "I feel unmoored and need something to hold onto",
    "I'm furious about how they dismissed me at work",
    "I miss her so much it aches",
    "There's a quiet joy in watching them sleep",
    "I'm overwhelmed by everything I'm carrying"
]

system = (
    "Extract concise 'glyphs' from user messages. A glyph is a named "
    "emotional/experiential construct and may include a response layer (inner reflection, grounding, outreach), "
    "and a rough depth from 1-5. Return only valid JSON having a top-level key 'glyphs' which is an array of objects. "
    "Each glyph object should have: name (snake_case), description (<=120 chars), optional response_layer, optional depth (1-5), optional glyph_type, optional symbolic_pairing."
)

API_URL = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENAI_KEY}",
    "Content-Type": "application/json",
}

results = []

for msg in messages:
    prompt_user = 'User message: "{}". Return JSON with an array "glyphs", each: {{ "name": "string (snake_case)", "description": "string (<=120 chars)", "response_layer"?: "string", "depth"?: "number(1-5)", "glyph_type"?: "string", "symbolic_pairing"?: "string" }}'.format(
        msg)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": 0.3,
        "max_tokens": 600
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=data, headers=headers, method="POST")
    raw_text = None
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            j = json.loads(body)
            # OpenAI v1 chat completions: choices[0].message.content
            raw_text = j.get("choices", [])[0].get("message", {}).get(
                "content") if j.get("choices") else None
    except urllib.error.HTTPError as he:
        raw_text = he.read().decode('utf-8')
        results.append(
            {"message": msg, "error": f"HTTPError {he.code}", "raw": raw_text})
        continue
    except Exception as e:
        results.append({"message": msg, "error": str(e)})
        continue

    parsed = {"glyphs": []}
    if raw_text:
        # Try direct JSON parse
        try:
            parsed = json.loads(raw_text)
        except Exception:
            # Fallback: extract first JSON object from text
            m = re.search(r"(\{[\s\S]*\})", raw_text)
            if m:
                try:
                    parsed = json.loads(m.group(1))
                except Exception:
                    parsed = {"glyphs": []}
            else:
                parsed = {"glyphs": []}
    else:
        parsed = {"glyphs": []}

    glyphs = parsed.get("glyphs") if isinstance(parsed, dict) else []
    if not isinstance(glyphs, list):
        glyphs = []

    results.append({"message": msg, "glyphs": glyphs, "raw": raw_text})

print(json.dumps(results, ensure_ascii=False, indent=2))
