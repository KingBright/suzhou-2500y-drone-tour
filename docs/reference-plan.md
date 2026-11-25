# Step 1：视觉参考与建筑测绘总规划（Reference Plan）

> **项目**：一镜飞越 2500 年苏州（Suzhou 2500Y Drone Tour）  
> **维护者**：`@ref-mapper`  
> **坐标基准**：严格对齐 `world-layout.json` 与 `docs/design-spec.md`（`1 Blender Unit = 1 Meter`，`+Y Up`，水面 `Y = 0.0m`，基准地面 `Y = 1.6m`，世界范围 `X ∈ [-1700, 1750]`、`Z ∈ [-950, 950]`）。  
> **服务对象**：`@blender-west`、`@blender-gusu`、`@blender-modern`、`@web-engine`、`@verifier`。

---

## 一、三大建筑级 SVG 参考图总览（`references/maps/`）

| 文件名 | 画幅 / 比例 | 核心用途与读取指南 |
| :--- | :--- | :--- |
| `references/maps/suzhou-master-route.svg` | `1840 × 1140`（等比 `1:1` X/Z 投影，含 `300m` 比例尺） | **全城 12 站顶视航线与精确世界坐标图**。完整标注大运河（`x=-1320, w=85m`）、七里山塘河（`w=28m`）、环城护城河（`[-480..380]×[-400..420], w=42m`）、平江河（`x=140, w=16m`）、金鸡湖（`cx=1030, cz=40, rx=390, rz=460`）、李公堤、干将路光流轴、全部 12 站精确 Footprint 边界框、3 个子锚点（西园寺/狮子林/苏博）、`heroView` 机位视线、慢速环绕段（金色实圈 `1× / FOV 46°`）与高速掠过段（青色虚线 `5.5–8× / FOV 82° / Roll ±22°`）。 |
| `references/maps/suzhou-elevation-lighting.svg` | `1840 × 1020`（垂直高程 `0m–480m` 线性真实比例） | **西→东航线高程剖面与 2500 年动态天光渐变图**。上方展示无人机 `6m–465m` 飞行高度曲线与各站真实地标高度（`16m–450m`），重点标注 `125m` 穿东方之门 → `60°` 贴湖俯冲至 `6m` → `8m` 穿李公堤桥洞 → `465m` 垂直冲顶回望；下方同步绘制 `≤ 3` 盏实时光源下的太阳仰角（`18°→3°→-8°`）、`Emissive_Warm` / `Emissive_Gold` / `Emissive_Cyan` 激活曲线与 Selective Bloom 强度曲线。 |
| `references/maps/suzhou-silhouettes.svg` | `1920 × 1140`（双带式：Band A `0–460m` `1:1` + Band B `0–135m` `3.2×` 放大） | **古今地标建筑剪影与真实尺度对照图**。Band A 呈现 16m 园林到 450m 苏州 IFS 的真实 `28:1` 震撼高度差；Band B 放大 `3.2×` 清晰呈现每座古塔层数（五级方塔/七级八面/九级八面）、虎丘塔 **`3.5°` 倾角（顶部偏心 2.34m）**、吴门桥/李公堤桥洞净空、28 太空舱摩天轮与各建筑对应的 Emissive 材质命名标签。 |

---

## 二、实景参考图库清单（`references/streetview/`，共 23 张）

全部图片均来自 Wikimedia Commons / Wikipedia 实景摄影（高分辨率 `1280px` 宽 JPEG，清单元数据同步存档于 `references/streetview/manifest.json`）：

