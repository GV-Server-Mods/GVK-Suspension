"""Kharak Tread Mk II round 3: export the finished link to Content/Models/KharakTreadMk2.mwm for an in-game test.

Run after kt2_r3.py, kt2_r3_detail.py, kt2_r3_seam.py and kt2_r3_decals.py, with KharakTreadMk2.blend saved:
    exec(open(r"...\\kt2_r3_export.py").read(), {"__name__": "__main__"})
    exec(open(r"...\\kt2_r3_export.py").read(), {"__name__": "__main__", "LINK": "5x5"})   # KharakTreadMk2_5x5.mwm
Every round 3 script takes the same LINK setting.

Joins copies of the R3 parts (modifiers applied) into one object in SEUT scene KharakTreadMk2 and adds Tank Tracks'
empties: the hinges (track_pivot1/2, only their Blender Y counts) and the ground-contact box (track_collider, scale
is half its size). The link frame already matches Tank Tracks: X across, Y along (Z in game), Z out (Y in game).
Main model only for now: no LODs or construction model yet.
"""
import os
import bpy

CONTENT = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Content"
HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
SNAP = r"C:\Users\blayl\.agents\skills\se-dev-seut\scripts\decal_snap.py"
LINK = globals().get("LINK", "small")        # "small" or "5x5" (kt2_r3_geom.py)
GEO = {"__name__": "kt2_r3_geom_lib", "LINK": LINK}
exec(open(HERE + r"\kt2_r3_geom.py").read(), GEO)
NAME = "KharakTreadMk2_5x5" if LINK == "5x5" else "KharakTreadMk2"
PARTS = tuple(GEO["P"] + n for n in ("plate", "tip", "pad_front", "pad_rear", "rod", "horn", "seam", "decals")
              if GEO["P"] + n in bpy.data.objects)           # decals: 5x5 only (kt2_r3_decals.py)
HINGE_Y, HINGE_Z, HALF_W = GEO["HINGE_Y"], GEO["KNUCKLE_H"], GEO["HALF_W"]
THICK = GEO["PLATE_T"] + GEO["PAD_T"]


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


def joined(main):
    dg = bpy.context.evaluated_depsgraph_get()
    obs = []
    for n in PARTS:
        src = bpy.data.objects[n]
        me = bpy.data.meshes.new_from_object(src.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        me.transform(src.matrix_world)
        ob = bpy.data.objects.new(NAME if not obs else NAME + "_" + n[3:], me)
        main.objects.link(ob)
        if obs:
            ob.parent = obs[0]      # one top-level object per collection (SEUT E031); every part sits at the origin
        obs.append(ob)
    return obs[0]


def empties(root, main):
    out = []
    for n, y in (("track_pivot1", HINGE_Y), ("track_pivot2", -HINGE_Y)):
        e = bpy.data.objects.new(n, None)
        e.empty_display_type, e.empty_display_size, e.location = "SPHERE", 0.05, (0, y, HINGE_Z)
        out.append(e)
    c = bpy.data.objects.new("track_collider", None)
    c.empty_display_type, c.empty_display_size = "CUBE", 1.0
    c.location, c.scale = (0, 0, THICK / 2), (HALF_W, HINGE_Y, THICK / 2)
    out.append(c)
    for e in out:
        main.objects.link(e)
        e.parent = root
    return out


def build():
    clear(NAME)
    s = bpy.data.scenes.new(NAME)
    s.seut.sceneType = "mainScene"
    s.seut.subtypeId = NAME
    s.seut.gridScale = "large"
    s = bpy.data.scenes[NAME]
    with bpy.context.temp_override(scene=s, view_layer=s.view_layers[0]):
        bpy.ops.scene.recreate_collections()
    main = next(c for c in s.collection.children_recursive if c.name.startswith("Main"))
    root = joined(main)
    empties(root, main)
    if max(abs(v.co.x) for v in root.data.vertices) > 2.0:
        # past 2 m the game's vertex rounding can sink a 1.5 mm decal into its surface (se-dev-seut, "Decal offset")
        ns = {"__name__": "decal_snap_lib"}
        exec(open(SNAP).read(), ns)
        print("decal snap", ns["snap"](main))
    s.seut.export_exportPath = os.path.join(CONTENT, "Models")
    if hasattr(s.seut, "mod_path"):
        s.seut.mod_path = CONTENT
    s.seut.export_sbc_type, s.seut.export_largeGrid, s.seut.export_smallGrid = "none", True, False
    return s, root


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
    scene, ob = build()
    print(ob.name, len(ob.data.vertices), [m.name for m in ob.data.materials], [c.name for c in ob.children])
    print(export(scene))
