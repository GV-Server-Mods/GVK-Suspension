"""Kharak Tread Mk II round 3: scale decals on the 5x5 link, run after kt2_r3_seam.py.

    exec(open(r"...\\kt2_r3_decals.py").read(), {"__name__": "__main__", "LINK": "5x5"})

The owner's picks from the contact sheet and layout (owner, 2026-11-24: "the 5x5 version could look good just with
some extra decals to help sell the scale"):
- Bolts: Atlas3 piece 17 (cross-head screw cap in a ring groove), brushed steel, the piece 10.5 cm with its outer silver ring cut off (9.1 cm across), 4 per pad: at the outer
  ends and on the centre run.
- Slots: Atlas3 piece 20 (tall pill slot), 6 x 27 cm at its own aspect, 2 on each end cap face, top and bottom.
- Plate: Atlas3 piece 34 (tall plate, a groove across the middle, four corner screws), in the plate's paint,
  44 x 24 cm, its long side across the track, on each outer corner of the plate beside the end caps. It replaced Atlas1 piece 8,
  the recessed X (owner, 2026-11-24: "not loving the Xs can we swap them with C1?").
Every quad is lifted 1.5 mm and wound so (U, V, normal) is right-handed. Small link: nothing (5x5 only for now).
"""
import math
import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

LIB = next(bpy.path.abspath(lb.filepath) for lb in bpy.data.libraries if lb.filepath.endswith("Materials.blend"))
HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
INI = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Content\Data\TankTracks.ini"
LINK = globals().get("LINK", "small")
GEO = {"__name__": "kt2_r3_geom_lib", "LINK": LINK}
exec(open(HERE + r"\kt2_r3_geom.py").read(), GEO)
NAME = GEO["P"] + "decals"
LIFT = 0.0015
BOLT = ("Atlas3_Chrome", (0.2554, 0.6929, 0.3706, 0.8076), 0.105)    # 7 cm first (owner: "50% larger")
# cut inside the outer silver ring, in the black groove (39-43 % of the piece out from its centre, read from the
# colour map), so the groove is the edge (owner, 2026-11-24: "cut into those screw decals so that the outer silver
# ring is gone")
BOLT_CUT = 0.435
SLOT = ("Atlas3_Chrome", (0.0049, 0.4429, 0.0586, 0.6826), 0.06)       # width; length from the piece's aspect
PLATE = ("Atlas3_Colorable", (0.7637, 0.2554, 0.8613, 0.4321), 0.442)   # length along X, width from the aspect
# (34 cm first; owner, 2026-11-24: "make those C1 decals 30% larger")
BOLTS = [(2.3, -0.415), (2.3, 0.095), (0.75, 0.09), (0.75, 0.6)]          # +X side; the -X side is the same at -x
SLOTS_Y = (0.33, -0.33)
PLATE_XY = (2.33, 0.5)
SX_GAME = 1.0          # set by build() from TankTracks.ini


def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        with bpy.data.libraries.load(LIB, link=True) as (src, dst):
            dst.materials = [name]
        m = bpy.data.materials[name]
    return m


def ini_stretch():
    """SegmentScale X of the test design's 5x5 style in TankTracks.ini. The game stretches the link across the
    track by it, so every decal is laid out at its in-game size and built that much narrower (owner, 2026-11-24:
    "I don't like how it stretched the bolt decals", then the slots and plates too)."""
    style = None
    for line in open(INI, encoding="utf-8"):
        s = line.strip()
        if s.startswith("["):
            style = s
        elif style == "[Track:KharakTreadMk2_Large_5x5_Track]" and s.startswith("SegmentScale"):
            return float(s.split("=")[1].split(",")[0])
    return 1.0


def frame(c, n, t):
    """The decal's centre (lifted) and its U and V directions on the face as the game draws it, stretched by
    SX_GAME along X, plus the map from an in-game offset back to the model."""
    s = SX_GAME
    ng = Vector((n.x / s, n.y, n.z)).normalized()      # a stretched face's normal
    tg = Vector((t.x * s, t.y, t.z))
    tg = (tg - ng * tg.dot(ng)).normalized()
    bg = ng.cross(tg)
    return c + n.normalized() * LIFT, tg, bg, lambda o: Vector((o.x / s, o.y, o.z))


def quad(bm, uv, slot, c, n, t, w, l, box):
    """A w x l quad (in game) at c on a face of normal n: U along t, V along n x t, right-handed."""
    c, t, b, back = frame(c, n, t)
    u0, v0, u1, v1 = box
    pts = [(-t * w / 2 - b * l / 2, (u0, v0)), (t * w / 2 - b * l / 2, (u1, v0)),
           (t * w / 2 + b * l / 2, (u1, v1)), (-t * w / 2 + b * l / 2, (u0, v1))]
    f = bm.faces.new([bm.verts.new(c + back(o)) for o, _ in pts])
    f.material_index = slot
    for lp, (_, q) in zip(f.loops, pts):
        lp[uv].uv = q
    return f


