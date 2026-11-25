"""
Generate shizilin_garden.glb — Station 07 South (shizilinAnchor: x=210, y=1.6, z=-95):
  Lion Grove Garden (狮子林) — famous dramatic sculpted Taihu rockery labyrinth
  with caves/arches/bridges/peaks (Nine Lions Peak), central pond, marble boat
  pavilion (石舫), nine-turn zigzag bridge (九曲桥), Zhenqu Pavilion (真趣亭),
  Yanyu Hall, covered corridors, and white perimeter garden walls.
"""
import math
import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gusu_common import clear_scene, create_gusu_palette, SceneBuilder, export_glb


def build_rockery_labyrinth(sb):
    """
    Signature Taihu Rockery Labyrinth (假山迷宫) on East/Southeast of pond:
    Multi-layered sculpted Taihu limestone caves, winding upper footpaths,
    stone rockery bridges, and dramatic Nine Lions Peak (九狮峰) pinnacles!
    """
    # Base rockery mass with hollow cave archways (forming a genuine navigable visual maze)
    # Build two main sculpted ridges flanking a central canyon/cave channel + overhead rock bridges!
    west_ridge = [
        (10.0, -14.0, 5.2, 6.2, 111),
        (12.5, -5.0,  5.5, 7.6, 112),
        (11.0,  5.0,  5.0, 6.8, 113),
        (13.0, 14.0,  4.8, 5.8, 114),
    ]
    east_ridge = [
        (24.0, -16.0, 5.6, 7.2, 115),
        (26.5, -6.0,  6.2, 9.4, 116),  # Nine Lions Peak (九狮峰) monumental crag!
        (25.0,  4.5,  5.8, 8.2, 117),
        (23.5, 14.5,  5.2, 6.4, 118),
    ]
    south_ridge = [
        (2.0,  -19.5, 4.8, 5.4, 119),
        (17.5, -21.0, 5.4, 6.5, 120),
    ]
    for cx, cy, rad, h, sd in west_ridge + east_ridge + south_ridge:
        sb.add_taihu_rock_cluster(center=(cx, cy, -0.4), radius=rad, height=h, lobes=9, seed=sd)

    # Sculpted overhanging rockery cave lintels / natural stone arches spanning the canyon (X=12..24)
    cave_arches = [
        (18.0, -10.5, 4.2, 10.5, 3.2, 0.15),
        (18.5,   0.0, 5.0, 11.2, 3.6, -0.10),
        (18.0,  10.0, 3.8, 10.0, 3.0, 0.18),
    ]
    rng = random.Random(130)
    for ax, ay, az, span, w, rz in cave_arches:
        # Stone footpath bridge slab atop the rockery cave arch
        sb.add_box("stone_light", span, w * 0.65, 0.45, center=(ax, ay, az), rot_z=rz)
        # Flanking craggy Taihu arch stones clinging underneath & alongside
        for ox in (-2.6, 0.0, 2.6):
            sb.add_ico("taihu_rock", radius=1.55, subdivisions=1,
                       scale=(1.35, 1.0, 0.72),
                       center=(ax + ox, ay, az - 0.55),
                       rot_euler=(rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rz),
                       jitter=0.30, rng=rng)

    # Nine Lions Peak dramatic vertical perforated pinnacles rising atop the east ridge
    lion_peaks = [
        (25.5, -7.5, 7.6, 1.4, 2.8, 141),
        (27.8, -5.0, 8.8, 1.6, 3.2, 142),
        (26.2, -2.5, 7.2, 1.3, 2.5, 143),
        (24.5,  3.5, 7.8, 1.5, 2.7, 144),
        (27.0,  6.0, 6.8, 1.3, 2.4, 145),
        (22.5, -9.0, 6.2, 1.2, 2.2, 146),
        (23.5,  8.5, 6.4, 1.3, 2.3, 147),
        (14.5, -4.5, 6.6, 1.3, 2.4, 148),
        (13.0,  4.8, 6.2, 1.2, 2.2, 149),
    ]
    for px, py, pz, r, hh, sd in lion_peaks:
        r_loc = random.Random(sd)
        sb.add_ico("taihu_rock", radius=r, subdivisions=2, scale=(1.0, 0.85, hh / r),
                   center=(px, py, pz), jitter=0.34, rng=r_loc)
        # Secondary sculpted limestone crag jutting outward (瘦皱漏透)
        sb.add_ico("taihu_dark", radius=r * 0.72, subdivisions=2,
                   scale=(1.15, 0.78, 0.85),
                   center=(px + r_loc.uniform(-1.1, 1.1), py + r_loc.uniform(-1.1, 1.1), pz - 1.2),
                   jitter=0.32, rng=r_loc)

    # Carved stone staircase flights climbing through the Taihu rockery labyrinth
    for sy_i, (sx, sy, sz, rot) in enumerate([
        (15.0, -14.5, 1.6, 0.2),
        (18.5,  -4.0, 2.8, -0.15),
        (21.0,   6.0, 3.2, 0.35),
    ]):
        for step in range(5):
            sb.add_box("stone_light", 1.8, 0.65, 0.28,
                       center=(sx + step * 0.45 * math.cos(rot),
                               sy + step * 0.45 * math.sin(rot),
                               sz + step * 0.32), rot_z=rot)

    # Warm concealed rockery cave uplights (Emissive_Warm) making the labyrinth glow at dusk!
    for lx, ly, lz in [(17.5, -10.0, 1.2), (18.5, 0.5, 1.5), (18.0, 10.0, 1.1), (25.5, -5.5, 4.5)]:
        sb.add_ico("emissive_warm", radius=0.32, subdivisions=1, center=(lx, ly, lz))

    # Feipu Pavilion (飞瀑亭) perched dramatically atop the north-east rockery peak!
    sb.add_pavilion(center=(24.5, 14.0, 4.6), radius=2.8, sides=6, col_h=3.0,
                    podium_h=0.5, lantern=True)


