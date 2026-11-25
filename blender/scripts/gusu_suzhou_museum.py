"""
Generate suzhou_museum.glb — Station 07 NE (museumAnchor: x=265, y=1.6, z=-220):
  I.M. Pei's Suzhou Museum (苏州博物馆) — world-famous modernist Jiangnan masterpiece!
  Spatial alignment: local X in [-19, +68] (world X in [246, 333]), Y in [-46, +46]
  so its West white perimeter wall at X=-18.5 sits right beside Humble Administrator's
  Garden East wall (world X=244) with ZERO overlap or Z-fighting!

  Unmistakable I.M. Pei Architectural Language:
  - Pure crisp matte white geometric pitched-wall volumes (Pei_WhiteWall)
  - Razor-sharp dark charcoal-grey granite roof/gable trim (Pei_DarkGranite)
  - Diamond & triangular glass roof skylights glowing warm from within (Emissive_Warm)
  - Iconic central octagonal atrium pyramid skylight & cantilevered entrance portico
  - Central geometric reflecting water court with stepped geometric stone bridge & modern tea pavilion
  - Iconic SLICED-STONE ROCKERY (片石假山 — "以壁为纸，以石为绘") backed by a pure white canvas wall!
"""
import math
import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gusu_common import clear_scene, create_gusu_palette, SceneBuilder, export_glb


