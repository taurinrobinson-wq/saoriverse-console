#!/usr/bin/env python3
"""Assign reveal layers from velinor/cipher_seeds.json to NPCs in npc_registry.json

Follows rules in project spec: low->layer0, medium->layer1, high->no tokens, no plaintext to NPCs,
respect fragment_capacity and ensure each phrase appears at least twice across NPCs.
"""
import json
from pathlib import Path
from collections import defaultdict


def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(p: Path, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def bucket_npcs(npcs):
    low = []
    med = []
    high = []
    for n in npcs:
        r = float(n.get("reliability", 0.0))
        if r < 0.33:
            low.append(n)
        elif r < 0.66:
            med.append(n)
        else:
            high.append(n)
    return low, med, high


def assign(seeds_path: Path, npcs_path: Path):
    seeds_obj = load_json(seeds_path)
    npcs = load_json(npcs_path)

    # Map npc_id -> remaining capacity
    cap = {n["npc_id"]: int(n.get("fragment_capacity", 0)) for n in npcs}

    low, med, high = bucket_npcs(npcs)
    low_ids = [n["npc_id"] for n in low if cap.get(n["npc_id"], 0) > 0]
    med_ids = [n["npc_id"] for n in med if cap.get(n["npc_id"], 0) > 0]
    # high never receives tokens per spec

    # helper iterators
    li = 0
    mi = 0

    for seed in seeds_obj.get("seeds", []):
        layers = seed.get("reveal_layers", [])
        # ensure minimal two representations across NPCs
        assigned = set()

        # Try assign layer 0 to low reliability NPCs first
        for layer in layers:
            if layer.get("token") is None:
                continue
            layer_num = layer.get("layer")
            # choose bucket based on layer
            if layer_num == 0:
                bucket = low_ids
            elif layer_num == 1:
                bucket = med_ids
            else:
                # for any other non-final token layer prefer med then low
                bucket = med_ids + low_ids

            placed = False
            for attempt in range(len(bucket)):
                idx = (li + attempt) % len(bucket) if bucket else None
                if idx is None:
                    break
                npc_id = bucket[idx]
                if cap.get(npc_id, 0) <= 0:
                    continue
                # assign
                layer.setdefault("visible_to", []).append(npc_id)
                cap[npc_id] -= 1
                assigned.add(npc_id)
                placed = True
                # advance iterators
                li = (idx + 1) % len(bucket) if bucket else li
                break
            if not placed:
                # fallback: try any med then low
                for npc_id in (med_ids + low_ids):
                    if cap.get(npc_id, 0) > 0:
                        layer.setdefault("visible_to", []).append(npc_id)
                        cap[npc_id] -= 1
                        assigned.add(npc_id)
                        placed = True
                        break

        # Ensure at least two representations overall (across layers)
        flat_vis = set()
        for l in layers:
            for v in l.get("visible_to", []):
                if v != "server_only":
                    flat_vis.add(v)
        # if less than 2, try to add more from low then med
        if len(flat_vis) < 2:
            need = 2 - len(flat_vis)
            candidates = low_ids + med_ids
            for npc_id in candidates:
                if need <= 0:
                    break
                if npc_id in flat_vis:
                    continue
                if cap.get(npc_id, 0) <= 0:
                    continue
                # attach to layer 0 by preference
                for l in layers:
                    if l.get("token") is None:
                        continue
                    l.setdefault("visible_to", []).append(npc_id)
                    cap[npc_id] -= 1
                    flat_vis.add(npc_id)
                    need -= 1
                    break

    # write back
    write_json(seeds_path, seeds_obj)
    print(f"Wrote assignments to {seeds_path}")


def main():
    seeds = Path("velinor/cipher_seeds.json")
    npcs = Path("velinor/npc_registry.json")
    if not seeds.exists() or not npcs.exists():
        print("Missing required files: velinor/cipher_seeds.json and velinor/npc_registry.json")
        return
    assign(seeds, npcs)


if __name__ == "__main__":
    main()
