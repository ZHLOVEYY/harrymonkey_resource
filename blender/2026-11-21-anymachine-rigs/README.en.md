# 2026-11-21 · AnyMachine: making AI-generated meshes actually move

[中文](README.md) | **English**

![Stilt: a 30 m walker passing a 1.75 m figure](https://raw.githubusercontent.com/apekshik/anymachine/d5e8889eef0b33e0bbe62ddca6f713f94b154b68/stilt/renders/stilt_walk.gif)

*Image from the author's repo (MIT): Stilt, a 30 m walker, 160 parts and 104 bones, all built by one Blender Python script.*

## What it is

A 3D model from Tripo or Meshy comes out as one lump: the lid is welded to the box, the legs are fused to the body, and once you cut them apart the hinge is not on the real axis, so anything that moves clips through something.
AnyMachine is a set of experiments by apekshik: an agent (Claude Code) writes Blender Python that **treats the generated mesh as a skin**, measures where the joints are on it, rebuilds the moving parts as clean rigid geometry, gives each joint a 0-1 parameter, and then sweeps every pose with a script to prove that no part passes through another.

It is **not** a ready-made auto-rigging tool: every object gets a new script written by the agent (466 lines for the quadruped, about 2,200 for the walker). The author marks the repo "experiments": six runs, no general entry point.

## Source

- Post: [introduction on X](https://x.com/i/web/status/2124118996978942038)
- Repo: [apekshik/anymachine](https://github.com/apekshik/anymachine) (MIT); the method is in [PIPELINE.md](https://github.com/apekshik/anymachine/blob/d5e8889eef0b33e0bbe62ddca6f713f94b154b68/PIPELINE.md)
- Same author's series: AnyScene (whole sets), AnyKit (props), AnyShot (shooting the result)

| Laptop hinge 0-135° | Quadruped trot |
|---|---|
| ![](https://raw.githubusercontent.com/apekshik/anymachine/d5e8889eef0b33e0bbe62ddca6f713f94b154b68/laptop/out/laptop_hinge.gif) | ![](https://raw.githubusercontent.com/apekshik/anymachine/d5e8889eef0b33e0bbe62ddca6f713f94b154b68/quadruped/out/quadruped_trot.gif) |

*Images from the author's repo (MIT).*

## How it works

The route from a generated mesh (the author's laptop, quadruped and spider runs):

| Step | What happens | Author's example |
|---|---|---|
| 1 Generate | The reference image, and so the mesh, shows the object **opened up**: lid open, knees bent | a closed lid gives no hinge to measure |
| 2 Measure | A script measures the mesh: planes by an area-weighted median fit, the lid's direction by PCA, the hinge where the two meet; legs from side-profile bins (hip, knee) | a max-height fit doubled the deck slope; left and right legs agreed within 1-7 mm, so the measurement is real |
| 3 Keep the skin, rebuild what moves | Keep the generated surface (keys, shell), delete the lid or legs, rebuild them on the measured axes: the lid's back edge as a cylinder **coaxial** with the hinge, each leg link in its own slab with 1-2 mm gaps | the generated lid was 2.4 cm short and fused to a hinge block |
| 4 Parameters | Each joint is a 0-1 custom property, baked to a 1 s linear clip, so `seek(value)` poses it in any engine | glTF carries no drivers, so it has to be baked |
| 5 Machine check | Sweep every parameter: triangle overlaps, clamping out of range, minimum clearance, foot slip; re-import the exported GLB and compare | laptop: 0 overlaps, min clearance 0.32 mm; quadruped: 0.014 mm foot slip |

Complicated static props (a helicopter, a lifeboat) go another way: generate a six-view sheet and close-up sheets first, model part by part, compare side by side with the sheets, then do a planned second pass.

My reading (not the author's words): the point is **"cannot clip by construction" before "fix the clipping afterwards"**. Parts that are coaxial with their axis and sit in their own layer cannot touch at any angle; the sweep only proves it.

## Why it is worth a look

- **It fills the step from "generated mesh" to "a prop that moves".** Image-to-3D is cheap now, but what comes out cannot move. Usual auto-rigging (skin weights per vertex) suits bodies that bend; on a hard shell it bends the shell like rubber. For hard parts turning on axes, this is a method.
- **Acceptance is a number, not a look.** A lid has hundreds of angles and nobody checks every frame; the sweep says which frame and which two parts collide.
- **The author's own counter-intuitive finding:** do not use image-to-3D for complicated props with many parts. Their generated lifeboat "had the right outline and nothing underneath it" and was rejected on sight. A generated mesh is good to measure joints from, or for a background prop nobody walks up to.
- **Limits (from the author's material, not my own run):** soft goods only partly work, with two of three backpacks failing where controls interact; the rebuilt moving parts are plain ("legs are plain slabs"); there is no engine-side test anywhere in the repo, and the notes say the helicopter is "not yet tested in the game"; `run_all.sh` hard-codes paths on the author's machine and does not run as is.

## The tool I extracted

[`tools/overlap_check.py`](tools/overlap_check.py): a clash sweep rewritten from the idea of the author's step 5. It does not depend on his per-object scripts and works on any animated `.glb` / `.blend`.

```bash
blender -b --factory-startup -P tools/overlap_check.py -- prop.glb --all-actions --out report.json
```

- Two parts that do not touch at rest must not touch at any frame, or the check fails (exit code 1).
- Parts that already touch at rest (a tyre on the road, a wiper on glass) are only listed as "contact changed", because a turning part keeps bringing new triangles into contact; `--strict` fails those too.
- Parts that move together on one hinge (a hatch and its glass) are skipped.

Trial results: on a two-control test chest it passes with the hinge in the right place, fails with the hinge moved 6 cm into the box, and fails with the lid rotation sign flipped. On an older vehicle prop it also found a problem nobody had noticed: once the car drives off, all four tyres sink about 4 cm into the road.

A full run on a real generated mesh comes later.
