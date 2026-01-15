#!/usr/bin/env python3
"""
Run batch generation against Automatic1111 WebUI REST API using prompts file.

Usage:
  python tools/run_automatic1111_batch.py --prompts output/generated/missing_npc_prompts.txt --out output/generated --steps 28 --cfg 8.5

The prompts file format is `slug|prompt` per line.
"""
import argparse
from pathlib import Path
import requests
import base64
import json

API_DEFAULT = 'http://127.0.0.1:7860/sdapi/v1/txt2img'


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--prompts', required=True)
    p.add_argument('--out', default='output/generated')
    p.add_argument('--steps', type=int, default=28)
    p.add_argument('--cfg', type=float, default=8.5)
    p.add_argument('--width', type=int, default=1024)
    p.add_argument('--height', type=int, default=1024)
    p.add_argument('--sampler', default='Euler a')
    return p.parse_args()


def load_prompts(path: Path):
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '|' not in line:
            continue
        slug, prompt = line.split('|', 1)
        out.append((slug.strip(), prompt.strip()))
    return out


def call_api(api_url, prompt, steps, cfg, width, height, sampler):
    payload = {
        'prompt': prompt,
        'steps': steps,
        'cfg_scale': cfg,
        'width': width,
        'height': height,
        'sampler_name': sampler
    }
    r = requests.post(api_url, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    args = parse_args()
    prompts_file = Path(args.prompts)
    if not prompts_file.exists():
        print('Prompts file not found:', prompts_file)
        return
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompts = load_prompts(prompts_file)
    if not prompts:
        print('No prompts loaded from', prompts_file)
        return

    print(f'Loaded {len(prompts)} prompts')

    for slug, prompt in prompts:
        for i in range(1,4):
            print(f'Generating {slug} v{i}...')
            try:
                res = call_api(API_DEFAULT, prompt, args.steps, args.cfg, args.width, args.height, args.sampler)
            except Exception as e:
                print('API call failed:', e)
                print('Make sure Automatic1111 WebUI is running at http://127.0.0.1:7860')
                return
            images = res.get('images')
            if not images:
                print('No images returned for', slug)
                continue
            img_b64 = images[0]
            img_bytes = base64.b64decode(img_b64)
            filename = out_dir / f'npc_{slug}_v{i}.png'
            with open(filename, 'wb') as f:
                f.write(img_bytes)
            print('Wrote', filename)

    print('Batch generation complete. Outputs in', out_dir)

if __name__ == '__main__':
    try:
        import requests  # ensure available
    except Exception:
        print('requests library is required: pip install requests')
    main()
