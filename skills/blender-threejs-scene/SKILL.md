---
name: blender-threejs-scene
description: >-
  End-to-end multi-stage production workflow for building high-fidelity 3D games,
  racing courses, architectural walkthroughs, and interactive WebGL scenes modeled
  in Blender and rendered in Three.js at 30–60+ FPS. Use when the user wants to
  create a Blender + Three.js 3D scene/game from scratch (especially real-world
  locations), build a visual reference plan with photos and SVG maps, align specs
  before parallel swarm modeling, add a Look-Dev parameter control panel with
  JSON export, or run a video-review AAA upgrade and FPS optimization loop.
---

# Blender + Three.js 3D 场景/游戏全流程制作技能

将高保真 3D Web 项目拆解为 **6 个带门禁（Gate）的闭环阶段**：先用真实参考图与 SVG 地图钉死空间真值，再通过需求访谈锁死设计与性能预算，随后并行生产与视觉自检，最后借助 Look-Dev 面板和录屏复盘把画质从 80 分拉到 99+ 分并稳住帧率。

> 详细提示词模板见 [prompts.md](./references/prompts.md)；Blender 导出契约、WebGL 性能红线与 Look-Dev 面板规范见 [performance-and-lookdev.md](./references/performance-and-lookdev.md)。

---

## 执行总原则

1. **先真值、后建模**：未经参考图与尺度确认，不要直接让多个代理凭印象生成 3D 资产。
2. **先对齐、后并行**：在启动多智能体并行建模前，必须先和用户确认光照、风格、玩法与 FPS 预算并落盘 `docs/design-spec.md`。
3. **硬守性能红线**：默认实时动态光源 **≤ 3 盏**（严禁给每盏路灯/窗户放 `PointLight`），重复物体一律用 `THREE.InstancedMesh` 或静态合批；详情见 [performance-and-lookdev.md](./references/performance-and-lookdev.md)。
4. **视觉闭环验收**：每个关键里程碑必须实际运行网页、截屏或录屏，并与仓库中的真实参考图对比，不得仅凭代码编译通过就宣告完成。

---

## 标准 6 步流程

### Step 0：地理 / 路线与可行性调研（对真实地点不够熟时执行）

**适用条件**：项目基于真实世界路线/地标/街区（如阿姆斯特丹运河快艇竞速）；若为纯架空场景，则改为空间动线与关卡节奏调研。

1. 调研 2~3 套候选真实路线或场地方案，核算真实尺度、单圈/漫游时长（例如单圈 ~60 秒）与核心地标密度。
2. 评估视觉节奏变化（宽阔水面 vs 狭窄弯道、桥梁净空、标志性立面）及 WebGL 目标帧率（30/60 FPS）可行性。
3. 输出 `docs/route-research.md`，给出推荐方案并等待用户选定。

**门禁**：用户确认最终路线/场地范围、核心地标清单与目标 FPS。

---

### Step 1：视觉参考资料库与全景规划（Visual Grounding）

1. 将整个赛道/场景划分为带编号的分区（Zone 1..N），统一物理尺度 `1 Blender Unit = 1 Meter`，确定世界原点、宽度、标高与关键机位。
2. 明确所需的外部真实数据源（Wikipedia / Wikimedia Commons、OpenStreetMap、Google Street View Static API 等）。若需要 API Key，先向用户说明用途并请求提供。
3. 拉取覆盖所有分区与核心地标的真实参考图，存入 `references/streetview/` 与 `references/style/`。
4. 为**每一段赛道 / 建筑的每一个主要立面与角度**生成清晰的 SVG 矢量地图/剖面图，存入 `references/maps/`。
5. 汇总空间坐标、分区表、地标清单与机位索引写入 `docs/reference-plan.md`。

**门禁**：`docs/reference-plan.md`、`references/maps/*.svg` 和实景照片均已落盘，足以作为后续建模与视觉比对的唯一真值。

---

### Step 2：深度需求对齐（推荐配合 `/grill-me`）

1. 若用户尚未执行 `/grill-me`，主动发起结构化访谈（或建议用户触发 `/grill-me`），逐项确认：
   - **时间与氛围**：黄金时刻 / 黄昏 / 夜景 / 阴雨 / 薄雾。
   - **视觉风格**：写实照片级 vs 风格化；核心 Hero 地标清单 vs 模块化复用街区。
   - **交互与玩法**：操控键位、载具/角色物理手感、相机模式、水面/粒子/音效、HUD 要素。
   - **性能与管线**：目标 FPS（30 还是 60）、Draw Call / 光源红线、Draco/纹理压缩与烘焙策略。
2. 将最终确认的规格固化为 `docs/design-spec.md`。

