"""
Station 02b: Tiger Hill & Leaning Yunyan Pagoda (虎丘山 · 剑池 · 云岩斜塔)
Exports: web/public/assets/models/tiger_hill.glb
Features:
  - ~32m high lush layered rocky Haiyong Hill (海涌山) with dark pines & bamboo
  - Dramatic Sword Pool (剑池) vertical cliff cleft, dark emerald water, stone arch bridge & red plaque
  - Crowned by the iconic 47.7m 7-story octagonal Tiger Hill Leaning Pagoda (云岩斜塔)
    visibly leaning ~3.7 deg toward NE (real-world direction & perpendicular to SE hero camera!)
    with layered corbeled brick eaves & warm perimeter uplighting.
"""
import math
import os
import sys
from mathutils import Matrix, Euler, Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from west_common import SuzhouBuilder

OUT_GLB = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/tiger_hill.glb"


def hill_height(x, y):
    """Smooth sculpted Haiyong Hill heightfield (peak plateau ~31.6m at center, base ~-2.0m at r=98m)."""
    r = math.hypot(x, y)
    ang = math.atan2(y, x)
    # Organic multi-lobe hill footprint radius (~88-100m)
    r_max = 94.0 + 7.5 * math.cos(2.0 * ang - 0.5) + 4.5 * math.sin(3.0 * ang + 0.8)
    u = min(1.0, r / r_max)

    # Flat summit plateau for pagoda courtyard (r < 17m -> z = 31.6m)
    if r <= 16.5:
        h = 31.6
    else:
        t = (r - 16.5) / max(1.0, (r_max - 16.5))
        t = min(1.0, max(0.0, t))
        # Natural rocky terraced hillside profile
        base_profile = 31.6 * ((1.0 - t) ** 1.48) - 2.0 * (t ** 2.2)
        # Subtle geological rock ledges + ridge ribs
        ledge = 1.15 * math.sin(t * math.pi * 4.5) * (1.0 - t) * t * 3.0
        ridge = 1.4 * math.cos(5.0 * ang + t * 2.0) * math.sin(t * math.pi)
        h = base_profile + ledge + ridge

    # Carve dramatic Sword Pool (剑池) cliff chasm on SE flank (around x=18..34, y=-34..-18)
    # Aligned along SE axis so heroView camera (+95, -95) looks straight into the cleft!
    sx = (x - 24.0) * 0.7071 - (y + 24.0) * 0.7071   # along chasm length
    sy = (x - 24.0) * 0.7071 + (y + 24.0) * 0.7071   # across chasm width
    # Wait: rotate so chasm runs SW-to-NE or NW-to-SE facing SE
    # Chasm centered at (22, -24), length along NW-SE (u_len), width across SW-NE (u_wid)
    dx, dy = x - 22.0, y + 24.0
    u_len = (dx * 0.7071 - dy * 0.7071)   # positive toward SE (+1,-1)
    u_wid = (dx * 0.7071 + dy * 0.7071)   # perpendicular SW-NE
    if abs(u_wid) < 10.5 and -14.0 < u_len < 16.0:
        # Smooth steep gorge depression down to z = 2.0m
        wx = max(0.0, 1.0 - (abs(u_wid) / 10.5) ** 2.4)
        lx = max(0.0, 1.0 - (abs(u_len - 1.0) / 15.0) ** 3.0)
        cut = wx * lx
        h = h * (1.0 - cut) + 1.2 * cut

    # Flatten Qianrenshi (千人石) terrace on south slope around (x=8, y=-48)
    d_q = math.hypot((x - 6.0) / 18.0, (y + 48.0) / 13.0)
    if d_q < 1.0:
        w_q = (1.0 - d_q * d_q) ** 1.5
        h = h * (1.0 - w_q) + 9.2 * w_q

    return h


