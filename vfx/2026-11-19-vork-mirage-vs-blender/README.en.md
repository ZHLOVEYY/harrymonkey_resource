# 2026-11-19 · vork: a renderer where an agent writes how light travels (mirages, black-hole lensing)

[中文](README.md) | **English**

![A cargo ship beside a black hole, with a moon lensed into a ring around it](https://raw.githubusercontent.com/voyager-so/vork/bc228cba5b0b3554ef97b50954bdd8f9a0ad0256/docs/images/black-hole.jpg)

*Image from the black-hole example in the vork repo (`examples/black-hole/`); the ship is based on ["Corinth Cargo Transporter"](https://sketchfab.com/3d-models/corinth-cargo-transporter-7614d85856f6477ba2a603970dcbb0dd) by Yvo Pors, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*

## What it is

[vork](https://github.com/voyager-so/vork) is a headless GPU renderer made for AI agents, written in Rust and Slang,
running on Vulkan / Metal on Linux, Windows and macOS.

A scene is one JSON file. Materials, cameras, simulations and even how light propagates can be written as small Slang
programs inside it, so an agent produces images by writing code instead of clicking through Blender's UI or presets.
The original post shows a mirage: Blender has no preset for it, so the agent writes how light travels through hot air.

## Original source

- Original post (mirage demo video): [Ravi Parikh on X](https://x.com/i/web/status/2123582432884789294)
- Repo: [voyager-so/vork](https://github.com/voyager-so/vork) (Nullframe, Inc.; source-available, not open source; licence
  "vork Preview License")
- The author's examples: `examples/` in the repo has a starling murmuration, a cyber-car film, VFX over real footage,
  a black hole, a cake, a kitchen and a water splash, each with its scene code and asset credits.

## How it works

| Mechanism | What it does | Where |
|---|---|---|
| Scene JSON | Everything lives in one JSON file with a fixed schema; `vork check` validates it without a GPU | README, `packages/ts/scene.schema.json` |
| Slang programs | Surface shading, displacement, fog, environments, cameras, compositing and GPU compute can all be authored | `vork help programs` |
| `scene.propagation` | A program decides which way each light segment turns next, so light can travel curved paths; outside the given bounds it goes straight again | README black-hole section, `examples/black-hole/propagation.slang` |
| Four quality profiles | `std/previs` blocking, `std/draft` quick lighting, `std/final` delivery (default), `std/path` accuracy; authored propagation needs `std/path` | `vork help` |

My reading (not the author's words):

- **Where the mirage comes from.** Hot air near the road has a lower refractive index than the air above, and light
  bends towards the higher index. Write a `propagation` function with "lower index closer to the ground" and rays
  skimming the road are slowly bent back up to the sky, so an inverted image appears under distant objects with no
  post-processing. The black-hole example uses the same hook with the index replaced by an approximation of the
  hole's gravity (the author states it is a numerical approximation, not an exact relativistic solver).
- **Why "for agents".** The input is plain text with a schema to validate against, the author says the core API fits
  in about 2,500 tokens, and the repo ships its own agent skill (`skills/vork/SKILL.md`). All of it is there so a model
  can write and check scenes itself, not so a person can drag things with a mouse.

## Why it is worth a look

- **Optics that Blender presets cannot make.** Heat haze, gravitational lensing and dispersion are usually faked in
  Blender with a displace in post: the image wobbles but the physics is wrong (no inverted image, for one). vork lets
  you write how the light travels, which suits the one-glance special shots of a trailer.
- **Agents can render in bulk.** No UI, stills and videos from the command line, scenes as text that fit in git: good
  for an agent batch-rendering turntables and cover shots, or re-rendering automatically on every change.
- **No paid API.** With a supported local GPU (Apple Silicon, or NVIDIA / AMD with ray queries) rendering is free; the
  paid cloud rendering is only for machines without one.
- **Things to watch (read from the author's material, not my own run):**
  - The "much faster than EEVEE" numbers at the top of the README were measured on an NVIDIA L4, with **projected**
    Blender times.
  - The author writes in `benchmarks/RESULTS.md` that the final profile uses 8 samples + denoising while the EEVEE it is
    compared with uses 64 samples and no denoising, "different workflows, not quality parity". The Blender comparison
    script in the repo (`integrations/blender/benchmark.py`) gives Cycles adaptive sampling up to 4096 by default. The
    settings differ, so equalise the sample counts before reading any speed ratio.
  - It is a research preview: this version is free, including commercial use, but may not be resold or offered as a
    rendering service to others; later versions may be paid.
  - The output is images and video, not a real-time engine such as Godot. `vork export` writes glTF assets (geometry
    and animation), but programs such as light propagation only take effect when vork renders.
