"""Kharak Tread Mk II round 3: export the link to Content/Models/KharakTreadMk2.mwm and its construction model.

Build every level first (kt2_r3_geom.py LEVELS), each with kt2_r3.py and kt2_r3_detail.py, main and lod1 also with
kt2_r3_seam.py and kt2_r3_decals.py, then, with KharakTreadMk2.blend saved:
    exec(open(r"...\\kt2_r3_export.py").read(), {"__name__": "__main__"})
    exec(open(r"...\\kt2_r3_export.py").read(), {"__name__": "__main__", "LINK": "5x5"})   # KharakTreadMk2_5x5.mwm
Every round 3 script takes the same LINK and LEVEL settings.

Two SEUT scenes per link (Docs/design/gvk-treads.md, "Mk II finish"):
- KharakTreadMk2: Main, LOD1, LOD2, LOD3 at 10 / 30 / 60 m (5x5: 20 / 60 / 120 m), the Rubber Track's distances.
- KharakTreadMk2_Construction: the metal link without pads or decals, with its own LOD1 and LOD2 at 10 / 30 m (5x5:
  20 / 60 m). Tank Tracks shows it on every link of a track while any wheel or suspension on that track is not fully
  built (SegmentConstruction; Track.cs AllBuilt, TrackRender.cs ChangeModels).
Each level joins copies of its parts (modifiers applied) under one root object, and each scene's Main gets Tank
Tracks' empties: the hinges (track_pivot1/2, only their Blender Y counts) and the ground-contact box (track_collider,
scale is half its size). The link frame already matches Tank Tracks: X across, Y along (Z in game), Z out (Y in game).
"""
import os
import bpy

CONTENT = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Content"
HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
SNAP = r"C:\Users\blayl\.agents\skills\se-dev-seut\scripts\decal_snap.py"
LINK = globals().get("LINK", "small")        # "small" or "5x5" (kt2_r3_geom.py)
NAME = "KharakTreadMk2_5x5" if LINK == "5x5" else "KharakTreadMk2"
PART_NAMES = ("plate", "tip", "pad_front", "pad_rear", "rod", "horn", "seam", "decals")
FAR = 2 if LINK == "5x5" else 1               # the 5x5 is twice the size, so it keeps its detail twice as far
SCENES = {NAME: [("Main", "main", 0), ("LOD1", "lod1", 10 * FAR), ("LOD2", "lod2", 30 * FAR),
                 ("LOD3", "lod3", 60 * FAR)],
          NAME + "_Construction": [("Main", "con", 0), ("LOD1", "con1", 10 * FAR), ("LOD2", "con2", 30 * FAR)]}


def geom(level):
    g = {"__name__": "kt2_r3_geom_lib", "LINK": LINK, "LEVEL": level}
    exec(open(HERE + r"\kt2_r3_geom.py").read(), g)
    return g


def clear(name):
    s = bpy.data.scenes.get(name)
    if s is None:
        return
    objs = list(s.collection.all_objects)
    for o in objs:
        me = o.data if o.type == "MESH" else None
        bpy.data.objects.remove(o)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)
    for c in list(s.collection.children_recursive):
        bpy.data.collections.remove(c)
    bpy.data.scenes.remove(s)


def joined(col, root_name, level):
    """Copies of this level's parts in col, all parented to the first (one top-level object per collection, SEUT
    E031; every part sits at the origin)."""
    p = geom(level)["P"]
    dg = bpy.context.evaluated_depsgraph_get()
    obs = []
    for n in PART_NAMES:
        src = bpy.data.objects.get(p + n)
        if src is None:
            continue
        me = bpy.data.meshes.new_from_object(src.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        me.transform(src.matrix_world)
        ob = bpy.data.objects.new(root_name if not obs else root_name + "_" + n, me)
        col.objects.link(ob)
        if obs:
            ob.parent = obs[0]
        obs.append(ob)
    return obs[0]


def empties(root, col, suffix):
    g = geom("main")
    hy, hz = g["HINGE_Y"], g["KNUCKLE_H"]
    thick = g["PLATE_T"] + g["PAD_T"]
    out = []
    for n, y in (("track_pivot1", hy), ("track_pivot2", -hy)):
        e = bpy.data.objects.new(n + suffix, None)
        e.empty_display_type, e.empty_display_size, e.location = "SPHERE", 0.05, (0, y, hz)
        out.append(e)
    c = bpy.data.objects.new("track_collider" + suffix, None)
    c.empty_display_type, c.empty_display_size = "CUBE", 1.0
    c.location, c.scale = (0, 0, thick / 2), (g["HALF_W"], hy, thick / 2)
    out.append(c)
    for e in out:
        col.objects.link(e)
        e.parent = root
    return out


def scene(name, levels, suffix):
    clear(name)
    s = bpy.data.scenes.new(name)
    s.seut.sceneType = "mainScene"
    s.seut.subtypeId = name
    s.seut.gridScale = "large"
    s = bpy.data.scenes[name]
    with bpy.context.temp_override(scene=s, view_layer=s.view_layers[0]):
        bpy.ops.scene.recreate_collections()
    cols = {c.name.split(" (")[0]: c for c in s.collection.children_recursive}
    roots = {}
    for kind, level, dist in levels:
        col = cols[kind]
        roots[kind] = joined(col, name if kind == "Main" else name + "_" + kind, level)
        if dist:
            col.seut.lod_distance = dist
        if max(abs(v.co.x) for v in roots[kind].data.vertices) > 2.0 and geom(level)["DECALS"]:
            # past 2 m the game's vertex rounding can sink a 1.5 mm decal into its surface (se-dev-seut, "Decal offset")
            ns = {"__name__": "decal_snap_lib"}
            exec(open(SNAP).read(), ns)
            print(name, kind, "decal snap", ns["snap"](col))
    empties(roots["Main"], cols["Main"], suffix)
    s.seut.export_exportPath = os.path.join(CONTENT, "Models")
    if hasattr(s.seut, "mod_path"):
        s.seut.mod_path = CONTENT
    s.seut.export_sbc_type, s.seut.export_largeGrid, s.seut.export_smallGrid = "none", True, False
    return s, roots


def build():
    # Blender names must be unique, so the construction scene's empties carry ".c" (as rt_build.py's), which SEUT
    # keeps. Harmless: Tank Tracks reads the dummies from SegmentModel only, by name prefix
    # (DefinitionsInternal.cs GetDataFromModel, SpawnSegment(construction: false), StartsWith)
    return [scene(n, lv, "" if n == NAME else ".c") for n, lv in SCENES.items()]


def export(s):
    bpy.ops.wm.save_mainfile()
    win = bpy.context.window
    old = win.scene
    win.scene = s                   # SEUT exports the window's scene, whatever the override says
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    try:
        with bpy.context.temp_override(window=win, area=area, region=region, scene=s):
            return bpy.ops.scene.export()
    finally:
        win.scene = old


if __name__ == "__main__":
    for sc, roots in build():
        print(sc.name, {k: (len(r.data.vertices), len(r.children)) for k, r in roots.items()})
        print(export(sc))