def add_pei_pitched_volume(sb, w, d, wall_h, gable_h, center=(0, 0, 0), rot_z=0.0,
                           skylight=True, trim_thick=0.38, gable_axis="X"):
    """
    I.M. Pei's signature crisp white geometric volume with triangular pitched gable roof,
    razor-sharp dark charcoal granite trim, and glowing diamond/triangular glass roof skylight!
    gable_axis='X' means ridge runs along X (triangular gables face -X and +X).
    """
    cx, cy, cz = center
    if gable_axis == "Y":
        w, d = d, w
        rot_z += math.pi * 0.5

    # Crisp pure white rectangular base volume
    sb.add_box("pei_white", w, d, wall_h, center=(cx, cy, cz + wall_h * 0.5), rot_z=rot_z)

    # Dark charcoal granite horizontal plinth & cornice trim bands
    sb.add_box("pei_granite", w + 0.16, d + 0.16, 0.36, center=(cx, cy, cz + 0.18), rot_z=rot_z)
    sb.add_box("pei_granite", w + 0.24, d + 0.24, trim_thick,
               center=(cx, cy, cz + wall_h), rot_z=rot_z)

    # Triangular white gable prism running along local X
    hw = w * 0.5
    hd = d * 0.5
    z_eave = wall_h
    z_ridge = wall_h + gable_h

    # Build exact 3D triangular gable body via loft along X
    rings = [
        [(-hw, -hd, z_eave), (-hw, hd, z_eave), (-hw, 0.0, z_ridge)],
        [(hw, -hd, z_eave), (hw, hd, z_eave), (hw, 0.0, z_ridge)],
    ]
    sb.add_loft("pei_white", rings, closed_caps=True, center=(cx, cy, cz), rot_z=rot_z)

    # Dark charcoal granite roof cladding slabs (slightly overhanging with crisp geometric bevel)
    slope_len = math.hypot(hd + 0.35, gable_h + 0.20)
    slope_ang = math.atan2(gable_h, hd)
    for side in (-1.0, 1.0):
        ly = side * (hd * 0.5 + 0.08)
        lx = 0.0
        wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
        wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
        sb.add_box(
            "pei_granite", w + 0.55, slope_len, 0.28,
            center=(wx, wy, cz + z_eave + gable_h * 0.5 + 0.12),
            rot_euler=(-side * slope_ang, 0.0, rot_z),
        )

    # Razor-sharp granite ridge beam & end-gable triangular edge trims
    sb.add_box("pei_granite", w + 0.65, 0.42, 0.34,
               center=(cx, cy, cz + z_ridge + 0.16), rot_z=rot_z)
    for xs in (-1.0, 1.0):
        for side in (-1.0, 1.0):
            lx = xs * (hw + 0.12)
            ly = side * (hd * 0.5)
            wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
            wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
            sb.add_box(
                "pei_granite", 0.34, slope_len + 0.15, 0.36,
                center=(wx, wy, cz + z_eave + gable_h * 0.5 + 0.14),
                rot_euler=(-side * slope_ang, 0.0, rot_z),
            )

    # Signature I.M. Pei DIAMOND & TRIANGULAR GLASS ROOF SKYLIGHTS glowing warm from within!
    if skylight and w >= 7.0:
        n_sky = max(1, int(w / 7.5))
        for si in range(n_sky):
            u = 0.0 if n_sky == 1 else (-0.56 + 1.12 * si / (n_sky - 1))
            lx = u * hw
            # Warm glowing skylight core + dark granite diamond frame on both slopes
            for side in (-1.0, 1.0):
                ly = side * (hd * 0.48)
                wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                sz_w = min(4.2, w / (n_sky * 1.35))
                sz_s = slope_len * 0.58
                # Glowing interior glass skylight panel + Pei's architectural timber louver lattice
                sb.add_box(
                    "emissive_win", sz_w, sz_s, 0.16,
                    center=(wx, wy, cz + z_eave + gable_h * 0.52 + 0.20),
                    rot_euler=(-side * slope_ang, 0.0, rot_z),
                )
                # Subtle translucent architectural glass plane over warm skylight
                sb.add_box(
                    "pei_glass", sz_w * 0.96, sz_s * 0.96, 0.06,
                    center=(wx, wy, cz + z_eave + gable_h * 0.52 + 0.31),
                    rot_euler=(-side * slope_ang, 0.0, rot_z),
                )
                # Pei's signature warm timber louver slats (木格栅遮阳天窗)
                for l_i in range(5):
                    l_off = -0.38 + 0.76 * l_i / 4.0
                    bx_l = lx + l_off * sz_w
                    bwx = cx + bx_l * math.cos(rot_z) - ly * math.sin(rot_z)
                    bwy = cy + bx_l * math.sin(rot_z) + ly * math.cos(rot_z)
                    sb.add_box(
                        "pei_wood", 0.08, sz_s * 0.94, 0.14,
                        center=(bwx, bwy, cz + z_eave + gable_h * 0.52 + 0.26),
                        rot_euler=(-side * slope_ang, 0.0, rot_z),
                    )
                # Crisp dark granite diamond & diagonal framing bars across the skylight
                for bar_off in (-0.48, 0.0, 0.48):
                    bx_l = lx + bar_off * sz_w
                    bwx = cx + bx_l * math.cos(rot_z) - ly * math.sin(rot_z)
                    bwy = cy + bx_l * math.sin(rot_z) + ly * math.cos(rot_z)
                    sb.add_box(
                        "pei_granite", 0.18, sz_s + 0.24, 0.26,
                        center=(bwx, bwy, cz + z_eave + gable_h * 0.52 + 0.30),
                        rot_euler=(-side * slope_ang, 0.0, rot_z),
                    )
                # Horizontal & diamond-cross granite mullions
                for h_off in (-0.35, 0.0, 0.35):
                    ly_h = ly + side * h_off * (hd * 0.45)
                    hz_h = cz + z_eave + gable_h * (0.52 - h_off * 0.30) + 0.30
                    hwx = cx + lx * math.cos(rot_z) - ly_h * math.sin(rot_z)
                    hwy = cy + lx * math.sin(rot_z) + ly_h * math.cos(rot_z)
                    sb.add_box(
                        "pei_granite", sz_w + 0.28, 0.16, 0.24,
                        center=(hwx, hwy, hz_h),
                        rot_euler=(-side * slope_ang, 0.0, rot_z),
                    )


