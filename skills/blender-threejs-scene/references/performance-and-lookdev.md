# Blender 导出契约、WebGL 性能红线与 Look-Dev 面板规范

---

## 1. Blender → Three.js 统一资产契约

多智能体并行建模时，必须由 Coordinator 在首轮锁定以下契约，所有 Builder 严格遵守：

| 约定项 | 标准规则 | 常见错误 |
| :--- | :--- | :--- |
| **世界单位** | `1 Blender Unit = 1 Meter`（真实物理比例） | 船/建筑/桥各自按不同比例缩放 |
| **坐标系与朝向** | glTF 导出启用 `+Y Up`；可动载具统一朝向 `-Z` | 模型导入后侧翻或倒着开 |
| **原点对齐** | 场景大块按统一世界坐标原点；可复用单体按「底面中心 `(0, 0, 0)`」 | 建筑浮空、桥墩陷进河底 |
| **法线与变换** | 导出前统一 `Apply Scale & Rotation`，检查面法线朝外 | 背面剔除导致墙体消失或光照反转 |
| **色彩空间** | Three.js 启用 `SRGBColorSpace` + `ACESFilmicToneMapping`；Albedo/Emissive 用 sRGB，Roughness/Metalness/Normal 用 Linear | 画面发灰、金属变黑或过曝 |
| **碰撞与视觉分离** | 物理/碰撞走简化低模或样条路径（Spline/Bounds），不直接对高模三角面做碰撞检测 | 过桥卡死或物理每帧掉帧 |

---

## 2. WebGL 性能预算与高频掉帧避坑

### 2.1 硬性预算表

| 指标 | 30 FPS 底线 | 60 FPS 推荐目标 | 优化手段 |
| :--- | :--- | :--- | :--- |
| **实时动态光源** | ≤ 4 盏 | **≤ 3 盏**（太阳光 + 半球光 + ≤1 重点光） | **严禁批量放 `PointLight`/`SpotLight`**；路灯、窗户、霓虹用 **Emissive 材质 + Bloom** 或 **Blender 烘焙 Lightmap** |
| **投射阴影光源** | 1 盏 | **仅 1 盏**（主方向光，ShadowMap 1024–2048，紧贴视锥裁剪） | 缩小阴影相机 frustum，避免覆盖整张地图浪费纹素 |
| **Draw Calls** | < 200 | **< 120** | 同材质静态网格合并（`mergeGeometries`）；树木/路灯/栏杆/窗框/船只全部 `THREE.InstancedMesh` |
| **视锥内三角面** | < 1M | **300K – 600K** | 远景降模 + `THREE.LOD` + 视锥裁剪 |
| **像素比 DPR** | ≤ 2.0 | **≤ 1.5 ~ 2.0**（`Math.min(devicePixelRatio, 2)`） | 高分屏直接渲染 3x 会让片元计算量暴增 |
| **资产传输体积** | < 30 MB | **< 15 MB** | glTF 启用 Draco 几何压缩 + WebP / KTX2（BasisU）纹理压缩，单图 ≤ 1024/2048px |

### 2.2 AI 代理最容易引入的 5 个性能杀手（Step 3 / Step 5 必查）

1. **光源爆炸**：在循环里为每根路灯或每扇亮灯的窗户 `new THREE.PointLight()` → **立刻重构为 Emissive + Selective Bloom / 烘焙贴图**。
2. **未合批的重复物体**：几百棵树、护柱、屋顶烟囱各自独立 `Mesh` → **改为 `InstancedMesh`**。
3. **每帧动态分配对象**：在 `requestAnimationFrame` 里 `new THREE.Vector3()` / `new THREE.Matrix4()` 触发 GC 卡顿 → **模块级复用临时对象**。
4. **全屏高分辨率后处理叠加**：同时开启高采样的 SSAO + DOF + Bloom + SSR 且未降半分辨率 → **优先保留 ACES ToneMapping + 轻量 Bloom + Fog + Vignette，重效果按需降分辨率或开关化**。
5. **实时反射相机滥用**：水面使用全分辨率 `Reflector` 每帧把整个场景渲染两遍 → **优先用预设环境贴图（PMREM HDRI）+ 法线波纹 + 屏幕空间近似高光，或将反射渲染目标降到 0.25–0.5 分辨率并剔除低优先级图层**。

---

## 3. Look-Dev 精细调参面板规范（Step 4）

### 3.1 交互与快捷键

- **`G`**：展开 / 收起 Look-Dev 调参面板（默认可收起或右上角弱提示 `Press G for Look-Dev, H to hide UI`）。
- **`H`**：一键隐藏 / 恢复**全部界面元素**（含游戏 HUD、计时器、小地图、FPS 统计、调参面板），确保截屏和录屏 100% 纯净。
- **`Copy JSON` 按钮**：将当前全部参数序列化为格式化 JSON 复制到剪贴板，并弹出简短 Toast 提示“已复制”。
- **`Reset Defaults` 按钮**：一键恢复当前代码中的默认值。
- **状态微浮层**：显示实时 `FPS`、`Draw Calls`、`Triangles`、`Active Lights`（受 `H` 键统一隐藏）。

### 3.2 滑块分组与推荐 JSON 结构

```json
{
  "lights": {
    "sun": { "color": "#ffd9a8", "intensity": 2.4, "elevation": 18, "azimuth": 135, "shadowBias": -0.0004 },
    "hemisphere": { "skyColor": "#87b5ff", "groundColor": "#3a3228", "intensity": 0.75 },
    "accent": { "color": "#ffaa55", "intensity": 0.8 }
  },
  "emissives": {
    "canalHouseWindows": { "color": "#ffbe73", "intensity": 1.6 },
    "streetLamps": { "color": "#ffd28a", "intensity": 2.2 },
    "boatHeadlights": { "color": "#ffffff", "intensity": 2.5 }
  },
  "materials": {
    "water": { "color": "#163038", "roughness": 0.14, "waveScale": 1.2, "waveSpeed": 0.85, "envMapIntensity": 1.3 },
    "brick": { "roughness": 0.82, "metalness": 0.04, "envMapIntensity": 0.6 },
    "stoneBridge": { "roughness": 0.78, "metalness": 0.05 },
    "foliage": { "roughness": 0.7, "saturation": 1.0 }
  },
  "atmosphere": {
    "fogType": "exp2",
    "fogColor": "#c9d6e3",
    "fogDensity": 0.0028,
    "skyTurbidity": 6.5,
    "skyRayleigh": 1.8
  },
  "postProcessing": {
    "toneMapping": "ACESFilmic",
    "exposure": 1.08,
    "bloomEnabled": true,
    "bloomThreshold": 0.88,
    "bloomStrength": 0.35,
    "bloomRadius": 0.45,
    "dofEnabled": false,
    "dofFocus": 45.0,
    "dofAperture": 0.0002,
    "vignetteIntensity": 0.22
  }
}
```

### 3.3 发布前清理

用户确认最终 JSON 并写回默认配置后，提供两种收尾模式供用户选择：
- **彻底移除模式**：删除 `src/debug/` 调参面板代码与依赖，减小打包体积。
- **隐藏开关模式**：保留面板但仅当 URL 带 `?debug=1` 时动态懒加载（`import('./debug/lookdevPanel')`），平时零开销。