def build_haiyong_hill(b):
    """Build sculpted layered Haiyong Hill mesh + rocky cliff outcrops."""
    n_ang = 44
    radii = [0.0, 8.0, 16.5, 23.0, 30.0, 38.0, 46.0, 55.0, 64.0, 74.0, 84.0, 94.0, 102.0]

    coords = [(0.0, 0.0, hill_height(0.0, 0.0))]
    for r in radii[1:]:
        for i in range(n_ang):
            a = 2.0 * math.pi * i / n_ang
            x = r * math.cos(a)
            y = r * math.sin(a)
            z = hill_height(x, y)
            coords.append((x, y, z))

    # Assign grassy/earthy hill faces and rocky cliff faces based on slope!
    grass_faces = []
    rock_faces = []

    # Center fan
    for i in range(n_ang):
        ni = (i + 1) % n_ang
        grass_faces.append((0, 1 + i, 1 + ni))

    # Rings
    for ri in range(len(radii) - 2):
        r0 = 1 + ri * n_ang
        r1 = 1 + (ri + 1) * n_ang
        for i in range(n_ang):
            ni = (i + 1) % n_ang
            f = (r0 + i, r1 + i, r1 + ni, r0 + ni)
            p0, p1, p2, p3 = Vector(coords[f[0]]), Vector(coords[f[1]]), Vector(coords[f[2]]), Vector(coords[f[3]])
            normal = (p1 - p0).cross(p3 - p0)
            if normal.length > 1e-5:
                normal.normalize()
            # Steep slopes get craggy rock material, gentle slopes get lush green earth
            if normal.z < 0.72:
                rock_faces.append(f)
            else:
                grass_faces.append(f)

    b.add_mesh_data(coords, grass_faces, "Mat_HillEarth", smooth=True)
    b.add_mesh_data(coords, rock_faces, "Mat_TaihuRock", smooth=False)

    # Summit octagonal stone courtyard plaza (Z = 31.6m)
    b.prism(0.0, 0.0, 30.5, 31.8, 17.5, 16.8, 8, "Mat_GraniteLight")
    # Historic low grey-brick octagonal enclosure wall around Tiger Hill Pagoda
    for i in range(8):
        if i == 6:  # leave south-east entry gateway open
            continue
        a0 = 2.0 * math.pi * i / 8.0 + math.pi / 8.0
        a1 = 2.0 * math.pi * (i + 1) / 8.0 + math.pi / 8.0
        r_w = 15.8
        b.add_wall(r_w * math.cos(a0), r_w * math.sin(a0),
                   r_w * math.cos(a1), r_w * math.sin(a1),
                   z0=31.8, h=2.4, thickness=0.55,
                   wall_mat="Mat_CityBrick", tile_mat="Mat_DarkTile", pilaster_step=12.0)