def disc(bm, uv, slot, c, n, t, size, k, box, sides=24):
    """A round piece cut to radius k * size (se-dev-seut atlas-regions.md, "Cropping a round piece to a smaller
    circle"): a polygon on the face, UVs on the same circle round the piece's centre, right-handed; round in game."""
    c, t, b, back = frame(c, n, t)
    u0, v0, u1, v1 = box
    cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    ring = [(math.cos(2 * math.pi * i / sides), math.sin(2 * math.pi * i / sides)) for i in range(sides)]
    f = bm.faces.new([bm.verts.new(c + back((t * x + b * y) * k * size)) for x, y in ring])
    f.material_index = slot
    for lp, (x, y) in zip(f.loops, ring):
        lp[uv].uv = (cu + k * (u1 - u0) * x, cv + k * (v1 - v0) * y)
    return f


def bvh_of(name):
    o = bpy.data.objects[name]
    return BVHTree.FromPolygons([o.matrix_world @ v.co for v in o.data.vertices], [p.vertices for p in o.data.polygons])


def surface(bvh, p, down):
    """The hit point and normal straight along `down` from p."""
    h = bvh.ray_cast(p - down * 0.5, down)
    return h[0], h[1]


def build():
    old = bpy.data.objects.get(NAME)
    if old:
        me_old = old.data
        bpy.data.objects.remove(old)
        if me_old.users == 0:
            bpy.data.meshes.remove(me_old)
    if LINK != "5x5":
        return None
    global SX_GAME
    SX_GAME = ini_stretch()
    P = GEO["P"]
    pads = {n: bvh_of(P + n) for n in ("pad_front", "pad_rear")}
    plate = bvh_of(P + "plate")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    mats = [BOLT[0], SLOT[0], PLATE[0]]
    dn = Vector((0, 0, -1))
    for s in (1, -1):
        for x, y in BOLTS:
            hit = [surface(b, Vector((s * x, y, 1.0)), dn) for b in pads.values()]
            p, n = max((h for h in hit if h[0] is not None), key=lambda h: h[0].z)
            disc(bm, uv, 0, p, n, Vector((1, 0, 0)), BOLT[2], BOLT_CUT, BOLT[1])
        u0, v0, u1, v1 = SLOT[1]
        length = SLOT[2] * (v1 - v0) / (u1 - u0)
        xc = s * (GEO["END_X"] + 0.087)
        for side in (1, -1):                      # top (outer) and bottom (inner) faces of the end cap
            for y in SLOTS_Y:
                p, n = surface(plate, Vector((xc, y, 0.14 + side * 0.5)), Vector((0, 0, -side)))
                bt = Vector((0, 1, 0))
                quad(bm, uv, 1, p, n, bt.cross(n), SLOT[2], length, SLOT[1])
        u0, v0, u1, v1 = PLATE[1]
        p, n = surface(plate, Vector((s * PLATE_XY[0], PLATE_XY[1], 1.0)), dn)
        # a quarter turn: the long side runs across the track (owner, 2026-11-24: "rotate those C1 decals 1/4 turn")
        quad(bm, uv, 2, p, n, Vector((0, -1, 0)), PLATE[2] * (u1 - u0) / (v1 - v0), PLATE[2], PLATE[1])
    me = bpy.data.meshes.new(NAME)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(material(m))
    ob = bpy.data.objects.new(NAME, me)
    pl = bpy.data.objects[P + "plate"]
    for c in pl.users_collection:
        c.objects.link(ob)
    return ob


def check(ob):
    """Per face: lowest and highest gap to the link's surface at its corners and centre, and the UV handedness."""
    P = GEO["P"]
    parts = [bpy.data.objects[P + n] for n in ("plate", "tip", "pad_front", "pad_rear")]
    vs, fs = [], []
    for o in parts:
        k = len(vs)
        vs += [o.matrix_world @ v.co for v in o.data.vertices]
        fs += [[k + i for i in p.vertices] for p in o.data.polygons]
    bvh = BVHTree.FromPolygons(vs, fs)
    me = ob.data
    uvl = me.uv_layers[0].data
    lo, hi, flipped = 1, 0, 0
    for p in me.polygons:
        pts = [me.vertices[i].co for i in p.vertices] + [p.center]
        for q in pts:
            h = bvh.ray_cast(q + p.normal * 0.01, -p.normal, 0.05)
            d = h[3] - 0.01 if h[0] is not None else 1
            lo, hi = min(lo, d), max(hi, d)
        a, b, c = (uvl[i].uv for i in p.loop_indices[:3])
        if (b - a).cross(c - a) <= 0:
            flipped += 1
    return len(me.polygons), "gap mm", round(lo * 1000, 2), round(hi * 1000, 2), "flipped", flipped


if __name__ == "__main__":
    o = build()
    print(check(o) if o else "no decals on the small link")
