"""Kharak Tread Mk II round 3: the finish on the blockout's parts, run after kt2_r3.py builds them.

    exec(open(r"...\\kt2_r3_detail.py").read(), {"__name__": "__main__"})

The rubber follows the Rubber Track's Look and Bevel in Docs/design/gvk-treads.md (Source/RubberTread/scripts/
rt_build.py; owner, 2026-11-24: "I want the rubber portions to follow the same style as the rubber trade we made with
the rubber textures, chamfers, and direction", "use the keen's rubber look section of the gvk-treads.md"):
- Keen's tire split: RubberWheels on the tops, RubberWheelsScratched on the bevel faces, RubberDry on the walls.
- One round 3 cm bevel, 3 segments, on the top edges and the outside upright corners; the bottoms and inside
  corners stay sharp.
- Smooth by angle (60 degrees) and weighted normals, so the flat faces stay flat and only the bevels round off.
- Box UVs, turned 90 degrees so the texture's streaks run along the track; y and z inside one tile and the width
  stretched to one tile (0.245 UV per metre), since Keen's rubber textures do not tile.
The plate, slice and horn take PaintedMetal_Colorable, the plate's and slice's 1 cm chamfers
PaintedMetalScratched_Colorable, with box UVs at 0.5 UV per metre.
"""
import math
import bmesh
import bpy

RUBBER = ("RubberWheels", "RubberWheelsScratched", "RubberDry")
# Faces and chamfers alike: Keen's scratched paint is 100% paintable (flat ADD), so its scratches never showed, and no
# tiling worn steel takes paint (owner, 2026-11-24: "worn steel if it is colorable")
METAL = ("PaintedMetal_Colorable",)
# The plate's end caps in unpainted dark steel, their chamfers scratched (owner, 2026-11-24: "I want to make those end
# caps a dark metal with scratched metal chamfers"); neither takes paint, so the scratches show
CAP = ("PaintedMetal_VeryDark", "PaintedMetalScratched_VeryDark")
END_X = 1.31                                 # kt2_r3_geom.py HALF_W - END_W: where each end cap starts
CHAMFER = 0.01
SEAM, PITCH, HALF_L, Y_SH = 0.3765, 0.736, 0.34, 0.4265   # kt2_r3_geom.py SEAM_Y, PITCH, HALF_L and Y_SH
LIB = next(bpy.path.abspath(lb.filepath) for lb in bpy.data.libraries if lb.filepath.endswith("Materials.blend"))
BEVEL, SEGMENTS = 0.03, 3
PLATE_T = 0.14
TONGUE_C = 0.5925 + 0.513   # kt2_r3_geom.py TONGUE_C: the tongue's sides are |x| = TONGUE_C - y


def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        with bpy.data.libraries.load(LIB, link=True) as (src, dst):
            dst.materials = [name]
        m = bpy.data.materials[name]
    return m


