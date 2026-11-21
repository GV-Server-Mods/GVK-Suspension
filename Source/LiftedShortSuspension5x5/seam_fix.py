"""Mitre Keen's seam network (se-dev-seut atlas-regions.md, "Joins and ends", "Inherited seams").

Strips come from seam_map.build(). nodes(S) groups strip ends; normalize(S, ed) maps Atlas4 strips' V exactly onto
piece 3's box; mitre(), tip() and apply_tris() do the joins. seam_driver.run() runs the whole pass in that order.
"""
import bpy, bmesh, math
from mathutils import Vector
from mathutils.geometry import intersect_line_line, intersect_point_line

B0, B1 = 0.4834, 0.5166


class Edit:
    """Vertex and UV edits per object, plus new tip triangles, applied with bmesh at the end."""
    def __init__(self, S):
        self.S = S; self.loops = {}; self.tris = []

    def loops_of(self, s):
        k = id(s)
        if k not in self.loops:
            me = bpy.data.objects[s['obj']].data; d = {}
            for f in s['faces']:
                for li in me.polygons[f].loop_indices:
                    d.setdefault(me.loops[li].vertex_index, []).append(li)
            self.loops[k] = d
        return self.loops[k]

    def move(self, s, sec, key, p, du=0.0, v=None):
        o = bpy.data.objects[s['obj']]; me = o.data; uvl = me.uv_layers.active.data
        vi = sec['lo'] if key == 'pl' else sec['hi']
        me.vertices[vi].co = o.matrix_world.inverted() @ p
        for li in self.loops_of(s)[vi]:
            uvl[li].uv.x += du
            if v is not None:
                uvl[li].uv.y = v
        sec[key] = p
        uk = 'ul' if key == 'pl' else 'uh'; sec[uk] += du
        if v is not None:
            sec['vl' if key == 'pl' else 'vh'] = v
        sec['c'] = (sec['pl'] + sec['ph']) / 2; sec['w'] = (sec['ph'] - sec['pl']).length


def normalize(S, ed):
    n = 0
    for s in S:
        if not s['mat'].startswith('Atlas4'):
            continue
        if s['v0'] > B0 - 0.0005 and s['v1'] < B1 + 0.0005:
            continue
        for q in s['secs']:
            vl, vh = q['vl'], q['vh']; pl, ph = q['pl'].copy(), q['ph'].copy()
            def at(v): return pl + (ph - pl) * ((v - vl) / (vh - vl))
            nl = max(vl, B0) if vl < vh else min(vl, B1)
            nh = min(vh, B1) if vl < vh else max(vh, B0)
            if abs(nl - vl) > 1e-6:
                ed.move(s, q, 'pl', at(nl), 0.0, nl)
            if abs(nh - vh) > 1e-6:
                ed.move(s, q, 'ph', at(nh), 0.0, nh)
        s['v0'] = min(min(q['vl'], q['vh']) for q in s['secs']); s['v1'] = max(max(q['vl'], q['vh']) for q in s['secs'])
        n += 1
    return n


def end(s, which):
    e = s['secs'][which]; p = s['secs'][1 if which == 0 else -2]
    d = (e['c'] - p['c']); dl = d.length
    us = (((e['ul'] + e['uh']) / 2) - ((p['ul'] + p['uh']) / 2)) / dl if dl > 1e-6 else 0.0
    return e, p, d / dl if dl > 1e-9 else d, us


def nodes(S, same=0.99):
    """Group strip ends that meet on one plane; T stems (an end on another strip's interior) get kind 'stem'.

    Ends on planes more than ~8 degrees apart are a seam carried over an edge or bevel, not a join, and a
    strip's two ends never join each other (a short bevel strip is shorter than the join radius).
    """
    ends = [(i, w) for i, s in enumerate(S) for w in (0, -1)]
    par = {k: k for k in ends}
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for a in range(len(ends)):
        ia, wa = ends[a]; ea, _, _, _ = end(S[ia], wa)
        for b in range(a + 1, len(ends)):
            ib, wb = ends[b]; eb, _, _, _ = end(S[ib], wb)
            if ia == ib or abs(S[ia]['n'].dot(S[ib]['n'])) < same:
                continue
            if (ea['c'] - eb['c']).length < 0.6 * (ea['w'] + eb['w']) / 2 + 0.003:
                ra, rb = find(ends[a]), find(ends[b])
                if ra != rb:
                    par[ra] = rb
    groups = {}
    for k in ends:
        groups.setdefault(find(k), []).append(k)
    out = []
    for g in groups.values():
        if len(g) == 1:
            ia, wa = g[0]; ea, _, da, _ = end(S[ia], wa)
            best = None
            for ib, B in enumerate(S):
                if ib == ia or abs(S[ia]['n'].dot(B['n'])) < same:
                    continue
                cs = [q['c'] for q in B['secs']]; acc = 0.0
                for k in range(len(cs) - 1):
                    q, t = intersect_point_line(ea['c'], cs[k], cs[k + 1])
                    sl = (cs[k + 1] - cs[k]).length
                    if 0.0 <= t <= 1.0:
                        d = (ea['c'] - q).length; wB = B['secs'][k]['w']
                        far = min(acc + t * sl, B['length'] - acc - t * sl)
                        if d < wB / 2 + ea['w'] / 2 + 0.004 and far > wB / 2 and (best is None or d < best[0]):
                            best = (d, ib, k)
                    acc += sl
            out.append(dict(kind='stem', ends=g, onto=best[1:]) if best else dict(kind='free', ends=g))
        else:
            out.append(dict(kind='node%d' % len(g), ends=g))
    return out


