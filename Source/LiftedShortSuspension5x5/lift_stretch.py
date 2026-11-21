"""Stretch the arm of a SEUT-imported suspension model along world -Y.

Run inside Blender with exec(open(path).read(), ns). Uses world space throughout.
Rules (se-dev-seut kitbash.md):
  - Arm islands: every vertex with world y < cut moves by -lift in y.
  - Tiling materials: UVs of moved loops shift by -lift * dUV/dy per UV island,
    so stretched faces keep their texel density and stay continuous.
  - Non-tiling decal islands that cross the cut: a single long quad gets a thin
    stretch band in its uniform middle; anything else moves or stays whole by
    its centroid.
  - Corner normals are recorded first and written back afterwards.
"""
import bpy, bmesh, statistics
from mathutils import Vector
from mathutils.bvhtree import BVHTree

NONTILE = ('Atlas1', 'Atlas2', 'Atlas3', 'ButtonsAtlas', 'TextAtlas')


def world_bvh(objs):
    bm = bmesh.new()
    for o in objs:
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        me = bpy.data.meshes.new('tmp_bvh'); t.to_mesh(me); t.free()
        bm.from_mesh(me); bpy.data.meshes.remove(me)
    tr = BVHTree.FromBMesh(bm); bm.free()
    return tr


def vert_islands(me):
    adj = [[] for _ in me.vertices]
    for e in me.edges:
        a, b = e.vertices; adj[a].append(b); adj[b].append(a)
    lab = [-1] * len(me.vertices); k = 0
    for i in range(len(me.vertices)):
        if lab[i] >= 0:
            continue
        st = [i]; lab[i] = k
        while st:
            a = st.pop()
            for b in adj[a]:
                if lab[b] < 0:
                    lab[b] = k; st.append(b)
        k += 1
    return lab, k


def mat_name(me, p):
    if me.materials and me.materials[p.material_index]:
        return me.materials[p.material_index].name
    return None


def tiling(mats, vmin, vmax):
    for m in mats:
        if m is None or m.startswith(NONTILE):
            return False
        if (m == 'Decals' or m.startswith('Paneling')) and not (0.19 <= vmin and vmax <= 0.31):
            return False
    return True


def island_info(o, mode, arm_tree, stay_tree):
    me = o.data; mw = o.matrix_world
    W = [mw @ v.co for v in me.vertices]
    lab, k = vert_islands(me)
    verts = [[] for _ in range(k)]
    for i, l in enumerate(lab):
        verts[l].append(i)
    faces = [[] for _ in range(k)]
    for p in me.polygons:
        faces[lab[p.vertices[0]]].append(p.index)
    uv = me.uv_layers.active.data
    info = []
    for l in range(k):
        ps = [W[i] for i in verts[l]]
        ys = [p.y for p in ps]; xs = [p.x for p in ps]; zs = [p.z for p in ps]
        if mode == 'arm':
            arm = True
        elif mode == 'fa':
            fa = sum(1 for p in ps if arm_tree.find_nearest(p)[3] < stay_tree.find_nearest(p)[3]) / len(ps)
            arm = fa > 0.6
        else:
            da = statistics.median(arm_tree.find_nearest(p)[3] for p in ps)
            ds = statistics.median(stay_tree.find_nearest(p)[3] for p in ps)
            arm = da < ds
        mats = set(mat_name(me, me.polygons[f]) for f in faces[l])
        vs = [uv[li].uv.y for f in faces[l] for li in me.polygons[f].loop_indices]
        info.append(dict(verts=verts[l], faces=faces[l], arm=arm, y0=min(ys), y1=max(ys),
                         x0=min(xs), x1=max(xs), z0=min(zs), z1=max(zs),
                         yc=sum(ys) / len(ys), mats=mats,
                         tile=tiling(mats, min(vs) if vs else 0, max(vs) if vs else 0)))
    return info


def pkey(co):
    return (round(co.x, 4), round(co.y, 4), round(co.z, 4))


def nkey(n):
    return (round(n.x, 2), round(n.y, 2), round(n.z, 2))


