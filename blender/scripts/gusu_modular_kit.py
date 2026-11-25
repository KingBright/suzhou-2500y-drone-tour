"""
Generate gusu_modular_kit.glb — Clean low-poly modular kit for THREE.InstancedMesh city filling.
Top-level named mesh objects (each centered at base (0,0,0), 150-800 tris each):
  HouseA, HouseB, HouseC, WillowTree, PineTree, StoneBridge, LanternPost, WoodenBoat
"""
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gusu_common import clear_scene, create_gusu_palette, SceneBuilder, export_glb


def build_house_a(palette):
    """2-story classic white-wall dark-tile Gusu house with Matouqiang gables."""
    sb = SceneBuilder(palette)
    # Compact low-poly foundation skirt
    sb.add_box("stone_dark", 9.6, 6.4, 2.2, center=(0, 0, -0.85))
    sb.add_box("white_wall", 9.2, 6.0, 6.2, center=(0, 0, 0.25 + 3.1))
    sb.add_box("dark_wood", 9.32, 6.12, 0.22, center=(0, 0, 3.35))
    # Warm glowing windows (front & back, 2 floors x 3 bays)
    for st in (0, 1):
        wz = 1.75 + st * 3.0
        for sy in (-1.0, 1.0):
            for lx in (-2.7, 0.0, 2.7):
                sb.add_box("dark_wood", 1.35, 0.14, 1.35, center=(lx, sy * 3.04, wz))
                sb.add_box("emissive_win", 1.05, 0.08, 1.05, center=(lx, sy * 3.09, wz))
    # Swept dark-tile pitched roof (low-poly version)
    sb.add_suzhou_roof(9.2, 6.0, 2.25, center=(0, 0, 6.35), eave_overhang=0.68,
                       corner_lift=0.30, hip_gable=False, add_ribs=False)
    # Horse-head stepped gable walls (马头墙)
    for xs in (-1.0, 1.0):
        for sd, sh in ((6.6, 0.65), (4.0, 1.45), (1.9, 2.2)):
            sb.add_box("white_wall", 0.30, sd, sh + 0.3, center=(xs * 4.72, 0, 6.35 + sh * 0.5))
            sb.add_box("dark_tile", 0.48, sd + 0.24, 0.16, center=(xs * 4.72, 0, 6.50 + sh))
    return sb.build_single_named_object("HouseA")


def build_house_b(palette):
    """Wider 2-story Gusu waterfront courtyard residence with timber balcony."""
    sb = SceneBuilder(palette)
    sb.add_box("stone_dark", 12.2, 7.2, 2.2, center=(0, 0, -0.85))
    sb.add_box("cream_wall", 11.8, 6.8, 6.6, center=(0, 0, 0.25 + 3.3))
    sb.add_box("dark_wood", 11.95, 6.95, 0.24, center=(0, 0, 3.55))
    # Front timber balcony + railing
    sb.add_box("dark_wood", 8.8, 1.15, 0.20, center=(0, -3.95, 3.55))
    sb.add_box("warm_wood", 8.8, 0.14, 0.78, center=(0, -4.46, 3.98))
    # Windows
    for st in (0, 1):
        wz = 1.85 + st * 3.15
        for sy in (-1.0, 1.0):
            for lx in (-3.8, -1.3, 1.3, 3.8):
                sb.add_box("dark_wood", 1.3, 0.14, 1.4, center=(lx, sy * 3.44, wz))
                sb.add_box("emissive_win", 1.0, 0.08, 1.1, center=(lx, sy * 3.49, wz))
    # Sweeping hip-gable roof
    sb.add_suzhou_roof(11.8, 6.8, 2.55, center=(0, 0, 6.75), eave_overhang=0.82,
                       corner_lift=0.42, hip_gable=True, add_ribs=False)
    # Hanging red lantern under balcony
    sb.add_ico("emissive_red", radius=0.26, subdivisions=1, scale=(1.0, 1.0, 1.25),
               center=(0, -4.0, 2.85))
    return sb.build_single_named_object("HouseB")


def build_house_c(palette):
    """Compact 2-story corner teahouse / canal shopfront with dark timber ground facade."""
    sb = SceneBuilder(palette)
    sb.add_box("stone_dark", 7.8, 6.6, 2.2, center=(0, 0, -0.85))
    # Ground floor dark-wood shopfront + upper white plaster
    sb.add_box("dark_wood", 7.4, 6.2, 3.1, center=(0, 0, 0.25 + 1.55))
    sb.add_box("white_wall", 7.4, 6.2, 2.9, center=(0, 0, 3.35 + 1.45))
    # Warm glowing shopfront doors & upper windows
    for lx in (-2.0, 0.0, 2.0):
        sb.add_box("emissive_win", 1.25, 0.10, 2.1, center=(lx, -3.14, 1.55))
        sb.add_box("dark_wood", 1.25, 0.14, 1.2, center=(lx, -3.14, 4.75))
        sb.add_box("emissive_win", 0.95, 0.08, 0.95, center=(lx, -3.18, 4.75))
        sb.add_box("emissive_win", 0.95, 0.08, 0.95, center=(lx, 3.16, 4.75))
    # Front awning + main roof
    sb.add_box("dark_tile", 7.8, 1.25, 0.18, center=(0, -3.55, 3.25),
               rot_euler=(0.32, 0.0, 0.0))
    sb.add_suzhou_roof(7.4, 6.2, 2.15, center=(0, 0, 6.15), eave_overhang=0.72,
                       corner_lift=0.38, hip_gable=True, add_ribs=False)
    # Pair of red lanterns at shopfront
    for lx in (-2.6, 2.6):
        sb.add_ico("emissive_red", radius=0.25, subdivisions=1, scale=(1.0, 1.0, 1.28),
                   center=(lx, -3.75, 2.65))
    return sb.build_single_named_object("HouseC")


