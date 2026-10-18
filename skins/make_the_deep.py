"""Generate a 64x64 Minecraft skin of The Deep (The Boys).

Classic (4px wide) arms. Run: python3 skins/make_the_deep.py
Writes skins/the_deep.png next to this script.
"""
from pathlib import Path

from PIL import Image

PALETTE = {
    # skin
    "S": "#e3b08e", "s": "#c99272", "k": "#efc6a6", "n": "#b47c60",
    # hair
    "H": "#6a4a2f", "h": "#4b3320", "L": "#8e6a46",
    # face
    "W": "#f4f4f4", "I": "#3c8fa8", "B": "#4b3320", "M": "#8e5650", "m": "#c4907a",
    # scaly suit
    "K": "#0a302d", "D": "#0e4540", "T": "#16625a", "Q": "#24806f", "q": "#3aa08a",
    # gold belt and emblem
    "G": "#d6a532", "g": "#9c7420", "Y": "#f3d370",
    # fins and emblem water
    "F": "#43bfae", "f": "#2c9586", "A": "#5fd3c4",
    # boot soles
    "Z": "#062220",
}

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))


def rgba(c):
    c = PALETTE[c].lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)


def faces(u, v, w, h, d):
    """Texture rects (x, y, width, height) of a box unwrapped at (u, v)."""
    return {
        "top": (u + d, v, w, d),
        "bottom": (u + d + w, v, w, d),
        "right": (u, v + d, d, h),
        "front": (u + d, v + d, w, h),
        "left": (u + d + w, v + d, d, h),
        "back": (u + 2 * d + w, v + d, w, h),
    }


def grid(rect, rows):
    """Paint a face from strings; '.' leaves the pixel untouched."""
    x0, y0, w, h = rect
    assert len(rows) == h and all(len(r) == w for r in rows), rect
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                img.putpixel((x0 + x, y0 + y), rgba(ch))


def fill(rect, fn):
    x0, y0, w, h = rect
    for y in range(h):
        for x in range(w):
            ch = fn(x, y)
            if ch and ch != ".":
                img.putpixel((x0 + x, y0 + y), rgba(ch))


DARKER = {"q": "Q", "Q": "T", "T": "D", "D": "K", "K": "K"}


