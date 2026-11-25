"""Generate Suzhou MoCA (by BIG, west X≈-45) & 128m Eye of Suzhou Ferris Wheel (east X≈+45).
CRITICAL: Separate named child node `FerrisWheelRotor` with origin strictly at (45, 0, 68) in Blender Z-up
= (45, 68, 0) in Three.js Y-up, rotating cleanly around the X-axis!
"""
import math
import os
import sys
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modern_common import (
    clear_scene,
    make_standard_modern_mats,
    make_mat,
    MeshBuilder,
    export_glb,
    verify_glb,
)

OUT_PATH = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/moca_eye_of_suzhou.glb"

HUB_BLENDER = (45.0, 0.0, 68.0)  # -> Three.js Y-up: (45.0, 68.0, 0.0), rotates around X axis
WHEEL_OUTER_R = 58.0
WHEEL_INNER_R = 53.0
NUM_CAPSULES = 28


def build_moca_and_eye():
    clear_scene()
    mats = make_standard_modern_mats()
    moca_ribbon_mat = make_mat("Metal_MoCARibbon", "#d9d2c5", metallic=0.86, roughness=0.22)
    capsule_glass = make_mat("Glass_CapsuleShell", "#2a5578", metallic=0.72, roughness=0.10)
    all_mats = list(mats.values()) + [moca_ribbon_mat, capsule_glass]

    # Root empty at (0, 0, 0) so `FerrisWheelRotor` is an explicit named child node
    root = bpy.data.objects.new("MoCA_EyeOfSuzhou", None)
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # ==================================================================
    # PART A: STATIC COMPLEX (Suzhou MoCA + Plaza + Ferris Wheel A-Frame)
    # ==================================================================
    mb = MeshBuilder("MoCA_Eye_Static", all_mats)

    # ------------------------------------------------------------------
    # 1. LAKESIDE PLAZA DECK & PROMENADE (z = -2.5m .. 0.0m)
    # ------------------------------------------------------------------
    mb.add_box_minmax(-105.0, 102.0, -96.0, 96.0, -2.5, 0.0, mats["stone_granite"])
    mb.add_box_minmax(-102.0, 98.0, -92.0, 92.0, 0.0, 0.22, mats["stone_light"])
    # Reflecting courtyard water pools around MoCA pavilions
    mb.add_box_minmax(-76.0, -18.0, -32.0, 32.0, 0.22, 0.34, mats["water_pool"])
    # West waterfront boardwalk facing Jinji Lake (-X)
    mb.add_box_minmax(-112.0, -102.0, -94.0, 94.0, -1.8, 0.15, mats["wood_deck"])
    mb.add_tube((-112.0, -93.0, 0.25), (-112.0, 93.0, 0.25), 0.32, mats["em_warm"], segments=4)
    # Glowing walkway connecting MoCA (-45) to Eye of Suzhou (+45)
    for sy in (-12.0, 12.0):
        mb.add_tube((-14.0, sy, 0.30), (36.0, sy, 0.30), 0.26, mats["em_cyan"], segments=4)

    # ------------------------------------------------------------------
    # 2. SUZHOU MoCA (苏州当代美术馆 by BIG, around X = -45, heights 14-18m)
    # Cluster of sleek low-rise pavilions united by flowing metallic ribbon roofs!
    # ------------------------------------------------------------------
    pavilions = [
        # (cx, cy, wx, dy, wall_h, rot_z)
        (-74.0, -44.0, 24.0, 18.0, 11.0, 0.14),
        (-44.0, -52.0, 26.0, 18.0, 12.5, -0.08),
        (-18.0, -36.0, 22.0, 17.0, 11.5, 0.18),
        (-78.0, 0.0, 24.0, 22.0, 13.0, 0.02),
        (-45.0, 0.0, 28.0, 22.0, 14.5, 0.0),
        (-16.0, 6.0, 22.0, 18.0, 12.0, -0.12),
        (-72.0, 44.0, 24.0, 18.0, 11.5, -0.15),
        (-42.0, 50.0, 26.0, 18.0, 13.0, 0.10),
    ]

    for cx, cy, wx, dy, wh, rz in pavilions:
        # Warm glowing gallery glass pavilion core
        mb.add_box((cx, cy, 0.2 + 0.5 * wh), (wx - 1.4, dy - 1.4, wh), mats["em_warm"], rot_euler=(0, 0, rz))
        # Outer dark glass curtain-wall framing columns & horizontal mullions
        cos_r, sin_r = math.cos(rz), math.sin(rz)

        def to_w(lx, ly, lz):
            return (cx + lx * cos_r - ly * sin_r, cy + lx * sin_r + ly * cos_r, lz)

        hx, hy = 0.5 * wx, 0.5 * dy
        # Corner & mid perimeter vertical architectural mullions
        for fx in (-1.0, -0.5, 0.0, 0.5, 1.0):
            for sy in (-1.0, 1.0):
                p0 = to_w(fx * hx, sy * hy, 0.2)
                p1 = to_w(fx * hx, sy * hy, wh + 0.4)
                mb.add_tube(p0, p1, 0.28, mats["metal_dark"], segments=4)
        for fy in (-0.5, 0.0, 0.5):
            for sx in (-1.0, 1.0):
                p0 = to_w(sx * hx, fy * hy, 0.2)
                p1 = to_w(sx * hx, fy * hy, wh + 0.4)
                mb.add_tube(p0, p1, 0.28, mats["metal_dark"], segments=4)

        # Signature BIG upturned sculpted swooping pavilion roof cap
        nx, ny = 8, 6
        top_grid = []
        bot_grid = []
        for ix in range(nx + 1):
            u = -1.0 + 2.0 * (ix / nx)
            r_top, r_bot = [], []
            for iy in range(ny + 1):
                v = -1.0 + 2.0 * (iy / ny)
                # Upturned Jiangnan-inspired modern saddle/ribbon curve (peaking ~16.5-18.5m at corners!)
                curl = 3.2 * (u * u * 0.7 + v * v * 0.6) - 1.2 * (1.0 - u * u) * (1.0 - v * v)
                z_r = wh + 0.6 + curl
                lx = u * (hx + 3.2)
                ly = v * (hy + 2.8)
                r_top.append(to_w(lx, ly, z_r + 0.35))
                r_bot.append(to_w(lx, ly, z_r - 0.35))
            top_grid.append(r_top)
            bot_grid.append(r_bot)
        mb.add_loft(top_grid, moca_ribbon_mat, closed_loop=False, smooth=True)
        mb.add_loft([list(reversed(r)) for r in bot_grid], mats["metal_silver"], closed_loop=False, smooth=True)
        # Perimeter glowing eave strip tracing the curved ribbon roof
        eave_loop = (
            [top_grid[ix][0] for ix in range(nx + 1)]
            + [top_grid[nx][iy] for iy in range(1, ny + 1)]
            + [top_grid[ix][ny] for ix in range(nx - 1, -1, -1)]
            + [top_grid[0][iy] for iy in range(ny - 1, -1, -1)]
        )
        mb.add_polyline_tubes(eave_loop, 0.22, mats["em_gold"], segments=4, smooth=True)

    # Signature BIG Continuous Flowing Metallic Ribbon Bridges connecting the pavilions!
    ribbon_paths = [
        # Sweeping North-South ribbon waves linking the cluster
        [(-84, -55, 13.5), (-66, -34, 17.8), (-46, -12, 14.2), (-45, 12, 18.2), (-62, 36, 14.5), (-76, 56, 17.4)],
        [(-12, -48, 14.0), (-26, -24, 17.6), (-45, 0, 15.2), (-24, 24, 17.8), (-36, 54, 14.2)],
        # Sweeping West-East ribbon linking lakeside entrance to central courtyard
        [(-94, -18, 12.2), (-74, -4, 17.5), (-45, 6, 15.8), (-18, 12, 17.2), (-4, 24, 12.6)],
        [(-88, 22, 12.8), (-60, 14, 17.4), (-32, -8, 15.0), (-8, -22, 16.5)],
    ]
    for ctrl in ribbon_paths:
        # Smooth Catmull-like / sinusoidal interpolation for fluid metallic silk ribbons
        dense = []
        steps_per_seg = 6
        for i in range(len(ctrl) - 1):
            p0 = Vector(ctrl[max(0, i - 1)])
            p1 = Vector(ctrl[i])
            p2 = Vector(ctrl[i + 1])
            p3 = Vector(ctrl[min(len(ctrl) - 1, i + 2)])
            for s in range(steps_per_seg):
                t = s / steps_per_seg
                t2 = t * t
                t3 = t2 * t
                pt = 0.5 * (
                    (2.0 * p1)
                    + (-p0 + p2) * t
                    + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
                    + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
                )
                dense.append(tuple(pt))
        dense.append(ctrl[-1])
        mb.add_ribbon_strip(dense, half_width=3.6, thickness=0.65, mat=moca_ribbon_mat, smooth=True)
        # Glowing gold edge vein along ribbon center/edge
        edge_up = [(p[0], p[1], p[2] + 0.42) for p in dense]
        mb.add_polyline_tubes(edge_up, 0.20, mats["em_gold"], segments=4, smooth=True)

    # ------------------------------------------------------------------
    # 3. 128m EYE OF SUZHOU — STATIC A-FRAME SUPPORT LEGS & BOARDING HALL
    # Hub center is at (45, 0, 68). Twin A-frames straddle X = 45±10m at hub,
    # splaying out to X = 45±24m, Y = ±34m at ground Z = 0!
    # ------------------------------------------------------------------
    hx, hy, hz = HUB_BLENDER
    for sx in (-1.0, 1.0):
        hub_anchor = (hx + sx * 10.5, hy, hz)
        for sy in (-1.0, 1.0):
            foot = (hx + sx * 24.0, hy + sy * 35.0, -2.5)
            # Primary heavy tapered tubular white steel leg
            mb.add_tube(foot, hub_anchor, 2.35, mats["metal_white"], segments=12, radius2=1.45, smooth=True)
            # Illuminated cyan architectural strip running up each leg
            foot_led = (foot[0] + sx * 1.4, foot[1] + sy * 1.4, 1.0)
            hub_led = (hub_anchor[0] + sx * 1.1, hub_anchor[1] + sy * 0.9, hz - 2.0)
            mb.add_tube(foot_led, hub_led, 0.28, mats["em_cyan"], segments=5)
            # Concrete sculpted foundation pier pedestal
            mb.add_cylinder((foot[0], foot[1], 0.8), 4.6, 3.6, 5.2, mats["stone_granite"], segments=8, smooth=False)

        # Horizontal A-frame cross-beams at z=24m and z=46m
        for frac in (0.36, 0.68):
            z_b = frac * hz
            x_b = hx + sx * (24.0 * (1.0 - frac) + 10.5 * frac)
            y_b = 35.0 * (1.0 - frac)
            mb.add_tube((x_b, -y_b, z_b), (x_b, y_b, z_b), 0.95, mats["metal_white"], segments=8)

    # Axle housing caps bridging both A-frame apexes (fixed outer axle sleeves)
    mb.add_tube((hx - 12.5, hy, hz), (hx + 12.5, hy, hz), 2.2, mats["metal_white"], segments=14)

    # Modern lakeside Ferris Wheel Boarding Terminal directly beneath the wheel (Z=0..5.2m)
    # Bottom capsule clears at Z ≈ 7.8m, so 5.2m terminal has crisp clearance!
    mb.add_box_minmax(hx - 14.0, hx + 14.0, -22.0, 22.0, 0.0, 4.6, mats["glass_dark"])
    mb.add_box_minmax(hx - 16.5, hx + 16.5, -24.5, 24.5, 4.6, 5.3, mats["metal_white"])
    mb.add_tube((hx - 16.6, -24.5, 4.95), (hx - 16.6, 24.5, 4.95), 0.30, mats["em_cyan"], segments=4)
    mb.add_tube((hx + 16.6, -24.5, 4.95), (hx + 16.6, 24.5, 4.95), 0.30, mats["em_cyan"], segments=4)
    mb.add_tube((hx - 14.2, -21.0, 2.5), (hx - 14.2, 21.0, 2.5), 0.45, mats["em_warm"], segments=4)

    # Park trees flanking the plaza
    for tx, ty in [(-92, -68), (-88, 68), (-12, -74), (-10, 74), (18, -64), (18, 64), (82, -58), (82, 58)]:
        mb.add_cylinder((tx, ty, 2.5), 0.35, 0.22, 5.0, mats["trunk_bark"], segments=5)
        mb.add_icosphere((tx, ty, 6.2), 3.0, mats["foliage_green"], subdivisions=2, scale=(1.1, 1.1, 0.85))

    mb.build(origin=(0.0, 0.0, 0.0), parent=root)

    # ==================================================================
    # PART B: SEPARATE NAMED CHILD NODE `FerrisWheelRotor`
    # Origin strictly at HUB_BLENDER = (45, 0, 68) -> Three.js (45, 68, 0)
    # Wheel lies in local Y-Z plane, rotating cleanly around local X-axis!
    # ==================================================================
    mr = MeshBuilder("FerrisWheelRotor", all_mats)

    # 1. Central Rotating Hub Drum (local x = -8.5..+8.5, r = 5.6m)
    mr.add_cylinder((0.0, 0.0, 0.0), 5.6, 5.6, 17.0, mats["metal_white"], segments=24, rot_euler=(0.0, 0.5 * math.pi, 0.0))
    # Glowing cyan & accent hub halo rings on West (-X) and East (+X) hub faces
    for sx in (-1.0, 1.0):
        hub_ring = [
            (sx * 8.65, 4.2 * math.cos(2 * math.pi * k / 24), 4.2 * math.sin(2 * math.pi * k / 24))
            for k in range(24)
        ]
        mr.add_polyline_tubes(hub_ring, 0.38, mats["em_cyan"], segments=5, closed=True)
        inner_hub = [
            (sx * 8.75, 2.2 * math.cos(2 * math.pi * k / 16), 2.2 * math.sin(2 * math.pi * k / 16))
            for k in range(16)
        ]
        mr.add_polyline_tubes(inner_hub, 0.32, mats["em_accent"], segments=5, closed=True)

    # 2. Double Illuminated Structural Space-Frame Rim (outer R=58.0m, inner R=53.0m)
    n_seg = 56  # 2 segments per capsule for ultra-smooth circular silhouette
    rim_half_x = 5.4
    outer_pts_L, outer_pts_R = [], []
    inner_pts_L, inner_pts_R = [], []
    mid_cyan_L, mid_cyan_R = [], []
    mid_acc_L, mid_acc_R = [], []

    for i in range(n_seg):
        a = 2.0 * math.pi * (i / n_seg)
        ca, sa = math.cos(a), math.sin(a)
        outer_pts_L.append((-rim_half_x, WHEEL_OUTER_R * ca, WHEEL_OUTER_R * sa))
        outer_pts_R.append((rim_half_x, WHEEL_OUTER_R * ca, WHEEL_OUTER_R * sa))
        inner_pts_L.append((-rim_half_x * 0.85, WHEEL_INNER_R * ca, WHEEL_INNER_R * sa))
        inner_pts_R.append((rim_half_x * 0.85, WHEEL_INNER_R * ca, WHEEL_INNER_R * sa))
        mid_cyan_L.append((-rim_half_x - 0.85, (WHEEL_OUTER_R - 0.8) * ca, (WHEEL_OUTER_R - 0.8) * sa))
        mid_cyan_R.append((rim_half_x + 0.85, (WHEEL_OUTER_R - 0.8) * ca, (WHEEL_OUTER_R - 0.8) * sa))
        mid_acc_L.append((-rim_half_x - 0.65, (WHEEL_INNER_R + 0.6) * ca, (WHEEL_INNER_R + 0.6) * sa))
        mid_acc_R.append((rim_half_x + 0.65, (WHEEL_INNER_R + 0.6) * ca, (WHEEL_INNER_R + 0.6) * sa))

    # Primary structural white steel double rims
    mr.add_polyline_tubes(outer_pts_L, 0.88, mats["metal_white"], segments=6, closed=True)
    mr.add_polyline_tubes(outer_pts_R, 0.88, mats["metal_white"], segments=6, closed=True)
    mr.add_polyline_tubes(inner_pts_L, 0.68, mats["metal_white"], segments=6, closed=True)
    mr.add_polyline_tubes(inner_pts_R, 0.68, mats["metal_white"], segments=6, closed=True)

    # Luminous Neon Rim Halos (Emissive_Cyan outer + Emissive_Accent inner on both faces!)
    mr.add_polyline_tubes(mid_cyan_L, 0.48, mats["em_cyan"], segments=5, closed=True)
    mr.add_polyline_tubes(mid_cyan_R, 0.48, mats["em_cyan"], segments=5, closed=True)
    mr.add_polyline_tubes(mid_acc_L, 0.38, mats["em_accent"], segments=5, closed=True)
    mr.add_polyline_tubes(mid_acc_R, 0.38, mats["em_accent"], segments=5, closed=True)

    # Space-frame zig-zag truss bracing linking outer & inner rims + cross-ties between L & R
    for i in range(n_seg):
        nxt = (i + 1) % n_seg
        # Transverse tie connecting L and R outer rims at every capsule mount (even i)
        if i % 2 == 0:
            mr.add_tube(outer_pts_L[i], outer_pts_R[i], 0.42, mats["metal_silver"], segments=4)
            mr.add_tube(inner_pts_L[i], inner_pts_R[i], 0.35, mats["metal_silver"], segments=4)
        # Diagonal truss struts between inner and outer rim on both sides
        mr.add_tube(inner_pts_L[i], outer_pts_L[i], 0.30, mats["metal_white"], segments=4)
        mr.add_tube(inner_pts_L[i], outer_pts_L[nxt], 0.26, mats["metal_silver"], segments=4)
        mr.add_tube(inner_pts_R[i], outer_pts_R[i], 0.30, mats["metal_white"], segments=4)
        mr.add_tube(inner_pts_R[i], outer_pts_R[nxt], 0.26, mats["metal_silver"], segments=4)

    # 3. Tension Spokes (28 pairs = 56 crisp metallic tension cables + glowing radial accent spokes)
    for k in range(NUM_CAPSULES):
        a = 2.0 * math.pi * (k / NUM_CAPSULES)
        ca, sa = math.cos(a), math.sin(a)
        hub_y, hub_z = 5.2 * ca, 5.2 * sa
        rim_y, rim_z = WHEEL_INNER_R * ca, WHEEL_INNER_R * sa
        # Tension spokes from hub flange to both L and R inner rims
        mr.add_tube((-7.6, hub_y, hub_z), (-rim_half_x * 0.85, rim_y, rim_z), 0.20, mats["metal_silver"], segments=4)
        mr.add_tube((7.6, hub_y, hub_z), (rim_half_x * 0.85, rim_y, rim_z), 0.20, mats["metal_silver"], segments=4)
        # Every 2nd spoke carries an illuminated LED radial light bar for dramatic night spiral look
        if k % 2 == 0:
            s_mat = mats["em_cyan"] if (k // 2) % 2 == 0 else mats["em_accent"]
            mr.add_tube((0.0, 7.0 * ca, 7.0 * sa), (0.0, (WHEEL_INNER_R - 1.5) * ca, (WHEEL_INNER_R - 1.5) * sa), 0.22, s_mat, segments=4)

    # 4. 28 GLOWING PANORAMIC CAPSULES (Emissive_Gold) evenly spaced around the 58m rim!
    for k in range(NUM_CAPSULES):
        a = 2.0 * math.pi * (k / NUM_CAPSULES)
        ca, sa = math.cos(a), math.sin(a)
        # Center of each panoramic capsule sits cleanly on the outer rim mounting axis (R = 58.6m)
        cy = (WHEEL_OUTER_R + 0.6) * ca
        cz = (WHEEL_OUTER_R + 0.6) * sa
        # Outer metallic mounting yoke ring connecting capsule to both L & R outer rims
        mr.add_tube((-rim_half_x, WHEEL_OUTER_R * ca, WHEEL_OUTER_R * sa), (-2.3, cy, cz), 0.24, mats["metal_white"], segments=4)
        mr.add_tube((rim_half_x, WHEEL_OUTER_R * ca, WHEEL_OUTER_R * sa), (2.3, cy, cz), 0.24, mats["metal_white"], segments=4)
        # Panoramic ovoid capsule body (elongated along X = 4.4m, diameter = 3.2m)
        mr.add_icosphere((0.0, cy, cz), 1.65, mats["em_gold"], subdivisions=2, scale=(1.45, 0.98, 0.98), smooth=True)
        # Sleek metallic structural end-caps & equatorial frame band
        mr.add_cylinder((-2.2, cy, cz), 0.95, 0.55, 0.7, mats["metal_white"], segments=8, rot_euler=(0.0, 0.5 * math.pi, 0.0))
        mr.add_cylinder((2.2, cy, cz), 0.55, 0.95, 0.7, mats["metal_white"], segments=8, rot_euler=(0.0, 0.5 * math.pi, 0.0))
        mr.add_cylinder((0.0, cy, cz), 1.72, 1.72, 0.35, capsule_glass, segments=12, rot_euler=(0.0, 0.5 * math.pi, 0.0))

    rotor_obj = mr.build(origin=HUB_BLENDER, parent=root)
    print(f"[ROTOR] name={rotor_obj.name}, blender_origin={tuple(rotor_obj.location)}, three_pos=({HUB_BLENDER[0]}, {HUB_BLENDER[2]}, {-HUB_BLENDER[1]}), axis=X")

    export_glb(OUT_PATH)
    verify_glb(OUT_PATH)


if __name__ == "__main__":
    build_moca_and_eye()
