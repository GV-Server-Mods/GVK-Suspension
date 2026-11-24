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
from mathutils import Matrix, Vector

HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
LINK = globals().get("LINK", "small")      # "small" or "5x5" (kt2_r3_geom.py)
ROOT_COLL = "KT3_blockout_5x5" if LINK == "5x5" else "KT3_blockout"
VARIANT = "R3_5x5" if LINK == "5x5" else "R3"


def load(name):
    ns = {"__name__": name.replace(".py", "_lib"), "LINK": LINK}
    exec(open(os.path.join(HERE, name)).read(), ns)
    return ns


GEO = load("kt2_r3_geom.py")
LIB = load("kt2_build.py")
P = GEO["P"]


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


def cut_notch(tip):
    """The slice's front notch (kt2_r3_geom.py NOTCH_HALF, NOTCH_BACK), so the rod shows through it."""
    g = GEO
    h, y0, y1 = g["NOTCH_HALF"], g["NOTCH_BACK"] - g["PITCH"], g["TIP_Y"] - g["PITCH"] + 0.05
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x, v.co.y, v.co.z = v.co.x * 2 * h, y0 + (v.co.y + 0.5) * (y1 - y0), v.co.z
    me = bpy.data.meshes.new("R3_notch_cutter")
    bm.to_mesh(me)
    bm.free()
    cutter = bpy.data.objects.new("R3_notch_cutter", me)
    for c in tip.users_collection:
        c.objects.link(cutter)
    mod = tip.modifiers.new("notch", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", cutter
    with bpy.context.temp_override(object=tip, active_object=tip, selected_objects=[tip]):
        bpy.ops.object.modifier_apply(modifier="notch")
    bpy.data.objects.remove(cutter)
    bpy.data.meshes.remove(me)
    bm = bmesh.new()
    bm.from_mesh(tip.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(tip.data)
    bm.free()


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
    plate = lib["prism"](P + "plate", g["plate"](seam=True), 0.0, pt, metal, coll)
    # The slice and its knuckle are one profile extruded across the tongue, its ends moved onto the tongue's 45 degree
    # sides all the way back (owner, 2026-11-24: "continue the angled (45 degree?) edge on both sides all the way to
    # the knuckle end", "you still have a tiny little step that needs to be flattened"). Built as one solid, so its
    # edges and chamfers run unbroken from the tip to the knuckle's back ("you have some ugly jagged edges here when
    # it should be smooth and the chamfer needs to continue to the edge/corners"; two stacked meshes or a boolean
    # union left steps and slivers there).
    tip = lib["prism_x"](P + "tip", g["knuckle_yz"](whole=True), -1.0, 1.0, metal, coll)
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
    cut_notch(tip)
    parts = [plate, tip]

    parts.append(lib["prism"](P + "pad_front", g["front_pad"](), pt, pt + g["PAD_T"], rubber, coll))
    parts.append(lib["prism"](P + "pad_rear", g["rear_pad"](), pt, pt + g["PAD_T"], rubber, coll))
    bevel_ends(plate)
    # No floor in the notch's gap: only the rod holds the links together (owner, 2026-11-24: "remove that, its
    # supposed to look like the rod hinge is holding it together only").
    yb = g["BAR_Y"] - g["PITCH"]
    # 16 sides, and no end caps: both ends sit inside the plate (owner, 2026-11-24, picked fewer faces here)
    rod = lib["hinge_bar"](P + "rod", yb, g["BAR_Z"], g["BAR_R"], g["bar_half"](yb), lib["bar_mat"](), coll, n=16)
    bm = bmesh.new()
    bm.from_mesh(rod.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) > 4], context="FACES_ONLY")
    bm.to_mesh(rod.data)
    bm.free()
    parts.append(rod)
    horn_src = bpy.data.objects.get("KT_horn")
    if horn_src:
        horn = bpy.data.objects.new(P + "horn", horn_src.data.copy())
        horn.data.materials.clear()
        horn.data.materials.append(metal)
        # 7 cm forward, clear of the open gap in front of the tongue's tip (owner, 2026-11-24: "the guide horn should
        # be moved forward a little so it isn't visible from this angel")
        horn.data.transform(Matrix.Translation((0, g["HORN_Y"], 0)) @ Matrix.Scale(g["HORN_S"], 4))
        coll.objects.link(horn)
        parts.append(horn)
    return parts


