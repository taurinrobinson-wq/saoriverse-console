"""
Deterministic + pluggable LLM dialogue scaffold for REMNANTS-driven NPC lines.
- Provides `generate_line(npc_name, remnants, variant='deterministic')` API
- Deterministic pipeline uses small rule-based emotion/sentiment/syntax shaping
- LLM variant is a stub that can be wired to Ollama/OpenAI later

Designed to run without optional NLP libraries; will use them when available.
"""
from typing import Dict, Optional
import json
import os

# Try optional NLP libs; fall back gracefully if missing
try:
    from nrclex import NRCLex
    HAS_NRC = True
except Exception:
    HAS_NRC = False

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except Exception:
    HAS_TEXTBLOB = False

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except Exception:
    nlp = None
    HAS_SPACY = False

# LLM client support (optional)
try:
    import openai
    HAS_OPENAI = True
except Exception:
    openai = None
    HAS_OPENAI = False

try:
    # simple local ollama client wrapper if installed; fallback safe
    import ollama
    HAS_OLLAMA = True
except Exception:
    ollama = None
    HAS_OLLAMA = False
    # we'll try CLI fallback later via subprocess when needed
    import shutil
    HAS_OLLAMA_CLI = shutil.which("ollama") is not None
    del shutil
    # HTTP requests fallback
    try:
        import requests
        HAS_REQUESTS = True
    except Exception:
        requests = None
        HAS_REQUESTS = False
# Simple local mappings used when libs not available
TRAIT_EMOTION_POOL = {
    "skepticism": ["doubt", "caution", "shadow"],
    "empathy": ["care", "warmth", "shared"],
    "trust": ["faith", "steadiness", "anchor"],
    "resolve": ["steadfast", "firm", "certain"],
    "memory": ["recall", "record", "archive"],
    "nuance": ["balance", "shade", "layered"],
    "authority": ["command", "lead", "decree"],
    "need": ["want", "hunger", "longing"]
}

# Prompt variables (fallback location)
PROMPT_VARS_PATH = os.path.join("velinor", "markdowngameinstructions", "llm_prompt_vars.json")
try:
    with open(PROMPT_VARS_PATH, "r", encoding="utf-8") as fh:
        PROMPT_VARS = json.load(fh)
except Exception:
    PROMPT_VARS = {
        "trust": {"emotion": "faith", "syntax": "affirmation"},
        "skepticism": {"emotion": "distrust", "syntax": "conditional"},
        "empathy": {"emotion": "compassion", "syntax": "inclusive"}
    }


def _dominant_trait(remnants: Dict[str, float]) -> str:
    return max(remnants.items(), key=lambda kv: kv[1])[0]


def _deterministic_sentence(npc_name: str, dominant: str, remnants: Dict[str, float], persona_text: Optional[str] = None) -> str:
    """Generate a deterministic line based on dominant trait, small rule set."""
    pool = TRAIT_EMOTION_POOL.get(dominant, [dominant])
    word = pool[0]

    # sentiment heuristic
    if HAS_TEXTBLOB:
        # use sentiment of a short template to modulate tone
        polarity = TextBlob(dominant).sentiment.polarity
    else:
        # simple heuristic: empathy/trust => positive, skepticism => negative
        if dominant in ("empathy", "trust"):
            polarity = 0.4
        elif dominant in ("skepticism",):
            polarity = -0.4
        else:
            polarity = 0.0

    # basic syntax shaping
    if dominant == "skepticism":
        template = "Although I hear you, {npc}, I cannot ignore the {word} in your words."
    elif dominant == "empathy":
        template = "I feel the {word} you carry; perhaps we can share it together, {npc}."
    elif dominant == "trust":
        template = "I believe you now; your presence steadies me, {npc}."
    elif dominant == "memory":
        template = "The records remember what we forget; the archive speaks true, {npc}."
    elif dominant == "nuance":
        template = "On one hand, there is {word}; on the other, there is also reason to be gentle, {npc}."
    else:
        template = "{npc} says: I am guided by {word} in this moment."

    sentence = template.format(npc=npc_name, word=word)

    # optionally include a persona hint
    if persona_text:
        sentence = sentence + " — " + persona_text.splitlines()[0]

    return sentence


def _read_persona(npc_name: str) -> Optional[str]:
    path = os.path.join("velinor", "markdowngameinstructions", "llm_templates", f"{npc_name.lower().replace(' ', '_')}_persona.md")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except Exception:
        return None


