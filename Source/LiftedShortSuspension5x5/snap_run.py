import bpy
import numpy as np
from mathutils import Vector

DS = {}
exec(open(r"C:\Users\blayl\source\repos\se-dev-seut\scripts\decal_snap.py").read(), DS)
DEC, KEEP = DS["DEC"], DS["KEEP"]


def lift_dips(col, deep=0.0012, target=0.0009):
    """Move decal triangles that sit 0..1.2 mm under KEEP (before rounding) out along their normal to 0.9 mm."""
    rb, tb, dec = DS["surfaces"](col); out = {}
    for o, kind in dec:
        me = o.data; M = o.matrix_world; Mi = M.inverted_safe(); N = Mi.transposed().to_3x3()
        g = DS["gaps"](tb, o, kind, False)
        mv = {}
        for ti, (vs, lo) in g.items():
            if lo is None or lo >= KEEP or lo < KEEP - deep:
                continue
            t = me.loop_triangles[ti]; n = (N @ t.normal).normalized(); d = target - lo
            for i in vs:
                if i not in mv or mv[i][0] < d:
                    mv[i] = (d, n)
        if mv:
            cn = [tuple(c.vector) for c in me.corner_normals]
            for i, (d, n) in mv.items():
                me.vertices[i].co = Mi @ (M @ me.vertices[i].co + n * d)
            me.update()
            for p in me.polygons:
                p.use_smooth = True
            me.normals_split_custom_set(cn)
        out[o.name] = len(mv)
    return out


def broken(col):
    """Decal triangles under KEEP after the game's rounding, per object."""
    rb, tb, dec = DS["surfaces"](col)
    return {o.name: sum(1 for v, g in DS["gaps"](rb, o, kind).values() if g is not None and g < KEEP) for o, kind in dec}


def run(col):
    before = broken(col)
    dips = lift_dips(col)
    rep = DS["snap"](col)
    after = broken(col)
    return before, dips, rep, after