def add_pei_octagonal_atrium(sb, center=(22.0, -20.0, 0.0), radius=10.5, wall_h=8.2, pyr_h=5.2):
    """I.M. Pei's iconic Suzhou Museum Central Octagonal Atrium with diamond glass pyramid roof!"""
    cx, cy, cz = center
    # Crisp white octagonal atrium drum
    sb.add_cylinder("pei_white", radius, radius, wall_h, segments=8,
                    center=(cx, cy, cz + wall_h * 0.5), rot_z=math.pi / 8)
    # Dark granite cornice ring & corner vertical framing ribs
    sb.add_cylinder("pei_granite", radius + 0.25, radius + 0.25, 0.42, segments=8,
                    center=(cx, cy, cz + wall_h), rot_z=math.pi / 8)
    for k in range(8):
        ang = (2.0 * math.pi * k / 8) + math.pi / 8
        rx = cx + radius * 0.99 * math.cos(ang)
        ry = cy + radius * 0.99 * math.sin(ang)
        sb.add_box("pei_granite", 0.38, 0.38, wall_h, center=(rx, ry, cz + wall_h * 0.5), rot_z=ang)

    # Tall glowing architectural glass entrance & water-court portals (South & North faces)
    for side in (-1.0, 1.0):
        sb.add_box("pei_granite", 9.6, 0.45, 6.2, center=(cx, cy + side * (radius * 0.92), cz + 3.2))
        sb.add_box("emissive_win", 8.4, 0.32, 5.4, center=(cx, cy + side * (radius * 0.94), cz + 3.1))
        # Dark vertical mullions
        for mx in (-2.8, 0.0, 2.8):
            sb.add_box("pei_granite", 0.20, 0.42, 5.5,
                       center=(cx + mx, cy + side * (radius * 0.95), cz + 3.1))

    # Glowing faceted octagonal glass pyramid skylight crown!
    sb.add_cylinder("emissive_warm", radius * 0.88, 0.35, pyr_h, segments=8,
                    center=(cx, cy, cz + wall_h + pyr_h * 0.5), rot_z=math.pi / 8)
    # Dark charcoal granite structural pyramid ribs & horizontal diamond rings
    diag = math.hypot(radius * 0.94, pyr_h)
    pitch = math.atan2(pyr_h, radius * 0.94)
    for k in range(8):
        ang = (2.0 * math.pi * k / 8) + math.pi / 8
        mx = cx + radius * 0.47 * math.cos(ang)
        my = cy + radius * 0.47 * math.sin(ang)
        sb.add_box("pei_granite", diag, 0.28, 0.30,
                   center=(mx, my, cz + wall_h + pyr_h * 0.5 + 0.08),
                   rot_euler=(0.0, pitch, ang))
    # Horizontal octagonal skylight rings
    for s in (0.35, 0.68):
        rr = radius * (1.0 - s * 0.92)
        sb.add_cylinder("pei_granite", rr + 0.14, rr + 0.10, 0.24, segments=8,
                        center=(cx, cy, cz + wall_h + pyr_h * s + 0.08),
                        rot_z=math.pi / 8, cap_ends=False)
    # Crisp geometric apex cap
    sb.add_cylinder("pei_granite", 0.95, 0.25, 0.55, segments=8,
                    center=(cx, cy, cz + wall_h + pyr_h + 0.22), rot_z=math.pi / 8)


