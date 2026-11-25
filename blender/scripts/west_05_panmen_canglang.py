"""
Station 04: Panmen Three Views & Canglang Pavilion (盘门三景 & 沧浪亭)
Exports: web/public/assets/models/panmen_canglang.glb
Features:
  - West Side (Panmen Three Views):
      * 53.6m 7-story octagonal Song-dynasty Ruiguang Pagoda (瑞光塔) with upturned eaves & golden spire
      * Ancient Suzhou brick City Wall (盘门古城墙) with battlements, Land Gate + City Gate Tower (盘门城楼),
        and iconic Twin Water Gates (水门) spanning the moat canal
      * High-Arch Granite Wumen Bridge (吴门桥) at local X=0, Y=-12 with span_axis='Y'
        (arch tunnel opens cleanly East-West along X for drone fly-through!)
        GUARANTEED CLEAR OPENING: width = 22.0m (>=18m), height = 13.6m above water / 12.0m above ground (>=10m)!
  - East Side (Canglang Pavilion 沧浪亭):
      * Waterfront curving double-corridor (复廊) with leak-windows & Fish-Watching Pavilion (观鱼处)
      * Lush dense emerald bamboo groves (翠竹林), sculpted central rockery hill,
        crowned by the hilltop stone Canglang Pavilion (沧浪亭) & Mingdao Hall.
"""
import math
import os
import sys
from mathutils import Matrix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from west_common import SuzhouBuilder

OUT_GLB = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/panmen_canglang.glb"


def build_ruiguang_pagoda(b, cx, cy, z0=0.0):
    """53.6m 7-story octagonal Song-dynasty Ruiguang Pagoda (瑞光塔)."""
    # 2-tier octagonal granite terrace base (Z = 0..2.8m)
    b.prism(cx, cy, z0 - 0.5, z0 + 1.5, 10.6, 10.2, 8, "Mat_GraniteDark")
    b.prism(cx, cy, z0 + 1.5, z0 + 2.8, 9.2, 8.8, 8, "Mat_GraniteLight")
    # Warm perimeter uplights around pagoda terrace
    for i in range(8):
        a = 2.0 * math.pi * i / 8.0
        b.box_z(cx + 8.3 * math.cos(a), cy + 8.3 * math.sin(a), z0 + 2.8, z0 + 3.4, 0.55, 0.55, "Emissive_Warm_Uplight")

    # 7 tapering octagonal Song brick-and-wood stories (Z = 2.8m to 44.2m)
    # Heights: 6.6 + 6.1 + 5.7 + 5.3 + 4.9 + 4.6 + 4.4 = 37.6m + top roof 3.8m -> 44.2m
    # Plus 9.4m golden bronze spire -> 53.6m exact!
    stories = [
        (6.8, 6.5, 6.6, 2.3),
        (6.2, 5.9, 6.1, 2.15),
        (5.65, 5.4, 5.7, 2.0),
        (5.15, 4.9, 5.3, 1.85),
        (4.70, 4.45, 4.9, 1.72),
        (4.28, 4.05, 4.6, 1.60),
        (3.88, 3.62, 4.4, 1.55),
    ]
    z = z0 + 2.8
    for idx, (r0, r1, sh, ovh) in enumerate(stories):
        wall_h = sh * 0.72
        # Warm cream-ochre Song masonry shaft
        b.prism(cx, cy, z, z + wall_h, r0, r1, 8, "Mat_RuiguangBrick")
        # Crimson perimeter wooden balcony & corner pillars
        if idx > 0:
            b.prism(cx, cy, z, z + 0.92, r0 + 0.78, r0 + 0.78, 8, "Mat_CrimsonWood",
                    cap_bottom=False, cap_top=False)
        for fi in range(8):
            a_c = 2.0 * math.pi * fi / 8.0
            a_f = a_c + math.pi / 8.0
            b.cylinder(cx + r0 * math.cos(a_c), cy + r0 * math.sin(a_c),
                       z, z + wall_h, 0.18, "Mat_CrimsonWood", sides=6)
            ap = 0.5 * (r0 + r1) * math.cos(math.pi / 8.0)
            fx, fy = cx + ap * math.cos(a_f), cy + ap * math.sin(a_f)
            rot_f = a_f + math.pi * 0.5
            # Glowing arched doorway on alternating facets
            dw = r0 * (0.28 if fi % 2 == 0 else 0.16)
            dh = wall_h * (0.62 if fi % 2 == 0 else 0.42)
            b.box_z(fx, fy, z + 0.25, z + 0.25 + dh, dw + 0.18, 0.22, "Mat_DarkWood", rot_z=rot_f)
            b.box_z(fx, fy, z + 0.30, z + 0.20 + dh, dw, 0.28, "Emissive_Warm_Window", rot_z=rot_f)

        # Sweeping octagonal upturned timber-and-tile roof with golden eave LEDs
        is_top = (idx == len(stories) - 1)
        rh = 3.8 if is_top else (sh * 0.48)
        b.add_polygonal_roof(
            cx, cy, z + wall_h - 0.05,
            r_inner=(0.45 if is_top else r1 * 0.84),
            r_outer=r1 + ovh, h=rh, sides=8,
            mat_tile="Mat_DarkTile", mat_ridge="Mat_TileRidge",
            mat_wood="Mat_CrimsonWood", mat_gold=None,
            mat_eave_light="Emissive_Gold_Eave",
            flare_z=0.85 if is_top else 0.65, flare_r=0.45, steps=3, finial=False,
        )
        z += sh if not is_top else (wall_h + rh)

    # Tall Golden-Bronze Ruiguang Pagoda Spire reaching exact 53.6m!
    b.add_pagoda_spire(cx, cy, z - 0.1, height=53.6 - z + 0.1, r_base=1.05)