def build_marble_boat(sb):
    """Iconic Lion Grove Marble Boat Pavilion (石舫) moored on the West edge of the pond."""
    bx, by = -20.0, 4.0
    # Carved stone boat hull resting in the water
    rings = [
        [(-2.4, -7.2, 0.45), (2.4, -7.2, 0.45), (2.0, -7.2, -0.55), (-2.0, -7.2, -0.55)],
        [(-2.8, -2.0, 0.50), (2.8, -2.0, 0.50), (2.4, -2.0, -0.55), (-2.4, -2.0, -0.55)],
        [(-2.8,  3.5, 0.50), (2.8,  3.5, 0.50), (2.4,  3.5, -0.55), (-2.4,  3.5, -0.55)],
        [(-1.6,  7.5, 0.65), (1.6,  7.5, 0.65), (1.1,  7.5, -0.45), (-1.1,  7.5, -0.45)],
    ]
    sb.add_loft("stone_light", rings, closed_caps=True, center=(bx, by, 0.0))
    # Aft & Fore carved stone railings
    sb.add_box("stone_dark", 5.2, 0.22, 0.72, center=(bx, by - 7.0, 0.85))
    sb.add_box("stone_light", 3.2, 0.22, 0.72, center=(bx, by + 7.2, 0.95))
    # Two-part classical timber boat pavilion superstructure
    # Main cabin (center-aft)
    sb.add_box("dark_wood", 4.6, 8.2, 3.0, center=(bx, by - 1.5, 2.0))
    sb.add_box("emissive_win", 4.72, 6.8, 1.9, center=(bx, by - 1.5, 2.1))
    sb.add_suzhou_roof(w=5.0, d=8.6, h=1.8, center=(bx, by - 1.5, 3.45), rot_z=math.pi * 0.5,
                       eave_overhang=0.75, corner_lift=0.45, hip_gable=True, add_ribs=False)
    # Upper lookout stern deck cabin
    sb.add_box("dark_wood", 4.0, 4.2, 2.2, center=(bx, by - 4.4, 4.8))
    sb.add_box("emissive_win", 4.12, 3.2, 1.3, center=(bx, by - 4.4, 4.8))
    sb.add_suzhou_roof(w=4.4, d=4.6, h=1.55, center=(bx, by - 4.4, 5.85), rot_z=math.pi * 0.5,
                       eave_overhang=0.65, corner_lift=0.40, hip_gable=True, add_ribs=False)
    # Warm bow lantern
    sb.add_ico("emissive_warm", radius=0.28, subdivisions=1, scale=(1.0, 1.0, 1.3),
               center=(bx, by + 6.2, 2.5))
    # Short stone gangplank connecting Marble Boat to West shore
    sb.add_box("stone_light", 4.2, 1.8, 0.28, center=(bx - 4.2, by - 1.5, 0.35))


