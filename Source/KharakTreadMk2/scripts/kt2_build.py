"""Kharak Tread Mk II blockout: the small link (3x3 size) with both tongue options.

Run in Blender with KharakTreadMk2.blend open:
    exec(open(r"...\\kt2_build.py").read(), {"__name__": "__main__"})

Every outline is read off the owner's mockup
(Source/KharakTread/reference/kharak_tread_v2_mockup_owner_2026-11-23.png) at 2.80 m across the plate.
Axes as the Kharak Tread: X across the track, Y along it (+Y toward the arrowhead's tip), Z outward from the
wheel. Origin on the plate's underside, at the plate's center.

Tongue A ("rubber over the plate", as drawn): the arrowhead's front is rubber only; it lies on the plate of the
link ahead, which has a cut-out in front of the tip.
Tongue B ("notch for the tongue"): the plate runs under the tongue; the link ahead has a notch of the tongue's
shape with one even gap (NOTCH_GAP) all round, open at its rear edge.
Tongue C (owner idea, 2026-11-23: "faking it by attaching part of the tongue to the link ahead"): B's shapes, cut
at the hinge line (half a pitch ahead of the link's center). The front piece of the tongue belongs to the link ahead
and sits in that link's notch, so it turns with it on a wheel instead of lifting out.
Its rear has a knuckle (owner, 2026-11-23: "the back of the tongue tip would extend back and maybe curve downward so
the curve is hidden when the link is straight but bridges the gap when around the wheel"): a sector of a cylinder
round the hinge axis, reaching back inside the arrowhead behind. On a wheel the cut opens round that same axis, so
the sector's arc spans the opening exactly.
A round hinge pin runs through the metal plate under the tongue's front piece, across the notch's side gaps. A thin
floor under the gap in front of the tip hides the horn.
"""
import math
import bpy
import bmesh

S = 2.80 / 886.0            # meters per mockup pixel
CX, CY = 464.5, 412.0       # mockup pixel of the plate's center (second link from the top)

PLATE_T = 0.14              # plate thickness
PAD_T = 0.10                # raised pads (owner pick "Taller pads")
HALF_W = 1.40               # plate half width
HALF_L = 107.5 * S          # plate half length (215 px)
PITCH = 233 * S             # 0.736 m
NOTCH_GAP = 0.04            # tongue B: even gap round the tongue

COLL = "KT2_blockout"


def m(px, py):
    """Mockup pixel to meters in the link frame."""
    return ((px - CX) * S, (CY - py) * S)


# Left half of the raised rubber, mockup pixels (pixel edges), from the tip down the left side to the rear
# center. 45 degree shoulders through the drawn shoulder's midpoint.
PAD_LEFT_PX = [
    (348.0, 224.5),   # tip corner
    (196.0, 376.5),   # shoulder meets the upper bar's top edge
    (40.5, 376.5),    # upper bar, outer top
    (40.5, 423.5),    # upper bar, outer bottom
    (227.0, 423.5),   # upper bar's bottom edge meets the slot
    (277.0, 373.5),   # slot top, left wall
    (284.0, 373.5),   # slot top, right wall
    (212.0, 445.5),   # slot's right wall meets the lower bar's top edge
    (40.5, 445.5),    # lower bar, outer top
    (40.5, 500.5),    # lower bar, outer bottom
    (240.0, 500.5),   # lower bar's inner end, bottom
    (308.0, 432.5),   # 45 degree end meets the arrowhead's back edge
]


SLOT_W = 0.03   # across the 45 degree slot (owner pick, 2026-11-23: "3 cm"; drawn 1.6 cm, 7 px wide)


def pad_outline():
    d = (SLOT_W * math.sqrt(2) / S - 7.0) / 2      # widen the slot about its center line, in pixels
    px = list(PAD_LEFT_PX)
    for i, sign in ((4, -1), (5, -1), (6, 1), (7, 1)):
        px[i] = (px[i][0] + sign * d, px[i][1])
    left = [m(x, y) for x, y in px]
    right = [(-x, y) for x, y in reversed(left)]
    return left + right


