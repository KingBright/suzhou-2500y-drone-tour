"""
Generate humble_admin_garden.glb — Station 07 NW (anchor: x=230, y=1.6, z=-230):
  Humble Administrator's Garden (拙政园) — China's premier classical water garden.
  Spatial alignment: local X in [-76, +14] (world X in [154, 244]), Y in [-52, +56]
  so its East white garden boundary wall at X=+13.5 sits cleanly adjacent to
  I.M. Pei's Suzhou Museum (museumAnchor x=265, local west wall at world X=246.5)
  with ZERO overlap!

  Highlights:
  - Expansive Lotus Pond (大荷花池) dotted with lush lily pads & pink lotus blossoms
  - Hall of Distant Fragrance (远香堂) overlooking the central lotus pond
  - Iconic vermilion-red covered corridor bridge Little Flying Rainbow (小飞虹)
  - Jianshan Pavilion (见山楼) 2-story lakeside pavilion on the NW bank
  - West & East Island Hills crowned by Xuexiang Yunwei Pavilion (雪香云蔚亭) & Daishuang Pavilion
  - White Suzhou perimeter garden walls with wave-tile caps & lush willows/pines.
"""
import math
import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gusu_common import clear_scene, create_gusu_palette, SceneBuilder, export_glb


def build_humble_admin(sb):
    # Perimeter ground slabs framing the expansive Central Lotus Pond (X in [-60, +4], Y in [-28, +34])
    # All foundations extend cleanly down to Z=-2.5
    sb.add_box("courtyard", 16.0, 108.0, 2.5, center=(-68.0, 2.0, -1.25))   # West (-76..-60)
    sb.add_box("courtyard", 10.0, 108.0, 2.5, center=(9.0, 2.0, -1.25))     # East (+4..+14)
    sb.add_box("courtyard", 64.0, 22.0, 2.5, center=(-28.0, 45.0, -1.25))   # North (+34..+56)
    sb.add_box("courtyard", 64.0, 24.0, 2.5, center=(-28.0, -40.0, -1.25))  # South (-52..-28)

    # Expansive Lotus Pond bed & reflective emerald water plane
    sb.add_box("stone_dark", 68.0, 66.0, 1.0, center=(-28.0, 3.0, -2.0))
    sb.add_box("water", 66.0, 64.0, 0.12, center=(-28.0, 3.0, -0.35))

    # White Suzhou perimeter walls enclosing the entire garden (East wall at X=+13.5 borders Suzhou Museum!)
    w_pts = [(-75, -51), (13.5, -51), (13.5, 55), (-75, 55)]
    for i in range(4):
        sb.add_garden_wall(w_pts[i], w_pts[(i + 1) % 4], height=4.0, wave_cap=True)

    # 1. MAIN HALL OF DISTANT FRAGRANCE (远香堂) — iconic centerpiece overlooking the Lotus Pond!
    sb.add_box("stone_light", 24.0, 14.0, 0.95, center=(-26.0, -33.5, 0.475))
    sb.add_hall(w=21.0, d=11.0, h=5.0, center=(-26.0, -34.5, 0.95), rot_z=0.0,
                podium_h=0.45, double_eave=False, col_mat="dark_wood", open_front=True)
    # Warm glowing terrace lanterns flanking the lakeside terrace of Yuanxiang Tang
    for lx in (-35.5, -16.5):
        sb.add_cylinder("dark_wood", 0.08, 0.07, 3.2, segments=6, center=(lx, -27.2, 2.5))
        sb.add_ico("emissive_warm", radius=0.28, subdivisions=1, scale=(1.0, 1.0, 1.3),
                   center=(lx, -27.2, 4.1))
    # Sculpted Taihu rockery hill immediately south of Yuanxiang Tang
    sb.add_taihu_rock_cluster(center=(-26.0, -45.0, 0.0), radius=6.5, height=4.8, lobes=8, seed=201)

    # 2. ICONIC VERMILION-RED COVERED CORRIDOR BRIDGE — LITTLE FLYING RAINBOW (小飞虹)!!
    # Spans across the west-south water arm from (-50, -26) to (-50, -5) with an arched center bay!
    bx = -49.5
    # Vermilion pier columns descending into the pond water
    for by in (-24.0, -19.0, -14.0, -9.0):
        for ox in (-1.35, 1.35):
            sb.add_cylinder("stone_dark", 0.24, 0.22, 1.6, segments=6, center=(bx + ox, by, -0.5))
    # Three-section arched covered red timber corridor bridge (center raised over water arch!)
    # South ramp
    sb.add_corridor_segment((bx, -26.5), (bx, -19.5), width=2.8, height=3.1, z0=0.25,
                            vermilion=True, lantern=True)
    # Central elevated bridge span (rising visibly like a flying red rainbow over the pond!)
    sb.add_box("vermilion", 3.1, 8.8, 0.35, center=(bx, -15.0, 1.15))
    # Curved red under-arch beams + red railings
    for ox in (-1.35, 1.35):
        sb.add_box("vermilion", 0.16, 8.8, 0.85, center=(bx + ox, -15.0, 1.75))
        for by in (-19.0, -15.0, -11.0):
            sb.add_cylinder("vermilion", 0.13, 0.12, 3.3, segments=6, center=(bx + ox, by, 2.95))
    sb.add_suzhou_roof(w=9.8, d=3.4, h=1.65, center=(bx, -15.0, 4.45), rot_z=math.pi * 0.5,
                       eave_overhang=0.72, corner_lift=0.52, hip_gable=True, add_ribs=False)
    # Glowing red lanterns hanging along Little Flying Rainbow + warm reflection shimmer on water!
    for by in (-22.0, -15.0, -8.0):
        sb.add_ico("emissive_red", radius=0.28, subdivisions=1, scale=(1.0, 1.0, 1.3),
                   center=(bx, by, 3.85))
    sb.add_cylinder("emissive_red", 1.8, 1.8, 0.03, segments=10, center=(bx + 3.2, -15.0, -0.27))
    # North ramp landing onto West Island shore
    sb.add_corridor_segment((bx, -10.5), (bx, -3.5), width=2.8, height=3.1, z0=0.25,
                            vermilion=True, lantern=True)

    # 3. WEST ISLAND HILL + XUEXIANG YUNWEI PAVILION (雪香云蔚亭)
    wx, wy = -40.0, 10.0
    # Grassy rocky island hill rising smoothly out of the lotus pond
    sb.add_ico("grass", radius=14.0, subdivisions=2, scale=(1.15, 0.92, 0.28),
               center=(wx, wy, 0.4), jitter=0.06, rng=random.Random(210))
    sb.add_taihu_rock_cluster(center=(wx - 10.5, wy - 4.0, -0.3), radius=4.8, height=3.6, lobes=7, seed=211)
    sb.add_taihu_rock_cluster(center=(wx + 10.0, wy + 5.0, -0.3), radius=4.5, height=3.4, lobes=7, seed=212)
    # Xuexiang Yunwei Pavilion (雪香云蔚亭) crowning the West Island Hill!
    sb.add_pavilion(center=(wx, wy, 3.6), radius=4.2, sides=4, col_h=3.6,
                    podium_h=0.55, double_eave=False, col_mat="dark_wood", lantern=True)
    sb.add_pine_tree(center=(wx - 7.5, wy + 5.5, 1.5), height=9.5, seed=213)
    sb.add_willow_tree(center=(wx + 8.5, wy - 6.0, 0.5), height=8.5, lean=(1.4, -1.0), seed=214)

    # 4. EAST ISLAND HILL + DAISHUANG PAVILION (待霜亭)
    ex, ey = -13.0, 12.0
    sb.add_ico("grass", radius=12.0, subdivisions=2, scale=(1.05, 0.88, 0.27),
               center=(ex, ey, 0.3), jitter=0.06, rng=random.Random(215))
    sb.add_taihu_rock_cluster(center=(ex + 8.0, ey - 5.0, -0.3), radius=4.4, height=3.5, lobes=7, seed=216)
    sb.add_pavilion(center=(ex, ey, 3.1), radius=3.6, sides=6, col_h=3.4,
                    podium_h=0.50, double_eave=False, col_mat="dark_wood", lantern=True)
    sb.add_pine_tree(center=(ex + 5.5, ey + 5.0, 1.4), height=9.0, seed=217)

    # Bridges linking the two island hills and the north/east shores
    sb.add_arch_bridge(span=10.5, width=2.2, arch_h=1.9, center=(-26.5, 11.0, -0.2),
                       rot_z=0.08, lanterns=True)
    sb.add_zigzag_bridge([(-13.0, 23.0), (-11.0, 28.5), (-14.0, 34.5)], width=1.8, z_deck=0.22)
    sb.add_zigzag_bridge([(-2.5, 12.0), (2.0, 14.5), (6.0, 12.0)], width=1.8, z_deck=0.22)

    # 5. JIANSHAN PAVILION (见山楼) — Iconic 2-story waterfront pavilion on NW bank!
    jx, jy = -59.0, 24.0
    sb.add_box("stone_dark", 13.0, 9.5, 2.2, center=(jx, jy, -0.85))
    # Ground floor open colonnade + upper 2nd-story pavilion with double swept upturned eaves!
    sb.add_hall(w=12.0, d=8.4, h=3.8, center=(jx, jy, 0.25), rot_z=-0.12,
                podium_h=0.5, double_eave=False, col_mat="dark_wood")
    # Second story pavilion rising above lower roof
    sb.add_box("dark_wood", 8.6, 6.0, 3.0, center=(jx, jy, 6.2), rot_z=-0.12)
    sb.add_box("emissive_win", 8.75, 4.8, 1.85, center=(jx, jy, 6.3), rot_z=-0.12)
    sb.add_box("emissive_win", 7.2, 6.15, 1.85, center=(jx, jy, 6.3), rot_z=-0.12)
    sb.add_suzhou_roof(w=9.2, d=6.6, h=2.4, center=(jx, jy, 7.65), rot_z=-0.12,
                       eave_overhang=0.95, corner_lift=0.62, hip_gable=True)

    # 6. Supporting Iconic Halls & Waterfront Corridors
    # Thirty-Six Mandarin Ducks Hall (卅六鸳鸯馆) on SW bank
    sb.add_hall(w=15.0, d=8.5, h=4.5, center=(-65.0, -18.0, 0.0), rot_z=math.pi * 0.5,
                podium_h=0.7, double_eave=False)
    # Xiangzhou (香洲 — Fragrant Boat Hall) on NW cove
    sb.add_hall(w=13.0, d=6.8, h=4.2, center=(-40.0, 41.0, 0.0), rot_z=0.0, podium_h=0.7)
    # Loquat Garden / Pipa Yuan & Wuzhu Youju Pavilion (梧竹幽居) along the East bank
    sb.add_pavilion(center=(6.5, 14.0, 0.0), radius=3.5, sides=4, col_h=3.4,
                    podium_h=0.55, lantern=True)
    sb.add_hall(w=12.5, d=7.2, h=4.2, center=(-12.0, 43.0, 0.0), rot_z=0.0, podium_h=0.7)
    sb.add_hall(w=13.5, d=7.2, h=4.2, center=(-2.0, -34.0, 0.0), rot_z=0.0, podium_h=0.7)

    # Winding lakeside covered corridors
    sb.add_corridor_segment((-60.0, -2.0), (-60.0, 16.0), width=2.2, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-50.0, 36.0), (-22.0, 36.0), width=2.2, lantern=True)
    sb.add_corridor_segment((6.5, -24.0), (6.5, 8.0), width=2.2, has_back_wall=True, lantern=True)
    sb.add_corridor_segment((-12.0, -34.0), (6.0, -28.0), width=2.2, lantern=False)

    # 7. EXPANSIVE LOTUS LILY PADS & PINK LOTUS BLOSSOMS across the pond!
    rng = random.Random(225)
    lotus_zones = [
        (-36, -15, 10, 9),
        (-16, -14, 10, 9),
        (-28,  26, 12, 6),
        (-52,  10,  5, 8),
        (-2,   25,  6, 6),
    ]
    for cx, cy, rx, ry in lotus_zones:
        for _ in range(9):
            lx = cx + rng.uniform(-rx, rx)
            ly = cy + rng.uniform(-ry, ry)
            lr = rng.uniform(0.65, 1.15)
            sb.add_cylinder("lotus_pad", lr, lr, 0.04, segments=8, center=(lx, ly, -0.26))
            if rng.random() < 0.45:
                sb.add_ico("lotus_pink", radius=rng.uniform(0.15, 0.22), subdivisions=1,
                           center=(lx + rng.uniform(-0.2, 0.2), ly + rng.uniform(-0.2, 0.2), -0.15))

    # 8. Lush Weeping Willows, Ancient Pines & Bamboo Framing the Water Views
    for wx, wy, wh, lean, sd in [
        (-58.0, -27.0, 9.5, (1.8, 1.2), 231),
        (-38.0, -27.0, 9.0, (1.0, 1.6), 232),
        (-12.0, -26.0, 9.2, (-1.2, 1.5), 233),
        (-56.0,  34.0, 9.6, (1.6, -1.2), 234),
        (4.0,    32.0, 9.0, (-1.6, -1.0), 235),
        (5.0,    -8.0, 8.8, (-1.8, 0.3), 236),
    ]:
        sb.add_willow_tree(center=(wx, wy, 0.0), height=wh, lean=lean, seed=sd)

    for px, py, ph, sd in [
        (-68.0,  42.0, 11.5, 241),
        (-24.0,  47.0, 11.0, 242),
        (6.0,    46.0, 10.8, 243),
        (-68.0, -40.0, 11.2, 244),
        (6.0,   -44.0, 10.5, 245),
        (-44.0, -44.0, 10.2, 246),
    ]:
        sb.add_pine_tree(center=(px, py, 0.0), height=ph, seed=sd)

    sb.add_bamboo_clump(center=(9.5, 24.0, 0.0), count=9, height=7.0, spread=2.2, seed=247)
    sb.add_bamboo_clump(center=(-68.0, 6.0, 0.0), count=8, height=6.5, spread=2.0, seed=248)


def main():
    clear_scene()
    palette = create_gusu_palette()
    sb = SceneBuilder(palette)
    build_humble_admin(sb)
    objs = sb.build_objects_by_material(prefix="HumbleAdmin")
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    print(f"[STATS] humble_admin_garden: {len(objs)} meshes, {total_tris} tris")
    export_glb("humble_admin_garden.glb")


if __name__ == "__main__":
    main()
