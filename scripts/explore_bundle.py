import sys
import UnityPy
from collections import Counter

path = sys.argv[1]

env = UnityPy.load(path)

type_counter = Counter()
names_by_type = {}

for obj in env.objects:
    t = obj.type.name
    type_counter[t] += 1
    if t in ("TextAsset", "MonoBehaviour"):
        try:
            data = obj.read()
            name = getattr(data, "m_Name", None) or getattr(data, "name", None)
        except Exception as e:
            name = None
        if name:
            names_by_type.setdefault(t, []).append(name)

print("=== Object type counts ===")
for t, c in type_counter.most_common(30):
    print(f"{t}: {c}")

for t in ("TextAsset", "MonoBehaviour"):
    names = names_by_type.get(t, [])
    print(f"\n=== {t} names (total {len(names)}), sample up to 60 ===")
    for n in names[:60]:
        print(n)