TIP_Y = m(0, 224.5)[1]                 # 0.5925
TIP_HALF = -m(348.0, 0)[0]             # 0.368


def arrow_half(y):
    """Half width of the arrowhead at y, on its 45 degree shoulders."""
    return TIP_HALF + (TIP_Y - y)


def plate_outline_b():
    front = HALF_L
    t = arrow_half(front)
    tip_behind = TIP_Y - PITCH             # the tip of the link behind, in this link's frame
    g = NOTCH_GAP
    nf = tip_behind + g                    # notch front edge
    nf_half = TIP_HALF + g * (math.sqrt(2) - 1)
    nr_half = arrow_half(-HALF_L + PITCH) + g * math.sqrt(2)
    return [(-TIP_HALF, TIP_Y), (-t, front), (-HALF_W, front), (-HALF_W, -HALF_L), (-nr_half, -HALF_L),
            (-nf_half, nf), (nf_half, nf), (nr_half, -HALF_L), (HALF_W, -HALF_L), (HALF_W, front),
            (t, front), (TIP_HALF, TIP_Y)]


HINGE_Y = PITCH / 2


def clip_tip(outline):
    """An outline with the arrowhead's tip cut off at the hinge line (the tip corners are its first and last point)."""
    a = arrow_half(HINGE_Y)
    return [(-a, HINGE_Y)] + outline[1:-1] + [(a, HINGE_Y)]


def tongue_c():
    """The arrowhead's front, ahead of the hinge line, moved back one pitch onto the link ahead."""
    a = arrow_half(HINGE_Y)
    return [(-TIP_HALF, TIP_Y - PITCH), (-a, HINGE_Y - PITCH), (a, HINGE_Y - PITCH), (TIP_HALF, TIP_Y - PITCH)]


def bar_mat():
    """Darker steel for the hinge bar, so it shows against the plate in the review renders."""
    mat = material("KT2_bar", (0.10, 0.10, 0.11), 0.35)
    mat.diffuse_color = (0.27, 0.29, 0.33, 1.0)
    return mat


