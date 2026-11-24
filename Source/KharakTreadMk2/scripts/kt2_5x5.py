"""Kharak Tread Mk II: blockouts of the 5x5 link, and their renders on the 5x5 track wheel.

Plan: Docs/design/gvk-treads.md, "Mk II 5x5 link". Run in Blender with KharakTreadMk2.blend open (ONLY names one
option, or several split by commas; without it every option is built and rendered):
    exec(open(r"...\\kt2_5x5.py").read(), {"__name__": "__main__", "ONLY": "S1"})

The small link scaled up 2.13x (5.96 / 2.80) in width and pitch (owner, 2026-11-23: "just scaling up the small one
and adding a few details would look a lot better, maybe making the arrowhead wider so it doesnt look too flmsy, maybe
do 3 side cuts instead of 2"), 0.48 m thick in the small link's proportions: 0.20 m pads on a 0.28 m plate.
S1: the small link scaled. S2: S1 with a wider arrowhead. S3: S2 with three bars a side instead of two.
S2X: S2 with the side slots run on up and across the arrowhead, splitting the rubber into two lugs (owner,
2026-11-23: "have it go up a little more and cut all the way across so it spits the arrowhead into 2 large lugs").
G6, G13: S2X with a trapezoid corner lug in front of each pair of side bars, and one gap between every two lugs and
to the plate's edges (6.4 cm or 12.8 cm).
Tongue C with its knuckle and the Kharak 5x5 horn on all of them.
"""
import math
import os
import bpy
from mathutils import Matrix, Vector

ROOT = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2"
LIB = {"__name__": "kt2_build_lib"}
exec(open(os.path.join(ROOT, "scripts", "kt2_build.py")).read(), LIB)
REV = {"__name__": "kt2_review_lib"}
exec(open(os.path.join(ROOT, "scripts", "kt2_review.py")).read(), REV)

K = 5.96 / 2.80
PIT = LIB["PITCH"] * K                  # 1.567 m
HL = LIB["HALF_L"] * K                  # plate half length
HW = 2.98                               # the 5x5's rubber width, 5.96 m
TY = LIB["TIP_Y"] * K                   # the arrowhead's tip, 1.26 m ahead of the plate center
NG = LIB["NOTCH_GAP"] * K               # gap round the tip of the link behind, in this link's notch
PLATE5, PAD5 = 0.28, 0.20
THICK5 = PLATE5 + PAD5                  # outer face on the collision sphere
R5, SPHERE5 = 5.478, 5.8
SPAN = math.radians(46)                 # knuckle reach, as the small link
SLOT = LIB["SLOT_W"] * K * math.sqrt(2)  # slot width along the bars (6.4 cm across)
WIDE = 1.05                             # S2, S3: tip half width (S1: 0.78 m)


def scaled_pattern():
    """The small link's pads, scaled: tip half width, bars (top, bottom), each bar's diagonal arm width, bar ends,
    where the slots stop, and the arrowhead's back edge. Diagonals are lines x - y = c."""
    left = [(x * K, y * K) for x, y in LIB["pad_outline"]()[:12]]
    c = [x - y for x, y in left]
    th = -left[0][0]
    bars = [(left[1][1], left[3][1]), (left[7][1], left[9][1])]
    arms = [c[4] - (-th - TY), c[10] - c[7]]
    return th, bars, arms, -left[2][0], left[5][1], left[11][1]


TH0, BARS2, ARMS2, XO, Y_END, Y_BACK = scaled_pattern()


def three_bars():
    """Three bars in the band the two filled, with gaps 0.7x the scaled one and arms at the same ratio to height."""
    top, bot = BARS2[0][0], BARS2[1][1]
    gap = 0.7 * (BARS2[0][1] - BARS2[1][0])
    h = (top - bot - 2 * gap) / 3
    ratio = sum(a / (t - b) for a, (t, b) in zip(ARMS2, BARS2)) / 2
    bars = [(top - i * (h + gap), top - i * (h + gap) - h) for i in range(3)]
    return bars, [h * ratio] * 3


CUT = Y_END + 0.15                      # S2X: top of the cut across the arrowhead
EVEN = {"G6": SLOT / math.sqrt(2),      # S2X with corner lugs and one gap everywhere: the slot's 6.4 cm,
        "G13": HW - XO}                 # or the plate margin's 12.8 cm
