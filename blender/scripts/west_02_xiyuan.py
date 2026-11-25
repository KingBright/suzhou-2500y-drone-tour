"""
Station 02a: Xiyuan Temple (西园戒幢律寺)
Exports: web/public/assets/models/xiyuan_temple.glb
Features: Ornate 3-bay Xiyuan Paifang archway, yellow mountain gate & walls,
          Release Pond (放生池) with octagonal double-eave Lake Pavilion & zigzag bridge,
          Arhat Hall (罗汉堂) & Mahavira complex.
"""
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from west_common import SuzhouBuilder

OUT_GLB = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models/xiyuan_temple.glb"


def build_xiyuan_paifang(b, cx, cy, z0=0.0):
    """Iconic 3-bay multi-tiered stone & timber Xiyuan Paifang archway (敕赐西园戒幢律寺)."""
    # 4 granite square pillars with carved drum bases
    pxs = [-7.8, -3.2, 3.2, 7.8]
    for i, px in enumerate(pxs):
        h = 6.6 if i in (1, 2) else 4.9
        b.box_z(cx + px, cy, z0, z0 + 1.4, 0.85, 1.45, "Mat_GraniteLight")
        b.box_z(cx + px, cy, z0 + 1.4, z0 + h, 0.56, 0.56, "Mat_GraniteLight")
    # Horizontal lintel beams + crimson central inscription plaque
    b.box_z(cx, cy, z0 + 5.2, z0 + 6.1, 6.8, 0.52, "Mat_GraniteLight")
    b.box_z(cx, cy - 0.30, z0 + 5.3, z0 + 6.0, 6.2, 0.14, "Mat_PlaqueRed")
    b.box_z(cx, cy - 0.38, z0 + 5.42, z0 + 5.88, 5.6, 0.08, "Mat_GoldTrim")
    # Side bay lintels
    for sx in (-1, 1):
        b.box_z(cx + sx * 5.5, cy, z0 + 4.1, z0 + 4.8, 4.8, 0.45, "Mat_GraniteLight")
        b.add_upturned_roof(
            cx + sx * 5.5, cy, z0 + 4.85, 5.2, 2.2, 1.55,
            mat_wood="Mat_CrimsonWood", mat_gold="Mat_GoldTrim",
            mat_eave_light="Emissive_Gold_Eave", overhang=0.85, flare_z=0.75, flare_xy=0.55, steps=3,
        )
    # Central upper crimson shrine box + double sweeping upturned roofs
    b.add_upturned_roof(
        cx, cy, z0 + 6.2, 7.4, 2.5, 1.65,
        mat_wood="Mat_CrimsonWood", mat_gold=None,
        mat_eave_light="Emissive_Gold_Eave", overhang=0.95, flare_z=0.85, flare_xy=0.65, steps=3,
    )
    b.box_z(cx, cy, z0 + 7.2, z0 + 9.4, 3.6, 1.6, "Mat_CrimsonWood")
    b.box_z(cx, cy - 0.85, z0 + 7.5, z0 + 9.1, 1.4, 0.14, "Emissive_Warm_Window")
    b.add_upturned_roof(
        cx, cy, z0 + 9.35, 5.4, 2.4, 2.1,
        mat_wood="Mat_CrimsonWood", mat_gold="Mat_GoldTrim",
        mat_eave_light="Emissive_Gold_Eave", overhang=1.05, flare_z=1.05, flare_xy=0.75, steps=4,
    )
    # Hanging archway lanterns
    for lx in (-5.5, -1.8, 1.8, 5.5):
        b.add_lantern(cx + lx, cy - 0.45, z0 + 4.6, scale=0.75)


