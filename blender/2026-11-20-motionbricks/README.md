# 2026-11-20 · MotionBricks：实时生成角色动作的补间模型

**中文** | [English](README.en.md)

![MotionBricks 演示：UE5 里的角色与机器人](https://media.githubusercontent.com/media/NVlabs/motionbricks/54fc563aeaaf819a753d72cc9fdc6713989cdd43/docs/media/teaser.jpg)

*图来自作者仓库（docs/media，CC-BY-4.0）：上半是 UE5 里带护盾的角色与白色人形，下半是 Unitree G1 机器人在实验室里做动作。*

## 这是什么

一个**在运行时实时生成角色动作**的模型。给它角色"最近 4 帧长什么样"（context）和"它要去哪 1–4 个姿势"（target），它把中间那段动作编出来。

和"生成一段动作"是两回事：它不做文生动作、不做视频转动作，它做的是**补间**——你给首尾两个关键帧，中间那 0.6 到 1.9 秒由它编，时长也由它自己决定。

一次生成的量是 6–16 个 token，每个 token 4 帧，30 Hz。播完把最后 4 帧当成下一轮的 context，串起来就是连续动作。

![生成与播放的循环：目标姿势 + 上下文姿势 → 生成 → 播放 → 记录 → 下一轮上下文](https://media.githubusercontent.com/media/NVlabs/motionbricks/54fc563aeaaf819a753d72cc9fdc6713989cdd43/docs/media/generation_flow.png)

*图来自作者仓库（docs/media，CC-BY-4.0）：这就是它的全部运行流程。*

## 原出处

- 原帖：[NVIDIA Game Dev 在 X 上的发布帖](https://x.com/NVIDIAGameDev/status/2123138842375107057)（2026-11-18）
  「Trained on 350,000+ motion clips, MotionBricks generates character motion in real time from target poses.」
  另有一条更早的官方介绍：[NVIDIA AI 的帖子](https://x.com/NVIDIAAI/status/2065196536276173306)（2026-06-11）
  「One open model. 350,000+ motion clips. 15,000 FPS.」
- 作者主页：[nvlabs.github.io/motionbricks](https://nvlabs.github.io/motionbricks/)（SIGGRAPH 2026 项目页，含 2 分 40 秒 UE5 无剪辑演示）
- 论文：[MotionBricks: Scalable Real-Time Motions with Modular Latent Generative Model and Smart Primitives](https://arxiv.org/abs/2604.24833)（ACM TOG / SIGGRAPH 2026）
- 仓库：[NVlabs/motionbricks](https://github.com/NVlabs/motionbricks)（代码 Apache-2.0）
- 模型：[nvidia/MotionBricks on Hugging Face](https://huggingface.co/nvidia/MotionBricks)（NVIDIA Open Model Agreement，SOMA 与 G1 的 SafeTensors checkpoint）
- 作者的演示：项目页的 UE5 无剪辑演示、机器人演示、Smart Primitive 搭建演示；仓库 `docs/media/` 下的 GIF 与截图
- 社区：[Atomic 在 X 上的插件演示](https://x.com/i/web/status/2123694448647590018)（2026-11-20，自制 Blender 插件，未开源）

## 它怎么做到的

| 部件 | 做什么 | 作者给的数字 |
|---|---|---|
| root 模块 | 先预测这次过渡要几帧、骨盆沿什么路径走 | 时长由模型自己决定，范围 6–16 token |
| pose 模块 | masked transformer，在根轨迹 + 约束下预测动作 token | 16 层，宽度 1024 |
| 解码器 | VQ-VAE，把离散 token 解回连续的关节旋转与位置 | 8 个 codebook，每个 10 个码 |
| Smart Primitive | 把动作做成可拼的积木：交互盒 + 目标姿势 + 动作序列 | 导航和物体交互各一套，JSON 文档 |

模型有两个骨架，共用同一套代码，只差姿势布局：**SOMA**（30 关节人形）和 **Unitree G1**（34 关节机器人）。一个模型覆盖 35 万段以上的动作片段，论文里报的是 15,000 FPS、2 ms 延迟。

![Smart Primitive 编辑器](https://media.githubusercontent.com/media/NVlabs/motionbricks/54fc563aeaaf819a753d72cc9fdc6713989cdd43/docs/media/smart_primitive_editor.png)

*图来自作者仓库（docs/media，CC-BY-4.0）：Smart Primitive 编辑器。右侧层级是动作积木，下方 Sequences 里放 Entry / Action / Exit，每个 Action 可以指定目标姿势来自哪一段 clip、约束速度、要不要锁根节点。*

![状态机：Idle / Locomotion / Interaction](https://media.githubusercontent.com/media/NVlabs/motionbricks/54fc563aeaaf819a753d72cc9fdc6713989cdd43/docs/media/state_machine.png)

*图来自作者仓库（docs/media，CC-BY-4.0）：它和传统状态机的关系。蓝色是模型生成的，黄色是固定 clip。Idle 和 Locomotion 之间切换靠输入，Interaction 由 Smart Primitive 触发。*

我的理解（不是作者原话）：

- **为什么它不是"动作生成器"而是"补间器"。** 约束只加在两头：开头 4 帧、结尾最多 4 帧，中间那段完全是模型按训练数据的先验"编"出来的。所以它能补的是"从 A 到 B 怎么过去"，不能告诉你"这个人走路是什么风格"——风格得由训练数据和 smart primitive 里的 clip 决定。
- **它替换的是动画状态机里最难写的那部分。** 传统做法是"状态 × 过渡"的组合爆炸：走 → 跑 → 停 → 被撞 → 坐下去，每个组合要么有专门 clip，要么手写过渡条件。它把这些组合交给一个模型，状态之间只需要声明"目标姿势在哪"。
- **Smart Primitive 是这套东西里最值得单独学的部分，跟神经网络无关。** 让场景里的物体（椅子、栏杆、箱子）自己带一组关键帧和交互范围，角色只负责走过去对上位置。用普通动画状态机 + IK 也能实现这个思路，只是没有模型补中间。
- **"实时"这个前提是 NVIDIA 硬件给的。** 官方 runtime 用 TensorRT，README 写明"requires an NVIDIA GPU"，demo 在 RTX 4090 上测的。<!-- privacy-scan: allow — 作者公开的测试显卡，不是本人的设备 -->
  仓库自己给的表是 SOMA FP32 单次 2.50 ms、FP16 1.28 ms（batch 1，同一张卡，Windows）。
  不过模型本身是 ONNX，文档里明确写了可以用 ONNX Runtime 跑，张量契约全公开。

## 为什么值得看

- **它是第一个把"角色动作过渡"整件事交给模型并且放出权重的项目。** 论文的措辞是"no foot-locking, no blending, no collision detection, no hand-authored transitions"，UE5 演示 2 分 40 秒不剪辑，全部动作同一个模型出来。
- **接口是工程友好的。** 不是文本也不是标签，是关键帧约束：8 个槽位（4 个 context + 4 个 target）+ 三个 mask，张量形状全部写死在文档里，输入输出名字都给全了。
- **零样本。** 新任务不用重新训练、不用打标签，作者的说法是"像搭积木一样拼"。
- **不只做动画。** MotionBricks 现在是 NVIDIA GR00T 全身控制里的动作生成层，能驱动真机 Unitree G1。
- **Blender 侧已经有三个能用的第三方插件。** NVIDIA 自己的仓库里**没有一行 Blender 代码**（我查过仓库全文，没有 blender / mixamo / rigify 字样），但社区已经补上了这一段：

  | 插件 | 做什么 | 许可 / 状态 |
  |---|---|---|
  | [toyxyz/toyxyz-motion-ai-tool](https://github.com/toyxyz/toyxyz-motion-ai-tool) | Blender 里用 Kimodo、ARDY、MotionBricks 生成和编辑 SOMA 动作，运动块 + 姿势关键帧 + 路径，最后导出 FBX；带一个 Windows 伴侣程序跑模型 | GPL-3.0，52 star |
  | [Ciellllllllll/motion-creator](https://github.com/Ciellllllllll/motion-creator) | 指定首尾姿势 → 生成中间动作 → 存成 Mixamo 骨骼的 FBX；可固定手/脚/躯干/头，加 root 骨，导出脚步落地的 JSON 事件 | 未标许可，README 日文 |
  | [hyun2xyz/motionbricks-blender](https://github.com/hyun2xyz/motionbricks-blender) | 把 MotionBricks 生成的 `.npz` 当作动画角色导入 Blender，另附走位脚本和录制器 | GPL-3.0，16 star |

  另有 [Atomic 在 X 上演示的自制 Blender 插件](https://x.com/i/web/status/2123694448647590018)（2026-11-20），说正在做"一键重定向到 Mixamo 和 Rigify"——**那个插件没有开源，也没有下载链接**，帖子当时只有十来条浏览，所以这条路线还没落地。

  值得单独说一句的是 **motion-creator 已经实现了 MotionBricks → Mixamo 骨骼 FBX 导出**，也就是"把模型动作接到现成游戏角色上"这一步，社区已经有人做完了，不需要等 Atomic 的那个插件。

  但这三个插件**都要 Windows + NVIDIA 显卡**（官方 runtime 走 TensorRT），所以对没有 N 卡的人，这条路目前还是堵着。

- **要注意的地方（看作者自己的材料得出的）：**
  - 官方 runtime 跑不了非 NVIDIA 的卡，TensorRT 是硬性要求；仓库里也没有 FBX/glTF 导出，BVH 只有读没有写。
  - 自带的 38 个示例动作片段是 **NVIDIA Sample Data Evaluation License**：只允许"评估和测试 NVIDIA 技术"，不能发行、不能放进自己的游戏。更宽的授权要去找数据集方（BONES-SEED）。
  - 模型权重是 NVIDIA Open Model Agreement，可商用，但要读它的条款。
  - SOMA 骨架只有 30 关节，手指几乎不保留，做手部精细动作不够用。
  - 三个社区插件都以 Windows + NVIDIA 卡为前提；其中一个（motion-creator）仓库里没有 LICENSE 文件，用之前要自己确认授权。