def build_sword_pool(b):
    """Iconic Sword Pool (剑池) sheer rock cleft, emerald water, stone arch bridge & red plaque."""
    # Rotated local frame centered at (22, -24), u_len along SE (-45 deg)
    rot_se = -math.pi * 0.25
    m_sp = Matrix.Translation((22.0, -24.0, 0.0)) @ Matrix.Rotation(rot_se, 4, 'Z')

    # Dark emerald Sword Pool water surface deep inside the cleft
    b.box_z(0.0, 0.0, 1.5, 3.2, 26.0, 12.0, "Mat_PondWater", matrix=m_sp)

    # Twin sheer vertical rocky cliffs framing the chasm (like sword-split rock walls!)
    for sy in (-1, 1):
        for seg_x, seg_h, seg_w in [(-8.0, 17.5, 9.0), (0.0, 16.0, 10.0), (8.0, 13.0, 9.0)]:
            b.box_z(seg_x, sy * 7.6, 1.0, seg_h, seg_w, 5.2, "Mat_TaihuRock",
                    rot_z=sy * 0.08, matrix=m_sp)
            b.box_z(seg_x + 1.2, sy * 8.4, 2.0, seg_h + 1.8, seg_w * 0.85, 4.4, "Mat_GraniteDark",
                    rot_z=-sy * 0.06, matrix=m_sp)

    # Iconic Stone Arch Bridge (双井桥) spanning directly across the Sword Pool cleft!
    # Bridge crosses Y (between cliffs), opening along X (facing hero camera!)
    m_arch = Matrix.Translation((22.0, -24.0, 0.0)) @ Matrix.Rotation(rot_se, 4, 'Z')
    # Build arch vault using ring segments
    rx, rz = 5.6, 5.2
    z_spring = 8.2
    segs = 12
    hw = 2.8
    ring_v, ring_f = [], []
    for i in range(segs + 1):
        th = math.pi * (1.0 - i / segs)
        ct, st = math.cos(th), math.sin(th)
        ring_v.extend([
            (-hw, rx * ct, z_spring + rz * st),
            ( hw, rx * ct, z_spring + rz * st),
            ( hw, (rx + 1.1) * ct, z_spring + (rz + 1.1) * st),
            (-hw, (rx + 1.1) * ct, z_spring + (rz + 1.1) * st),
        ])
    for i in range(segs):
        a, c = i * 4, (i + 1) * 4
        ring_f.extend([
            (a + 0, c + 0, c + 1, a + 1),
            (a + 3, a + 2, c + 2, c + 3),
            (a + 0, a + 3, c + 3, c + 0),
            (a + 1, c + 1, c + 2, a + 2),
        ])
    b.add_mesh_data(ring_v, ring_f, "Mat_GraniteLight", matrix=m_arch)
    # Bridge deck & stone parapets over the arch
    b.box_z(0.0, 0.0, z_spring + rz + 0.6, z_spring + rz + 1.5, hw * 2.0, 14.5, "Mat_GraniteLight", matrix=m_arch)
    for sx in (-1, 1):
        b.box_z(sx * (hw - 0.25), 0.0, z_spring + rz + 1.5, z_spring + rz + 2.5, 0.42, 14.5, "Mat_GraniteLight", matrix=m_arch)

    # Iconic Cinnabar-Red Carved Cliff Inscription ("虎丘剑池") on a tall vertical cliff backwall + warm uplights
    b.box_z(-11.5, 0.0, 2.5, 22.5, 4.8, 15.0, "Mat_TaihuRock", matrix=m_sp)
    b.box_z(-9.0, 0.0, 12.0, 19.5, 0.45, 5.2, "Mat_PlaqueRed", matrix=m_sp)
    b.box_z(-8.7, 0.0, 12.6, 18.9, 0.22, 4.2, "Mat_GoldTrim", matrix=m_sp)
    # Warm hidden cliff uplights illuminating Sword Pool at dusk & night
    for uy in (-4.8, 0.0, 4.8):
        b.box_z(-7.8, uy, 3.4, 4.1, 0.8, 0.8, "Emissive_Warm_Uplight", matrix=m_sp)
        b.box_z(6.0, uy, 3.4, 4.1, 0.8, 0.8, "Emissive_Warm_Uplight", matrix=m_sp)