def renders():
    g = GEO
    rev = load("kt2_review.py")
    os.makedirs(rev["OUT"], exist_ok=True)
    bpy.data.materials["KT2_metal"].diffuse_color = (0.58, 0.6, 0.63, 1)   # workbench views only
    yb = g["BAR_Y"] - g["PITCH"]
    if LINK == "5x5":
        renders_5x5(rev, yb)
        return
    rev["top_view"](VARIANT)
    rev["straight_view"](VARIANT)
    rev["hinge_view"](VARIANT, yb, g["BAR_Z"], x=g["notch_half"](yb) - g["NOTCH_GAP"] / math.sqrt(2))
    for w in rev["RENDERED"]:
        rev["wheel_views"](VARIANT, w)


def renders_5x5(rev, yb):
    """kt2_review.py's views, sized for the 5x5 link on TankWheel5x5 (as kt2_5x5.py views())."""
    g, k = GEO, GEO["SX"]
    rev["PITCH"], rev["THICK"], rev["PLATE_T"] = g["PITCH"], g["PLATE_T"] + g["PAD_T"], g["PLATE_T"]
    rev["WHEELS"]["TankWheel5x5"] = (5.478, 5.8)
    drawn = rev["lib_drawn"]
    rev["lib_drawn"] = lambda name: 5.288 if name == "TankWheel5x5" else drawn(name)
    out = rev["OUT"]
    sc = rev["scene_setup"]("KT5_top_R3", "BLENDER_WORKBENCH")
    for i in (-1, 0, 1, 2):
        rev["link_instance"](sc, VARIANT, Matrix.Translation((0, i * g["PITCH"], 0)), f"L{i}")
    rev["camera"](sc, (0, 0.5 * g["PITCH"], 10), (0, 0.5 * g["PITCH"], 0), ortho=6.6)
    rev["render"](sc, "top_R3_5x5")
    sc = rev["scene_setup"]("KT5_straight_R3", "BLENDER_EEVEE_NEXT")
    rev["add_sun"](sc)
    rev["add_ground"](sc, -0.001)
    for i in (-1, 0, 1):
        rev["link_instance"](sc, VARIANT, Matrix.Translation((0, i * g["PITCH"], 0)), f"L{i}")
    rev["camera"](sc, (3.0 * k, 2.9 * k, 2.4 * k), (0, 0.15 * k, 0), lens=38)
    rev["render"](sc, "straight_R3_5x5")
    rev["hinge_view"](VARIANT, yb, g["BAR_Z"], s=k, name="hinge_R3_5x5",
                      x=g["notch_half"](yb) - g["NOTCH_GAP"] / math.sqrt(2))
    sc, pts, rh, yo, sphere = rev["wheel_scene"]("KT5_run_R3", VARIANT, "TankWheel5x5", "BLENDER_EEVEE_NEXT")
    ys = [p[0] for p in pts]
    y0, y1 = min(ys) - g["PITCH"], max(ys) + 0.6
    z0, z1 = -sphere - 0.2, sphere + 0.2
    res = rev["RES"]
    scale = max(y1 - y0, (z1 - z0) * res[0] / res[1]) * 1.04
    rev["camera"](sc, (40, (y0 + y1) / 2, (z0 + z1) / 2), (0, (y0 + y1) / 2, (z0 + z1) / 2), ortho=scale)
    rev["render"](sc, "5x5_run_R3")
    circle = pts[3:-3]
    j = min(circle, key=lambda p: abs(math.degrees(math.atan2(p[1], p[0])) - 10))
    j = Vector((0, *j))
    u = j.normalized()
    t = Vector((0, -u.z, u.y))
    js = j * (1 + (rev["THICK"] + yo) / rh)
    sc, *_ = rev["wheel_scene"]("KT5_close_R3", VARIANT, "TankWheel5x5", "BLENDER_EEVEE_NEXT")
    rev["camera"](sc, js + u * 1.6 * k + Vector((2.3 * k, 0, 0)) + t * 1.9 * k, js + t * 0.15 * k, lens=30)
    rev["render"](sc, "5x5_close_R3")
    sc, *_ = rev["wheel_scene"]("KT5_cut_R3", VARIANT, "TankWheel5x5", "BLENDER_WORKBENCH", with_wheel=False)
    c = j + t * 0.12 * k
    rev["camera"](sc, (30, c.y, c.z), (0, c.y, c.z), ortho=1.5 * k, clip=30 - 0.02)
    rev["render"](sc, "5x5_cut_R3")
    return out, round(math.degrees(2 * math.asin(g["PITCH"] / 2 / rh)), 1), round(yo, 4)


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
