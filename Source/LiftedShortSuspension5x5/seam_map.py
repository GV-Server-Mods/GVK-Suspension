"""Map seam decal strips (Atlas4 piece 3, Paneling 58 halves) in a collection: sections, ends, joins."""
import bpy, bmesh, math
from mathutils import Vector
from mathutils.geometry import intersect_point_line


def is_seam(mat, v0, v1):
    return (mat.startswith('Atlas4') and mat != 'Atlas4_Chrome' and 0.47 < v0 and v1 < 0.53) or \
           (mat.startswith('Paneling') and v1 < 0.031)


def build(col):
    strips = []
    for o in sorted(col.all_objects, key=lambda x: x.name):
        if o.type != 'MESH':
            continue
        me = o.data
        if not any(m and (m.name.startswith('Atlas4') or m.name.startswith('Paneling')) for m in me.materials):
            continue
        bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
        uvl = bm.loops.layers.uv.active
        M = o.matrix_world; seen = set()
        for f0 in bm.faces:
            if f0.index in seen:
                continue
            st = [f0]; seen.add(f0.index); fs = []
            while st:
                f = st.pop(); fs.append(f)
                for e in f.edges:
                    for g in e.link_faces:
                        if g.index not in seen:
                            seen.add(g.index); st.append(g)
            mat = me.materials[fs[0].material_index].name
            uv = {}
            for f in fs:
                for l in f.loops:
                    uv[l.vert.index] = l[uvl].uv.copy()
            vmin = min(u.y for u in uv.values()); vmax = max(u.y for u in uv.values())
            if not is_seam(mat, vmin, vmax):
                continue
            vids = list(uv); span = vmax - vmin
            side = {i: (0 if abs(uv[i].y - vmin) < 0.25 * span else (1 if abs(uv[i].y - vmax) < 0.25 * span else 2)) for i in vids}
            if any(s == 2 for s in side.values()):
                continue
            lows = [i for i in vids if side[i] == 0]; highs = [i for i in vids if side[i] == 1]
            if len(lows) != len(highs) or len(lows) < 2:
                continue
            edges = {(min(e.verts[0].index, e.verts[1].index), max(e.verts[0].index, e.verts[1].index)) for f in fs for e in f.edges}
            rail = {i: [] for i in lows}
            for a, b in edges:
                if a in rail and b in rail:
                    rail[a].append(b); rail[b].append(a)
            ends = [i for i in lows if len(rail[i]) <= 1]
            if len(ends) != 2:
                continue
            order = [ends[0]]
            while len(order) < len(lows):
                nx = [j for j in rail[order[-1]] if j not in order]
                if not nx:
                    break
                order.append(nx[0])
            if len(order) != len(lows):
                continue
            secs = []; ok = True
            for i in order:
                cand = [b if a == i else a for a, b in edges if i in (a, b) and side[b if a == i else a] == 1]
                if not cand:
                    ok = False; break
                j = min(cand, key=lambda h: abs(uv[h].x - uv[i].x))
                pl = M @ bm.verts[i].co; ph = M @ bm.verts[j].co
                secs.append(dict(lo=i, hi=j, pl=pl, ph=ph, c=(pl + ph) / 2, w=(ph - pl).length,
                                 ul=uv[i].x, uh=uv[j].x, vl=uv[i].y, vh=uv[j].y))
            if not ok or len({s['hi'] for s in secs}) != len(secs):
                continue
            n = sum(((M.to_3x3() @ f.normal).normalized() for f in fs), Vector()).normalized()
            L = sum((secs[k + 1]['c'] - secs[k]['c']).length for k in range(len(secs) - 1))
            half = mat.startswith('Paneling') or vmax < 0.505 or vmin > 0.495
            strips.append(dict(obj=o.name, mat=mat, v0=vmin, v1=vmax, faces=[f.index for f in fs], secs=secs, n=n,
                               length=L, half=half,
                               closed=(secs[0]['c'] - secs[-1]['c']).length < 0.6 * secs[0]['w'] and len(secs) > 2))
        bm.free()
    return strips


def enddir(s, which):
    e = s['secs'][which]; p = s['secs'][1 if which == 0 else -2]
    return (e['c'] - p['c']).normalized(), e


def nearest_on(sB, p):
    best = None; acc = 0.0
    cs = [q['c'] for q in sB['secs']]
    for k in range(len(cs) - 1):
        q, t = intersect_point_line(p, cs[k], cs[k + 1])
        t = max(0.0, min(1.0, t)); q = cs[k].lerp(cs[k + 1], t)
        d = (p - q).length; sl = (cs[k + 1] - cs[k]).length
        if best is None or d < best[0]:
            best = (d, acc + t * sl, k, q)
        acc += sl
    return best


def classify(S):
    """One record per strip end: (ia, which, kind, ib, ib_end_or_seg)."""
    out = []
    for ia, A in enumerate(S):
        for which in (0, -1):
            if A['closed']:
                out.append((ia, which, 'closed', ia, -1 - which if which == 0 else 0)); continue
            dA, e = enddir(A, which)
            best = None
            for ib, B in enumerate(S):
                if ib == ia:
                    continue
                if (B['secs'][0]['c'] - e['c']).length > B['length'] + 0.2:
                    continue
                d, along, k, q = nearest_on(B, e['c'])
                wB = B['secs'][0]['w']
                if d < wB / 2 + e['w'] / 2 + 0.005 and (best is None or d < best[0]):
                    near_end = min(along, B['length'] - along) < wB / 2 + e['w'] / 2 + 0.003
                    best = (d, ib, near_end, abs(A['n'].dot(B['n'])), along, k)
            if best is None:
                out.append((ia, which, 'free', None, None)); continue
            d, ib, near_end, nd, along, k = best
            edge = nd < 0.9
            if near_end:
                B = S[ib]
                wb = 0 if (B['secs'][0]['c'] - e['c']).length < (B['secs'][-1]['c'] - e['c']).length else -1
                out.append((ia, which, 'L-edge' if edge else 'L', ib, wb))
            else:
                out.append((ia, which, 'T-edge' if edge else 'T', ib, k))
    return out
