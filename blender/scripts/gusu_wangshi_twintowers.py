"""
Generate wangshi_twin_pagodas.glb — Station 05:
  West side: Master of the Nets Garden (网师园) centered on Rosy Cloud Pool (彩霞池)
             with Moon Comes with Breeze Pavilion (月到风来亭), Dianchun Yi courtyard,
             Zhuoying Water Pavilion, tiny stone arch bridge & warm lantern reflections.
  East side (~75-85m offset): Suzhou Twin Pagodas (罗汉院双塔) — symmetrical pair of
             33.3m Song-dynasty 7-story octagonal brick pagodas with delicate upturned eaves,
             warm uplighting, golden finials, and ~25m clear drone flight corridor between them!
"""
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gusu_common import clear_scene, create_gusu_palette, SceneBuilder, export_glb


def build_wangshi_garden(sb):
    """West side (X in [-88, +10], Y in [-62, +62]): Master of the Nets Garden (网师园)."""
    # Solid ground platform skirt down to Z=-2.5 surrounding the recessed Rosy Cloud Pool
    # Outer garden base around pond: pond occupies X in [-56, -14], Y in [-24, +20]
    # Build 4 perimeter slabs framing the recessed pond cleanly (no Z-fighting!)
    sb.add_box("courtyard", 34.0, 124.0, 2.5, center=(-73.0, 0.0, -1.25))     # West strip (-90..-56)
    sb.add_box("courtyard", 28.0, 124.0, 2.5, center=(0.0, 0.0, -1.25))       # East strip (-14..+14)
    sb.add_box("courtyard", 42.0, 42.0, 2.5, center=(-35.0, 41.0, -1.25))     # North strip (+20..+62)
    sb.add_box("courtyard", 42.0, 38.0, 2.5, center=(-35.0, -43.0, -1.25))    # South strip (-62..-24)
    # Recessed pond floor + emerald water plane
    sb.add_box("stone_dark", 46.0, 48.0, 1.2, center=(-35.0, -2.0, -1.9))
    sb.add_box("water", 44.0, 46.0, 0.12, center=(-35.0, -2.0, -0.35))

    # Stone coping embankment around Rosy Cloud Pool (彩霞池)
    embank_segs = [
        ((-56, -24), (-56, 20)),
        ((-56, 20), (-14, 20)),
        ((-14, 20), (-14, -24)),
        ((-14, -24), (-56, -24)),
    ]
    for p0, p1 in embank_segs:
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        sb.add_box("stone_light", length + 0.6, 1.2, 0.75,
                   center=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, -0.15), rot_z=ang)

    # Outer white Suzhou garden perimeter walls with undulating dark-tile caps
    wall_pts = [(-88, -58), (10, -58), (10, 58), (-88, 58)]
    for i in range(4):
        sb.add_garden_wall(wall_pts[i], wall_pts[(i + 1) % 4], height=3.8, wave_cap=True)

    # 1. Moon Comes with Breeze Pavilion (月到风来亭) cantilevered on West bank of Rosy Cloud Pool
    sb.add_box("stone_dark", 6.8, 6.8, 2.4, center=(-54.5, -2.0, -0.95))
    sb.add_pavilion(center=(-54.5, -2.0, 0.25), radius=4.1, sides=6, col_h=3.6,
                    podium_h=0.65, double_eave=False, col_mat="dark_wood",
                    bench_mat="warm_wood", lantern=True)
    # Warm golden lantern reflection shimmer floating gently on the pool water below pavilion
    sb.add_cylinder("emissive_warm", 1.85, 1.85, 0.03, segments=12,
                    center=(-49.5, -2.0, -0.27))

    # 2. Zhuoying Water Pavilion (濯缨水阁) on the South shore overhanging water
    sb.add_box("stone_dark", 13.5, 6.5, 2.2, center=(-36.0, -24.5, -0.9))
    sb.add_hall(w=12.5, d=6.2, h=4.2, center=(-36.0, -25.5, 0.0), rot_z=0.0,
                podium_h=0.75, double_eave=False)
    sb.add_ico("emissive_warm", radius=0.30, subdivisions=1, scale=(1.0, 1.0, 1.25),
               center=(-36.0, -21.8, 3.6))
    sb.add_cylinder("emissive_warm", 1.15, 1.15, 0.03, segments=10,
                    center=(-36.0, -19.5, -0.27))

    # 3. Xiaoshan Conggui Xuan & Kan Song Du Hua Xuan (看松读画轩) on North shore
    sb.add_hall(w=15.0, d=8.2, h=4.5, center=(-35.0, 27.5, 0.0), rot_z=0.0,
                podium_h=0.85, double_eave=False)
    # West-side Zhuwai Yizhi Xuan (竹外一枝轩)
    sb.add_hall(w=11.0, d=6.8, h=4.0, center=(-54.0, 23.0, 0.0), rot_z=-0.18,
                podium_h=0.65)

    # 4. Tiny iconic Stone Arch Bridge (引静桥) spanning the SE cove of Rosy Cloud Pool
    sb.add_arch_bridge(span=8.6, width=1.8, arch_h=1.9, center=(-19.5, -14.5, -0.2),
                       rot_z=0.68, lanterns=True)
    # Small rockery peninsula creating the SE cove
    sb.add_taihu_rock_cluster(center=(-16.5, -21.0, -0.4), radius=5.2, height=4.4, lobes=8, seed=51)
    sb.add_taihu_rock_cluster(center=(-16.0, 14.0, -0.4), radius=5.8, height=5.2, lobes=9, seed=52)
    sb.add_taihu_rock_cluster(center=(-52.0, -18.5, -0.4), radius=4.8, height=4.2, lobes=7, seed=53)
    sb.add_taihu_rock_cluster(center=(-50.0, 14.0, -0.4), radius=5.0, height=4.5, lobes=8, seed=54)

    # Covered winding corridors (长廊) connecting pavilions & halls around the pool
    sb.add_corridor_segment((-54.5, 3.5), (-54.5, 18.0), width=2.2, height=3.0, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-54.5, -7.5), (-54.5, -23.0), width=2.2, height=3.0, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-54.5, -23.0), (-43.5, -25.0), width=2.2, height=3.0, lantern=False)
    sb.add_corridor_segment((-28.5, -25.0), (-15.0, -25.0), width=2.2, height=3.0, lantern=True)
    sb.add_corridor_segment((-12.5, -12.0), (-12.5, 18.0), width=2.2, height=3.0, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-26.0, 27.5), (-12.5, 22.0), width=2.2, height=3.0, lantern=False)

    # 5. Dianchun Yi (殿春簃) — intimate NW Ming scholar's courtyard (model of Astor Court)
    sb.add_garden_wall((-86, 12), (-62, 12), height=3.2, wave_cap=False)
    sb.add_garden_wall((-62, 12), (-62, 54), height=3.2, wave_cap=False)
    # Scholar's studio hall at north end of Dianchun Yi
    sb.add_hall(w=13.0, d=7.4, h=4.1, center=(-74.5, 45.0, 0.0), rot_z=0.0, podium_h=0.65)
    # Half-pavilion (冷泉亭) & sculptural Taihu peak + tiny spring pool inside Dianchun Yi
    sb.add_box("water", 6.5, 5.5, 0.12, center=(-76.5, 23.0, 0.05))
    sb.add_taihu_rock_cluster(center=(-79.5, 26.5, 0.0), radius=4.2, height=5.0, lobes=7, seed=55)
    sb.add_pavilion(center=(-68.5, 22.0, 0.0), radius=2.7, sides=4, col_h=3.1,
                    podium_h=0.45, lantern=True)
    sb.add_bamboo_clump(center=(-82.5, 36.0, 0.0), count=8, height=6.5, spread=2.2, seed=56)
    sb.add_bamboo_clump(center=(-66.0, 35.0, 0.0), count=6, height=5.8, spread=1.8, seed=57)

    # 6. Residential halls (万卷堂 / 轿厅) on the eastern & southern residential axes
    sb.add_hall(w=16.0, d=9.0, h=4.6, center=(-2.0, 34.0, 0.0), rot_z=0.0, double_eave=False)
    sb.add_hall(w=16.0, d=9.0, h=4.8, center=(-2.0, 10.0, 0.0), rot_z=0.0, double_eave=True)
    sb.add_suzhou_house(w=13.5, d=7.2, h=6.0, center=(-2.0, -24.0, 0.0), matouqiang=True)
    sb.add_suzhou_house(w=12.0, d=6.8, h=5.8, center=(-73.0, -34.0, 0.0), matouqiang=True)

    # Classical garden trees & lotus pads
    sb.add_willow_tree(center=(-49.0, 19.0, 0.0), height=9.2, lean=(1.4, -1.0), seed=61)
    sb.add_willow_tree(center=(-16.0, -5.0, 0.0), height=8.8, lean=(-1.5, 0.4), seed=62)
    sb.add_pine_tree(center=(-35.0, 38.0, 0.0), height=11.0, seed=63)
    sb.add_pine_tree(center=(-66.0, -14.0, 0.0), height=10.2, seed=64)
    sb.add_pine_tree(center=(-25.0, -39.0, 0.0), height=9.5, seed=65)
    sb.add_pine_tree(center=(-81.0, 4.0, 0.0), height=9.0, seed=66)
    # Floating lotus pads in Rosy Cloud Pool
    for lx, ly, lr in [(-42, 8, 0.9), (-40, 10, 0.75), (-38, 7, 0.85),
                       (-26, -6, 0.95), (-24, -4, 0.8), (-28, -8, 0.7),
                       (-32, 12, 0.85), (-44, -12, 0.8)]:
        sb.add_cylinder("lotus_pad", lr, lr, 0.04, segments=8, center=(lx, ly, -0.26))
        sb.add_ico("lotus_pink", radius=0.18, subdivisions=1, center=(lx + 0.15, ly, -0.16))


