"""Comprehensive verification & clearance audit for all 6 Modern Jinji Lake GLB assets."""
import os
import sys
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modern_common import clear_scene

MODEL_DIR = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models"
FILES = [
    "gate_of_orient.glb",
    "ligongdi.glb",
    "moca_eye_of_suzhou.glb",
    "arts_centre_moon.glb",
    "suzhou_ifs.glb",
    "modern_cbd_kit.glb",
]


def check_clearance(mesh_objs, box_min, box_max, label):
    """Verify ZERO mesh vertices/face-centers fall inside the navigable clearance corridor."""
    hits = 0
    for obj in mesh_objs:
        mesh = obj.data
        mw = obj.matrix_world
        for poly in mesh.polygons:
            c = mw @ poly.center
            if (
                box_min[0] <= c.x <= box_max[0]
                and box_min[1] <= c.y <= box_max[1]
                and box_min[2] <= c.z <= box_max[2]
            ):
                hits += 1
    status = "PASS (0 obstructions)" if hits == 0 else f"FAIL ({hits} face centers inside clearance box!)"
    print(f"  [CLEARANCE] {label}: {status}")
    return hits == 0


def audit_all():
    all_ok = True
    for fname in FILES:
        fpath = os.path.join(MODEL_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[ERROR] Missing {fpath}")
            all_ok = False
            continue
        size_bytes = os.path.getsize(fpath)
        size_kb = size_bytes / 1024.0
        size_mb = size_kb / 1024.0
        clear_scene()
        bpy.ops.import_scene.gltf(filepath=fpath)

        total_tris = 0
        mesh_objs = []
        min_v = Vector((1e9, 1e9, 1e9))
        max_v = Vector((-1e9, -1e9, -1e9))
        emissive_mats = set()

        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                mesh_objs.append(obj)
                obj.data.calc_loop_triangles()
                tris = len(obj.data.loop_triangles)
                total_tris += tris
                for m in obj.data.materials:
                    if m and "Emissive_" in m.name:
                        emissive_mats.add(m.name)
                for corner in obj.bound_box:
                    wc = obj.matrix_world @ Vector(corner)
                    min_v.x = min(min_v.x, wc.x)
                    min_v.y = min(min_v.y, wc.y)
                    min_v.z = min(min_v.z, wc.z)
                    max_v.x = max(max_v.x, wc.x)
                    max_v.y = max(max_v.y, wc.y)
                    max_v.z = max(max_v.z, wc.z)

        print(f"\n=== AUDIT: {fname} ===")
        print(f"  Size       : {size_kb:.1f} KB ({size_mb:.2f} MB) | Budget < 3.5MB: {'OK' if size_mb < 3.5 else 'OVER'}")
        print(f"  Triangles  : {total_tris:,}")
        print(f"  BBox (Z-up): X[{min_v.x:.1f}, {max_v.x:.1f}] Y[{min_v.y:.1f}, {max_v.y:.1f}] Z[{min_v.z:.1f}, {max_v.z:.1f}]")
        print(f"  BBox (Y-up): X[{min_v.x:.1f}, {max_v.x:.1f}] Y[{min_v.z:.1f}, {max_v.z:.1f}] Z[{-max_v.y:.1f}, {-min_v.y:.1f}]")
        print(f"  Emissives  : {sorted(emissive_mats)}")
        print(f"  Nodes      : {[(o.name, o.type, tuple(round(c, 2) for c in o.matrix_world.translation)) for o in bpy.context.scene.objects]}")

        if fname == "gate_of_orient.glb":
            # Arch opening along X, clear width >= 64m (Y in [-32, +32]), clear Z in [30, 178] and center [30, 215]
            ok1 = check_clearance(mesh_objs, (-30.0, -32.0, 30.0), (30.0, 32.0, 178.0), "Gate Main Arch (64m wide x 30..178m)")
            ok2 = check_clearance(mesh_objs, (-30.0, -14.0, 30.0), (30.0, 14.0, 215.0), "Gate Upper Arch Crown (28m wide x 30..215m)")
            all_ok = all_ok and ok1 and ok2

        if fname == "ligongdi.glb":
            # Bridge arch opening along Y, clear width >= 20m (X in [-10, +10]), clear height >= 12m (Z in [0.5, 12.0])
            ok = check_clearance(mesh_objs, (-12.0, -10.0, 0.5), (12.0, 10.0, 12.5), "Ligongdi Arch Bridge (24m wide x 12.5m high)")
            all_ok = all_ok and ok

        if fname == "moca_eye_of_suzhou.glb":
            rotor = bpy.data.objects.get("FerrisWheelRotor")
            if rotor is None:
                print("  [ERROR] FerrisWheelRotor node NOT FOUND!")
                all_ok = False
            else:
                loc = rotor.matrix_world.translation
                print(f"  [ROTOR VERIFY] FerrisWheelRotor world loc (Blender Z-up)=({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}) -> Three.js Y-up=({loc.x:.2f}, {loc.z:.2f}, {-loc.y:.2f})")
                if abs(loc.x - 45.0) > 0.01 or abs(loc.y - 0.0) > 0.01 or abs(loc.z - 68.0) > 0.01:
                    print("  [ERROR] FerrisWheelRotor origin mismatch!")
                    all_ok = False

        if fname == "modern_cbd_kit.glb":
            expected = {"TowerA", "TowerB", "TowerC", "TowerD", "ModernLamp", "YachtBoat", "ParkTree"}
            found = {}
            for o in mesh_objs:
                o.data.calc_loop_triangles()
                found[o.name] = (len(o.data.loop_triangles), tuple(round(c, 2) for c in o.matrix_world.translation))
            print(f"  [KIT PARTS]: {found}")
            missing = expected - set(found.keys())
            if missing:
                print(f"  [ERROR] Missing kit parts: {missing}")
                all_ok = False

    print(f"\n=== FINAL AUDIT STATUS: {'ALL PASS' if all_ok else 'FAILED'} ===")
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    audit_all()