def scales(x, y, dark=0):
    """Offset fish-scale pattern: a light pixel sitting on a dark one."""
    phase = (x + y // 2) % 2
    if y % 2 == 0:
        ch = "Q" if phase == 0 else "T"
    else:
        ch = "D" if phase == 0 else "T"
    for _ in range(dark):
        ch = DARKER[ch]
    return ch


# ---------------------------------------------------------------- head
head = faces(0, 0, 8, 8, 8)
hat = faces(32, 0, 8, 8, 8)

grid(head["front"], [
    "HHLLHHLH",
    "HSSSSHLH",
    "SBBSSBBS",
    "SWISSIWS",
    "SSSSsSSS",
    "SSmSSmSS",
    "SSSMMSSS",
    "sSSSSSSs",
])
right_side = [  # x0 = back of head, x7 = face side
    "HHLHHHHH",
    "HHHHHLHH",
    "hHHHHHHS",
    "hHHnnSSS",
    "hHHnnSSS",
    "hhHSSSSs",
    "hsSSSSss",
    "sssSSSss",
]
grid(head["right"], right_side)
grid(head["left"], [r[::-1] for r in right_side])
grid(head["back"], [
    "HLHHHLHH",
    "HHHLHHHL",
    "hHHHHHHh",
    "hHLHHLHh",
    "hHHHHHHh",
    "hhHHHHhh",
    "shhHHhhs",
    "ssssssss",
])
# top: row 0 = back of head, row 7 = forehead; streaks combed back
grid(head["top"], [
    "hHHLHHhH",
    "HHLHHHHH",
    "HLHHHhLH",
    "HHHLHHHH",
    "HLHHHhHL",
    "HHLHHHLH",
    "HLHLHhHH",
    "HHLLHHLH",
])
fill(head["bottom"], lambda x, y: "s")

# hat layer: swept-back volume on top and a quiff over the forehead
grid(hat["top"], [
    "........",
    "........",
    "..L...L.",
    "........",
    ".L..L...",
    "...L..L.",
    "HLHHLHHH",
    "HHLLHLHH",
])
grid(hat["front"], [
    "LHLLHLHH",
    "......HH",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
])
grid(hat["right"], ["HHHHHLHH"] + ["........"] * 7)
grid(hat["left"], ["HHLHHHHH"] + ["........"] * 7)
grid(hat["back"], ["HHLHHHLH", "hHHHHHHh"] + ["........"] * 6)

# ---------------------------------------------------------------- body
body = faces(16, 16, 8, 12, 4)
jacket = faces(16, 32, 8, 12, 4)

EMBLEM = [  # gold medallion with two waves, rows 2-5, x 2-5
    ".YG.",
    "YAqG",
    "GqAg",
    ".Gg.",
]


def body_front(x, y):
    if y == 0:
        return "DDDssDDD"[x]
    if 2 <= y <= 5 and 2 <= x <= 5 and EMBLEM[y - 2][x - 2] != ".":
        return EMBLEM[y - 2][x - 2]
    if y == 9:
        return "gGGYYGGg"[x]
    if y == 10 and x in (3, 4):
        return "G"
    return scales(x, y, dark=1 if x in (0, 7) or y >= 10 else 0)


fill(body["front"], body_front)
fill(body["back"], lambda x, y: "D" if y == 0 else "gGGGGGGg"[x] if y == 9
     else scales(x, y, dark=1 if x in (0, 7) else 0))
for side in ("right", "left"):
    fill(body[side], lambda x, y: "D" if y == 0 else "G" if y == 9
         else scales(x, y, dark=1))
fill(body["top"], lambda x, y: "D")
fill(body["bottom"], lambda x, y: "D")

# jacket layer: raised belt and medallion
fill(jacket["front"], lambda x, y: "gGGYYGGg"[x] if y == 9
     else EMBLEM[y - 2][x - 2] if 2 <= y <= 5 and 2 <= x <= 5 else ".")
fill(jacket["back"], lambda x, y: "gGGGGGGg"[x] if y == 9 else ".")
for side in ("right", "left"):
    fill(jacket[side], lambda x, y: "G" if y == 9 else ".")


# ---------------------------------------------------------------- arms
def arm(base, overlay, outer):
    f = faces(*base, 4, 12, 4)
    o = faces(*overlay, 4, 12, 4)
    inner = "left" if outer == "right" else "right"

    def paint(dark):
        def fn(x, y):
            if y <= 5:
                return scales(x, y, dark)
            if y == 6:
                return "D"
            return "D" if x == 1 and y < 11 and dark == 0 else "K"
        return fn

    fill(f["front"], paint(0))
    fill(f[outer], paint(0))
    fill(f["back"], paint(1))
    fill(f[inner], paint(1))
    fill(f["top"], lambda x, y: scales(x, y))
    fill(f["bottom"], lambda x, y: "K")
    # fin along the outside of the forearm, raised on the overlay
    fin = ["....", "....", "....", "....", "....", "....",
           ".Ff.", ".Ff.", ".Ff.", ".Ff.", ".F..", ".f.."]
    if outer == "left":
        fin = [r[::-1] for r in fin]
    grid(o[outer], fin)


arm((40, 16), (40, 32), outer="right")
arm((32, 48), (48, 48), outer="left")


# ---------------------------------------------------------------- legs
def leg(base, inner):
    f = faces(*base, 4, 12, 4)

    def paint(dark):
        def fn(x, y):
            if y == 0:
                return "D"
            if y <= 6:
                return scales(x, y, dark)
            if y == 7:
                return "f"
            if y == 11:
                return "Z"
            return "D" if x == 1 and dark == 0 else "K"
        return fn

    outer = "left" if inner == "right" else "right"
    fill(f["front"], paint(0))
    fill(f[outer], paint(0))
    fill(f["back"], paint(1))
    fill(f[inner], paint(1))
    fill(f["top"], lambda x, y: "D")
    fill(f["bottom"], lambda x, y: "Z")


leg((0, 16), inner="left")    # right leg: its left side faces the other leg
leg((16, 48), inner="right")  # left leg

out = Path(__file__).with_name("the_deep.png")
img.save(out)
print(f"wrote {out}")
