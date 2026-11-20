#!/usr/bin/env python3
"""Generate the pixel art for the tall-grass demo.

Everything is drawn from scratch here: no SpriteCook assets, no downloads.
Spec follows the article (SpriteCook blog, 2026-11-19):
  - tufts 16x18 px, 4 variants + horizontal flip, lower 10 rows solid
  - two darker shades per tuft, made by moving every colour one / two steps
    down its own ramp
  - the ground under the patch is one flat dark green
  - the player is ~32 px tall
"""
from pathlib import Path
import random
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "project" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

# one green ramp; a darker shade is the same shape with every index moved down
RAMP = [
    (16, 40, 22),    # 0 outline / deepest shadow
    (30, 74, 34),    # 1
    (46, 108, 44),   # 2
    (66, 145, 54),   # 3 body (normal)
    (92, 180, 66),   # 4 body highlight
    (124, 214, 96),  # 5 tip highlight
]
GROUND = (30, 58, 38)      # flat dark green under the patch
FLOOR_BASE = (30, 74, 34)  # the "grass painted on the floor" tile
OUTLINE = (48, 34, 20)
CREAM = (240, 226, 190)
CREAM_LIGHT = (250, 240, 214)
CREAM_SHADE = (212, 190, 144)
EAR = (206, 146, 108)
SCARF = (200, 72, 60)
EYE = (32, 24, 18)

TUFT_W, TUFT_H = 16, 18
BASE_ROW = 8   # rows 8..17 (the lower 10 rows) are the solid foot
FOOT_L, FOOT_R = 4, 11

# blade layout per variant: (x centre, height above the foot, curve)
VARIANTS = [
    [(3, 7, -1), (6, 5, 0), (9, 6, 0), (12, 7, 1)],
    [(3, 6, -1), (6, 7, 0), (9, 5, 0), (12, 6, 1)],
    [(2, 6, -1), (5, 8, 0), (8, 6, 0), (11, 7, 1)],
    [(3, 8, -1), (6, 6, 0), (9, 7, 0), (12, 5, 1)],
]


def _shade(ramp, down):
    """Every colour one or two steps down the same ramp."""
    return [c if i - down < 0 else ramp[max(0, i - down)] for i, c in enumerate(ramp)]


def _tuft_mask(variant):
    """Boolean mask of the tuft silhouette (no colour yet)."""
    m = [[False] * TUFT_W for _ in range(TUFT_H)]
    # solid foot: the lower 10 rows, nothing behind a tuft shows through it
    for y in range(BASE_ROW + 2, TUFT_H - 1):
        for x in range(FOOT_L, FOOT_R + 1):
            m[y][x] = True
    blade_cols = {}
    for cx, h, curve in VARIANTS[variant]:
        for d in range(h):                      # d = rows above the foot
            y = BASE_ROW - 1 - d
            if y < 1:
                break
            x = cx + int(round(curve * d / 4.0))
            for xx in (x - 1, x):
                if 0 <= xx < TUFT_W:
                    m[y][xx] = True
            blade_cols.setdefault(y, set()).update((x - 1, x))
    # ragged shoulder: the foot only starts under the blades, so the tuft has
    # no flat rim; the foot is solid from row 10 down.
    all_cols = set()
    for cols in blade_cols.values():
        all_cols |= cols
    for y in (BASE_ROW, BASE_ROW + 1):
        for x in range(FOOT_L, FOOT_R + 1):
            if x in all_cols:
                m[y][x] = True
    return m


def _outline(img, colour):
    """Classic pixel-art outline: any opaque pixel next to transparency."""
    px = img.load()
    w, h = img.size
    out = img.copy()
    op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                continue
            edge = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or px[nx, ny][3] == 0:
                    edge = True
                    break
            if edge:
                op[x, y] = colour + (255,)
    return out


def _outline_out(img, colour):
    """Outline drawn outside the silhouette, so 2 px blades keep their body."""
    px = img.load()
    w, h = img.size
    out = img.copy()
    op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] != 0:
                    op[x, y] = colour + (255,)
                    break
    return out


