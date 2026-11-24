# Track builder icon for the Kharak Tread Mk II: five small links on a 3x3 curve, transparent background, as the
# Rubber Track's (Source/RubberTread/scripts/rt_icon.py). Run on the saved .blend after kt2_r3_export.py:
#   blender -b KharakTreadMk2.blend --python scripts\kt2_icon.py -- <out.png> [root pitch scale_x]
# The Kharak Tread and Double Tread icons use it too, on KharakTread.blend:
#   -- KharakTread.png KharakTread 0.78 1.104      -- KharakDoubleTread.png KharakDoubleTread 0.78 0.979
import math
import sys
import bpy
import mathutils

a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
DX, DY, DZ = 0.75, -0.9, 0.85
if len(a) >= 4:
    ROOT, PITCH, SX = a[1], float(a[2]), float(a[3])
else:
    HERE = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2\scripts"
    g = {"__name__": "kt2_r3_geom_lib", "LINK": "small", "LEVEL": "main"}
    exec(open(HERE + r"\kt2_r3_geom.py").read(), g)
    ROOT, PITCH = "KharakTreadMk2", 2 * g["HINGE_Y"]
    SX = 1.104                # SegmentScale X of the Mk II 3x3 style (TankTracks.ini)
RW = 3.3                      # the 3x3 curve, as rt_icon.py
root = bpy.data.objects[ROOT]
parts = [root] + list(root.children)
dg = bpy.context.evaluated_depsgraph_get()
meshes = {p.name: bpy.data.meshes.new_from_object(p.evaluated_get(dg)) for p in parts if p.type == "MESH"}
sc = bpy.data.scenes.new("Icon")
links = []
for i in range(-2, 3):
    t = i * PITCH / RW
    m = (mathutils.Matrix.Translation((0, RW * math.sin(t), RW * math.cos(t) - RW))
         @ mathutils.Matrix.Rotation(-t, 4, "X") @ mathutils.Matrix.Diagonal((SX, 1, 1, 1)))
    for p in parts:
        if p.type != "MESH":
            continue
        c = bpy.data.objects.new("icon_%d_%s" % (i, p.name), meshes[p.name])   # with modifiers (slot, bevels)
        c.matrix_world = m @ root.matrix_world.inverted() @ p.matrix_world
        sc.collection.objects.link(c)
        links.append(c)
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        sc.render.engine = eng
        break
    except TypeError:
        pass
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 512
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value, bg.inputs[1].default_value = (0.5, 0.52, 0.55, 1), 0.9
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 7.0
sun.rotation_euler = (math.radians(40), math.radians(-15), math.radians(35))
sc.collection.objects.link(sun)
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
sc.render.filepath = out
with bpy.context.temp_override(scene=sc):
    bpy.ops.render.render(write_still=True, scene=sc.name)
print("ICON", out)
