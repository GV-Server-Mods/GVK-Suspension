"""Kharak Tread Mk II blockout review renders and joint numbers.

Run in Blender after kt2_build.py (ONLY = "A" or "B" renders one tongue):
    exec(open(r"...\\kt2_review.py").read(), {"__name__": "__main__", "ONLY": "A"})

Lays links out as Tank Tracks does: hull points on a circle of sqrt(R^2 + (pitch/2)^2) round each wheel, each
link's chord between two hull points, then moved along its own normal by SegmentOffset Y. Y follows the Kharak
Tread rule (outer face on the collision sphere on the ground run): Y = sphere - thickness - hull radius.
The hinge between two links is the hull point, at height -Y in the link's frame.
"""
import math
import os
import bpy
from mathutils import Matrix, Vector

ROOT = r"C:\Users\blayl\source\repos\MDK2 Mods\GVK_Suspension\Source\KharakTreadMk2"
OUT = os.path.join(ROOT, "review", "renders")
BUILD = os.path.join(ROOT, "scripts", "kt2_build.py")
PITCH = 233 * 2.80 / 886.0
THICK = 0.24
PLATE_T = 0.14
WHEELS = {  # name: (reported radius, collision sphere)
    "TankWheel1x1": (0.897, 1.1),
    "TankWheel2x2": (2.121, 2.278),
    "TankWheel3x3": (3.255, 3.4),
}
RENDERED = ("TankWheel3x3", "TankWheel1x1")
RES = (900, 560)


def build_lib():
    ns = {"__name__": "kt2_build_lib"}
    exec(open(BUILD).read(), ns)
    return ns


# ---------------------------------------------------------------- joint numbers (link frame: y along, z out)

def hull(radius, sphere):
    rh = math.sqrt(radius ** 2 + (PITCH / 2) ** 2)
    return rh, sphere - THICK - rh, 2 * math.asin(PITCH / 2 / rh)


def to_next(p, theta, h):
    """A point (y, z) of one link in the frame of the link ahead, on a joint that turns theta toward the wheel."""
    d = (p[0] - PITCH / 2, p[1] - h)
    c, s = math.cos(theta), math.sin(theta)
    return (-PITCH / 2 + c * d[0] - s * d[1], h + s * d[0] + c * d[1])


def inside(pt, poly):
    x, y = pt
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def edge_dist(pt, poly):
    best = 1e9
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((pt[0] - x1) * dx + (pt[1] - y1) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(pt[0] - x1 - t * dx, pt[1] - y1 - t * dy))
    return best


def joint_numbers(lib):
    rows = []
    plate_b = lib["plate_outline_b"]()
    tip_y, half_l = lib["TIP_Y"], lib["HALF_L"]
    tongue = [p for p in plate_b if p[1] > half_l - 1e-6]          # the arrowhead part ahead of the plate
    for name, (radius, sphere) in WHEELS.items():
        rh, yo, theta = hull(radius, sphere)
        h = -yo
        lift = to_next((tip_y, PLATE_T), theta, h)[1] - PLATE_T
        tip_bottom = to_next((tip_y, 0.0), theta, h)[1]
        corner = to_next((half_l, 0.0), theta, h)
        overlap = corner[0] + half_l
        clip = 0.0
        for (x1, y1), (x2, y2) in zip(tongue, tongue[1:]):
            for k in range(21):
                x, y = x1 + (x2 - x1) * k / 20, y1 + (y2 - y1) * k / 20
                for z in (0.0, 0.035, 0.07):
                    ny, nz = to_next((y, z), theta, h)
                    if 0 < nz < PLATE_T and inside((x, ny), plate_b):
                        clip = max(clip, edge_dist((x, ny), plate_b))
        c_open = (THICK - h) * math.sin(theta)      # C: the cut at the hinge line opens this much at the outer face
        c_into = h * math.sin(theta)                # C: and its bottom corner runs this far into the piece ahead
        # D: how far the big lip stands above the outer face of the link behind, once that link has turned
        n_top, n_face = (-math.sin(theta), math.cos(theta)), (math.cos(theta), math.sin(theta))
        proud = 0.0
        for y, z in lib["lip_yz"]()[2]:
            d = (y + PITCH / 2, z - h)
            if d[0] * n_face[0] + d[1] * n_face[1] < 0:
                proud = max(proud, d[0] * n_top[0] + d[1] * n_top[1] - (THICK - h))
        rows.append((name, round(math.degrees(theta), 1), round(yo, 4), round(radius + yo - lib_drawn(name), 3),
                     round(lift, 3), round(tip_bottom, 3), round(overlap, 3), round(clip, 3), round(c_open, 3),
                     round(c_into, 3), round(proud, 3)))
    return rows