def _tuft(variant, shade):
    ramp = _shade(RAMP, shade)
    img = Image.new("RGBA", (TUFT_W, TUFT_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mask = _tuft_mask(variant)
    body, hi, tip = ramp[3], ramp[4], ramp[5]
    px = img.load()
    for y in range(TUFT_H):
        for x in range(TUFT_W):
            if not mask[y][x]:
                continue
            px[x, y] = body + (255,)
    # highlight the upper half of every blade, tip in the lightest step
    for cx, h, curve in VARIANTS[variant]:
        for d_ in range(h):
            y = BASE_ROW - 1 - d_
            if y < 1:
                break
            x = cx + int(round(curve * d_ / 4.0))
            col = tip if d_ == h - 1 else (hi if d_ > h * 0.5 else body)
            for xx in (x - 1, x):
                if 0 <= xx < TUFT_W and mask[y][xx]:
                    px[xx, y] = col + (255,)
    img = _outline_out(img, ramp[0])
    return img


def _floor_tile():
    """32x32 tileable 'grass painted on the floor' for the naive panel."""
    rnd = random.Random(7)
    img = Image.new("RGBA", (32, 32), FLOOR_BASE + (255,))
    d = ImageDraw.Draw(img)
    for _ in range(34):
        x = rnd.randrange(32)
        y = rnd.randrange(32)
        h = rnd.choice((1, 2, 2, 3))
        col = RAMP[2] if rnd.random() < 0.6 else RAMP[1]
        for k in range(h):                      # wrap so the tile stays seamless
            d.point((x % 32, (y + k) % 32), fill=col + (255,))
    return img


def _ellipse(draw, cx, cy, rx, ry, colour):
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=colour)


def _creature(frame):
    """32x32 top-down creature, facing down (eyes low on the body)."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bob = -1 if frame in (1, 3) else 0
    foot_l = (26, 27, 28, 27)[frame]
    foot_r = (28, 27, 26, 27)[frame]

    _ellipse(d, 16, 20 + bob, 11, 10, CREAM_SHADE)         # shaded rim
    _ellipse(d, 16, 18 + bob, 11, 10, CREAM)                # body
    _ellipse(d, 8, 7 + bob, 3, 4, EAR)                      # ears
    _ellipse(d, 24, 7 + bob, 3, 4, EAR)
    _ellipse(d, 16, 13 + bob, 6, 4, RAMP[3])                # leaf on its back
    d.point((16, 17 + bob), fill=RAMP[1] + (255,))
    _ellipse(d, 10, foot_l, 3, 2, CREAM_SHADE)              # feet
    _ellipse(d, 22, foot_r, 3, 2, CREAM_SHADE)
    img = _outline(img, OUTLINE)
    # eyes and nose on top of the outline
    px = img.load()
    for x0 in (11, 19):
        for y0 in (20, 21):
            px[x0, y0] = EYE + (255,)
            px[x0 + 1, y0] = EYE + (255,)
    px[15, 23] = EYE + (255,)
    px[16, 23] = EYE + (255,)
    return img


def main():
    made = []
    for v in range(4):
        for shade, tag in ((0, ""), (1, "_dark1"), (2, "_dark2")):
            name = f"tuft_{v}{tag}.png"
            _tuft(v, shade).save(OUT / name)
            made.append(name)
    _floor_tile().save(OUT / "grass_floor.png")
    made.append("grass_floor.png")

    sheet = Image.new("RGBA", (32 * 4, 32), (0, 0, 0, 0))
    for f in range(4):
        sheet.paste(_creature(f), (f * 32, 0))
    sheet.save(OUT / "creature.png")
    made.append("creature.png")

    for name in made:
        im = Image.open(OUT / name)
        print(f"{name:22s} {im.size[0]}x{im.size[1]}")
    print(f"{len(made)} files -> {OUT}")


if __name__ == "__main__":
    main()
