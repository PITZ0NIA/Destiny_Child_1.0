import sys
import UnityPy

path = sys.argv[1]
env = UnityPy.load(path)

names = set()
for obj in env.objects:
    if obj.type.name == "MonoScript":
        try:
            data = obj.read()
            cls = getattr(data, "m_ClassName", None)
            ns = getattr(data, "m_Namespace", None)
            names.add(f"{ns}.{cls}" if ns else cls)
        except Exception:
            pass

for n in sorted(names):
    print(n)