OPTIONS = {"S1": (TH0, BARS2, ARMS2, None), "S2": (WIDE, BARS2, ARMS2, None), "S3": (WIDE, *three_bars(), None),
           "S2X": (WIDE, BARS2, ARMS2, CUT), "G6": (WIDE, BARS2, ARMS2, CUT), "G13": (WIDE, BARS2, ARMS2, CUT)}


def arrow_half(y, th):
    return th + (TY - y)


def mirrored(left):
    return left + [(-x, y) for x, y in reversed(left)]


def pads(th, bars, arms, cut=None):
    """The raised rubber, as outlines, the one with the tip first. Per side the bars each turn 45 degrees up into
    the arrowhead as an arm; a slot between neighboring arms stops at Y_END; the last arm's inner edge runs up to the
    back edge, Y_BACK. With cut (two bars only), the slot runs on up to there and turns across the arrowhead to the
    other side's slot, splitting the rubber into a front lug and a rear lug."""
    if cut is not None:
        (t0, b0), (t1, b1) = bars
        c_s = -th - TY
        c_l = c_s + arms[0]
        c_r = c_l + SLOT
        c_in = c_r + arms[1]
        low = cut - SLOT / math.sqrt(2)          # the cut keeps the slot's width across
        front = [(-th, TY), (c_s + t0, t0), (-XO, t0), (-XO, b0), (c_l + b0, b0), (c_l + cut, cut)]
        rear = [(c_r + low, low), (c_r + t1, t1), (-XO, t1), (-XO, b1), (c_in + b1, b1), (c_in + Y_BACK, Y_BACK)]
        return [mirrored(front), mirrored(rear)]
    left = [(-th, TY)]
    c_out = -th - TY
    for i, ((t, b), arm) in enumerate(zip(bars, arms)):
        left += [(c_out + t, t), (-XO, t), (-XO, b)]
        c_in = c_out + arm
        if i < len(bars) - 1:
            left += [(c_in + b, b), (c_in + Y_END, Y_END), (c_in + SLOT + Y_END, Y_END)]
            c_out = c_in + SLOT
        else:
            left += [(c_in + b, b), (c_in + Y_BACK, Y_BACK)]
    return [mirrored(left)]


def even_pads(th, g, cut):
    """S2X with one gap g between every two lugs and between each lug and the plate's edges, the tongue aside (owner,
    2026-11-24: "add a 3rd but disconnected trapezoid lug in the vacant grey space in front of the two side wings.
    Then make all lugs with an equal gap between lugs and to the of the plate except the tongue"). Outlines: the front
    lug (tip and upper bars), the rear lug (core and lower bars, g in front of the notch), and a trapezoid corner lug
    on each side in front of the upper bar. The upper bar's top stays put; the bars keep their height ratio and the
    arms their width ratio."""
    r2 = math.sqrt(2)
    t0 = BARS2[0][0]
    hu, hl = BARS2[0][0] - BARS2[0][1], BARS2[1][0] - BARS2[1][1]
    xo, b1 = HW - g, -HL + g
    b0 = t0 - (t0 - b1 - g) * hu / (hu + hl)
    t1 = b0 - g
    c_s = -th - TY                                      # the shoulder
    c_in = c_s + PIT - NG * r2 - g * r2                 # g outside the notch's 45 degree wall
    c_l = c_s + (c_in - c_s - g * r2) * ARMS2[0] / sum(ARMS2)
    c_r = c_l + g * r2
    y_back = TY - PIT + NG + g                          # g behind the notch's front edge
    low = cut - g
    front = [(-th, TY), (c_s + t0, t0), (-xo, t0), (-xo, b0), (c_l + b0, b0), (c_l + cut, cut)]
    rear = [(c_r + low, low), (c_r + t1, t1), (-xo, t1), (-xo, b1), (c_in + b1, b1), (c_in + y_back, y_back)]
    c_k, top, bot = c_s - g * r2, HL - g, t0 + g
    corner = [(-xo, top), (-xo, bot), (c_k + bot, bot), (c_k + top, top)]
    return [mirrored(front), mirrored(rear), corner, [(-x, y) for x, y in reversed(corner)]]


