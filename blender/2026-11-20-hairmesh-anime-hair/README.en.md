# 2026-11-20 · HairMesh: draw guide curves, get anime hair meshes in Blender

[中文](README.md) | **English**

![Author's demo: switching between the guide curves and the converted mesh](https://raw.githubusercontent.com/riel-gab/hairmesh/3b8e9fe634a7994dfbf68b31c348672401531625/docs/img/overview.gif)

*From the author's repo (`docs/img/overview.gif`, GPL-3.0-or-later): the guide curves on the left, the converted hair mesh on the right, switching between Live and Baked.*

## What it is

A free Blender add-on: **draw a few guide curves** on a character's head, and the tool stretches
a "wall" between each pair of neighbouring curves — a row of walls is one lock of hair — which
it then converts into a **quad mesh with evenly spread edge loops**.

That is not the same thing as a "hair card" (a flat textured plane with an alpha map): this
produces **solid hair clumps**.

The author is riel (@koankitsu); the code is GPL-3.0-or-later. It is an authorised Blender port
of catarackta's browser app "Stylized HairMesh Creator" — the method and the original
application are theirs.

## Original source

- Original post: [Riel's introduction post on X](https://x.com/i/web/status/2123793496381485245) (2026-11-20)
  "Draw the silhouette of an anime fringe. Split a tip into two. Turn the locks into quads."
- Repo: [riel-gab/hairmesh](https://github.com/riel-gab/hairmesh) (GPL-3.0-or-later, created
  2026-10, 70 stars on 2026-11-20)
- Original app: [Stylized HairMesh Creator](https://catarackta.netlify.app/) (browser app,
  catarackta's original method)
- Docs: the `docs/` folder in the repo (getting-started / workflow / tools / shortcuts /
  troubleshooting)
- Author's demo: the `overview.gif` above; `docs/img/` also holds step-by-step screenshots of
  the wall, the conversion preview and the Live/Baked switch
- Third-party write-up: [80 Level's article](https://80.lv/articles/free-blender-tool-for-creating-stylized-anime-hair) (2026-11-10)

![Author's demo: a wall stretched between two curves](https://raw.githubusercontent.com/riel-gab/hairmesh/3b8e9fe634a7994dfbf68b31c348672401531625/docs/img/gs-wall.png)

*From the author's repo (`docs/img/gs-wall.png`, GPL-3.0-or-later): the "wall" pulled between two
selected curves via `Shift+RMB > Walls/Lock > Create Wall`.*

## How it works

| Part | What it does | Where |
|---|---|---|
| Guide curve | Draw a line point by point or freehand over the scalp, anchors snapping to the head surface; **the curves are the source**, the mesh is only the result | `docs/workflow.md`, "The idea" |
| Wall | The surface stretched between two neighbouring curves; a row of walls = one lock | same |
| Convert / Confirm | Bakes the ticked groups' locks into quad meshes with edge loops spread evenly by Loop Step; edit the curves and Convert again and only the changed locks are rebuilt | `docs/workflow.md`, "Conversion" |
| Group + Tick | Which locks become which mesh (Tick Top Groups = one mesh per top-level group) | same |
| Guides / Crowns | Guide rings (steer the loop layout), the whorl and the parting structure | same, "Guides" / "Crowns" |
| Symmetry | Model one side, mirror the other | same |
| Modifiers | tube / mask / thickness / twist / noise / curls / fill / density | same, "Modifiers" |

My reading (not the author's words):

- **It outputs solid clumps, not cards.** The difference matters a lot in anime and cel-shaded
  rendering: solid clumps have no alpha, so the silhouette stays clean and the outline (inverted
  hull) follows the clump's edge instead of the card's rectangle; alpha cards are actually more
  expensive in that look (sorting flicker, ugly outlines). So this tool targets the **standard
  approach for cartoon hair**, not a card pipeline.
- **It stops at geometry.** The converted mesh carries **no UV**, and no material, bones, weights
  or secondary animation. There is no UV-generating code anywhere in the repo — `from_pydata`
  builds vertices and faces and nothing else. "One click to a mesh" is still three manual steps
  away from "one click to a game-ready asset": UVs, texturing, skinning.
- **It is a purely deterministic tool that can be scripted.** The whole chain is geometry — no
  model, no sampling, the same inputs always give the same result. Every operator has a
  non-interactive entry point (`draw_curve(points_json=…)`, `create_walls`, `convert`,
  `confirm_conversion`), so it can be driven headless and in batches.

## Why it is worth a look

- **It is free, and it fills the gap in the one lane that is thin.** Most other Blender hair
  add-ons sold around the same time do **cards** (Hair Tool $52, StrandKit $90, HairTG-Cards
  $49, Simple Hair Cards $15, GBH Tool $10). For **solid clumps**, this is close to the only
  free option.
- **The nearest paid rival** is [Stylized Hair PRO](https://superhivemarket.com/products/stylized-hair-pro)
  ($22, MIT): free-form profiles, UVs, Hair Dynamics, braids. It does more, but it costs money.
  Further back is GBH Tool ($10–15, the most feature-complete, with automatic weights and hair
  card textures), but it has not been updated since 2024-11 and users report it crashing
  outright on Blender 5.1.
- **What studios actually do is neither of these.** Most cartoon hair is **modelled by hand**,
  or adapted from [VRoid Studio](https://vroid.com/en/studio) hair (VRoid's hair is already solid
  clumps; pixiv's terms allow commercial use and require no credit to pixiv, but the content is
  **not CC0**, and individual items carry their own terms). A tool saves the "cut the topology"
  step, not the styling and the shading.
- **Two free add-ons that complement it**: MT Hair Taper (tapers the ends of hair meshes —
  HairMesh's Tips cannot produce that natural taper) and Draw-Hair (draw curves along a guide
  mesh with automatic snapping).
- Requirements: **Blender 5.1 or newer**; `Detail Proxy` is a migration switch that changes the
  loop layout of older projects when it is on.

## Limits

- No UVs, no material, no bone weights, no LOD / shadow cards / alpha cards.
- Solid clumps only. Realistic strands are a different class of tool.
- Blender only — no Maya, Houdini or UE version.
- It is a port: the author says future updates focus on Blender-specific improvements; the method
  itself belongs to catarackta.