def uv_box(ob, sx, s, edge=None):
    """Box projection: x at sx UV per metre, y and z at s, all offset half a tile; turned 90 degrees as rt_build.py.
    With edge, faces in slot 1 (the chamfers) take that scale on every axis instead."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uv = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        fx, fs = (edge, edge) if edge and f.material_index == 1 else (sx, s)
        for lp in f.loops:
            c = lp.vert.co
            ux = c.x * fx + 0.5
            a, b = ((c.y * fs + 0.5, c.z * fs + 0.5) if ax == 0 else (ux, c.z * fs + 0.5) if ax == 1
                    else (ux, c.y * fs + 0.5))
            lp[uv].uv = (b, -a)
    bm.to_mesh(ob.data)
    bm.free()


def finish_rubber(ob):
    me = ob.data
    me.materials.clear()
    for n in RUBBER[:2]:
        me.materials.append(material(n))
    bm = bmesh.new()
    bm.from_mesh(me)
    bw = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    for e in bm.edges:
        sharp = len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(30)
        # the top edges and the outside upright corners; the bottoms and the inside corners stay sharp (owner,
        # 2026-11-24: "no chamfers on the bottom sides of the rubber pads", then "you accidentally removed some of
        # the vertical chamfers on the rubber vertical edges")
        upright = abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-4
        top = min(v.co.z for v in e.verts) > PLATE_T + 1e-4 and not upright
        e[bw] = 1.0 if sharp and (top or upright and e.is_convex) else 0.0
    bm.to_mesh(me)
    bm.free()
    bv = ob.modifiers.new("bev", "BEVEL")
    bv.width, bv.segments, bv.limit_method = BEVEL, SEGMENTS, "WEIGHT"
    bv.use_clamp_overlap, bv.face_strength_mode, bv.material = True, "FSTR_ALL", 1
    apply(ob, "bev")
    if "bevel_weight_edge" in me.attributes:
        me.attributes.remove(me.attributes["bevel_weight_edge"])
    me.materials.append(material(RUBBER[2]))
    for p in me.polygons:                        # walls: any other face steeper than about 53 degrees
        if p.material_index == 0 and abs(p.normal.z) < 0.6:
            p.material_index = 2
    smooth(ob, 60)
    uv_box(ob, 0.245, 0.5)


def finish_metal(ob, chamfer=True):
    """Paintable metal with a small chamfer on its prominent edges in the scratched paint (owner, 2026-11-24: "I
    want this metal plate to be paintable, and do small chamfers on all of the prominent metal edges, lets try
    scratched paintable on those chamfers"). The seam stays sharp, so the slice still closes it when straight, and
    so does the knuckle, which hides inside the plate behind."""
    me = ob.data
    me.materials.clear()
    caps = ob.name == "R3_plate"
    for n in METAL + (CAP if caps else ()):
        me.materials.append(material(n))
    if chamfer:
        bm = bmesh.new()
        bm.from_mesh(me)
        bw = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
        for e in bm.edges:
            ys = [v.co.y for v in e.verts]
            # the seam, the knuckle, and the tongue's base between the plate's front edge and the seam, where the
            # knuckle meets it (owner, 2026-11-24: "don't chamfer the knuckle where it intersects with the trailing
            # tread")
            # the knuckle's bottom side edges keep the slice's chamfer to its back corner (owner, 2026-11-24: "the
            # chamfer needs to continue to the edge/corners")
            side_bottom = all(v.co.z < 1e-4 for v in e.verts) and abs(ys[0] - ys[1]) > 1e-4
            # its top edges stop where the front pad's shoulders overhang them ("chamfer on the top side needs to
            # end where it overlaps with the rubber tread")
            under_pad = all(v.co.z > PLATE_T - 1e-4 for v in e.verts) and max(ys) < Y_SH - PITCH + 1e-4
            seam = (all(abs(y - SEAM) < 1e-4 for y in ys)
                    or (ob.name == "R3_tip" and (under_pad or max(ys) < SEAM - PITCH + 0.011 and not side_bottom))
                    or (ob.name == "R3_plate" and min(ys) > HALF_L - 1e-4 and max(ys) > HALF_L + 1e-4))
            # outside corners only: an inside corner (the tongue's base) chamfered twists the chamfer beside it
            e[bw] = 1.0 if (len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(30) and e.is_convex
                            and not seam) else 0.0
        bm.to_mesh(me)
        bm.free()
        bv = ob.modifiers.new("bev", "BEVEL")
        bv.width, bv.segments, bv.limit_method = CHAMFER, 1, "WEIGHT"
        # no clamp: Blender's clamp shrinks the whole bevel to its tightest spot, which left most chamfers a sliver
        # chamfer faces land in slot 2 for now (the scratched cap steel on the plate), sorted after the bevel
        bv.use_clamp_overlap, bv.face_strength_mode, bv.material = False, "FSTR_ALL", 2 if caps else 0
        apply(ob, "bev")
        if caps:
            for p in me.polygons:
                # all corners on one end: the front, back and long chamfer faces run end to end and stay painted
                xs = [me.vertices[i].co.x for i in p.vertices]
                on_cap = min(xs) > END_X - 1e-4 or max(xs) < -END_X + 1e-4
                chamfer = p.material_index == 2
                p.material_index = (2 if chamfer else 1) if on_cap else 0
        if ob.name == "R3_plate":
            # Blender slides the front edge's chamfer forward up the unchamfered tongue side at the tongue's base, so
            # it pinches to nothing there; put its top corner back on the chamfer line (owner, 2026-11-24, of the
            # front and back top edges: "JUST FIX THE CHAMFER ON THESE EDGES")
            for v in me.vertices:
                if (v.co.z > PLATE_T - 1e-4 or v.co.z < 1e-4) and HALF_L - 1e-4 < v.co.y < HALF_L + CHAMFER + 1e-3 and abs(v.co.x) < 0.8:
                    y = HALF_L - CHAMFER
                    v.co.x, v.co.y = math.copysign(TONGUE_C - y, v.co.x), y
        if "bevel_weight_edge" in me.attributes:
            me.attributes.remove(me.attributes["bevel_weight_edge"])
    # sharp from 10 degrees, so the crease where each end's tapers start stays crisp instead of smearing the
    # shading across the flat plate (owner, 2026-11-24: "something looks bad where the beveled end chamfers meet
    # with the flat part of the plate")
    smooth(ob, 10)
    uv_box(ob, 0.5, 0.5)     # chamfers too (5 UV per metre on them read "scaled way too small", owner, 2026-11-24)


def apply(ob, mod):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod)


def smooth(ob, deg):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))
    wn = ob.modifiers.get("wn") or ob.modifiers.new("wn", "WEIGHTED_NORMAL")
    wn.mode, wn.keep_sharp, wn.weight, wn.use_face_influence = "FACE_AREA", True, 100, True


def finish():
    for name in ("R3_pad_front", "R3_pad_rear"):
        finish_rubber(bpy.data.objects[name])
    finish_metal(bpy.data.objects["R3_plate"])
    finish_metal(bpy.data.objects["R3_tip"])
    if bpy.data.objects.get("R3_horn"):
        finish_metal(bpy.data.objects["R3_horn"], chamfer=False)   # hidden in the wheel's groove
    rod = bpy.data.objects["R3_rod"]          # dark steel, the Kharak Tread's metal
    rod.data.materials.clear()
    rod.data.materials.append(material("PaintedMetal_VeryDark"))
    smooth(rod, 30)
    uv_box(rod, 0.5, 0.5)


if __name__ == "__main__":
    finish()
    for name in ("R3_pad_front", "R3_pad_rear"):
        me = bpy.data.objects[name].data
        print(name, len(me.vertices), [m.name for m in me.materials],
              [sum(p.material_index == i for p in me.polygons) for i in range(len(me.materials))])
