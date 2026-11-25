"""Generate Suzhou Culture & Arts Centre ('Crescent Bird's Nest', 苏州文化艺术中心)
& Moon Harbour (月光码头) waterfront boardwalk and European gable village.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modern_common import (
    clear_scene,
    make_standard_modern_mats,
    make_mat,
    MeshBuilder,
    export_glb,
    verify_glb,
)

OUT_PATH = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/arts_centre_moon.glb"


def build_arts_centre_and_moon():
    clear_scene()
    mats = make_standard_modern_mats()
    crescent_shell = make_mat("Metal_CrescentShell", "#cfd6df", metallic=0.88, roughness=0.20)
    lattice_silver = make_mat("Metal_LatticeNest", "#eef2f7", metallic=0.85, roughness=0.22)
    # Keep material count lean (~14 primitives) for ultra-low Three.js draw calls!
    all_mats = [
        mats["stone_granite"], mats["stone_light"], mats["water_pool"], mats["wood_deck"],
        mats["metal_dark"], mats["metal_silver"], crescent_shell, lattice_silver,
        mats["glass_dark"], mats["glass_blue"], mats["wall_cream"], mats["wall_white"],
        mats["roof_slate"], mats["roof_terracotta"],
        mats["em_cyan"], mats["em_warm"], mats["em_gold"],
    ]

    mb = MeshBuilder("ArtsCentreMoonHarbour", all_mats)

    # ------------------------------------------------------------------
    # 1. WATERFRONT PLAZA & MOON HARBOUR CRESCENT BOARDWALK (z = -2.5..0.0)
    # ------------------------------------------------------------------
    mb.add_box_minmax(-28.0, 114.0, -86.0, 86.0, -2.5, 0.0, mats["stone_granite"])
    mb.add_box_minmax(-24.0, 110.0, -82.0, 82.0, 0.0, 0.25, mats["stone_light"])
    mb.add_cylinder((16.0, 0.0, 0.16), 34.0, 34.0, 0.22, mats["water_pool"], segments=32, smooth=False)

    # Moon Harbour sweeping crescent timber boardwalk pier projecting West (-X) over Jinji Lake!
    n_pier = 28
    pier_rings = []
    outer_edge_pts = []
    inner_edge_pts = []
    for i in range(n_pier + 1):
        a = -0.58 * math.pi + 1.16 * math.pi * (i / n_pier)
        cx, cy = -24.0, 0.0
        r_in = 54.0
        r_out = 84.0
        x_in, y_in = cx - r_in * math.cos(a), cy + r_in * math.sin(a)
        x_out, y_out = cx - r_out * math.cos(a), cy + r_out * math.sin(a)
        pier_rings.append([
            (x_in, y_in, -0.4),
            (x_out, y_out, -0.4),
            (x_out, y_out, 0.28),
            (x_in, y_in, 0.28),
        ])
        outer_edge_pts.append((x_out, y_out, 0.35))
        inner_edge_pts.append((x_in, y_in, 0.35))
        if i % 2 == 0:
            mb.add_cylinder((x_out + 1.8 * math.cos(a), y_out - 1.8 * math.sin(a), -1.2), 0.55, 0.55, 2.8, mats["metal_dark"], segments=6)
            mb.add_cylinder((x_in - 1.8 * math.cos(a), y_in + 1.8 * math.sin(a), -1.2), 0.55, 0.55, 2.8, mats["metal_dark"], segments=6)

    mb.add_loft(pier_rings, mats["wood_deck"], closed_loop=True, cap_start=True, cap_end=True, smooth=False)
    mb.add_polyline_tubes(outer_edge_pts, 0.32, mats["em_gold"], segments=5, smooth=True)
    mb.add_polyline_tubes(inner_edge_pts, 0.28, mats["em_warm"], segments=5, smooth=True)

    # Waterfront safety railing along outer crescent boardwalk
    rail_outer = [(p[0], p[1], p[2] + 0.95) for p in outer_edge_pts]
    mb.add_polyline_tubes(rail_outer, 0.10, mats["metal_dark"], segments=4, smooth=True)

    # Two wooden finger jetties projecting further west into Jinji Lake
    for jy in (-36.0, 36.0):
        mb.add_box_minmax(-118.0, -96.0, jy - 4.5, jy + 4.5, -0.4, 0.24, mats["wood_deck"])
        mb.add_tube((-118.0, jy - 4.5, 0.34), (-96.0, jy - 4.5, 0.34), 0.22, mats["em_warm"], segments=4)
        mb.add_tube((-118.0, jy + 4.5, 0.34), (-96.0, jy + 4.5, 0.34), 0.22, mats["em_warm"], segments=4)
        for px in (-116.0, -108.0, -100.0):
            for py in (jy - 3.6, jy + 3.6):
                mb.add_cylinder((px, py, -1.2), 0.42, 0.42, 2.8, mats["metal_dark"], segments=6)
                mb.add_cylinder((px, py, 0.65), 0.24, 0.22, 0.8, mats["metal_dark"], segments=6)

    # ------------------------------------------------------------------
    # 2. SUZHOU CULTURE & ARTS CENTRE ("CRESCENT BIRD'S NEST", X = -8..+102)
    # Sweeping silver-metallic crescent shell dome + rich sculptural woven lattice skin!
    # ------------------------------------------------------------------
    arc_cx, arc_cy = 18.0, 0.0
    n_u = 40
    n_v = 16

    def crescent_point(u, v, offset_z=0.0):
        theta = (-114.0 + 228.0 * u) * math.pi / 180.0
        tip_env = math.sin(u * math.pi) ** 0.72
        r_in = 31.0 + 8.0 * (1.0 - tip_env)
        r_out = r_in + 12.0 + 44.0 * tip_env
        r = r_in + (r_out - r_in) * v

        crest_h = 14.0 + 26.0 * tip_env
        arch_curve = math.sin(v * math.pi) ** 0.85
        inner_lift = (1.0 - v) * (10.0 + 8.0 * tip_env)
        outer_skirt = v * (5.5 + 4.5 * tip_env)
        z = inner_lift + outer_skirt + (crest_h - 11.0) * arch_curve + offset_z

        x = arc_cx + r * math.cos(theta)
        y = arc_cy + r * math.sin(theta)
        return (x, y, z)

    shell_top = []
    shell_bot = []
    for iu in range(n_u + 1):
        u = iu / n_u
        rt, rb = [], []
        for iv in range(n_v + 1):
            v = iv / n_v
            rt.append(crescent_point(u, v, offset_z=0.55))
            rb.append(crescent_point(u, v, offset_z=-0.55))
        shell_top.append(rt)
        shell_bot.append(rb)

    mb.add_loft(shell_top, crescent_shell, closed_loop=False, smooth=True)
    mb.add_loft([list(reversed(r)) for r in shell_bot], mats["metal_silver"], closed_loop=False, smooth=True)

    # Glowing crescent perimeter lip tubes (Emissive_Cyan)
    front_lip = [crescent_point(iu / n_u, 0.0, 0.0) for iu in range(n_u + 1)]
    back_lip = [crescent_point(iu / n_u, 1.0, 0.0) for iu in range(n_u + 1)]
    mb.add_polyline_tubes(front_lip, 0.68, mats["em_cyan"], segments=6, smooth=True)
    mb.add_polyline_tubes(back_lip, 0.56, mats["em_cyan"], segments=6, smooth=True)

    # SCULPTURAL WOVEN LATTICE SKIN ("Bird's Nest" diagrid wrapping the entire crescent shell!)
    # Dense crisp diagonal weave + secondary cross-ribs
    for start_u in range(-18, n_u + 18, 2):
        diag1 = []
        diag2 = []
        for iv in range(n_v + 1):
            iu1 = start_u + int(iv * 1.15)
            if 0 <= iu1 <= n_u:
                diag1.append(crescent_point(iu1 / n_u, iv / n_v, offset_z=0.95))
            iu2 = start_u - int(iv * 1.15)
            if 0 <= iu2 <= n_u:
                diag2.append(crescent_point(iu2 / n_u, iv / n_v, offset_z=0.95))
        if len(diag1) >= 2:
            mb.add_polyline_tubes(diag1, 0.40, lattice_silver, segments=5, smooth=True)
        if len(diag2) >= 2:
            mb.add_polyline_tubes(diag2, 0.40, lattice_silver, segments=5, smooth=True)

    # Longitudinal silver & glowing cyan spine ribs along the crescent shell
    for iv_rib in (2, 5, 8, 11, 14):
        pts_rib = [crescent_point(iu / n_u, iv_rib / n_v, offset_z=0.92) for iu in range(n_u + 1)]
        r_mat = mats["em_cyan"] if iv_rib in (5, 11) else lattice_silver
        mb.add_polyline_tubes(pts_rib, 0.46 if iv_rib in (5, 11) else 0.34, r_mat, segments=5, smooth=True)

    # Glowing Underside Atrium & Curved Glass Theater Curtain Wall beneath the Crescent Shell!
    atrium_rings_bot = []
    atrium_rings_top = []
    for iu in range(4, n_u - 3):
        u = iu / n_u
        p_in = crescent_point(u, 0.16, offset_z=-0.8)
        p_out = crescent_point(u, 0.86, offset_z=-0.8)
        atrium_rings_bot.append((p_in[0], p_in[1], 0.25))
        atrium_rings_top.append((p_in[0], p_in[1], max(6.0, p_in[2] - 0.2)))
        if iu % 3 == 0:
            mb.add_tube((p_in[0], p_in[1], 0.25), (p_in[0], p_in[1], p_in[2]), 0.65, lattice_silver, segments=6)
            mb.add_tube((p_out[0], p_out[1], 0.25), (p_out[0], p_out[1], p_out[2]), 0.60, lattice_silver, segments=6)

    mb.add_loft([atrium_rings_bot, atrium_rings_top], mats["em_warm"], closed_loop=False, smooth=True)
    for i in range(0, len(atrium_rings_bot), 2):
        p0 = atrium_rings_bot[i]
        p1 = atrium_rings_top[i]
        mb.add_tube((p0[0] - 0.3, p0[1], p0[2]), (p1[0] - 0.3, p1[1], p1[2]), 0.22, mats["metal_dark"], segments=4)

    outer_wall_bot = []
    outer_wall_top = []
    for iu in range(3, n_u - 2):
        p_o = crescent_point(iu / n_u, 0.94, offset_z=-0.4)
        outer_wall_bot.append((p_o[0], p_o[1], 0.25))
        outer_wall_top.append((p_o[0], p_o[1], max(5.0, p_o[2])))
    mb.add_loft([outer_wall_bot, outer_wall_top], mats["glass_dark"], closed_loop=False, smooth=True)

    # Iconic Glowing Pearl Theatre / IMAX Pavilion inside the Crescent Lagoon
    mb.add_cylinder((34.0, 0.0, 7.5), 14.8, 13.2, 14.5, mats["glass_blue"], segments=28, smooth=True)
    mb.add_icosphere((34.0, 0.0, 14.5), 13.2, crescent_shell, subdivisions=3, scale=(1.0, 1.0, 0.56), smooth=True)
    for k in range(20):
        a = 2.0 * math.pi * k / 20.0
        px, py = 34.0 + 14.9 * math.cos(a), 14.9 * math.sin(a)
        mb.add_tube((px, py, 0.5), (px, py, 14.5), 0.24, mats["em_warm"], segments=4)
    # Glowing Pearl base ring
    pearl_ring = [(34.0 + 15.2 * math.cos(2 * math.pi * k / 24), 15.2 * math.sin(2 * math.pi * k / 24), 0.55) for k in range(24)]
    mb.add_polyline_tubes(pearl_ring, 0.26, mats["em_cyan"], segments=5, closed=True)

    # ------------------------------------------------------------------
    # 3. MOON HARBOUR EUROPEAN WATERFRONT GABLE BUILDINGS (7 varied buildings)
    # ------------------------------------------------------------------
    euro_buildings = [
        (-92, 69.0, 18.0, 12.0, 8.5, 5.2, mats["wall_cream"], mats["roof_terracotta"]),
        (-62, 69.5, 21.0, 12.5, 10.2, 6.0, mats["wall_white"], mats["roof_slate"]),
        (-32, 69.5, 19.0, 12.0, 9.2, 5.6, mats["wall_cream"], mats["roof_terracotta"]),
        (0, 69.5, 22.0, 13.0, 11.2, 6.4, mats["wall_white"], mats["roof_slate"]),
        (32, 69.5, 20.0, 12.0, 9.6, 5.8, mats["wall_cream"], mats["roof_terracotta"]),
        (62, 69.5, 21.0, 12.5, 10.0, 6.0, mats["wall_white"], mats["roof_slate"]),
        (90, 69.0, 18.0, 12.0, 8.8, 5.4, mats["wall_cream"], mats["roof_terracotta"]),
    ]
    for ang_deg, r_mid, w, d, wh, rh, wmat, rmat in euro_buildings:
        a = ang_deg * math.pi / 180.0
        bx = -24.0 - r_mid * math.cos(a)
        by = r_mid * math.sin(a)
        rot_z = -a + 0.5 * math.pi
        mb.add_pitched_roof_building(
            (bx, by), w, d, z_base=0.28, wall_h=wh, roof_h=rh,
            wall_mat=wmat,
            roof_mat=rmat,
            glass_mat=mats["glass_dark"],
            emissive_mat=mats["em_warm"],
            rot_z=rot_z,
            eave_overhang=0.95,
        )
        # Dormer gable accent on roof center
        mb.add_box((bx, by, 0.28 + wh + 0.45 * rh), (3.8, d * 0.72, 2.8), wmat, rot_euler=(0, 0, rot_z))
        mb.add_box((bx, by, 0.28 + wh + 0.45 * rh + 1.5), (4.2, d * 0.78, 0.5), rmat, rot_euler=(0, 0, rot_z))

    # Waterfront Clock/Lantern Tower on Moon Harbour Pier tip
    mb.add_box_minmax(-101.5, -95.5, -9.0, -3.0, 0.28, 17.5, mats["wall_cream"])
    mb.add_box_minmax(-102.0, -95.0, -9.5, -2.5, 17.5, 18.2, mats["metal_dark"])
    mb.add_cylinder((-98.5, -6.0, 21.4), 4.5, 0.2, 6.4, mats["roof_slate"], segments=4, rot_euler=(0, 0, 0.25 * math.pi), smooth=False)
    mb.add_box_minmax(-101.7, -95.3, -9.2, -2.8, 13.0, 16.5, mats["em_gold"])

    # Warm promenade lamps curving along Moon Harbour boardwalk
    for i in range(1, n_pier, 2):
        px, py, _ = outer_edge_pts[i]
        a = -0.58 * math.pi + 1.16 * math.pi * (i / n_pier)
        lx, ly = px + 2.5 * math.cos(a), py - 2.5 * math.sin(a)
        mb.add_cylinder((lx, ly, 3.0), 0.14, 0.10, 5.4, mats["metal_dark"], segments=6)
        mb.add_icosphere((lx, ly, 5.9), 0.46, mats["em_warm"], subdivisions=2)

    mb.build(origin=(0.0, 0.0, 0.0))
    export_glb(OUT_PATH)
    verify_glb(OUT_PATH)


if __name__ == "__main__":
    build_arts_centre_and_moon()
