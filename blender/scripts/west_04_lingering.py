"""
Station 03: Lingering Garden (留园)
Exports: web/public/assets/models/lingering_garden.glb
Features:
  - Classic Suzhou whitewashed perimeter walls & dark tile coping (粉墙黛瓦) with horse-head gables
  - Central winding emerald pond with natural Taihu rock shores & curved stone bridge
  - Hanbi Mountain Villa (涵碧山房) with cantilevered waterside terrace
  - Iconic 2-story Mingse Pavilion (明瑟楼) & hexagonal Keting Pavilion (可亭)
  - Zigzag covered corridors (曲廊) with glowing carved leak-windows (漏窗)
  - Eastern Courtyard centerpiece: sculpted perforated vertical Taihu rock
    'Cloud-Capped Peak' (冠云峰) + Cloud-Capped Pavilion (冠云楼) & rockeries.
"""
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from west_common import SuzhouBuilder

OUT_GLB = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/lingering_garden.glb"


def build_mingse_pavilion(b, cx, cy, z0=0.0):
    """Iconic 2-story narrow waterside Mingse Pavilion (明瑟楼), faithful to reference 03."""
    # Waterside stone terrace plinth
    b.box_z(cx, cy, z0 - 1.2, z0 + 0.55, 10.4, 8.2, "Mat_GraniteLight")
    # Ground story open dark-wood pavilion colonnade
    z1 = z0 + 0.55
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cylinder(cx + sx * 4.2, cy + sy * 3.2, z1, z1 + 3.6, 0.16, "Mat_DarkWood", sides=6)
    b.box_z(cx, cy, z1 + 0.2, z1 + 3.4, 7.6, 5.2, "Mat_DarkWood")
    b.box_z(cx, cy + 2.68, z1 + 0.5, z1 + 3.1, 6.4, 0.16, "Emissive_Warm_Window")
    b.box_z(cx, cy - 2.68, z1 + 0.5, z1 + 3.1, 6.4, 0.16, "Emissive_Warm_Window")
    # Lower upturned eave skirt
    b.add_upturned_roof(
        cx, cy, z1 + 3.55, 8.6, 6.4, 1.55,
        mat_wood="Mat_DarkWood", mat_gold=None, mat_eave_light="Emissive_Gold_Eave",
        overhang=1.45, flare_z=0.85, flare_xy=0.65, ridge_ratio=0.72, steps=3,
    )
    # Upper 2nd story with signature square white-framed lattice windows (matching 03_lingering_garden.jpg!)
    z2 = z1 + 4.4
    b.box_z(cx, cy, z2, z2 + 3.4, 7.4, 5.4, "Mat_DarkWood")
    for wx in (-2.2, 0.0, 2.2):
        for wz in (0.55, 2.0):
            for sy in (-1, 1):
                b.box_z(cx + wx, cy + sy * 2.75, z2 + wz, z2 + wz + 1.05, 1.45, 0.14, "Mat_WhiteWall")
                b.box_z(cx + wx, cy + sy * 2.82, z2 + wz + 0.14, z2 + wz + 0.91, 1.15, 0.14, "Emissive_Warm_Window")
    # Soaring upper sweeping roof
    b.add_upturned_roof(
        cx, cy, z2 + 3.35, 7.8, 5.8, 2.85,
        mat_wood="Mat_DarkWood", mat_gold="Mat_GoldTrim", mat_eave_light="Emissive_Gold_Eave",
        overhang=1.55, flare_z=1.15, flare_xy=0.85, ridge_ratio=0.58, steps=4,
    )


