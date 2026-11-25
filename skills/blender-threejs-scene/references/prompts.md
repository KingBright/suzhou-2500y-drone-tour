# 标准提示词模板库（Step 0 → Step 5）

以下模板保留了经过实战验证的英文核心指令（对多智能体与视觉模型最稳），并将可变部分抽象为 `[占位符]`，可根据具体项目直接套用。

---

## Step 0：真实路线 / 场景调研

```text
Make a [game/experience, e.g., racing game] where I [core loop, e.g., race through the Amsterdam canals on a speedboat].
[Pacing target, e.g., A lap should take about 1 minute.]
Everything around the [course/scene] should be built in Blender, exported and rendered in Three.js, and run in the browser at [30/60] FPS minimum.

Can you first do some research on what would be a suitable real-world [route/location] to base this on?
Bonus points if it goes past iconic landmarks and offers varied sightlines, architecture, and pacing.
Present 2–3 candidate options with real-world distances, landmark lists, and your recommendation in docs/route-research.md.
```

---

## Step 1：视觉参考资料库与全景规划

```text
Build an extensive visual and spatial plan for the [route/scene] in docs/reference-plan.md and references/.
Include:
1. Lots of real-world reference images covering every zone and landmark (pull from Wikipedia/Wikimedia Commons, OpenStreetMap, Google Street View, etc.). Figure out what reference data you need to pull from—maybe Street View APIs—and tell me if you need an API key from me.
2. Clean SVG maps and elevation/layout diagrams of every [segment of the course / angle of the building], with exact 1 unit = 1 meter dimensions, landmark coordinates, clearances, and camera viewpoints.
Save all assets cleanly under references/ so builder and verifier agents can compare renders directly against them.
```

---

## Step 2：深度需求对齐（`/grill-me`）

```text
/grill-me Before we start modeling in Blender or coding in Three.js, interview me to finalize every open design decision for [Project Name] (lighting/time of day, visual style, interaction/controls, camera, hero landmarks vs. modular assets, water/atmosphere, and FPS/performance budgets). Once aligned, write the final spec to docs/design-spec.md.
```

---

## Step 3：多智能体并行建模与视觉验证（`/swarm`）

```text
/swarm orchestrate a swarm to build out [Project Name] per the discussion in this thread, docs/reference-plan.md, and docs/design-spec.md.
Use Neon subagents on high thinking for parallel Blender modeling, asset pipeline, and Three.js engineering, except all verifier agents—they should be Carbon on medium thinking.

Hard requirements:
- Enforce the WebGL FPS budget (<= 3 real-time lights; use emissive + bloom or baked lighting instead of spawning per-lamp PointLights; use InstancedMesh for repeated props; keep browser performance >= [30/60] FPS).
- Verifiers must launch the build, capture multi-angle screenshots across every zone, and compare the build directly against the reference images and SVG maps in references/.
- Don't complete the task until the scene looks extremely faithful to the references and runs smoothly with zero console errors.
```

---

## Step 4：Look-Dev 精细控制面板（80 分 → 99 分）

```text
Add a real-time Look-Dev control panel (press G to toggle) with fine-grained sliders grouped by category for:
- every individual light
- every emissive element
- every material / surface group
- atmosphere / fog / sky
- post-processing settings (exposure, bloom, DOF, vignette, color grading, etc.)

Add a "Copy JSON" button so I can paste my favorite setup back to you to set as the default, a "Reset Defaults" button, and a hotkey (H) to hide ALL UI (including HUD and stats) for clean viewing and video recording.
```

固化参数与收尾移除提示词：

```text
Here is my finalized Look-Dev JSON preset:
[paste JSON]
Please bake these values in as the new default scene settings, verify the live render matches, and [remove the debug panel / gate it behind ?debug=1] for the clean build.
```

---

## Step 5：录屏复盘、AAA 升级计划与性能调优

```text
Carefully review this video ([path/to/video]), check it for visual bugs, and compare all angles to our reference plan in docs/reference-plan.md and references/.
Draft a AAA upgrade plan (save to docs/aaa-upgrade-plan.md) with specific fixes that will make this scene an absolute 10/10.
Also identify how we can make this run at higher, steadier FPS without losing quality in the scene (specifically audit real-time light counts—make sure we didn't add too many lights—draw calls, instancing, geometry merging, shadow cost, texture/mesh compression, and post-processing passes).
```

审批计划后再次发起 `/swarm`：

```text
/swarm execute docs/aaa-upgrade-plan.md. Use Neon subagents on high thinking for implementation and Carbon subagents on medium thinking for visual & FPS verification. Capture updated screenshots across all fixed angles and verify higher FPS before completing.
```
