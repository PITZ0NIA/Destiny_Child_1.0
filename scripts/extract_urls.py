import re
import sys
import UnityPy

path = r"C:\Destiny_Child\apk_desmantelada\resources\assets\bin\Data\data.unity3d"

print("Loading bundle...", flush=True)
env = UnityPy.load(path)

url_re = re.compile(rb"https?://[A-Za-z0-9_./:%\-]+")
seen = set()

count = 0
for obj in env.objects:
    count += 1
    try:
        data = obj.get_raw_data()
    except Exception:
        continue
    for m in url_re.findall(data):
        s = m.decode("utf-8", errors="ignore")
        if s not in seen:
            seen.add(s)

print(f"Scanned {count} objects, found {len(seen)} unique url-like strings", flush=True)
for s in sorted(seen):
    print(s)