def lib_drawn(name):
    return {"TankWheel1x1": 0.833, "TankWheel2x2": 2.033, "TankWheel3x3": 3.165}[name]


# ---------------------------------------------------------------- layout

def chain(radius, sphere, n_straight=3):
    """Hull points: a ground run, the wheel's front half, a top run. Returns link matrices and the points."""
    rh, yo, step = hull(radius, sphere)
    pts = [(-k * PITCH, -rh) for k in range(n_straight, 0, -1)]
    phi = -math.pi / 2
    while phi <= math.pi / 2 + step / 2:
        pts.append((rh * math.cos(phi), rh * math.sin(phi)))
        phi += step
    last_phi = phi - step
    last = pts[-1]
    tdir = (-math.sin(last_phi), math.cos(last_phi))
    for k in range(1, n_straight + 1):
        pts.append((last[0] + tdir[0] * PITCH * k, last[1] + tdir[1] * PITCH * k))
    mats = []
    for a, b in zip(pts, pts[1:]):
        d = (b[0] - a[0], b[1] - a[1])
        ln = math.hypot(*d)
        d = (d[0] / ln, d[1] / ln)
        n = (d[1], -d[0])
        y_axis = Vector((0, d[0], d[1]))
        z_axis = Vector((0, n[0], n[1]))
        rot = Matrix((y_axis.cross(z_axis), y_axis, z_axis)).transposed().to_4x4()
        mid = ((a[0] + b[0]) / 2 + n[0] * yo, (a[1] + b[1]) / 2 + n[1] * yo)
        mats.append(Matrix.Translation((0, mid[0], mid[1])) @ rot)
    return mats, pts, rh, yo


def rubber_mid(ob):
    me = ob.data
    idx = {i for i, mt in enumerate(me.materials) if mt and mt.name == "RubberWheels"}
    zs = [me.vertices[v].co.z for p in me.polygons if p.material_index in idx for v in p.vertices]
    return (min(zs) + max(zs)) / 2


# ---------------------------------------------------------------- scenes

def set_engine(sc, engine):
    try:
        sc.render.engine = engine
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"


def scene_setup(name, engine):
    sc = bpy.data.scenes.get(name)
    if sc:
        for ob in list(sc.objects):
            bpy.data.objects.remove(ob)
    else:
        sc = bpy.data.scenes.new(name)
    set_engine(sc, engine)
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    world = bpy.data.worlds.get("KT2_world") or bpy.data.worlds.new("KT2_world")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.72, 0.77, 0.84, 1)
    bg.inputs["Strength"].default_value = 0.8
    world.color = (0.8, 0.8, 0.8)
    sc.world = world
    if engine == "BLENDER_WORKBENCH":
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_object_outline = False
    else:
        try:
            sc.eevee.taa_render_samples = 32
        except AttributeError:
            pass
    return sc


def add_sun(sc):
    li = bpy.data.lights.get("KT2_sun") or bpy.data.lights.new("KT2_sun", "SUN")
    li.energy = 3.5
    li.angle = math.radians(3)
    ob = bpy.data.objects.new("KT2_sun", li)
    ob.rotation_euler = Vector((-0.55, -0.35, -0.75)).to_track_quat("-Z", "Y").to_euler()   # from +X, ahead, above
    sc.collection.objects.link(ob)