def build_willow_tree(palette):
    sb = SceneBuilder(palette)
    sb.add_willow_tree(center=(0, 0, 0), height=8.8, lean=(0.75, 0.15), seed=101)
    return sb.build_single_named_object("WillowTree")


def build_pine_tree(palette):
    sb = SceneBuilder(palette)
    sb.add_pine_tree(center=(0, 0, 0), height=9.8, seed=202)
    # Extra lower sculptural branch pad + stone root collar for richer close-up silhouette
    sb.add_cylinder("stone_dark", 0.55, 0.48, 0.35, segments=6, center=(0, 0, 0.17))
    sb.add_ico("pine", radius=1.9, subdivisions=1, scale=(1.2, 0.9, 0.36), center=(1.8, -1.2, 4.4))
    sb.add_ico("pine", radius=1.6, subdivisions=1, scale=(1.1, 0.9, 0.38), center=(-1.5, 1.4, 5.2))
    return sb.build_single_named_object("PineTree")


def build_stone_bridge(palette):
    sb = SceneBuilder(palette)
    sb.add_arch_bridge(span=14.0, width=3.2, arch_h=3.1, center=(0, 0, 0),
                       rot_z=0.0, lanterns=True)
    return sb.build_single_named_object("StoneBridge")


def build_lantern_post(palette):
    """Classical Suzhou dark-timber waterfront lantern post."""
    sb = SceneBuilder(palette)
    sb.add_cylinder("stone_dark", 0.38, 0.30, 0.65, segments=8, center=(0, 0, 0.325))
    sb.add_cylinder("stone_light", 0.30, 0.24, 0.22, segments=8, center=(0, 0, 0.72))
    sb.add_cylinder("dark_wood", 0.11, 0.08, 3.85, segments=8, center=(0, 0, 2.3))
    # Ornate curved cross-arm, diagonal brace & upturned mini roof cap
    sb.add_box("dark_wood", 1.20, 0.12, 0.12, center=(0.48, 0, 4.05))
    sb.add_box("dark_wood", 0.62, 0.09, 0.09, center=(0.25, 0, 3.72), rot_euler=(0.0, -0.78, 0.0))
    sb.add_radial_roof(4, 0.44, 0.30, center=(0.90, 0, 3.75), corner_lift=0.08, finial=False)
    # Glowing red-gold palace lantern + bottom tassel
    sb.add_ico("emissive_red", radius=0.28, subdivisions=1, scale=(1.0, 1.0, 1.32),
               center=(0.90, 0, 3.32))
    sb.add_cylinder("emissive_warm", 0.18, 0.14, 0.12, segments=8, center=(0.90, 0, 2.92))
    sb.add_cylinder("vermilion", 0.05, 0.02, 0.32, segments=6, center=(0.90, 0, 2.70))
    return sb.build_single_named_object("LanternPost")


def build_wooden_boat(palette):
    sb = SceneBuilder(palette)
    sb.add_wooden_boat(center=(0, 0, 0), rot_z=0.0, length=6.8, width=1.65)
    # Added transverse bench thwarts, ribbed bamboo awning hoops & stern sculling oar (摇橹)
    for ox in (-1.2, 0.0, 1.2):
        sb.add_box("warm_wood", 0.22, 1.48, 0.10, center=(ox, 0, 0.36))
    sb.add_cylinder("warm_wood", 0.05, 0.03, 3.2, segments=6, center=(-3.2, 0.42, 0.45),
                    rot_euler=(0.15, 1.35, 0.18))
    sb.add_box("warm_wood", 0.85, 0.22, 0.06, center=(-4.6, 0.58, 0.12), rot_euler=(0.1, 0.2, 0.18))
    return sb.build_single_named_object("WoodenBoat")


def main():
    clear_scene()
    palette = create_gusu_palette()
    builders = [
        build_house_a,
        build_house_b,
        build_house_c,
        build_willow_tree,
        build_pine_tree,
        build_stone_bridge,
        build_lantern_post,
        build_wooden_boat,
    ]
    for fn in builders:
        obj = fn(palette)
        tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
        print(f"  [MODULAR] {obj.name}: {tris} tris, {len(obj.data.materials)} mats")
    export_glb("gusu_modular_kit.glb")


if __name__ == "__main__":
    main()
