"""Kharak Tread Mk II round 3: the seam decal round each end cap, run after kt2_r3_detail.py.

    exec(open(r"...\\kt2_r3_seam.py").read(), {"__name__": "__main__"})

One closed panel line where the dark end cap meets the painted plate (owner, 2026-11-24: "add a seam decal all the
way around to split the line between the metal end cap and the painted metal"), by the se-dev-seut seam rules:
- Atlas4 piece 3 (Keen's newer panel line), 16 mm wide, in Atlas4_Colorable so it takes some of the paint
  (first tried in Atlas4_VeryDark, the cap's metal).
- Centred on the material border at |x| = END_X, half on each side ("Lines on a material border"); the loop is
  the plate's own edge loop there, so the line and the border cannot drift apart.
- Three rows across: the inner on the flat plate, the centre on the fold where the end taper starts, the outer on
  the taper. Every corner (chamfers, the fold) is mitred by lifting each vertex 1.5 mm off every face it touches.
- V runs v0 -> v1 towards the cap on both ends, U along the loop at 0.5 UV per metre, (U, V, normal) right-handed
  on every face (each end built on its own, not mirrored); every face has UV area both ways.
The model stays inside 1.4 m of its origin, so the game's vertex rounding (about 0.1 mm across Y and Z here) needs
no decal_snap pass.
"""
import math
import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

LIB = next(bpy.path.abspath(lb.filepath) for lb in bpy.data.libraries if lb.filepath.endswith("Materials.blend"))
MAT = "Atlas4_Colorable"       # takes part of the paint (owner, 2026-11-24: "i want it to take some of the paint color")
HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
LINK = globals().get("LINK", "small")        # "small" or "5x5" (kt2_r3_geom.py)
GEO = {"__name__": "kt2_r3_geom_lib", "LINK": LINK}
exec(open(HERE + r"\kt2_r3_geom.py").read(), GEO)
END_X = GEO["END_X"]            # the line keeps Keen's 16 mm width and 1.5 mm lift on both links
HALF = 0.008                    # half the line's width
LIFT = 0.0015
V0, V1 = 0.4834, 0.5166         # Atlas4 piece 3's box
U_PER_M = 0.5
STEP = 0.2         # rows at most this far apart (2.5 cm first; owner, 2026-11-24, picked the cut)
NAME = GEO["P"] + "seam"


def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        with bpy.data.libraries.load(LIB, link=True) as (src, dst):
            dst.materials = [name]
        m = bpy.data.materials[name]
    return m


def loop(me, side):
    """The plate's edge loop at x = side * END_X, in order round the section."""
    on = {v.index for v in me.vertices if abs(v.co.x - side * END_X) < 1e-4}
    nb = {i: [] for i in on}
    for e in me.edges:
        a, b = e.vertices
        if a in on and b in on:
            nb[a].append(b)
            nb[b].append(a)
    start = next(iter(on))
    out, prev = [start], None
    while True:
        cur = out[-1]
        nxt = next(i for i in nb[cur] if i != prev)
        if nxt == start:
            break
        out.append(nxt)
        prev = cur
    return [me.vertices[i].co.copy() for i in out]


def lifted(bvh, p):
    """p moved off the surface so it sits LIFT clear of every face it touches (a mitre at folds and corners)."""
    hits = bvh.find_nearest_range(p, 1e-3)
    ns = []
    for _, n, _, _ in hits:
        if all(n.dot(m) < 0.9999 for m in ns):
            ns.append(n.normalized())
    avg = sum(ns, Vector()).normalized()
    return p + avg * (LIFT / min(avg.dot(n) for n in ns)), avg


