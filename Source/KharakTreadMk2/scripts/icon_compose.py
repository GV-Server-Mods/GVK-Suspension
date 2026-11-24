# Links on top of their wheel, the wheel fading out below and at the sides; cropped to the links plus a strip below.
import sys
from PIL import Image

base, out = sys.argv[1], sys.argv[2]
wheel = Image.open(base + "_wheel.png").convert("RGBA")
links = Image.open(base + "_links.png").convert("RGBA")
l, t, r, b = links.getbbox()
h = b - t
bottom = min(wheel.height, b + int(float(sys.argv[3]) * h))
fade_top, fade_bot = b - int(float(sys.argv[4]) * h), bottom
W = wheel.width
px = wheel.load()
for y in range(wheel.height):
    fy = 1.0 if y <= fade_top else max(0.0, (fade_bot - y) / (fade_bot - fade_top))
    for x in range(W):
        fx = min(1.0, (x - l) / (float(sys.argv[5]) * (r - l)), (r - x) / (float(sys.argv[5]) * (r - l))) if l <= x <= r else 0.0
        f = max(0.0, fy * fx)
        R, G, B, A = px[x, y]
        px[x, y] = (R, G, B, int(A * f))
wheel.alpha_composite(links)
wheel.crop((l, t, r, bottom)).save(out)
print("COMPOSE", out)
