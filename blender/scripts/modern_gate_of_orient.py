"""Generate 301.8m Gate of the Orient (东方之门) & Suzhou Center Wings of the Future."""
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

OUT_PATH = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/gate_of_orient.glb"


def outer_y_profile(z):
    """Outer North/South half-width of Gate of the Orient from z=0 to 301.8m."""
    t = max(0.0, min(1.0, z / 301.8))
    if t < 0.72:
        # Gentle organic inward taper from 74m at base to 63m at z=217m
        u = t / 0.72
        return 74.0 - 11.0 * (u ** 1.35)
    else:
        # Graceful iconic curved shoulder sweep from 63m to 44m at 301.8m
        u = (t - 0.72) / 0.28
        return 63.0 - 19.0 * (u ** 1.65)


def inner_y_profile(z):
    """Inner arch opening half-width along Y_blender (Z_three).
    CRITICAL: Clear opening width >= 64m (|y| >= 34m) from z=0 to z=185m,
    and smooth monumental pointed/elliptical arch curving up to apex at z=224m!
    """
    if z <= 178.0:
        # Slight elegant taper from 36m at base to 34.5m at springline (clear width 69m..72m!)
        u = z / 178.0
        return 36.0 - 1.5 * u
    elif z < 224.0:
        # Smooth arch curve from y=34.5 at z=178 to y=0 at z=224
        u = (z - 178.0) / 46.0
        return 34.5 * math.sqrt(max(0.0, 1.0 - u * u))
    else:
        return 0.0


def half_x_profile(z):
    """East-West half-thickness of the towers (lenticular rounded profile)."""
    t = max(0.0, min(1.0, z / 301.8))
    return 22.0 - 6.0 * (t ** 1.2)


def rounded_rect_ring(x_half, y_min, y_max, z, corner_r=6.0, segs_per_corner=4):
    """Generate a smooth rounded-corner cross-section ring at elevation z."""
    yc = 0.5 * (y_min + y_max)
    yh = 0.5 * (y_max - y_min)
    cr = min(corner_r, x_half * 0.48, yh * 0.48)
    pts = []
    # 4 corners: (+x,+y), (-x,+y), (-x,-y), (+x,-y)
    corners = [
        (x_half - cr, yc + yh - cr, 0.0, 0.5 * math.pi),
        (-x_half + cr, yc + yh - cr, 0.5 * math.pi, math.pi),
        (-x_half + cr, yc - yh + cr, math.pi, 1.5 * math.pi),
        (x_half - cr, yc - yh + cr, 1.5 * math.pi, 2.0 * math.pi),
    ]
    for cx, cy, a0, a1 in corners:
        for s in range(segs_per_corner + 1):
            a = a0 + (a1 - a0) * (s / segs_per_corner)
            pts.append((cx + cr * math.cos(a), cy + cr * math.sin(a), z))
    return pts


