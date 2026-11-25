"""Shared Blender 5.2 LTS utilities for Act III & IV Modern Jinji Lake landmarks."""
import math
import os
import bpy
import bmesh
from mathutils import Vector, Matrix


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def srgb_to_linear(c):
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def hex_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip("#")
    r = srgb_to_linear(int(h[0:2], 16) / 255.0)
    g = srgb_to_linear(int(h[2:4], 16) / 255.0)
    b = srgb_to_linear(int(h[4:6], 16) / 255.0)
    return (r, g, b, alpha)


def make_mat(
    name,
    base_color=(0.5, 0.5, 0.5, 1.0),
    metallic=0.0,
    roughness=0.5,
    emission_color=None,
    emission_strength=0.0,
    alpha=1.0,
):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = None
    for node in nt.nodes:
        if node.type == "BSDF_PRINCIPLED":
            bsdf = node
            break
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")

    if isinstance(base_color, str):
        bc = hex_rgba(base_color, alpha)
    else:
        bc = base_color if len(base_color) == 4 else (*base_color, alpha)
    bsdf.inputs["Base Color"].default_value = bc
    bsdf.inputs["Metallic"].default_value = float(metallic)
    bsdf.inputs["Roughness"].default_value = float(roughness)
    bsdf.inputs["Alpha"].default_value = float(alpha)

    if emission_color is not None and emission_strength > 0.0:
        if isinstance(emission_color, str):
            ec = hex_rgba(emission_color, 1.0)
        else:
            ec = emission_color if len(emission_color) == 4 else (*emission_color, 1.0)
        bsdf.inputs["Emission Color"].default_value = ec
        bsdf.inputs["Emission Strength"].default_value = float(emission_strength)
    return mat


def make_standard_modern_mats():
    """Return a shared dictionary of PBR + Emissive materials following naming conventions."""
    return {
        "glass_dark": make_mat("Glass_ModernDark", "#1b334d", metallic=0.78, roughness=0.12),
        "glass_blue": make_mat("Glass_ModernBlue", "#285073", metallic=0.75, roughness=0.14),
        "glass_silver": make_mat("Glass_ModernSilver", "#5d7b93", metallic=0.80, roughness=0.15),
        "glass_warm": make_mat("Glass_WarmAtrium", "#3d3328", metallic=0.45, roughness=0.20,
                               emission_color="#ffba66", emission_strength=1.2),
        "metal_silver": make_mat("Metal_BrushedSilver", "#c7cfd9", metallic=0.88, roughness=0.24),
        "metal_champagne": make_mat("Metal_Champagne", "#d6c3a5", metallic=0.84, roughness=0.26),
        "metal_dark": make_mat("Metal_DarkSteel", "#2a3038", metallic=0.82, roughness=0.32),
        "metal_white": make_mat("Metal_WhiteSteel", "#eef2f6", metallic=0.35, roughness=0.28),
        "wall_white": make_mat("Wall_WhitePlaster", "#e8e6e0", metallic=0.0, roughness=0.78),
        "wall_cream": make_mat("Wall_WarmStone", "#d4c8b4", metallic=0.0, roughness=0.75),
        "roof_slate": make_mat("Roof_DarkSlate", "#2c323b", metallic=0.12, roughness=0.62),
        "roof_terracotta": make_mat("Roof_Terracotta", "#8a4232", metallic=0.05, roughness=0.68),
        "stone_granite": make_mat("Stone_PlazaGranite", "#5a6068", metallic=0.05, roughness=0.68),
        "stone_light": make_mat("Stone_LightPaving", "#8e949c", metallic=0.04, roughness=0.70),
        "wood_deck": make_mat("Wood_Boardwalk", "#7a5234", metallic=0.0, roughness=0.72),
        "foliage_green": make_mat("Foliage_ParkGreen", "#2e5c36", metallic=0.0, roughness=0.82),
        "foliage_light": make_mat("Foliage_WillowGreen", "#467a44", metallic=0.0, roughness=0.80),
        "trunk_bark": make_mat("Wood_TreeTrunk", "#4a3829", metallic=0.0, roughness=0.90),
        "water_pool": make_mat("Water_ReflectPool", "#16354a", metallic=0.30, roughness=0.08),
        # Strictly named Emissive materials for dynamic Three.js time-of-day scaling
        "em_warm": make_mat("Emissive_Warm", "#ffcf8c", metallic=0.0, roughness=0.30,
                            emission_color="#ffba66", emission_strength=3.6),
        "em_gold": make_mat("Emissive_Gold", "#ffe4a8", metallic=0.1, roughness=0.22,
                            emission_color="#ffd98a", emission_strength=4.2),
        "em_cyan": make_mat("Emissive_Cyan", "#7aeaff", metallic=0.1, roughness=0.20,
                            emission_color="#4de2ff", emission_strength=4.5),
        "em_accent": make_mat("Emissive_Accent", "#ff8ad8", metallic=0.1, roughness=0.22,
                              emission_color="#ff5cc8", emission_strength=4.2),
    }