**门禁**：所有设计决策与性能红线已在 `docs/design-spec.md` 中无歧义定稿。

---

### Step 3：多智能体并行建模与视觉验收（Swarm / 并行分工）

> 当用户已发起 `/swarm` 或明确要求启动蜂群并行制作时，按以下角色与模型分工编排；否则建议用户使用 `/swarm`（可直接提供 [prompts.md](./references/prompts.md) 中的 Step 3 模板）。

1. **先建骨架（Blockout）**：Coordinator 先建立统一坐标系、路径骨架、公共目录与 `web/` 最小可运行框架，再并行分派任务，防止多代理各自建模比例/原点打架。
2. **异构模型与角色分工**：
   - **Builders（高思考模型，如 Neon · High Thinking）**：按互不重叠的分区/模块并行执行——Blender MCP / `bpy` 脚本建 Hero 地标、模块化建筑群、桥梁、载具与环境资产并规范导出 `.glb`；Three.js 侧实现场景加载、水面着色器、操控物理与合批优化。
   - **Verifiers（中等思考模型，如 Carbon · Medium Thinking）**：独立负责启动本地应用、沿 `docs/reference-plan.md` 的固定机位与路线截屏（存入 `qa/shots/`），并逐张与 `references/` 实景图和 SVG 地图进行视觉对比，同时核验控制台零报错、Draw Calls、实时光源数与实测 FPS。
3. **硬性完结条件**：发现浮空、穿模、Z-fighting、贴图丢失、比例失真、风格割裂或低于目标 FPS 时，打回对应 Builder 修复并重新验证，**未达到高还原度且稳帧前不得收尾**。

**门禁**：可运行的完整 3D 场景已组装，全分区截图与 `references/` 高度吻合，零运行期报错且 FPS 达标。

---

### Step 4：Look-Dev 精细调参面板（80 分 → 99 分）

AI 很难靠文字盲调出最舒服的电影级光影平衡，这一步通过实时滑块把“最后 15% 的质感微调”交给用户，再固化回代码：

1. 按 [performance-and-lookdev.md](./references/performance-and-lookdev.md) 的规范，在 Three.js 应用中接入实时调参面板：
   - 按 **`G`** 键切换调参面板显示/隐藏。
   - 按 **`H`** 键一键隐藏**全部 UI（含 HUD、小地图与 FPS 浮层）**，供纯净观感审查与录屏。
   - 滑块按 5 大类精细分组：**独立光源、独立自发光元素、材质/表面组、大气与雾效、后处理（Exposure/Bloom/DOF/Vignette）**。
   - 提供 **`Copy JSON`** 按钮与 **`Reset Defaults`** 按钮。
2. 邀请用户在浏览器中实时微调参数，点击 `Copy JSON` 并把配置贴回对话。
3. 将用户发回的 JSON 写死为项目的默认渲染配置。最终验收满意后，按用户要求移除调试面板或隐藏至 `?debug=1` 开关后。

**门禁**：用户调优后的 JSON 已成为默认视觉预设，且 `H` 键可输出无 UI 纯净画面。

---

### Step 5：录屏复盘、AAA 升级计划与性能调优循环

静态截图难以暴露动态问题（过桥穿模、水面周期闪烁、转弯掉帧、LOD 突变）。

1. 让用户按 `H` 隐藏全部 UI 后录制一段完整跑圈/多角度漫游视频（或通过自动化脚本录制），保存到 `qa/recordings/`。
2. 逐帧审阅视频，执行双维度审计：
   - **视觉 Bug 与还原度**：对比 `docs/reference-plan.md` 与 `references/`，列出所有穿帮、穿模、光影瑕疵、材质失真、构图薄弱点及 10/10 细节增项（如尾浪泡沫、倒影、轮廓剪影、环境叙事道具）。
   - **性能剖析与提帧**：显式审计实时光源数量（警惕代理悄悄加了过多 `PointLight`/`SpotLight`）、Draw Calls、阴影贴图开销、纹理/网格压缩与后处理开销，提出**不降画质前提下的提帧方案**。
3. 输出按优先级排序的 `docs/aaa-upgrade-plan.md`。
4. 经用户确认后，执行新一轮 `/swarm`（或并行修复）落地升级计划并重新验证；循环直至画质达到 10/10 且全程 FPS 稳定达标，最后清理调试面板并完成构建。

---

## 仓库标准结构速览

```text
docs/        # route-research.md / reference-plan.md / design-spec.md / aaa-upgrade-plan.md
references/  # maps/*.svg / streetview/* / style/*
blender/     # scripts/*.py / scenes/*.blend / exports/*.glb
web/         # Three.js 前端（src/scene, gameplay, postprocessing, debug）
qa/          # shots/* / recordings/*
```
