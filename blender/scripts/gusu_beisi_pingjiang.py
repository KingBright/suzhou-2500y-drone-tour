"""
Generate beisi_pingjiang.glb — Station 06:
  West/North Focal Hero: 76m Beisi Pagoda (北寺塔 / 报恩寺塔) — monumental 9-story
      octagonal pagoda with sweeping upturned double eaves, dark timber balconies,
      vermilion railings, golden spire finial & glowing warm eave bands, plus Bao'en Temple halls.
  East/South Extension: Pingjiang Road Historic Canal Street (平江路) — parallel recessed canal
      & flagstone lane, continuous 2-story white-wall grey-tile Suzhou timber houses with
      Matouqiang gables, 3 arched stone bridges, weeping willows, glowing strings of red
      lanterns (Emissive_Warm), and wooden awning boats (乌篷船).
"""
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gusu_common import clear_scene, create_gusu_palette, SceneBuilder, export_glb


def build_beisi_temple(sb):
    """West/North hero zone (X in [-78, +32], Y in [-85, +85]): 76m Beisi Pagoda & Bao'en Temple."""
    # Temple stone plaza ground slab with skirt down to Z=-2.5
    sb.add_box("flagstone", 112.0, 174.0, 2.5, center=(-22.0, 0.0, -1.25))

    # Ochre temple perimeter walls enclosing Bao'en Temple
    w_pts = [(-74, -80), (28, -80), (28, 80), (-74, 80)]
    for i in range(4):
        if i == 0:
            sb.add_garden_wall((-74, -80), (-26, -80), height=4.2, wall_mat="ochre_wall", wave_cap=False)
            sb.add_garden_wall((-4, -80), (28, -80), height=4.2, wall_mat="ochre_wall", wave_cap=False)
        else:
            sb.add_garden_wall(w_pts[i], w_pts[(i + 1) % 4], height=4.2, wall_mat="ochre_wall", wave_cap=False)

    # THE MONUMENTAL 76m BEISI PAGODA (北寺塔) at local (-15, +8, 0)
    px, py = -15.0, 8.0
    # Broad square-to-octagonal monumental terrace base
    sb.add_box("stone_light", 34.0, 34.0, 1.1, center=(px, py, 0.55))
    # 4 grand staircases on N/S/E/W
    for ang in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
        sx = px + 18.2 * math.cos(ang)
        sy = py + 18.2 * math.sin(ang)
        sb.add_box("stone_dark", 3.6, 5.2, 1.0, center=(sx, sy, 0.5), rot_z=ang)
    # 76m 9-story octagonal pagoda (podium sits on top of terrace at Z=1.0 -> apex at Z=76.0m!)
    sb.add_oct_pagoda(
        center=(px, py, 1.0),
        stories=9,
        total_height=75.0,
        base_radius=10.4,
        taper=0.50,
        has_balcony=True,
        has_podium=True,
        podium_h=2.8,
        brick_mat="white_wall",
        eave_mat="dark_tile",
        spire_ratio=0.175,
        emissive_eave="emissive_warm",
        emissive_spire="emissive_gold",
    )
    # Warm golden perimeter uplights around Beisi Pagoda terrace
    for k in range(8):
        ang = math.pi / 8 + k * math.pi / 4
        ux = px + 15.6 * math.cos(ang)
        uy = py + 15.6 * math.sin(ang)
        sb.add_box("stone_dark", 0.55, 0.55, 1.1, center=(ux, uy, 1.55))
        sb.add_ico("emissive_gold", radius=0.28, subdivisions=1, center=(ux, uy, 2.25))

    # Bao'en Temple Main Hall (大雄宝殿) south of Beisi Pagoda
    sb.add_hall(w=26.0, d=14.0, h=6.0, center=(-15.0, -34.0, 0.0), rot_z=0.0,
                podium_h=1.2, double_eave=True, col_mat="vermilion", wall_mat="ochre_wall")
    # Temple Mountain Gate (报恩寺山门) at south wall
    sb.add_hall(w=20.0, d=8.5, h=4.8, center=(-15.0, -78.0, 0.0), rot_z=0.0,
                podium_h=0.8, double_eave=False, col_mat="vermilion", wall_mat="ochre_wall")
    # Copper Incense Burner (香炉) between Main Hall & Pagoda
    sb.add_cylinder("bronze", 1.2, 1.4, 2.6, segments=8, center=(-15.0, -18.5, 1.3))
    sb.add_ico("emissive_warm", radius=0.45, subdivisions=1, center=(-15.0, -18.5, 2.8))

    # North Guanyin Hall (观音殿 / 楠木观音殿)
    sb.add_hall(w=22.0, d=11.0, h=5.0, center=(-15.0, 56.0, 0.0), rot_z=0.0,
                podium_h=1.0, double_eave=False, col_mat="dark_wood", wall_mat="ochre_wall")

    # Flanking East & West Temple Cloisters
    sb.add_hall(w=32.0, d=7.2, h=4.0, center=(-55.0, -34.0, 0.0), rot_z=math.pi * 0.5,
                podium_h=0.6, wall_mat="ochre_wall")
    sb.add_hall(w=32.0, d=7.2, h=4.0, center=(16.0, -34.0, 0.0), rot_z=math.pi * 0.5,
                podium_h=0.6, wall_mat="ochre_wall")

    # Serene NW Temple Garden Pool (梅圃) with pavilion & rockery
    sb.add_box("water", 24.0, 26.0, 0.12, center=(-52.0, 44.0, 0.05))
    sb.add_taihu_rock_cluster(center=(-62.0, 52.0, 0.0), radius=5.5, height=5.8, lobes=8, seed=81)
    sb.add_pavilion(center=(-46.0, 38.0, 0.0), radius=3.5, sides=6, col_h=3.4,
                    podium_h=0.6, lantern=True)

    # Ancient temple pines & cypresses
    for tx, ty, th, sd in [
        (-42.0, -6.0, 12.0, 82),
        (12.0, -6.0, 12.0, 83),
        (-42.0, 22.0, 11.5, 84),
        (12.0, 22.0, 11.5, 85),
        (-36.0, -58.0, 10.8, 86),
        (6.0, -58.0, 10.8, 87),
        (-58.0, 14.0, 11.0, 88),
    ]:
        sb.add_pine_tree(center=(tx, ty, 0.0), height=th, seed=sd)