def add_city_wall_segment(b, x0, y0, x1, y1, z0=-1.6, h=9.0, thick=7.2):
    """Ancient Suzhou battered grey-brick city wall with crenellated battlements (垛口)."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.5:
        return
    ang = math.atan2(dy, dx)
    mx, my = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    m = Matrix.Translation((mx, my, 0.0)) @ Matrix.Rotation(ang, 4, 'Z')

    # Main wall body (stone plinth + grey brick rampart)
    b.box_z(0, 0, z0, 1.4, length, thick + 0.8, "Mat_GraniteDark", matrix=m)
    b.box_z(0, 0, 1.4, h, length, thick, "Mat_CityBrick", matrix=m)
    # Inner parapet + outer crenellated merlons (垛口)
    b.box_z(0, -thick * 0.44, h, h + 0.9, length, 0.55, "Mat_CityBrick", matrix=m)
    b.box_z(0,  thick * 0.44, h, h + 0.9, length, 0.55, "Mat_CityBrick", matrix=m)
    n_merlons = max(2, int(length // 2.8))
    for i in range(n_merlons):
        px = -length * 0.5 + (i + 0.5) * (length / n_merlons)
        b.box_z(px, thick * 0.44, h + 0.9, h + 1.85, 1.55, 0.58, "Mat_CityBrick", matrix=m)
        b.box_z(px, -thick * 0.44, h + 0.9, h + 1.65, 1.55, 0.58, "Mat_CityBrick", matrix=m)
    # Warm wall-wash uplights along rampart base
    n_lights = max(1, int(length // 14.0))
    for i in range(n_lights):
        lx = -length * 0.5 + (i + 0.5) * (length / n_lights)
        b.box_z(lx, thick * 0.55, 0.1, 0.65, 1.4, 0.45, "Emissive_Warm_Uplight", matrix=m)


def add_arched_gate_block(b, cx, cy, z_base, w_gate, h_gate, wall_h, wall_thick, axis="X"):
    """Solid grey-brick city gate block with an OPEN vaulted semicircular archway."""
    rot = 0.0 if axis == "X" else math.pi * 0.5
    m = Matrix.Translation((cx, cy, 0.0)) @ Matrix.Rotation(rot, 4, 'Z')
    # Side piers flanking the arch opening (along local Y)
    hw = w_gate * 0.5
    pier_w = 3.4
    for sy in (-1, 1):
        b.box_z(0, sy * (hw + pier_w * 0.5), z_base, wall_h, wall_thick, pier_w, "Mat_CityBrick", matrix=m)
    # Arch vault ring & spandrel lintel strictly above the arch!
    rx = hw
    rz = h_gate * 0.42
    z_sp = z_base + h_gate - rz
    segs = 10
    ht = wall_thick * 0.5
    # Build spandrel blocks from y = -rx to +rx above the arch curve up to wall_h
    verts, faces = [], []
    for i in range(segs + 1):
        th = math.pi * (1.0 - i / segs)
        y_a = rx * math.cos(th)
        z_a = z_sp + rz * math.sin(th)
        verts.extend([(-ht, y_a, z_a), (ht, y_a, z_a), (ht, y_a, wall_h), (-ht, y_a, wall_h)])
    for i in range(segs):
        a, c = i * 4, (i + 1) * 4
        faces.extend([
            (a + 0, c + 0, c + 1, a + 1),  # vault underside
            (a + 3, a + 2, c + 2, c + 3),  # top rampart deck
            (a + 0, a + 3, c + 3, c + 0),  # west facade
            (a + 1, c + 1, c + 2, a + 2),  # east facade
        ])
    b.add_mesh_data(verts, faces, "Mat_CityBrick", matrix=m)
    # Granite arch ring highlight + warm gate interior uplight
    b.box_z(-ht - 0.15, 0, wall_h - 1.2, wall_h - 0.2, 0.35, w_gate * 0.75, "Mat_GraniteLight", matrix=m)
    b.box_z(ht + 0.15, 0, wall_h - 1.2, wall_h - 0.2, 0.35, w_gate * 0.75, "Mat_GraniteLight", matrix=m)
    for sy in (-1, 1):
        b.box_z(0, sy * (hw - 0.25), max(0.0, z_base + 0.4), max(0.5, z_base + 0.9), 1.8, 0.35, "Emissive_Warm_Uplight", matrix=m)


def build_panmen_west(b):
    """Panmen Three Views (West Precinct): Ruiguang Pagoda, Ancient City Wall & Twin Water-and-Land Gates."""
    # West landmass NORTH of canal (X in [-132, -26], Y in [-1, +66])
    b.box_z(-79.0, 32.5, -2.4, 0.0, 106.0, 67.0, "Mat_GraniteLight")
    # West landmass SOUTH of canal (X in [-132, -26], Y in [-66, -23])
    b.box_z(-79.0, -44.5, -2.4, 0.0, 106.0, 43.0, "Mat_GraniteLight")
    # Stone quay walls lining the canal (Y = -1 and Y = -23)
    b.box_z(-79.0, -1.0, -2.4, 0.35, 106.0, 1.6, "Mat_GraniteDark")
    b.box_z(-79.0, -23.0, -2.4, 0.35, 106.0, 1.6, "Mat_GraniteDark")
    # Canal water bed deep below world water (Z = -2.35 so Three.js moat water at Y=0 / local Z=-1.6 never Z-fights!)
    b.box_z(-79.0, -12.0, -2.5, -2.25, 106.0, 22.0, "Mat_GraniteDark")

    # 1. 53.6m 7-Story Octagonal Ruiguang Pagoda (瑞光塔) at (-76, +38)
    # Positioned inside the Panmen walled precinct so heroView frames Ruiguang Pagoda +
    # City Gate Tower + Twin Water-and-Land Gates + Wumen Bridge + Canglang Pavilion all together!
    build_ruiguang_pagoda(b, -76.0, 38.0, z0=0.0)

    # 2. Ancient Suzhou City Wall (盘门古城墙) running North-South along X = -52
    # North wall wing (from Y=+31 to Y=+62)
    add_city_wall_segment(b, -52.0, 31.0, -52.0, 62.0, z0=-0.6, h=9.0, thick=7.4)
    # Turning NW along north boundary
    add_city_wall_segment(b, -52.0, 62.0, -126.0, 62.0, z0=-0.6, h=8.6, thick=6.4)
    # Mid wall between Land Gate and Water Gate (Y=+2 to Y=+16)
    add_city_wall_segment(b, -52.0, 1.5, -52.0, 16.5, z0=-0.6, h=9.0, thick=7.4)
    # South wall wing (from Y=-26 to Y=-62)
    add_city_wall_segment(b, -52.0, -26.0, -52.0, -62.0, z0=-0.6, h=8.6, thick=7.0)
    # Outer barbican wall (瓮城) wrapping east of the Water Gate (clean low profile so Wumen Bridge pops!)
    add_city_wall_segment(b, -36.0, -26.0, -36.0, -40.0, z0=-0.6, h=7.4, thick=5.4)
    add_city_wall_segment(b, -52.0, -40.0, -36.0, -40.0, z0=-0.6, h=7.4, thick=5.4)
    add_city_wall_segment(b, -36.0, 1.5, -36.0, 15.0, z0=-0.6, h=7.8, thick=5.4)

    # 3. Land Gate (陆门) at (-52, +23.5) + Iconic Double-Eave Panmen City Gate Watchtower (盘门城楼)!
    add_arched_gate_block(b, -52.0, 23.5, z_base=0.0, w_gate=7.4, h_gate=6.4, wall_h=9.0, wall_thick=7.4, axis="X")
    # Grand double-eave Watchtower ("吴中锁钥") atop Land Gate at Z = 9.0m (matching 04a_panmen_ruiguang.jpg!)
    b.add_hall(-52.0, 23.5, 9.0, 19.0, 10.5, wall_h=4.6, roof_h=4.0, double_eave=True,
               rot_z=math.pi * 0.5, wall_mat="Mat_CityBrick", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.5, stairs_front=False, plaque=False)
    # Iconic white calligraphic plaque "吴中锁钥" facing both East and West on the Watchtower!
    for sx in (-1, 1):
        b.box_z(-52.0 + sx * 5.65, 23.5, 13.6, 15.6, 0.25, 5.8, "Mat_WhiteWall")
        b.box_z(-52.0 + sx * 5.80, 23.5, 13.9, 15.3, 0.14, 5.0, "Mat_DarkWood")
    # Tall timber flagpole with vertical string of glowing red lanterns (visible in 04a_panmen_ruiguang.jpg!)
    b.cylinder(-46.5, 34.0, 9.0, 24.5, 0.16, "Mat_DarkWood", sides=6)
    for k in range(7):
        b.add_lantern(-46.5, 34.8, 12.0 + k * 1.5, scale=0.65, glow_mat="Emissive_Warm_Lantern")

    # 4. Iconic Twin Water Gates (水门 - Inner & Outer Water Lock Arches spanning canal at Y = -12)
    # Inner Water Gate at X = -52, Outer Water Gate at X = -36 (forming the historic double water-gate!)
    add_arched_gate_block(b, -52.0, -12.0, z_base=-1.6, w_gate=16.0, h_gate=9.2, wall_h=9.0, wall_thick=7.4, axis="X")
    add_arched_gate_block(b, -36.0, -12.0, z_base=-1.6, w_gate=16.0, h_gate=8.8, wall_h=8.4, wall_thick=5.8, axis="X")
    # Water-gate sluice watch pavilion atop the outer water gate
    b.add_pavilion(-36.0, -12.0, 8.4, radius=3.4, col_h=2.8, roof_h=2.6, sides=6,
                   plinth_h=0.3, pillar_mat="Mat_CrimsonWood", eave_light="Emissive_Gold_Eave")

    # 5. Panmen Garden Courtyard Hall (四瑞堂), Pavilions, Boats & Trees
    b.add_hall(-92.0, -40.0, 0.0, 20.0, 11.0, wall_h=4.6, roof_h=3.2, double_eave=False,
               rot_z=0.0, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.7)
    b.add_pavilion(-74.0, 4.0, 0.0, radius=3.8, col_h=3.4, roof_h=2.9, sides=6,
                   pillar_mat="Mat_CrimsonWood", eave_light="Emissive_Gold_Eave")
    # Moored boats in the canal
    b.add_wooden_boat(-78.0, -16.0, -1.55, rot_z=0.08, scale=1.1, lantern=True)
    b.add_wooden_boat(-108.0, -9.0, -1.55, rot_z=-0.05, scale=1.05, lantern=True)

    # Panmen pines, willows & maples (kept completely clear of X > -32 along Y=-12 flight corridor!)
    for i, (px, py, sc) in enumerate([
        (-116, 46, 1.3), (-118, 12, 1.25), (-72, 48, 1.25), (-116, -42, 1.25),
        (-72, -46, 1.20), (-64, 40, 1.15), (-82, 50, 1.20),
    ]):
        b.add_tree_pine(px, py, 0.0, scale=sc, seed=i + 1)
    for i, (wx, wy, sc) in enumerate([(-86, -24, 1.1), (-68, -24, 1.05), (-106, -1, 1.1), (-78, 1, 1.05)]):
        b.add_tree_willow(wx, wy, 0.0, scale=sc, seed=i + 20)


def build_wumen_bridge(b):
    """
    Iconic High-Arch Granite Wumen Bridge (吴门桥) at local X=0, Y=-12.
    Bridge deck runs North-South (span_axis='Y') across the East-West moat/canal!
    Arch tunnel opens cleanly East-West along X for drone fly-through:
      - Clear width = 24.0m (Y in [-24, 0], exceeds >=18m requirement!)
      - Clear height = 14.6m above water Z=-1.6 (13.0m above ground Z=0, exceeds >=10m requirement!)
    """
    # North & South granite landing embankments flanking the 24m canal under Wumen Bridge
    # North landing (X in [-26, +26], Y in [0, +42])
    b.box_z(0.0, 21.0, -2.4, 0.0, 52.0, 42.0, "Mat_GraniteLight")
    b.box_z(0.0, 0.0, -2.4, 0.35, 52.0, 1.6, "Mat_GraniteDark")
    # South landing (X in [-26, +26], Y in [-54, -24])
    b.box_z(0.0, -39.0, -2.4, 0.0, 52.0, 30.0, "Mat_GraniteLight")
    b.box_z(0.0, -24.0, -2.4, 0.35, 52.0, 1.6, "Mat_GraniteDark")

    # Open canal water channel beneath Wumen Bridge (recessed bed at Z=-2.35 -> Three.js water at Z=-1.6 flows cleanly!)
    b.box_z(0.0, -12.0, -2.45, -2.25, 52.0, 24.0, "Mat_GraniteDark")

    # High-arch Wumen Bridge!
    b.add_arch_bridge(
        cx=0.0, cy=-12.0, z_water=-1.6, span_axis="Y",
        clear_w=24.0, clear_h=14.6, deck_w=6.8, approach_len=19.0, arch_thick=1.15,
        stone_mat="Mat_GraniteLight", dark_stone="Mat_GraniteDark",
        lantern_mat="Emissive_Warm_Lantern", segs=20,
    )


def build_canglang_east(b):
    """
    Canglang Pavilion (沧浪亭) across the water on the East side (X in [+26, +132]):
    - Curving waterfront double-corridor (复廊) with leak-windows hugging the canal
    - Projecting square Fish-Watching Pavilion (观鱼处) over the water
    - Lush emerald bamboo grove (翠竹林), central Taihu rockery hill, and hilltop stone Canglang Pavilion!
    """
    # Main Canglang garden landmass NORTH of waterfront canal (X in [+26, +132], Y in [-1, +64])
    b.box_z(79.0, 31.5, -2.4, 0.0, 106.0, 65.0, "Mat_GraniteLight")
    # South opposite canal bank (X in [+26, +132], Y in [-58, -28])
    b.box_z(79.0, -43.0, -2.4, 0.0, 106.0, 30.0, "Mat_GraniteLight")
    # Canal quay walls (leaving wide 27m waterfront moat along Y in [-28, -1]!)
    b.box_z(79.0, -1.0, -2.4, 0.35, 106.0, 1.6, "Mat_GraniteDark")
    b.box_z(79.0, -28.0, -2.4, 0.35, 106.0, 1.6, "Mat_GraniteDark")

    # Classic Suzhou white perimeter walls around Canglang Pavilion (North, East, and partial West)
    b.add_wall(28.0, 62.0, 130.0, 62.0, h=3.8, wall_mat="Mat_WhiteWall", horse_head=True)
    b.add_wall(130.0, 62.0, 130.0, 0.0, h=3.8, wall_mat="Mat_WhiteWall", horse_head=True)
    b.add_wall(28.0, 2.0, 28.0, 62.0, h=3.8, wall_mat="Mat_WhiteWall", horse_head=True, leak_windows=True)

    # 1. Famous Canglang Waterfront Double-Corridor (复廊) hugging the south water edge (matching 04b!)
    # Gently winding along the waterfront with central white leak-window partition wall
    water_corridors = [
        (30.0, 2.0, 56.0, 4.0),
        (56.0, 4.0, 82.0, 1.5),
        (82.0, 1.5, 108.0, 4.0),
        (108.0, 4.0, 128.0, 2.0),
    ]
    for x0, y0, x1, y1 in water_corridors:
        b.add_corridor(x0, y0, x1, y1, z0=0.0, width=3.4, h=3.2,
                       back_wall=True, wall_side=0, wall_mat="Mat_WhiteWall",
                       wood_mat="Mat_DarkWood", leak_windows=True)

    # Projecting Waterside Fish-Watching Pavilion (观鱼处) jutting out right over the water!
    b.box_z(46.0, -3.5, -2.2, 0.35, 8.0, 7.6, "Mat_GraniteDark")
    b.add_pavilion(46.0, -3.5, 0.35, radius=3.8, col_h=3.4, roof_h=3.2, sides=4,
                   plinth_h=0.4, pillar_mat="Mat_DarkWood", gold_mat="Mat_GoldTrim",
                   eave_light="Emissive_Gold_Eave")
    # Waterside Face-Water Pavilion (面水轩) on eastern waterfront
    b.add_hall(114.0, 10.0, 0.0, 16.0, 9.0, wall_h=4.2, roof_h=2.8, double_eave=False,
               rot_z=0.0, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.6)

    # 2. Central Sculpted Rockery Hill (假山) & Hilltop Stone Canglang Pavilion (沧浪亭)!
    # Layered terraced Taihu rock & mossy earth hill rising to Z = 8.2m at (+78, +24)
    b.prism(78.0, 24.0, -0.4, 3.6, 22.0, 16.5, 10, "Mat_HillEarth", smooth=True)
    b.prism(78.0, 24.0, 3.4, 6.8, 16.0, 10.5, 9, "Mat_TaihuRock")
    b.prism(78.0, 24.0, 6.6, 8.2, 10.2, 8.0, 8, "Mat_GraniteDark")
    # Craggy Taihu rock boulders clothing the rockery hill slopes
    for i, (ox, oy, oz, sc) in enumerate([
        (-13, -8, 1.5, 5.2), (12, -9, 1.8, 5.0), (-11, 10, 2.0, 5.5),
        (13, 8, 1.6, 4.8), (0, -13, 1.5, 4.6), (0, 13, 2.2, 5.0),
    ]):
        b.add_taihu_rock(78.0 + ox, 24.0 + oy, oz, sc, sc * 0.85, sc * 0.9, seed=i + 30)

    # Iconic Hilltop Stone Canglang Pavilion (沧浪亭) — stone pillars, upturned dark-tile eaves!
    b.add_pavilion(
        78.0, 24.0, 8.2, radius=5.4, col_h=4.2, roof_h=4.2, sides=4,
        double_eave=False, plinth_h=0.75,
        pillar_mat="Mat_GraniteLight", roof_mat="Mat_DarkTile",
        gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave",
    )
    # Warm stone uplights on the Canglang Pavilion hill
    for a_i in range(4):
        a = a_i * math.pi * 0.5 + math.pi * 0.25
        b.box_z(78.0 + 7.2 * math.cos(a), 24.0 + 7.2 * math.sin(a), 8.2, 8.75, 0.55, 0.55, "Emissive_Warm_Uplight")

    # 3. Mingdao Hall (明道堂) & Cuilinglong Bamboo Hall (翠玲珑)
    b.add_hall(82.0, 48.0, 0.0, 24.0, 12.0, wall_h=4.8, roof_h=3.4, double_eave=False,
               rot_z=0.0, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.8)
    b.add_hall(44.0, 44.0, 0.0, 16.0, 9.5, wall_h=4.2, roof_h=2.9, double_eave=False,
               rot_z=0.0, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.6)

    # 4. Lush Dense Emerald Bamboo Groves (翠竹林 - signature of Canglang Pavilion!)
    bamboo_groves = [
        (46.0, 22.0, 7.5, 16), (58.0, 32.0, 7.0, 15), (62.0, 14.0, 6.5, 14),
        (98.0, 26.0, 7.5, 16), (104.0, 42.0, 7.0, 15), (38.0, 32.0, 6.0, 13),
        (118.0, 28.0, 6.5, 14), (70.0, 38.0, 6.0, 13),
    ]
    for i, (bx, by, rad, cnt) in enumerate(bamboo_groves):
        b.add_bamboo_cluster(bx, by, 0.0, radius=rad, count=cnt, h_min=7.0, h_max=11.5, seed=i + 50)

    # Waterfront weeping willows & ancient pines along Canglang canal banks
    for i, (wx, wy, sc) in enumerate([
        (34, -29, 1.15), (62, -29, 1.20), (92, -29, 1.15), (120, -29, 1.15),
        (68, 0, 1.05), (96, 0, 1.05),
    ]):
        b.add_tree_willow(wx, wy, 0.0, scale=sc, seed=i + 70)

    for i, (px, py, sc) in enumerate([
        (38, 54, 1.2), (118, 52, 1.25), (122, 16, 1.15), (56, 52, 1.15),
        (50, -44, 1.2), (96, -44, 1.2),
    ]):
        b.add_tree_pine(px, py, 0.0, scale=sc, seed=i + 90)

    # Waterfront boats & canal lanterns
    b.add_wooden_boat(64.0, -16.0, -1.55, rot_z=0.12, scale=1.05, lantern=True)
    b.add_wooden_boat(106.0, -14.0, -1.55, rot_z=-0.10, scale=1.0, lantern=True)
    for lx in (38.0, 68.0, 98.0, 122.0):
        b.add_lantern_post(lx, -28.8, 0.0, h=3.2)


def main():
    b = SuzhouBuilder("PanmenCanglang")
    build_panmen_west(b)
    build_wumen_bridge(b)
    build_canglang_east(b)
    b.build_and_export(OUT_GLB)


if __name__ == "__main__":
    main()