def build_twin_pagodas(sb):
    """
    East side (X in [+18, +90], centered at X=+54, ~89m east of Wangshi pool):
    Suzhou Twin Pagodas (罗汉院双塔) — pair of symmetrical 33.3m Song-dynasty
    7-story octagonal brick pagodas with delicate eaves & warm uplighting.
    Spaced 36m apart (X=36 and X=72) leaving ~24m clear drone flight corridor!
    """
    # Flagstone temple plaza + foundation skirt down to Z=-2.5
    sb.add_box("flagstone", 76.0, 108.0, 2.5, center=(54.0, 0.0, -1.25))
    # Connecting traditional stone lane between Wangshi Garden and Twin Pagodas
    sb.add_box("flagstone", 16.0, 108.0, 2.5, center=(14.0, 0.0, -1.25))

    # Ochre-and-white Luohan Yuan temple enclosure walls
    tw_pts = [(20, -48), (88, -48), (88, 48), (20, 48)]
    for i in range(4):
        if i == 0:
            # South wall with grand entrance gate gap
            sb.add_garden_wall((20, -48), (46, -48), height=3.4, wall_mat="ochre_wall", wave_cap=False)
            sb.add_garden_wall((62, -48), (88, -48), height=3.4, wall_mat="ochre_wall", wave_cap=False)
        else:
            sb.add_garden_wall(tw_pts[i], tw_pts[(i + 1) % 4], height=3.4, wall_mat="ochre_wall", wave_cap=False)

    # Southern Temple Mountain Gate (山门)
    sb.add_hall(w=15.0, d=6.2, h=4.0, center=(54.0, -48.0, 0.0), rot_z=0.0,
                podium_h=0.6, wall_mat="ochre_wall")
    sb.add_lantern_string((46, -44, 3.8), (62, -44, 3.8), count=5, sag=0.4, lantern_r=0.26)

    # THE SYMMETRICAL SUZHOU TWIN PAGODAS (东塔 & 西塔, 33.3m tall each!)
    # West Pagoda at (36, 8, 0), East Pagoda at (72, 8, 0) -> 36m separation!
    for px in (36.0, 72.0):
        sb.add_oct_pagoda(
            center=(px, 8.0, 0.0),
            stories=7,
            total_height=33.3,
            base_radius=4.9,
            taper=0.56,
            has_balcony=True,
            has_podium=True,
            podium_h=2.0,
            brick_mat="pagoda_brick",
            eave_mat="dark_tile",
            spire_ratio=0.20,
            emissive_eave="emissive_warm",
            emissive_spire="emissive_gold",
        )
        # Perimeter plaza stone terrace & warm uplight bollards
        sb.add_cylinder("stone_light", 8.5, 8.2, 0.35, segments=8,
                        center=(px, 8.0, 0.175), rot_z=math.pi / 8)
        for k in range(4):
            ang = math.pi * 0.25 + k * math.pi * 0.5
            bx = px + 7.6 * math.cos(ang)
            by = 8.0 + 7.6 * math.sin(ang)
            sb.add_box("stone_dark", 0.45, 0.45, 0.9, center=(bx, by, 0.65))
            sb.add_ico("emissive_warm", radius=0.22, subdivisions=1, center=(bx, by, 1.25))

    # Luohan Yuan Main Hall Ruins (罗汉院正殿石柱遗址) in front (south) of the Twin Pagodas
    sb.add_box("stone_light", 26.0, 14.0, 0.85, center=(54.0, -24.0, 0.425))
    # Authentic carved Song stone pillars standing in solemn geometric rows
    for ix in (-9.0, -3.0, 3.0, 9.0):
        for iy in (-28.0, -20.0):
            sb.add_cylinder("stone_dark", 0.52, 0.45, 0.5, segments=8, center=(54.0 + ix, iy, 1.1))
            sb.add_cylinder("stone_light", 0.34, 0.30, 4.6, segments=8, center=(54.0 + ix, iy, 3.6))
    # Ancient stone archway lintel connecting center pair
    sb.add_box("stone_light", 6.8, 0.72, 0.78, center=(54.0, -20.0, 6.1))
    sb.add_box("emissive_warm", 5.8, 0.18, 0.16, center=(54.0, -20.0, 5.6))

    # North Buddhist Stele Pavilion behind the Twin Pagodas
    sb.add_hall(w=18.0, d=7.8, h=4.2, center=(54.0, 36.0, 0.0), rot_z=0.0,
                podium_h=0.8, wall_mat="ochre_wall")

    # Ancient pines framing the Twin Pagodas courtyard (kept clear of central flight lane!)
    for tx, ty, th, sd in [
        (25.0, -34.0, 10.5, 71),
        (83.0, -34.0, 10.5, 72),
        (24.0, 30.0, 11.2, 73),
        (84.0, 30.0, 11.2, 74),
        (25.0, -8.0, 9.2, 75),
        (83.0, -8.0, 9.2, 76),
    ]:
        sb.add_pine_tree(center=(tx, ty, 0.0), height=th, seed=sd)


def main():
    clear_scene()
    palette = create_gusu_palette()
    sb = SceneBuilder(palette)
    build_wangshi_garden(sb)
    build_twin_pagodas(sb)
    objs = sb.build_objects_by_material(prefix="WangshiTwin")
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    print(f"[STATS] wangshi_twin_pagodas: {len(objs)} meshes, {total_tris} tris")
    export_glb("wangshi_twin_pagodas.glb")


if __name__ == "__main__":
    main()
