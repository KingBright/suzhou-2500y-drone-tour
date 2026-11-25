"""
Station 01: Hanshan Temple & Maple Bridge (寒山寺 & 枫桥)
Exports: web/public/assets/models/hanshan_temple.glb
"""
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from west_common import SuzhouBuilder

OUT_GLB = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/hanshan_temple.glb"


def build_puming_pagoda(b, cx, cy, z0=0.0):
    """42m 5-story square Tang-style Puming Pagoda (普明宝塔)."""
    # 2-tier granite Sumeru terrace base (Z=0..3.6m)
    b.box_z(cx, cy, z0 - 0.5, z0 + 1.8, 17.5, 17.5, "Mat_GraniteDark")
    b.box_z(cx, cy, z0 + 1.8, z0 + 3.6, 14.8, 14.8, "Mat_GraniteLight")
    # Granite balustrade around pedestal
    for sx in (-1, 1):
        b.box_z(cx + sx * 7.1, cy, z0 + 3.6, z0 + 4.45, 0.32, 14.0, "Mat_GraniteLight")
        b.box_z(cx, cy + sx * 7.1, z0 + 3.6, z0 + 4.45, 14.0, 0.32, "Mat_GraniteLight")
    # Approach stairs on West and South sides
    for st in range(5):
        h = (st + 1) * 0.72
        b.box_z(cx - 9.0 - (4 - st) * 0.65, cy, z0, z0 + h, 0.75, 4.6, "Mat_GraniteLight")
        b.box_z(cx, cy - 9.0 - (4 - st) * 0.65, z0, z0 + h, 4.6, 0.75, "Mat_GraniteLight")
    # Warm perimeter uplights around pagoda terrace
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box_z(cx + sx * 6.4, cy + sy * 6.4, z0 + 3.6, z0 + 4.25, 0.55, 0.55, "Emissive_Warm_Uplight")
        b.box_z(cx + sx * 6.4, cy, z0 + 3.6, z0 + 4.15, 0.50, 0.50, "Emissive_Warm_Uplight")
        b.box_z(cx, cy + sx * 6.4, z0 + 3.6, z0 + 4.15, 0.50, 0.50, "Emissive_Warm_Uplight")

    # 5 tapering square Tang-style stories (Z=3.6 to Z=34.5m -> spire reaches exact ~42.2m!)
    stories = [
        (11.2, 5.7, 2.20, 2.4),
        (9.7,  5.2, 2.05, 2.2),
        (8.4,  4.8, 1.90, 2.0),
        (7.2,  4.5, 1.80, 1.85),
        (6.0,  4.2, 3.00, 1.75),  # top story taller pyramidal Tang roof
    ]
    z = z0 + 3.6
    for idx, (w, sh, rh, ovh) in enumerate(stories):
        # White Tang plaster core
        b.box_z(cx, cy, z, z + sh, w - 0.6, w - 0.6, "Mat_WhiteWall")
        # Crimson corner & bay pillars (3 bays per face)
        for s in (-1, 1):
            for t in (-0.5, -0.17, 0.17, 0.5):
                b.cylinder(cx + t * w, cy + s * (w * 0.5), z, z + sh, 0.22, "Mat_CrimsonWood", sides=6)
                b.cylinder(cx + s * (w * 0.5), cy + t * w, z, z + sh, 0.22, "Mat_CrimsonWood", sides=6)
        # Crimson tie beams & dougong band
        b.box_z(cx, cy, z + sh - 0.55, z + sh + 0.15, w + 0.5, w + 0.5, "Mat_CrimsonWood")
        # Wooden gallery balcony railing (stories 2-5)
        if idx > 0:
            bw = w + 1.35
            for s in (-1, 1):
                b.box_z(cx, cy + s * (bw * 0.5), z, z + 0.95, bw, 0.18, "Mat_CrimsonWood")
                b.box_z(cx + s * (bw * 0.5), cy, z, z + 0.95, 0.18, bw, "Mat_CrimsonWood")
        # Warm glowing arched central doorway on all 4 facades
        dw = w * 0.26
        dh = sh * 0.60
        for s in (-1, 1):
            b.box_z(cx, cy + s * (w * 0.5 - 0.22), z + 0.35, z + 0.35 + dh, dw, 0.22, "Emissive_Warm_Window")
            b.box_z(cx + s * (w * 0.5 - 0.22), cy, z + 0.35, z + 0.35 + dh, 0.22, dw, "Emissive_Warm_Window")
        # Wide upturned square Tang-style roof with golden under-eave LEDs
        is_top = (idx == len(stories) - 1)
        b.add_upturned_roof(
            cx, cy, z + sh + 0.05, w, w, rh,
            mat_tile="Mat_DarkTile", mat_ridge="Mat_TileRidge",
            mat_wood="Mat_CrimsonWood",
            mat_gold="Mat_GoldTrim" if is_top else None,
            mat_eave_light="Emissive_Gold_Eave",
            overhang=ovh, flare_z=0.95 + (0.25 if is_top else 0.0), flare_xy=0.75,
            ridge_ratio=0.05 if is_top else 0.72, steps=4,
        )
        # Corner hanging lanterns on lower eaves
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.add_lantern(cx + sx * (w * 0.5 + ovh * 0.8), cy + sy * (w * 0.5 + ovh * 0.8),
                              z + sh - 0.35, scale=0.65)
        z += sh + (rh * 0.48 if not is_top else rh)

    # Tall Golden-Bronze Tang Pagoda Spire (塔刹) reaching exact ~42.2m!
    b.add_pagoda_spire(cx, cy, z - 0.15, height=42.2 - z + 0.15, r_base=1.15)


