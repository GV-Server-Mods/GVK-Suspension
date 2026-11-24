"""Kharak Tread Mk II round 3: the tongue joint seen from the side, straight and bent round the 3x3 and 1x1 wheels.

    uv run -q --no-project --with pillow python -I kt2_seam_sketch.py

A section through the middle of the tongue (x = 0), where the seam runs along the front pad's middle, from
kt2_r3_geom.py. Gray is the link behind (plate and front
pad), blue the link ahead (the slice, its plate and rear pad), amber the slice's knuckle (owner, 2026-11-24: "the
curve is hidden when the track is straight, and hides the split/gap when it is wrapped around a wheel"), drawn
dashed where it is hidden inside the link behind; red is where the links overlap. Writes review/seam_section.png.
"""
import math
import runpy
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "review" / "seam_section.png"
G = runpy.run_path(str(HERE / "kt2_r3_geom.py"))

HY, KH, PT, PAD_T, PITCH = G["HINGE_Y"], G["KNUCKLE_H"], G["PLATE_T"], G["PAD_T"], G["PITCH"]
WHEELS = (("Straight", 0.0), ("3x3 wheel: 12.9 degrees per link", 12.9), ("1x1 wheel: 44.6 degrees per link", 44.6))
Y0, Y1, Z0, Z1 = 0.16, 0.80, -0.06, 0.28
SC = 1000
PW, PH = round((Y1 - Y0) * SC), round((Z1 - Z0) * SC)


def box(y0, y1, z0, z1):
    return [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]


def pieces():
    g = G
    seam, tip = g["SEAM_Y"], g["TIP_Y"]
    nf = tip + g["NOTCH_GAP"]
    behind = [box(Y0 - 0.2, seam, 0.0, PT), box(Y0 - 0.2, seam, PT, PT + PAD_T)]
    ahead = [box(seam, tip, 0.0, PT), box(tip, tip, 0.0, 0.0), box(nf, Y1 + 0.3, 0.0, PT),
             box(nf + g["G"], nf + g["G"] + g["W"], PT, PT + PAD_T)]
    knuckle = [(y + PITCH, z) for y, z in g["knuckle_yz"]()]
    return behind, ahead, knuckle


def turn(pts, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(HY + (y - HY) * c - (z - KH) * s, KH + (y - HY) * s + (z - KH) * c) for y, z in pts]


def font(size):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def P(y, z):
    return (y - Y0) * SC, (Z1 - z) * SC


def mask(polys):
    m = Image.new("L", (PW, PH), 0)
    d = ImageDraw.Draw(m)
    for pts in polys:
        d.polygon([P(*q) for q in pts], fill=255)
    return m


def dashed(d, pts, fill, width=3, dash=9):
    for a, b in zip(pts, pts[1:] + pts[:1]):
        n = max(1, int(math.dist(a, b) / dash))
        for i in range(0, n, 2):
            t0, t1 = i / n, min(1.0, (i + 1) / n)
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=fill, width=width)


def panel(turn_deg):
    behind, ahead, knuckle = pieces()
    half = turn_deg / 2
    behind = [turn(p, half) for p in behind]
    ahead = [turn(p, -half) for p in ahead]
    knuckle = turn(knuckle, -half)
    img = Image.new("RGB", (PW, PH), (246, 244, 238))
    d = ImageDraw.Draw(img)
    for i, pts in enumerate(ahead):
        d.polygon([P(*q) for q in pts], fill=(55, 62, 75) if i == 3 else (118, 140, 170))
    d.polygon([P(*q) for q in knuckle], fill=(230, 150, 30))
    for i, pts in enumerate(behind):
        d.polygon([P(*q) for q in pts], fill=(30, 30, 30) if i == 1 else (150, 152, 156))
    shrink = ImageFilter.MinFilter(5)              # pieces that only touch show no overlap
    both = ImageChops.multiply(mask(behind).filter(shrink), mask(ahead).filter(shrink))
    img.paste((215, 40, 40), (0, 0), both)
    dashed(d, [P(*q) for q in knuckle], (200, 110, 0))
    hx, hz = P(HY, KH)
    d.line([(hx - 9, hz), (hx + 9, hz)], fill=(20, 20, 20), width=2)
    d.line([(hx, hz - 9), (hx, hz + 9)], fill=(20, 20, 20), width=2)
    return img


def step_cm(turn_deg):
    """How far the slice's top back edge sits below the plate's front edge once bent."""
    a, h, t = G["SEAM_Y"] - HY, PT - KH, math.radians(turn_deg)
    return (a * math.sin(t) + h * (1 - math.cos(t))) * 100


def main():
    pad, head, gap = 24, 44, 16
    W = pad * 2 + 3 * PW + 2 * gap
    board = Image.new("RGB", (W, 70 + head + PH + 170), (255, 255, 255))
    d = ImageDraw.Draw(board)
    d.text((pad, 16), "Tongue joint from the side, through the tongue's middle: gray = this link, blue = the link "
           "ahead, amber = the slice's knuckle (dashed where hidden), red = overlap", fill=(10, 10, 10), font=font(26))
    for col, (label, deg) in enumerate(WHEELS):
        x = pad + col * (PW + gap)
        d.text((x + 4, 78), label, fill=(20, 20, 20), font=font(24))
        board.paste(panel(deg), (x, 70 + head))
    a = (G["SEAM_Y"] - HY) * 100
    lines = [
        f"The seam runs straight across along the front pad's middle front edge, {a:.2f} cm ahead of the hinge (black "
        "cross). The knuckle runs straight across the tongue: its back stands on the",
        "hinge line at the underside, and its top curves gently from the slice's top down into the plate behind. "
        "Straight, it is hidden; bent, it fills the split, and what rises sits inside the front pad.",
        f"Bent, the slice sits this far below the plate's front edge: {step_cm(12.9):.1f} cm on the 3x3, "
        f"{step_cm(19.7):.1f} cm on the 2x2, {step_cm(44.6):.1f} cm on the 1x1. The pad's shoulders sit over the "
        "slice and lift off it when bent.",
    ]
    ny = 70 + head + PH + 16
    for line in lines:
        d.text((pad + 4, ny), line, fill=(30, 30, 30), font=font(22))
        ny += 32
    board.save(OUT)
    print(OUT, board.size, [round(step_cm(t), 2) for t in (12.9, 19.7, 44.6)])


if __name__ == "__main__":
    main()
