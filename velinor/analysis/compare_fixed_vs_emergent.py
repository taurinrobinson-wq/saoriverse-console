"""
Compare fixed vs emergent influence models for REMNANTS NPCs.
Generates CSVs and per-NPC plots into velinor/analysis/saturation_plots/compare_{seq}_*.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs, create_marketplace_influence_map

out_dir = os.path.join('velinor', 'analysis', 'saturation_plots')
os.makedirs(out_dir, exist_ok=True)

watch = ["Ravi","Nima","Mariel","Tovren","Dalen","Archivist Malrik","High Seer Elenya","Coren the Mediator"]
traits = ['empathy','trust','skepticism','resolve','need','memory','nuance','authority']

steps = 200
sequences = {
    'cycle_emp_trust_obs': lambda i: ({'empathy':0.2} if i%3==0 else ({'trust':0.1} if i%3==1 else {'observation':0.15})),
}

models = ['fixed','emergent']

for seq_name, tone_fn in sequences.items():
    results = {}
    for model in models:
        manager = NPCManager()
        for npc in create_marketplace_npcs():
            manager.add_npc(npc)
        manager.influence_map = create_marketplace_influence_map()
        if model == 'emergent':
            manager.use_emergent_influence = True
            manager.emergent_baseline = 0.5

        ts = {n: {t: [] for t in traits} for n in watch}
        for i in range(steps):
            tone = tone_fn(i)
            manager.simulate_encounters([tone])
            for n in watch:
                rem = manager.get_npc(n).remnants
                for t in traits:
                    ts[n][t].append(rem[t])
        results[model] = ts

    # Save CSVs and plots comparing final values
    for model, ts in results.items():
        rows = {}
        for i in range(steps):
            row = {}
            for n in watch:
                for t in traits:
                    row[f'{n}::{t}'] = ts[n][t][i]
            rows[i] = row
        df = pd.DataFrame.from_dict(rows, orient='index')
        csv_path = os.path.join(out_dir, f'compare_{seq_name}_{model}_timeseries.csv')
        df.to_csv(csv_path)

    # quick final vs initial summary print
    print('\nSequence:', seq_name)
    for model, ts in results.items():
        print('\nModel:', model)
        for n in watch:
            e0 = ts[n]['empathy'][0]
            ef = ts[n]['empathy'][-1]
            t0 = ts[n]['trust'][0]
            tf = ts[n]['trust'][-1]
            s0 = ts[n]['skepticism'][0]
            sf = ts[n]['skepticism'][-1]
            print(f"{n}: empathy {e0:.3f}->{ef:.3f}, trust {t0:.3f}->{tf:.3f}, skepticism {s0:.3f}->{sf:.3f}")

    # per NPC plot overlay fixed vs emergent
    for n in watch:
        plt.figure(figsize=(8,4))
        for model, ts in results.items():
            plt.plot(range(steps), ts[n]['trust'], label=f'trust-{model}')
            plt.plot(range(steps), ts[n]['skepticism'], linestyle='--', label=f'skepticism-{model}')
        plt.title(f'Compare {n} - {seq_name}')
        plt.xlabel('Step')
        plt.ylabel('Trait value')
        plt.ylim(0.0,1.0)
        plt.legend(loc='upper right', fontsize='small')
        png_path = os.path.join(out_dir, f'compare_{seq_name}_{n.replace(" ","_")}.png')
        plt.tight_layout()
        plt.savefig(png_path)
        plt.close()

print('\nComparison complete. Outputs in', out_dir)
