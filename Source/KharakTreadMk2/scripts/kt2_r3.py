"""Kharak Tread Mk II round 3 blockout: the small link with two equal pads, built as collection KT2_R3 under
KT3_blockout, and its review renders.

Run in Blender with KharakTreadMk2.blend open:
    exec(open(r"...\\kt2_r3.py").read(), {"__name__": "__main__"})            # build only
    exec(open(r"...\\kt2_r3.py").read(), {"__name__": "__main__", "RENDER": True})

Outlines from kt2_r3_geom.py, which lists the owner's rules for this round; mesh helpers from kt2_build.py, layout
and renders from kt2_review.py (renders land in review/renders as *_R3.png).
The tongue is cut straight at the seam. Its front piece (the slice) belongs to the link ahead, moved back one pitch
into this link's notch, and carries a knuckle that reaches back into the link behind: hidden there when straight,
filling the split on a wheel.
"""
import math
import os
import bmesh
import bpy
from mathutils import Matrix

HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
ROOT_COLL = "KT3_blockout"
VARIANT = "R3"


def load(name):
    ns = {"__name__": name.replace(".py", "_lib")}
    exec(open(os.path.join(HERE, name)).read(), ns)
    return ns


GEO = load("kt2_r3_geom.py")
LIB = load("kt2_build.py")


def bevel_ends(ob):
    """Make each end of the plate a truncated prism over its last END_W (owner, 2026-11-24: "it should be beveled on
    all 4 sides so the end cap is a truncated prism")."""
    # The outline already tapers the front and back over END_W; split the top and bottom where each end begins and
    # taper them in by END_BEVEL at the end face.
    g = GEO
    x0, xe, b, pt, eps = g["HALF_W"] - g["END_W"], g["HALF_W"], g["END_BEVEL"], g["PLATE_T"], 1e-4
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for s in (1, -1):
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(s * x0, 0, 0), plane_no=(1, 0, 0))
    # the cut runs through the outline's own corners at x0; weld the copies, or the chamfer there collapses
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
    moved = 0
    for v in bm.verts:
        if abs(v.co.x) > xe - eps:
            v.co.z = b if v.co.z < pt / 2 else pt - b
            moved += 1
    bm.to_mesh(ob.data)
    bm.free()
    return moved


def fresh(scene):
    old = bpy.data.collections.get(ROOT_COLL)
    if old:
        for ob in list(old.all_objects):
            me = ob.data
            bpy.data.objects.remove(ob)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)
        for child in list(old.children):
            bpy.data.collections.remove(child)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new(ROOT_COLL)
    scene.collection.children.link(coll)
    return coll


def build():
    g, lib = GEO, LIB
    scene = bpy.data.scenes.get("KT2_build") or bpy.data.scenes.new("KT2_build")
    root = fresh(scene)
    coll = bpy.data.collections.new(f"KT2_{VARIANT}")
    root.children.link(coll)
    metal = lib["material"]("KT2_metal", (0.30, 0.30, 0.31), 0.55)
    rubber = lib["material"]("KT2_rubber", (0.035, 0.035, 0.035), 0.9)
    pt = g["PLATE_T"]

    # Plate and tongue base, cut along the front pad's front edge; the tongue's front piece (slice) in this link's
    # notch, with its knuckles reaching back into the link behind.
    plate = lib["prism"]("R3_plate", g["plate"](seam=True), 0.0, pt, metal, coll)
    # The slice and its knuckle are one profile extruded across the tongue, its ends moved onto the tongue's 45 degree
    # sides all the way back (owner, 2026-11-24: "continue the angled (45 degree?) edge on both sides all the way to
    # the knuckle end", "you still have a tiny little step that needs to be flattened"). Built as one solid, so its
    # edges and chamfers run unbroken from the tip to the knuckle's back ("you have some ugly jagged edges here when
    # it should be smooth and the chamfer needs to continue to the edge/corners"; two stacked meshes or a boolean
    # union left steps and slivers there).
    tip = lib["prism_x"]("R3_tip", g["knuckle_yz"](whole=True), -1.0, 1.0, metal, coll)
    for v in tip.data.vertices:
        v.co.x = math.copysign(g["tongue_half"](v.co.y + g["PITCH"]), v.co.x)
    # a cut all round where the front pad's shoulders start to overhang it, so the top side chamfers end square there
    bm = bmesh.new()
    bm.from_mesh(tip.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                           plane_co=(0, g["Y_SH"] - g["PITCH"], 0), plane_no=(0, 1, 0))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(tip.data)
    bm.free()
    parts = [plate, tip]

    parts.append(lib["prism"]("R3_pad_front", g["front_pad"](), pt, pt + g["PAD_T"], rubber, coll))
    parts.append(lib["prism"]("R3_pad_rear", g["rear_pad"](), pt, pt + g["PAD_T"], rubber, coll))
    bevel_ends(plate)
    # No floor in the notch's gap: only the rod holds the links together (owner, 2026-11-24: "remove that, its
    # supposed to look like the rod hinge is holding it together only").
    yb = g["BAR_Y"] - g["PITCH"]
    parts.append(lib["hinge_bar"]("R3_rod", yb, g["BAR_Z"], g["BAR_R"], g["bar_half"](yb), lib["bar_mat"](), coll))
    horn_src = bpy.data.objects.get("KT_horn")
    if horn_src:
        horn = bpy.data.objects.new("R3_horn", horn_src.data.copy())
        horn.data.materials.clear()
        horn.data.materials.append(metal)
        # 7 cm forward, clear of the open gap in front of the tongue's tip (owner, 2026-11-24: "the guide horn should
        # be moved forward a little so it isn't visible from this angel")
        horn.data.transform(Matrix.Translation((0, g["HORN_Y"], 0)))
        coll.objects.link(horn)
        parts.append(horn)
    return parts


def renders():
    g = GEO
    rev = load("kt2_review.py")
    os.makedirs(rev["OUT"], exist_ok=True)
    bpy.data.materials["KT2_metal"].diffuse_color = (0.58, 0.6, 0.63, 1)   # workbench views only
    rev["top_view"](VARIANT)
    rev["straight_view"](VARIANT)
    yb = g["BAR_Y"] - g["PITCH"]
    rev["hinge_view"](VARIANT, yb, g["BAR_Z"], x=g["notch_half"](yb) - g["NOTCH_GAP"] / math.sqrt(2))
    for w in rev["RENDERED"]:
        rev["wheel_views"](VARIANT, w)


if __name__ == "__main__":
    for ob in build():
        me = ob.data
        xs = [v.co.x for v in me.vertices]
        ys = [v.co.y for v in me.vertices]
        zs = [v.co.z for v in me.vertices]
        print(ob.name, len(me.vertices), "x", round(min(xs), 3), round(max(xs), 3), "y", round(min(ys), 3),
              round(max(ys), 3), "z", round(min(zs), 3), round(max(zs), 3))
    print(GEO["summary"]())
    if globals().get("RENDER"):
        renders()
        print("renders done")