def build():
    plate = bpy.data.objects[GEO["P"] + "plate"]
    old = bpy.data.objects.get(NAME)
    if old:
        me_old = old.data
        bpy.data.objects.remove(old)
        if me_old.users == 0:
            bpy.data.meshes.remove(me_old)
    bvh = BVHTree.FromPolygons([v.co for v in plate.data.vertices], [p.vertices for p in plate.data.polygons])
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    vs_v = (V0, 0.5, V1)
    for side in (1, -1):
        pts = loop(plate.data, side)
        # one direction rule: V towards the cap and (U, V, normal) right-handed on both ends, so along the top the
        # loop runs -Y on the +X end and +Y on the -X end
        top = max(range(len(pts)), key=lambda i: pts[i].z + pts[(i + 1) % len(pts)].z)
        if (pts[(top + 1) % len(pts)].y - pts[top].y) * side > 0:
            pts.reverse()
        pts.append(pts[0])                   # closed: the last row repeats the first at the full U
        # rows at most STEP apart, each lifted off its own spot: one quad across the 66 cm top sagged to 0.8 mm
        fine = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            n = max(1, math.ceil((b - a).length / STEP))
            fine += [a.lerp(b, i / n) for i in range(1, n + 1)]
        pts = fine
        rows, s = [], 0.0
        for k, p in enumerate(pts):
            if k:
                s += (p - pts[k - 1]).length
            row = []
            for dx in (-HALF, 0.0, HALF):
                q = Vector((p.x + dx * side, p.y, p.z))
                if dx > 0:                   # the outer row lies on the end taper
                    q = bvh.find_nearest(q)[0]
                row.append(lifted(bvh, q)[0])
            rows.append((row, s * U_PER_M))
        for k in range(len(rows) - 1):
            (ra, ua), (rb, ub) = rows[k], rows[k + 1]
            for j in range(2):
                quad = [(ra[j], ua, vs_v[j]), (rb[j], ub, vs_v[j]), (rb[j + 1], ub, vs_v[j + 1]),
                        (ra[j + 1], ua, vs_v[j + 1])]
                f = bm.faces.new([bm.verts.new(c) for c, _, _ in quad])
                for lp, (_, u, v) in zip(f.loops, quad):
                    lp[uv].uv = (u, v)
    bm.normal_update()
    me = bpy.data.meshes.new(NAME)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material(MAT))
    ob = bpy.data.objects.new(NAME, me)
    for c in plate.users_collection:
        c.objects.link(ob)
    ob.matrix_world = plate.matrix_world
    lift_dips(ob, bvh)
    return ob


BARY = ((.96, .02, .02), (.02, .96, .02), (.02, .02, .96), (1 / 3, 1 / 3, 1 / 3), (.5, .5, 0), (0, .5, .5), (.5, 0, .5))


def tri_gap(bvh, me, t):
    """Lowest gap over a triangle, from 7 samples cast back along its normal (se-dev-seut decal_snap.py gaps())."""
    lo = None
    for b in BARY:
        p = sum((me.vertices[v].co * w for v, w in zip(t.vertices, b)), Vector())
        h = bvh.ray_cast(p + t.normal * 0.0025, -t.normal, 0.0125)
        if h[0] is not None:
            lo = h[3] - 0.0025 if lo is None else min(lo, h[3] - 0.0025)
    return lo


def lift_dips(ob, bvh, keep=0.001, to=0.0012, passes=4):
    """Where the end taper's corners twist, a flat triangle of the strip passes under the surface between its
    corners (0.1 mm left on the small link, touching on the 5x5). Lift each triangle under `keep` out along its
    normal to `to`, moving every copy of a corner together (se-dev-seut bpy-recipes.md, "Dips the snap leaves")."""
    me = ob.data
    groups = {}
    for v in me.vertices:
        groups.setdefault(tuple(round(c, 5) for c in v.co), []).append(v.index)
    of = {i: k for k, idx in groups.items() for i in idx}
    for _ in range(passes):
        me.calc_loop_triangles()
        move = {}
        for t in me.loop_triangles:
            g = tri_gap(bvh, me, t)
            if g is not None and g < keep:
                for v in t.vertices:
                    k = of[v]
                    d = t.normal * (to - g)
                    if k not in move or d.length > move[k].length:
                        move[k] = d
        if not move:
            break
        for k, d in move.items():
            for i in groups[k]:
                me.vertices[i].co += d
        groups = {}
        for v in me.vertices:
            groups.setdefault(tuple(round(c, 5) for c in v.co), []).append(v.index)
        of = {i: k for k, idx in groups.items() for i in idx}
    me.update()


def check(ob):
    """Faces facing in, faces whose UVs break the right-handed rule, and the lift range against the plate."""
    plate = bpy.data.objects[GEO["P"] + "plate"]
    bvh = BVHTree.FromPolygons([v.co for v in plate.data.vertices], [p.vertices for p in plate.data.polygons])
    me = ob.data
    uvl = me.uv_layers[0].data
    inward = flipped = 0
    gaps = []
    for p in me.polygons:
        c = p.center
        _, n, _, d = bvh.find_nearest(c)
        gaps.append(d)
        if p.normal.dot(n) < 0.5:
            inward += 1
        a, b, cc = (uvl[i].uv for i in p.loop_indices[:3])
        if (b - a).cross(cc - a) <= 0:
            flipped += 1
    me.calc_loop_triangles()
    lows = [g for g in (tri_gap(bvh, me, t) for t in me.loop_triangles) if g is not None]
    return (len(me.polygons), inward, flipped, round(min(gaps) * 1000, 2), round(max(gaps) * 1000, 2),
            "lowest triangle sample mm", round(min(lows) * 1000, 2))


if __name__ == "__main__":
    print(check(build()))