def plate(th):
    t = arrow_half(HL, th)
    nf = TY - PIT + NG
    nf_half = th + NG * (math.sqrt(2) - 1)
    nr_half = arrow_half(PIT - HL, th) + NG * math.sqrt(2)
    return [(-th, TY), (-t, HL), (-HW, HL), (-HW, -HL), (-nr_half, -HL), (-nf_half, nf), (nf_half, nf),
            (nr_half, -HL), (HW, -HL), (HW, HL), (t, HL), (th, TY)]


def clip_tip(outline, th):
    a = arrow_half(PIT / 2, th)
    return [(-a, PIT / 2)] + outline[1:-1] + [(a, PIT / 2)]


def tip_piece(th):
    """The arrowhead's front, ahead of the hinge line: it belongs to the link ahead, in that link's notch."""
    a = arrow_half(PIT / 2, th)
    return [(-th, TY - PIT), (-a, -PIT / 2), (a, -PIT / 2), (th, TY - PIT)]


def clip_z(poly, c, above):
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        p_in, q_in = (p[1] >= c, q[1] >= c) if above else (p[1] <= c, q[1] <= c)
        if p_in:
            out.append(p)
        if p_in != q_in:
            t = (c - p[1]) / (q[1] - p[1])
            out.append((p[0] + t * (q[0] - p[0]), c))
    return out


def hinge_height():
    return -(SPHERE5 - THICK5 - math.sqrt(R5 ** 2 + (PIT / 2) ** 2))


def knuckle():
    """Sector round the hinge axis, up to 4 mm under the outer face, reaching SPAN back; split at the plate top."""
    h = hinge_height()
    r = THICK5 - h - 0.004
    sector = [(-PIT / 2, h)] + [(-PIT / 2 - r * math.sin(a), h + r * math.cos(a))
                                for a in (SPAN * k / 16 for k in range(17))]
    return clip_z(sector, PLATE5, False), clip_z(sector, PLATE5, True)


def bar_yzr():
    """The hinge bar's center (along the link, height) and radius, as on the small link: halfway between the gap in
    front of the tip and the joint, centered in the plate's depth."""
    return ((TY - PIT + Y_BACK) / 2 - PIT / 2) / 2, PLATE5 / 2, LIB["BAR_R"] * K


def notch_wall(y, th):
    """Half width of this link's notch at y: the tip piece's side plus the gap round it, at 45 degrees."""
    return arrow_half(y + PIT, th) + NG * math.sqrt(2)


def box(name, x, y, z0, z1, mat, coll):
    return LIB["prism"](name, [(-x, y), (-x, -y), (x, -y), (x, y)], z0, z1, mat, coll)


def build_option(name, root, metal, rubber):
    th, bars, arms, cut = OPTIONS[name]
    coll = bpy.data.collections.new(f"KT2_{name}")
    root.children.link(coll)
    LIB["prism"](f"{name}_plate", clip_tip(plate(th), th), 0.0, PLATE5, metal, coll)
    outlines = even_pads(th, EVEN[name], cut) if name in EVEN else pads(th, bars, arms, cut)
    outlines[0] = clip_tip(outlines[0], th)
    for i, pad in enumerate(outlines):
        LIB["prism"](f"{name}_pads_{i}", pad, PLATE5, THICK5, rubber, coll)
    tip = tip_piece(th)
    LIB["prism"](f"{name}_tip_plate", tip, 0.0, PLATE5, metal, coll)
    LIB["prism"](f"{name}_tip_pads", tip, PLATE5, THICK5, rubber, coll)
    LIB["prism"](f"{name}_gap_floor", LIB["gap_floor"](th, TY - PIT, NG, 0.005 * K), 0.0, LIB["FLOOR_T"] * K,
                 metal, coll)                                    # hides the horn, as on the small link
    a = arrow_half(PIT / 2, th)
    k_metal, k_rubber = knuckle()
    LIB["prism_x"](f"{name}_knuckle_plate", k_metal, -a, a, metal, coll)
    LIB["prism_x"](f"{name}_knuckle_pads", k_rubber, -a, a, rubber, coll)
    bar_y, bar_z, bar_r = bar_yzr()                              # the hinge bar, as on the small link
    LIB["hinge_bar"](f"{name}_hinge_bar", bar_y, bar_z, bar_r, notch_wall(bar_y - bar_r, th) + 0.04 * K,
                     LIB["bar_mat"](), coll)
    box(f"{name}_horn", 0.426, 0.34, -0.937, 0.0, metal, coll)       # Kharak 5x5 horn
    return coll


