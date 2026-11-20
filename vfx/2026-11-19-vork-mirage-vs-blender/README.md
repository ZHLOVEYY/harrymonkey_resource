# 2026-11-19 · vork：让 agent 用代码定义光怎么走（海市蜃楼、黑洞透镜）

**中文** | [English](README.en.md)

![黑洞旁的货船，月亮被引力透镜拉成一圈光环](https://raw.githubusercontent.com/voyager-so/vork/bc228cba5b0b3554ef97b50954bdd8f9a0ad0256/docs/images/black-hole.jpg)

*图片来自 vork 仓库的黑洞示例（`examples/black-hole/`）；货船模型基于 Yvo Pors 的 ["Corinth Cargo Transporter"](https://sketchfab.com/3d-models/corinth-cargo-transporter-7614d85856f6477ba2a603970dcbb0dd)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。*

## 这是什么

[vork](https://github.com/voyager-so/vork) 是一个给 AI agent 用的无界面 GPU 渲染器，用 Rust 和 Slang 写成，跑在 Vulkan / Metal 上，
Linux、Windows、macOS 都能用。

它的场景就是一份 JSON。材质、相机、模拟，甚至光线怎么传播，都可以用 Slang 写成小程序塞进去，
所以 agent 不用去点 Blender 的界面或预设，直接写代码出画面。原帖演示的是海市蜃楼：Blender 里没有现成的预设，
就让 agent 自己写光在热空气里怎么走。

## 原出处

- 原帖（海市蜃楼演示视频）：[Ravi Parikh 在 X 上的帖子](https://x.com/i/web/status/2123582432884789294)
- 仓库：[voyager-so/vork](https://github.com/voyager-so/vork)（Nullframe, Inc.，源码公开，不是开源；许可证叫 "vork Preview License"）
- 作者的示例：仓库 `examples/` 里有鸟群、赛博车短片、实拍素材叠特效、黑洞、蛋糕、厨房、水花。
  每个都带了场景代码和素材出处。

## 它怎么做到的

| 机制 | 做什么 | 出处 |
|---|---|---|
| 场景 JSON | 所有东西都写在一份 JSON 里，有固定的 schema，`vork check` 不用 GPU 就能先校验 | README、`packages/ts/scene.schema.json` |
| Slang 程序 | 表面着色、置换、雾、环境、相机、合成、GPU 计算都可以自己写 | `vork help programs` |
| `scene.propagation` | 一个程序决定光线每走一段之后往哪个方向拐，所以光可以走弯路；离开设定的范围后恢复走直线 | README 的黑洞一节、`examples/black-hole/propagation.slang` |
| 四档画质 | `std/previs` 布局预览、`std/draft` 快速打光、`std/final` 正式出图（默认）、`std/path` 追求准确；自定义光线传播要用 `std/path` | `vork help` |

我的理解（不是作者原话）：

- **海市蜃楼怎么来的。** 路面附近的热空气折射率比上面低，光线会朝折射率高的地方弯。用 `propagation` 写一个
  「越贴近地面折射率越低」的函数，贴地飞的光线就会被慢慢掰回天上，远处物体下面自然出现倒过来的像，不用任何后期。
  黑洞示例是同一个接口，只是把折射率换成了黑洞引力场的近似（作者写明这是数值近似，不是精确的相对论求解）。
- **为什么说"给 agent 用"。** 输入是纯文本、有 schema 可以校验、核心 API 作者说大约 2500 token 就能讲完，
  还自带一份 agent skill（`skills/vork/SKILL.md`）。这些都是为了让模型能自己写、自己检查，而不是给人用鼠标拖。

## 为什么值得看

- **Blender 预设做不出的物理光学。** 热浪、引力透镜、色散这类效果，Blender 里一般只能在后期用置换去"假装"，
  画面能扭但物理上不对（比如不会出现倒影）。vork 让你直接写光怎么走，适合做宣传片里那种一眼就能看出来的特殊镜头。
- **能让 agent 批量出画面。** 不开界面、命令行出图出视频、场景是文本能放进 git，适合让 agent 批量出转台图、封面图，
  或者每次改版自动重渲。
- **不用付费 API。** 本地有支持的 GPU（Apple Silicon，或者支持光线查询的 NVIDIA / AMD）就能免费渲染；
  没有 GPU 才需要它的付费云渲染。
- **要注意的地方（看作者材料得出的，不是自己跑的）：**
  - README 开头那组"比 EEVEE 快很多"的数字是在 NVIDIA L4 上测的，Blender 那边的时间是**推算**的。
  - 作者自己在 `benchmarks/RESULTS.md` 里写明：final 档是 8 采样 + 降噪，拿来比的 EEVEE 是 64 采样、不降噪，"是不同的工作流，不是同等画质"。仓库里的 Blender 对比脚本（`integrations/blender/benchmark.py`）默认给 Cycles 设的是自适应、最多 4096 采样。两边设置不一样，看倍数之前要先统一采样数。
  - 现在是研究预览：这个版本免费、可以商用，但不能转卖，也不能拿来做给别人用的渲染服务；以后的版本可能收费。
  - 输出是图片和视频，不进 Godot 这类实时引擎。`vork export` 能导出 glTF 资产（几何和动画），但光线怎么走这类程序只在 vork 里渲染时生效。