class MeshBuilder:
    """Fast multi-material BMesh builder that compiles into a single low-draw-call Object."""

    def __init__(self, name, materials):
        self.name = name
        self.materials = list(materials)
        self.mat_index = {m.name: i for i, m in enumerate(self.materials)}
        self.bm = bmesh.new()

    def idx(self, mat):
        name = mat.name if isinstance(mat, bpy.types.Material) else mat
        if name not in self.mat_index:
            if isinstance(mat, bpy.types.Material):
                self.mat_index[name] = len(self.materials)
                self.materials.append(mat)
            else:
                raise KeyError(f"Unknown material {name}")
        return self.mat_index[name]

    def _tag_faces(self, faces, mat, smooth=False):
        mi = self.idx(mat)
        for f in faces:
            f.material_index = mi
            f.smooth = smooth

    def add_box(self, center, size, mat, rot_euler=(0.0, 0.0, 0.0), smooth=False):
        """Add an axis-aligned or rotated box centered at `center` with dimensions `size=(sx, sy, sz)`."""
        sx, sy, sz = size
        m_scale = Matrix.Diagonal((sx, sy, sz, 1.0))
        m_rot = Matrix.Identity(4)
        if any(abs(a) > 1e-6 for a in rot_euler):
            rx, ry, rz = rot_euler
            m_rot = (
                Matrix.Rotation(rz, 4, "Z")
                @ Matrix.Rotation(ry, 4, "Y")
                @ Matrix.Rotation(rx, 4, "X")
            )
        m_trans = Matrix.Translation(Vector(center))
        mat4 = m_trans @ m_rot @ m_scale
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=mat4)
        verts = set(res["verts"])
        faces = {f for v in verts for f in v.link_faces if all(fv in verts for fv in f.verts)}
        self._tag_faces(faces, mat, smooth=smooth)
        return faces

    def add_box_minmax(self, x0, x1, y0, y1, z0, z1, mat, smooth=False):
        cx = 0.5 * (x0 + x1)
        cy = 0.5 * (y0 + y1)
        cz = 0.5 * (z0 + z1)
        return self.add_box((cx, cy, cz), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mat, smooth=smooth)

    def add_cylinder(
        self,
        center,
        radius_bottom,
        radius_top,
        height,
        mat,
        segments=16,
        rot_euler=(0.0, 0.0, 0.0),
        cap_ends=True,
        smooth=True,
    ):
        m_rot = Matrix.Identity(4)
        if any(abs(a) > 1e-6 for a in rot_euler):
            rx, ry, rz = rot_euler
            m_rot = (
                Matrix.Rotation(rz, 4, "Z")
                @ Matrix.Rotation(ry, 4, "Y")
                @ Matrix.Rotation(rx, 4, "X")
            )
        mat4 = Matrix.Translation(Vector(center)) @ m_rot
        res = bmesh.ops.create_cone(
            self.bm,
            cap_ends=cap_ends,
            cap_tris=False,
            segments=segments,
            radius1=radius_bottom,
            radius2=radius_top,
            depth=height,
            matrix=mat4,
        )
        verts = set(res["verts"])
        faces = {f for v in verts for f in v.link_faces if all(fv in verts for fv in f.verts)}
        self._tag_faces(faces, mat, smooth=smooth)
        return faces

    def add_tube(self, p0, p1, radius, mat, segments=8, radius2=None, cap_ends=True, smooth=True):
        """Add a cylindrical strut/tube from point p0 to p1."""
        v0 = Vector(p0)
        v1 = Vector(p1)
        diff = v1 - v0
        length = diff.length
        if length < 1e-5:
            return set()
        mid = 0.5 * (v0 + v1)
        z_axis = Vector((0.0, 0.0, 1.0))
        quat = z_axis.rotation_difference(diff.normalized())
        mat4 = Matrix.Translation(mid) @ quat.to_matrix().to_4x4()
        r2 = radius if radius2 is None else radius2
        res = bmesh.ops.create_cone(
            self.bm,
            cap_ends=cap_ends,
            cap_tris=False,
            segments=segments,
            radius1=radius,
            radius2=r2,
            depth=length,
            matrix=mat4,
        )
        verts = set(res["verts"])
        faces = {f for v in verts for f in v.link_faces if all(fv in verts for fv in f.verts)}
        self._tag_faces(faces, mat, smooth=smooth)
        return faces

    def add_icosphere(self, center, radius, mat, subdivisions=2, scale=(1.0, 1.0, 1.0), smooth=True):
        mat4 = Matrix.Translation(Vector(center)) @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
        res = bmesh.ops.create_icosphere(
            self.bm, subdivisions=subdivisions, radius=radius, matrix=mat4
        )
        verts = set(res["verts"])
        faces = {f for v in verts for f in v.link_faces if all(fv in verts for fv in f.verts)}
        self._tag_faces(faces, mat, smooth=smooth)
        return faces

    def add_loft(self, rings, mat, closed_loop=True, cap_start=False, cap_end=False, smooth=True):
        """Loft a list of vertex rings (each ring is a list of (x,y,z) of identical length)."""
        if len(rings) < 2:
            return []
        bm_rings = [[self.bm.verts.new(Vector(pt)) for pt in ring] for ring in rings]
        n = len(rings[0])
        mi = self.idx(mat)
        created = []
        for r_i in range(len(bm_rings) - 1):
            r0 = bm_rings[r_i]
            r1 = bm_rings[r_i + 1]
            count = n if closed_loop else n - 1
            for j in range(count):
                jn = (j + 1) % n
                try:
                    f = self.bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
                    f.material_index = mi
                    f.smooth = smooth
                    created.append(f)
                except ValueError:
                    pass
        if cap_start and len(bm_rings[0]) >= 3:
            try:
                f = self.bm.faces.new(list(reversed(bm_rings[0])))
                f.material_index = mi
                f.smooth = False
                created.append(f)
            except ValueError:
                pass
        if cap_end and len(bm_rings[-1]) >= 3:
            try:
                f = self.bm.faces.new(bm_rings[-1])
                f.material_index = mi
                f.smooth = False
                created.append(f)
            except ValueError:
                pass
        return created

    def add_ribbon_strip(self, pts, half_width, thickness, mat, up_vec=(0.0, 0.0, 1.0), smooth=True):
        """Sweep a rectangular ribbon along a 3D polyline `pts`."""
        if len(pts) < 2:
            return
        up = Vector(up_vec).normalized()
        rings = []
        for i, p in enumerate(pts):
            pv = Vector(p)
            if i == 0:
                tang = (Vector(pts[1]) - pv).normalized()
            elif i == len(pts) - 1:
                tang = (pv - Vector(pts[-2])).normalized()
            else:
                tang = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
            side = tang.cross(up)
            if side.length < 1e-4:
                side = Vector((1.0, 0.0, 0.0))
            else:
                side.normalize()
            local_up = side.cross(tang).normalized()
            hw = half_width[i] if isinstance(half_width, (list, tuple)) else half_width
            ht = 0.5 * (thickness[i] if isinstance(thickness, (list, tuple)) else thickness)
            ring = [
                pv - side * hw - local_up * ht,
                pv + side * hw - local_up * ht,
                pv + side * hw + local_up * ht,
                pv - side * hw + local_up * ht,
            ]
            rings.append(ring)
        self.add_loft(rings, mat, closed_loop=True, cap_start=True, cap_end=True, smooth=smooth)

    def add_polyline_tubes(self, pts, radius, mat, segments=6, closed=False, smooth=True):
        count = len(pts) if closed else len(pts) - 1
        for i in range(count):
            self.add_tube(pts[i], pts[(i + 1) % len(pts)], radius, mat, segments=segments, smooth=smooth)

    def add_pitched_roof_building(
        self,
        center_xy,
        width_x,
        depth_y,
        z_base,
        wall_h,
        roof_h,
        wall_mat,
        roof_mat,
        glass_mat=None,
        emissive_mat=None,
        rot_z=0.0,
        eave_overhang=1.2,
    ):
        """Build a clean modern neo-Suzhou or European gable building at center_xy."""
        cx, cy = center_xy
        rot = Matrix.Rotation(rot_z, 4, "Z")
        base_m = Matrix.Translation(Vector((cx, cy, z_base))) @ rot

        def xf(pt):
            return base_m @ Vector(pt)

        # Main wall volume
        hx, hy = 0.5 * width_x, 0.5 * depth_y
        wall_bot = [xf((-hx, -hy, 0)), xf((hx, -hy, 0)), xf((hx, hy, 0)), xf((-hx, hy, 0))]
        wall_top = [xf((-hx, -hy, wall_h)), xf((hx, -hy, wall_h)), xf((hx, hy, wall_h)), xf((-hx, hy, wall_h))]
        self.add_loft([wall_bot, wall_top], wall_mat, closed_loop=True, cap_start=True, cap_end=True, smooth=False)

        # Glowing window band on long faces
        if glass_mat is not None or emissive_mat is not None:
            gmat = emissive_mat if emissive_mat is not None else glass_mat
            w_z0, w_z1 = wall_h * 0.16, wall_h * 0.78
            for sy in (-1.0, 1.0):
                y_face = sy * (hy + 0.08)
                n_bays = max(2, int(width_x / 4.2))
                bay_w = (width_x - 2.0) / n_bays
                for b in range(n_bays):
                    bx0 = -hx + 1.0 + b * bay_w + 0.35
                    bx1 = -hx + 1.0 + (b + 1) * bay_w - 0.35
                    if bx1 <= bx0:
                        continue
                    pts = [
                        xf((bx0, y_face, w_z0)),
                        xf((bx1, y_face, w_z0)),
                        xf((bx1, y_face, w_z1)),
                        xf((bx0, y_face, w_z1)),
                    ]
                    if sy < 0:
                        pts.reverse()
                    verts = [self.bm.verts.new(p) for p in pts]
                    try:
                        f = self.bm.faces.new(verts)
                        f.material_index = self.idx(gmat)
                        f.smooth = False
                    except ValueError:
                        pass

        # Gable roof with overhang and slight upturned eave flair
        rx = hx + eave_overhang
        ry = hy + eave_overhang
        z_eave = wall_h - 0.25
        z_ridge = wall_h + roof_h
        # Two roof slopes + gable triangles via a clean 6-vertex prism
        prof_l = [
            xf((-rx, -ry, z_eave)),
            xf((-rx, 0.0, z_ridge)),
            xf((-rx, ry, z_eave)),
            xf((-rx, ry - 0.3, z_eave - 0.35)),
            xf((-rx, 0.0, z_ridge - 0.45)),
            xf((-rx, -ry + 0.3, z_eave - 0.35)),
        ]
        prof_r = [
            xf((rx, -ry, z_eave)),
            xf((rx, 0.0, z_ridge)),
            xf((rx, ry, z_eave)),
            xf((rx, ry - 0.3, z_eave - 0.35)),
            xf((rx, 0.0, z_ridge - 0.45)),
            xf((rx, -ry + 0.3, z_eave - 0.35)),
        ]
        self.add_loft([prof_l, prof_r], roof_mat, closed_loop=True, cap_start=True, cap_end=True, smooth=False)

        # Gable end fill walls
        for sx in (-1.0, 1.0):
            gx = sx * (hx - 0.05)
            g_pts = [xf((gx, -hy, wall_h)), xf((gx, hy, wall_h)), xf((gx, 0.0, z_ridge - 0.35))]
            if sx < 0:
                g_pts.reverse()
            try:
                f = self.bm.faces.new([self.bm.verts.new(p) for p in g_pts])
                f.material_index = self.idx(wall_mat)
                f.smooth = False
            except ValueError:
                pass

        # Under-eave warm accent glow strip
        if emissive_mat is not None:
            for sy in (-1.0, 1.0):
                p0 = xf((-rx + 0.4, sy * (hy + 0.45), wall_h - 0.28))
                p1 = xf((rx - 0.4, sy * (hy + 0.45), wall_h - 0.28))
                self.add_tube(p0, p1, 0.14, emissive_mat, segments=4, smooth=False)

    def build(self, origin=(0.0, 0.0, 0.0), parent=None):
        """Finalize BMesh, fix normals, attach materials, and link object to scene."""
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        mesh = bpy.data.meshes.new(self.name + "_Mesh")
        self.bm.to_mesh(mesh)
        self.bm.free()

        for m in self.materials:
            mesh.materials.append(m)

        obj = bpy.data.objects.new(self.name, mesh)
        obj.location = Vector(origin)
        bpy.context.collection.objects.link(obj)
        if parent is not None:
            obj.parent = parent
        return obj


