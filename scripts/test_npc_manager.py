from velinor.engine.npc_manager import create_marketplace_npcs, create_marketplace_influence_map
npcs = create_marketplace_npcs()
print('NPC count:', len(npcs))
print('Names:', [n.name for n in npcs])
im = create_marketplace_influence_map()
print('Archivist Malrik in influence map:', 'Archivist Malrik' in im)
print('High Seer Elenya in influence map:', 'High Seer Elenya' in im)
