"""Kharak Tread Mk II review boards: two tongues side by side, from the renders kt2_review.py writes.

    uv run -q --no-project --with pillow python -I kt2_boards.py [AB|BC|CD|C|5x5|5x5cut|5x5even|hinge|r3]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REN = ROOT / "review" / "renders"
OUT = ROOT / "review"
MOCKUP = ROOT.parent / "KharakTread" / "reference" / "kharak_tread_v2_mockup_owner_2026-11-23.png"
CELL_W = 900
GAP = 16
NAMES = {"A": "Tongue A: rubber over the plate", "B": "Tongue B: notch, 4 cm gap",
         "C": "Tongue C: knuckle round the hinge (0.127 m)", "D": "Tongue D: 0.9 m back curve"}


def font(size):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def on_white(im):
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg.convert("RGB")


def overlay(variant):
    """The owner's mockup with the model's top-view edges drawn over it in red."""
    mock = on_white(Image.open(MOCKUP))
    ren = Image.open(REN / f"top_{variant}.png")
    assert ren.size == mock.size, (ren.size, mock.size)
    edges = on_white(ren).convert("L").filter(ImageFilter.FIND_EDGES)
    alpha = ren.getchannel("A").filter(ImageFilter.FIND_EDGES)
    mask = Image.eval(Image.eval(edges, lambda v: 255 if v > 25 else 0), lambda v: v)
    mask.paste(255, mask=Image.eval(alpha, lambda v: 255 if v > 60 else 0))
    mask = mask.filter(ImageFilter.MaxFilter(3))
    out = mock.copy()
    out.paste((225, 20, 20), mask=mask)
    return out


def cell(im, label):
    im = im.convert("RGB")
    h = round(im.height * CELL_W / im.width)
    im = im.resize((CELL_W, h), Image.LANCZOS)
    c = Image.new("RGB", (CELL_W, h + 40), (32, 34, 38))
    c.paste(im, (0, 40))
    ImageDraw.Draw(c).text((10, 5), label, fill=(235, 235, 235), font=font(22))
    return c


def board(name, title, rows, note):
    rows = [[cell(im, lab) for im, lab in row] for row in rows]
    width = GAP + 2 * (CELL_W + GAP)
    head = 64
    foot = 24 + 30 * len(note)
    height = head + sum(max(c.height for c in row) + GAP for row in rows) + foot
    b = Image.new("RGB", (width, height), (20, 21, 24))
    d = ImageDraw.Draw(b)
    d.text((GAP, 14), title, fill=(255, 255, 255), font=font(30))
    y = head
    for row in rows:
        for i, c in enumerate(row):
            b.paste(c, (GAP + i * (CELL_W + GAP), y))
        y += max(c.height for c in row) + GAP
    for k, line in enumerate(note):
        d.text((GAP, y + 6 + 30 * k), line, fill=(215, 215, 215), font=font(21))
    b.save(OUT / f"{name}.png", optimize=True)
    print(OUT / f"{name}.png", b.size)


def img(n):
    return Image.open(REN / f"{n}.png")


NOTES = {
    "top": {
        "A": "Tongue A: the plate is a plain rectangle; the arrowhead's front 0.25 m is rubber only and lies on the "
             "plate of the link ahead, with the cut-out drawn in front of the tip.",
        "B": "Tongue B: the plate runs under the arrowhead; the link ahead has a notch 4 cm wider all round, which "
             "leaves a 3.9 cm strip of plate between the notch and the arrowhead's back edge.",
        "C": "Tongue C: B's shapes, cut at the hinge line. The tongue's front piece belongs to the link ahead and "
             "turns with it; its knuckle stays hidden inside the arrowhead behind while the run is straight.",
        "D": "Tongue D: C with a back curve of 0.9 m radius, starting flush with the outer face at the hinge line; "
             "hidden inside the arrowhead behind while the run is straight.",
    },
    "3x3": {
        "A": "Tongue A: on every joint the tip stands 5.0 cm off the next plate.",
        "B": "Tongue B: the tip rises 5.3 cm in its notch, so it stands about 5 cm proud of the next plate.",
        "C": "Tongue C: nothing lifts. The knuckle fills the cut's 2.8 cm opening at the outer face; under the "
             "hinge the cut's bottom corner runs 2.6 cm into the piece ahead.",
        "D": "Tongue D: the back curve stands up to 1.6 cm above the outer face of the link behind.",
        "all": "On the curve the plate underside sits 2.6 cm inside the drawn tire. That comes from Tank Tracks' "
               "layout, not from the tongue.",
    },
    "1x1": {
        "A": "Tongue A: on every joint the tip stands 14.9 cm off the next plate.",
        "B": "Tongue B: the tip rises 18.9 cm, clear of its notch, which shows empty under it.",
        "C": "Tongue C: nothing lifts. The knuckle fills the cut's 9.2 cm opening at the outer face; under the "
             "hinge the cut's bottom corner runs 7.7 cm into the piece ahead.",
        "D": "Tongue D: the back curve stands up to 19 cm above the outer face of the link behind, like a blade.",
        "all": "Every tongue: the plates' inner corners run 2.8 cm into each other, and the plate underside sits "
               "4.6 cm inside the drawn tire.",
    },
}


def picked(v="C"):
    """One board of the picked tongue: the top view over the mockup, straight, and a joint on each wheel."""
    board(f"board_{v}", f"Kharak Tread Mk II blockout: tongue {v} with its knuckle, 3 cm slots",
          [[(overlay(v), "Red = model edges over your mockup"), (img(f"straight_{v}"), "Three links, straight")],
           [(img(f"3x3_close_{v}"), "3x3 track wheel: joint on the front"),
            (img(f"1x1_close_{v}"), "1x1 track wheel: joint on the front")]],
          ["The slots between the upper bars and the arrowhead's shoulders are 3 cm across (1.6 cm in the "
           "mockup).", NOTES["1x1"][v]])


FIVE = {"S1": "S1: the small link scaled 2.13x", "S2": "S2: S1 with a wider arrowhead",
        "S3": "S3: wider arrowhead, three bars a side"}


def five():
    """The 5x5 link's options (kt2_5x5.py renders): top and straight, then on the 5x5 track wheel."""
    board("board_5x5_top", "Kharak Tread Mk II, 5x5 link: top view and three links straight",
          [[(img(f"5x5_top_{v}"), f"{FIVE[v]}: top view"), (img(f"5x5_straight_{v}"), f"{v}: three links")]
           for v in FIVE],
          ["Every option: the small link scaled 2.13x, 5.96 m wide with a 1.57 m pitch; 0.48 m thick, 0.20 m pads on "
           "a 0.28 m plate; tongue C with its knuckle, 6.4 cm slots, the Kharak 5x5 horn underneath.",
           "S2 and S3: the arrowhead's tip is 2.10 m across instead of 1.57 m, and the bars are 0.27 m shorter.",
           "S3: three bars a side, 0.21 m wide with 10 cm gaps, where S1 and S2 have two, 0.32 and 0.37 m wide with a "
           "15 cm gap."])
    board("board_5x5_wheel", "Kharak Tread Mk II, 5x5 link: round the 5x5 track wheel",
          [[(img("5x5_close_S1"), FIVE["S1"]), (img("5x5_close_S2"), FIVE["S2"])],
           [(img("5x5_close_S3"), FIVE["S3"]), (img("5x5_run_S1"), "Side view (the same for all three)")]],
          ["16.3 degrees per link, 22 links round the wheel (the Kharak Tread's 5x5 has 21).",
           "At each joint the cut opens 7.5 cm at the outer face, which the knuckle fills; its bottom corner runs "
           "6.0 cm into the piece ahead. Mid-link the plate underside sits 2.4 cm inside the drawn tire.",
           "A mixed track takes the 5x5 style onto its smaller wheels too: 27 degrees per link on a 3x3, 41 on a 2x2 "
           "and 82 on a 1x1. The knuckle's 46 covers all but the 1x1."])