def main():
    b = SuzhouBuilder("LingeringGarden")

    # 1. Garden Ground Footprint (126m x 106m, Z = -2.2..0.0) with recessed Central Pond
    # South ground band (X in [-63, +63], Y in [-53, -18])
    b.box_z(0.0, -35.5, -2.2, 0.0, 126.0, 35.0, "Mat_GraniteLight")
    # North ground band (X in [-63, +63], Y in [+22, +53])
    b.box_z(0.0, 37.5, -2.2, 0.0, 126.0, 31.0, "Mat_GraniteLight")
    # West ground band (X in [-63, -40], Y in [-18, +22])
    b.box_z(-51.5, 2.0, -2.2, 0.0, 23.0, 40.0, "Mat_GraniteLight")
    # East Courtyard ground (X in [+14, +63], Y in [-18, +22])
    b.box_z(38.5, 2.0, -2.2, 0.0, 49.0, 40.0, "Mat_GraniteLight")

    # 2. Central Winding Pond (X in [-40, +14], Y in [-18, +22])
    b.box_z(-13.0, 2.0, -2.2, -1.0, 56.0, 42.0, "Mat_GraniteDark")
    b.box_z(-13.0, 2.0, -0.95, -0.35, 54.6, 40.6, "Mat_PondWater")

    # Naturalistic Taihu stone pond shoreline boulders + small central rockery island
    shore_rocks = [
        (-37, -14, 3.8), (-39, 4, 4.2), (-36, 18, 4.5), (-22, 21, 5.0),
        (-4, 21, 4.6), (11, 16, 4.2), (13, 0, 3.8), (10, -14, 4.0),
        (-16, 6, 4.8),  # Small central islet rockery
    ]
    for i, (rx, ry, sc) in enumerate(shore_rocks):
        b.add_taihu_rock(rx, ry, -0.8, sc, sc * 0.85, sc * 0.72, seed=i + 1)

    # Low curved stone garden footbridge crossing east-west to central islet
    b.add_arch_bridge(
        cx=2.0, cy=4.0, z_water=-0.35, span_axis="X",
        clear_w=8.0, clear_h=1.9, deck_w=2.4, approach_len=4.5, arch_thick=0.45,
        lantern_mat="Emissive_Warm_Lantern", segs=10,
    )
    # Lotus leaves on pond
    for lx, ly in [(-28, -4), (-25, -7), (-30, 8), (-6, -6), (4, 14), (7, 11), (-18, -9)]:
        b.prism(lx, ly, -0.34, -0.28, 0.95, 0.95, 7, "Mat_LotusLeaf")

    # 3. Classic Suzhou White-Wall Dark-Tile Perimeter Enclosure (粉墙黛瓦) + Horse-head Gables
    b.add_wall(-61.0, -51.0, 61.0, -51.0, h=4.0, wall_mat="Mat_WhiteWall", horse_head=True, leak_windows=True)
    b.add_wall(61.0, -51.0, 61.0, 51.0, h=4.0, wall_mat="Mat_WhiteWall", horse_head=True)
    b.add_wall(61.0, 51.0, -61.0, 51.0, h=4.0, wall_mat="Mat_WhiteWall", horse_head=True)
    b.add_wall(-61.0, 51.0, -61.0, -51.0, h=4.0, wall_mat="Mat_WhiteWall", horse_head=True, leak_windows=True)
    # Partition white wall with moon-gate & leak windows separating Central Pond Garden & Eastern Peak Courtyard
    b.add_wall(17.0, -50.0, 17.0, -8.0, h=3.8, wall_mat="Mat_WhiteWall", horse_head=True, leak_windows=True)
    b.add_wall(17.0, 6.0, 17.0, 50.0, h=3.8, wall_mat="Mat_WhiteWall", horse_head=True, leak_windows=True)

    # 4. Hanbi Mountain Villa (涵碧山房) on South Pond Edge + Cantilevered Water Terrace
    # Stone waterside terrace projecting over pond
    b.box_z(-6.0, -17.0, -1.0, 0.45, 22.0, 6.0, "Mat_GraniteLight")
    for px in (-16.0, -11.0, -6.0, -1.0, 4.0):
        b.box_z(px, -14.2, 0.45, 1.35, 0.35, 0.35, "Mat_GraniteLight")
    b.box_z(-6.0, -14.2, 0.45, 1.05, 21.5, 0.22, "Mat_GraniteLight")
    b.add_hall(-6.0, -25.5, 0.0, 21.0, 11.5, wall_h=4.6, roof_h=3.2, double_eave=False,
               rot_z=math.pi, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.6, stairs_front=False, plaque=True)

    # 5. Iconic 2-Story Mingse Pavilion (明瑟楼) directly west of Hanbi Mountain Villa
    build_mingse_pavilion(b, -22.5, -22.5, z0=0.0)

    # 6. Keting Pavilion (可亭) on NW Rockery Mound & North Shore Halls
    # Rockery hillock on NW corner of pond
    b.add_taihu_rock(-34.0, 24.0, -0.5, 13.0, 11.0, 4.6, seed=20)
    b.add_pavilion(-34.0, 24.0, 3.2, radius=4.0, col_h=3.4, roof_h=3.1, sides=6,
                   plinth_h=0.55, pillar_mat="Mat_DarkWood", gold_mat="Mat_GoldTrim",
                   eave_light="Emissive_Gold_Eave")

    # Yuancui Pavilion / North Hall (远翠阁 & 闻木樨香轩)
    b.add_hall(-6.0, 34.0, 0.0, 20.0, 10.5, wall_h=5.2, roof_h=3.6, double_eave=True,
               rot_z=0.0, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.8)
    # West hillside pavilion (舒啸亭)
    b.add_pavilion(-49.0, 4.0, 1.2, radius=3.6, col_h=3.2, roof_h=2.8, sides=6,
                   pillar_mat="Mat_DarkWood", eave_light="Emissive_Gold_Eave")

    # 7. Famous Zigzag Covered Corridors (曲廊) with Carved Lattice Leak-Windows (漏窗)
    corridors = [
        (-48.0, -36.0, -48.0, -14.0, -1),
        (-48.0, -14.0, -42.0, -14.0, -1),
        (-42.0, -14.0, -42.0, 18.0, -1),
        (-42.0, 18.0, -34.0, 38.0, 1),
        (-34.0, 38.0, -18.0, 38.0, 1),
        (6.0, 36.0, 15.0, 36.0, 1),
        (15.0, 36.0, 15.0, 10.0, 1),
        (-36.0, -38.0, 12.0, -38.0, -1),
        (12.0, -38.0, 12.0, -18.0, 1),
    ]
    for x0, y0, x1, y1, wside in corridors:
        b.add_corridor(x0, y0, x1, y1, z0=0.0, width=2.9, h=3.1,
                       back_wall=True, wall_side=wside, wall_mat="Mat_WhiteWall",
                       wood_mat="Mat_DarkWood", leak_windows=True)

    # 8. EASTERN COURTYARD: Iconic Cloud-Capped Peak (冠云峰) + Cloud-Capped Pavilion (冠云楼)
    # Carved octagonal lotus pool pedestal at (+39, +2)
    b.prism(39.0, 2.0, 0.0, 0.75, 6.2, 6.0, 8, "Mat_GraniteLight")
    b.prism(39.0, 2.0, 0.50, 0.65, 5.4, 5.4, 8, "Mat_PondWater")
    b.prism(39.0, 2.0, 0.60, 1.55, 2.2, 1.85, 8, "Mat_GraniteLight")
    # THE FAMOUS SCULPTED VERTICAL TAIHU ROCK: Cloud-Capped Peak (冠云峰)!
    b.add_taihu_rock(39.0, 2.0, 1.45, 3.8, 2.6, 8.6, seed=77, tall_peak=True)
    # Companion flanking Taihu peaks (瑞云峰 & 岫云峰)
    b.add_taihu_rock(31.5, 4.5, 0.0, 2.2, 1.8, 4.4, seed=78, tall_peak=True)
    b.add_taihu_rock(46.5, 4.0, 0.0, 2.1, 1.7, 4.1, seed=79, tall_peak=True)
    # Dramatic warm uplights highlighting Cloud-Capped Peak from the lotus pool!
    for a_i in range(4):
        a = math.pi * 0.25 + a_i * math.pi * 0.5
        b.box_z(39.0 + 3.2 * math.cos(a), 2.0 + 3.2 * math.sin(a), 0.70, 1.15, 0.45, 0.45, "Emissive_Warm_Uplight")

    # Cloud-Capped Pavilion (冠云楼, 2-story hall) framing the peak from the North
    b.add_hall(39.0, 32.0, 0.0, 24.0, 11.5, wall_h=5.6, roof_h=3.8, double_eave=True,
               rot_z=0.0, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.9)
    # South Eastern Grand Hall (五峰仙馆 / 林泉耆硕之馆)
    b.add_hall(39.0, -30.0, 0.0, 24.0, 13.0, wall_h=5.0, roof_h=3.6, double_eave=False,
               rot_z=math.pi, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.8)
    # East wing garden corridor
    b.add_corridor(54.0, -20.0, 54.0, 24.0, z0=0.0, width=2.8, h=3.1,
                   back_wall=True, wall_side=1, wall_mat="Mat_WhiteWall", wood_mat="Mat_DarkWood")
    # Small Cloud-Capped Pavilion viewing kiosk (冠云亭)
    b.add_pavilion(26.0, -10.0, 0.0, radius=3.2, col_h=3.0, roof_h=2.5, sides=6,
                   pillar_mat="Mat_DarkWood", eave_light="Emissive_Gold_Eave")

    # 9. Lush Garden Vegetation: Crimson Maples, Ancient Pines, Willows & Bamboo
    pines = [
        (-52, 34, 1.15), (-48, -42, 1.1), (-16, 44, 1.15), (8, 44, 1.1),
        (52, 42, 1.2), (52, -42, 1.15), (24, 42, 1.1), (-54, 18, 1.1),
    ]
    for i, (px, py, sc) in enumerate(pines):
        b.add_tree_pine(px, py, 0.0, scale=sc, seed=i + 10)

    maples = [
        (-36, -22, 1.05), (-20, 24, 1.05), (10, -24, 1.0), (26, 16, 1.05),
        (48, -10, 1.0), (-52, -24, 1.1), (-2, -44, 1.0),
    ]
    for i, (mx, my, sc) in enumerate(maples):
        b.add_tree_maple(mx, my, 0.0, scale=sc, seed=i + 40)

    willows = [(-38, -8, 1.0), (11, 8, 0.95), (-14, 21, 1.0)]
    for i, (wx, wy, sc) in enumerate(willows):
        b.add_tree_willow(wx, wy, 0.0, scale=sc, seed=i + 70)

    # Bamboo accents in Eastern Courtyard & West Garden
    b.add_bamboo_cluster(26.0, 22.0, 0.0, radius=4.0, count=10, h_min=6.0, h_max=9.0, seed=1)
    b.add_bamboo_cluster(50.0, 14.0, 0.0, radius=3.8, count=10, h_min=6.0, h_max=9.0, seed=2)
    b.add_bamboo_cluster(-52.0, -8.0, 0.0, radius=4.2, count=10, h_min=6.0, h_max=9.5, seed=3)

    b.build_and_export(OUT_GLB)


if __name__ == "__main__":
    main()