def band_split(o, isl, b, w):
    """Rebuild a 4-vertex strip quad as three quads with a thin band [b-w, b]."""
    me = o.data; mw = o.matrix_world; imw = mw.inverted()
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    uvl = bm.loops.layers.uv.active
    vids = isl['verts']
    BV = {i: bm.verts[i] for i in vids}
    OF = [bm.faces[fi] for fi in isl['faces']]
    uvof = {}
    for i in vids:
        for lp in bm.verts[i].link_loops:
            uvof[i] = lp[uvl].uv.copy()
    mat = bm.faces[isl['faces'][0]].material_index
    smooth = bm.faces[isl['faces'][0]].smooth
    n0 = bm.faces[isl['faces'][0]].normal.copy()
    Wv = {i: mw @ bm.verts[i].co for i in vids}
    s = sorted(vids, key=lambda i: Wv[i].y)
    lo, hi = s[:2], s[2:]
    def xz(i): return Vector((Wv[i].x, Wv[i].z))
    pairs = [(lo[0], min(hi, key=lambda h: (xz(h) - xz(lo[0])).length))]
    pairs.append((lo[1], [h for h in hi if h != pairs[0][1]][0]))
    sides = []
    for a, c in pairs:
        pa, pc = Wv[a], Wv[c]; ua, uc = uvof[a], uvof[c]
        pts = []
        for yy in (b - w, b):
            t = (yy - pa.y) / (pc.y - pa.y)
            pts.append((pa.lerp(pc, t), ua.lerp(uc, t)))
        sides.append((a, pts, c))
    for f in OF:
        bm.faces.remove(f)
    new = []
    for a, pts, c in sides:
        vs = [BV[a]]
        for p, _ in pts:
            vs.append(bm.verts.new(imw @ p))
        vs.append(BV[c])
        uvs = [uvof[a]] + [u for _, u in pts] + [uvof[c]]
        new.append((vs, uvs))
    (A, UA), (B, UB) = new
    # keep the original winding: compare with the first original face's normal later
    for k in range(3):
        quad = [(A[k], UA[k]), (A[k + 1], UA[k + 1]), (B[k + 1], UB[k + 1]), (B[k], UB[k])]
        for tri in ([quad[0], quad[1], quad[2]], [quad[0], quad[2], quad[3]]):
            f = bm.faces.new([t[0] for t in tri])
            f.material_index = mat; f.smooth = smooth
            for lp, t in zip(f.loops, tri):
                lp[uvl].uv = t[1]
            f.normal_update()
            if f.normal.dot(n0) < 0:
                f.normal_flip()
    bm.normal_update()
    bm.to_mesh(me); bm.free(); me.update()


