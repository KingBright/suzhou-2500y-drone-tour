# Design Spec — 一镜飞越 2500 年苏州（Suzhou 2500Y Drone Tour）

> 本文件锁定了全项目的美术、空间坐标、运镜、动态天光切换与性能红线。所有 Swarm 成员必须严格遵守。

## 1. 核心目标与体验形态
- **项目目录**：`/Users/jinliang/workspace/experiment/suzhou-drone-tour/`
- **体验模式**：
  1. **一镜到底自动无人机电影模式（默认）**：约 115 秒无缝穿越 12 站（覆盖 14+ 苏州古今标志性地标），地标处优雅慢速环绕，景点间**高速掠过切换**（Dynamic FOV `45°→82°` + Roll `±22°` + 速度流光）。
  2. **12 站一键直达**：底部优雅导航栏（分「古韵姑苏」与「现代金鸡湖」两段），点击任意景点平滑飞跃/定位至该站最佳机位，并可继续沿航线巡航。
  3. **自由无人机探索模式（Free Fly）**：一键切换 `WASD / QE` + 鼠标拖动自由穿梭整座苏州城。
  4. **动态天光切换系统**：
     - `auto`（默认）：随航线进度 `t ∈ [0, 1]` 从 **金色夕阳（寒山寺/虎丘）→ 粉紫暮色（古城五大名园/古塔）→ 蓝调璀璨夜景（穿东方之门后全金鸡湖亮灯）** 平滑实时渐变。
     - `dawn`（清晨水墨薄雾）、`golden`（金色夕阳）、`dusk`（粉紫暮色）、`night`（蓝调璀璨夜）：用户随时一键丝滑切换全城天光（1.5s 渐变插值），并支持连续时间滑块 `0.0–1.0`。
  5. **Step 4 Look-Dev 精细控制面板**：按 `G` 呼出/收起，按 `H` 隐藏包括 HUD 在内的全部 UI，支持 5 大类细粒度滑块 + **`Copy JSON`** + **`Reset Defaults`**。

## 2. Blender 建模硬规范（所有 Blender Worker 必守）
- **工具**：使用 headless CLI `/Users/jinliang/.local/bin/blender -b --python <script.py>` 批量生成并直接导出 `.glb` 到 `web/public/assets/models/<name>.glb`（同时保留脚本在 `blender/scripts/`）。
- **坐标与原点**：
  - `1 Blender Unit = 1 Meter`，glTF 导出默认 `+Y Up`（Blender 中 Z 轴向上，导出器自动转换）。
  - 每个站点模型以**本地原点 `(0, 0, 0)` 为该站点地面中心**（地面台基顶面在 `Z=0`，如需入水基础可下探至 `Z=-2.0`）。Three.js 加载时直接放置在 `world-layout.json` 对应 `anchor` 处！
  - **特别注意可穿越开口**：
    - `gate_of_orient.glb`（东方之门）：301.8m 总高，沿 X 轴东西通透（门洞开口面朝 `-X` 与 `+X`），拱门净空宽度 ≥ 60m、净空高度 40m–210m，确保无人机沿 X 轴无碰撞丝滑穿洞！
    - `panmen_canglang.glb`（吴门桥）与 `ligongdi.glb`（李公堤拱桥）：桥洞净空高度 ≥ 10m、宽度 ≥ 18m。
    - `moca_eye_of_suzhou.glb`（苏州之眼摩天轮 128m）：旋转轮盘命名节点 `FerrisWheelRotor`（含 28 个发光太空舱），枢轴位于轮心，方便 Three.js 驱动其缓慢旋转！
- **材质与自发光（Emissive）命名约定**：
  - 所有夜间亮灯元素（古塔檐灯、红灯笼、苏州中心羽翼光带、东方之门幕墙竖条灯、摩天轮外圈与太空舱、月牙穹顶轮廓灯、IFS 幕墙与鱼尾塔冠）必须使用独立带 `emissive` 的 PBR 材质，且材质名包含关键字：
    - `Emissive_Warm`（古塔/灯笼/古建暖金光 `#ffba66`）
    - `Emissive_Cyan`（现代建筑青蓝流光 `#4de2ff`）
    - `Emissive_Gold`（东方之门/IFS/摩天轮金白光 `#ffd98a`）
    - `Emissive_Accent`（霓虹紫/品红点缀 `#ff5cc8`）
  - 这样 Three.js 端只需遍历材质名就能**动态随天光（夕阳→夜景）自动点亮/调暗全部建筑灯光，并接入 Look-Dev 面板滑块**！
- **多边形与文件体积预算**：
  - 单个 Hero `.glb` 控制在 **15,000 – 55,000 三角面**、文件大小 **< 4 MB**，确保 12 站全部加载总面数 < 600K、秒开、45–60 FPS！
  - 精细度聚焦**剪影识别度与标志性建筑细部**（斗拱飞檐多层翘角、八面塔身逐层收分与塔刹、太湖石多面体镂空、苏博菱形灰瓦边线、东方之门弧形幕墙肋条与裙房未来之翼、BIG 波浪丝带屋顶、摩天轮双环钢索辐条与 28 舱、文化艺术中心月牙壳体网格、IFS 450m 鱼尾斜切塔冠）。

## 3. Three.js 渲染与性能硬红线
- **实时动态光源总数 ≤ 3 盏**（1 主方向太阳/月光带软阴影 + 1 半球天光 + 1 辅助补光；严禁创建任何多余 `PointLight`/`SpotLight`）。
- **Draw Calls < 160**（古城民居/树/桥/船/灯笼 & 现代 CBD 配楼/游船全部使用 `THREE.InstancedMesh`）。
- **色彩与后处理**：`THREE.SRGBColorSpace` + `THREE.ACESFilmicToneMapping` + 轻量 `UnrealBloomPass` + 动态大气指数雾 + 电影级微暗角。
- **DPR 限制**：`Math.min(window.devicePixelRatio, 2)`。
- **调试与验证接口**：挂载 `window.__SUZHOU_DEBUG__`（提供 `jumpToStation(index)`, `setAtmosphere(mode)`, `setTimeOfDay(t)`, `setProgress(p)`, `togglePanel(bool)`, `hideAllUI(bool)`, `getStats()`），确保 Verifier 可以自动化截取全部 12 站与不同天光模式的清晰对比图。
