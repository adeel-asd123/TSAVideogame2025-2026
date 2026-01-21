import os

assets_dir = "TSAVideogame2025-2026/assets"

files = []
for root, _, filenames in os.walk(assets_dir):
    for filename in filenames:
        full_path = os.path.join(root, filename)
        files.append("'" + (full_path.replace("\\", "/")).replace("TSAVideogame2025-2026/", "") + "',")

for f in files:
    print(f)
