# 2026-11-19 · EasyFix: de-graining nodes for MiniMax H3 Image

[中文](README.md) | **English**

![EasyFix comparison: jaguar, 1:1 source pixels](https://raw.githubusercontent.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix/a73c53594cd8c362736b69c24814e948a2730fcf/assets/crop_jaguar.jpg)

*Images from the author's repo (Apache-2.0): plain H3 Image on the left, EasyFix on the right, 1:1 crops of the source pixels.*

## What it is

Plain MiniMax H3 Image text-to-image often leaves a layer of grainy speckle on fine texture such as
skin, fur and stone. PedroMarinhoDev made a set of ComfyUI nodes that removes it without touching
the prompt or adding post-processing: they change **the sampling itself**.

## Original source

- Original post: [Photogenic Weekend on X](https://x.com/i/web/status/2123455858478883030)
- Repo: [PedroMarinhoDev/ComfyUI-H3-Image-EasyFix](https://github.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix) (Apache-2.0, released 2026-11-19)
- Author's demo: same-seed before/after pairs at 16 MP and 1:1 crops in the repo README, plus a ready T2I workflow: `workflows/H3 Image EasyFix - T2I.json`

| Full image | 1:1 crop |
|---|---|
| ![](https://raw.githubusercontent.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix/a73c53594cd8c362736b69c24814e948a2730fcf/assets/compare_jaguar.jpg) | ![](https://raw.githubusercontent.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix/a73c53594cd8c362736b69c24814e948a2730fcf/assets/crop_lion.jpg) |

## How it works

| Node | What it does | Suggested setting |
|---|---|---|
| H3 Image Steering | On the first one or two steps, nudges the model toward what it draws when an empty picture is added to the prompt, which gives cleaner texture; leaves edit mode (reference pictures) alone | strength 0.7, step 0 only |
| H3 Image Re-Noise Sampler | On chosen steps of H3's official 6-step schedule, takes the model's predicted finished image and adds fresh noise back, so the model redraws fine texture instead of keeping the grain it settled on early | plan `RNmid` (SSRRRS), s_noise 0.85–0.95 |
| Resolution Selector | ComfyUI's own selector stops at 16 MP; this one goes to 256 MP | H3 is trained for 4–20 MP |

My reading (not the author's words):

- **Where the grain comes from.** H3 Image takes only 6 steps, each a big jump, so fine texture is fixed in the first few steps and the later steps have no room to smooth it out; it stays behind as grain.
- **Why re-noising helps.** Adding noise back wipes part of the high-frequency detail already settled, so the following steps draw it again. It is what ComfyUI's `lcm` sampler does on every step, applied here only to the middle three: the early steps keep the composition and the last step finishes. It is still 6 steps, so no extra compute.
- **Why steering helps.** The author found that putting an empty picture in the prompt gives cleaner texture, and applies that difference directly on the first step, without paying for a real reference image. The repo ships a precomputed file under 1 MB, `data/vmproj_all6.safetensors`; my guess is that it holds this direction. Because it acts on the very first step, the composition shifts too.

## Why it is worth a look

- **A hosted API cannot do this.** MiniMax's hosted H3 Image exposes only the prompt, the aspect ratio and a resolution tier (1k / 2k / 4k), with prompt rewriting always on; steps, sigmas and model patches are out of reach. The fix only runs in ComfyUI on the open weights.
- **It changes sampling, not post-processing.** Upscaling or denoising patches a finished image after the grain is drawn; here the model draws less grain in the first place. "Few-step model with rough detail → re-noise the middle steps" carries over to other distilled models.
- **Solid material.** Same-seed full-image pairs, 1:1 source-pixel crops, parameter notes, a ready-to-import workflow and tests, so it is easy to check against.
- **Things to watch (from the author's images, not my own run):** the composition changes at the same seed too (in the jaguar pair the foreground branch is gone and the pose differs); the fixed version is softer overall, which people who like a crisp, grainy photo look may not count as an improvement. All the author's pairs are 16 MP; the README does not say whether the grain is as visible at lower resolutions.
