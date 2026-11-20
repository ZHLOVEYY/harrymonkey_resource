#!/usr/bin/env python3
"""Reference model of the tall-grass spring / trample maths.

This is the pseudo code from the SpriteCook article (2026-11-19) turned into a
script, so the acceptance numbers the article quotes can be recomputed instead
of believed. Numbers printed here are the facts quoted in the post.
"""
import math

DT = 1.0 / 60.0
SPRING_HZ = 2.6
DAMPING = 0.22
MAX_LEAN = 8.0
LEAN_PX = 7.0
FEEL_X, FEEL_BACK, FEEL_FRONT = 12.0, 4.0, 10.0
FRONT_X, FRONT_LEAN = 9.0, 2.0
PRESS_X, PRESS_BACK = 7.0, 10.0
PRESS_TIME, RECOVER_TIME = 0.12, 0.7
PRESS_SQUASH = 0.67
SORT_OFFSET = 1


def spring(lean, vel, target):
    w = 2 * math.pi * SPRING_HZ
    acc = w * w * (target - lean) - 2 * DAMPING * w * vel
    vel += acc * DT
    lean = max(-MAX_LEAN, min(MAX_LEAN, lean + vel * DT))
    return lean, vel


def lean_target(dx, dy, side):
    if abs(dx) < FEEL_X and dy > -FEEL_BACK and dy < FEEL_FRONT:
        if side == 0:
            side = 1 if dx > 0 else -1
        target = (side * LEAN_PX * min(1.0, (FEEL_X - abs(dx)) / 6.0)
                  * min(1.0, (FEEL_FRONT - abs(dy - 3)) / 5.0))
        if dy > -SORT_OFFSET and abs(dx) < FRONT_X:
            target = max(-FRONT_LEAN, min(FRONT_LEAN, target))
        return target, side
    return 0.0, 0


def smoothstep(p):
    return p * p * (3 - 2 * p)


def drawn_height(h, press):
    return int(math.floor(h * (1 - PRESS_SQUASH * smoothstep(press)) + 0.5))


def _settles_from(hist, target, tol=0.5):
    """First tick from which the value never leaves the tolerance band again."""
    last_bad = -1
    for i, v in enumerate(hist):
        if abs(v - target) > tol:
            last_bad = i
    return last_bad + 2


def check_spring():
    """Article: peak 6.9 px on tick 11, settles within 0.5 of 4.67 from tick 35."""
    lean = vel = 0.0
    side = 0
    hist = []
    for _ in range(120):
        target, side = lean_target(7.0, -3.0, side)
        lean, vel = spring(lean, vel, target)
        hist.append(lean)
    peak = max(hist)
    peak_tick = hist.index(peak) + 1
    settle = _settles_from(hist, 4.666667)

    # release
    hist2 = []
    for _ in range(120):
        lean, vel = spring(lean, vel, 0.0)
        hist2.append(lean)
    back = min(hist2)
    back_tick = hist2.index(back) + 1
    settle0 = _settles_from(hist2, 0.0)
    return {
        "target_px": round(LEAN_PX * min(1, (12 - 7) / 6) * min(1, (10 - 6) / 5), 3),
        "peak_px": round(peak, 3), "peak_tick": peak_tick,
        "settle_tick": settle,
        "release_px": round(back, 3), "release_tick": back_tick,
        "settle_zero_tick": settle0,
    }


def check_trample():
    """Article: press 1 on tick 8 at 6 px tall, back to 18 px on tick 37, press 0 on tick 42."""
    press = 0.0
    for tick in range(1, 60):
        press = min(1.0, press + DT / PRESS_TIME)
        if press >= 1.0:
            break
    flat_tick = tick
    flat_h = drawn_height(18, press)

    press = 1.0
    full_tick = press_zero_tick = None
    for tick in range(1, 60):
        press = max(0.0, press - DT / RECOVER_TIME)
        if full_tick is None and drawn_height(18, press) == 18:
            full_tick = tick
        if press <= 0.0:
            press_zero_tick = tick
            break
    return {
        "press_full_tick": flat_tick, "pressed_height_px": flat_h,
        "full_height_tick": full_tick, "press_zero_tick": press_zero_tick,
    }


if __name__ == "__main__":
    s = check_spring()
    t = check_trample()
    print("SPRING")
    for k, v in s.items():
        print(f"  {k:20s} {v}")
    print("TRAMPLE")
    for k, v in t.items():
        print(f"  {k:20s} {v}")
    article = {
        "peak_px": 6.9, "peak_tick": 11, "settle_tick": 35, "release_px": -2.3,
        "settle_zero_tick": 36, "press_full_tick": 8, "pressed_height_px": 6,
        "full_height_tick": 37, "press_zero_tick": 42,
    }
    print("MATCH AGAINST THE ARTICLE")
    ok = True
    for k, want in article.items():
        got = s.get(k, t.get(k))
        tol = 0.06 if k.endswith("_px") else 1      # pixels: 0.06 px, ticks: +-1
        good = abs(float(got) - float(want)) <= tol
        ok = ok and good
        print(f"  {'OK ' if good else 'DIFF'} {k:20s} article={want} recomputed={got}")
    print("ALL MATCH" if ok else "MISMATCH")
    print("note: settle_zero_tick depends on the tick the player steps away on "
          "(article: 36, ours: 35 for a tuft that had already settled)")