def angle_pair(S, a, b):
    _, _, da, _ = end(S[a[0]], a[1]); _, _, db, _ = end(S[b[0]], b[1])
    return math.degrees(da.angle(-db, 0.0))


def mitre(S, ed, a, b):
    A, B = S[a[0]], S[b[0]]
    eA, pA, dA, uA = end(A, a[1]); eB, pB, dB, uB = end(B, b[1])
    n = (A['n'] + B['n']).normalized()
    ang = math.degrees(dA.angle(-dB, 0.0))
    if ang < 2:
        P = (eA['c'] + eB['c']) / 2
    else:
        r = intersect_line_line(pA['c'], pA['c'] + dA, pB['c'], pB['c'] + dB)
        if r is None:
            return 'no intersection'
        P = (r[0] + r[1]) / 2
    tA, tB = dA, -dB
    th = tA.angle(tB, 0.0)
    if math.cos(th / 2) < 0.35:
        return 'too sharp'
    if (P - pA['c']).dot(dA) < 0.25 * eA['w'] or (P - pB['c']).dot(dB) < 0.25 * eB['w']:
        return 'end would invert'
    P = P + n * (((eA['c'] - P).dot(n) + (eB['c'] - P).dot(n)) / 2)
    sd = n.cross((tA + tB).normalized()).normalized()
    w = (min(eA['w'], width(A)) + min(eB['w'], width(B))) / 2 / math.cos(th / 2)
    moves = []
    for s, e, d, us in ((A, eA, dA, uA), (B, eB, dB, uB)):
        sg = 1.0 if sd.dot(e['ph'] - e['pl']) > 0 else -1.0
        for key, p in (('ph', P + sd * sg * w / 2), ('pl', P - sd * sg * w / 2)):
            moves.append((s, e, key, p, us * (p - e[key]).dot(d)))
    if max((p - e[key]).length for s, e, key, p, du in moves) < 0.0003:
        return 'already mitred'
    for s, e, key, p, du in moves:
        ed.move(s, e, key, p, du)
    return 'mitred'


def width(s):
    """The strip's own width: the median over its sections, so an end that is already mitred does not count."""
    ws = sorted(q['w'] for q in s['secs'][1:-1]) or sorted(q['w'] for q in s['secs'])
    return ws[len(ws) // 2]


def tip(S, ed, a, Q, u, hB, lift=0.001):
    """Point stem end a at the cross line (Q, u) of half-width hB; Q=None caps a free end half a width out."""
    A = S[a[0]]; eA, pA, dA, uA = end(A, a[1]); n = A['n']
    if Q is None:
        P = eA['c'] + dA * (eA['w'] / 2)
    else:
        m = n.cross(u).normalized()
        if m.dot(pA['c'] - Q) < 0:
            m = -m
        r = intersect_line_line(pA['c'], eA['c'], Q, Q + u)
        if r is None:
            return 'no intersection'
        P = r[0]
        E0 = Q + m * hB
        for key in ('pl', 'ph'):
            r2 = intersect_line_line(pA[key], eA[key], E0, E0 + u)
            if r2 is None:
                return 'no rail intersection'
            p = r2[0]
            if (p - pA[key]).dot(dA) < 0.2 * eA['w']:
                return 'end would invert'
            ed.move(A, eA, key, p, uA * (p - eA[key]).dot(dA))
    for key in ('pl', 'ph'):
        ed.move(A, eA, key, eA[key] + n * lift)
    P = P + n * ((eA['c'] - P).dot(n))
    uP = (eA['ul'] + eA['uh']) / 2 + uA * (P - eA['c']).dot(dA)
    vP = (A['v0'] + A['v1']) / 2
    ed.tris.append(dict(obj=A['obj'], s=A, lo=eA['lo'], hi=eA['hi'], P=P, uP=uP, vP=vP, n=n, face=A['faces'][0]))
    return 'pointed'


def apply_tris(ed):
    by = {}
    for t in ed.tris:
        by.setdefault(t['obj'], []).append(t)
    for name, ts in by.items():
        o = bpy.data.objects[name]; me = o.data; Mi = o.matrix_world.inverted(); N = o.matrix_world.to_3x3()
        bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        uvl = bm.loops.layers.uv.active
        refs = [(bm.faces[t['face']], bm.verts[t['lo']], bm.verts[t['hi']]) for t in ts]
        for t, (ref, vlo, vhi) in zip(ts, refs):
            uvlo = next(l[uvl].uv.copy() for l in vlo.link_loops)
            uvhi = next(l[uvl].uv.copy() for l in vhi.link_loops)
            vp = bm.verts.new(Mi @ t['P'])
            f = bm.faces.new((vlo, vhi, vp))
            f.material_index = ref.material_index; f.smooth = ref.smooth
            f.normal_update()
            uvs = {vlo: uvlo, vhi: uvhi, vp: Vector((t['uP'], t['vP']))}
            if (N @ f.normal).dot(t['n']) < 0:
                f.normal_flip()
            for l in f.loops:
                l[uvl].uv = uvs[l.vert]
        bm.to_mesh(me); bm.free(); me.update()
    return {k: len(v) for k, v in by.items()}