def hinge_bar(name, y, z, r, x_half, mat, coll, n=24):
    """A round bar along X, smooth shaded, centered at (y, z) in the link frame."""
    pts = [(y + r * math.cos(2 * math.pi * k / n), z + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    ob = prism_x(name, pts, -x_half, x_half, mat, coll)
    for p in ob.data.polygons[2:]:
        p.use_smooth = True
    return ob


KNUCKLE_H = 0.113                      # hinge height in the link frame: -Y, 0.110 (1x1) to 0.116 (3x3)
KNUCKLE_R = PLATE_T + PAD_T - KNUCKLE_H - 0.004   # 4 mm under the outer face, so it stays hidden when straight
KNUCKLE_SPAN = math.radians(46)         # covers the 1x1's 44.6 degree turn per link

# Hinge bar (owner, 2026-11-23: "a round bar that bridges the gap like a wide hinge that the arrowhead tongue holds on
# to", "a long horizontal bar"; 2026-11-24: "further back like the bar I had in my original drawing that went across
# under the tongue"; owner pick, 2026-11-24: "Half way between 1 and 2", the first try in front of the tip and the
# joint; "It should be connected deep in at the metal plate, not at the rubber pad"): a pin through the metal plate
# under the tongue's front piece, centered in the plate's depth. It shows only where it crosses the notch's side gaps,
# and both ends stay 4 cm inside the plate beyond them.
BACK_Y = m(*PAD_LEFT_PX[11])[1]                          # the arrowhead's back edge, -0.065
BAR_Y = ((TIP_Y - PITCH + BACK_Y) / 2 - HINGE_Y) / 2     # -0.236
BAR_R = 0.045
BAR_Z = PLATE_T / 2
BAR_HALF = TIP_HALF + TIP_Y - (BAR_Y - BAR_R) - PITCH + NOTCH_GAP * math.sqrt(2) + 0.04   # notch wall + 4 cm

# Floor under the gap in front of the tip (owner, 2026-11-24: "Yes now you got it", to the bar with this floor): the
# horn showed through that gap as the tab the owner disliked. The tip piece and the notch are on the same link, so a
# floor at the plate's underside can join them; the gap stays 12 cm deep.
FLOOR_T = 0.02


def gap_floor(th, tip_behind, gap, e=0.005):
    """The gap in front of a tip at tip_behind (half width th), reaching e into the walls round it."""
    side = th + gap * math.sqrt(2) + e
    front = th + gap * (math.sqrt(2) - 1) + e
    return [(-side, tip_behind - e), (-front, tip_behind + gap + e), (front, tip_behind + gap + e),
            (side, tip_behind - e)]


def knuckle_yz():
    """The knuckle's side profile (y, z) in the link frame, split at the plate top: (metal, rubber)."""
    hy = -HINGE_Y
    arc = [(hy - KNUCKLE_R * math.sin(a), KNUCKLE_H + KNUCKLE_R * math.cos(a))
           for a in (KNUCKLE_SPAN * k / 12 for k in range(13))]
    back = (PLATE_T - KNUCKLE_H) * math.tan(KNUCKLE_SPAN)
    metal = [(hy, KNUCKLE_H), (hy, PLATE_T), (hy - back, PLATE_T)]
    rubber = [(hy, PLATE_T)] + arc + [(hy - back, PLATE_T)]
    return metal, rubber


LIP_R = 0.9     # tongue D (owner, 2026-11-23: "a back curve with a MUCH larger radius ... like the radius of the 1x1")


def lip_yz(n=16):
    """Tongue D's back lip, (y, z): tangent to the outer face at the hinge line, curving down with radius LIP_R
    until it reaches hinge height. Split at the plate top: (metal, rubber, the arc's points)."""
    hy, top, h = -HINGE_Y, PLATE_T + PAD_T - 0.004, KNUCKLE_H
    end = math.sqrt(LIP_R ** 2 - (LIP_R - (top - h)) ** 2)

    def z(u):
        return top - LIP_R + math.sqrt(LIP_R ** 2 - u * u)
    u_mid = math.sqrt(LIP_R ** 2 - (LIP_R - (top - PLATE_T)) ** 2)     # where the arc crosses the plate top
    hi = [(hy - u_mid * k / n, z(u_mid * k / n)) for k in range(n + 1)]
    lo = [(hy - (u_mid + (end - u_mid) * k / n), z(u_mid + (end - u_mid) * k / n)) for k in range(n + 1)]
    rubber = [(hy, PLATE_T)] + hi
    metal = [(hy, h), (hy, PLATE_T)] + lo + [(hy - end, h)]
    return metal, rubber, hi + lo[1:]


def prism_x(name, pts_yz, x0, x1, mat, coll):
    """A closed mesh from a (y, z) outline, extruded across the track from x0 to x1."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    lo = [bm.verts.new((x0, y, z)) for y, z in pts_yz]
    hi = [bm.verts.new((x1, y, z)) for y, z in pts_yz]
    bm.faces.new(lo)
    bm.faces.new(hi)
    n = len(pts_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def plate_outline_a():
    return [(-HALF_W, HALF_L), (-HALF_W, -HALF_L), (HALF_W, -HALF_L), (HALF_W, HALF_L)]


def hole_outline_a():
    """The cut-out in front of the next link's tip, as drawn: 2.5 cm ahead of the tip, 45 degree sides."""
    f, r = m(0, 450.5)[1], m(0, 473.5)[1]
    fh, rh = -m(335.5, 0)[0], -m(312.5, 0)[0]
    return [(-fh, f), (-rh, r), (rh, r), (fh, f)]


def material(name, rgb, rough):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    mat.diffuse_color = (*rgb, 1.0)
    return mat


def prism(name, pts, z0, z1, mat, coll):
    """A closed mesh from a CCW outline, extruded from z0 to z1."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in pts]
    hi = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def cut(target, cutter):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    with bpy.context.temp_override(object=target, active_object=target, selected_objects=[target]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    me = cutter.data
    bpy.data.objects.remove(cutter)
    if me.users == 0:
        bpy.data.meshes.remove(me)


def fresh_collection(scene):
    old = bpy.data.collections.get(COLL)
    if old:
        objs = list(old.all_objects)
        for ob in objs:
            me = ob.data
            bpy.data.objects.remove(ob)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)
        for child in list(old.children):
            bpy.data.collections.remove(child)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new(COLL)
    scene.collection.children.link(coll)
    return coll


def build():
    scene = bpy.data.scenes.get("KT2_build") or bpy.data.scenes.new("KT2_build")
    root = fresh_collection(scene)
    metal = material("KT2_metal", (0.30, 0.30, 0.31), 0.55)
    rubber = material("KT2_rubber", (0.035, 0.035, 0.035), 0.9)
    horn_src = bpy.data.objects.get("KT_horn")
    out = {}
    for variant in ("A", "B", "C", "D"):
        coll = bpy.data.collections.new(f"KT2_{variant}")
        root.children.link(coll)
        outline = plate_outline_a() if variant == "A" else plate_outline_b()
        outline = clip_tip(outline) if variant in "CD" else outline
        plate = prism(f"KT2_{variant}_plate", outline, 0.0, PLATE_T, metal, coll)
        if variant == "A":
            cutter = prism("cutter", hole_outline_a(), -0.05, PLATE_T + 0.05, metal, coll)
            cut(plate, cutter)
        pads = prism(f"KT2_{variant}_pads", clip_tip(pad_outline()) if variant in "CD" else pad_outline(),
                     PLATE_T, PLATE_T + PAD_T, rubber, coll)
        parts = [plate, pads]
        if variant in "CD":
            v = variant
            parts.append(prism(f"KT2_{v}_plate_tongue", tongue_c(), 0.0, PLATE_T, metal, coll))
            parts.append(prism(f"KT2_{v}_pads_tongue", tongue_c(), PLATE_T, PLATE_T + PAD_T, rubber, coll))
            a = arrow_half(HINGE_Y)
            k_metal, k_rubber = knuckle_yz() if v == "C" else lip_yz()[:2]
            parts.append(prism_x(f"KT2_{v}_knuckle_plate", k_metal, -a, a, metal, coll))
            parts.append(prism_x(f"KT2_{v}_knuckle_pads", k_rubber, -a, a, rubber, coll))
            parts.append(hinge_bar(f"KT2_{v}_hinge_bar", BAR_Y, BAR_Z, BAR_R, BAR_HALF, bar_mat(), coll))
            parts.append(prism(f"KT2_{v}_gap_floor", gap_floor(TIP_HALF, TIP_Y - PITCH, NOTCH_GAP), 0.0, FLOOR_T,
                               metal, coll))
        if horn_src:
            horn = bpy.data.objects.new(f"KT2_{variant}_horn", horn_src.data.copy())
            horn.data.materials.clear()
            horn.data.materials.append(metal)
            coll.objects.link(horn)
            parts.append(horn)
        out[variant] = parts
    return out


if __name__ == "__main__":
    res = build()
    for v, parts in res.items():
        for ob in parts:
            xs = [p.co.x for p in ob.data.vertices]
            ys = [p.co.y for p in ob.data.vertices]
            print(v, ob.name, len(ob.data.vertices), "x", round(min(xs), 3), round(max(xs), 3),
                  "y", round(min(ys), 3), round(max(ys), 3))
