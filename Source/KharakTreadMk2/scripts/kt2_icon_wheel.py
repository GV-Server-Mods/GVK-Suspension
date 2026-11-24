# Mockup: kt2_icon.py's five links, wrapped on their 3x3 wheel. Renders <out>_wheel.png (links + wheel) and
# <out>_links.png (links alone, same camera). Args after --:
#   out root pitch sx sz wheel_blend wheel_obj xlo xhi [turn sun_tilt sun_heading sun_energy fill]
# xlo..xhi: |x| band of the link's underside that rests on the tire (beside the groove).
# turn: degrees about Z for the links (180 shows their back edge); sun tilt from vertical and heading, degrees.
import math, sys, bpy, mathutils

a = sys.argv[sys.argv.index("--") + 1:]
out, ROOT, PITCH, SX, SZ, WB, WO, XLO, XHI = a[0], a[1], float(a[2]), float(a[3]), float(a[4]), a[5], a[6], float(a[7]), float(a[8])
TURN, SUN_T, SUN_H, SUN_E, FILL = [float(v) for v in a[9:14]] if len(a) >= 14 else (0, 40, 35, 7.0, 0.9)
AO = float(a[14]) if len(a) >= 15 else 0.0     # ambient occlusion distance, m (0: off): darkens grooves only
RIM = float(a[15]) if len(a) >= 16 else 0.0    # energy of a second sun from behind that lights only the edges (0: off)
DX, DY, DZ = 0.75, -0.9, 0.85

root = bpy.data.objects[ROOT]
parts = [p for p in [root] + list(root.children) if p.type == "MESH"]
dg = bpy.context.evaluated_depsgraph_get()
meshes = {p.name: bpy.data.meshes.new_from_object(p.evaluated_get(dg)) for p in parts}
inv = root.matrix_world.inverted()
zs = [((inv @ p.matrix_world) @ v.co).z * SZ for p in parts for v in meshes[p.name].vertices
      if XLO <= abs(((inv @ p.matrix_world) @ v.co).x) * SX <= XHI and abs(((inv @ p.matrix_world) @ v.co).y) < 0.25]
ZU = min(zs)

with bpy.data.libraries.load(WB, link=False) as (src, dst):
    dst.objects = [WO]
wob = dst.objects[0]
wme = bpy.data.meshes.new_from_object(wob)
rub = [i for i, m in enumerate(wme.materials) if m and "Rubber" in m.name]
rv = {vi for p in wme.polygons if p.material_index in rub for vi in p.vertices}
rz = [wme.vertices[i].co.z for i in rv]
ZC = (min(rz) + max(rz)) / 2
R = max(math.hypot(wme.vertices[i].co.x, wme.vertices[i].co.y) for i in rv)
allz = [v.co.z for v in wme.vertices]
stub_neg = (ZC - min(allz)) > (max(allz) - ZC)   # the hub stub runs toward -Z
RW = R - ZU
print("WHEEL", WO, "R", round(R, 3), "ZC", round(ZC, 3), "ZU", round(ZU, 3), "RW", round(RW, 3), "stub-Z", stub_neg)

sc = bpy.data.scenes.new("IconWheel")
links = []
for i in range(-2, 3):
    t = i * PITCH / RW
    m = (mathutils.Matrix.Rotation(math.radians(TURN), 4, "Z") @ mathutils.Matrix.Translation((0, RW * math.sin(t), RW * math.cos(t) - RW))
         @ mathutils.Matrix.Rotation(-t, 4, "X") @ mathutils.Matrix.Diagonal((SX, 1, SZ, 1)))
    for p in parts:
        c = bpy.data.objects.new("icon_%d_%s" % (i, p.name), meshes[p.name])
        c.matrix_world = m @ inv @ p.matrix_world
        sc.collection.objects.link(c)
        links.append(c)
# wheel: its axle (local Z) along X, the stub away from the camera (-X), tire centre on x = 0, axle at the curve centre
ang = math.pi / 2 if stub_neg else -math.pi / 2
rot = mathutils.Matrix.Rotation(ang, 4, "Y")
off = (rot @ mathutils.Vector((0, 0, ZC))).x
w = bpy.data.objects.new("icon_wheel", wme)
w.matrix_world = mathutils.Matrix.Translation((-off, 0, -RW)) @ rot
sc.collection.objects.link(w)

for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        sc.render.engine = eng
        break
    except TypeError:
        pass
if AO > 0:
    ee = sc.eevee
    for k, v in (("use_raytracing", True), ("use_fast_gi", True), ("fast_gi_method", "AMBIENT_OCCLUSION_ONLY"),
                 ("fast_gi_distance", AO), ("use_gtao", True), ("gtao_distance", AO)):
        if hasattr(ee, k):
            try:
                setattr(ee, k, v)
            except (TypeError, AttributeError) as e:
                print("AO skip", k, e)
    print("AO", {k: getattr(ee, k) for k in ("use_raytracing", "use_fast_gi", "fast_gi_method", "fast_gi_distance") if hasattr(ee, k)})
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 512
sc.view_settings.view_transform = "Standard"
wd = bpy.data.worlds.new("w")
sc.world = wd
wd.use_nodes = True
bg = next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value, bg.inputs[1].default_value = (0.5, 0.52, 0.55, 1), FILL
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = SUN_E
sun.rotation_euler = (math.radians(SUN_T), math.radians(-15), math.radians(SUN_H))
sc.collection.objects.link(sun)
if RIM > 0:
    rim = bpy.data.objects.new("rim", bpy.data.lights.new("rim", "SUN"))
    rim.data.energy = RIM
    rim.rotation_euler = (math.radians(65), math.radians(-15), math.radians(200))
    sc.collection.objects.link(rim)
cd = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cd)
sc.collection.objects.link(cam)
sc.camera = cam
dv = mathutils.Vector((DX, DY, DZ)).normalized()
pts = [o.matrix_world @ v.co for o in links for v in o.data.vertices]
lo = mathutils.Vector([min(p[i] for p in pts) for i in range(3)])
hi = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
c = (lo + hi) / 2
cam.location = c + dv * 30
fwd = -dv
right = fwd.cross(mathutils.Vector((0, 0, 1))).normalized()
upv = right.cross(fwd).normalized()
cam.rotation_euler = mathutils.Matrix((right, upv, -fwd)).transposed().to_euler()
cd.type, cd.clip_end = "ORTHO", 100
xs = [(p - c).dot(right) for p in pts]
ys = [(p - c).dot(upv) for p in pts]
cd.ortho_scale = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.06
cam.location += right * (max(xs) + min(xs)) / 2 + upv * (max(ys) + min(ys)) / 2
for tag, hide in (("_wheel", False), ("_links", True)):
    w.hide_render = hide
    sc.render.filepath = out + tag + ".png"
    with bpy.context.temp_override(scene=sc):
        bpy.ops.render.render(write_still=True, scene=sc.name)
print("ICON", out)
