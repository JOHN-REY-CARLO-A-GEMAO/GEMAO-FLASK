
import os
from PIL import Image

assets_dir = r"c:\Users\Administrator\Downloads\GEMAO-FLASK (1)-20251205T044439Z-3-001\GEMAO-FLASK\MyFlaskapp\games\assets"

files = os.listdir(assets_dir)
print(f"{'File Name':<30} {'Width':<10} {'Height':<10}")
print("-" * 50)

with open("dimensions.txt", "w") as log:
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                path = os.path.join(assets_dir, f)
                with Image.open(path) as img:
                    log.write(f"{f}: {img.width}x{img.height}\n")
            except Exception as e:
                print(f"Error opening {f}: {e}")
