"""
Quick headless EEVEE preview renderer for all 5 @blender-west GLBs from their exact heroView cameras.
Outputs 800x480 PNGs into scratch folder so @blender-west can visually inspect every model!
"""
import math
import os
import bpy
from mathutils import Vector

MODELS_DIR = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models"
OUT_DIR = "/Users/jinliang/.gemini/antigravity/brain/004fe1d6-573d-44d5-96db-578d08bcb624/scratch/west_previews"
os.makedirs(OUT_DIR, exist_ok=True)

# Exact heroView cameras converted to Blender local Z-up coords (X, -Z_three, Y_three - 1.6)
SHOTS = [
    ("hanshan_temple.glb",   "01_hanshan.png",   (-95, -65, 28),   (5, 5, 16)),
    ("xiyuan_temple.glb",    "02a_xiyuan.png",   (-78, -72, 34),   (0, 4, 8)),
    ("tiger_hill.glb",       "02b_tigerhill.png",(95, -95, 60),    (0, 0, 44)),
    ("lingering_garden.glb", "03_lingering.png", (-65, -55, 28),   (4, 2, 6)),
    ("panmen_canglang.glb",  "04_panmen.png",    (-125, -95, 38),  (-10, 5, 20)),
]


def render_shot(glb_name, out_name, cam_pos, target_pos):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(MODELS_DIR, glb_name))

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 800
    scene.render.resolution_y = 480
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(OUT_DIR, out_name)

    # Warm golden-dusk sky & sun so silhouettes + emissives both read clearly!
    world = bpy.data.worlds.new("PreviewWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.14, 0.16, 0.28, 1.0)
        bg.inputs["Strength"].default_value = 0.7

    # Warm golden sunset key sun
    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = 3.2
    sun_data.color = (1.0, 0.80, 0.58)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(58), math.radians(12), math.radians(-35))

    # Camera pointing at target
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 30.0
    cam_data.clip_end = 1000.0
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector(cam_pos)
    direction = Vector(target_pos) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam_obj

    bpy.ops.render.render(write_still=True)
    print(f"[PREVIEW OK] {out_name}")


def main():
    for args in SHOTS:
        render_shot(*args)


if __name__ == "__main__":
    main()
