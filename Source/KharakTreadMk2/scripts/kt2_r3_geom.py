"""Kharak Tread Mk II round 3, the small link's outlines: plain Python, shared by kt2_v3_reading.py and kt2_r3.py.

Owner's markup, 2026-11-24 (Source/KharakTread/reference/kharak_tread_v3_mockup_owner_2026-11-24.webp): "green lines
are the pads, red is the plate, blue is the hinge rod that connects them". It is AI concept art ("the dimensions are
not perfect, it is a concept"), so these rules and round 2's sizes win over its pixels:
- "I want to keep the visual trick with the tongue attached to the next tread, but it will just be the backplate
  instead of backplate and rubber".
- "I want the rubber pads to be equal in width", "the gap between the pads should be equal all the way across too".
- "the ends of the plate are beveled all the way around with some detail lines". To the first build: "the end caps
  need to be better integrated into the plate, they have extra chamfers around the wider base that shouldn't be
  there", so the ends are part of the plate and only their own edges are beveled. Then: "it should be beveled on
  all 4 sides so the end cap is a truncated prism".
- To the reading, "looking good, the forward pad is missing the shoulders": the front pad rises up the tongue's
  sides at each end of its middle run, as drawn. Owner pick, 2026-11-24: "Seam back, shoulders end on it" (they
  first pushed the seam 6 cm forward: "I think you moved the dotted orange line too far forward").
- The seam is a cut with round 2's knuckle on the slice. The first build curved the seam round the hinge axis, which
  put the round on the plate; owner: "you had this perfect on the prior design. You are overthinking it now with
  these perfectly grooved cutouts. Its just supposed to extend into the tread behind to hide gap when its around a
  wheel". A straight seam at the shoulder tops left the slice dipping 1.4 cm below the plate on a 3x3; owner: "you
  could make the tongue slice larger so it takes more parts of the trailing tread to help improve the bend seam". So
  the slice took the bare strip in front of the front pad. Then: "make the seam here all the way across, straight
  line, its fine if the rubber part of the tread looks like it is lifting off a little on a really tight bend". So
  the seam runs straight across along the pad's middle front edge, 0.85 cm ahead of the hinge, and the shoulders'
  5 cm rise sits over the slice.
Link frame as kt2_build.py: X across, Y along (+Y toward the tongue's tip), Z out, meters, origin at the plate's
underside center. Outlines are counterclockwise seen from +Z.
"""
import math

R2 = math.sqrt(2)
# Which link: "small" (1x1 to 3x3) or "5x5", set by the caller's namespace. The 5x5 link is the small one with every
# outline scaled to the 5x5 rubber's 5.96 m width and its thickness doubled, as round 2's 5x5 (Docs/design/gvk-treads.md,
# "Mk II round 3: the 5x5 link"; owner, 2026-11-24: "Yes, build it")
LINK = globals().get("LINK", "small")
SX = 5.96 / 2.80 if LINK == "5x5" else 1.0       # outlines: width, length, gaps
SZ = 2.0 if LINK == "5x5" else 1.0               # thickness, and the chamfers with it
# Which level of detail, set by the caller like LINK (Docs/design/gvk-treads.md, "Mk II finish"; owner, 2026-11-24:
# "lod 1 drops all chamfers but keeps decals, lod 2 drops decals, and so on"). Per level: name tag, rod sides, knuckle
# arc steps. The construction model ("con") is the metal link without pads or decals, with its own two LODs.
LEVEL = globals().get("LEVEL", "main")
LEVELS = {"main": ("", 16, 8), "lod1": ("L1", 8, 4), "lod2": ("L2", 6, 2), "lod3": ("L3", 6, 2),
          "con": ("C", 16, 8), "con1": ("C1", 8, 4), "con2": ("C2", 6, 2)}