def build_tiger_hill_leaning_pagoda(b, cx=0.0, cy=0.0, z_base=31.7):
    """
    Iconic 47.7m 7-story octagonal Tiger Hill Leaning Pagoda (云岩斜塔).
    Visibly leaning ~3.7 deg toward NE (+X, +Y), matching real-world lean & maximally
    visible in silhouette from SE heroView!
    """
    # Tilt matrix: lean 3.75 deg toward NE (+45 deg in XY plane)
    # Rotating +2.65 deg around Y tilts +Z toward +X; rotating -2.65 deg around X tilts +Z toward +Y!
    tilt_deg = 2.68
    m_lean = (
        Matrix.Translation((cx, cy, z_base))
        @ Euler((math.radians(-tilt_deg), math.radians(tilt_deg), math.pi / 8.0), 'XYZ').to_matrix().to_4x4()
    )

    # Octagonal brick plinth base (partially embedded so tilted base has zero gap!)
    b.prism(0, 0, -1.2, 1.8, 7.6, 7.2, 8, "Mat_GraniteDark", matrix=m_lean)
    b.prism(0, 0, 1.8, 2.6, 7.1, 6.9, 8, "Mat_PagodaBrickDark", matrix=m_lean)

    # 7 tapering Song-dynasty octagonal brick stories (total height = 47.7m from z_base!)
    # Heights sum: 2.6 + (7.6 + 6.9 + 6.4 + 6.0 + 5.6 + 5.2 + 4.9) + 2.5 crown = 47.7m!
    stories = [
        (6.80, 6.55, 7.6),
        (6.25, 6.02, 6.9),
        (5.78, 5.56, 6.4),
        (5.36, 5.15, 6.0),
        (4.98, 4.78, 5.6),
        (4.62, 4.44, 5.2),
        (4.28, 4.05, 4.9),
    ]
    z = 2.6
    for idx, (r_bot, r_top, sh) in enumerate(stories):
        wall_h = sh * 0.68
        eave_h = sh * 0.32

        # Main aged terracotta-ochre brick octagonal shaft
        b.prism(0, 0, z, z + wall_h, r_bot, r_top, 8, "Mat_PagodaBrick", matrix=m_lean)

        # Horizontal light plaster frieze bands + corner pilasters + arched doorways on 8 facets
        b.prism(0, 0, z + wall_h - 0.55, z + wall_h, r_top + 0.08, r_top + 0.08, 8, "Mat_WhiteWall", matrix=m_lean)
        for f_i in range(8):
            a_corner = 2.0 * math.pi * f_i / 8.0
            a_face = a_corner + math.pi / 8.0
            # Corner brick pilaster column
            b.cylinder(r_bot * math.cos(a_corner), r_bot * math.sin(a_corner),
                       z, z + wall_h, 0.24, "Mat_GraniteLight", sides=6, smooth=False, matrix=m_lean)
            # Face center distance (apothem)
            apothem = 0.5 * (r_bot + r_top) * math.cos(math.pi / 8.0)
            fx, fy = apothem * math.cos(a_face), apothem * math.sin(a_face)
            rot_f = a_face + math.pi * 0.5
            # Subtle weathered plaster inlay panel on alternating faces (keeping warm Song brick dominant!)
            if f_i % 2 == 0:
                pw = r_bot * 0.44
                b.box_z(fx, fy, z + 0.45, z + wall_h - 0.75, pw, 0.14, "Mat_WhiteWall", rot_z=rot_f, matrix=m_lean)
            # Recessed dark-wood & warm glowing ogee-arched doorway / niche
            dw = r_bot * (0.24 if f_i % 2 == 0 else 0.15)
            dh = wall_h * (0.58 if f_i % 2 == 0 else 0.40)
            b.box_z(fx, fy, z + 0.3, z + 0.3 + dh, dw + 0.22, 0.26, "Mat_DarkWood", rot_z=rot_f, matrix=m_lean)
            b.box_z(fx, fy, z + 0.35, z + 0.25 + dh, dw, 0.32, "Emissive_Warm_Window", rot_z=rot_f, matrix=m_lean)

        # Layered Corbeled Song Brick Eaves (叠涩砖檐) — 3 stepping courses + dark tile skirt!
        z_e0 = z + wall_h
        b.prism(0, 0, z_e0, z_e0 + eave_h * 0.32, r_top + 0.25, r_top + 0.65, 8, "Mat_PagodaBrickDark", matrix=m_lean)
        b.prism(0, 0, z_e0 + eave_h * 0.32, z_e0 + eave_h * 0.64, r_top + 0.65, r_top + 1.05, 8, "Mat_PagodaBrick", matrix=m_lean)
        # Sloped dark-tile eave cap with gentle corner flare & warm golden uplight accent!
        b.add_polygonal_roof(
            0, 0, z_e0 + eave_h * 0.62,
            r_inner=(r_top * 0.90), r_outer=(r_top + 1.18), h=eave_h * 0.58,
            sides=8, mat_tile="Mat_DarkTile", mat_ridge="Mat_TileRidge",
            mat_wood="Mat_PagodaBrickDark", mat_gold=None,
            mat_eave_light="Emissive_Gold_Eave",
            flare_z=0.32, flare_r=0.22, steps=2, finial=False, matrix=m_lean,
        )
        z += sh

    # Authentic Historic Stepped Brick Crown (truncated spire top at 47.7m!)
    b.prism(0, 0, z, z + 1.1, 3.85, 3.30, 8, "Mat_PagodaBrickDark", matrix=m_lean)
    b.prism(0, 0, z + 1.1, z + 1.9, 3.10, 2.30, 8, "Mat_DarkTile", matrix=m_lean)
    b.prism(0, 0, z + 1.9, z + 2.5, 1.45, 0.95, 8, "Mat_Bronze", matrix=m_lean)
    b.sphere(0, 0, z + 2.65, 0.42, 0.42, 0.42, 6, 4, "Emissive_Gold_Crown", matrix=m_lean)

    # Warm Perimeter Uplighting Ring around Pagoda Base (grounded on summit plaza Z=31.8)
    for i in range(8):
        a = 2.0 * math.pi * i / 8.0 + math.pi / 8.0
        ux, uy = cx + 9.4 * math.cos(a), cy + 9.4 * math.sin(a)
        b.prism(ux, uy, z_base, z_base + 0.65, 0.55, 0.45, 6, "Mat_GraniteDark")
        b.prism(ux, uy, z_base + 0.65, z_base + 1.05, 0.42, 0.48, 6, "Emissive_Warm_Uplight")