def build():
    scene = bpy.data.scenes["KT2_build"]
    old = bpy.data.collections.get("KT5_blockout")
    if old:
        for ob in list(old.all_objects):
            me = ob.data
            bpy.data.objects.remove(ob)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)
        for child in list(old.children):
            bpy.data.collections.remove(child)
        bpy.data.collections.remove(old)
    root = bpy.data.collections.new("KT5_blockout")
    scene.collection.children.link(root)
    metal, rubber = bpy.data.materials["KT2_metal"], bpy.data.materials["KT2_rubber"]
    for name in OPTIONS:
        build_option(name, root, metal, rubber)


# ---------------------------------------------------------------- renders

def use():
    REV["PITCH"], REV["THICK"] = PIT, THICK5
    REV["WHEELS"]["TankWheel5x5"] = (R5, SPHERE5)


def links(sc, name, n=(-1, 0, 1)):
    for k in n:
        REV["link_instance"](sc, name, Matrix.Translation((0, k * PIT, 0)), f"L{k}")


def views(name):
    use()
    sc = REV["scene_setup"](f"KT5_top_{name}", "BLENDER_WORKBENCH")
    links(sc, name)
    REV["camera"](sc, (0, 0, 10), (0, 0, 0), ortho=8.4)
    REV["render"](sc, f"5x5_top_{name}")

    sc = REV["scene_setup"](f"KT5_straight_{name}", "BLENDER_EEVEE_NEXT")
    REV["add_sun"](sc)
    REV["add_ground"](sc, -0.001)
    links(sc, name)
    REV["camera"](sc, (6.4, 5.6, 4.6), (0, 0.3, 0), lens=44)
    REV["render"](sc, f"5x5_straight_{name}")
    bar_y, bar_z, _ = bar_yzr()
    gap_x = notch_wall(bar_y, OPTIONS[name][0]) - NG / math.sqrt(2)     # middle of the notch's side gap
    REV["hinge_view"](name, bar_y, bar_z, s=K, name=f"5x5_hinge_{name}", x=gap_x)

    sc, pts, rh, yo, sphere = REV["wheel_scene"](f"KT5_run_{name}", name, "TankWheel5x5", "BLENDER_EEVEE_NEXT")
    ys = [p[0] for p in pts]
    y0, y1 = min(ys) - PIT, max(ys) + 0.6
    z0, z1 = -sphere - 0.2, sphere + 0.2
    res = REV["RES"]
    scale = max(y1 - y0, (z1 - z0) * res[0] / res[1]) * 1.04
    REV["camera"](sc, (40, (y0 + y1) / 2, (z0 + z1) / 2), (0, (y0 + y1) / 2, (z0 + z1) / 2), ortho=scale)
    REV["render"](sc, f"5x5_run_{name}")

    circle = pts[3:-3]
    j = min(circle, key=lambda p: abs(math.degrees(math.atan2(p[1], p[0])) - 10))
    j = Vector((0, *j))
    u = j.normalized()
    t = Vector((0, -u.z, u.y))
    js = j * (1 + (THICK5 + yo) / rh)
    sc, *_ = REV["wheel_scene"](f"KT5_close_{name}", name, "TankWheel5x5", "BLENDER_EEVEE_NEXT")
    REV["camera"](sc, js + u * 8.0 + Vector((3.2, 0, 0)) + t * 3.0, js + Vector((0.6, 0, 0)), lens=30)
    REV["render"](sc, f"5x5_close_{name}")
    return round(math.degrees(2 * math.asin(PIT / 2 / rh)), 1), round(yo, 4)


if __name__ == "__main__":
    build()
    only = globals().get("ONLY")
    for name in (only.split(",") if only else list(OPTIONS)):
        print(name, "turn per link, Y:", views(name))