def add_ground(sc, z, size=40):
    me = bpy.data.meshes.get("KT2_ground")
    if me is None:
        me = bpy.data.meshes.new("KT2_ground")
        s = size / 2
        me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
        mat = bpy.data.materials.get("KT2_sand") or bpy.data.materials.new("KT2_sand")
        mat.use_nodes = True
        col = (0.62, 0.52, 0.38, 1)
        next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = col
        mat.diffuse_color = col
        me.materials.append(mat)
    ob = bpy.data.objects.new("KT2_ground", me)
    ob.location.z = z
    sc.collection.objects.link(ob)


def camera(sc, loc, target, lens=40, ortho=None, clip=None):
    cam = bpy.data.cameras.new("KT2_cam")
    if ortho:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho
    else:
        cam.lens = lens
    cam.clip_start = clip if clip else 0.05
    cam.clip_end = 200
    ob = bpy.data.objects.new("KT2_cam", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(ob)
    sc.camera = ob


def link_instance(sc, variant, mat, name):
    ob = bpy.data.objects.new(name, None)
    ob.instance_type = "COLLECTION"
    ob.instance_collection = bpy.data.collections[f"KT2_{variant}"]
    ob.matrix_world = mat
    sc.collection.objects.link(ob)


def render(sc, name):
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True, scene=sc.name)


def top_view(variant):
    """Flat top view at the mockup's scale and framing (923 x 551 px, 2.80 m = 886 px), transparent background."""
    sc = scene_setup(f"KT2_top_{variant}", "BLENDER_WORKBENCH")
    sc.render.resolution_x, sc.render.resolution_y = 923, 551
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"
    sc.display.shading.light = "FLAT"
    for k in range(-1, 3):
        link_instance(sc, variant, Matrix.Translation((0, k * PITCH, 0)), f"L{k}")
    s = 2.80 / 886.0
    cx, cy = (461.5 - 464.5) * s, (412.0 - 275.5) * s
    camera(sc, (cx, cy, 5), (cx, cy, 0), ortho=923 * s)
    render(sc, f"top_{variant}")


def straight_view(variant):
    sc = scene_setup(f"KT2_straight_{variant}", "BLENDER_EEVEE_NEXT")
    add_sun(sc)
    add_ground(sc, -0.001)
    for k in range(-1, 2):
        link_instance(sc, variant, Matrix.Translation((0, k * PITCH, 0)), f"L{k}")
    camera(sc, (3.0, 2.9, 2.4), (0, 0.15, 0.0), lens=38)
    render(sc, f"straight_{variant}")