def build_shizilin(sb):
    # Perimeter ground slabs framing recessed central pond (X in [-24, +14], Y in [-18, +20])
    # Skirt extends cleanly down to Z=-2.5
    sb.add_box("courtyard", 24.0, 88.0, 2.5, center=(-36.0, 0.0, -1.25))    # West (-48..-24)
    sb.add_box("courtyard", 34.0, 88.0, 2.5, center=(31.0, 0.0, -1.25))     # East (+14..+48)
    sb.add_box("courtyard", 38.0, 24.0, 2.5, center=(-5.0, 32.0, -1.25))    # North (+20..+44)
    sb.add_box("courtyard", 38.0, 26.0, 2.5, center=(-5.0, -31.0, -1.25))   # South (-44..-18)

    # Central Pond bed & emerald water surface
    sb.add_box("stone_dark", 42.0, 42.0, 1.0, center=(-5.0, 1.0, -2.0))
    sb.add_box("water", 40.0, 40.0, 0.12, center=(-5.0, 1.0, -0.35))

    # White Suzhou perimeter walls with undulating wave-tile caps
    pts = [(-46, -42), (46, -42), (46, 42), (-46, 42)]
    for i in range(4):
        sb.add_garden_wall(pts[i], pts[(i + 1) % 4], height=3.8, wave_cap=True)

    # 1. Dramatic Taihu Rockery Labyrinth (East & SE)
    build_rockery_labyrinth(sb)

    # 2. Marble Boat Pavilion (石舫) on West bank
    build_marble_boat(sb)

    # 3. Nine-Turn Zigzag Bridge (九曲桥) & Central Lake Pavilion (湖心亭)
    zigzag_pts = [
        (-24.0, -8.0),
        (-16.0, -8.0),
        (-13.0, -2.0),
        (-5.5,  -2.0),
        (-1.5,   3.5),
        (5.5,    3.5),
        (9.5,   -1.5),
    ]
    sb.add_zigzag_bridge(zigzag_pts, width=1.85, z_deck=0.22, with_rails=True)
    # Central Lake Pavilion (湖心亭) on stone pier in the middle of the pond
    sb.add_cylinder("stone_dark", 4.6, 4.4, 2.2, segments=8, center=(-3.5, 4.5, -0.85))
    sb.add_pavilion(center=(-3.5, 4.5, 0.25), radius=3.6, sides=8, col_h=3.4,
                    podium_h=0.55, double_eave=False, lantern=True)

    # 4. Zhenqu Pavilion (真趣亭 — Qianlong's imperial pavilion) on North shore!
    sb.add_box("stone_light", 9.6, 9.6, 0.85, center=(-11.5, 22.5, 0.425))
    sb.add_pavilion(center=(-11.5, 22.5, 0.85), radius=4.4, sides=4, col_h=3.8,
                    podium_h=0.45, double_eave=True, col_mat="vermilion",
                    bench_mat="warm_wood", lantern=True)
    # Royal golden imperial plaque ("真趣") glowing subtly under front eave
    sb.add_box("emissive_gold", 2.2, 0.16, 0.72, center=(-11.5, 19.0, 4.65))

    # 5. Main Classical Halls: Yanyu Hall (燕誉堂) South, Woyun Chamber (卧云室) North,
    #    Wenmei Pavilion (问梅阁) West
    sb.add_hall(w=18.0, d=9.5, h=4.8, center=(-10.0, -31.0, 0.0), rot_z=0.0,
                podium_h=0.9, double_eave=True)
    sb.add_hall(w=16.0, d=8.2, h=4.4, center=(12.0, 31.0, 0.0), rot_z=0.0,
                podium_h=0.8)
    sb.add_hall(w=13.5, d=7.6, h=4.2, center=(-35.5, 22.0, 0.0), rot_z=math.pi * 0.5,
                podium_h=0.7)
    sb.add_suzhou_house(w=12.0, d=6.8, h=5.6, center=(-35.5, -18.0, 0.0), rot_z=math.pi * 0.5)

    # Covered zigzag perimeter corridors with lattice windows & warm lanterns
    sb.add_corridor_segment((-27.5, -24.0), (-27.5, -8.0), width=2.2, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-27.5, 12.0), (-27.5, 26.0), width=2.2, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-25.0, 27.5), (-16.5, 27.5), width=2.2, lantern=False)
    sb.add_corridor_segment((-5.0, 27.5), (4.0, 29.0), width=2.2, lantern=True)
    sb.add_corridor_segment((34.0, -28.0), (34.0, 26.0), width=2.2, has_back_wall=True, lantern=True)

    # Ancient pines, weeping willows, bamboo groves & pond lotus pads
    for tx, ty, th, sd in [
        (-28.0, 34.0, 10.5, 151),
        (36.0,  33.0, 11.0, 152),
        (37.0, -32.0, 10.2, 153),
        (-36.0, -33.0, 9.8, 154),
        (16.0,  22.0,  9.2, 155),
        (-2.0, -21.0,  9.5, 156),
    ]:
        sb.add_pine_tree(center=(tx, ty, 0.0), height=th, seed=sd)

    sb.add_willow_tree(center=(-22.5, 17.5, 0.0), height=8.8, lean=(1.5, -1.0), seed=157)
    sb.add_willow_tree(center=(4.0, 18.5, 0.0), height=8.6, lean=(-1.2, -1.2), seed=158)
    sb.add_bamboo_clump(center=(-38.0, 4.0, 0.0), count=8, height=6.4, spread=2.2, seed=159)
    sb.add_bamboo_clump(center=(38.0, 4.0, 0.0), count=8, height=6.2, spread=2.0, seed=160)

    for lx, ly, lr in [(-14, 10, 0.9), (-11, 13, 0.75), (-16, 12, 0.8),
                       (2, 12, 0.85), (4, 9, 0.75), (-10, -12, 0.9), (-7, -14, 0.8)]:
        sb.add_cylinder("lotus_pad", lr, lr, 0.04, segments=8, center=(lx, ly, -0.26))
        sb.add_ico("lotus_pink", radius=0.17, subdivisions=1, center=(lx + 0.1, ly, -0.16))


def main():
    clear_scene()
    palette = create_gusu_palette()
    sb = SceneBuilder(palette)
    build_shizilin(sb)
    objs = sb.build_objects_by_material(prefix="Shizilin")
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    print(f"[STATS] shizilin_garden: {len(objs)} meshes, {total_tris} tris")
    export_glb("shizilin_garden.glb")


if __name__ == "__main__":
    main()