def five_cut():
    """S2 against S2X, the same link with the side slots cut across the arrowhead."""
    labels = {"S2": "S2 as picked", "S2X": "S2X: slots cut across, two lugs"}
    board("board_5x5_cut", "Kharak Tread Mk II, 5x5 link: S2 and S2 cut into two lugs",
          [[(img(f"5x5_{view}_{v}"), f"{labels[v]}: {what}") for v in labels]
           for view, what in (("top", "top view"), ("straight", "three links"), ("close", "on the 5x5 wheel"))],
          ["S2X: each side slot runs on up 0.15 m further, then turns across the arrowhead at the slots' width "
           "(6.4 cm) to meet the other side's.",
           "That splits the rubber into two lugs: the front one is the tip with the upper bars, the rear one the "
           "arrowhead's core with the lower bars.",
           "The cut's top edge is 0.41 m ahead of the plate center, 0.37 m behind the hinge line."])


def five_even():
    """S2X with corner lugs and one gap everywhere: 6.4 cm (G6) against 12.8 cm (G13)."""
    labels = {"G6": "G6: every gap 6.4 cm", "G13": "G13: every gap 12.8 cm"}
    board("board_5x5_even", "Kharak Tread Mk II, 5x5 link: corner lugs and one gap everywhere",
          [[(on_white(img(f"5x5_{view}_{v}")), f"{labels[v]}: {what}") for v in labels]
           for view, what in (("top", "top view"), ("straight", "three links"), ("close", "on the 5x5 wheel"))],
          ["Both: S2X with a trapezoid lug in each front corner, in front of the upper bar. One gap everywhere: "
           "between every two lugs, across the slot and the cut, and from each lug to the plate's edges.",
           "The tongue keeps its 8.5 cm gap; the rear lug stands one gap off the notch round it. The upper bar's top "
           "stays put, and the bars and arms keep their proportions.",
           "G6: the slot's width (6.4 cm). The plate margins shrink from 12.8 cm and the bars grow.",
           "G13: the plate margin's width (12.8 cm). The slot and the cut double, and the corner lugs are 0.23 m "
           "deep against G6's 0.36 m."])