def build_bell_tower(b, cx, cy, z0=0.0):
    """Hanshan Temple 2-story Bell Tower (钟楼) with hanging bronze bell."""
    # High granite base terrace
    b.box_z(cx, cy, z0 - 0.4, z0 + 2.6, 12.6, 12.6, "Mat_GraniteDark")
    b.box_z(cx, cy, z0 + 2.6, z0 + 3.2, 11.4, 11.4, "Mat_GraniteLight")
    # Ground story crimson pavilion
    z1 = z0 + 3.2
    b.box_z(cx, cy, z1, z1 + 3.8, 7.2, 7.2, "Mat_TempleYellow")
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cylinder(cx + sx * 4.4, cy + sy * 4.4, z1, z1 + 4.0, 0.22, "Mat_CrimsonWood", sides=6)
    b.add_upturned_roof(
        cx, cy, z1 + 3.9, 9.2, 9.2, 2.2,
        mat_wood="Mat_CrimsonWood", mat_gold=None, mat_eave_light="Emissive_Gold_Eave",
        overhang=1.6, flare_z=0.85, flare_xy=0.65, ridge_ratio=0.55, steps=3,
    )
    # Upper open belfry story
    z2 = z1 + 5.1
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cylinder(cx + sx * 3.1, cy + sy * 3.1, z2, z2 + 4.2, 0.22, "Mat_CrimsonWood", sides=6)
    # Railings
    for s in (-1, 1):
        b.box_z(cx, cy + s * 3.5, z2, z2 + 1.0, 7.2, 0.18, "Mat_CrimsonWood")
        b.box_z(cx + s * 3.5, cy, z2, z2 + 1.0, 0.18, 7.2, "Mat_CrimsonWood")
    # Iconic Bronze Hanshan Temple Bell hanging in center!
    b.cylinder(cx, cy, z2 + 2.8, z2 + 4.0, 0.14, "Mat_DarkWood", sides=6)
    b.prism(cx, cy, z2 + 1.0, z2 + 2.8, 1.35, 0.85, 10, "Mat_Bronze", smooth=True)
    b.prism(cx, cy, z2 + 0.8, z2 + 1.05, 1.48, 1.35, 10, "Mat_GoldTrim", smooth=True)
    # Warm bell illumination glow
    b.sphere(cx, cy, z2 + 0.55, 0.65, 0.65, 0.25, 6, 4, "Emissive_Warm_Uplight")
    # Upper octagonal/square sweeping roof
    b.add_polygonal_roof(
        cx, cy, z2 + 4.15, 0.15, 5.8, 3.8, sides=8,
        mat_wood="Mat_CrimsonWood", mat_gold="Mat_GoldTrim",
        mat_eave_light="Emissive_Gold_Eave", flare_z=0.95, flare_r=0.55, finial=True,
    )