def build_sliced_stone_rockery(sb):
    """
    THE ICONIC SLICED-STONE ROCKERY (片石假山 — "以壁为纸，以石为绘")!
    Backed by a monumental pure white plaster canvas wall with crisp dark granite coping,
    and composed of dramatic layered vertical dark-slate stone silhouettes rising from the
    reflecting water court like a Song-dynasty ink-wash mountain scroll!
    """
    # Monumental Pure White Canvas Backdrop Wall along the North edge of the reflecting pool
    wall_y = 33.5
    sb.add_box("pei_white", 48.0, 0.95, 7.6, center=(22.0, wall_y, 3.8))
    # Razor-sharp dark granite top cap & vertical geometric wing returns
    sb.add_box("pei_granite", 48.6, 1.32, 0.32, center=(22.0, wall_y, 7.72))
    sb.add_box("pei_white", 0.90, 8.5, 6.2, center=(-1.8, wall_y - 4.0, 3.1))
    sb.add_box("pei_granite", 1.25, 8.8, 0.30, center=(-1.8, wall_y - 4.0, 6.32))
    sb.add_box("pei_white", 0.90, 8.5, 6.2, center=(45.8, wall_y - 4.0, 3.1))
    sb.add_box("pei_granite", 1.25, 8.8, 0.30, center=(45.8, wall_y - 4.0, 6.32))

    # Concealed warm linear grazing uplight strip washing the pure white wall behind the rocks!
    sb.add_box("emissive_warm", 36.0, 0.22, 0.18, center=(22.0, wall_y - 0.85, 0.15))

    # Layered Sliced-Stone Mountain Peaks (片石假山): dramatic flat-sliced angled dark slate slabs!
    # Arranged in three poetic ink-wash mountain clusters (Left minor peak, Center main peak, Right ridge)
    slabs = [
        # (cx, cy, width, thickness, height, top_tilt_deg, yaw)
        # Left cluster
        (6.5,  30.6, 4.2, 0.85, 3.6,  12,  0.04),
        (9.5,  31.2, 5.0, 0.95, 4.9,  -8, -0.05),
        (12.2, 30.2, 3.6, 0.80, 3.1,  15,  0.06),
        # Center monumental ink-wash peak
        (17.5, 31.4, 5.4, 1.05, 5.6,  10, -0.03),
        (21.5, 30.8, 6.2, 1.15, 6.7,  -6,  0.02),  # Tallest main sliced peak!
        (25.2, 31.3, 5.0, 1.00, 5.3, -14, -0.04),
        (28.0, 30.3, 3.8, 0.85, 3.8,  11,  0.05),
        # Right distant misty ridge
        (33.0, 31.1, 5.2, 0.95, 4.7,  -9, -0.04),
        (36.8, 30.5, 4.4, 0.85, 3.5,  14,  0.03),
        (39.8, 31.2, 3.5, 0.80, 2.5, -10,  0.00),
    ]
    for sx, sy, sw, st, sh, tilt, yaw in slabs:
        # Build sharp faceted mountain slab polygon (beveled peak top like Pei's sliced Taishan stone)
        tilt_dx = math.tan(math.radians(tilt)) * (sh * 0.25)
        pts_2d = [
            (-sw * 0.5, -st * 0.5),
            (sw * 0.5, -st * 0.5),
            (sw * 0.5, st * 0.5),
            (-sw * 0.5, st * 0.5),
        ]
        # Stepped mountain-ridge profile loft from water base Z=-0.4 to sharp angular peak!
        rings = [
            [(-sw * 0.52, -st * 0.55, -0.4), (sw * 0.52, -st * 0.55, -0.4),
             (sw * 0.52, st * 0.55, -0.4), (-sw * 0.52, st * 0.55, -0.4)],
            [(-sw * 0.48, -st * 0.48, sh * 0.58), (sw * 0.46, -st * 0.48, sh * 0.58),
             (sw * 0.46, st * 0.48, sh * 0.58), (-sw * 0.48, st * 0.48, sh * 0.58)],
            [(-sw * 0.22 + tilt_dx, -st * 0.36, sh), (sw * 0.20 + tilt_dx, -st * 0.36, sh * 0.86),
             (sw * 0.20 + tilt_dx, st * 0.36, sh * 0.86), (-sw * 0.22 + tilt_dx, st * 0.36, sh)],
        ]
        sb.add_loft("pei_stone", rings, closed_caps=True, center=(sx, sy, 0.0), rot_z=yaw)

    # Low stone pebble terrace & shallow wading ledge in front of sliced rockery
    sb.add_box("stone_light", 42.0, 4.6, 0.45, center=(22.0, 30.8, -0.35))


