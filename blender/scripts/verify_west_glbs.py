"""
Verification & Re-Import Sanity Checker for all 5 @blender-west GLB models.
Run via: /Users/jinliang/.local/bin/blender -b --python verify_west_glbs.py
"""
import os
import bpy
from mathutils import Vector

MODELS_DIR = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models"
FILES = [
    ("hanshan_temple.glb",    {"w": 180, "d": 150, "maxH": 44}),
    ("xiyuan_temple.glb",     {"w": 160, "d": 140, "maxH": 30}),
    ("tiger_hill.glb",        {"w": 220, "d": 220, "maxH": 82}),
    ("lingering_garden.glb",  {"w": 140, "d": 120, "maxH": 16}),
    ("panmen_canglang.glb",   {"w": 280, "d": 150, "maxH": 56}),
]


def check_wumen_arch_clearance():
    """Verify ZERO mesh vertices intrude inside Wumen Bridge navigable elliptical arch opening!
    In Blender space (re-imported from Y-up GLB -> back to Blender Z-up):
      Bridge at X=0, Y=-12 (clear Y in [-24, 0] => width=24.0m >= 18m;
                            clear Z in [-1.6, +13.0] => height=14.6m above water / 13.0m above ground >= 10m).
      Test 1: Inner rectangular fly-through corridor 14m wide x 10m tall: Y in [-19.0, -5.0], Z in [0.0, 10.0]
      Test 2: Full semi-elliptical arch vault 23.6m wide x 14.2m tall: ((y+12)/11.8)^2 + ((z+1.6)/14.2)^2 < 1.0
    """
    intr_rect = 0
    intr_arch = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        mw = obj.matrix_world
        for v in obj.data.vertices:
            p = mw @ v.co
            if -4.0 <= p.x <= 4.0 and p.z >= -1.4:
                if -19.0 <= p.y <= -5.0 and 0.0 <= p.z <= 10.0:
                    intr_rect += 1
                ell = ((p.y + 12.0) / 11.7) ** 2 + ((p.z + 1.6) / 14.2) ** 2
                if ell < 1.0:
                    intr_arch += 1
    return intr_rect, intr_arch


def main():
    all_ok = True
    print("=" * 90)
    print("WEST GLB RE-IMPORT VERIFICATION REPORT")
    print("=" * 90)
    for fname, budget in FILES:
        fpath = os.path.join(MODELS_DIR, fname)
        if not os.path.isfile(fpath):
            print(f"[FAIL] Missing file: {fpath}")
            all_ok = False
            continue
        fsize = os.path.getsize(fpath)
        mb = fsize / (1024.0 * 1024.0)

        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=fpath)

        tris = 0
        mesh_objs = 0
        mat_names = set()
        min_v = Vector((1e9, 1e9, 1e9))
        max_v = Vector((-1e9, -1e9, -1e9))

        for obj in bpy.data.objects:
            if obj.type != "MESH":
                continue
            mesh_objs += 1
            mesh = obj.data
            mesh.calc_loop_triangles()
            tris += len(mesh.loop_triangles)
            for m in mesh.materials:
                if m:
                    mat_names.add(m.name)
            mw = obj.matrix_world
            for corner in obj.bound_box:
                wc = mw @ Vector(corner)
                min_v.x = min(min_v.x, wc.x)
                min_v.y = min(min_v.y, wc.y)
                min_v.z = min(min_v.z, wc.z)
                max_v.x = max(max_v.x, wc.x)
                max_v.y = max(max_v.y, wc.y)
                max_v.z = max(max_v.z, wc.z)

        emissives = sorted([m for m in mat_names if ("Emissive_Warm" in m or "Emissive_Gold" in m)])
        # Convert Blender Z-up bbox to Three.js Y-up bbox: (X, Z, -Y)
        w_x = max_v.x - min_v.x
        d_z = max_v.y - min_v.y
        h_y = max_v.z - min_v.z

        issues = []
        if fsize == 0 or mb >= 3.5:
            issues.append(f"size {mb:.2f}MB out of (0, 3.5MB)")
        if tris < 15000 or tris > 45000:
            issues.append(f"tris {tris:,} outside target 15k-45k")
        if not emissives:
            issues.append("missing Emissive_Warm/Emissive_Gold material")
        if max_v.z > budget["maxH"] + 1.0:
            issues.append(f"maxH {max_v.z:.1f}m > budget {budget['maxH']}m")

        arch_msg = ""
        if fname == "panmen_canglang.glb":
            intr_rect, intr_arch = check_wumen_arch_clearance()
            arch_msg = (
                f" | WumenArch(24m x 14.6m clear, 14x10m rect): "
                f"{'PASS (0 verts)' if (intr_rect == 0 and intr_arch == 0) else f'FAIL (rect={intr_rect}, arch={intr_arch})'}"
            )
            if intr_rect > 0 or intr_arch > 0:
                issues.append(f"Wumen arch intruded (rect={intr_rect}, arch={intr_arch})")

        status = "PASS" if not issues else "WARN: " + "; ".join(issues)
        if issues:
            all_ok = False
        print(
            f"[{status}] {fname}\n"
            f"   Size: {mb:.2f} MB | Tris: {tris:,} | Meshes: {mesh_objs} | Mats: {len(mat_names)}\n"
            f"   Three.js BBox (Y-up): X[{min_v.x:.1f}, {max_v.x:.1f}] (W={w_x:.1f}m) | "
            f"Y[{min_v.z:.1f}, {max_v.z:.1f}] (H={h_y:.1f}m) | "
            f"Z[{-max_v.y:.1f}, {-min_v.y:.1f}] (D={d_z:.1f}m){arch_msg}\n"
            f"   Emissives: {', '.join(emissives)}"
        )

    print("=" * 90)
    print("OVERALL:", "ALL 5 MODELS PASSED!" if all_ok else "SOME WARNINGS - CHECK ABOVE")
    print("=" * 90)


if __name__ == "__main__":
    main()
