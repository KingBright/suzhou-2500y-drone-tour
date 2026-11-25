"""
Re-import sanity check for all 6 Act II Gusu GLB assets in Blender 5.2.2 LTS.
Reports exact file sizes, mesh counts, triangle counts, bounding boxes (in both
Blender Z-up and Three.js Y-up), material names, emissive tags, and modular kit nodes.
"""
import os
import bpy
from mathutils import Vector

MODEL_DIR = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models"
FILES = [
    "wangshi_twin_pagodas.glb",
    "beisi_pingjiang.glb",
    "shizilin_garden.glb",
    "humble_admin_garden.glb",
    "suzhou_museum.glb",
    "gusu_modular_kit.glb",
]


def inspect_glb(filename):
    path = os.path.join(MODEL_DIR, filename)
    assert os.path.exists(path), f"MISSING: {path}"
    size_bytes = os.path.getsize(path)
    assert size_bytes > 1000, f"EMPTY: {path}"

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)

    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    total_tris = 0
    min_v = Vector((1e9, 1e9, 1e9))
    max_v = Vector((-1e9, -1e9, -1e9))
    mat_names = set()
    node_report = []

    for obj in meshes:
        obj_tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
        total_tris += obj_tris
        for m in obj.data.materials:
            if m:
                mat_names.add(m.name)
        o_min = Vector((1e9, 1e9, 1e9))
        o_max = Vector((-1e9, -1e9, -1e9))
        for corner in obj.bound_box:
            wc = obj.matrix_world @ Vector(corner)
            for axis in range(3):
                min_v[axis] = min(min_v[axis], wc[axis])
                max_v[axis] = max(max_v[axis], wc[axis])
                o_min[axis] = min(o_min[axis], wc[axis])
                o_max[axis] = max(o_max[axis], wc[axis])
        node_report.append((obj.name, obj_tris, o_min, o_max))

    emissives = sorted([m for m in mat_names if "Emissive_" in m])
    # Convert Blender Z-up bbox to Three.js Y-up: X_t=X_b, Y_t=Z_b, Z_t=-Y_b
    tx0, tx1 = min_v.x, max_v.x
    ty0, ty1 = min_v.z, max_v.z
    tz0, tz1 = -max_v.y, -min_v.y

    print(f"=== {filename} ===")
    print(f"  Size: {size_bytes / 1024:.1f} KB ({size_bytes / (1024*1024):.2f} MB)")
    print(f"  Meshes: {len(meshes)} | Tris: {total_tris}")
    print(f"  BBox (Three.js Y-up): X[{tx0:.1f}, {tx1:.1f}] Y[{ty0:.1f}, {ty1:.1f}] Z[{tz0:.1f}, {tz1:.1f}] "
          f"(W={tx1-tx0:.1f}m, H={ty1-ty0:.1f}m, D={tz1-tz0:.1f}m)")
    print(f"  Emissive Mats ({len(emissives)}): {emissives}")
    if filename == "gusu_modular_kit.glb":
        print("  Top-level modular mesh nodes:")
        for name, tris, o_min, o_max in sorted(node_report):
            print(f"    - {name}: {tris} tris | Three.js Y-up "
                  f"X[{o_min.x:.1f},{o_max.x:.1f}] Y[{o_min.z:.1f},{o_max.z:.1f}] Z[{-o_max.y:.1f},{-o_min.y:.1f}]")


def main():
    for fn in FILES:
        inspect_glb(fn)
    print("\nALL 6 GUSU GLB ASSETS PASSED RE-IMPORT SANITY CHECK!")


if __name__ == "__main__":
    main()