def build_suzhou_museum(sb):
    """
    Complete I.M. Pei Suzhou Museum campus:
      local X in [-18.5, +66.5], Y in [-45, +45]
      Central reflecting water court around (22, +8)
    """
    # Perimeter stone plaza slabs framing the Central Reflecting Water Court
    # Reflecting Pool occupies X in [0, +44], Y in [-8, +29]
    sb.add_box("courtyard", 19.0, 90.0, 2.5, center=(-9.0, 0.0, -1.25))     # West (-18.5..0.5)
    sb.add_box("courtyard", 23.0, 90.0, 2.5, center=(55.0, 0.0, -1.25))     # East (+43.5..+66.5)
    sb.add_box("courtyard", 44.0, 37.0, 2.5, center=(22.0, -26.5, -1.25))   # South (-45..-8)
    sb.add_box("courtyard", 44.0, 16.0, 2.5, center=(22.0, 37.0, -1.25))    # North (+29..+45)

    # Central Reflecting Water Court (recessed sleek dark-granite basin + mirror water)
    sb.add_box("pei_granite", 46.0, 39.0, 1.0, center=(22.0, 10.5, -1.95))
    sb.add_box("water", 44.2, 37.2, 0.12, center=(22.0, 10.5, -0.30))
    # Crisp dark-granite linear pool coping borders
    sb.add_box("pei_granite", 45.2, 0.65, 0.42, center=(22.0, -8.1, -0.05))
    sb.add_box("pei_granite", 0.65, 37.8, 0.42, center=(-0.1, 10.5, -0.05))
    sb.add_box("pei_granite", 0.65, 37.8, 0.42, center=(44.1, 10.5, -0.05))

    # Crisp White Outer Museum Perimeter Walls with Razor-Sharp Dark Granite Caps (NO curved tiles!)
    w_pts = [(-18.5, -44.5), (66.0, -44.5), (66.0, 44.5), (-18.5, 44.5)]
    for i in range(4):
        if i == 0:
            # South entrance plaza opening
            sb.add_garden_wall((-18.5, -44.5), (6.0, -44.5), height=3.8,
                               wall_mat="pei_white", cap_mat="pei_granite", wave_cap=False)
            sb.add_garden_wall((38.0, -44.5), (66.0, -44.5), height=3.8,
                               wall_mat="pei_white", cap_mat="pei_granite", wave_cap=False)
        else:
            sb.add_garden_wall(w_pts[i], w_pts[(i + 1) % 4], height=3.8,
                               wall_mat="pei_white", cap_mat="pei_granite", wave_cap=False)

    # 1. CENTRAL OCTAGONAL ENTRANCE ATRIUM & DIAMOND GLASS PYRAMID SKYLIGHT
    add_pei_octagonal_atrium(sb, center=(22.0, -21.0, 0.0), radius=10.2, wall_h=8.0, pyr_h=5.2)

    # Monumental South Cantilevered Entrance Gate Portico (大门几何门楼)
    sb.add_box("pei_white", 18.0, 3.6, 5.8, center=(22.0, -37.0, 2.9))
    sb.add_box("pei_granite", 19.2, 4.4, 0.48, center=(22.0, -37.0, 6.0))
    # Wide dark-granite framed central entrance portal glowing warm inside
    sb.add_box("pei_granite", 8.8, 3.8, 4.5, center=(22.0, -37.0, 2.25))
    sb.add_box("emissive_win", 7.6, 3.9, 3.8, center=(22.0, -37.0, 2.1))
    # Flanked by sleek white entrance flanking wings
    add_pei_pitched_volume(sb, w=12.0, d=8.2, wall_h=5.4, gable_h=3.2,
                           center=(5.0, -32.0, 0.0), skylight=True)
    add_pei_pitched_volume(sb, w=12.0, d=8.2, wall_h=5.4, gable_h=3.2,
                           center=(39.0, -32.0, 0.0), skylight=True)

    # 2. WEST EXHIBITION PAVILIONS (interlocking Pei pitched geometric volumes with diamond skylights!)
    add_pei_pitched_volume(sb, w=14.5, d=11.0, wall_h=6.4, gable_h=3.8,
                           center=(-9.0, -18.0, 0.0), gable_axis="Y", skylight=True)
    add_pei_pitched_volume(sb, w=15.0, d=11.5, wall_h=6.8, gable_h=4.0,
                           center=(-9.0, 2.0, 0.0), gable_axis="Y", skylight=True)
    add_pei_pitched_volume(sb, w=14.0, d=10.5, wall_h=6.0, gable_h=3.6,
                           center=(-9.0, 22.0, 0.0), gable_axis="Y", skylight=True)
    # West glass-and-granite gallery links facing the reflecting pool
    for gy in (-8.0, 12.0):
        sb.add_box("pei_white", 7.5, 7.2, 5.2, center=(-6.5, gy, 2.6))
        sb.add_box("pei_granite", 7.9, 7.6, 0.36, center=(-6.5, gy, 5.35))
        sb.add_box("emissive_win", 0.28, 5.6, 3.6, center=(-2.6, gy, 2.4))

    # 3. EAST EXHIBITION WINGS & ZHONG WANG FU TRANSITION VOLUMES
    add_pei_pitched_volume(sb, w=15.0, d=11.5, wall_h=6.6, gable_h=3.9,
                           center=(54.5, -16.0, 0.0), gable_axis="Y", skylight=True)
    add_pei_pitched_volume(sb, w=16.0, d=12.0, wall_h=7.0, gable_h=4.2,
                           center=(54.5, 5.0, 0.0), gable_axis="Y", skylight=True)
    add_pei_pitched_volume(sb, w=14.5, d=10.8, wall_h=6.2, gable_h=3.6,
                           center=(54.5, 25.0, 0.0), gable_axis="Y", skylight=True)
    # Glowing geometric gallery windows facing the central reflecting water court
    for gy in (-16.0, 5.0, 25.0):
        sb.add_box("pei_granite", 0.38, 8.0, 4.4, center=(48.4, gy, 2.5))
        sb.add_box("emissive_win", 0.24, 7.0, 3.6, center=(48.25, gy, 2.5))

    # 4. STEPPED GEOMETRIC STONE BRIDGE (几何折桥) across the Central Reflecting Court!
    # Clean flat architectural granite decks with razor-crisp geometric zigzag steps!
    bridge_segs = [
        ((22.0, -8.5), (22.0, 1.5)),
        ((22.0,  1.5), (14.5, 1.5)),
        ((14.5,  1.5), (14.5, 11.5)),
        ((14.5, 11.5), (27.5, 11.5)),
        ((27.5, 11.5), (27.5, 19.5)),
        ((27.5, 19.5), (36.5, 19.5)),
    ]
    for p0, p1 in bridge_segs:
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        mx, my = (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5
        # Sleek pale stone slab + dark granite shadow edge
        sb.add_box("stone_light", length + 2.4, 2.6, 0.24, center=(mx, my, 0.14), rot_z=ang)
        sb.add_box("pei_granite", length + 2.5, 2.7, 0.14, center=(mx, my, -0.02), rot_z=ang)
        # Subtle warm under-bridge LED glow reflecting onto the water court!
        sb.add_box("emissive_warm", length * 0.78, 0.14, 0.10, center=(mx, my, -0.10), rot_z=ang)

    # 5. MODERNIST OCTAGONAL WATER PAVILION (苏博现代八角亭) cantilevered over East water court!
    px, py = 37.5, 11.0
    sb.add_cylinder("pei_white", 4.8, 4.8, 0.65, segments=8, center=(px, py, 0.05), rot_z=math.pi / 8)
    sb.add_cylinder("pei_granite", 5.0, 5.0, 0.16, segments=8, center=(px, py, 0.42), rot_z=math.pi / 8)
    # 8 slender dark-granite minimalist columns + geometric flat-faceted pyramid glass roof
    for k in range(8):
        ang = (2.0 * math.pi * k / 8) + math.pi / 8
        cx_c = px + 4.0 * math.cos(ang)
        cy_c = py + 4.0 * math.sin(ang)
        sb.add_box("pei_granite", 0.22, 0.22, 3.8, center=(cx_c, cy_c, 2.35), rot_z=ang)
    sb.add_cylinder("pei_granite", 4.7, 4.7, 0.26, segments=8, center=(px, py, 4.30), rot_z=math.pi / 8)
    sb.add_cylinder("emissive_warm", 4.2, 0.22, 2.2, segments=8, center=(px, py, 5.5), rot_z=math.pi / 8)
    # Dark granite pyramidal frame ribs on modern pavilion
    diag_p = math.hypot(4.5, 2.2)
    pitch_p = math.atan2(2.2, 4.5)
    for k in range(8):
        ang = (2.0 * math.pi * k / 8) + math.pi / 8
        sb.add_box("pei_granite", diag_p, 0.18, 0.20,
                   center=(px + 2.25 * math.cos(ang), py + 2.25 * math.sin(ang), 5.55),
                   rot_euler=(0.0, pitch_p, ang))

    # 6. THE ICONIC SLICED-STONE ROCKERY (片石假山) backed by Pure White Canvas Wall!
    build_sliced_stone_rockery(sb)

    # 7. Crisp Architectural Bamboo Groves & Minimalist Courtyard Pines in Granite Planters
    for bx, by, sd in [
        (3.5, 23.0, 261),
        (41.0, 24.5, 262),
        (4.0, -4.5, 263),
        (40.5, -4.5, 264),
        (-13.5, -36.0, 265),
        (56.0, -36.0, 266),
    ]:
        sb.add_box("pei_granite", 4.6, 4.6, 0.45, center=(bx, by, 0.22))
        sb.add_bamboo_clump(center=(bx, by, 0.40), count=8, height=7.2, spread=1.6, seed=sd)

    # Iconic architectural courtyard pines (sculptural accents in Pei's courtyard)
    sb.add_pine_tree(center=(8.0, 12.0, 0.0), height=7.8, seed=267)
    sb.add_pine_tree(center=(35.0, -36.5, 0.0), height=8.5, seed=268)
    sb.add_pine_tree(center=(9.0, -36.5, 0.0), height=8.5, seed=269)

    # Pei's Signature Geometric Octagonal Framed "Moon Windows" (现代八角漏窗) & Stepped Waterfall Ledges (叠水)
    for my in (-12.0, 4.0, 20.0):
        # Octagonal granite window frames punched into the West courtyard garden wall
        sb.add_cylinder("pei_granite", 1.55, 1.55, 0.55, segments=8,
                        center=(-18.2, my, 2.2), rot_euler=(0.0, math.pi * 0.5, 0.0))
        sb.add_cylinder("emissive_warm", 1.15, 1.15, 0.35, segments=8,
                        center=(-18.2, my, 2.2), rot_euler=(0.0, math.pi * 0.5, 0.0))
    # Stepped granite water cascade ledges (叠水) along the west & south reflecting pool edge
    for step_i in range(4):
        sb.add_box("pei_granite", 14.0 - step_i * 1.4, 1.1, 0.20,
                   center=(10.5, -5.8 + step_i * 1.1, 0.20 - step_i * 0.14))
        sb.add_box("stone_light", 13.6 - step_i * 1.4, 0.9, 0.12,
                   center=(10.5, -5.8 + step_i * 1.1, 0.28 - step_i * 0.14))
    # Modernist minimalist courtyard stone benches & glowing low granite bollards
    for bx, by in [(16.0, -33.0), (28.0, -33.0), (16.0, -40.5), (28.0, -40.5),
                   (2.0, -10.5), (42.0, -10.5), (2.0, 27.0), (42.0, 27.0)]:
        sb.add_box("pei_granite", 0.36, 0.36, 0.85, center=(bx, by, 0.42))
        sb.add_box("emissive_warm", 0.30, 0.30, 0.20, center=(bx, by, 0.72))
    # Additional sculptural faceted Sliced-Stone mid-ground boulders for richer Mi Fu ink-wash depth!
    rng_rock = random.Random(280)
    for rx, ry, r_sz in [(13.5, 28.0, 1.4), (19.0, 27.8, 1.8), (24.5, 28.2, 1.7),
                         (30.5, 27.6, 1.5), (35.5, 28.0, 1.3), (8.0, 28.2, 1.2)]:
        sb.add_ico("pei_stone", radius=r_sz, subdivisions=2, scale=(1.4, 0.65, 1.15),
                   center=(rx, ry, r_sz * 0.55), jitter=0.28, rng=rng_rock)


def main():
    clear_scene()
    palette = create_gusu_palette()
    sb = SceneBuilder(palette)
    build_suzhou_museum(sb)
    objs = sb.build_objects_by_material(prefix="SuzhouMuseum")
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    print(f"[STATS] suzhou_museum: {len(objs)} meshes, {total_tris} tris")
    export_glb("suzhou_museum.glb")


if __name__ == "__main__":
    main()
