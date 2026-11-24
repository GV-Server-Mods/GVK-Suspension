"""Kharak Tread Mk II round 3: the reading of the owner's markup (2026-11-24), drawn under the markup itself.

    uv run -q --no-project --with pillow python -I kt2_v3_reading.py

The markup (Source/KharakTread/reference/kharak_tread_v3_mockup_owner_2026-11-24.webp, kept local) is colored lines
over a picture of a track link: red the plate, green the two rubber pads, blue the hinge rod. Only the colored lines
are copied onto the board, so the picture itself stays out of the repo. The outlines come from kt2_r3_geom.py, which
also lists the owner's rules for this round. Writes review/v3_reading.png.
"""
import math
import runpy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MOCKUP = ROOT.parent / "KharakTread" / "reference" / "kharak_tread_v3_mockup_owner_2026-11-24.webp"
OUT = ROOT / "review" / "v3_reading.png"
GEO = runpy.run_path(str(HERE / "kt2_r3_geom.py"))

# Markup scale: the red outline is 990 px end to end for the 2.80 m plate; plate center at px (507, 229.5).
S = 2.80 / 990
CX, CY = 507.0, 229.5


def owner_strokes(img):
    """Only the owner's red, green and blue lines, on white."""
    src = img.convert("RGB")
    out = Image.new("RGB", src.size, (255, 255, 255))
    sp, op = src.load(), out.load()
    for yy in range(src.height):
        for xx in range(src.width):
            r, g, b = sp[xx, yy]
            if r > 180 and g < 80 and b < 80:
                op[xx, yy] = (225, 40, 40)
            elif g > 170 and r < 120 and b < 120:
                op[xx, yy] = (40, 190, 60)
            elif b > 170 and r < 90 and g < 140:
                op[xx, yy] = (40, 90, 235)
    return out


def font(size):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def dashed(d, a, b, fill, width, dash=12):
    n = max(1, int(math.dist(a, b) / dash))
    for i in range(0, n, 2):
        t0, t1 = i / n, min(1, (i + 1) / n)
        d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=fill, width=width)


def main():
    g = GEO
    k = 1.6
    strokes = owner_strokes(Image.open(MOCKUP))
    sw, sh = round(strokes.width * k), round(strokes.height * k)
    strokes = strokes.resize((sw, sh), Image.LANCZOS)
    top, pad_x, gap = 80, 30, 40
    board = Image.new("RGB", (pad_x * 2 + sw, top + 2 * sh + gap + 60 + 600), (255, 255, 255))
    d = ImageDraw.Draw(board)
    d.text((pad_x, 18), "Kharak Tread Mk II round 3: your markup (top) and my reading (bottom)", fill=(10, 10, 10),
           font=font(36))
    board.paste(strokes, (pad_x, top))
    oy = top + sh + gap + 40
    d.text((pad_x, oy - 44), "Reading: gray plate, black pads, blue rod, orange dashes the tongue's seam; your lines "
           "faint underneath", fill=(20, 20, 20), font=font(26))
    board.paste(Image.blend(Image.new("RGB", strokes.size, (255, 255, 255)), strokes, 0.35), (pad_x, oy))

    def P(x, y):
        return pad_x + (CX + x / S) * k, oy + (CY - y / S) * k

    d.polygon([P(x, y) for x, y in g["plate"]()], fill=(150, 150, 150))
    d.polygon([P(x, y) for x, y in g["tip_piece"]()], fill=(150, 150, 150))
    for poly in (g["front_pad"](), g["rear_pad"]()):
        d.polygon([P(x, y) for x, y in poly], fill=(20, 20, 20))
    for shift in (0.0, g["PITCH"]):
        seam = g["seam_line"]()
        for (xa, ya), (xb, yb) in zip(seam, seam[1:]):
            dashed(d, P(xa, ya - shift), P(xb, yb - shift), (230, 120, 0), 4)
    for yb in (g["BAR_Y"], g["BAR_Y"] - g["PITCH"]):
        hw = g["bar_half"](yb - g["PITCH"] if yb > 0 else yb)
        d.rectangle([P(-hw, yb + g["BAR_R"]), P(hw, yb - g["BAR_R"])], outline=(40, 90, 235), width=3)

    ny = oy + sh + 30
    lines = [
        f"Plate 2.80 x {2 * g['HALF_L']:.2f} m, pitch {g['PITCH']:.3f} m as now; each end's corners cut back "
        f"{g['END_CUT'] * 100:.0f} cm over its last {g['END_W'] * 100:.0f} cm, beveled round each end only.",
        f"Tongue: plate only, {2 * g['TIP_HALF']:.2f} m across its front, 45 degree sides, "
        f"{g['TIP_Y'] - g['HALF_L']:.2f} m long; the notch round it keeps the 4 cm gap.",
        f"Pads: both {g['W'] * 100:.0f} cm wide, one {g['G'] * 100:.0f} cm gap between them all the way across; the "
        "same gap to the back edge, the end bands and the notch.",
        f"   The front pad's shoulders run up the tongue's sides and rise {g['SH_RISE'] * 100:.0f} cm above its middle, "
        f"{g['SH_LEN'] * 100:.0f} cm long, as you drew them.",
        "Tongue trick: the seam (orange) runs along the front pad's front edge, shoulders included; the piece in front "
        "belongs to the next link,",
        "   with a knuckle that curves down into this link's plate: hidden when straight, it fills the split round a "
        "wheel.",
        f"Rod (blue): 9 cm across, in the middle of that front piece ({g['BAR_Y']:.3f} m ahead of the center); it "
        "shows only in the gaps beside the tongue.",
    ]
    for line in lines:
        d.text((pad_x, ny), line, fill=(30, 30, 30), font=font(24))
        ny += 34
    board = board.crop((0, 0, board.width, ny + 20))
    board.save(OUT)
    print(OUT, board.size)
    print(g["summary"]())


if __name__ == "__main__":
    main()
