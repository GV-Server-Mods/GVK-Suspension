"""Run the seam mitre pass on a collection. Needs SM, SF, DS namespaces (seam_map, seam_fix, decal_snap).

Exec this file in a namespace that holds decal_snap's DEC set, e.g. DR = {'DEC': DS['DEC']}, then
DR['run'](main, SM, SF, DS). Run it on Keen's seams once (it is not idempotent), then snap_run.run(main).
"""
import math
from collections import Counter
from mathutils.bvhtree import BVHTree


def decal_bvh(dec):
    """Every decal face of the collection, in world space."""
    pts, polys = [], []
    for o, kind in dec:
        M = o.matrix_world; me = o.data; b = len(pts)
        pts += [M @ v.co for v in me.vertices]
        polys += [[b + i for i in p.vertices] for p in me.polygons if kind(p.material_index) in DEC]
    return BVHTree.FromPolygons(pts, polys)


def mid(q):
    """The groove's centre line (v = 0.5) across section q; on a half strip that is one of its rails."""
    t = (0.5 - q['vl']) / (q['vh'] - q['vl'])
    return q['pl'] + (q['ph'] - q['pl']) * t


def reach(q, Q, u, n, pA):
    """How far cross section q extends from its centre line Q toward the stem body at pA: where the stem's sides stop."""
    m = n.cross(u).normalized()
    if m.dot(pA - Q) < 0:
        m = -m
    return max(0.0, max((q['pl'] - Q).dot(m), (q['ph'] - Q).dot(m)))


def run(col, SM, SF, DS, apply=True):
    rb, tb, dec = DS['surfaces'](col)
    db = decal_bvh(dec)
    S = SM['build'](col); ed = SF['Edit'](S)
    N = SF['nodes'](S)  # group on Keen's geometry; normalizing V first narrows strips and splits joins
    nn = SF['normalize'](S, ed) if apply else 0
    allends = [(i, w) for i, s in enumerate(S) for w in (0, -1)]
    res = Counter(); marks = []
    for nd in N:
        k = nd['kind']; g = nd['ends']
        if k == 'node2':
            a, b = g
            if SF['angle_pair'](S, a, b) < 5:
                res['straight join, left'] += 1; continue
            c = S[a[0]]['secs'][a[1]]['c'].copy()
            r = SF['mitre'](S, ed, a, b) if apply else 'dry'
            res['corner ' + r] += 1; marks.append(('corner', c, S[a[0]]['n'].copy(), r))
        elif k == 'node3':
            pairs = [(SF['angle_pair'](S, g[i], g[j]), i, j) for i in range(3) for j in range(i + 1, 3)]
            ang, i, j = min(pairs)
            c = S[g[0][0]]['secs'][g[0][1]]['c'].copy()
            if ang > 15:
                res['3-way without a through line, left'] += 1; marks.append(('3way', c, S[g[0][0]]['n'].copy(), 'left')); continue
            st = [g[x] for x in range(3) if x not in (i, j)][0]
            if S[st[0]]['half']:
                res['half stem, left'] += 1; continue
            e1, _, d1, _ = SF['end'](S[g[i][0]], g[i][1]); e2, _, d2, _ = SF['end'](S[g[j][0]], g[j][1])
            Q = (mid(e1) + mid(e2)) / 2; u = (d1 - d2).normalized()
            if apply:  # square both halves of the through line at Q, so the stem's tip leaves no gap
                for (si, sw) in (g[i], g[j]):
                    ee, _, dd, us = SF['end'](S[si], sw)
                    for key in ('pl', 'ph'):
                        p = ee[key] + dd * (Q - ee[key]).dot(dd)
                        ed.move(S[si], ee, key, p, us * (p - ee[key]).dot(dd))
            pA = SF['end'](S[st[0]], st[1])[1]['c']
            hB = (reach(e1, Q, u, S[st[0]]['n'], pA) + reach(e2, Q, u, S[st[0]]['n'], pA)) / 2
            r = SF['tip'](S, ed, st, Q, u, hB) if apply else 'dry'
            res['T (3-way) ' + r] += 1; marks.append(('T3', c, S[st[0]]['n'].copy(), r))
        elif k == 'stem':
            a = g[0]
            if S[a[0]]['half']:
                res['half stem, left'] += 1; continue
            ib, kk = nd['onto']; B = S[ib]
            q = B['secs'][kk]; Q = mid(q); u = (B['secs'][kk + 1]['c'] - q['c']).normalized()
            hB = reach(q, Q, u, S[a[0]]['n'], SF['end'](S[a[0]], a[1])[1]['c'])
            c = S[a[0]]['secs'][a[1]]['c'].copy()
            r = SF['tip'](S, ed, a, Q, u, hB) if apply else 'dry'
            res['T stem ' + r] += 1; marks.append(('T', c, S[a[0]]['n'].copy(), r))
        elif k == 'free' and S[g[0][0]]['closed']:
            i = g[0][0]
            if g[0][1] != 0:
                continue
            c = S[i]['secs'][0]['c'].copy()
            if SF['angle_pair'](S, (i, 0), (i, -1)) < 5:
                res['closed loop, straight join, left'] += 1; continue
            r = SF['mitre'](S, ed, (i, 0), (i, -1)) if apply else 'dry'
            res['closed loop corner ' + r] += 1; marks.append(('loop', c, S[i]['n'].copy(), r))
        elif k == 'free':
            a = g[0]; e, _, d, _ = SF['end'](S[a[0]], a[1])
            if any((SF['end'](S[i], w)[0]['c'] - e['c']).length < 0.6 * (e['w'] + S[i]['secs'][w]['w']) / 2 + 0.005
                   for i, w in allends if i != a[0]):
                res['continues over an edge'] += 1; continue
            n = S[a[0]]['n']; ok = True; why = 'free end at a face edge, left'
            for f in (0.5, 1.0):
                p = e['c'] + d * (e['w'] * f) + n * 0.02
                h = tb.ray_cast(p, -n, 0.05)
                if h[0] is None or math.degrees(h[1].angle(n)) > 10 or not 0.0195 < h[3] < 0.026:
                    ok = False
                hd = db.ray_cast(p, -n, 0.025)
                if hd[0] is not None and ok:
                    ok = False; why = 'free end runs into another decal, left'
            if not ok:
                res[why] += 1; marks.append(('skip', e['c'].copy(), n.copy(), why)); continue
            if S[a[0]]['half']:
                res['half free end, left'] += 1; continue
            c = e['c'].copy()
            r = SF['tip'](S, ed, a, None, None, None, lift=0.0) if apply else 'dry'
            res['free cap ' + r] += 1; marks.append(('cap', c, n.copy(), r))
        else:
            res[k + ' left'] += 1
            marks.append((k, S[g[0][0]]['secs'][g[0][1]]['c'].copy(), S[g[0][0]]['n'].copy(), 'left'))
    added = SF['apply_tris'](ed) if apply else {}
    return dict(strips=len(S), normalized=nn, kinds=Counter(n['kind'] for n in N), res=res, added=added, marks=marks)
