# 2026-11-20 · sprite-stacking: four orthographic views into rotatable 3D pixel art

[中文](README.md) | **English**

![The author's demo: six pixel assets — a lighthouse, a hot-air balloon, a rocket, a car, a house and a bonsai — turning](https://raw.githubusercontent.com/danielwh2/sprite-stacking/6fecdfd0d6e5a0595f979550e05f4b1fcde550fe/media/showcase.gif)

*Above is the demo GIF from the author's repo (`media/showcase.gif`). MIT licence, © Daniel White.*

## What it is

[sprite-stacking](https://github.com/danielwh2/sprite-stacking) is a skill for AI agents: give it a pixel sheet
with four orthographic views (top / side / front / back) and it intersects those four silhouettes into a rough
volume, cuts it into flat layers, and renders each layer rotated by the same angle and lifted by one pixel — so
**one flat pixel drawing becomes a rotatable fake-3D pixel sculpture**.

Author Daniel White (@dwhitedesign) posted it on 2026-11-20: "I made a skill so your agent can turn anything into
spinning 3D pixel art", crediting @asynkimo's article. Sprite stacking itself is a long-standing indie technique;
what this repo adds is the four-view carving and the agent-facing workflow.

## Original source

- Original post: [Daniel White on X](https://x.com/i/web/status/2123787861392855388) (2026-11-20)
- Repo: [danielwh2/sprite-stacking](https://github.com/danielwh2/sprite-stacking) (MIT, created 2026-11-20;
  106 stars / 12 forks as of 2026-11-20)
- The author's demo: `media/showcase.gif` (above) and `media/pipeline.png` (below) in the repo

![Four views → carved slices → stacked and spinning](https://raw.githubusercontent.com/danielwh2/sprite-stacking/6fecdfd0d6e5a0595f979550e05f4b1fcde550fe/media/pipeline.png)

*The author's pipeline diagram: ① four orthographic views → ② carved into 42 slices → ③ stacked, spinning at any angle.*

## How it works

| Mechanism | What it does | Where |
|---|---|---|
| Four-view intersection (visual hull) | The top view fixes the plan outline, the front/side views fix the profile; their intersection is the voxel volume. Interior cavities no view can see get filled in | `scripts/views_to_slices.py`, SKILL.md steps 1–2 |
| Slicing along height | The volume is cut into N horizontal layers, written as one horizontal strip PNG (ground layer leftmost, roof layer rightmost) | same |
| Shared palette quantisation | The four views are first quantised to one palette so slices don't seam with colour steps | same (`--colours`, default 24) |
| `--shade` side shading | Gives each layer's edge a bit of thickness, otherwise it still reads as a sticker | same (default 0.2) |
| The render loop | Each layer rotates by `turn` → y scaled by `squash` → lifted by `spacing` → drawn with nearest filtering | SKILL.md step 3, `references/engines.md` |
| One outline for the whole stack | The silhouette is traced once after the layers are composited, not per layer (per-layer outlines draw seam stripes across the body) | SKILL.md step 3 |
| Baking static stacks | 200 trees × 30 slices is 6,000 draw calls a frame, so static stacks are baked into one sprite at load time | SKILL.md step 3 |

The author fixes the render numbers so you don't have to guess them: `spacing = 1.0`, `squash = 0.75`
(= `sin(camera elevation)`), and the rotation centre is the symmetric `(w-1) * 0.5` with `Math.round` nearest
sampling — using `floor(... + w/2)` on even-sized slices shifts the centre by half an art pixel and makes the
sprite wobble across 90° / 180° / 270° turns. Positions stay in floating-point screen space and are rounded only
at the final blit.

`references/engines.md` carries a recipe per engine: web Canvas / React, Godot 4 `Node2D` (about 20 lines),
Unity (one `SpriteRenderer` per layer) and Phaser / Pygame. `scripts/viewer.html` is a standalone web viewer:
turntable, small scenes (Neon Street, Meadow Island), slice scan, exploded view, Drive / Wind / Shatter play modes,
day through night, rain and snow, plus a 16-direction PNG sprite-sheet export.

## Why it is worth a look

- **It saves art time, not art skill.** "An asset that can turn" used to mean 8 or 16 directions × N frames; now
  it means 4 orthographic views — and an image model can produce those from the repo's copy-paste prompt.
  That turns an exponential number of drawings into a constant.
- **The valuable part is the lessons table, not the code.** The 19-row Lessons table at the end of SKILL.md is
  one row per mistake: what broke → the rule that prevents it → what enforces the rule. "1-pixel parts blink as
  the stack turns → draw them at least 2px wide → the slicer warns", "a square TOP view carves a box → carve
  towers and balloons with `--round`". Turning bugs into rules, and rules into automatic checks, is worth more
  than any single function in this repo.
- **It is written as a skill for agents.** The usage is "tell your agent: make me a rotatable pixel car" and the
  agent does the drawing, carving and rendering itself. The repo ships a self-check, `tests/check.py`, which
  prints `ok` (I ran it).
- **One use I can think of that the author does not cover.** Render orthographic views from a 3D model you already
  have, quantise them to pixel art and feed them to the slicer — "turn my 3D project props into rotatable pixel
  art" as a pipeline.

## Limits

Written in the author's own Lessons table:

- **Cavities fill in.** Interior structure no view can see (truck beds, hollow arches, the middle of a mug handle)
  cannot be carved out; those slices have to be fixed by hand afterwards.
- **Fins, wings and foliage carve as blocks.** The TOP view must carry the real outline, or irregular planes
  come out rectangular.
- **1-pixel-wide parts flicker.** Flag poles and antennas need to be at least 2px wide; the script warns about
  such thin runs.
- **Background enclosed on all sides carves solid.** Every gap has to reach the outside of its view.
- **An off-centre object spins off-axis.** If the base reaches further on one side, the whole stack orbits a
  shifted centre.
- **Slice count decides how smooth the turn looks.** The author's tiers: chunky retro 15–20 slices (~25×48 px),
  detailed hi-bit 26–44, showcase / video 36–56 slices shown at only 4–6×. Too few slices blown up too far
  gives visible stepping.

Others (from reading the repo and the author's material):

- **The repo is brand new.** Created 2026-11-20, `main` branch only, no formal release, and the author kept
  committing the same day. Pin a commit rather than tracking `main`.
- **It is not real 3D.** There is no true back-side geometry, only something that looks like it. Objects whose
  back view differs from the front are safest drawn the same on both.
- **Do not use it in place of 3D.** If your project is 3D anyway, a low-poly model plus a pixelation shader is
  the better route. This pipeline earns its keep when you have pixel art, or when you have a 3D model but want a
  spinning pixel version of it.
