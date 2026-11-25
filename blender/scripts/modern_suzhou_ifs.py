"""Generate 450m Suzhou IFS (苏州国金中心) — Jiangsu's tallest skyscraper with sculptural
tapering 'Koi Leaping Over Dragon Gate' (鲤鱼跳龙门) silhouette & diagonal glowing fishtail crown!
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

OUT_PATH = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/suzhou_ifs.glb"


def koi_section_point(theta, z, expand=0.0):
    """Smooth tapering almond/koi-fish lenticular cross-section of Suzhou IFS.
    Long axis along X (prow facing West -X toward Jinji Lake, sculpted tail spine East +X).
    """
    t = max(0.0, min(1.0, z / 412.0))
    rx = (36.5 - 13.8 * (t ** 1.18)) + expand
    ry = (26.5 - 10.6 * (t ** 1.15)) + expand

    if z > 250.0:
        u = min(1.0, (z - 250.0) / 160.0)
        ry -= 1.6 * (u ** 1.4)

    ct = math.cos(theta)
    st = math.sin(theta)
    x = rx * ct
    y = ry * math.copysign(abs(st) ** 0.90, st) * (0.94 + 0.06 * ct)

    rot = 0.06 * t
    xr = x * math.cos(rot) - y * math.sin(rot)
    yr = x * math.sin(rot) + y * math.cos(rot)
    return (xr, yr, z)


def build_suzhou_ifs():
    clear_scene()
    mats = make_standard_modern_mats()
    glass_ifs = make_mat("Glass_IFSCurtain", "#1c3d5e", metallic=0.84, roughness=0.10)
    glass_crown = make_mat("Glass_IFSCrown", "#2b5e8a", metallic=0.80, roughness=0.12)
    fin_champagne = make_mat("Metal_IFSFin", "#d9ccb4", metallic=0.88, roughness=0.22)
    all_mats = [
        glass_ifs, glass_crown, fin_champagne,
        mats["glass_dark"], mats["metal_silver"], mats["stone_granite"], mats["stone_light"],
        mats["water_pool"], mats["trunk_bark"], mats["foliage_green"],
        mats["em_gold"], mats["em_cyan"], mats["em_warm"],
    ]

    mb = MeshBuilder("SuzhouIFS_450m", all_mats)

    # ------------------------------------------------------------------
    # 1. MAIN TAPERING KOI TOWER SHAFT (z = 0m .. 408m, 48-seg ultra-smooth!)
    # ------------------------------------------------------------------
    n_ang = 48
    z_levels = [
        0, 12, 26, 44, 64, 86, 110, 136, 164, 192,
        220, 248, 276, 304, 332, 358, 382, 398, 408.0
    ]
    shaft_rings = []
    for z in z_levels:
        ring = [koi_section_point(2.0 * math.pi * k / n_ang, z) for k in range(n_ang)]
        shaft_rings.append(ring)
    mb.add_loft(shaft_rings, glass_ifs, closed_loop=True, cap_start=True, cap_end=True, smooth=True)

    # ------------------------------------------------------------------
    # 2. ICONIC DIAGONAL SLICED GLOWING FISHTAIL CROWN (z = 406m .. 450.0m)
    # ------------------------------------------------------------------
    n_crown = 32
    core_bot = [koi_section_point(2.0 * math.pi * k / n_crown, 406.0, expand=-2.2) for k in range(n_crown)]
    core_mid = []
    core_top = []
    for k in range(n_crown):
        a = 2.0 * math.pi * k / n_crown
        p = koi_section_point(a, 412.0, expand=-3.0)
        diag = 0.5 * (1.0 + math.cos(a - 0.2))
        z_m = 414.0 + 10.0 * diag
        z_t = 420.0 + 18.0 * diag
        core_mid.append((p[0] * 0.90, p[1] * 0.88, z_m))
        core_top.append((p[0] * 0.68, p[1] * 0.65, z_t))
    mb.add_loft([core_bot, core_mid, core_top], glass_crown, closed_loop=True, cap_start=False, cap_end=True, smooth=True)

    # Glowing luminous crown lantern horizontal & diagonal rings
    for z_ring in (410.0, 416.0, 422.0, 428.0, 434.0):
        frac = (z_ring - 406.0) / 34.0
        scale = 1.0 - 0.30 * frac
        pts = []
        for k in range(n_crown):
            a = 2.0 * math.pi * k / n_crown
            p = koi_section_point(a, 410.0, expand=-1.9)
            pts.append((p[0] * scale, p[1] * scale, z_ring))
        mb.add_polyline_tubes(pts, 0.42, mats["em_gold"] if z_ring in (410.0, 422.0, 434.0) else mats["em_cyan"], segments=5, closed=True)

    def build_fishtail_fin(a_start, a_end, peak_z, peak_a, blade_mat, glow_mat):
        nu, nv = 18, 12
        outer_grid = []
        inner_grid = []
        top_edge_pts = []
        for iu in range(nu + 1):
            u = iu / nu
            a = a_start + (a_end - a_start) * u
            dist = abs(a - peak_a) / max(0.01, abs(a_end - a_start))
            z_top = 408.0 + (peak_z - 408.0) * (max(0.0, 1.0 - dist * 1.08) ** 0.72)
            ro_col, ri_col = [], []
            for iv in range(nv + 1):
                v = iv / nv
                z = 406.0 + (z_top - 406.0) * v
                taper = 1.0 - 0.30 * (v ** 1.35)
                p_o = koi_section_point(a, 408.0, expand=0.35)
                p_i = koi_section_point(a, 408.0, expand=-1.65)
                ro_col.append((p_o[0] * taper, p_o[1] * taper, z))
                ri_col.append((p_i[0] * taper, p_i[1] * taper, z))
            outer_grid.append(ro_col)
            inner_grid.append(ri_col)
            top_edge_pts.append(ro_col[-1])

        mb.add_loft(outer_grid, blade_mat, closed_loop=False, smooth=True)
        mb.add_loft([list(reversed(c)) for c in inner_grid], fin_champagne, closed_loop=False, smooth=True)
        mb.add_loft([[c[-1] for c in outer_grid], [c[-1] for c in inner_grid]], glow_mat, closed_loop=False, smooth=True)
        # Razor-sharp glowing LED outline tracing the diagonal koi-tail blade!
        mb.add_polyline_tubes(top_edge_pts, 0.76, glow_mat, segments=6, smooth=True)
        # Crisp vertical & diagonal koi-scale lattice ribs across the fishtail crown!
        for iu in range(0, nu + 1, 2):
            mb.add_polyline_tubes(outer_grid[iu], 0.36, glow_mat if iu in (0, nu // 2, nu) else fin_champagne, segments=4, smooth=True)
        for iv in (3, 6, 9):
            horiz = [outer_grid[iu][iv] for iu in range(nu + 1)]
            mb.add_polyline_tubes(horiz, 0.28, glow_mat if iv == 9 else fin_champagne, segments=4, smooth=True)

    # Primary East-soaring Koi Tail Blade reaching exact 450.0m!
    build_fishtail_fin(-0.42 * math.pi, 0.48 * math.pi, peak_z=450.0, peak_a=0.05 * math.pi,
                       blade_mat=glass_crown, glow_mat=mats["em_gold"])
    # Secondary West-soaring Koi Tail Blade reaching 435.0m (creating dramatic fishtail V-cleft!)
    build_fishtail_fin(0.58 * math.pi, 1.44 * math.pi, peak_z=435.0, peak_a=1.02 * math.pi,
                       blade_mat=glass_crown, glow_mat=mats["em_cyan"])

    # ------------------------------------------------------------------
    # 3. CRISP VERTICAL CURTAIN-WALL FINS & GLOWING LED RIBS (0..408m)
    # 24 full-height vertical fins wrapping the entire curved facade!
    # ------------------------------------------------------------------
    for k in range(0, n_ang, 2):
        a = 2.0 * math.pi * k / n_ang
        pts = [koi_section_point(a, z, expand=0.55) for z in z_levels]
        if k in (0, 12, 24, 36):
            led_m = mats["em_gold"] if k in (0, 24) else mats["em_cyan"]
            mb.add_polyline_tubes(pts, 0.56, led_m, segments=5, smooth=True)
        elif k in (6, 18, 30, 42):
            mb.add_polyline_tubes(pts, 0.38, mats["em_cyan"], segments=4, smooth=True)
        else:
            mb.add_polyline_tubes(pts, 0.34, fin_champagne, segments=4, smooth=True)

    # Rhythmic Illuminated Office Floor Bands & Spandrel Collars (26 bands over 408m!)
    floor_band_zs = [
        24, 40, 56, 72, 88, 104, 120, 136, 152, 168, 184, 200,
        216, 232, 248, 264, 280, 296, 312, 328, 344, 360, 376, 390, 404
    ]
    for idx_f, z in enumerate(floor_band_zs):
        r_lo = [koi_section_point(2.0 * math.pi * k / n_ang, z - 0.52, expand=0.45) for k in range(n_ang)]
        r_hi = [koi_section_point(2.0 * math.pi * k / n_ang, z + 0.52, expand=0.45) for k in range(n_ang)]
        if idx_f % 3 == 0:
            mat_b = mats["em_gold"]
        elif idx_f % 3 == 1:
            mat_b = mats["em_cyan"]
        else:
            mat_b = fin_champagne
        mb.add_loft([r_lo, r_hi], mat_b, closed_loop=True, smooth=False)

    # ------------------------------------------------------------------
    # 4. SLEEK TERRACED PLAZA PODIUM & COMMERCIAL WINGS (z = -2.5m .. 24m)
    # ------------------------------------------------------------------
    mb.add_box_minmax(-78.0, 78.0, -72.0, 72.0, -2.5, 0.0, mats["stone_granite"])
    mb.add_box_minmax(-74.0, 74.0, -68.0, 68.0, 0.0, 0.35, mats["stone_light"])

    for sy in (-1.0, 1.0):
        mb.add_box_minmax(-68.0, -38.0, sy * 22.0 - 12.0, sy * 22.0 + 12.0, 0.35, 0.52, mats["water_pool"])
        mb.add_tube((-68.0, sy * 10.0, 0.62), (-38.0, sy * 10.0, 0.62), 0.28, mats["em_cyan"], segments=5)
        mb.add_tube((-68.0, sy * 34.0, 0.62), (-38.0, sy * 34.0, 0.62), 0.24, mats["em_gold"], segments=4)

    for sy in (-1.0, 1.0):
        y0 = 32.0 if sy > 0 else -62.0
        y1 = 62.0 if sy > 0 else -32.0
        mb.add_box_minmax(-52.0, 56.0, y0, y1, 0.35, 19.5, mats["glass_dark"])
        mb.add_box_minmax(-54.0, 58.0, y0 - 1.2, y1 + 1.2, 19.5, 21.2, fin_champagne)
        # Vertical podium facade mullions
        for mx in range(-48, 56, 12):
            mb.add_tube((mx, 31.7 * sy, 0.4), (mx, 31.7 * sy, 19.6), 0.26, fin_champagne, segments=4)
            mb.add_tube((mx, 62.3 * sy, 0.4), (mx, 62.3 * sy, 19.6), 0.26, fin_champagne, segments=4)
        for zb in (5.0, 12.5, 19.6):
            face_y = 31.8 if sy > 0 else -31.8
            mb.add_tube((-51.0, face_y, zb), (55.0, face_y, zb), 0.38, mats["em_warm"] if zb < 19.0 else mats["em_gold"], segments=5)
            outer_y = 62.2 if sy > 0 else -62.2
            mb.add_tube((-51.0, outer_y, zb), (55.0, outer_y, zb), 0.38, mats["em_warm"] if zb < 19.0 else mats["em_gold"], segments=5)

    # Grand West entrance canopy + sculptural columns
    mb.add_box_minmax(-56.0, -28.0, -18.0, 18.0, 11.2, 12.6, fin_champagne)
    mb.add_tube((-56.2, -18.0, 11.9), (-56.2, 18.0, 11.9), 0.38, mats["em_gold"], segments=5)
    for cy in (-15.0, -5.0, 5.0, 15.0):
        mb.add_cylinder((-52.0, cy, 5.8), 0.72, 0.54, 11.2, mats["metal_silver"], segments=8)

    # Perimeter plaza landscape trees & glowing plaza bollards
    for tx, ty in [(-66, -54), (-66, 54), (66, -54), (66, 54), (-66, -12), (-66, 12), (66, -12), (66, 12)]:
        mb.add_cylinder((tx, ty, 2.8), 0.38, 0.22, 5.2, mats["trunk_bark"], segments=6)
        mb.add_icosphere((tx, ty, 6.8), 3.2, mats["foliage_green"], subdivisions=2, scale=(1.1, 1.1, 0.85))

    mb.build(origin=(0.0, 0.0, 0.0))
    export_glb(OUT_PATH)
    verify_glb(OUT_PATH)


if __name__ == "__main__":
    build_suzhou_ifs()