TAG, ROD_N, KNUCKLE_N = LEVELS[LEVEL]
CHAMFERS = LEVEL in ("main", "con")              # metal and rubber chamfers
DECALS = LEVEL in ("main", "lod1")               # the seam and the 5x5's decals
PADS = not LEVEL.startswith("con")
NOTCH = LEVEL != "lod3"                          # the rod and the notch it shows through
P = ("R5" if LINK == "5x5" else "R3") + TAG + "_"   # object names
HALF_W, HALF_L, PITCH = 1.40 * SX, 0.34 * SX, 0.736 * SX
HINGE_Y = PITCH / 2
PLATE_T, PAD_T = 0.14 * SZ, 0.10 * SZ
# hinge height in the link frame, as round 2 (0.110 on the 1x1 to 0.116 on the 3x3); on the 5x5 the Kharak rule,
# outer face on the 5x5's collision sphere (5.8 m, reported radius 5.478 m): -(5.8 - 0.48 - hull radius)
KNUCKLE_H = 0.2138 if LINK == "5x5" else 0.113
TIP_Y = 0.5925 * SX             # tongue front, as round 2 (markup: 0.595)
TIP_HALF = 0.513 * SX           # markup: 1.03 m across the tongue's front
NOTCH_GAP = 0.04 * SX
END_W = 0.09 * SX               # each end of the plate: its corners are cut back over this width (markup: 9 cm)
END_CUT = 0.05 * SX             # each end is a truncated prism over END_W: its front and back taper in by this
END_BEVEL = 0.02 * SZ           # and its top and bottom by this (owner, 2026-11-24: "it should be beveled on all 4
                                # sides so the end cap is a truncated prism"; markup: 5.7 cm)
G = 0.05 * SX                   # one gap: between the pads, to the back edge, the end bands and the notch
W = 0.19 * SX                   # each pad's width (markup: 2W + G = 0.43 m at the sides and in the middle)
SH_RISE, SH_LEN = G, 0.24 * SX  # the front pad's shoulders: rise to the seam (markup: 6 cm), 24 cm long
# the 5x5's reach twice that, further over the tongue (owner, 2026-11-24: "increase the size of forward rubber tread's
# shoulders so they extend further over the tongue", picked "Double" and "5x5 only"); the rod and its notch stay put
SH_REACH = 2 * SH_RISE if LINK == "5x5" else SH_RISE
BAR_R = 0.045 * SX
BAR_Z = PLATE_T / 2
HORN_Y = 0.07 * SX              # the guide horn's shift forward: its back 4 cm in front of the notch's open gap
HORN_S = SX                     # the Kharak Tread's horn, scaled as its 5x5 style does
CHAMFER = 0.01 * SZ             # the metal's chamfer (kt2_r3_detail.py)
RUBBER_BEVEL = 0.03 * SZ        # the rubber's chamfer
END_X = HALF_W - END_W          # where each end cap starts

TONGUE_C = TIP_Y + TIP_HALF     # the tongue's 45 degree sides: |x| = TONGUE_C - y


def tongue_half(y):
    return TONGUE_C - y


def notch_half(y):
    """The notch round the tongue of the link behind, one NOTCH_GAP all round."""
    return tongue_half(y + PITCH) + NOTCH_GAP * R2


NOTCH_FRONT = TIP_Y - PITCH + NOTCH_GAP

# The gap between the pads is a chevron: a side run at Y_SIDE, 45 degree shoulders, a middle run at Y_MID. Its center
# line is offset by D to each pad's outer edge. The front pad's outer shoulder lies on the tongue's side line, as
# drawn; the rear pad sits one G in from the back edge and one G in front of the notch.
D = G / 2 + W
Y_SIDE = -HALF_L + G + D
Y_MID = NOTCH_FRONT + G + D
C_DIAG = TONGUE_C - D * R2      # the center line's shoulder: y = C_DIAG - |x|
PAD_END = HALF_W - END_W - G
SEAM_Y = Y_MID + D              # the seam, straight across the tongue along the front pad's middle front edge
Y_SH0 = Y_MID + D + SH_RISE     # the shoulders' first top line: the rod and its notch are placed from it
Y_SH = Y_MID + D + SH_REACH     # top of the front pad's shoulders, over the slice
BAR_Y = (Y_SH0 + TIP_Y) / 2     # the rod, 0.51 m from center
# A notch cut into the slice's front, through its full thickness, so the rod shows in the middle (owner, 2026-11-24:
# "cutting a notch out of the front of the tongue so you can see the metal connecting rod in the center"): 0.56 m
# across, read off the owner's sketch, back to where the front pad's shoulders start
NOTCH_HALF = 0.28 * SX
NOTCH_BACK = Y_SH0
KNUCKLE_TOP = PLATE_T - 0.004 * SZ   # 4 mm under the plate top, so the knuckle stays hidden when straight (round 2)