def hinge_view(variant, bar_y, bar_z, s=1.0, name=None, x=None):
    """The hinge bar under the tongue, three links straight, looking down the notch's side gap at x along its
    45 degrees: a wide view (<name>_wide) and a close one down into the gap (<name>)."""
    sc = scene_setup(f"KT2_hinge_{variant}", "BLENDER_EEVEE_NEXT")
    add_sun(sc)
    add_ground(sc, -0.001)
    for k in range(-1, 2):
        link_instance(sc, variant, Matrix.Translation((0, k * PITCH, 0)), f"L{k}")
    target = Vector((0.5 * s if x is None else x, bar_y, bar_z))
    name = name or f"hinge_{variant}"
    for sfx, d, dist in (("_wide", (0.9, -0.9, 0.7), 2.2), ("", (0.6, -0.6, 0.9), 0.9)):
        for ob in [o for o in sc.collection.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(ob)
        camera(sc, target + Vector(d).normalized() * dist * s, target, lens=40, clip=0.01)
        render(sc, name + sfx)


def ring(sc, radius, width=0.012, seg=256):
    """A thin red ring in the track's plane at the drawn tire radius, for the cut views."""
    me = bpy.data.meshes.new("KT2_ring")
    vs, fs = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for r in (radius - width, radius):
            vs.append((0.0, r * math.cos(a), r * math.sin(a)))
    for i in range(seg):
        j = (i + 1) % seg
        fs.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    me.from_pydata(vs, [], fs)
    mat = bpy.data.materials.get("KT2_red") or bpy.data.materials.new("KT2_red")
    mat.diffuse_color = (0.85, 0.1, 0.1, 1)
    me.materials.append(mat)
    ob = bpy.data.objects.new("KT2_ring", me)
    ob.location.x = -0.05
    sc.collection.objects.link(ob)


def wheel_scene(name, variant, wheel, engine, with_wheel=True):
    radius, sphere = WHEELS[wheel]
    sc = scene_setup(name, engine)
    if engine != "BLENDER_WORKBENCH":
        add_sun(sc)
    if with_wheel:
        src = bpy.data.objects[wheel]
        wob = bpy.data.objects.new(f"{wheel}_view", src.data)
        wob.matrix_world = Matrix.Translation((-rubber_mid(src), 0, 0)) @ Matrix.Rotation(math.radians(90), 4, "Y")
        sc.collection.objects.link(wob)
    else:
        ring(sc, lib_drawn(wheel))
    mats, pts, rh, yo = chain(radius, sphere)
    for i, mt in enumerate(mats):
        link_instance(sc, variant, mt, f"L{i}")
    add_ground(sc, -sphere)
    return sc, pts, rh, yo, sphere


def wheel_views(variant, wheel):
    tag = wheel.replace("TankWheel", "")
    # whole run from the outer side
    sc, pts, rh, yo, sphere = wheel_scene(f"KT2_{tag}_run_{variant}", variant, wheel, "BLENDER_EEVEE_NEXT")
    ys = [p[0] for p in pts]
    y0, y1 = min(ys) - PITCH, max(ys) + 0.4
    z0, z1 = -sphere - 0.15, sphere + 0.15
    scale = max(y1 - y0, (z1 - z0) * RES[0] / RES[1]) * 1.04
    cy, cz = (y0 + y1) / 2, (z0 + z1) / 2
    camera(sc, (30, cy, cz), (0, cy, cz), ortho=scale)
    render(sc, f"{tag}_run_{variant}")
    # the joint on the wheel's front nearest 10 degrees above the axle: cut on the center line, and a close view
    circle = pts[3:-3]
    j = min(circle, key=lambda p: abs(math.degrees(math.atan2(p[1], p[0])) - 10))
    j = Vector((0, *j))
    u = j.normalized()
    t = Vector((0, -u.z, u.y))
    js = j * (1 + (THICK + yo) / rh)
    sc, *_ = wheel_scene(f"KT2_{tag}_cut_{variant}", variant, wheel, "BLENDER_WORKBENCH", with_wheel=False)
    c = j + t * 0.12
    camera(sc, (30, c.y, c.z), (0, c.y, c.z), ortho=1.5, clip=30 - 0.02)
    render(sc, f"{tag}_cut_{variant}")
    sc, *_ = wheel_scene(f"KT2_{tag}_close_{variant}", variant, wheel, "BLENDER_EEVEE_NEXT")
    loc = js + u * 1.6 + Vector((2.3, 0, 0)) + t * 1.9
    camera(sc, loc, js + t * 0.15, lens=30)
    render(sc, f"{tag}_close_{variant}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    lib = build_lib()
    for v in ("A", "B", "C", "D"):
        for ob in bpy.data.collections[f"KT2_{v}"].objects:
            ob.location = (0, 0, 0)
    bpy.data.materials["KT2_metal"].diffuse_color = (0.58, 0.6, 0.63, 1)   # workbench views only
    print("wheel, deg per link, Y, plate underside vs drawn wheel on the curve, A tongue lift, B tongue bottom at "
          "tip, plate bottom corner overlap, B notch side clip, C cut opening at the top, C bottom corner overlap")
    for row in joint_numbers(lib):
        print(row)
    only = globals().get("ONLY")
    for v in ([only] if only else ["A", "B", "C"]):
        top_view(v)
        straight_view(v)
        if v in "CD":
            hinge_view(v, lib["BAR_Y"], lib["BAR_Z"],
                       x=lib["arrow_half"](lib["BAR_Y"] + PITCH) + lib["NOTCH_GAP"] / math.sqrt(2))
        for w in RENDERED:
            wheel_views(v, w)
    print("done", only)