def main():
    b = SuzhouBuilder("HanshanTemple")

    # 1. Ground Platforms & Stone-Embanked Maple Canal (枫江)
    # East main temple bank (X in [-30, +70], Y in [-58, +58])
    b.box_z(20.0, 0.0, -2.4, 0.0, 100.0, 116.0, "Mat_GraniteLight")
    # Stone canal quay wall along West edge of temple bank (X = -30)
    b.box_z(-30.0, 0.0, -2.4, 0.25, 1.8, 116.0, "Mat_GraniteDark")
    # West far bank across Maple Canal (X in [-78, -54], Y in [-58, +58])
    b.box_z(-66.0, 0.0, -2.4, 0.0, 24.0, 116.0, "Mat_GraniteLight")
    b.box_z(-54.0, 0.0, -2.4, 0.25, 1.8, 116.0, "Mat_GraniteDark")
    # Maple Canal water surface (X in [-54, -30], Y in [-58, +58], Z = -0.75)
    b.box_z(-42.0, 0.0, -1.5, -0.75, 24.4, 116.0, "Mat_PondWater")

    # 2. Iconic Single-Arch Stone Maple Bridge (枫桥) spanning the canal in SW foreground
    # Span axis = 'X' so deck crosses East-West over the North-South canal!
    b.add_arch_bridge(
        cx=-42.0, cy=-26.0, z_water=-0.75, span_axis="X",
        clear_w=14.5, clear_h=5.4, deck_w=5.4, approach_len=11.0, arch_thick=0.95,
    )
    # Stone steps & moored Jiangnan black-awning fishing boats ("江枫渔火")
    b.add_wooden_boat(-45.5, -6.0, -0.72, rot_z=1.48, scale=1.05, lantern=True)
    b.add_wooden_boat(-38.5, 16.0, -0.72, rot_z=-1.65, scale=0.95, lantern=True)
    b.add_wooden_boat(-43.0, -45.0, -0.72, rot_z=1.55, scale=1.0, lantern=True)

    # Traditional Jiangnan white-wall riverside pavilion & houses on far west bank
    b.add_hall(-65.0, -10.0, 0.0, 12.0, 9.0, wall_h=4.0, roof_h=2.8, double_eave=False,
               rot_z=math.pi * 0.5, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light=None, plinth_h=0.5, stairs_front=False, plaque=False)
    b.add_hall(-65.0, 14.0, 0.0, 14.0, 9.5, wall_h=4.2, roof_h=3.0, double_eave=False,
               rot_z=math.pi * 0.5, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light=None, plinth_h=0.5, stairs_front=False, plaque=False)
    b.add_pavilion(-60.0, -34.0, 0.0, radius=3.8, col_h=3.4, roof_h=2.9, sides=6,
                   pillar_mat="Mat_CrimsonWood", eave_light="Emissive_Gold_Eave")

    # 3. Iconic Yellow Hanshan Temple Screen Wall (照壁) facing Maple Bridge & Canal
    # Located right at the eastern waterfront plaza (X = -25.5, Y = -18..+6)
    b.add_wall(-25.5, -15.0, -25.5, 3.0, z0=0.0, h=4.8, thickness=1.0,
               wall_mat="Mat_TempleYellow", tile_mat="Mat_DarkTile", pilaster_step=6.0)
    # Red-gold calligraphic plaque on screen wall facing West ("寒山寺")
    b.box_z(-26.1, -6.0, 1.8, 3.7, 0.25, 5.2, "Mat_PlaqueRed")
    b.box_z(-26.25, -6.0, 2.0, 3.5, 0.14, 4.6, "Mat_GoldTrim")
    b.box_z(-26.3, -6.0, 0.2, 0.65, 0.45, 5.4, "Emissive_Warm_Uplight")

    # 4. Ochre-Yellow Temple Perimeter Walls (黄墙黛瓦) enclosing temple grounds
    b.add_wall(-18.0, -48.0, 62.0, -48.0, h=4.4, wall_mat="Mat_TempleYellow")
    b.add_wall(62.0, -48.0, 62.0, 52.0, h=4.4, wall_mat="Mat_TempleYellow")
    b.add_wall(62.0, 52.0, -18.0, 52.0, h=4.4, wall_mat="Mat_TempleYellow")
    b.add_wall(-18.0, 52.0, -18.0, 6.0, h=4.4, wall_mat="Mat_TempleYellow")
    b.add_wall(-18.0, -48.0, -18.0, -18.0, h=4.4, wall_mat="Mat_TempleYellow")

    # Temple Mountain Gate (山门殿) facing West toward Screen Wall & Maple Bridge
    b.add_hall(-16.0, -6.0, 0.0, 16.0, 8.5, wall_h=4.6, roof_h=3.4, double_eave=False,
               rot_z=-math.pi * 0.5, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               eave_light="Emissive_Gold_Eave", plinth_h=0.8)

    # 5. Courtyard Incense Burner (香炉) & Stone Lanterns
    b.box_z(0.0, -4.0, 0.0, 0.7, 4.2, 4.2, "Mat_GraniteLight")
    b.box_z(0.0, -4.0, 0.7, 2.3, 2.4, 1.6, "Mat_Bronze")
    b.box_z(0.0, -4.0, 2.3, 2.65, 1.8, 1.1, "Emissive_Warm_Lantern")
    for ly in (-12.0, 4.0):
        b.add_lantern_post(-6.0, ly, 0.0, h=3.4)
        b.add_lantern_post(4.0, ly, 0.0, h=3.4)

    # 6. Grand Mahavira Hall (大雄宝殿) - Double-eave upturned dark-tile roofs & gold ridges
    b.add_hall(18.0, -4.0, 0.0, 28.0, 18.0, wall_h=6.6, roof_h=5.2, double_eave=True,
               rot_z=-math.pi * 0.5, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=1.4)

    # Flanking Side Halls (东西配殿) & Sutra Library (藏经楼)
    b.add_hall(2.0, -34.0, 0.0, 22.0, 9.5, wall_h=4.4, roof_h=3.0, double_eave=False,
               rot_z=0.0, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.8)
    b.add_hall(2.0, 26.0, 0.0, 22.0, 9.5, wall_h=4.4, roof_h=3.0, double_eave=False,
               rot_z=math.pi, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.8)
    # Rear Dharma Hall (法堂)
    b.add_hall(46.0, -4.0, 0.0, 22.0, 12.0, wall_h=5.2, roof_h=3.8, double_eave=False,
               rot_z=-math.pi * 0.5, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=1.0)

    # 7. Bell Tower (钟楼) in SE temple garden
    build_bell_tower(b, 38.0, -32.0, z0=0.0)

    # 8. 42m 5-Story Square Tang-Style Puming Pagoda (普明宝塔) in NE temple precinct
    build_puming_pagoda(b, 38.0, 30.0, z0=0.0)

    # 9. Lush Riverbank Weeping Willows, Ancient Temple Pines & Autumn Maples
    willow_spots = [
        (-32.0, -42.0, 1.15), (-32.0, -14.0, 1.05), (-32.0, 12.0, 1.15), (-32.0, 36.0, 1.20),
        (-52.0, -46.0, 1.10), (-52.0, -12.0, 1.00), (-52.0, 26.0, 1.15), (-52.0, 44.0, 1.05),
    ]
    for i, (wx, wy, sc) in enumerate(willow_spots):
        b.add_tree_willow(wx, wy, 0.0, scale=sc, seed=i)

    pine_spots = [
        (-8.0, -26.0, 1.1), (-8.0, 16.0, 1.15), (16.0, -36.0, 1.1), (16.0, 34.0, 1.2),
        (54.0, -38.0, 1.2), (54.0, 14.0, 1.1), (54.0, 44.0, 1.25), (18.0, 42.0, 1.15),
        (-10.0, 42.0, 1.1), (-24.0, 28.0, 1.15), (-24.0, -40.0, 1.05),
    ]
    for i, (px, py, sc) in enumerate(pine_spots):
        b.add_tree_pine(px, py, 0.0, scale=sc, seed=i + 30)

    maple_spots = [
        (-22.0, -24.0, 1.05), (-22.0, 14.0, 1.0), (24.0, -22.0, 1.0), (24.0, 16.0, 1.05),
        (-58.0, 2.0, 1.1), (-58.0, 34.0, 1.0),
    ]
    for i, (mx, my, sc) in enumerate(maple_spots):
        b.add_tree_maple(mx, my, 0.0, scale=sc, seed=i + 60)

    # Waterfront warm lantern posts along canal quay
    for ly in (-46.0, -14.0, 10.0, 32.0):
        b.add_lantern_post(-31.2, ly, 0.0, h=3.2)
        b.add_lantern_post(-52.8, ly, 0.0, h=3.2)

    b.build_and_export(OUT_GLB)


if __name__ == "__main__":
    main()