def stretch(o, cut, lift, mode='arm', arm_tree=None, stay_tree=None, band_w=0.03, zone=(0.15, 0.85),
            sgn=-1, pick=None):
    """sgn=-1 moves world y < cut by -lift (the first build); sgn=+1 moves y > cut by +lift.
    pick(island) -> bool limits the move to the islands it accepts."""
    me = o.data; mw = o.matrix_world; imw = mw.inverted()
    rep = dict(obj=o.name, band=[], whole=[], uvisl=0, spread=[])
    side = (lambda y: y < cut) if sgn < 0 else (lambda y: y > cut)
    _info = globals()['island_info']
    def island_info(o, mode, arm_tree, stay_tree):
        inf = _info(o, mode, arm_tree, stay_tree)
        if pick:
            for isl in inf:
                isl['arm'] = isl['arm'] and pick(isl)
        return inf
    # 1. record corner normals (object space), keyed by position + face normal
    rec = {}; facen = {}
    cn = me.corner_normals
    for p in me.polygons:
        for li in p.loop_indices:
            rec[(pkey(me.vertices[me.loops[li].vertex_index].co), nkey(p.normal))] = cn[li].vector.copy()
    info = island_info(o, mode, arm_tree, stay_tree)
    # 2. band splits on non-tiling long single quads crossing the cut
    bands = []
    for isl in info:
        if isl['arm'] and isl['y0'] < cut < isl['y1'] and not isl['tile'] \
                and len(isl['verts']) == 4 and isl['y1'] - isl['y0'] > 0.5:
            b = min(max((isl['y0'] + isl['y1']) / 2, zone[0] + band_w), zone[1])
            bands.append((round(isl['y0'], 4), round(isl['y1'], 4), b, isl['yc']))
    for y0, y1, b, yc in bands:
        cur = island_info(o, mode, arm_tree, stay_tree)
        isl = min(cur, key=lambda i: abs(i['y0'] - y0) + abs(i['y1'] - y1) + abs(i['yc'] - yc) + (0 if len(i['verts']) == 4 else 99))
        band_split(o, isl, b, band_w)
        rep['band'].append((y0, y1, round(b, 3)))
    info = island_info(o, mode, arm_tree, stay_tree)
    # 3. moving vertex set
    W = [mw @ v.co for v in me.vertices]
    M = set()
    for isl in info:
        if not isl['arm']:
            continue
        if isl['y0'] < cut < isl['y1'] and not isl['tile']:
            hit = [bb for y0, y1, bb, _ in bands if abs(isl['y0'] - y0) < 1e-3 and abs(isl['y1'] - y1) < 1e-3]
            if hit:
                M.update(i for i in isl['verts'] if (W[i].y < hit[0] - band_w / 2) == (sgn < 0))
            else:
                mv = side(isl['yc'])
                rep['whole'].append((round(isl['y0'], 3), round(isl['y1'], 3), 'move' if mv else 'stay', sorted(isl['mats'])))
                if mv:
                    M.update(isl['verts'])
        else:
            M.update(i for i in isl['verts'] if side(W[i].y))
    # 4. UV refit on tiling faces. Pure faces (all loops moved or none) form
    #    components joined by UV-matching edges; crossing faces join a moved and an
    #    unmoved component and fix their offset difference to -g*lift, where g is
    #    dUV/dy of the crossing faces. Offsets are solved over that graph.
    uvl = me.uv_layers.active.data
    tile_face = {}
    for isl in info:
        for f in isl['faces']:
            tile_face[f] = isl['tile'] and isl['arm']
    fstate = {}
    for p in me.polygons:
        if tile_face.get(p.index, False):
            inM = [v in M for v in p.vertices]
            fstate[p.index] = 'X' if any(inM) and not all(inM) else ('M' if all(inM) else 'U')
    adj = {f: [] for f in fstate}
    byedge = {}
    for p in me.polygons:
        if p.index not in fstate:
            continue
        li = list(p.loop_indices)
        for j in range(len(li)):
            a, b = li[j], li[(j + 1) % len(li)]
            va, vb = me.loops[a].vertex_index, me.loops[b].vertex_index
            ua, ub = uvl[a].uv, uvl[b].uv
            ka = (round(ua.x, 5), round(ua.y, 5)); kb = (round(ub.x, 5), round(ub.y, 5))
            key = (va, ka, vb, kb) if va < vb else (vb, kb, va, ka)
            if key in byedge:
                q = byedge[key]; adj[p.index].append(q); adj[q].append(p.index)
            else:
                byedge[key] = p.index
    par = {f: f for f in fstate}
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for f, nb in adj.items():
        for q in nb:
            if (fstate[f] == 'X') == (fstate[q] == 'X') and (fstate[f] == 'X' or fstate[f] == fstate[q]):
                ra, rb = find(f), find(q)
                if ra != rb:
                    par[ra] = rb
    ydir = Vector((0, 1, 0))
    def grad(p):
        vs = list(p.vertices); li = list(p.loop_indices)
        P = [W[v] for v in vs]; U = [uvl[x].uv.copy() for x in li]
        e1 = P[1] - P[0]; e2 = P[2] - P[0]
        a11 = e1.dot(e1); a12 = e1.dot(e2); a22 = e2.dot(e2)
        r1 = ydir.dot(e1); r2 = ydir.dot(e2)
        det = a11 * a22 - a12 * a12
        if abs(det) < 1e-12:
            return None
        al = (r1 * a22 - r2 * a12) / det; be = (a11 * r2 - a12 * r1) / det
        return (U[1] - U[0]) * al + (U[2] - U[0]) * be
    def wmed(vals):
        vals = sorted(vals); tot = sum(a for _, a in vals); acc = 0
        for v, a in vals:
            acc += a
            if acc >= tot / 2:
                return v
        return vals[-1][0]
    clusters = {}
    for f, s in fstate.items():
        if s == 'X':
            clusters.setdefault(find(f), []).append(f)
    links = {}
    cl_d = {}; cl_m = {}; cl_u = {}
    for c, fs in clusters.items():
        ga = [(grad(me.polygons[f]), me.polygons[f].area) for f in fs]
        ga = [(g, a) for g, a in ga if g is not None]
        if not ga:
            continue
        gu = wmed([(g.x, a) for g, a in ga]); gv = wmed([(g.y, a) for g, a in ga])
        sp = max(max(abs(g.x - gu), abs(g.y - gv)) for g, _ in ga)
        if sp > 2e-3:
            rep['spread'].append((round(gu, 4), round(gv, 4), round(sp, 4), len(ga)))
        dlt = Vector((sgn * gu * lift, sgn * gv * lift))
        cl_d[c] = dlt
        ms = set(); us = set()
        for f in fs:
            for q in adj[f]:
                if fstate[q] == 'M': ms.add(find(q))
                elif fstate[q] == 'U': us.add(find(q))
        cl_m[c] = ms; cl_u[c] = us
        for m in ms:
            for u in us:
                links.setdefault(u, []).append((m, dlt))
                links.setdefault(m, []).append((u, -dlt))
        rep['uvisl'] += 1
    off = {}
    conflict = 0.0
    comps = sorted(set(find(f) for f, s in fstate.items() if s != 'X'),
                   key=lambda r: (fstate[r] != 'U', 0))
    for r0 in comps:
        if r0 in off:
            continue
        off[r0] = Vector((0, 0)); st = [r0]
        while st:
            a = st.pop()
            for b, dlt in links.get(a, []):
                want = off[a] + dlt
                if b in off:
                    conflict = max(conflict, (off[b] - want).length)
                else:
                    off[b] = want; st.append(b)
    rep['uv_conflict'] = round(conflict, 4)
    rep['uv_shifted_comps'] = sum(1 for v in off.values() if v.length > 1e-6)
    newuv = {}
    for f, s in fstate.items():
        p = me.polygons[f]
        if s == 'X':
            c = find(f)
            if c not in cl_d:
                continue
            if cl_u[c]:
                ou = off[next(iter(cl_u[c]))]
            elif cl_m[c]:
                ou = off[next(iter(cl_m[c]))] - cl_d[c]
            else:
                ou = Vector((0, 0))
            om = ou + cl_d[c]
            for x in p.loop_indices:
                newuv[x] = uvl[x].uv + (om if me.loops[x].vertex_index in M else ou)
        else:
            o2 = off.get(find(f))
            if o2 is not None and o2.length > 1e-9:
                for x in p.loop_indices:
                    newuv[x] = uvl[x].uv + o2
    for x, u in newuv.items():
        uvl[x].uv = u
    # 5. desired normals per loop (looked up before the move), then move, then set
    want = []
    for p in me.polygons:
        for li in p.loop_indices:
            k = (pkey(me.vertices[me.loops[li].vertex_index].co), nkey(p.normal))
            want.append(rec.get(k, p.normal.copy()))
    rep['normals_missing'] = sum(1 for p in me.polygons for li in p.loop_indices
                                 if (pkey(me.vertices[me.loops[li].vertex_index].co), nkey(p.normal)) not in rec)
    d = imw.to_3x3() @ Vector((0, sgn * lift, 0))
    for i in M:
        me.vertices[i].co += d
    me.normals_split_custom_set([tuple(v) for v in want])
    me.update()
    rep['moved'] = len(M)
    return rep
