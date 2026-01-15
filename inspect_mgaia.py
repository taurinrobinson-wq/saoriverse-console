import sys
sys.path.insert(0, 'third_party/MGAIA-Minecraft-GDMC')
import pickle
p = "third_party/MGAIA-Minecraft-GDMC/structures/brickhouse-entrance.pkl"
with open(p,"rb") as f:
    s = pickle.load(f)
print(type(s))
print("name=", getattr(s,"name",None))
print("size=", getattr(s,"size",None))
print("offset=", getattr(s,"offset",None))
print("num_blocks=", len(getattr(s,"blocks",{})))
for i,(k,v) in enumerate(list(s.blocks.items())[:10]):
    try:
        repr_v = getattr(v,'namespacedName', getattr(v,'name', getattr(v,'id', str(v))))
    except Exception:
        repr_v = str(v)
    print(i, k, type(v), repr_v)