| 编号 | 文件名 | 所属站点 | 实际尺寸 / 体积 | 建筑与材质关键参考点（Blender 建模必看） | 来源页面 |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 01a | `01a_hanshan_temple.jpg` | 01 寒山寺 | `1280×884` · 276KB | 鹅黄照壁与寺墙、大雄宝殿重檐歇山黛瓦屋顶、金色脊饰、朱红立柱与门窗格栅 | [Wikipedia: Hanshan Temple](https://en.wikipedia.org/wiki/Hanshan_Temple) |
| 01b | `01b_maple_bridge.jpg` | 01 枫桥 | `1280×750` · 291KB | 单孔高拱石桥（枫桥）、紧邻铁铃关古关隘与大运河石砌驳岸、垂柳临水 | [Commons: Fengqiao Bridge](https://commons.wikimedia.org/wiki/File:Fengqiao_Bridge_and_Tielingguan_Gate.JPG) |
| 01c | `01c_puming_pagoda.jpg` | 01 普明宝塔 | `1280×960` · 444KB | **42m 五级方形仿唐木构宝塔**，出檐深远平缓、四角微翘、底层宽阔台基、顶部鎏金塔刹 | [Commons: Puming Pagoda](https://commons.wikimedia.org/wiki/File:Puming_Pagoda_of_Hanshansi_Temple_2.jpg) |
| 02a | `02a_xiyuan_temple.jpg` | 02 西园寺 | `1280×960` · 559KB | 俯瞰视角的黄色山门照壁、前临河桥（福德/智慧桥）、放生池与大殿院落轴线布局 | [Wikipedia: Xiyuan Temple](https://en.wikipedia.org/wiki/Xiyuan_Temple) |
| 02b | `02b_tiger_hill_pagoda.jpg` | 02 虎丘斜塔 | `1280×1707` · 878KB | **47.7m 七级八面砖塔（云岩寺塔）**，红褐沧桑青砖质地、明显向东北倾斜 **`~3.5°`**、层层叠涩砖檐与无木构平座特征 | [Wikipedia: Tiger Hill Pagoda](https://en.wikipedia.org/wiki/Tiger_Hill_Pagoda) |
| 03 | `03_lingering_garden.jpg` | 03 留园 | `1280×960` · 521KB | 典型粉墙黛瓦围合水池、曲折临水长廊与花格漏窗、明瑟楼与涵碧山房低矮舒展比例、岸边太湖石假山与冠云峰 | [Wikipedia: Lingering Garden](https://en.wikipedia.org/wiki/Lingering_Garden) |
| 04a | `04a_panmen_ruiguang.jpg` | 04 盘门陆门 | `1280×960` · 532KB | 青砖古城墙雉堞垛口、瓮城拱券陆门、城楼歇山顶木构敌楼 | [Wikipedia: Pan Gate](https://en.wikipedia.org/wiki/Pan_Gate) |
| 04b | `04b_canglang_pavilion.jpg` | 04 沧浪亭 | `1280×959` · 609KB | 临水复廊（园外绿水绕墙、漏窗透景）、假山土丘翠竹林、山顶石柱单檐方亭（沧浪亭） | [Wikipedia: Canglang Pavilion](https://en.wikipedia.org/wiki/Canglang_Pavilion) |
| 04c | `04c_ruiguang_pagoda.jpg` | 04 瑞光塔 | `1280×1708` · 789KB | **53.6m 七级八面砖木楼阁式古塔**，每层腰檐平座分明、修长收分优雅、顶部铁刹直刺天际 | [Commons: Ruiguang Pagoda](https://commons.wikimedia.org/wiki/File:%E7%91%9E%E5%85%89%E5%A1%94%C2%B7%E8%8B%8F%E5%B7%9E%C2%B7%EF%BC%88%E8%A5%BF%E5%90%91%E4%B8%9C%EF%BC%89.jpg) |
| 04d | `04d_wumen_bridge.jpg` | 04 吴门桥 | `1280×960` · 314KB | 苏州最大单孔石拱桥，高耸半圆石拱洞（模型要求净空 **`≥18m W × ≥10m H`** 供无人机直穿）、阶梯石板桥面与石望柱 | [Commons: Wumen Bridge](https://commons.wikimedia.org/wiki/File:%E8%8B%8F%E5%B7%9E%E7%9B%98%E9%97%A8%E6%99%AF%E5%8C%BA-%E5%90%B4%E9%97%A8%E6%A1%A5.jpg) |
| 05a | `05a_master_of_nets_garden.jpg` | 05 网师园 | `1280×852` · 434KB | “以小见大”精巧彩霞池中心水庭、月到风来亭、濯缨水阁、极低矮近水的引静桥与精雕花窗 | [Wikipedia: Master of the Nets Garden](https://en.wikipedia.org/wiki/Master_of_the_Nets_Garden) |
| 05b | `05b_suzhou_twin_pagodas.jpg` | 05 苏州双塔 | `1280×1708` · 798KB | **罗汉院双塔（33.3m × 2）**，两座形制几乎完全相同的七级八面宋代仿木构砖塔东西并立、间距紧凑形成“门阙式”穿飞缝隙、细长铁塔刹 | [Wikipedia: Twin Pagodas](https://zh.wikipedia.org/wiki/%E7%BD%97%E6%B1%89%E9%99%A2%E5%8F%8C%E5%A1%94%E5%8F%8A%E6%AD%A3%E6%AE%BF%E9%81%97%E5%9D%80) |
| 06a | `06a_beisi_pagoda.jpg` | 06 北寺塔 | `1280×1706` · 738KB | **76m 九级八面重檐楼阁式宝塔（江南第一古塔）**，体量雄浑、粉白塔身配深色宽大翘角木檐与斗拱回廊、高耸铜顶铁刹 | [Wikipedia: Beisi Pagoda](https://en.wikipedia.org/wiki/Beisi_Pagoda) |
| 06b | `06b_pingjiang_road.jpg` | 06 平江路 | `1280×853` · 253KB | 窄水道（`w=16m`）夹粉墙黛瓦双坡民居、青石驳岸、低矮石拱桥、檐下红灯笼串与乌篷摇橹船 | [Wikipedia: Pingjiang Road](https://en.wikipedia.org/wiki/Pingjiang_Road) |
| 07a | `07a_lion_grove_garden.jpg` | 07 狮子林 | `1280×851` · 409KB | “假山王国”层叠多孔太湖石峰林迷宫、九狮峰、湖心石舫与八角亭、连绵起伏云墙 | [Wikipedia: Lion Grove Garden](https://en.wikipedia.org/wiki/Lion_Grove_Garden) |
| 07b | `07b_humble_administrators_garden.jpg` | 07 拙政园 | `1280×867` · 436KB | 开阔疏朗大水面与荷塘岛屿、见山楼/远香堂重檐水榭、标志性朱红廊桥**小飞虹**、青砖白墙与古松翠竹 | [Wikipedia: Humble Administrator's Garden](https://en.wikipedia.org/wiki/Humble_Administrator%27s_Garden) |
| 07c | `07c_suzhou_museum.jpg` | 07 苏州博物馆 | `1280×959` · 582KB | 贝聿铭经典现代苏式几何建筑：**纯白几何块体 + 深灰花岗岩勾勒菱形/八角折面屋顶与金属百叶天窗**、倒影镜面水池、现代片石假山（米芾山水意境） | [Wikipedia: Suzhou Museum](https://en.wikipedia.org/wiki/Suzhou_Museum) |
| 08 | `08_gate_of_the_orient.jpg` | 08 东方之门 | `1280×971` · 153KB | **301.8m 超高层“门”字形双塔拱门**，外侧优雅弧形收分幕墙配竖向金属肋条与夜景光带，底部裙房连接苏州中心“未来之翼”流线屋盖；**拱门必须东西通透（`X` 轴贯穿，净空 `62m W × 195m H`）** | [Wikipedia: Gate of the Orient](https://en.wikipedia.org/wiki/Gate_of_the_Orient) |
| 09 | `09_ligongdi.jpg` | 09 李公堤 | `1280×960` · 340KB | 横卧金鸡湖南岸的湖中长堤，水岸步廊、新中式坡顶商业院落、滨水现代景观拱桥（模型净空 **`≥18m W × ≥10m H`**）与湖面暖金灯带倒影 | [Commons: Ligongdi](https://commons.wikimedia.org/wiki/File:%E6%9D%8E%E5%85%AC%E5%A0%A4%E8%A5%BF.jpg) |
| 10a | `10a_ferris_wheel_jinji.jpg` | 10 苏州之眼摩天轮 | `1280×1707` · 281KB | **128m 亚洲最大水上摩天轮（苏州之眼）**，细密钢索双环轮圈、人字形巨型钢支撑腿、**28 个发光观景太空舱**（轮盘须命名 `FerrisWheelRotor` 枢轴居圆心） | [Wikipedia: Suzhou Ferris Wheel](https://en.wikipedia.org/wiki/Suzhou_Ferris_Wheel) |
| 10b | `10b_suzhou_moca_jinji.jpg` | 10 金鸡湖滨水 & MoCA 语境 | `1280×777` · 395KB | 金鸡湖开阔现代湖岸线、高密度玻璃幕墙 CBD 天际线与滨水广场尺度参考；配合 BIG 事务所设计的苏州当代美术馆（连续波浪金属丝带屋顶 + 玻璃幕墙展厅群落） | [Wikipedia: Jinji Lake](https://en.wikipedia.org/wiki/Jinji_Lake) |
| 11 | `11_suzhou_culture_arts_centre.jpg` | 11 苏州文化艺术中心 | `1280×536` · 225KB | 保罗·安德鲁设计的**银色金属网格编织“月牙鸟巢”穹顶（42m）**，流畅水平月牙弧线 + 菱形镂空遮阳表皮，临湖连接月光码头木质栈桥 | [Wikipedia: Suzhou Culture and Arts Centre](https://en.wikipedia.org/wiki/Suzhou_Culture_and_Arts_Centre) |
| 12 | `12_suzhou_ifs.jpg` | 12 苏州国金中心 IFS | `1280×2276` · 345KB | **450m 江苏第一高楼**，修长逐层微收蓝银玻璃幕墙塔身、竖向玻璃翼肋灯光、标志性**“鲤鱼跳龙门”不对称斜切鱼尾双峰塔冠** | [Wikipedia: Suzhou IFS](https://en.wikipedia.org/wiki/Suzhou_IFS) |

---

## 三、12 站空间锚点、边界框与硬约束总表（对齐 `world-layout.json`）

> 所有站点 `.glb` 模型以**本地原点 `(0, 0, 0)` 为该站地面中心**（地面台基顶 `Z=0`；入水基础/河岸下探至 `Z=-2.0~-2.5`），Three.js 加载时直接对齐到下表 `Anchor` 坐标。

| # | Station ID | 站点名称 | 责任方 | 锚点 `(X, Y, Z)` | 世界边界框 `X范围 × Z范围` | 真实高度 `maxH` | 默认天光 `t` | `heroView` 机位 → 视点 | 特殊穿越 / 动画节点约束 |
| :-: | :--- | :--- | :---: | :--- | :--- | :-: | :-: | :--- | :--- |
| 01 | `01-hanshan` | 寒山寺 & 枫桥 | `blender-west` | `(-1360, 1.6, 110)` | `[-1450, -1270] × [35, 185]` (`180×150m`) | `44m` | `0.12` | `[-1455, 28, 175] → [-1355, 18, 105]` | 含枫桥单孔石拱跨越大运河边线 |
| 02 | `02-xiyuan-tigerhill` | 西园寺 & 虎丘斜塔 | `blender-west` | `(-920, 1.6, -360)`<br/>西园子锚 `(-1080, 1.6, -160)` | `[-1030, -810] × [-470, -250]` (`220×220m`) | `82m` | `0.22` | `[-825, 62, -265] → [-920, 48, -360]` | 32m 海涌山 + **47.7m 虎丘塔倾角 `~3.5°`** |
| 03 | `03-lingering` | 留园 | `blender-west` | `(-560, 1.6, -90)` | `[-630, -490] × [-150, -30]` (`140×120m`) | `16m` | `0.34` | `[-625, 26, -35] → [-560, 8, -90]` | 含冠云峰太湖石、曲廊水庭与粉墙黛瓦 |
| 04 | `04-panmen-canglang` | 盘门三景 & 沧浪亭 | `blender-west` | `(-340, 1.6, 340)` | `[-480, -200] × [265, 415]` (`280×150m`) | `56m` | `0.44` | `[-465, 36, 435] → [-350, 24, 335]` | **吴门桥洞净空 `W≥18m, H≥10m`**（无人机直穿） |
| 05 | `05-wangshi-twintowers` | 网师园 & 苏州双塔 | `blender-gusu` | `(80, 1.6, 240)` | `[-20, 180] × [150, 330]` (`200×180m`) | `36m` | `0.52` | `[10, 32, 330] → [95, 18, 225]` | 双塔 `33.3m × 2` 中间留出穿飞走廊 |
| 06 | `06-beisi-pingjiang` | 北寺塔 & 平江路水巷 | `blender-gusu` | `(-10, 1.6, -180)` | `[-135, 115] × [-290, -70]` (`250×220m`) | `78m` | `0.60` | `[-125, 68, -110] → [-10, 42, -185]` | 76m 九层八面北寺塔 + 东侧衔接平江河灯笼水巷 |
| 07 | `07-gardens-museum` | 狮子林·拙政园 & 苏博 | `blender-gusu` | `(230, 1.6, -230)`<br/>狮子林 `(210, 1.6, -95)`<br/>苏博 `(265, 1.6, -220)` | `[100, 360] × [-350, -110]` (`260×240m`) | `20m` | `0.68` | `[165, 34, -315] → [245, 10, -225]` | 拙政园与苏博一墙之隔，方便翻墙完成古→今转场 |
| 08 | `08-gate-of-orient` | 东方之门 & 苏州中心 | `blender-modern` | `(650, 1.6, 0)`<br/>拱心 `(650, 125, 0)` | `[540, 760] × [-140, 140]` (`220×280m`) | `302m` | `0.78` | `[430, 140, 85] → [650, 145, 0]` | **沿 X 轴东西通透门洞：`W≥62m, H=40–235m`**（禁任何封堵面片！） |
| 09 | `09-ligongdi` | 李公堤 | `blender-modern` | `(1000, 0.0, 365)` | `[810, 1190] × [310, 420]` (`380×110m`) | `24m` | `0.85` | `[835, 30, 425] → [1010, 10, 360]` | **湖中长堤 + 拱桥洞净空 `W≥18m, H≥10m`**（锚点 `Y=0.0` 水面齐平） |
| 10 | `10-moca-eye` | 当代美术馆 & 苏州之眼 | `blender-modern` | `(1310, 1.6, 125)` | `[1200, 1420] × [15, 235]` (`220×220m`) | `130m` | `0.90` | `[1135, 58, 225] → [1310, 62, 125]` | **128m 摩天轮转盘命名 `FerrisWheelRotor`（含 28 发光舱，枢轴在轮心）** |
| 11 | `11-arts-centre` | 文化艺术中心 & 月光码头 | `blender-modern` | `(1280, 1.6, -230)` | `[1160, 1400] × [-325, -135]` (`240×190m`) | `42m` | `0.94` | `[1120, 48, -145] → [1285, 22, -230]` | 银色编织月牙穹顶 + 临湖栈桥灯火 |
| 12 | `12-suzhou-ifs` | 苏州国金中心 IFS | `blender-modern` | `(1480, 1.6, -60)` | `[1390, 1570] × [-150, 30]` (`180×180m`) | `450m` | `1.00` | `[1620, 465, -20] → [850, 80, 0]` | 450m 鱼尾斜切塔冠；机位 `Y=465m` 西望全城 2500 年全景 |

---

## 四、给 `@verifier` 的具体视觉与技术验收清单

请 `@verifier` 在场景集成后，通过 `window.__SUZHOU_DEBUG__` 逐站截图并结合 `references/streetview/` 实景照片与 `references/maps/suzhou-silhouettes.svg` 执行以下硬性检查：

### A. 建筑剪影与地标辨识度检查（对照实景图与 `suzhou-silhouettes.svg`）
- [ ] **01 寒山寺 & 枫桥**：黄色寺墙清晰可辨；普明宝塔为**五层方形仿唐塔**（非八角塔），单孔石拱枫桥跨水自然无悬空。
- [ ] **02 西园寺 & 虎丘斜塔**：海涌山植被覆盖连贯；虎丘七层八面砖塔**从 `heroView` 角度能肉眼明显看出约 `3.5°` 倾斜**；西园寺放生池与湖心亭位于 `(-1080, -160)` 无穿模。
- [ ] **03 留园**：粉墙黛瓦与中央水池清晰，曲廊、明瑟楼及垂直雕塑感太湖石（冠云峰）比例和谐，整体高度压在 `≤16m`。
- [ ] **04 盘门三景 & 沧浪亭**：瑞光塔（53.6m 七级八面）+ 水陆城门 + 高拱吴门桥同框；东侧沧浪亭绿竹与山顶石亭清晰；**验证无人机穿吴门桥洞无任何穿模/削顶**。
- [ ] **05 网师园 & 苏州双塔**：两座 33.3m 七级八面宋塔并立对称、细塔刹清晰，网师园小巧水庭与双塔比例正确。
- [ ] **06 北寺塔 & 平江路**：76m 九级八面重檐翘角北寺塔显著高于周遭古城（比双塔高出 2 倍以上），平江路窄水巷两侧红灯笼与石拱桥完整。
- [ ] **07 狮子林 · 拙政园 & 苏博**：拙政园水面+朱红小飞虹廊桥与一墙之隔的**苏博纯白几何墙体 + 灰瓦菱形屋顶折线**形成鲜明“古典→现代”美学对比；狮子林多孔太湖石群落在 `(210, -95)` 独立成景。
- [ ] **08 东方之门 & 苏州中心**：301.8m 双塔拱门比例端庄挺拔，底部苏州中心流线型“未来之翼”铺展自然；**核心红线：在 `progress` 穿越 `(650, 125, 0)` 门洞帧检查前后视野完全通透，无任何隐形碰撞面或幕墙横梁遮挡**。
- [ ] **09 李公堤**：长堤贴合 `Y=0.0m` 金鸡湖面（无悬浮白缝），现代拱桥净空足够无人机低空穿行，湖面倒影连贯。
- [ ] **10 当代美术馆 & 苏州之眼**：BIG 波浪丝带屋顶线条流利；128m 摩天轮含清晰双环钢索辐条与 28 发光太空舱，且 `FerrisWheelRotor` **绕圆心平滑自转（无偏心晃动）**。
- [ ] **11 文化艺术中心 & 月光码头**：银色月牙壳体网格纹理鲜明，临水月光码头灯火与东方之门隔湖相望构图成立。
- [ ] **12 苏州国金中心 IFS**：450m 明显高于东方之门（约 `1.5×` 高度比），顶部**“鱼尾”不对称斜切塔冠**剪影锐利；终镜 `Y=465m` 西望构图能同时框住璀璨金鸡湖夜景与远处姑苏古城古塔灯火。

### B. 动态天光、自发光材质与性能红线检查（对照 `suzhou-elevation-lighting.svg`）
- [ ] **4 种手动天光 + `auto` 模式验证**：分别调用 `setAtmosphere('dawn' | 'golden' | 'dusk' | 'night' | 'auto')` 截图，确认：
  - `golden`（Act I）：低角度暖橙夕阳斜照黄墙与斜塔，古建自发光处于低强度；
  - `dusk`（Act II）：粉紫暮色天空，古塔檐灯与平江路红灯笼（`Emissive_Warm`）柔和点亮；
  - `night`（Act IV）：深蓝调夜空，东方之门/摩天轮/文化艺术中心/IFS（`Emissive_Gold` / `Emissive_Cyan` / `Emissive_Accent`）全面璀璨亮灯且 Selective Bloom 不泛白过曝；
  - `dawn`：水墨清晨冷灰薄雾氛围。
- [ ] **性能与资源红线（调用 `getStats()` 核查）**：
  - `activeLights <= 3`（严禁出现任何 `PointLight` / `SpotLight`）；
  - `drawCalls < 160`（古城民居与现代 CBD 配楼均由 `InstancedMesh` 批处理）；
  - `missingModels.length === 0`（全部 12 站 + 2 套模块化 Kit `.glb` 均成功加载，无白模占位残留）；
  - 实时帧率在 1080p 下稳定 **≥ 45 FPS**（目标 60 FPS）。
- [ ] **UI / Look-Dev 面板检查**：
  - 按 `G` 呼出 Look-Dev 面板，拖动光源/自发光/水面/Bloom 滑块即时生效，`Copy JSON` 与 `Reset Defaults` 正常；
  - 按 `H` 彻底隐藏 100% UI（零残留像素）用于录屏。
