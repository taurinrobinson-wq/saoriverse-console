from velinor.engine.npc_manager import create_marketplace_npcs, create_marketplace_influence_map

npcs = create_marketplace_npcs()
names = [n.name for n in npcs]
print('NPCs (count={}):'.format(len(names)), names)

imap = create_marketplace_influence_map()
keys = list(imap.keys())
print('\nInfluence map keys (count={}):'.format(len(keys)), keys)

# gather targets
targets = set()
for k,v in imap.items():
    targets.update(v.keys())
print('\nInfluence targets (count={}):'.format(len(targets)), sorted(targets))

# find NPCs not mentioned as key or target
mentioned = set(keys) | targets
missing = [n for n in names if n not in mentioned]
print('\nNPCs not mentioned in influence map:', missing)
