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

我的理解（不是作者原话）：

- **颗粒从哪来。** H3 Image 只走 6 步，每一步跨度很大，细纹理在前几步就“定”下来了，后面的步数来不及把它修顺，于是留成一层颗粒。
- **Re-Noise 为什么有用。** 重新加噪等于把已经定下的高频细节擦掉一部分，让后面的步数再画一次，原理和 ComfyUI 的 `lcm` 采样器每步都重新加噪一样，只是这里只挑中间三步做，前面保构图、最后一步收尾。总步数还是 6 步，不额外花算力。
- **Steering 为什么有用。** 作者发现“在提示词里塞一张空图”画出来的纹理更干净，于是把这个差别直接作用在第一步，省掉真的喂一张参考图的开销。仓库里附带一个不到 1 MB 的预计算文件 `data/vmproj_all6.safetensors`，我猜就是这个方向。因为它动的是最早一步，构图也会跟着变。

## 为什么值得看

- **托管 API 做不了。** MiniMax 官方托管的 H3 Image 只开放提示词、画幅和分辨率档位（1k / 2k / 4k），提示词改写强制开启，采样步、sigma、模型 patch 都碰不到。这个修复只能在 ComfyUI 里跑开源权重。
- **改的是采样，不是后期。** 超分、降噪是对成图修补，颗粒已经画进去了；这里是让模型自己少画颗粒。“少步数模型细节发糙，就在中间步重新加噪”这个思路也可以迁移到别的蒸馏模型。
- **材料扎实。** 同 seed 的整图对比、1:1 原图像素裁切、参数说明、一份可直接导入的 workflow 都有，还附了测试，拿来就能对照。
- **要注意的地方（看作者图得出的，不是自己跑的）：** 同 seed 下构图也会变（美洲豹那组，前景树枝没了、姿势也变了）；修复版整体更柔和，喜欢锐利颗粒感照片质感的人未必觉得是改进。作者的对比都是 16 MP，低分辨率下颗粒是否同样明显，README 没有给出。
