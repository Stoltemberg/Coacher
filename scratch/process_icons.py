import os
import shutil
from PIL import Image

# Paths
source_png = r"C:\Users\Administrator\.gemini\antigravity\brain\f98aef54-db41-4ee9-9d69-b0120255b087\coacher_logo_1776440171426.png"
assets_dir = r"c:\Users\Administrator\Documents\New project\Coacher\src\assets"
target_png = os.path.join(assets_dir, "icon.png")
target_ico = os.path.join(assets_dir, "icon.ico")

# Ensure assets dir exists
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)

# Copy PNG
shutil.copy(source_png, target_png)
print(f"Copied PNG to {target_png}")

# Convert to ICO
img = Image.open(target_png)
# Windows icons usually need multiple sizes. Pillow handles this well.
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(target_ico, format='ICO', sizes=icon_sizes)
print(f"Converted and saved ICO to {target_ico}")
