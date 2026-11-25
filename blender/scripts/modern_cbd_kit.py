"""Generate Modern CBD Modular Kit (`modern_cbd_kit.glb`) for THREE.InstancedMesh Jinji Lake skyline filling.
Exports 7 top-level named mesh objects, each centered at base (0, 0, 0), low-poly (150-700 tris each):
  - TowerA (140m glass tower)
  - TowerB (185m stepped tower)
  - TowerC (110m curved office tower)
  - TowerD (220m sleek spire tower)
  - ModernLamp (9m contemporary waterfront lamp)
  - YachtBoat (18m luxury lake cruiser yacht)
  - ParkTree (10m modern urban park tree)
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

OUT_PATH = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/modern_cbd_kit.glb"


def build_tower_a(mats):
    """TowerA: 140m sleek chamfered octagonal glass skyscraper (~260 tris)."""
    mb = MeshBuilder("TowerA", [mats["glass_blue"], mats["metal_silver"], mats["em_cyan"], mats["em_gold"]])

    def oct_ring(r, z):
        c = r * 0.42
        return [
            (r, c, z), (c, r, z), (-c, r, z), (-r, c, z),
            (-r, -c, z), (-c, -r, z), (c, -r, z), (r, -c, z),
        ]

    mb.add_loft([oct_ring(18.0, 0.0), oct_ring(17.5, 70.0), oct_ring(16.2, 134.0)], mats["glass_blue"],
                closed_loop=True, cap_start=True, cap_end=True, smooth=False)
    mb.add_loft([oct_ring(16.5, 134.0), oct_ring(14.5, 140.0)], mats["metal_silver"],
                closed_loop=True, cap_start=False, cap_end=True, smooth=False)
    for zb, mat_b in [(36.0, mats["em_gold"]), (72.0, mats["em_gold"]), (108.0, mats["em_cyan"]), (135.5, mats["em_cyan"])]:
        r = 18.2 - 1.8 * (zb / 140.0)
        mb.add_loft([oct_ring(r, zb - 1.1), oct_ring(r, zb + 1.1)], mat_b, closed_loop=True, smooth=False)
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        mb.add_box((sx * 12.6, sy * 12.6, 68.0), (0.8, 0.8, 132.0), mats["em_cyan"])
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_tower_b(mats):
    """TowerB: 185m 3-tier stepped corporate skyscraper (~250 tris)."""
    mb = MeshBuilder("TowerB", [mats["glass_dark"], mats["metal_champagne"], mats["em_gold"], mats["em_cyan"]])
    mb.add_box_minmax(-21.0, 21.0, -18.0, 18.0, 0.0, 95.0, mats["glass_dark"])
    mb.add_box_minmax(-16.5, 16.5, -14.5, 14.5, 95.0, 148.0, mats["glass_dark"])
    mb.add_box_minmax(-12.0, 12.0, -11.0, 11.0, 148.0, 178.0, mats["glass_dark"])
    mb.add_box_minmax(-12.2, 12.2, -11.2, 11.2, 178.0, 185.0, mats["metal_champagne"])
    for (hx, hy, z0, z1, m) in [
        (21.3, 18.3, 34.0, 36.2, mats["em_gold"]),
        (21.3, 18.3, 66.0, 68.2, mats["em_gold"]),
        (21.4, 18.4, 93.8, 96.0, mats["em_gold"]),
        (16.8, 14.8, 122.0, 124.2, mats["em_gold"]),
        (16.9, 14.9, 146.8, 149.0, mats["em_cyan"]),
        (12.4, 11.4, 177.2, 179.4, mats["em_gold"]),
        (12.5, 11.5, 183.6, 185.2, mats["em_gold"]),
    ]:
        mb.add_box_minmax(-hx, hx, -hy, hy, z0, z1, m)
    for sx in (-1.0, 1.0):
        mb.add_box((sx * 21.2, 0.0, 47.5), (1.0, 4.0, 95.0), mats["metal_champagne"])
        mb.add_box((sx * 16.7, 0.0, 121.5), (0.9, 3.2, 53.0), mats["metal_champagne"])
        mb.add_box((0.0, sx * 18.2, 47.5), (4.0, 1.0, 95.0), mats["metal_champagne"])
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_tower_c(mats):
    """TowerC: 110m curved elliptical modern office tower (~260 tris)."""
    mb = MeshBuilder("TowerC", [mats["glass_silver"], mats["em_cyan"], mats["em_warm"]])
    segs = 16

    def ell_ring(rx, ry, z, slope_x=0.0):
        pts = []
        for k in range(segs):
            a = 2.0 * math.pi * k / segs
            x = rx * math.cos(a)
            y = ry * math.sin(a)
            pts.append((x, y, z + slope_x * (x / max(1.0, rx))))
        return pts

    mb.add_loft(
        [ell_ring(21.0, 13.0, 0.0), ell_ring(20.5, 12.6, 55.0), ell_ring(19.2, 11.8, 102.0, slope_x=7.8)],
        mats["glass_silver"], closed_loop=True, cap_start=True, cap_end=True, smooth=True
    )
    mb.add_loft(
        [ell_ring(19.6, 12.1, 101.2, slope_x=7.8), ell_ring(19.6, 12.1, 102.8, slope_x=7.8)],
        mats["em_cyan"], closed_loop=True, smooth=True
    )
    for zb, m in [(28.0, mats["em_warm"]), (56.0, mats["em_cyan"]), (82.0, mats["em_warm"])]:
        mb.add_loft([ell_ring(20.8, 12.9, zb - 0.9), ell_ring(20.8, 12.9, zb + 0.9)], m, closed_loop=True, smooth=True)
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_tower_d(mats):
    """TowerD: 220m sleek tapering hexagonal spire skyscraper (~260 tris)."""
    mb = MeshBuilder("TowerD", [mats["glass_blue"], mats["metal_silver"], mats["em_gold"], mats["em_cyan"]])
    segs = 6

    def hex_ring(rx, ry, z, slope=0.0):
        pts = []
        for k in range(segs):
            a = 2.0 * math.pi * k / segs
            x = rx * math.cos(a)
            y = ry * math.sin(a)
            pts.append((x, y, z + slope * (x / max(1.0, rx))))
        return pts

    mb.add_loft(
        [
            hex_ring(22.0, 20.0, 0.0),
            hex_ring(19.5, 18.0, 96.0),
            hex_ring(14.0, 13.0, 174.0),
            hex_ring(11.5, 10.5, 192.0, slope=10.0),
        ],
        mats["glass_blue"], closed_loop=True, cap_start=True, cap_end=True, smooth=False
    )
    mb.add_loft(
        [hex_ring(11.8, 10.8, 190.5, slope=10.0), hex_ring(11.8, 10.8, 192.8, slope=10.0)],
        mats["em_gold"], closed_loop=True, smooth=False
    )
    mb.add_cylinder((0.0, 0.0, 207.0), 1.8, 0.25, 24.0, mats["metal_silver"], segments=6, smooth=False)
    mb.add_cylinder((0.0, 0.0, 217.5), 0.55, 0.15, 5.0, mats["em_cyan"], segments=6, smooth=False)

    for k in range(segs):
        a = 2.0 * math.pi * k / segs
        p0 = (22.3 * math.cos(a), 20.3 * math.sin(a), 2.0)
        p1 = (14.3 * math.cos(a), 13.3 * math.sin(a), 174.0)
        mb.add_tube(p0, p1, 0.48, mats["em_cyan"] if k % 2 == 0 else mats["em_gold"], segments=4)

    for zb, rx, ry in [(64.0, 20.5, 18.8), (128.0, 17.4, 16.0)]:
        mb.add_loft([hex_ring(rx, ry, zb - 1.1), hex_ring(rx, ry, zb + 1.1)], mats["em_gold"], closed_loop=True, smooth=False)
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_modern_lamp(mats):
    """ModernLamp: 9m sleek contemporary curved waterfront street lamp (~200 tris)."""
    mb = MeshBuilder("ModernLamp", [mats["metal_dark"], mats["em_warm"], mats["em_gold"]])
    mb.add_cylinder((0.0, 0.0, 0.35), 0.36, 0.24, 0.7, mats["metal_dark"], segments=10, smooth=True)
    mb.add_cylinder((0.0, 0.0, 4.1), 0.16, 0.10, 7.2, mats["metal_dark"], segments=10, smooth=True)
    # Curved modern twin-segment gooseneck arm up to 9.0m
    mb.add_tube((0.0, 0.0, 7.4), (0.65, 0.0, 8.35), 0.10, mats["metal_dark"], segments=8)
    mb.add_tube((0.65, 0.0, 8.35), (1.45, 0.0, 8.85), 0.09, mats["metal_dark"], segments=8)
    mb.add_tube((1.45, 0.0, 8.85), (2.25, 0.0, 9.0), 0.08, mats["metal_dark"], segments=8)
    mb.add_box((2.20, 0.0, 9.04), (1.18, 0.44, 0.12), mats["metal_dark"])
    mb.add_box((2.20, 0.0, 8.95), (1.04, 0.36, 0.08), mats["em_warm"])
    mb.add_cylinder((0.0, 0.0, 2.2), 0.18, 0.18, 0.28, mats["em_gold"], segments=10, smooth=True)
    mb.add_cylinder((0.0, 0.0, 5.6), 0.14, 0.14, 0.22, mats["em_gold"], segments=10, smooth=True)
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_yacht_boat(mats):
    """YachtBoat: 18m sleek luxury Jinji Lake cruiser yacht (~270 tris)."""
    mb = MeshBuilder("YachtBoat", [mats["metal_white"], mats["glass_dark"], mats["wood_deck"], mats["em_warm"], mats["em_cyan"]])
    hull_stations = [
        (-9.0, 2.5, 1.8, -0.75, 1.35),
        (-4.5, 2.8, 1.9, -0.85, 1.50),
        (1.0, 2.6, 1.4, -0.80, 1.65),
        (5.5, 1.6, 0.5, -0.55, 1.85),
        (9.0, 0.12, 0.05, 0.15, 2.15),
    ]
    rings = []
    for x, hwt, hwk, zk, zd in hull_stations:
        rings.append([
            (x, 0.0, zk),
            (x, hwk, zk + 0.35),
            (x, hwt, zd),
            (x, -hwt, zd),
            (x, -hwk, zk + 0.35),
        ])
    mb.add_loft(rings, mats["metal_white"], closed_loop=True, cap_start=True, cap_end=True, smooth=True)

    # Teak aft cockpit deck & swim platform
    mb.add_box_minmax(-9.5, -3.5, -2.2, 2.2, 1.38, 1.54, mats["wood_deck"])

    # Sleek salon superstructure & wrap-around glass
    mb.add_loft(
        [
            [(-4.2, -2.2, 1.5), (3.8, -1.7, 1.65), (3.8, 1.7, 1.65), (-4.2, 2.2, 1.5)],
            [(-3.6, -1.8, 3.1), (2.2, -1.4, 3.2), (2.2, 1.4, 3.2), (-3.6, 1.8, 3.1)],
        ],
        mats["glass_dark"], closed_loop=True, cap_start=False, cap_end=True, smooth=False
    )
    # Aerodynamic flybridge roof + radar arch + navigation mast
    mb.add_box((-1.0, 0.0, 3.35), (6.4, 3.6, 0.38), mats["metal_white"])
    mb.add_box((-0.6, 0.0, 4.15), (3.4, 2.4, 1.0), mats["metal_white"])
    mb.add_tube((-2.2, -1.5, 3.5), (-2.8, -1.1, 5.1), 0.14, mats["metal_white"], segments=5)
    mb.add_tube((-2.2, 1.5, 3.5), (-2.8, 1.1, 5.1), 0.14, mats["metal_white"], segments=5)
    mb.add_tube((-2.8, -1.1, 5.1), (-2.8, 1.1, 5.1), 0.15, mats["metal_white"], segments=5)
    mb.add_cylinder((-2.8, 0.0, 5.55), 0.25, 0.20, 0.55, mats["metal_white"], segments=6)

    # Stainless bow rail + warm cabin glow & cyan waterline accent strips
    for sy in (-1.0, 1.0):
        mb.add_tube((2.8, sy * 2.1, 2.25), (8.6, sy * 0.25, 2.65), 0.06, mats["metal_white"], segments=4)
        mb.add_tube((-3.8, sy * 2.05, 2.35), (2.6, sy * 1.62, 2.45), 0.16, mats["em_warm"], segments=5)
        mb.add_tube((-8.5, sy * 2.55, 0.25), (6.5, sy * 1.30, 0.35), 0.10, mats["em_cyan"], segments=5)
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_park_tree(mats):
    """ParkTree: 10m modern urban park tree with layered sculpted foliage (~212 tris)."""
    mb = MeshBuilder("ParkTree", [mats["trunk_bark"], mats["foliage_green"], mats["foliage_light"]])
    mb.add_cylinder((0.0, 0.0, 2.4), 0.42, 0.22, 4.8, mats["trunk_bark"], segments=7, smooth=True)
    mb.add_tube((0.0, 0.0, 3.8), (1.1, 0.7, 5.4), 0.16, mats["trunk_bark"], segments=5)
    mb.add_tube((0.0, 0.0, 3.9), (-1.0, 0.6, 5.5), 0.16, mats["trunk_bark"], segments=5)
    mb.add_tube((0.0, 0.0, 4.0), (0.1, -1.1, 5.3), 0.16, mats["trunk_bark"], segments=5)
    mb.add_icosphere((0.0, 0.0, 7.3), 2.75, mats["foliage_green"], subdivisions=2, scale=(1.15, 1.15, 0.96), smooth=True)
    mb.add_icosphere((1.35, 0.85, 6.2), 1.95, mats["foliage_light"], subdivisions=1, scale=(1.1, 1.05, 0.9), smooth=True)
    mb.add_icosphere((-1.25, 0.75, 6.4), 2.05, mats["foliage_green"], subdivisions=1, scale=(1.05, 1.1, 0.9), smooth=True)
    mb.add_icosphere((0.15, -1.35, 6.1), 1.90, mats["foliage_light"], subdivisions=1, scale=(1.1, 1.05, 0.9), smooth=True)
    return mb.build(origin=(0.0, 0.0, 0.0))


def build_modern_cbd_kit():
    clear_scene()
    mats = make_standard_modern_mats()

    objs = [
        build_tower_a(mats),
        build_tower_b(mats),
        build_tower_c(mats),
        build_tower_d(mats),
        build_modern_lamp(mats),
        build_yacht_boat(mats),
        build_park_tree(mats),
    ]
    for obj in objs:
        obj.data.calc_loop_triangles()
        print(f"  [KIT PART] {obj.name}: {len(obj.data.loop_triangles)} tris, origin={tuple(obj.location)}")

    export_glb(OUT_PATH)
    verify_glb(OUT_PATH)


if __name__ == "__main__":
    build_modern_cbd_kit()
