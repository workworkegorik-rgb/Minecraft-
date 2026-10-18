"""Generate a 128x128 HD Minecraft skin of The Deep (The Boys).

Same layout as a 64x64 skin with every pixel split in four, so it needs a
launcher, server or edition that accepts HD skins. Classic (4px wide) arms.
Run: python3 skins/make_the_deep_hd.py  -> writes skins/the_deep_hd.png
"""
import math
from pathlib import Path

from PIL import Image

S = 2  # HD pixels per classic skin pixel
img = Image.new("RGBA", (64 * S, 64 * S), (0, 0, 0, 0))


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# palette for the hand-drawn head
CHARS = {
    # hair, dark to light
    "1": "#3e2a1a", "2": "#5a3e27", "3": "#765536", "4": "#977049",
    # skin, light to dark
    "a": "#f2cdb0", "b": "#e9bb9a", "c": "#dca684", "d": "#c48b6a",
    "e": "#a8715a", "f": "#8a5745",
    # eyes, brows, lips
    "w": "#f5f2ee", "x": "#d6cec8", "h": "#7cc3db", "i": "#3f93b0", "j": "#24627a",
    "l": "#3a2a22", "B": "#4a3220", "C": "#6a4a30",
    "m": "#a5625a", "o": "#7d4842", "n": "#c27b70",
}

SUIT = rgb("#16625a")
GLOVE = rgb("#0f3d39")
TRIM = rgb("#2c9586")
BOOT = rgb("#0d3532")
SOLE = rgb("#082624")
GOLD = rgb("#d6a532")
AQUA = rgb("#5fd3c4")
DEEP_WATER = rgb("#1d6f86")
FIN = rgb("#43bfae")


def faces(u, v, w, h, d):
    """HD texture rects (x, y, width, height) of a box unwrapped at (u, v)."""
    u, v, w, h, d = (n * S for n in (u, v, w, h, d))
    return {
        "top": (u + d, v, w, d),
        "bottom": (u + d + w, v, w, d),
        "right": (u, v + d, d, h),
        "front": (u + d, v + d, w, h),
        "left": (u + d + w, v + d, d, h),
        "back": (u + 2 * d + w, v + d, w, h),
    }


def put(x, y, color):
    img.putpixel((x, y), tuple(max(0, min(255, round(c))) for c in color) + (255,))


def paint(rect, fn):
    """fn(x, y, w, h) returns an RGB tuple, a palette char, or None to skip."""
    x0, y0, w, h = rect
    for y in range(h):
        for x in range(w):
            c = fn(x, y, w, h)
            if c is None or c == ".":
                continue
            put(x0 + x, y0 + y, rgb(CHARS[c]) if isinstance(c, str) else c)


def grid(rect, rows):
    assert len(rows) == rect[3] and all(len(r) == rect[2] for r in rows), rect
    paint(rect, lambda x, y, w, h: rows[y][x])


# ---------------------------------------------------------------- shading
def noise(x, y, seed=0):
    """Deterministic value noise in [-1, 1]."""
    n = (x * 374761393 + y * 668265263 + seed * 982451653) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1


def shade(color, b):
    """b > 0 lightens toward white, b < 0 darkens toward black."""
    b = max(-0.75, min(0.6, b))
    if b >= 0:
        return tuple(c + (255 - c) * b for c in color)
    return tuple(c * (1 + b) for c in color)


def dome(px, py, cx, cy, rx, ry, amp=1.0):
    e = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
    return amp * math.sqrt(1 - e) if e < 1 else 0.0


def lit(bumps, x, y, k=0.9, ao=0.32):
    """Light a muscle height map from above and slightly to the left."""
    def height(px, py):
        return sum(dome(px, py, *b) for b in bumps)

    px, py = x + 0.5, y + 0.5
    dx = height(px + 0.5, py) - height(px - 0.5, py)
    dy = height(px, py + 0.5) - height(px, py - 0.5)
    b = k * (0.3 * dx + 0.95 * dy)
    return max(-0.45, min(0.35, b)) + ao * (min(height(px, py), 1) - 0.4)


def roundness(x, w, k=0.22):
    """Darken toward the vertical edges so limbs read as round."""
    return -k * ((x + 0.5 - w / 2) / (w / 2)) ** 2


