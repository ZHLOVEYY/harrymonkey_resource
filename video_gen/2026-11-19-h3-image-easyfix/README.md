# 2026-11-19 · MiniMax H3 Image 去颗粒节点 EasyFix

**中文** | [English](README.en.md)

![EasyFix 对比：美洲豹 1:1 原图像素](https://raw.githubusercontent.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix/a73c53594cd8c362736b69c24814e948a2730fcf/assets/crop_jaguar.jpg)

*图片来自作者仓库（Apache-2.0），左边是普通 H3 Image，右边是 EasyFix，1:1 原图像素裁切。*

## 这是什么

MiniMax H3 Image 直接文生图时，皮肤、毛皮、石头这类细纹理常常带一层颗粒斑点。
PedroMarinhoDev 做了一组 ComfyUI 节点，不改提示词、不加后处理，改的是**采样过程本身**，把这层颗粒压下去。

## 原出处

- 原帖：[Photogenic Weekend 在 X 上的介绍](https://x.com/i/web/status/2123455858478883030)
- 仓库：[PedroMarinhoDev/ComfyUI-H3-Image-EasyFix](https://github.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix)（Apache-2.0，2026-11-19 发布）
- 作者的演示：仓库 README 里的同 seed 前后对比（16 MP）和 1:1 裁切，以及一份可直接导入的 T2I workflow：`workflows/H3 Image EasyFix - T2I.json`

| 整图对比 | 1:1 裁切 |
|---|---|
| ![](https://raw.githubusercontent.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix/a73c53594cd8c362736b69c24814e948a2730fcf/assets/compare_jaguar.jpg) | ![](https://raw.githubusercontent.com/PedroMarinhoDev/ComfyUI-H3-Image-EasyFix/a73c53594cd8c362736b69c24814e948a2730fcf/assets/crop_lion.jpg) |

## 它怎么做到的

| 节点 | 做什么 | 推荐设置 |
|---|---|---|
| H3 Image Steering | 在最开始一两步，把模型往“提示词里加一张空图”时的结果推一下，纹理更干净；有参考图的编辑模式不动 | strength 0.7，只作用第 0 步 |
| H3 Image Re-Noise Sampler | H3 官方 6 步采样里，挑几步“取模型预测的成图，再加回新噪声”，逼它重画细纹理，而不是沿用早期定下的颗粒 | plan `RNmid`（SSRRRS），s_noise 0.85–0.95 |
| Resolution Selector | ComfyUI 自带的分辨率选择器上限 16 MP，这个到 256 MP | H3 训练在 4–20 MP |

## 为什么值得看

- **托管 API 做不了。** 我查了 MiniMax Design 里的 H3 Image，只开放 `prompt`、`aspect_ratio`、`resolution`（1k / 2k / 4k）三个参数，提示词改写强制开启；采样步、sigma、模型 patch 都碰不到。这个修复只能在本地 ComfyUI 跑开源权重。
- **改的是采样，不是后期。** 超分、降噪是对成图修补，颗粒已经画进去了；这里是让模型自己少画颗粒。思路可以迁移到别的少步数模型。
- **要注意的地方（看作者图得出的，没有自己跑）：** 同 seed 下构图也会变（美洲豹那组，前景树枝没了、姿势也变了），因为 Steering 动的是最早几步；修复版整体也更柔和一些。

## 如果要在我的环境跑

- 需要支持 H3 Image 的 ComfyUI；我的测试实例已是 v0.45.2，H3 Image int8 权重和 VAE 都在本地。
- 速度是瓶颈：我之前在 M2 Max 上测过，同样 6 步，4 MP 文生图约 500 秒，1 MP 约 145 秒。作者的对比都是 16 MP，在 Mac 上会非常慢，复现建议先在 4 MP 上做同 seed A/B。