def export_glb(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_materials="EXPORT",
        export_yup=True,
    )
    size_kb = os.path.getsize(filepath) / 1024.0
    print(f"[EXPORT OK] {filepath} ({size_kb:.1f} KB)")
    return size_kb


def verify_glb(filepath):
    """Re-import exported GLB into a clean scene and report exact mesh stats, nodes, and bbox."""
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=filepath)
    total_tris = 0
    meshes = []
    nodes = []
    min_v = Vector((1e9, 1e9, 1e9))
    max_v = Vector((-1e9, -1e9, -1e9))
    mats = set()

    for obj in bpy.context.scene.objects:
        nodes.append((obj.name, obj.type, tuple(round(c, 2) for c in obj.matrix_world.translation)))
        if obj.type == "MESH":
            mesh = obj.data
            mesh.calc_loop_triangles()
            tris = len(mesh.loop_triangles)
            total_tris += tris
            meshes.append((obj.name, tris, len(mesh.materials)))
            for m in mesh.materials:
                if m:
                    mats.add(m.name)
            for corner in obj.bound_box:
                wc = obj.matrix_world @ Vector(corner)
                min_v.x = min(min_v.x, wc.x)
                min_v.y = min(min_v.y, wc.y)
                min_v.z = min(min_v.z, wc.z)
                max_v.x = max(max_v.x, wc.x)
                max_v.y = max(max_v.y, wc.y)
                max_v.z = max(max_v.z, wc.z)

    size_kb = os.path.getsize(filepath) / 1024.0
    print(f"=== VERIFY {os.path.basename(filepath)} ===")
    print(f"  File size : {size_kb:.1f} KB ({size_kb / 1024.0:.2f} MB)")
    print(f"  Total tris: {total_tris:,}")
    print(f"  BBox (Blender Z-up): min=({min_v.x:.1f}, {min_v.y:.1f}, {min_v.z:.1f}) max=({max_v.x:.1f}, {max_v.y:.1f}, {max_v.z:.1f})")
    print(f"  Materials : {sorted(mats)}")
    print(f"  Mesh objs : {meshes}")
    return {
        "file": os.path.basename(filepath),
        "size_kb": size_kb,
        "tris": total_tris,
        "bbox_min": tuple(round(c, 2) for c in min_v),
        "bbox_max": tuple(round(c, 2) for c in max_v),
        "nodes": nodes,
        "materials": sorted(mats),
    }