def scales(x, y):
    """Staggered fish scales: lit crown, dark lower rim."""
    row = y // 3
    lx, ly = (x + (2 if row % 2 else 0)) % 4, y % 3
    return ((-0.05, 0.06, 0.06, -0.05),
            (0.00, 0.10, 0.05, 0.00),
            (-0.16, -0.03, -0.03, -0.16))[ly][lx]


def suit(x, y, b, seed=11):
    return shade(SUIT, b + scales(x, y) + 0.035 * noise(x, y, seed))


def hair(x, y, seed, bias=0.0):
    t = (0.55 + bias + 0.22 * noise(x, 0, seed)
         + 0.14 * noise(x, y // 3, seed + 1) + 0.06 * noise(x, y, seed + 2))
    return "1" if t < 0.32 else "2" if t < 0.55 else "3" if t < 0.78 else "4"


# ---------------------------------------------------------------- head
head = faces(0, 0, 8, 8, 8)
hat = faces(32, 0, 8, 8, 8)

grid(head["front"], [
    "3344344334434433",
    "2344433443344432",
    "1233443344334321",
    "1223bbbbbbbb3221",
    "12cbbbbbbbbbbc21",
    "2cCBBBcbbcBBBCc2",
    "1cllllcbbcllllc1",
    "2cwhiwcbbcwhiwc2",
    "2dxijxcbbcxijxd2",
    "1dccccbbcdccccd1",
    "dcccccbbcdcccccd",
    "dcccccdccdcccccd",
    "dccccmccccmccccd",
    "dcccccmoomcccccd",
    "ddcccccbbcccccdd",
    "eddcccbbbbcccdde",
])
right_side = [  # x0 = back of head, x15 = face side; ear in the middle
    "2333443333443332",
    "1233443343344322",
    "1223334333433332",
    "1222333333332222",
    "1122223332222222",
    "112222222dcbbc22",
    "111222" "dccd" "c" "bb" "c" "22",
    "111222" "cefc" "c" "bb" "c" "22",
    "112222" "cefc" "c" "ab" "c" "21",
    "112222" "cefc" "c" "bb" "c" "21",
    "11222d" "cdec" "c" "bb" "c" "cd",
    "1122dd" "ddcd" "c" "cc" "c" "cd",
    "122ddd" "dddd" "c" "cc" "d" "dd",
    "dddeee" "dddd" "d" "cd" "d" "de",
    "eeeeee" "eddd" "d" "dd" "d" "ee",
    "eeeeee" "eeee" "e" "ee" "e" "ee",
]
grid(head["right"], right_side)
grid(head["left"], [r[::-1] for r in right_side])
paint(head["back"], lambda x, y, w, h:
      hair(x, y, 5, -0.18 * y / 12) if y <= 11 or (y == 12 and 2 <= x <= 13)
      else "d" if y <= 13 else "e")
paint(head["top"], lambda x, y, w, h: hair(x, y, 3, 0.05))
paint(head["bottom"], lambda x, y, w, h: "e")

# hat layer: volume swept up and back from the forehead
paint(hat["top"], lambda x, y, w, h: hair(x, y, 21, 0.1) if y >= 9 else None)
paint(hat["front"], lambda x, y, w, h:
      hair(x, y, 23, 0.12) if y <= 1 or (y == 2 and (x <= 2 or x >= 13)) else None)
paint(hat["right"], lambda x, y, w, h: hair(x, y, 25, 0.08) if y <= 2 and x >= 8 else None)
paint(hat["left"], lambda x, y, w, h: hair(x, y, 27, 0.08) if y <= 2 and x <= 7 else None)


# ---------------------------------------------------------------- body
def medallion(px, py):
    """Gold ring with a wave inside, centred on the chest."""
    r = math.hypot(px - 8, py - 7)
    if r > 2.5:
        b = 0.35 * (-(px - 8) * 0.4 - (py - 7) * 0.9) / r - (0.15 if r > 3.2 else 0)
        return shade(GOLD, b)
    wave = 7.0 + 0.8 * math.sin((px - 8) * 1.7)
    if abs(py - wave) < 0.5:
        return shade(AQUA, 0.25)
    return shade(DEEP_WATER, 0.05) if py < wave else shade(AQUA, -0.1)


def belt(x, y):
    b = 0.18 if y % 2 == 0 else -0.14
    if x % 4 == 3:
        b -= 0.16
    return shade(GOLD, b + 0.04 * noise(x, y, 31))


def buckle(x, y):
    if 7 <= x <= 8 and 18 <= y <= 19:  # aqua gem
        return shade(AQUA, 0.3 if (x, y) == (7, 18) else -0.05)
    return shade(GOLD, 0.32 if (x == 6 or y == 17) else -0.3)


PECS_ABS = [
    (4.3, 5.8, 3.9, 3.0, 1.0), (11.7, 5.8, 3.9, 3.0, 1.0),
    (6.0, 10.4, 1.9, 1.4, 0.75), (10.0, 10.4, 1.9, 1.4, 0.75),
    (6.0, 13.2, 1.9, 1.3, 0.75), (10.0, 13.2, 1.9, 1.3, 0.75),
    (6.1, 16.0, 1.8, 1.3, 0.7), (9.9, 16.0, 1.8, 1.3, 0.7),
    (1.2, 12.5, 1.6, 6.0, 0.5), (14.8, 12.5, 1.6, 6.0, 0.5),
]
BACK = [
    (4.6, 6.0, 3.4, 3.8, 0.9), (11.4, 6.0, 3.4, 3.8, 0.9),
    (5.6, 14.0, 2.4, 3.6, 0.6), (10.4, 14.0, 2.4, 3.6, 0.6),
    (8.0, 0.5, 6.0, 2.0, 0.5),
]


def body_front(x, y, w, h):
    px, py = x + 0.5, y + 0.5
    if y == 0:
        return "e" if 6 <= x <= 9 else suit(x, y, -0.4)
    if y == 1:
        return "e" if 7 <= x <= 8 else suit(x, y, -0.5 if x in (6, 9) else -0.3)
    if math.hypot(px - 8, py - 7) <= 3.6:
        return medallion(px, py)
    if 6 <= x <= 9 and 17 <= y <= 20:
        return buckle(x, y)
    if 18 <= y <= 19:
        return belt(x, y)
    b = lit(PECS_ABS, x, y) + 0.08 - py / 24 * 0.18 - 0.12 * (abs(px - 8) / 8) ** 4
    return suit(x, y, b - (0.12 if y >= 20 else 0))


def body_back(x, y, w, h):
    if y == 0:
        return suit(x, y, -0.4)
    if 18 <= y <= 19:
        return belt(x, y)
    b = lit(BACK, x, y) + 0.02 - (y + 0.5) / 24 * 0.18
    return suit(x, y, b - (0.12 if y >= 20 else 0))


def body_side(x, y, w, h):
    if y == 0:
        return suit(x, y, -0.45)
    if 18 <= y <= 19:
        return belt(x, y)
    return suit(x, y, lit([(4, 12, 3.2, 7, 0.6)], x, y) - 0.12 + roundness(x, w, 0.15))


body = faces(16, 16, 8, 12, 4)
jacket = faces(16, 32, 8, 12, 4)
paint(body["front"], body_front)
paint(body["back"], body_back)
paint(body["right"], body_side)
paint(body["left"], body_side)
paint(body["top"], lambda x, y, w, h: suit(x, y, -0.1))
paint(body["bottom"], lambda x, y, w, h: suit(x, y, -0.35))

# jacket layer: raised medallion and belt
paint(jacket["front"], lambda x, y, w, h:
      medallion(x + 0.5, y + 0.5) if math.hypot(x + 0.5 - 8, y + 0.5 - 7) <= 3.6
      else buckle(x, y) if 6 <= x <= 9 and 17 <= y <= 20
      else belt(x, y) if 18 <= y <= 19 else None)
paint(jacket["back"], lambda x, y, w, h: belt(x, y) if 18 <= y <= 19 else None)
for side in ("right", "left"):
    paint(jacket[side], lambda x, y, w, h: belt(x, y) if 18 <= y <= 19 else None)


# ---------------------------------------------------------------- arms
ARM_MUSCLES = {
    "front": [(4, 2.6, 4.2, 3.2, 0.8), (4, 8.6, 2.9, 3.2, 0.7)],
    "outer": [(4, 2.6, 4.2, 3.4, 0.9), (4, 8.6, 3.0, 3.0, 0.5)],
    "back": [(4, 2.6, 4.2, 3.2, 0.7), (4, 8.6, 2.9, 3.4, 0.7)],
    "inner": [(4, 5.0, 3.0, 5.0, 0.3)],
}
SIDE_DARK = {"front": 0.0, "outer": -0.04, "back": -0.1, "inner": -0.18}


def arm_face(kind):
    def fn(x, y, w, h):
        dark = SIDE_DARK[kind] + roundness(x, w)
        if y < 12:
            return suit(x, y, lit(ARM_MUSCLES[kind], x, y) + dark)
        if y < 14:  # glove cuff
            return shade(TRIM, (0.15 if y == 12 else -0.12) + dark)
        b = dark + 0.03 * noise(x, y, 41)
        if kind == "front":
            b += lit([(4, 16.5, 3.2, 4.0, 0.6)], x, y)
            if y == 20 and x % 2 == 1:
                b += 0.18  # knuckles
            if y >= 21 and x in (2, 4, 6):
                b -= 0.25  # gaps between fingers
        return shade(GLOVE, b)
    return fn


def fin(mirror):
    """Ribbed fin down the outside of the forearm, sweeping back."""
    def fn(x, y, w, h):
        px, py = x + 0.5, y + 0.5
        if mirror:
            px = w - px
        if not 12 <= y <= 22:
            return None
        t = (py - 12) / 11
        cx, half = 4.6 - 1.4 * t, 2.8 * (1 - t) + 0.4
        if abs(px - cx) > half:
            return None
        b = 0.16 * math.sin((px + py * 0.55) * 2.4) + 0.1 * (1 - t)
        if abs(px - cx) > half - 0.8:
            b -= 0.18
        return shade(FIN, b)
    return fn


def arm(base, overlay, outer):
    f, o = faces(*base, 4, 12, 4), faces(*overlay, 4, 12, 4)
    inner = "left" if outer == "right" else "right"
    paint(f["front"], arm_face("front"))
    paint(f["back"], arm_face("back"))
    paint(f[outer], arm_face("outer"))
    paint(f[inner], arm_face("inner"))
    paint(f["top"], lambda x, y, w, h:
          suit(x, y, lit([(4, 4, 4.5, 4.5, 0.8)], x, y) + 0.05))
    paint(f["bottom"], lambda x, y, w, h: shade(GLOVE, -0.25 if x in (2, 4, 6) else -0.05))
    # outer face of the right arm runs back->front, the left arm front->back
    paint(o[outer], fin(mirror=outer == "left"))


arm((40, 16), (40, 32), outer="right")
arm((32, 48), (48, 48), outer="left")


# ---------------------------------------------------------------- legs
LEG_MUSCLES = {
    "front": [(4, 7.5, 3.3, 5.5, 0.7), (4, 13.0, 2.6, 1.6, 0.4)],
    "outer": [(4, 7.5, 3.3, 6.0, 0.5)],
    "back": [(4, 7.0, 3.3, 5.0, 0.6)],
    "inner": [],
}


def leg_face(kind):
    def fn(x, y, w, h):
        dark = SIDE_DARK[kind] + roundness(x, w)
        if y < 2:
            return suit(x, y, -0.35 + dark)  # shadow under the belt
        if y < 14:
            return suit(x, y, lit(LEG_MUSCLES[kind], x, y) + dark)
        if y < 16:  # boot cuff
            return shade(TRIM, (0.15 if y == 14 else -0.12) + dark)
        if y >= 22:
            return shade(SOLE, (0.15 if y == 22 else -0.1) + dark)
        b = dark + 0.03 * noise(x, y, 51)
        if kind == "front":
            b += lit([(4, 18, 2.8, 3.6, 0.5)], x, y) + (0.12 if y == 21 else 0)
        return shade(BOOT, b)
    return fn


def leg(base, inner):
    f = faces(*base, 4, 12, 4)
    outer = "left" if inner == "right" else "right"
    paint(f["front"], leg_face("front"))
    paint(f["back"], leg_face("back"))
    paint(f[outer], leg_face("outer"))
    paint(f[inner], leg_face("inner"))
    paint(f["top"], lambda x, y, w, h: suit(x, y, -0.3))
    paint(f["bottom"], lambda x, y, w, h: shade(SOLE, -0.1))


leg((0, 16), inner="left")    # right leg: its left side faces the other leg
leg((16, 48), inner="right")  # left leg

out = Path(__file__).with_name("the_deep_hd.png")
img.save(out)
print(f"wrote {out} ({img.width}x{img.height})")
