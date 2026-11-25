"""Generate Ligongdi Causeway (李公堤) — 340m lake causeway, navigable modern arch bridge, and neo-Suzhou waterfront pavilions.
NOTE: world-layout.json anchor for Station 09 is (1000, 0.0, 365) where Y=0.0 is Jinji Lake water surface!
Therefore in Blender Z=0.0 is water level, foundations descend to Z=-2.5m, causeway deck is at Z=+2.0m.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modern_common import (
    clear_scene,
    make_standard_modern_mats,
    MeshBuilder,
    export_glb,
    verify_glb,
)

OUT_PATH = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/ligongdi.glb"


def bridge_deck_z(x):
    """Smooth vertical profile of the 340m causeway + signature central navigable arch bridge.
    Clear arch opening around x = -15..+15m (width 30m >= 20m) with clear soffit height >= 14.4m (>= 12m)!
    """
    ax = abs(x)
    if ax <= 18.0:
        u = ax / 18.0
        return 15.6 - 2.6 * (u * u)
    elif ax <= 58.0:
        u = (ax - 18.0) / 40.0
        s = 0.5 * (1.0 + math.cos(u * math.pi))
        return 2.0 + 11.0 * s
    else:
        return 2.0


def build_ligongdi():
    clear_scene()
    mats = make_standard_modern_mats()
    mb = MeshBuilder("LigongdiCauseway", list(mats.values()))

    # ------------------------------------------------------------------
    # 1. CONTINUOUS 340m CAUSEWAY DECK & EMBANKMENTS (x = -170 .. +170)
    # ------------------------------------------------------------------
    for sx in (-1.0, 1.0):
        x0, x1 = (56.0, 170.0) if sx > 0 else (-170.0, -56.0)
        mb.add_box_minmax(x0, x1, -11.0, 11.0, -2.5, 2.0, mats["stone_granite"])
        mb.add_box_minmax(x0, x1, -9.8, 9.8, 2.0, 2.25, mats["stone_light"])
        # Cantilevered lakeside timber boardwalks + balustrades
        for sy in (-1.0, 1.0):
            y_in = 10.2 * sy
            y_out = 14.8 * sy
            mb.add_box_minmax(x0 + 3.0, x1 - 3.0, min(y_in, y_out), max(y_in, y_out), 1.35, 1.85, mats["wood_deck"])
            mb.add_tube((x0 + 2.0, 14.9 * sy, 1.75), (x1 - 2.0, 14.9 * sy, 1.75), 0.24, mats["em_warm"], segments=5)
            mb.add_tube((x0 + 1.0, 10.0 * sy, 2.35), (x1 - 1.0, 10.0 * sy, 2.35), 0.20, mats["em_gold"], segments=4)
            # Boardwalk wooden handrail & posts
            mb.add_tube((x0 + 4.0, 14.4 * sy, 2.85), (x1 - 4.0, 14.4 * sy, 2.85), 0.10, mats["metal_dark"], segments=4)
            for px in range(int(x0) + 6, int(x1) - 4, 8):
                mb.add_cylinder((px, 14.4 * sy, 2.35), 0.08, 0.08, 1.0, mats["metal_dark"], segments=4)

        # Waterfront Pavilion Plaza Islands at x = ±110m
        cx_isl = sx * 110.0
        mb.add_box_minmax(cx_isl - 44.0, cx_isl + 44.0, -35.0, 35.0, -2.5, 1.9, mats["stone_granite"])
        mb.add_box_minmax(cx_isl - 42.0, cx_isl + 42.0, -33.0, 33.0, 1.9, 2.15, mats["stone_light"])

        # Neo-Suzhou white courtyard garden walls with dark slate cap & circular moon gate openings
        for sy in (-1.0, 1.0):
            wy = sy * 32.5
            mb.add_box_minmax(cx_isl - 40.0, cx_isl - 8.0, wy - 0.35, wy + 0.35, 2.15, 5.4, mats["wall_white"])
            mb.add_box_minmax(cx_isl + 8.0, cx_isl + 40.0, wy - 0.35, wy + 0.35, 2.15, 5.4, mats["wall_white"])
            mb.add_box_minmax(cx_isl - 40.4, cx_isl - 7.6, wy - 0.6, wy + 0.6, 5.4, 5.8, mats["roof_slate"])
            mb.add_box_minmax(cx_isl + 7.6, cx_isl + 40.4, wy - 0.6, wy + 0.6, 5.4, 5.8, mats["roof_slate"])
            # Sculpted circular moon-gate archway at plaza center
            gate_pts = [
                (cx_isl + 3.4 * math.cos(a), wy, 4.4 + 3.0 * math.sin(a))
                for a in [math.pi * k / 10.0 for k in range(11)]
            ]
            mb.add_polyline_tubes(gate_pts, 0.42, mats["wall_white"], segments=6, smooth=True)
            mb.add_polyline_tubes([(p[0], p[1], p[2] + 0.45) for p in gate_pts], 0.22, mats["em_gold"], segments=4, smooth=True)

        # Timber lakeside viewing piers jutting out over Jinji Lake
        for sy in (-1.0, 1.0):
            y_p0 = 34.0 * sy
            y_p1 = 45.0 * sy
            mb.add_box_minmax(cx_isl - 20.0, cx_isl + 20.0, min(y_p0, y_p1), max(y_p0, y_p1), 1.1, 1.65, mats["wood_deck"])
            mb.add_tube((cx_isl - 20.0, y_p1, 1.55), (cx_isl + 20.0, y_p1, 1.55), 0.24, mats["em_gold"], segments=5)
            # Pier perimeter bollard lights
            for px in (cx_isl - 18.0, cx_isl - 9.0, cx_isl, cx_isl + 9.0, cx_isl + 18.0):
                mb.add_cylinder((px, y_p1 - 1.5 * sy, -0.6), 0.45, 0.45, 3.6, mats["metal_dark"], segments=6)
                mb.add_cylinder((px, y_p1 - 0.8 * sy, 2.2), 0.16, 0.14, 1.1, mats["metal_dark"], segments=5)
                mb.add_icosphere((px, y_p1 - 0.8 * sy, 2.85), 0.24, mats["em_warm"], subdivisions=1)

    # ------------------------------------------------------------------
    # 2. SIGNATURE NAVIGABLE MODERN ARCH BRIDGE (x = -58 .. +58m)
    # Clear navigable arch channel x = -15..+15m (width 30m >= 20m),
    # clear vertical height Z = 0..14.4m (>= 12m) above Jinji Lake water!
    # ------------------------------------------------------------------
    bridge_xs = [-58 + i * 2.0 for i in range(59)]
    deck_rings = []
    for x in bridge_xs:
        z_top = bridge_deck_z(x)
        thickness = 1.05 if abs(x) < 20.0 else 1.8
        z_bot = z_top - thickness
        hw = 7.2
        deck_rings.append([(x, -hw, z_bot), (x, hw, z_bot), (x, hw, z_top), (x, -hw, z_top)])
    mb.add_loft(deck_rings, mats["metal_white"], closed_loop=True, cap_start=True, cap_end=True, smooth=False)

    road_rings = []
    for x in bridge_xs:
        z_top = bridge_deck_z(x) + 0.08
        road_rings.append([(x, -5.8, z_top), (x, 5.8, z_top), (x, 5.8, z_top + 0.12), (x, -5.8, z_top + 0.12)])
    mb.add_loft(road_rings, mats["stone_granite"], closed_loop=True, cap_start=True, cap_end=True, smooth=False)

    # Double glowing handrails, balusters & curved bridge arch soffit ribs
    for sy in (-1.0, 1.0):
        rail_top = [(x, sy * 6.9, bridge_deck_z(x) + 1.15) for x in bridge_xs[::2]]
        rail_mid = [(x, sy * 6.9, bridge_deck_z(x) + 0.62) for x in bridge_xs[::2]]
        edge_pts = [(x, sy * 7.35, bridge_deck_z(x) - 0.15) for x in bridge_xs[::2]]
        mb.add_polyline_tubes(rail_top, 0.15, mats["metal_silver"], segments=5, smooth=True)
        mb.add_polyline_tubes(rail_mid, 0.09, mats["metal_silver"], segments=4, smooth=True)
        mb.add_polyline_tubes(edge_pts, 0.28, mats["em_gold"], segments=5, smooth=True)
        for x in bridge_xs[::3]:
            z0 = bridge_deck_z(x)
            mb.add_tube((x, sy * 6.9, z0), (x, sy * 6.9, z0 + 1.15), 0.10, mats["metal_silver"], segments=4)

    # Sculptural Twin Tilted Modern Steel Arch Ribs (with twin parallel chord tubes + diagrid bracing!)
    arch_xs = [-28.0 + i * 2.0 for i in range(29)]
    for sy in (-1.0, 1.0):
        rib_outer = []
        rib_inner = []
        glow_pts = []
        for x in arch_xs:
            u = x / 28.0
            z_arch = 8.5 + 15.2 * (1.0 - u * u)
            y_arch = sy * (8.2 - 1.6 * (1.0 - u * u))
            rib_outer.append((x, y_arch, z_arch + 0.65))
            rib_inner.append((x, y_arch, z_arch - 0.65))
            glow_pts.append((x, y_arch + sy * 0.72, z_arch + 0.15))
        mb.add_polyline_tubes(rib_outer, 0.56, mats["metal_white"], segments=8, smooth=True)
        mb.add_polyline_tubes(rib_inner, 0.42, mats["metal_silver"], segments=6, smooth=True)
        mb.add_polyline_tubes(glow_pts, 0.28, mats["em_cyan"], segments=5, smooth=True)
        # Truss web lacing between outer & inner arch chords
        for i in range(len(arch_xs) - 1):
            mb.add_tube(rib_inner[i], rib_outer[i + 1], 0.16, mats["metal_silver"], segments=4)
            mb.add_tube(rib_outer[i], rib_inner[i], 0.16, mats["metal_white"], segments=4)
        # Tension hanger cables down to bridge deck
        for x in range(-22, 24, 3):
            u = x / 28.0
            z_arch = 8.5 + 15.2 * (1.0 - u * u) - 0.6
            y_arch = sy * (8.2 - 1.6 * (1.0 - u * u))
            z_dk = bridge_deck_z(x)
            if z_arch > z_dk + 0.8:
                mb.add_tube((x, sy * 7.0, z_dk), (x, y_arch, z_arch), 0.13, mats["metal_silver"], segments=5)

    # Transverse overhead wind-bracing X-struts linking the twin arches near the crown
    crown_xs = [-12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0]
    for i, x in enumerate(crown_xs):
        u = x / 28.0
        z_a = 8.5 + 15.2 * (1.0 - u * u) + 0.2
        y_a = 8.2 - 1.6 * (1.0 - u * u)
        mb.add_tube((x, -y_a, z_a), (x, y_a, z_a), 0.34, mats["metal_white"], segments=6)
        if i < len(crown_xs) - 1:
            xn = crown_xs[i + 1]
            un = xn / 28.0
            zn = 8.5 + 15.2 * (1.0 - un * un) + 0.2
            yn = 8.2 - 1.6 * (1.0 - un * un)
            mb.add_tube((x, -y_a, z_a), (xn, yn, zn), 0.20, mats["em_gold"], segments=4)

    # Massive Sculpted Bridge Piers strictly OUTSIDE the 30m navigable channel (at x = ±19.5m and ±38m)
    for sx in (-1.0, 1.0):
        px = sx * 19.5
        z_p_top = bridge_deck_z(px) - 0.8
        mb.add_box_minmax(px - 2.2, px + 2.2, -8.6, 8.6, -2.5, z_p_top, mats["stone_granite"])
        for sy in (-1.0, 1.0):
            mb.add_tube((px - sx * 2.3, sy * 7.8, 0.5), (px - sx * 2.3, sy * 7.8, z_p_top - 0.5), 0.28, mats["em_gold"], segments=5)
            # Sculpted waterfront pier lantern post
            mb.add_cylinder((px + sx * 1.2, sy * 8.0, z_p_top + 1.8), 0.20, 0.16, 3.6, mats["metal_dark"], segments=6)
            mb.add_icosphere((px + sx * 1.2, sy * 8.0, z_p_top + 3.8), 0.55, mats["em_gold"], subdivisions=2)
        px2 = sx * 38.0
        z_p2_top = bridge_deck_z(px2) - 1.0
        mb.add_box_minmax(px2 - 1.6, px2 + 1.6, -7.2, 7.2, -2.5, z_p2_top, mats["stone_granite"])

    # ------------------------------------------------------------------
    # 3. NEO-SUZHOU MODERN WATERFRONT PAVILIONS (8 varied complexes)
    # ------------------------------------------------------------------
    pavilions = [
        (-134.0, 21.0, 26.0, 14.0, 7.5, 4.2, 0.0),
        (-92.0, 21.5, 24.0, 13.5, 9.4, 4.8, 0.06),
        (-112.0, -21.5, 34.0, 15.0, 8.4, 4.6, -0.04),
        (-74.0, -19.0, 16.0, 11.0, 6.4, 3.6, 0.08),
        (92.0, 21.5, 24.0, 14.0, 9.0, 4.6, -0.05),
        (134.0, 21.0, 26.0, 14.0, 7.4, 4.2, 0.04),
        (110.0, -21.5, 34.0, 15.0, 9.6, 5.0, 0.0),
        (74.0, -19.0, 16.0, 11.0, 6.6, 3.6, -0.06),
    ]
    for cx, cy, w, d, wh, rh, rz in pavilions:
        mb.add_pitched_roof_building(
            (cx, cy), w, d, z_base=2.1, wall_h=wh, roof_h=rh,
            wall_mat=mats["wall_white"],
            roof_mat=mats["roof_slate"],
            glass_mat=mats["glass_dark"],
            emissive_mat=mats["em_warm"],
            rot_z=rz,
            eave_overhang=1.7,
        )
        # Decorative golden roof ridge line & mid-level floating eave collar
        cos_r, sin_r = math.cos(rz), math.sin(rz)
        hx = 0.5 * w + 1.5
        p_r0 = (cx - hx * cos_r, cy - hx * sin_r, 2.1 + wh + rh + 0.12)
        p_r1 = (cx + hx * cos_r, cy + hx * sin_r, 2.1 + wh + rh + 0.12)
        mb.add_tube(p_r0, p_r1, 0.16, mats["em_gold"], segments=4)
        if w >= 24.0:
            mb.add_box((cx, cy, 2.1 + wh * 0.52), (w + 2.8, d + 2.4, 0.45), mats["roof_slate"], rot_euler=(0, 0, rz))

    # Two Iconic Waterfront Octagonal Viewing Gazebos at causeway ends (x = ±158m)
    for sx in (-1.0, 1.0):
        gx = sx * 158.0
        mb.add_cylinder((gx, 0.0, 2.3), 7.8, 7.2, 0.8, mats["stone_light"], segments=8, smooth=False)
        for k in range(8):
            a = k * (2.0 * math.pi / 8.0)
            mb.add_cylinder((gx + 5.6 * math.cos(a), 5.6 * math.sin(a), 5.3), 0.26, 0.22, 5.4, mats["metal_dark"], segments=6)
        mb.add_cylinder((gx, 0.0, 5.5), 2.4, 2.4, 4.2, mats["em_warm"], segments=10, smooth=True)
        mb.add_cylinder((gx, 0.0, 9.2), 8.6, 2.4, 2.8, mats["roof_slate"], segments=8, smooth=False)
        mb.add_cylinder((gx, 0.0, 11.4), 3.4, 0.3, 1.8, mats["roof_slate"], segments=8, smooth=False)
        mb.add_icosphere((gx, 0.0, 12.6), 0.45, mats["em_gold"], subdivisions=2)
        ring_pts = [(gx + 7.4 * math.cos(k * math.pi / 4.0), 7.4 * math.sin(k * math.pi / 4.0), 7.8) for k in range(8)]
        mb.add_polyline_tubes(ring_pts, 0.20, mats["em_gold"], segments=5, closed=True)

    # ------------------------------------------------------------------
    # 4. PROMENADE LANTERN POLES & LAKESIDE WILLOWS
    # ------------------------------------------------------------------
    for x in range(-152, 156, 16):
        if abs(x) < 56:
            continue
        for sy in (-1.0, 1.0):
            ly = sy * 10.6
            mb.add_cylinder((x, ly, 4.6), 0.14, 0.10, 5.0, mats["metal_dark"], segments=6)
            mb.add_icosphere((x, ly, 7.3), 0.44, mats["em_gold"], subdivisions=2)

    tree_spots = [
        (-148, 12), (-148, -12), (-70, 16), (-70, -16), (-136, -24), (-86, -26),
        (-146, 28), (-146, -28), (70, 16), (70, -16), (148, 12), (148, -12),
        (86, -26), (136, -24), (146, 28), (146, -28),
    ]
    for tx, ty in tree_spots:
        mb.add_cylinder((tx, ty, 4.2), 0.36, 0.20, 4.4, mats["trunk_bark"], segments=6)
        mb.add_icosphere((tx, ty, 7.2), 2.9, mats["foliage_light"], subdivisions=2, scale=(1.1, 1.1, 0.85))
        mb.add_icosphere((tx + 1.1, ty - 0.8, 6.4), 2.1, mats["foliage_green"], subdivisions=2)

    mb.build(origin=(0.0, 0.0, 0.0))
    export_glb(OUT_PATH)
    verify_glb(OUT_PATH)


if __name__ == "__main__":
    build_ligongdi()