def build_pingjiang_road(sb):
    """
    East/South district (X in [+34, +124], Y in [-96, +94]):
    Pingjiang Road Historic Canal Street (平江路) — parallel canal (X=72..88)
    and flagstone lane (X=58..72), continuous 2-story white-wall dark-tile houses,
    3 stone arch bridges, weeping willows, strings of red lanterns & wooden awning boats!
    """
    # West bank ground slab (X in [+34, +72]) & East bank ground slab (X in [+88, +124])
    sb.add_box("flagstone", 38.0, 194.0, 2.5, center=(53.0, -1.0, -1.25))
    sb.add_box("courtyard", 36.0, 194.0, 2.5, center=(106.0, -1.0, -1.25))

    # Recessed Pingjiang Canal bed & emerald water surface (X in [+72, +88], width=16m)
    sb.add_box("stone_dark", 18.0, 194.0, 1.0, center=(80.0, -1.0, -2.0))
    sb.add_box("water", 16.4, 194.0, 0.12, center=(80.0, -1.0, -0.50))

    # Stone canal embankments (驳岸) on west (X=72) and east (X=88) edges
    for ex in (71.6, 88.4):
        sb.add_box("stone_light", 0.9, 194.0, 2.1, center=(ex, -1.0, -0.95))
        # Low stone coping rail along lane side
        if ex < 80:
            for ry in range(-88, 90, 12):
                sb.add_box("stone_dark", 0.45, 7.2, 0.48, center=(71.4, ry, 0.24))

    # Continuous 2-story white-wall grey-tile Suzhou timber houses along WEST side of flagstone lane
    # Facing East (+X) onto the flagstone lane (X=60..71)
    west_houses = [
        (-86, 13.5, 7.6, 6.2, True, False),
        (-71, 12.0, 7.2, 5.8, False, True),
        (-57, 14.0, 7.6, 6.4, True, False),
        (-41, 13.0, 7.4, 6.0, True, True),
        (-26, 12.5, 7.2, 6.2, False, False),
        (-11, 14.5, 7.8, 6.5, True, True),
        (6,   13.0, 7.4, 6.0, True, False),
        (21,  12.0, 7.2, 5.8, False, True),
        (36,  14.0, 7.6, 6.4, True, False),
        (52,  13.0, 7.4, 6.0, True, True),
        (68,  12.5, 7.2, 6.2, False, False),
        (83,  13.5, 7.6, 6.0, True, False),
    ]
    for hy, hw, hd, hh, mq, bal in west_houses:
        sb.add_suzhou_house(
            w=hw, d=hd, h=hh, stories=2,
            center=(51.5, hy, 0.0), rot_z=math.pi * 0.5,
            matouqiang=mq, warm_windows=True, waterfront_balcony=bal,
            wall_mat="white_wall" if mq else "cream_wall"
        )
        # Secondary back-courtyard houses behind west row for rich depth
        if hy in (-71, -41, -11, 21, 52):
            sb.add_suzhou_house(
                w=hw * 0.88, d=6.4, h=5.4, stories=2,
                center=(39.5, hy, 0.0), rot_z=math.pi * 0.5,
                matouqiang=not mq, warm_windows=True
            )

    # Continuous 2-story waterfront Suzhou houses directly on the EAST embankment (临水粉墙黛瓦)
    # Facing West (-X) over the canal with cantilevered timber balconies!
    east_houses = [
        (-85, 13.0, 7.4, 6.2, True, True),
        (-70, 12.5, 7.0, 5.8, False, True),
        (-54, 14.5, 7.6, 6.5, True, True),
        (-38, 12.0, 7.2, 5.8, True, False),
        (-23, 13.5, 7.4, 6.2, False, True),
        (-7,  14.0, 7.6, 6.4, True, True),
        (10,  12.5, 7.2, 5.8, True, False),
        (25,  13.5, 7.4, 6.2, False, True),
        (41,  14.0, 7.6, 6.4, True, True),
        (57,  12.0, 7.2, 5.8, True, False),
        (73,  13.5, 7.4, 6.2, False, True),
        (86,  11.5, 7.0, 5.8, True, True),
    ]
    for hy, hw, hd, hh, mq, bal in east_houses:
        sb.add_suzhou_house(
            w=hw, d=hd, h=hh, stories=2,
            center=(95.0, hy, 0.0), rot_z=-math.pi * 0.5,
            matouqiang=mq, warm_windows=True, waterfront_balcony=bal,
            wall_mat="white_wall" if mq else "cream_wall"
        )
        # Back row east courtyard residences
        if hy in (-70, -38, -7, 25, 57, 86):
            sb.add_suzhou_house(
                w=12.0, d=6.8, h=5.6, stories=2,
                center=(110.5, hy, 0.0), rot_z=-math.pi * 0.5,
                matouqiang=True, warm_windows=True
            )

    # 3 Classic Arched Stone Bridges spanning the Pingjiang Canal (X=80)
    # Clear vaulted arch openings above water!
    for by in (-62.0, 2.0, 64.0):
        sb.add_arch_bridge(
            span=17.4, width=3.4, arch_h=3.6,
            center=(80.0, by, -0.25), rot_z=0.0, lanterns=True
        )

    # Graceful Weeping Willows leaning over the Pingjiang Canal
    willows = [
        (70.5, -76.0, 8.8, (1.8, 0.3), 91),
        (70.5, -44.0, 9.4, (2.0, -0.2), 92),
        (70.5, -16.0, 8.6, (1.7, 0.4), 93),
        (70.5,  18.0, 9.2, (1.9, -0.3), 94),
        (70.5,  46.0, 8.8, (1.8, 0.2), 95),
        (70.5,  78.0, 9.0, (1.7, -0.2), 96),
        (89.2, -30.0, 8.5, (-1.8, 0.3), 97),
        (89.2,  32.0, 8.8, (-1.9, -0.2), 98),
    ]
    for wx, wy, wh, lean, sd in willows:
        sb.add_willow_tree(center=(wx, wy, 0.0), height=wh, lean=lean, seed=sd)

    # Glowing Strings of Red Lanterns (Emissive_Warm_LanternRed) across the canal & along lane eaves!
    for ly in (-80, -48, -22, 16, 44, 76):
        sb.add_lantern_string((57.0, ly, 5.4), (90.0, ly + 4.0, 5.4),
                              count=7, sag=1.15, lantern_r=0.28, mat="emissive_red")
    # Longitudinal eave lantern strings along the flagstone lane
    for y0, y1 in [(-88, -56), (-50, -14), (-8, 28), (34, 82)]:
        sb.add_lantern_string((57.8, y0, 4.4), (57.8, y1, 4.4),
                              count=6, sag=0.35, lantern_r=0.25, mat="emissive_red")

    # 5 Traditional Wooden Awning Boats (摇橹乌篷船) gliding along the Pingjiang Canal
    boats = [
        (78.5, -78.0, math.pi * 0.5 + 0.05),
        (81.5, -36.0, -math.pi * 0.5 + 0.04),
        (79.0, -14.0, math.pi * 0.5 - 0.06),
        (81.0,  26.0, math.pi * 0.5 + 0.04),
        (78.8,  48.0, -math.pi * 0.5 - 0.05),
    ]
    for bx, by, br in boats:
        sb.add_wooden_boat(center=(bx, by, -0.45), rot_z=br, length=6.8, width=1.65)


def main():
    clear_scene()
    palette = create_gusu_palette()
    sb = SceneBuilder(palette)
    build_beisi_temple(sb)
    build_pingjiang_road(sb)
    objs = sb.build_objects_by_material(prefix="BeisiPingjiang")
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    print(f"[STATS] beisi_pingjiang: {len(objs)} meshes, {total_tris} tris")
    export_glb("beisi_pingjiang.glb")


if __name__ == "__main__":
    main()