def generate_line(npc_name: str, remnants: Dict[str, float], tone: Optional[str] = None, variant: str = "deterministic") -> str:
    """
    Generate a dialogue line for an NPC.

    Args:
        npc_name: name string (must match persona filename when present)
        remnants: REMNANTS trait dict
        tone: optional override (e.g., 'empathy','trust')
        variant: 'deterministic' or 'llm'

    Returns:
        Generated dialogue line string.
    """
    dominant = tone if tone else _dominant_trait(remnants)
    persona = _read_persona(npc_name)

    if variant == "deterministic":
        return _deterministic_sentence(npc_name, dominant, remnants, persona_text=persona)

    # LLM variant: try to call configured provider (OpenAI or Ollama)
    if variant == "llm":
        from velinor.config import llm_config

        prompt_payload = {
            "npc": npc_name,
            "dominant_trait": dominant,
            "remnants": remnants,
            "persona": persona,
            "prompt_vars": PROMPT_VARS.get(dominant, {})
        }

        provider = getattr(llm_config, "PROVIDER", "stub")

        # OpenAI path
        if provider == "openai" and HAS_OPENAI:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return "[LLM-ERROR] OPENAI_API_KEY not set"
            openai.api_key = api_key
            model = getattr(llm_config, "MODEL", "gpt-3.5-turbo")
            try:
                system = (persona or f"You are playing {npc_name}.")
                user_prompt = (
                    f"Persona: {system}\nTrait: {dominant}\nPromptVars: {PROMPT_VARS.get(dominant,{})}\nGenerate a single concise line in-character."
                )
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user_prompt}],
                    max_tokens=60,
                    temperature=0.8
                )
                text = resp.choices[0].message.content.strip()
                return text
            except Exception as e:
                return f"[LLM-ERROR] openai call failed: {e}"

        # Ollama path (local) - try python client, else CLI fallback
        if provider == "ollama":
            # python client path
            if HAS_OLLAMA:
                try:
                    system = (persona or f"You are playing {npc_name}.")
                    prompt = f"{system}\nTrait:{dominant}\nPromptVars:{PROMPT_VARS.get(dominant,{})}\nGenerate one concise in-character line."
                    out = ollama.generate(model=getattr(llm_config, 'MODEL', 'llama2'), prompt=prompt)
                    return out.get('response', str(out))
                except Exception as e:
                    return f"[LLM-ERROR] ollama python client failed: {e}"

            # CLI fallback
            try:
                import subprocess, shlex
                system = (persona or f"You are playing {npc_name}.")
                prompt = f"{system}\nTrait:{dominant}\nPromptVars:{PROMPT_VARS.get(dominant,{})}\nGenerate one concise in-character line."
                model = getattr(llm_config, 'MODEL', 'llama2')
                # build command: ollama generate -m <model> --no-stream --prompt '<prompt>'
                cmd = ["ollama", "generate", "-m", model, "--no-stream", "--prompt", prompt]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                if proc.returncode != 0:
                    return f"[LLM-ERROR] ollama CLI failed: {proc.stderr.strip()}"
                # Ollama CLI prints the response to stdout
                resp = proc.stdout.strip()
                # crude extraction: return stdout
                return resp
            except subprocess.TimeoutExpired:
                return "[LLM-ERROR] ollama CLI timeout"
            except FileNotFoundError:
                return "[LLM-ERROR] ollama CLI not found"
            except Exception as e:
                return f"[LLM-ERROR] ollama CLI call failed: {e}"

        # HTTP REST fallback: call Ollama HTTP API if available and requests present
        if provider == "ollama" and HAS_REQUESTS:
            try:
                http_url = getattr(llm_config, 'OLLAMA_HTTP_URL', 'http://localhost:11434')
                endpoint = http_url.rstrip('/') + '/api/generate'
                # Ollama expects model and prompt in JSON body
                payload = {
                    'model': getattr(llm_config, 'MODEL', 'llama2'),
                    'prompt': prompt_payload.get('persona', '') + '\n' + (
                        f"Trait:{prompt_payload['dominant_trait']}\nPromptVars:{prompt_payload['prompt_vars']}\nGenerate one concise in-character line."
                    ),
                    'max_tokens': 120,
                    'temperature': 0.8
                }
                resp = requests.post(endpoint, json=payload, timeout=15)
                if resp.status_code != 200:
                    return f"[LLM-ERROR] ollama http {resp.status_code}: {resp.text[:200]}"
                j = resp.json()
                # Ollama HTTP response format may vary; try common fields
                if 'response' in j:
                    return j['response']
                if 'text' in j:
                    return j['text']
                # fallback: return full json preview
                return str(j)[:1000]
            except Exception as e:
                return f"[LLM-ERROR] ollama HTTP call failed: {e}"

        return "[LLM-STUB] provider not configured or client missing"

    raise ValueError(f"Unknown variant: {variant}")
