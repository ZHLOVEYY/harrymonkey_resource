# 2026-11-20 · HairMesh：在 Blender 里画曲线做二次元头发

**中文** | [English](README.en.md)

![HairMesh 作者演示：曲线与转好的网格之间来回切换](https://raw.githubusercontent.com/riel-gab/hairmesh/3b8e9fe634a7994dfbf68b31c348672401531625/docs/img/overview.gif)

*图来自作者仓库（`docs/img/overview.gif`，GPL-3.0-or-later）：左边是画好的引导曲线，右边是转成网格后的头发，在 Live / Baked 之间切换。*

## 这是什么

一个免费的 Blender 插件：在角色的头上**画几根引导曲线**，相邻两条曲线之间自动拉出一张"墙"，
一排墙就是一撮头发，最后把这撮转成**环线均匀的四边形网格**。

和"发卡"（带 alpha 贴图的扁平面片）是两种东西——它出的是**实心发块**。

作者本人是 riel（@koankitsu），代码 GPL-3.0-or-later。这是 catarackta 的浏览器版
"Stylized HairMesh Creator" 的授权移植版，方法和原始应用都是原作者的。

## 原出处

- 原帖：[riel 在 X 上的发布帖](https://x.com/koankitsu/status/2117606549652902035)（2026-11-03）
  「HairMesh is out! A free Blender add-on: draw curves over a head, get clean quad hair meshes.
  Port of Stylized HairMesh Creator by @CataRackta, made with his permission.
  Pay what you want: free is fine, tips help keep it updated 🧡」
  （4.2K like / 132K 浏览）
- 下载页：[ko-fi.com/rielart/shop](https://ko-fi.com/rielart/shop)（作者自己定价，可以选 0）
- 仓库：[riel-gab/hairmesh](https://github.com/riel-gab/hairmesh)（GPL-3.0-or-later，
  2026-11-08 建仓，2026-11-20 时 70 star）
- 原始应用：[Stylized HairMesh Creator](https://catarackta.netlify.app/)（浏览器版，
  catarackta 的原创方法）
- 文档：仓库里的 `docs/`（getting-started / workflow / tools / shortcuts / troubleshooting）
- 作者的演示：上面那张 `overview.gif`；`docs/img/` 下还有画墙、转换预览、Live/Baked 切换
  等分步截图
- 第三方介绍：[80 Level 的报道](https://80.lv/articles/free-blender-tool-for-creating-stylized-anime-hair)（2026-11-10）
- 同类报道：[ModelingTechNote 的日文介绍](https://modelingtechnote.com/2026/11/04/hairmesh-blender/)（2026-11-04）

![作者演示：两条曲线之间拉出一张墙](https://raw.githubusercontent.com/riel-gab/hairmesh/3b8e9fe634a7994dfbf68b31c348672401531625/docs/img/gs-wall.png)

*图来自作者仓库（`docs/img/gs-wall.png`，GPL-3.0-or-later）：选中两条曲线之后，
`Shift+RMB > Walls/Lock > Create Wall` 拉出来的"墙"。*

## 它怎么做到的

| 部件 | 做什么 | 出处 |
|---|---|---|
| 引导曲线（guide curve） | 在头顶逐点或自由手绘画线，锚点吸在头表面上；**曲线是源文件**，网格只是结果 | `docs/workflow.md`「The idea」 |
| 墙（wall） | 两条相邻曲线之间拉出的曲面；一排墙 = 一撮 lock | 同上 |
| Convert / Confirm | 把勾选组里的 lock 烘成四边形网格，环线按 Loop Step 均匀分布；改曲线再 Convert 只重建变了的几撮 | `docs/workflow.md`「Conversion」 |
| Group + Tick | 哪几撮变成哪个 mesh（Tick Top Groups = 顶层组各出一个） | 同上 |
| Guides / Crowns | 引导环（控制环线走向）、发旋与分缝结构 | 同上「Guides」「Crowns」 |
| Symmetry | 一侧建模，另一侧镜像 | 同上 |
| Modifiers | tube / mask / thickness / twist / noise / curls / fill / density | 同上「Modifiers」 |

我的理解（不是作者原话）：

- **它出的是"实心发块"，不是发卡。** 这两件事在二次元/卡通渲染里差别很大：实心发块没有
  alpha，剪影干净，描边（inverted hull）沿着发块边缘走而不是沿卡片矩形走；发卡在卡通渲染里
  反而更贵（排序闪烁、描边难看）。所以这个工具瞄准的是**卡通头发的标准做法**，不是发卡流程。
- **它只到"几何"这一步。** 转换出来的 mesh **不带 UV**，也没有材质、骨骼、权重、二次动画。
  搜遍整个仓库没有一处生成 UV 的代码，`from_pydata` 建出来就是顶点加面。换句话说
  "一键转 mesh"离"一键出资产"还差 UV、贴图、绑骨这三样。
- **它是一个可以脚本驱动的纯确定性工具。** 整条链是几何计算，没有模型、没有采样，
  同一组输入永远同一结果。操作符都留了非交互入口（`draw_curve(points_json=…)`、
  `create_walls`、`convert`、`confirm_conversion`），所以可以无头批量跑。

## 为什么值得看

- **免费，而且补的是卡通头发这条线上最缺的一环。** 同一时间点的其他 Blender 头发插件
  基本都做**发卡**（Hair Tool $52、StrandKit $90、HairTG-Cards $49、Simple Hair Cards
  $15、GBH Tool $10），做**实心发块**的免费工具几乎只有它。
- **最接近的付费对手**是 [Stylized Hair PRO](https://superhivemarket.com/products/stylized-hair-pro)（$22，
  MIT）：截面自由、带 UV、带 Hair Dynamics、还能做辫子。功能更全，但要花钱。
  再往前是 GBH Tool（$10–15，功能最全，含自动权重和发卡贴图），但它 2024-11 之后就没更新，
  用户报告在 Blender 5.1 上直接崩。
- **真正的行业做法其实两个插件都不是。** 卡通角色的头发大部分是**手搓**，或者拿
  [VRoid Studio](https://vroid.com/en/studio) 的发块改（VRoid 的头发本身就是实心发块，
  pixiv 条款允许商用、不用署 pixiv 的名，但**不是 CC0**，单项条款要看）。
  工具省掉的是"抠拓扑"那一步，省不掉造型和上色。
- **顺带两个能补它的免费插件**：MT Hair Taper（把发块末端收尖，HairMesh 的 Tips 做不了
  这种自然收尖）、Draw-Hair（沿引导网格画线并自动吸附）。
- 条件：需要 **Blender 5.1 或更高**；`Detail Proxy` 是开后改变老项目环线排布的迁移开关。

## 限制

- 不产 UV、不产材质、不产骨骼权重、不做 LOD / 阴影卡 / alpha 发片。
- 只做实心发块。写实发丝是另一类工具的活。
- 只有 Blender，没有 Maya / Houdini / UE 版本。
- 是个移植版：作者明说未来更新会集中在 Blender 专属的改进上，方法本身属于 catarackta。
