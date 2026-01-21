#!/usr/bin/env python3
"""Generate keyed, deterministic cipher tokens for phrase seeds.

Outputs `velinor/cipher_seeds.json` containing phrases with reveal_layers.
"""
import argparse
import json
import os
from pathlib import Path
from velinor.config import get_cipher_key, hmac_sha256, bytes_to_tokens


def load_input(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_tokens_for_phrase(key: bytes, phrase: str, num_layers: int = 3):
    words = [w for w in phrase.split() if w.strip()]
    num_words = max(1, len(words))
    layers = []
    for layer in range(num_layers):
        if layer == num_layers - 1:
            # final plaintext layer
            layers.append({"layer": layer, "token": None, "plaintext": phrase, "visible_to": ["server_only"]})
            continue
        # tokens per word: layer 0 -> 1, layer1 -> 2, etc.
        tokens_per_word = 1 + layer
        total_tokens = tokens_per_word * num_words
        digest = hmac_sha256(key, (phrase + f"|{layer}").encode("utf-8"))
        toks = bytes_to_tokens(digest, total_tokens)
        token_str = "-".join(toks)
        layers.append({"layer": layer, "token": token_str, "visible_to": []})
    return layers


def main():
    p = argparse.ArgumentParser(description="Generate keyed cipher seeds (HMAC->01..26 tokens)")
    p.add_argument("--key", required=True, help="hex key or raw string for CIPHER_KEY")
    p.add_argument("--input", help="path to source phrases JSON (default: velinor/markdowngameinstructions/glyphs/cipher_seeds.json)")
    p.add_argument("--output", help="output path", default="velinor/cipher_seeds.json")
    p.add_argument("--layers", type=int, default=3, help="number of reveal layers (min 3)")
    args = p.parse_args()

    # set env key temporarily so get_cipher_key can parse formats consistently
    os.environ["CIPHER_KEY"] = args.key
    key = get_cipher_key()

    input_path = Path(args.input) if args.input else Path("velinor/markdowngameinstructions/glyphs/cipher_seeds.json")
    if not input_path.exists():
        raise FileNotFoundError(f"Input seeds file not found: {input_path}")
    src = load_input(input_path)
    # expect same format as provided: { "domains": [...categories... ]}
    phrases_out = []
    for domain in src.get("domains", []):
        for cat in domain.get("categories", []):
            for idx, phrase in enumerate(cat.get("phrases", [])):
                phrase_text = phrase
                pid = f"{domain.get('name','domain').lower().replace(' ','_')}-{cat.get('name','cat').lower().replace(' ','_')}-{idx+1:03d}"
                layers = generate_tokens_for_phrase(key, phrase_text, num_layers=max(3, args.layers))
                phrases_out.append({
                    "phrase": phrase_text,
                    "domain": domain.get("name"),
                    "id": pid,
                    "reveal_layers": layers,
                })

    out = {"seeds": phrases_out}
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(phrases_out)} seeds to {out_path}")


if __name__ == "__main__":
    main()