def knee(y_run, d):
    """X (left side, negative) where a run at y_run, offset by d, meets the shoulder offset by d."""
    return -(C_DIAG + d * R2 - (y_run + d))


def mirrored(left):
    """A left half from the left end to the center line, closed with its mirror image."""
    return left + [(-x, y) for x, y in reversed(left)]


def ccw(pts):
    area = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else list(reversed(pts))


def pad_edge(d):
    return [(-PAD_END, Y_SIDE + d), (knee(Y_SIDE, d), Y_SIDE + d), (knee(Y_MID, d), Y_MID + d)]


def front_pad_top():
    """The front pad's outer edge, left half, from its end to the center line, with the shoulder."""
    x_out = -tongue_half(Y_SH)
    x_in = x_out + SH_LEN
    return [(-PAD_END, Y_SIDE + D), (knee(Y_SIDE, D), Y_SIDE + D), (x_out, Y_SH), (x_in, Y_SH),
            (x_in + SH_REACH, Y_MID + D)]


def seam_line():
    """The tongue's seam: straight across, side to side."""
    return [(-tongue_half(SEAM_Y), SEAM_Y), (tongue_half(SEAM_Y), SEAM_Y)]


def band(low, top):
    """A pad from its lower and upper edges (left halves, end to center line)."""
    return ccw(mirrored(low) + [(-x, y) for x, y in top] + list(reversed(top)))


def front_pad():
    return band(pad_edge(G / 2), front_pad_top())


def rear_pad():
    return band(pad_edge(-D), pad_edge(-G / 2))


def plate(seam=False):
    """The plate in one piece: its tongue (whole, or cut at the seam), the notch, and the ends with their corners
    cut back (owner, 2026-11-24: "the end caps need to be better integrated into the plate")."""
    x0 = HALF_W - END_W
    cut = NOTCH_GAP * (R2 - 1)
    if seam:
        # straight across the front edge: the strip of tongue up to the seam stuck out on a wheel, so the rubber
        # tongue and shoulders overhang there and the slice's knuckle fills the gap (owner, 2026-11-24: "The metal
        # plate should just go straight across and leave the rubber tread tongue and shoulders as overhang")
        top = [(-x0, HALF_L), (x0, HALF_L)]
    else:
        top = ([(-x0, HALF_L), (-tongue_half(HALF_L), HALF_L), (-TIP_HALF, TIP_Y), (TIP_HALF, TIP_Y),
                (tongue_half(HALF_L), HALF_L), (x0, HALF_L)])
    end = [(HALF_W, HALF_L - END_CUT), (HALF_W, -HALF_L + END_CUT)]
    notch = [(notch_half(-HALF_L), -HALF_L), (TIP_HALF + cut, NOTCH_FRONT), (-TIP_HALF - cut, NOTCH_FRONT),
             (-notch_half(-HALF_L), -HALF_L)]
    return ccw(top + end + [(x0, -HALF_L)] + notch + [(-x0, -HALF_L)] + [(-x, y) for x, y in reversed(end)])


def tip_piece():
    """The slice: the tongue's front piece from the seam to the tip, moved back one pitch into this link's notch."""
    return ccw([(x, y - PITCH) for x, y in seam_line()] + [(TIP_HALF, TIP_Y - PITCH), (-TIP_HALF, TIP_Y - PITCH)])


# Its arc: 0.105 m radius, turning 80 degrees from the slice's top, so it ends 9.5 cm behind the hinge and 5.3 cm up
# (owner, 2026-11-24, drawing over a bent joint in game: "adjust the knuckle so the radius is a little tighter and
# extends further back", which gave 0.12 m ending 8 cm behind, 10 cm up; then "tighter and angles even further into
# the back tread"; it was 0.20 m ending 5.3 cm behind, 13 cm up)
KNUCKLE_R = 0.105 * SZ                 # a round arc, so it scales with the thickness only
KNUCKLE_SWEEP = math.radians(80)
KNUCKLE_BOT = 0.0                      # flush with the underside (owner: "a similar step ... on the bottom side")
KNUCKLE_FRONT = SEAM_Y + 0.01 * SX     # it reaches 1 cm into the slice


