# Puts a track design's name on top of its builder icon, as Digi's "Over the tire" icon has it: white letters with a
# black outline across the top, the render below. One font size for every GVK design, set by the longest name, so the
# labels match in the picker. Run with plain Python (Pillow), then convert to DDS (Docs/design/icons.md):
#   python icon_label.py <render.png> <out.png> "<name>" [<name> of every other design...]
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = r"C:\Windows\Fonts\ARIALNB.TTF"      # Arial Narrow Bold: the longest name fits at a readable size
SIZE = 512
TEXT_W = 492                                 # widest label, px
BAND = 0.30                                  # top share of the icon kept for the label
STROKE = 5
MAX_PT = 112

src, out, name = sys.argv[1], sys.argv[2], sys.argv[3]
names = [name] + sys.argv[4:]


def width(n, pt):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(n, font=ImageFont.truetype(FONT, pt)) + 2 * STROKE


pt = MAX_PT
while pt > 20 and max(width(n, pt) for n in names) > TEXT_W:
    pt -= 1
font = ImageFont.truetype(FONT, pt)

canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
render = Image.open(src).convert("RGBA")
box = render.getbbox()
render = render.crop(box)
room = (SIZE - 8, int(SIZE * (1 - BAND)) - 8)
k = min(room[0] / render.width, room[1] / render.height)
render = render.resize((round(render.width * k), round(render.height * k)), Image.LANCZOS)
canvas.alpha_composite(render, ((SIZE - render.width) // 2, SIZE - 4 - render.height))

d = ImageDraw.Draw(canvas)
top = int(SIZE * BAND / 2)
d.text((SIZE // 2, top), name, font=font, anchor="mm", fill=(255, 255, 255, 255),
       stroke_width=STROKE, stroke_fill=(0, 0, 0, 255))
canvas.save(out)
print("LABEL", out, pt)