def build_gate_of_orient():
    clear_scene()
    mats = make_standard_modern_mats()
    glass_orient = make_mat("Glass_OrientCurtain", "#1e4266", metallic=0.80, roughness=0.11)
    glass_crown = make_mat("Glass_OrientCrown", "#2d5c85", metallic=0.78, roughness=0.13)
    canopy_glass = make_mat("Glass_WingsCanopy", "#386e96", metallic=0.72, roughness=0.14)
    all_mats = list(mats.values()) + [glass_orient, glass_crown, canopy_glass]

    mb = MeshBuilder("GateOfOrient", all_mats)

    # ------------------------------------------------------------------
    # 1. TWIN LOWER TOWER LEGS (z = 0m .. 224m) - North (+Y) & South (-Y)
    # ------------------------------------------------------------------
    z_leg_levels = [
        0, 12, 26, 44, 64, 86, 110, 134, 156, 178,
        186, 194, 202, 209, 215, 220, 224.0
    ]

    for sign in (1.0, -1.0):
        rings = []
        for z in z_leg_levels:
            yo = outer_y_profile(z)
            yi = max(inner_y_profile(z), 0.5 if z >= 224.0 else 0.0)
            xh = half_x_profile(z)
            if sign > 0:
                y0, y1 = yi, yo
            else:
                y0, y1 = -yo, -yi
            ring = rounded_rect_ring(xh, y0, y1, z, corner_r=5.5, segs_per_corner=4)
            rings.append(ring)
        mb.add_loft(rings, glass_orient, closed_loop=True, cap_start=True, cap_end=False, smooth=True)

        # Horizontal metallic spandrel / floor accent rings every 18m (huge sense of scale!)
        for z in range(18, 180, 18):
            yo = outer_y_profile(z) + 0.35
            yi = inner_y_profile(z) - 0.35
            xh = half_x_profile(z) + 0.35
            y0, y1 = (yi, yo) if sign > 0 else (-yo, -yi)
            r_lo = rounded_rect_ring(xh, y0, y1, z - 0.55, corner_r=5.6, segs_per_corner=3)
            r_hi = rounded_rect_ring(xh, y0, y1, z + 0.55, corner_r=5.6, segs_per_corner=3)
            mb.add_loft([r_lo, r_hi], mats["metal_silver"], closed_loop=True, cap_start=True, cap_end=True, smooth=False)

        # Glowing horizontal floor accent bands on mid/upper levels (Emissive_Gold & Emissive_Cyan)
        for idx_b, z in enumerate([48, 78, 108, 138, 168]):
            yo = outer_y_profile(z) + 0.42
            yi = inner_y_profile(z) - 0.42
            xh = half_x_profile(z) + 0.42
            y0, y1 = (yi, yo) if sign > 0 else (-yo, -yi)
            em = mats["em_gold"] if idx_b % 2 == 0 else mats["em_cyan"]
            r_lo = rounded_rect_ring(xh, y0, y1, z - 0.38, corner_r=5.6, segs_per_corner=3)
            r_hi = rounded_rect_ring(xh, y0, y1, z + 0.38, corner_r=5.6, segs_per_corner=3)
            mb.add_loft([r_lo, r_hi], em, closed_loop=True, cap_start=False, cap_end=False, smooth=False)

        # Crisp vertical metallic mullions & glowing vertical LED strips on West (-X) and East (+X) faces
        for sx in (-1.0, 1.0):
            # 7 vertical mullions per face per leg
            for frac in [0.12, 0.28, 0.44, 0.60, 0.76, 0.90]:
                pts = []
                for z in z_leg_levels:
                    yo = outer_y_profile(z)
                    yi = inner_y_profile(z)
                    y_val = sign * (yi + frac * (yo - yi))
                    x_val = sx * (half_x_profile(z) + 0.45)
                    pts.append((x_val, y_val, z))
                is_led = frac in (0.12, 0.60, 0.90)
                if is_led:
                    led_mat = mats["em_gold"] if frac != 0.60 else mats["em_cyan"]
                    mb.add_polyline_tubes(pts, 0.42, led_mat, segments=4, smooth=False)
                else:
                    mb.add_polyline_tubes(pts, 0.36, mats["metal_silver"], segments=4, smooth=False)

            # Outer silhouette sweeping glowing edge ribbon (from ground to 224m)
            outer_pts = []
            for z in z_leg_levels:
                y_val = sign * (outer_y_profile(z) + 0.5)
                x_val = sx * (half_x_profile(z) - 2.0)
                outer_pts.append((x_val, y_val, z))
            mb.add_polyline_tubes(outer_pts, 0.58, mats["em_gold"], segments=5, smooth=True)

            # Inner arch monumental glowing outline!
            arch_pts = []
            for z in z_leg_levels:
                y_val = sign * inner_y_profile(z)
                x_val = sx * (half_x_profile(z) - 1.5)
                arch_pts.append((x_val, y_val, z))
            mb.add_polyline_tubes(arch_pts, 0.72, mats["em_gold"], segments=6, smooth=True)

    # Arch soffit transverse glowing ribs inside the grand arch vault (z=178..224m)
    for z in [184, 194, 204, 213, 220, 224]:
        yi = inner_y_profile(z)
        xh = half_x_profile(z) - 0.8
        for sign in (1.0, -1.0):
            if z == 224 and sign < 0:
                continue
            mb.add_tube((-xh, sign * yi, z - 0.3), (xh, sign * yi, z - 0.3), 0.52, mats["em_cyan"], segments=5)

    # ------------------------------------------------------------------
    # 2. CROWNED SKY-BRIDGE ARCH & SCULPTURAL CROWN (z = 224m .. 301.8m)
    # ------------------------------------------------------------------
    z_crown_levels = [224.0, 232.0, 242.0, 254.0, 266.0, 278.0, 289.0, 296.5, 301.8]
    crown_rings = []
    for z in z_crown_levels:
        yo = outer_y_profile(z)
        xh = half_x_profile(z)
        # Sculpted double-curved crown narrowing gracefully at top
        crown_rings.append(rounded_rect_ring(xh, -yo, yo, z, corner_r=6.0, segs_per_corner=5))
    mb.add_loft(crown_rings, glass_crown, closed_loop=True, cap_start=True, cap_end=True, smooth=True)

    # Recessed luminous sky-gallery bands in the sky-bridge crown (234m..292m)
    for idx_c, z in enumerate([234.0, 246.0, 258.0, 270.0, 282.0, 293.0]):
        yo = outer_y_profile(z) + 0.55
        xh = half_x_profile(z) + 0.55
        r0 = rounded_rect_ring(xh, -yo, yo, z - 0.7, corner_r=6.1, segs_per_corner=4)
        r1 = rounded_rect_ring(xh, -yo, yo, z + 0.7, corner_r=6.1, segs_per_corner=4)
        mat_band = mats["em_gold"] if idx_c % 2 == 0 else mats["em_cyan"]
        mb.add_loft([r0, r1], mat_band, closed_loop=True, cap_start=False, cap_end=False, smooth=False)

    # Vertical crown ribs wrapping smoothly from z=224m to z=301.8m
    for sx in (-1.0, 1.0):
        for frac in [-0.88, -0.66, -0.44, -0.22, 0.0, 0.22, 0.44, 0.66, 0.88]:
            pts = []
            for z in z_crown_levels:
                yo = outer_y_profile(z)
                xh = half_x_profile(z) + 0.45
                pts.append((sx * xh, frac * yo, z))
            m_rib = mats["em_gold"] if abs(frac) in (0.0, 0.44, 0.88) else mats["metal_silver"]
            mb.add_polyline_tubes(pts, 0.48, m_rib, segments=4, smooth=True)

    # Sculptural crowning arch parapet & rooftop sky-garden crest at 301.8m
    top_yo = outer_y_profile(301.8)
    top_xh = half_x_profile(301.8)
    for sx in (-1.0, 1.0):
        crest_pts = []
        for i in range(17):
            u = -1.0 + 2.0 * (i / 16.0)
            y_val = u * top_yo
            # Subtle twin-shoulder sculptural rise at outer edges
            z_val = 301.8 + 1.8 * (u * u) - 1.8
            crest_pts.append((sx * (top_xh - 0.8), y_val, z_val))
        mb.add_polyline_tubes(crest_pts, 0.85, mats["em_gold"], segments=6, smooth=True)
    # Cross-braced crown skyline fins
    for y_fin in (-32.0, -16.0, 0.0, 16.0, 32.0):
        mb.add_tube((-top_xh + 1.0, y_fin, 301.2), (top_xh - 1.0, y_fin, 301.2), 0.55, mats["metal_silver"], segments=4)

    # ------------------------------------------------------------------
    # 3. GROUND PLAZA & LAKESIDE TERRACE (z = -2.5m .. 0.0m)
    # ------------------------------------------------------------------
    # Main lakeside podium foundation (leaves arch center clean & flat at z=0!)
    mb.add_box_minmax(-98.0, 82.0, -138.0, 138.0, -2.5, 0.0, mats["stone_granite"])
    # Raised architectural stone carpet under arch leading West-to-East
    mb.add_box_minmax(-98.0, 82.0, -32.0, 32.0, -0.02, 0.25, mats["stone_light"])
    # Glowing runway guide strips along arch plaza edges (y = ±30m)
    for sy in (-1.0, 1.0):
        mb.add_tube((-94.0, sy * 30.5, 0.45), (78.0, sy * 30.5, 0.45), 0.35, mats["em_cyan"], segments=4)
        mb.add_tube((-94.0, sy * 33.5, 0.35), (78.0, sy * 33.5, 0.35), 0.28, mats["em_gold"], segments=4)
    # East lakeside waterfront glowing edge (facing Jinji Lake +X)
    mb.add_tube((81.8, -137.0, 0.2), (81.8, 137.0, 0.2), 0.42, mats["em_warm"], segments=4)

    # ------------------------------------------------------------------
    # 4. SUZHOU CENTER "WINGS OF THE FUTURE" (苏州中心未来之翼)
    # Flanking North (y = +62..+134) & South (y = -134..-62) and West plaza wings!
    # Strictly outside |y| < 48m so the central 68m+ arch flight corridor stays 100% open!
    # ------------------------------------------------------------------
    for sign in (1.0, -1.0):
        # Podium retail base blocks flanking North and South of the twin legs
        y_in = 68.0 if sign > 0 else -130.0
        y_out = 130.0 if sign > 0 else -68.0
        mb.add_box_minmax(-82.0, 44.0, y_in, y_out, 0.0, 15.5, mats["glass_dark"])
        # Warm glowing retail atrium horizontal strip on podium facade
        for z_strip in (4.5, 10.5):
            y_face = 67.6 if sign > 0 else -67.6
            mb.add_tube((-80.0, y_face, z_strip), (42.0, y_face, z_strip), 0.45, mats["em_warm"], segments=4)
            y_outer = 130.4 if sign > 0 else -130.4
            mb.add_tube((-80.0, y_outer, z_strip), (42.0, y_outer, z_strip), 0.45, mats["em_warm"], segments=4)
            mb.add_tube((-82.4, y_in + 2.0, z_strip), (-82.4, y_out - 2.0, z_strip), 0.45, mats["em_warm"], segments=4)

        # Sweeping Organic Flowing "Wings of the Future" Canopy Roof!
        # Parametric multi-lobe undulating wave surface over each wing
        nx, ny = 18, 12
        x_min, x_max = -92.0, 58.0
        y_start = 52.0 * sign
        y_end = 136.0 * sign

        def wing_z(u, v):
            # u in [0,1] along West->East, v in [0,1] from inner->outer
            # Dramatic soaring wing wave peaking at 27m near outer-west and sweeping down to 16m
            wave1 = 4.8 * math.sin(u * math.pi * 2.0 - 0.5) * math.sin(v * math.pi)
            wave2 = 3.2 * math.cos(v * math.pi * 1.5) * math.sin(u * math.pi)
            arch_lift = 6.5 * math.sin(u * math.pi) * (0.4 + 0.6 * math.sin(v * math.pi * 0.85))
            return 16.5 + arch_lift + wave1 + wave2

        # Build thick doubly-curved wing canopy shell using lofted cross-sections along X
        shell_top_rings = []
        shell_bot_rings = []
        for ix in range(nx + 1):
            u = ix / nx
            x = x_min + (x_max - x_min) * u
            # Taper wing width slightly at west & east wingtips for organic phoenix-wing silhouette
            tip_taper = 0.72 + 0.28 * math.sin(u * math.pi)
            ring_top = []
            ring_bot = []
            for iy in range(ny + 1):
                v = iy / ny
                y_mid = 0.5 * (y_start + y_end)
                y_half = 0.5 * (y_end - y_start) * tip_taper
                y = y_mid + y_half * (2.0 * v - 1.0)
                z = wing_z(u, v)
                ring_top.append((x, y, z + 0.45))
                ring_bot.append((x, y, z - 0.45))
            shell_top_rings.append(ring_top)
            shell_bot_rings.append(ring_bot)

        # Top and bottom canopy surfaces
        mb.add_loft(shell_top_rings, canopy_glass, closed_loop=False, smooth=True)
        mb.add_loft([list(reversed(r)) for r in shell_bot_rings], mats["metal_silver"], closed_loop=False, smooth=True)

        # Flowing glowing structural ribs along the sweeping wing canopy (signature LED light veins!)
        for iy in [0, 3, 6, 9, 12]:
            rib_pts = [shell_top_rings[ix][iy] for ix in range(nx + 1)]
            rib_mat = mats["em_cyan"] if iy in (0, 6, 12) else mats["em_gold"]
            rad = 0.48 if iy in (0, 12) else 0.34
            mb.add_polyline_tubes(rib_pts, rad, rib_mat, segments=4, smooth=True)

        # Transverse structural steel ribs across the wing
        for ix in range(0, nx + 1, 3):
            cross_pts = [shell_top_rings[ix][iy] for iy in range(ny + 1)]
            mb.add_polyline_tubes(cross_pts, 0.28, mats["metal_silver"], segments=4, smooth=True)

        # Sculptural V-columns supporting the cantilevered wing overhang
        for ix in (2, 7, 12, 16):
            p_top = shell_bot_rings[ix][1]
            p_base = (p_top[0], p_top[1] + 5.0 * sign, 0.0)
            mb.add_tube(p_base, p_top, 0.65, mats["metal_white"], segments=6)

    mb.build(origin=(0.0, 0.0, 0.0))
    export_glb(OUT_PATH)
    verify_glb(OUT_PATH)


if __name__ == "__main__":
    build_gate_of_orient()