def add_zigzag_bridge_segment(b, x0, y0, x1, y1, z_deck=0.25, w=2.6):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.2:
        return
    ang = math.atan2(dy, dx)
    mx, my = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    from mathutils import Matrix
    m = Matrix.Translation((mx, my, z_deck)) @ Matrix.Rotation(ang, 4, 'Z')
    # Stone bridge slab + submerged piers
    b.box_z(0, 0, -0.35, 0.0, length + 0.3, w, "Mat_GraniteLight", matrix=m)
    n_piers = max(2, int(length // 4.5) + 1)
    for i in range(n_piers):
        px = -length * 0.5 + length * i / (n_piers - 1)
        b.box_z(px, 0, -1.3, -0.35, 0.55, w * 0.85, "Mat_GraniteDark", matrix=m)
        for sy in (-1, 1):
            b.box_z(px, sy * (w * 0.44), 0.0, 0.92, 0.26, 0.26, "Mat_GraniteLight", matrix=m)
            if i == n_piers // 2 and sy == -1:
                b.add_lantern(px, sy * (w * 0.44), 1.18, scale=0.55, matrix=m)
    # Side stone rails
    for sy in (-1, 1):
        b.box_z(0, sy * (w * 0.44), 0.0, 0.72, length, 0.16, "Mat_GraniteLight", matrix=m)


def main():
    b = SuzhouBuilder("XiyuanTemple")

    # 1. Ground Plinth (128m x 114m, Z = -2.2..0.0) with recessed Release Pond cavity on West side
    # East temple courtyard ground (X in [-2, +64], Y in [-56, +56])
    b.box_z(31.0, 0.0, -2.2, 0.0, 66.0, 112.0, "Mat_GraniteLight")
    # South forecourt plaza (X in [-64, -2], Y in [-56, -28])
    b.box_z(-33.0, -42.0, -2.2, 0.0, 62.0, 28.0, "Mat_GraniteLight")
    # North garden bank (X in [-64, -2], Y in [+38, +56])
    b.box_z(-33.0, 47.0, -2.2, 0.0, 62.0, 18.0, "Mat_GraniteLight")
    # West perimeter bank (X in [-64, -52], Y in [-28, +38])
    b.box_z(-58.0, 5.0, -2.2, 0.0, 12.0, 66.0, "Mat_GraniteLight")

    # 2. Iconic Release Pond (放生池) (X in [-52, -2], Y in [-28, +38])
    # Pond basin bottom + serene jade water surface at Z = -0.35 (well above world water!)
    b.box_z(-27.0, 5.0, -2.2, -1.1, 52.0, 68.0, "Mat_GraniteDark")
    b.box_z(-27.0, 5.0, -1.0, -0.35, 50.6, 66.6, "Mat_PondWater")
    # Carved granite pond coping parapet
    b.box_z(-27.0, -28.0, -1.1, 0.35, 51.0, 1.0, "Mat_GraniteLight")
    b.box_z(-27.0, 38.0, -1.1, 0.35, 51.0, 1.0, "Mat_GraniteLight")
    b.box_z(-52.0, 5.0, -1.1, 0.35, 1.0, 66.0, "Mat_GraniteLight")
    b.box_z(-2.0, 5.0, -1.1, 0.35, 1.0, 66.0, "Mat_GraniteLight")

    # Central Octagonal Double-Eave Lake Pavilion (湖心亭) on stone island
    b.prism(-27.0, 5.0, -1.3, 0.35, 7.6, 7.2, 8, "Mat_GraniteDark")
    b.add_pavilion(
        -27.0, 5.0, 0.35, radius=5.6, col_h=4.0, roof_h=4.4, sides=8,
        double_eave=True, plinth_h=0.6, pillar_mat="Mat_CrimsonWood",
        gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave",
    )

    # Iconic Zigzag Nine-Turn Bridge (九曲桥) linking East Temple -> Lake Pavilion -> West & North Banks
    zigzag_east = [(-2.0, -6.0), (-9.0, -6.0), (-9.0, 1.0), (-16.0, 1.0), (-16.0, 5.0), (-21.0, 5.0)]
    for i in range(len(zigzag_east) - 1):
        add_zigzag_bridge_segment(b, *zigzag_east[i], *zigzag_east[i + 1], z_deck=0.25, w=2.5)
    zigzag_north = [(-27.0, 11.5), (-27.0, 19.0), (-33.0, 19.0), (-33.0, 28.0), (-26.0, 28.0), (-26.0, 38.0)]
    for i in range(len(zigzag_north) - 1):
        add_zigzag_bridge_segment(b, *zigzag_north[i], *zigzag_north[i + 1], z_deck=0.25, w=2.4)
    zigzag_south = [(-27.0, -1.5), (-27.0, -11.0), (-35.0, -11.0), (-35.0, -20.0), (-28.0, -20.0), (-28.0, -28.0)]
    for i in range(len(zigzag_south) - 1):
        add_zigzag_bridge_segment(b, *zigzag_south[i], *zigzag_south[i + 1], z_deck=0.25, w=2.4)

    # Lotus leaf pads & pond rockeries in Release Pond
    lotus_spots = [
        (-42, -16), (-44, -12), (-40, -14), (-14, 24), (-10, 27), (-16, 28),
        (-44, 22), (-41, 25), (-14, -18), (-11, -21), (-46, 4), (-43, 7),
    ]
    for lx, ly in lotus_spots:
        b.prism(lx, ly, -0.34, -0.28, 1.1, 1.1, 7, "Mat_LotusLeaf")
    b.add_taihu_rock(-45.0, 31.0, -0.8, 5.5, 4.5, 4.2, seed=11)
    b.add_taihu_rock(-10.0, 32.0, -0.8, 4.8, 4.0, 3.6, seed=12)

    # West lakeside tea corridor overlooking the Release Pond
    b.add_corridor(-56.0, -20.0, -56.0, 30.0, z0=0.0, width=3.4, h=3.3,
                   back_wall=True, wall_side=-1, wall_mat="Mat_TempleYellow", wood_mat="Mat_CrimsonWood")

    # 3. South Forecourt: Ornate 3-Bay Xiyuan Paifang + Yellow Temple Perimeter Walls
    build_xiyuan_paifang(b, 26.0, -48.0, z0=0.0)

    # Yellow Temple Perimeter Walls (黄墙黛瓦)
    b.add_wall(-61.0, -53.0, 12.0, -53.0, h=4.2, wall_mat="Mat_TempleYellow")
    b.add_wall(40.0, -53.0, 61.0, -53.0, h=4.2, wall_mat="Mat_TempleYellow")
    b.add_wall(61.0, -53.0, 61.0, 53.0, h=4.2, wall_mat="Mat_TempleYellow")
    b.add_wall(61.0, 53.0, -61.0, 53.0, h=4.2, wall_mat="Mat_TempleYellow")
    b.add_wall(-61.0, 53.0, -61.0, -53.0, h=4.2, wall_mat="Mat_TempleYellow")

    # 4. Xiyuan Temple Main Axis & Arhat Hall Complex (East Precinct)
    # Yellow Mountain Gate Hall (山门 & 天王殿)
    b.add_hall(26.0, -32.0, 0.0, 22.0, 10.5, wall_h=4.8, roof_h=3.6, double_eave=False,
               rot_z=0.0, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=0.9)

    # Main Courtyard Bronze Incense Burner & Lanterns
    b.box_z(26.0, -16.0, 0.0, 0.65, 4.0, 4.0, "Mat_GraniteLight")
    b.box_z(26.0, -16.0, 0.65, 2.2, 2.3, 1.5, "Mat_Bronze")
    b.box_z(26.0, -16.0, 2.2, 2.55, 1.7, 1.0, "Emissive_Warm_Lantern")
    for sx in (-1, 1):
        b.add_lantern_post(26.0 + sx * 9.0, -21.0, 0.0, h=3.4)
        b.add_lantern_post(26.0 + sx * 9.0, -9.0, 0.0, h=3.4)

    # Grand Mahavira Hall (大雄宝殿) - Double-eave temple centerpiece
    b.add_hall(26.0, 2.0, 0.0, 30.0, 19.0, wall_h=6.8, roof_h=5.2, double_eave=True,
               rot_z=0.0, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=1.4)

    # Famous 500-Arhat Hall (罗汉堂) directly north of Mahavira Hall (large square-wing complex)
    b.add_hall(26.0, 32.0, 0.0, 34.0, 20.0, wall_h=6.2, roof_h=4.6, double_eave=True,
               rot_z=0.0, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave", plinth_h=1.2)

    # East & West Monastic Wing Corridors (东西厢房)
    b.add_hall(51.0, 2.0, 0.0, 26.0, 8.5, wall_h=4.4, roof_h=2.8, double_eave=False,
               rot_z=math.pi * 0.5, wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
               gold_mat=None, eave_light="Emissive_Gold_Eave", plinth_h=0.7)
    b.add_corridor(4.0, -22.0, 4.0, 24.0, z0=0.0, width=3.2, h=3.4,
                   back_wall=False, wall_mat="Mat_TempleYellow", wood_mat="Mat_CrimsonWood")

    # Small Bell & Drum Pavilions flanking the forecourt
    b.add_pavilion(10.0, -34.0, 0.0, radius=3.6, col_h=3.6, roof_h=3.0, sides=6,
                   pillar_mat="Mat_CrimsonWood", eave_light="Emissive_Gold_Eave")
    b.add_pavilion(42.0, -34.0, 0.0, radius=3.6, col_h=3.6, roof_h=3.0, sides=6,
                   pillar_mat="Mat_CrimsonWood", eave_light="Emissive_Gold_Eave")

    # 5. Lush Temple Pines, Lakeside Willows, Maples & Bamboo
    willows = [
        (-53.0, -24.0, 1.15), (-53.0, 12.0, 1.10), (-53.0, 36.0, 1.15),
        (-36.0, 43.0, 1.10), (-14.0, 43.0, 1.15), (-44.0, -34.0, 1.10), (-12.0, -34.0, 1.05),
    ]
    for i, (wx, wy, sc) in enumerate(willows):
        b.add_tree_willow(wx, wy, 0.0, scale=sc, seed=i + 10)

    pines = [
        (12.0, -46.0, 1.15), (40.0, -46.0, 1.15), (54.0, -40.0, 1.2), (54.0, -20.0, 1.1),
        (54.0, 28.0, 1.2), (54.0, 46.0, 1.15), (4.0, 44.0, 1.2), (-26.0, -44.0, 1.15),
        (-52.0, -44.0, 1.1), (-50.0, 46.0, 1.2),
    ]
    for i, (px, py, sc) in enumerate(pines):
        b.add_tree_pine(px, py, 0.0, scale=sc, seed=i + 50)

    maples = [
        (-2.0, -34.0, 1.05), (-2.0, 36.0, 1.05), (48.0, -30.0, 1.0), (48.0, 44.0, 1.0),
    ]
    for i, (mx, my, sc) in enumerate(maples):
        b.add_tree_maple(mx, my, 0.0, scale=sc, seed=i + 90)

    b.build_and_export(OUT_GLB)


if __name__ == "__main__":
    main()