def knuckle_yz(n=None, whole=False):  # 8 arc steps of 10 degrees on the main model (16 before; owner picked fewer)
    """The slice's knuckle, (y, z) in this link's frame (the slice sits in its notch): one profile straight across
    the tongue. Owner, 2026-11-24, of round 2's knuckle: "the curve is hidden when the track is straight, and hides
    the split/gap when it is wrapped around a wheel"; then, drawing on the joint section: "make the tongue slice
    knuckle straight across at the center of hinge point, and add a more gradual curve that intersects with the
    trailing plate, see green lines on my mockup" (review/seam_markup_owner_2026-11-24.png).
    Its top is an arc tangent to the slice's top at the seam, curving down behind the hinge; its back is a straight
    line from the arc's end down to the plate's underside, under the front edge of the plate behind.
    Straight, it is hidden in the plate and front pad behind; bent, it fills the split, and the part behind the hinge
    rises into that pad."""
    n = n or KNUCKLE_N
    r = KNUCKLE_R
    cz = PLATE_T - r
    a1 = math.pi / 2 + KNUCKLE_SWEEP
    arc = [(SEAM_Y + r * math.cos(math.pi / 2 + (a1 - math.pi / 2) * k / n),
            cz + r * math.sin(math.pi / 2 + (a1 - math.pi / 2) * k / n)) for k in range(n + 1)]
    yf = KNUCKLE_FRONT
    # its bottom reaches back to the plate's front edge, closing the gap under the hinge (owner, 2026-11-24: "need
    # to extend the bottom of the knuckle to close that gap"); bent, that corner turns up into the plate behind
    # whole: the slice and its knuckle as one profile, from the tongue's tip back (its top runs into the arc)
    # whole: its top also breaks at Y_SH, where the front pad's shoulders start to overhang it, so its side chamfers
    # can end there (owner, 2026-11-24: "chamfer on the top side needs to end where it overlaps with the rubber
    # tread")
    front = ([(TIP_Y, KNUCKLE_BOT), (TIP_Y, PLATE_T), (Y_SH, PLATE_T)] if whole
             else [(yf, KNUCKLE_BOT), (yf, KNUCKLE_TOP), (SEAM_Y, KNUCKLE_TOP)])
    # the bottom 1 cm under the plate's front chamfer as well ("pull the bottom just a tiny bit further")
    pts = front + arc + [(HALF_L - CHAMFER, KNUCKLE_BOT)]
    return [(y - PITCH, z) for y, z in pts]


def gap_floor(e=0.005):
    """The gap in front of the tip piece in this link's notch, reaching e into the walls round it."""
    tb, g = TIP_Y - PITCH, NOTCH_GAP
    side, front = TIP_HALF + g * R2 + e, TIP_HALF + g * (R2 - 1) + e
    return ccw([(-side, tb - e), (side, tb - e), (front, tb + g + e), (-front, tb + g + e)])


def bar_half(y):
    """Half length of the rod at y in this link's notch: 4 cm into the plate past the notch's side walls."""
    return notch_half(y - BAR_R) + 0.04 * SX


def summary():
    return (f"Y_SIDE {Y_SIDE:.4f} Y_MID {Y_MID:.4f} Y_SH {Y_SH:.4f} SEAM {SEAM_Y:.4f} "
            f"BAR {BAR_Y:.4f} knees {knee(Y_SIDE, 0):.4f} {knee(Y_MID, 0):.4f} front top {Y_MID + D:.4f} "
            f"front side top {Y_SIDE + D:.4f} rear bottom {Y_SIDE - D:.4f} rear mid bottom {Y_MID - D:.4f} "
            f"shoulder x {-tongue_half(Y_SH):.4f}..{-tongue_half(Y_SH) + SH_LEN:.4f}")
