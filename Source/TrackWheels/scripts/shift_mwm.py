"""Copy an .mwm model with its whole mesh moved by a fixed offset (model axes, metres).

    python tools/Shift-MwmModel.py <source.mwm> <target.mwm> <dx> <dy> <dz> [--rename OLD=NEW ...]

Used for the Track Wheel 1x1 look on Keen's Wheel 1x1 (Docs/design/track-wheel-swap.md, "Wheel 1x1 rollers"):
Tank Tracks draws a swap model exactly where the block is, so a model that has to show somewhere else needs its
mesh moved inside the file. Moves the vertices (repacked the game's way, VRage.Import.PositionPacker), the
bounding box and sphere, the hit-test tree's bounds (ModelBvh, quantized against those bounds, so its nodes stay
exact) and any dummies. --rename rewrites the LOD file names a main model lists. Everything else is copied byte for
byte, including the collision, which a wheel swap never uses (Tank Tracks keeps the wheel's own collider).
"""
import math
import struct
import sys


def r7(b, p):
    v = s = 0
    while True:
        c = b[p]; p += 1; v |= (c & 0x7F) << s
        if c < 0x80:
            return v, p
        s += 7


def w7(n):
    out = bytearray()
    while True:
        c = n & 0x7F; n >>= 7
        out.append(c | (0x80 if n else 0))
        if not n:
            return bytes(out)


def rstr(b, p):
    n, p = r7(b, p)
    return b[p:p + n].decode("utf-8"), p + n


def wstr(s):
    e = s.encode("utf-8")
    return w7(len(e)) + e


def pack_pos(x, y, z):
    num = min(math.floor(max(abs(x), abs(y), abs(z))), 2048.0)
    inv = 1.0 / num if num > 0 else 1.0
    if num <= 0:
        num = 1.0
    return struct.pack("<4e", x * inv, y * inv, z * inv, num)


def shift_vertices(body, d):
    n = struct.unpack_from("<i", body, 0)[0]
    out = bytearray(body[:4])
    for i in range(n):
        x, y, z, w = struct.unpack_from("<4e", body, 4 + 8 * i)
        out += pack_pos(x * w + d[0], y * w + d[1], z * w + d[2])
    return bytes(out) + body[4 + 8 * n:]


def shift_floats(body, d, count):
    """count Vector3s at the start of body."""
    v = list(struct.unpack_from("<%df" % (3 * count), body, 0))
    for i in range(count):
        for a in range(3):
            v[3 * i + a] += d[a]
    return struct.pack("<%df" % (3 * count), *v) + body[12 * count:]


def shift_bvh(body, d):
    size = struct.unpack_from("<i", body, 0)[0]
    blob = bytearray(body[4:4 + size])
    v = list(struct.unpack_from("<6f", blob, 4))       # after m_num_nodes: global bound min, max
    for i in range(6):
        v[i] += d[i % 3]
    struct.pack_into("<6f", blob, 4, *v)
    return body[:4] + bytes(blob) + body[4 + size:]


def shift_dummies(body, d):
    n = struct.unpack_from("<i", body, 0)[0]
    p, out = 4, bytearray(body[:4])
    for _ in range(n):
        name, q = rstr(body, p)
        m = list(struct.unpack_from("<16f", body, q))
        m[12] += d[0]; m[13] += d[1]; m[14] += d[2]   # row-major XNA matrix: translation in M41-M43
        q += 64
        cnt = struct.unpack_from("<i", body, q)[0]; q += 4
        for _ in range(cnt):
            q = rstr(body, q)[1]
            q = rstr(body, q)[1]
        out += body[p:p + (len(wstr(name)))] + struct.pack("<16f", *m) + body[p + len(wstr(name)) + 64:q]
        p = q
    return bytes(out) + body[p:]


def rename_lods(body, renames):
    n = struct.unpack_from("<i", body, 0)[0]
    p, out = 4, bytearray(body[:4])
    for _ in range(n):
        out += body[p:p + 4]; p += 4                  # distance
        path, p = rstr(body, p)
        for old, new in renames:
            path = path.replace(old, new)
        out += wstr(path)
        q = rstr(body, p)[1]                          # render quality
        out += body[p:q]; p = q
    return bytes(out) + body[p:]


def main():
    args = sys.argv[1:]
    renames = []
    while "--rename" in args:
        i = args.index("--rename")
        old, new = args[i + 1].split("=", 1)
        renames.append((old, new))
        del args[i:i + 2]
    src, dst = args[0], args[1]
    d = tuple(float(a) for a in args[2:5])

    b = open(src, "rb").read()
    hdr, p = rstr(b, 0)
    nh = struct.unpack_from("<i", b, p)[0]; p += 4
    for _ in range(nh):
        p = rstr(b, p)[1]
    head = b[:p]
    n = struct.unpack_from("<i", b, p)[0]; p += 4
    index = []
    for _ in range(n):
        t, p = rstr(b, p)
        index.append((t, struct.unpack_from("<i", b, p)[0])); p += 4
    offs = [o for _, o in index] + [len(b)]
    if offs != sorted(offs) or offs[0] != p:
        sys.exit("unexpected tag layout in " + src)

    blobs = []
    for i, (t, o) in enumerate(index):
        name, q = rstr(b, o)
        if name != t:
            sys.exit("tag %s does not match its index entry %s" % (name, t))
        body = b[q:offs[i + 1]]
        if t == "Vertices":
            body = shift_vertices(body, d)
        elif t == "BoundingBox":
            body = shift_floats(body, d, 2)
        elif t == "BoundingSphere":
            body = shift_floats(body, d, 1)
        elif t == "ModelBvh":
            body = shift_bvh(body, d)
        elif t == "Dummies":
            body = shift_dummies(body, d)
        elif t == "LODs" and renames:
            body = rename_lods(body, renames)
        blobs.append(b[o:q] + body)

    out = bytearray(head) + struct.pack("<i", n)
    pos = len(head) + 4 + sum(len(wstr(t)) + 4 for t, _ in index)
    for (t, _), blob in zip(index, blobs):
        out += wstr(t) + struct.pack("<i", pos)
        pos += len(blob)
    for blob in blobs:
        out += blob
    open(dst, "wb").write(bytes(out))
    print("%s -> %s (%d bytes)" % (src, dst, len(out)))


if __name__ == "__main__":
    main()