def hinge():
    """The hinge bar on both links: the small link's tongue C and the 5x5's S2X."""
    links = (("", "C", "Small link (tongue C)"), ("5x5_", "S2X", "5x5 link (S2X)"))
    views = (("top_{v}", "top view"), ("hinge_{v}_wide", "beside the tongue"), ("hinge_{v}", "down into the gap"))
    board("board_hinge", "Kharak Tread Mk II: hinge bar through the metal plate, under the tongue",
          [[(on_white(img(p + view.format(v=v))), f"{label}: {what}") for p, v, label in links]
           for view, what in views],
          ["The bar now runs through the metal plate under the tongue's front piece, centered in the plate's depth, "
           "halfway between the first try and the joint.",
           "It shows only where it crosses the gaps beside the tongue (4 cm; 8.5 cm on the 5x5). Both ends stay "
           "4 cm inside the plate beyond them, clear of the rubber.",
           "Small link: 9 cm across, 1.20 m long. 5x5: 19 cm across, 3.10 m long. Darker steel than the plate.",
           "A 2 cm floor at the plate's underside closes the gap in front of the tip, so the horn no longer shows "
           "there; the gap stays 12 cm deep (5x5: 4 cm floor, 24 cm deep)."])


def round3():
    """Round 3 small link (kt2_r3.py renders): two equal pads, plate-only tongue with its knuckle, beveled ends."""
    board("board_r3", "Kharak Tread Mk II round 3: two equal pads, plate-only tongue",
          [[(on_white(img("top_R3")), "Top view"), (img("straight_R3"), "Three links, straight")],
           [(img("3x3_close_R3"), "3x3 track wheel: joint on the front"),
            (img("1x1_close_R3"), "1x1 track wheel: joint on the front")],
           [(on_white(img("hinge_R3_wide")), "Beside the tongue"), (on_white(img("hinge_R3")), "The rod in the gap")]],
          ["Pads 19 cm wide with one 5 cm gap between them, to the back edge, the plate's ends and the notch. The front "
           "pad's shoulders run up the tongue's sides, over the front piece.",
           "The tongue is plate only, cut straight across at the front pad's middle front edge. One knuckle straight "
           "across curves gently down into the plate behind.",
           "The rod (9 cm) runs through the tongue's front piece and shows only in the gaps beside it. The ends are "
           "part of the plate, each a truncated prism: 5 cm in at the front and back, 2 cm at the top and bottom."])


def main(cols="BC"):
    if cols == "r3":
        return round3()
    if cols == "5x5":
        return five()
    if cols == "5x5cut":
        return five_cut()
    if cols == "hinge":
        return hinge()
    if cols == "5x5even":
        return five_even()
    if cols in NAMES:
        return picked(cols)
    sfx = "" if cols == "AB" else "_" + cols
    board(f"board_top{sfx}", "Kharak Tread Mk II blockout: top view and straight run",
          [[(overlay(v), f"{NAMES[v]}: red = model edges over your mockup") for v in cols],
           [(img(f"straight_{v}"), f"{NAMES[v]}: three links, straight") for v in cols]],
          [NOTES["top"][v] for v in cols])
    for wheel, deg in (("3x3", "12.9"), ("1x1", "44.6")):
        board(f"board_{wheel}{sfx}", f"Kharak Tread Mk II blockout: round the {wheel} track wheel "
              f"({deg} degrees per link, as Tank Tracks lays it out)",
              [[(img(f"{wheel}_close_{v}"), f"{NAMES[v]}: joint on the wheel's front") for v in cols],
               [(img(f"{wheel}_cut_{v}"), f"{v}: center-line cut (gray plate, black rubber, red tire surface)")
                for v in cols],
               [(img(f"{wheel}_run_{v}"), f"{NAMES[v]}: the run, side view") for v in cols]],
              [NOTES[wheel][v] for v in cols] + [NOTES[wheel]["all"]])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "BC")