def main():
    b = SuzhouBuilder("TigerHill")

    # 1. Lush Layered Rocky Haiyong Hill (~32m high)
    build_haiyong_hill(b)

    # 2. Iconic Sword Pool (剑池) cliff cleft & stone arch bridge
    build_sword_pool(b)

    # 3. 47.7m 7-Story Octagonal Tiger Hill Leaning Pagoda (云岩斜塔)
    build_tiger_hill_leaning_pagoda(b, 0.0, 0.0, z_base=31.7)

    # 4. Hilltop & Approach Pavilions + Winding Stone Steps
    # Qianrenshi Terrace Hall / Ershanmen (二山门) on southern approach
    b.add_hall(6.0, -48.0, 9.0, 15.0, 9.0, wall_h=4.2, roof_h=3.2, double_eave=False,
               rot_z=0.15, wall_mat="Mat_WhiteWall", pillar_mat="Mat_DarkWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.9)
    # Southern Hill Gate (虎丘头山门) at base
    b.add_hall(18.0, -76.0, 0.0, 16.0, 8.5, wall_h=4.4, roof_h=3.2, double_eave=False,
               rot_z=0.22, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.8)
    # Zhishuang Pavilion (致爽阁) & Wanjing Pavilion perched on hillside flanks
    z_p1 = hill_height(-24.0, -28.0)
    b.add_pavilion(-24.0, -28.0, z_p1 - 0.5, radius=4.2, col_h=3.5, roof_h=3.2, sides=6,
                   pillar_mat="Mat_CrimsonWood", eave_light="Emissive_Gold_Eave")
    z_p2 = hill_height(38.0, 8.0)
    b.add_pavilion(38.0, 8.0, z_p2 - 0.5, radius=4.0, col_h=3.4, roof_h=3.0, sides=6,
                   pillar_mat="Mat_DarkWood", eave_light="Emissive_Gold_Eave")

    # Winding stone steps & warm hillside path lanterns from south gate up to summit
    path_pts = [
        (16, -68), (12, -58), (0, -44), (-8, -32), (-14, -20), (-12, -12),
    ]
    for i, (px, py) in enumerate(path_pts):
        pz = hill_height(px, py)
        b.box_z(px, py, pz - 1.2, pz + 0.3, 4.2, 4.2, "Mat_GraniteLight")
        b.add_lantern_post(px + 2.4, py, pz, h=2.8)

    # 5. Lush Dark Pines, Bamboo Groves & Rocky Outcrops carpeting Haiyong Hill
    # Ring of dark pines around hillside (avoiding Sword Pool cleft & pagoda courtyard!)
    pine_coords = [
        # Dense lush upper slope crown flanking pagoda & Sword Pool cliffs (r ~ 20-34)
        (-24, 16, 1.45), (-12, 26, 1.40), (14, 24, 1.45), (26, 12, 1.35),
        (-28, -4, 1.40), (-16, -24, 1.35), (8, 28, 1.35), (-26, 20, 1.30),
        (24, -4, 1.40), (6, -24, 1.35), (32, -8, 1.40), (4, -34, 1.35),
        (16, -42, 1.30), (36, -24, 1.40), (-6, -28, 1.35), (22, 20, 1.35),
        # Mid slope ring (r ~ 38-58)
        (-42, 22, 1.50), (-48, 0, 1.45), (-38, -28, 1.45), (-22, -46, 1.40),
        (-28, 38, 1.55), (0, 48, 1.50), (28, 40, 1.45), (46, 22, 1.50),
        (52, -8, 1.45), (44, -34, 1.40), (30, -52, 1.35), (-8, 52, 1.40),
        (42, -20, 1.45), (50, -24, 1.40), (24, -46, 1.35), (-32, -16, 1.40),
        # Outer base ring (r ~ 62-80)
        (-64, 28, 1.55), (-68, -12, 1.50), (-52, -48, 1.45), (-24, -66, 1.45),
        (42, -62, 1.40), (66, -28, 1.50), (68, 14, 1.55), (52, 50, 1.50),
        (16, 68, 1.55), (-26, 64, 1.50), (-56, 52, 1.45), (62, 36, 1.45),
        (56, -44, 1.45), (34, -68, 1.40), (-42, -60, 1.40), (74, -8, 1.50),
    ]
    for i, (px, py, sc) in enumerate(pine_coords):
        pz = hill_height(px, py)
        b.add_tree_pine(px, py, pz - 0.5, scale=sc, seed=i + 10)

    # Dense emerald bamboo groves on the slopes
    bamboo_spots = [
        (-34, 10, 5.5, 11), (-18, 36, 6.0, 12), (24, 30, 5.5, 11),
        (42, -16, 5.5, 11), (-36, -42, 6.0, 11), (36, -44, 5.0, 10),
        (-54, 14, 6.0, 12), (56, 4, 6.0, 12),
    ]
    for i, (bx, by, rad, cnt) in enumerate(bamboo_spots):
        bz = hill_height(bx, by)
        b.add_bamboo_cluster(bx, by, bz - 0.4, radius=rad, count=cnt, h_min=7.0, h_max=11.5, seed=i + 40)

    # Autumn crimson maple highlights near Qianrenshi & Sword Pool
    for i, (mx, my) in enumerate([(14, -38), (-10, -40), (34, -14), (-22, 2), (20, 18)]):
        mz = hill_height(mx, my)
        b.add_tree_maple(mx, my, mz - 0.4, scale=1.15, seed=i + 80)

    # Natural craggy rock boulders scattered on slopes
    for i, (rx, ry, sc) in enumerate([(10, -34, 3.2), (-16, -34, 3.5), (34, -2, 3.8), (-32, 26, 4.0), (26, 20, 3.4)]):
        rz = hill_height(rx, ry)
        b.add_taihu_rock(rx, ry, rz - 0.8, sc, sc * 0.85, sc * 0.9, seed=i + 100)

    b.build_and_export(OUT_GLB)


if __name__ == "__main__":
    main()
