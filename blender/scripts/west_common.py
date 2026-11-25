"""
Shared procedural Suzhou Jiangnan architectural geometry & Blender 5.2 GLB export toolkit
for Act I & West/SW Ancient Suzhou landmarks (@blender-west).
"""

import math
import os
import random
import bpy
import bmesh
from mathutils import Matrix, Vector, Euler


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


MATERIAL_SPECS = {
    # Architectural plaster & walls
    "Mat_WhiteWall":      {"color": "#ebe6da", "roughness": 0.86, "metallic": 0.0},
    "Mat_TempleYellow":   {"color": "#d89c32", "roughness": 0.78, "metallic": 0.0},
    "Mat_TempleWallTrim": {"color": "#b87a24", "roughness": 0.80, "metallic": 0.0},
    # Roof tiles & ridges
    "Mat_DarkTile":       {"color": "#252b34", "roughness": 0.56, "metallic": 0.06},
    "Mat_TileRidge":      {"color": "#4f5662", "roughness": 0.64, "metallic": 0.04},
    "Mat_GoldTrim":       {"color": "#dca83b", "roughness": 0.28, "metallic": 0.82},
    # Wood & lacquer
    "Mat_CrimsonWood":    {"color": "#822019", "roughness": 0.44, "metallic": 0.02},
    "Mat_DarkWood":       {"color": "#3a2519", "roughness": 0.62, "metallic": 0.0},
    "Mat_WarmWood":       {"color": "#825634", "roughness": 0.58, "metallic": 0.0},
    "Mat_PlaqueRed":      {"color": "#a82218", "roughness": 0.48, "metallic": 0.05},
    # Stone, brick, rock
    "Mat_GraniteLight":   {"color": "#aca89e", "roughness": 0.82, "metallic": 0.0},
    "Mat_GraniteDark":    {"color": "#585b60", "roughness": 0.78, "metallic": 0.02},
    "Mat_CityBrick":      {"color": "#64696f", "roughness": 0.88, "metallic": 0.0},
    "Mat_PagodaBrick":    {"color": "#9d6b47", "roughness": 0.84, "metallic": 0.0},
    "Mat_PagodaBrickDark":{"color": "#6e472d", "roughness": 0.86, "metallic": 0.0},
    "Mat_RuiguangBrick":  {"color": "#c6ab83", "roughness": 0.82, "metallic": 0.0},
    "Mat_TaihuRock":      {"color": "#8f8c83", "roughness": 0.86, "metallic": 0.0},
    "Mat_Bronze":         {"color": "#635a3d", "roughness": 0.36, "metallic": 0.76},
    # Landscape & foliage
    "Mat_HillEarth":      {"color": "#2f4e27", "roughness": 0.90, "metallic": 0.0},
    "Mat_Grass":          {"color": "#395d2f", "roughness": 0.88, "metallic": 0.0},
    "Mat_PineFoliage":    {"color": "#1d3d23", "roughness": 0.82, "metallic": 0.0},
    "Mat_WillowFoliage":  {"color": "#487436", "roughness": 0.78, "metallic": 0.0},
    "Mat_BambooGreen":    {"color": "#366e31", "roughness": 0.66, "metallic": 0.0},
    "Mat_BambooCulm":     {"color": "#678f46", "roughness": 0.48, "metallic": 0.0},
    "Mat_MapleRed":       {"color": "#a83322", "roughness": 0.76, "metallic": 0.0},
    "Mat_TrunkBark":      {"color": "#4a3728", "roughness": 0.90, "metallic": 0.0},
    # Pond water & lotus
    "Mat_PondWater":      {"color": "#193e3c", "roughness": 0.14, "metallic": 0.12},
    "Mat_LotusLeaf":      {"color": "#2f592f", "roughness": 0.65, "metallic": 0.0},
    # Dynamic Emissive materials (strictly tagged Emissive_Warm / Emissive_Gold for @web-engine!)
    "Emissive_Warm_Lantern": {
        "color": "#ff9e3d", "roughness": 0.35, "metallic": 0.0,
        "emission": "#ff9a38", "emission_strength": 3.2,
    },
    "Emissive_Warm_Window": {
        "color": "#f5be6e", "roughness": 0.40, "metallic": 0.0,
        "emission": "#ffba66", "emission_strength": 2.2,
    },
    "Emissive_Warm_Uplight": {
        "color": "#ffd28a", "roughness": 0.30, "metallic": 0.0,
        "emission": "#ffba66", "emission_strength": 2.8,
    },
    "Emissive_Gold_Eave": {
        "color": "#ffe08f", "roughness": 0.25, "metallic": 0.2,
        "emission": "#ffd98a", "emission_strength": 3.4,
    },
    "Emissive_Gold_Crown": {
        "color": "#ffebad", "roughness": 0.20, "metallic": 0.3,
        "emission": "#ffd98a", "emission_strength": 4.0,
    },
}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def create_material(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    spec = MATERIAL_SPECS[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = hex_rgba(spec["color"])
    bsdf.inputs["Roughness"].default_value = spec["roughness"]
    bsdf.inputs["Metallic"].default_value = spec["metallic"]
    if "emission" in spec:
        bsdf.inputs["Emission Color"].default_value = hex_rgba(spec["emission"])
        bsdf.inputs["Emission Strength"].default_value = spec["emission_strength"]
    return mat


class SuzhouBuilder:
    """High-speed BMesh scene builder with per-material indexing & low draw-call export."""

    def __init__(self, name="Landmark"):
        self.name = name
        self.bm = bmesh.new()
        self.mat_names = []
        self.mat_index = {}

    def mat_id(self, name):
        if name not in self.mat_index:
            self.mat_index[name] = len(self.mat_names)
            self.mat_names.append(name)
        return self.mat_index[name]

    def _apply_face_props(self, faces, mat_name, smooth=False):
        mid = self.mat_id(mat_name)
        for f in faces:
            f.material_index = mid
            f.smooth = smooth

    def _transform_verts(self, verts, matrix):
        for v in verts:
            v.co = matrix @ v.co

    def add_mesh_data(self, verts_coords, faces_indices, mat_name, smooth=False, matrix=None):
        verts = []
        for co in verts_coords:
            v = Vector(co)
            if matrix is not None:
                v = matrix @ v
            verts.append(self.bm.verts.new(v))
        mid = self.mat_id(mat_name)
        created_faces = []
        for fi in faces_indices:
            try:
                f = self.bm.faces.new([verts[i] for i in fi])
                f.material_index = mid
                f.smooth = smooth
                created_faces.append(f)
            except ValueError:
                pass
        return created_faces

    def box(self, cx, cy, cz, sx, sy, sz, mat_name, rot_z=0.0, rot_x=0.0, rot_y=0.0, matrix=None):
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        coords = [
            (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
            (-hx, -hy,  hz), (hx, -hy,  hz), (hx, hy,  hz), (-hx, hy,  hz),
        ]
        faces = [
            (0, 3, 2, 1), (4, 5, 6, 7),
            (0, 1, 5, 4), (1, 2, 6, 5),
            (2, 3, 7, 6), (3, 0, 4, 7),
        ]
        m = Matrix.Translation((cx, cy, cz)) @ Euler((rot_x, rot_y, rot_z), 'XYZ').to_matrix().to_4x4()
        if matrix is not None:
            m = matrix @ m
        return self.add_mesh_data(coords, faces, mat_name, smooth=False, matrix=m)

    def box_z(self, cx, cy, z0, z1, sx, sy, mat_name, rot_z=0.0, matrix=None):
        return self.box(cx, cy, 0.5 * (z0 + z1), sx, sy, z1 - z0, mat_name, rot_z=rot_z, matrix=matrix)

    def prism(self, cx, cy, z0, z1, r0, r1, sides, mat_name, rot_z=0.0,
              cap_bottom=True, cap_top=True, smooth=False, matrix=None):
        coords = []
        for i in range(sides):
            a = 2.0 * math.pi * i / sides + rot_z
            ca, sa = math.cos(a), math.sin(a)
            coords.append((cx + r0 * ca, cy + r0 * sa, z0))
        for i in range(sides):
            a = 2.0 * math.pi * i / sides + rot_z
            ca, sa = math.cos(a), math.sin(a)
            coords.append((cx + r1 * ca, cy + r1 * sa, z1))
        faces = []
        for i in range(sides):
            ni = (i + 1) % sides
            faces.append((i, ni, sides + ni, sides + i))
        if cap_bottom and r0 > 1e-4:
            faces.append(tuple(range(sides - 1, -1, -1)))
        if cap_top and r1 > 1e-4:
            faces.append(tuple(range(sides, 2 * sides)))
        return self.add_mesh_data(coords, faces, mat_name, smooth=smooth, matrix=matrix)

    def cylinder(self, cx, cy, z0, z1, r, mat_name, sides=8, smooth=True, matrix=None):
        return self.prism(cx, cy, z0, z1, r, r, sides, mat_name, smooth=smooth, matrix=matrix)

    def sphere(self, cx, cy, cz, rx, ry, rz, segs, rings, mat_name, smooth=True, matrix=None):
        coords = [(0.0, 0.0, -rz)]
        for r_i in range(1, rings):
            phi = -0.5 * math.pi + math.pi * r_i / rings
            cp, sp = math.cos(phi), math.sin(phi)
            for s_i in range(segs):
                theta = 2.0 * math.pi * s_i / segs
                coords.append((rx * cp * math.cos(theta), ry * cp * math.sin(theta), rz * sp))
        coords.append((0.0, 0.0, rz))
        top_idx = len(coords) - 1
        faces = []
        for s_i in range(segs):
            ns = (s_i + 1) % segs
            faces.append((0, 1 + ns, 1 + s_i))
        for r_i in range(rings - 2):
            row0 = 1 + r_i * segs
            row1 = row0 + segs
            for s_i in range(segs):
                ns = (s_i + 1) % segs
                faces.append((row0 + s_i, row0 + ns, row1 + ns, row1 + s_i))
        last_row = 1 + (rings - 2) * segs
        for s_i in range(segs):
            ns = (s_i + 1) % segs
            faces.append((last_row + s_i, last_row + ns, top_idx))
        m = Matrix.Translation((cx, cy, cz))
        if matrix is not None:
            m = matrix @ m
        return self.add_mesh_data(coords, faces, mat_name, smooth=smooth, matrix=m)

    def extrude_polygon(self, pts_2d, z0, z1, mat_name, cap_bottom=True, cap_top=True, matrix=None):
        n = len(pts_2d)
        # Ensure counter-clockwise winding
        area = 0.0
        for i in range(n):
            x0, y0 = pts_2d[i]
            x1, y1 = pts_2d[(i + 1) % n]
            area += x0 * y1 - x1 * y0
        pts = list(pts_2d) if area >= 0 else list(reversed(pts_2d))
        coords = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]
        faces = []
        for i in range(n):
            ni = (i + 1) % n
            faces.append((i, ni, n + ni, n + i))
        if cap_bottom:
            faces.append(tuple(range(n - 1, -1, -1)))
        if cap_top:
            faces.append(tuple(range(n, 2 * n)))
        return self.add_mesh_data(coords, faces, mat_name, smooth=False, matrix=matrix)

    # ------------------------------------------------------------------
    # Classic Suzhou Upturned Sweeping Roofs (飞檐翘角)
    # ------------------------------------------------------------------
    def add_upturned_roof(
        self, cx, cy, z_base, w, d, h,
        mat_tile="Mat_DarkTile", mat_ridge="Mat_TileRidge",
        mat_wood="Mat_DarkWood", mat_gold="Mat_GoldTrim",
        mat_eave_light="Emissive_Gold_Eave",
        overhang=1.8, flare_z=1.1, flare_xy=0.75,
        rot_z=0.0, ridge_ratio=0.52, steps=5, matrix=None,
    ):
        """
        True Jiangnan hip-and-gable / curved upturned tiled roof.
        w = ridge axis length (X), d = slope span (Y), h = roof rise.
        """
        m_local = Matrix.Translation((cx, cy, z_base)) @ Matrix.Rotation(rot_z, 4, 'Z')
        if matrix is not None:
            m_local = matrix @ m_local

        hw = w * 0.5 + overhang
        hd = d * 0.5 + overhang
        rw = max(0.2, w * 0.5 * ridge_ratio)
        rd = 0.14

        # Build concentric curved rings from eave (t=0) to ridge (t=1)
        rings = []
        for s in range(steps + 1):
            t = s / steps  # 0 at eave, 1 at ridge
            # Concave Chinese roof profile
            z_curve = h * (t ** 1.55)
            # Corner upsweep concentrated near eave (t near 0)
            corner_lift = flare_z * ((1.0 - t) ** 2.4)
            corner_flare = flare_xy * ((1.0 - t) ** 2.2)

            rx = hw * (1.0 - t) + rw * t
            ry = hd * (1.0 - t) + rd * t

            # 8 points around rectangle (corners + edge midpoints for curved eave swoop!)
            ring = [
                (-rx - corner_flare, -ry - corner_flare, z_curve + corner_lift),
                (0.0,                -ry,                z_curve),
                ( rx + corner_flare, -ry - corner_flare, z_curve + corner_lift),
                ( rx,                 0.0,               z_curve),
                ( rx + corner_flare,  ry + corner_flare, z_curve + corner_lift),
                (0.0,                 ry,                z_curve),
                (-rx - corner_flare,  ry + corner_flare, z_curve + corner_lift),
                (-rx,                 0.0,               z_curve),
            ]
            rings.append(ring)

        coords = []
        for ring in rings:
            coords.extend(ring)
        faces = []
        for s in range(steps):
            r0 = s * 8
            r1 = (s + 1) * 8
            for i in range(8):
                ni = (i + 1) % 8
                faces.append((r0 + i, r0 + ni, r1 + ni, r1 + i))
        # Top cap along ridge
        top_r = steps * 8
        faces.append((top_r + 0, top_r + 1, top_r + 2, top_r + 3, top_r + 4, top_r + 5, top_r + 6, top_r + 7))
        self.add_mesh_data(coords, faces, mat_tile, smooth=False, matrix=m_local)

        # Roof eave soffit underside (wood)
        soffit_z = -0.18
        so_coords = [
            (-hw, -hd, soffit_z), (hw, -hd, soffit_z),
            (hw, hd, soffit_z), (-hw, hd, soffit_z),
        ]
        self.add_mesh_data(so_coords, [(0, 3, 2, 1)], mat_wood, smooth=False, matrix=m_local)

        # Main central ridge (正脊) + upturned finials (吻兽)
        ridge_len = rw * 2.0 + 0.5
        self.box(0.0, 0.0, h + 0.25, ridge_len, 0.48, 0.52, mat_ridge, matrix=m_local)
        if mat_gold:
            self.box(0.0, 0.0, h + 0.56, ridge_len * 0.92, 0.22, 0.18, mat_gold, matrix=m_local)
            # End dragon finials
            for sx in (-1.0, 1.0):
                self.box(sx * (rw + 0.2), 0.0, h + 0.65, 0.55, 0.42, 0.85, mat_gold, rot_y=sx * -0.25, matrix=m_local)
            # Central jewel
            self.sphere(0.0, 0.0, h + 0.88, 0.28, 0.28, 0.36, 6, 4, mat_gold, smooth=False, matrix=m_local)

        # 4 corner hip ridges (垂脊) following the curve
        for ci in (0, 2, 4, 6):
            for s in range(steps):
                p0 = Vector(rings[s][ci])
                p1 = Vector(rings[s + 1][ci])
                mid = (p0 + p1) * 0.5 + Vector((0, 0, 0.16))
                vec = p1 - p0
                seg_len = vec.length
                if seg_len < 1e-3:
                    continue
                ang_z = math.atan2(vec.y, vec.x)
                horiz = math.hypot(vec.x, vec.y)
                ang_y = -math.atan2(vec.z, horiz)
                self.box(mid.x, mid.y, mid.z, seg_len + 0.15, 0.26, 0.28, mat_ridge,
                         rot_z=ang_z, rot_y=ang_y, matrix=m_local)

        # Optional warm golden LED eave strip tucked under the eaves
        if mat_eave_light:
            ew = w * 0.5 + overhang * 0.55
            ed = d * 0.5 + overhang * 0.55
            ez = -0.22
            st = 0.20
            self.box(0.0, -ed, ez, ew * 2.0, st, 0.16, mat_eave_light, matrix=m_local)
            self.box(0.0,  ed, ez, ew * 2.0, st, 0.16, mat_eave_light, matrix=m_local)
            self.box(-ew, 0.0, ez, st, ed * 2.0, 0.16, mat_eave_light, matrix=m_local)
            self.box( ew, 0.0, ez, st, ed * 2.0, 0.16, mat_eave_light, matrix=m_local)

    def add_polygonal_roof(
        self, cx, cy, z_base, r_inner, r_outer, h, sides=8,
        mat_tile="Mat_DarkTile", mat_ridge="Mat_TileRidge",
        mat_wood="Mat_DarkWood", mat_gold="Mat_GoldTrim",
        mat_eave_light="Emissive_Gold_Eave",
        flare_z=0.75, flare_r=0.45, rot_z=0.0, steps=4,
        finial=False, matrix=None,
    ):
        """
        Octagonal / hexagonal / square curved Chinese pavilion or pagoda eave roof.
        """
        m_local = Matrix.Translation((cx, cy, z_base)) @ Matrix.Rotation(rot_z, 4, 'Z')
        if matrix is not None:
            m_local = matrix @ m_local

        n_pts = sides * 2  # vertices + edge midpoints for crisp corner flare
        rings = []
        for s in range(steps + 1):
            t = s / steps
            z_c = h * (t ** 1.55)
            r_base = r_outer * (1.0 - t) + r_inner * t
            c_lift = flare_z * ((1.0 - t) ** 2.3)
            c_flare = flare_r * ((1.0 - t) ** 2.1)
            ring = []
            for k in range(n_pts):
                a = 2.0 * math.pi * k / n_pts
                is_corner = (k % 2 == 0)
                if is_corner:
                    rr = r_base + c_flare
                    zz = z_c + c_lift
                else:
                    # Edge midpoint lies on chord between corners
                    rr = r_base * math.cos(math.pi / sides)
                    zz = z_c
                ring.append((rr * math.cos(a), rr * math.sin(a), zz))
            rings.append(ring)

        coords = []
        for ring in rings:
            coords.extend(ring)
        faces = []
        for s in range(steps):
            r0 = s * n_pts
            r1 = (s + 1) * n_pts
            for k in range(n_pts):
                nk = (k + 1) % n_pts
                faces.append((r0 + k, r0 + nk, r1 + nk, r1 + k))
        if r_inner < 0.3:
            top_r = steps * n_pts
            faces.append(tuple(range(top_r, top_r + n_pts)))
        self.add_mesh_data(coords, faces, mat_tile, smooth=False, matrix=m_local)

        # Soffit underside
        so_r = r_outer * 0.96
        so_coords = [(so_r * math.cos(2 * math.pi * i / sides),
                      so_r * math.sin(2 * math.pi * i / sides), -0.15) for i in range(sides)]
        self.add_mesh_data(so_coords, [tuple(range(sides - 1, -1, -1))], mat_wood, smooth=False, matrix=m_local)

        # Hip ridges along corners
        for k in range(0, n_pts, 2):
            p0 = Vector(rings[0][k])
            p1 = Vector(rings[-1][k])
            mid = (p0 + p1) * 0.5 + Vector((0, 0, 0.14))
            vec = p1 - p0
            seg_len = vec.length
            if seg_len > 0.05:
                ang_z = math.atan2(vec.y, vec.x)
                ang_y = -math.atan2(vec.z, math.hypot(vec.x, vec.y))
                self.box(mid.x, mid.y, mid.z, seg_len, 0.18, 0.22, mat_ridge,
                         rot_z=ang_z, rot_y=ang_y, matrix=m_local)

        # Eave light strip ring
        if mat_eave_light:
            lr = r_outer * 0.88
            for i in range(sides):
                a0 = 2.0 * math.pi * i / sides
                a1 = 2.0 * math.pi * ((i + 1) % sides) / sides
                p0 = Vector((lr * math.cos(a0), lr * math.sin(a0), -0.18))
                p1 = Vector((lr * math.cos(a1), lr * math.sin(a1), -0.18))
                mid = (p0 + p1) * 0.5
                seg = (p1 - p0).length
                ang = math.atan2(p1.y - p0.y, p1.x - p0.x)
                self.box(mid.x, mid.y, mid.z, seg * 0.92, 0.16, 0.14, mat_eave_light, rot_z=ang, matrix=m_local)

        if finial and mat_gold:
            self.prism(0.0, 0.0, h, h + 0.55, 0.45, 0.20, sides, mat_gold, matrix=m_local)
            self.sphere(0.0, 0.0, h + 0.85, 0.28, 0.28, 0.36, 6, 4, mat_gold, smooth=False, matrix=m_local)
            self.prism(0.0, 0.0, h + 1.15, h + 1.85, 0.10, 0.02, 6, mat_gold, matrix=m_local)

    # ------------------------------------------------------------------
    # Complete Suzhou / Temple Hall
    # ------------------------------------------------------------------
    def add_hall(
        self, cx, cy, z0, w, d, wall_h=6.0, roof_h=4.6,
        double_eave=True, rot_z=0.0,
        wall_mat="Mat_TempleYellow", pillar_mat="Mat_CrimsonWood",
        roof_mat="Mat_DarkTile", ridge_mat="Mat_TileRidge",
        gold_mat="Mat_GoldTrim", window_mat="Emissive_Warm_Window",
        eave_light="Emissive_Gold_Eave", plinth_h=1.2,
        stairs_front=True, plaque=True, matrix=None,
    ):
        m = Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(rot_z, 4, 'Z')
        if matrix is not None:
            m = matrix @ m

        # Stepped granite plinth (台基)
        if plinth_h > 0.05:
            self.box_z(0, 0, -0.3, plinth_h * 0.55, w + 3.4, d + 3.4, "Mat_GraniteDark", matrix=m)
            self.box_z(0, 0, plinth_h * 0.55, plinth_h, w + 2.4, d + 2.4, "Mat_GraniteLight", matrix=m)
            if stairs_front:
                sw = min(w * 0.34, 7.5)
                for st in range(4):
                    frac = st / 4.0
                    self.box_z(0, -(d * 0.5 + 1.2 + (3 - st) * 0.55), 0.0, plinth_h * (st + 1) / 4.0,
                               sw, 0.65, "Mat_GraniteLight", matrix=m)
                for sx in (-1, 1):
                    self.box_z(sx * (sw * 0.5 + 0.35), -(d * 0.5 + 2.1), 0.0, plinth_h + 0.45,
                               0.55, 2.6, "Mat_GraniteLight", matrix=m)

        # Core recessed hall walls
        z_floor = plinth_h
        core_w = w - 2.2
        core_d = d - 2.2
        self.box_z(0, 0, z_floor, z_floor + wall_h, core_w, core_d, wall_mat, matrix=m)

        # Warm glowing wooden lattice door/window bays on front and back
        n_bays = max(3, int(core_w // 3.4))
        bay_w = (core_w - 1.6) / n_bays
        for i in range(n_bays):
            bx = -core_w * 0.5 + 0.8 + (i + 0.5) * bay_w
            is_center = (i == n_bays // 2)
            wh = wall_h * (0.76 if is_center else 0.58)
            wb = bay_w * 0.68
            # Front glowing lattice
            self.box_z(bx, -core_d * 0.5 - 0.08, z_floor + 0.45, z_floor + 0.45 + wh, wb, 0.18, window_mat, matrix=m)
            # Frame mullions
            self.box_z(bx, -core_d * 0.5 - 0.14, z_floor + 0.45 + wh * 0.5, z_floor + 0.45 + wh * 0.5 + 0.14,
                       wb + 0.15, 0.16, pillar_mat, matrix=m)
            # Back windows
            if i % 2 == 0:
                self.box_z(bx, core_d * 0.5 + 0.08, z_floor + 1.2, z_floor + wall_h * 0.72, wb * 0.8, 0.16, window_mat, matrix=m)

        # Perimeter colonnade pillars + stone bases + dougong beam band
        nx = max(4, int(w // 3.6) + 1)
        ny = max(3, int(d // 3.8) + 1)
        px_list = [(-w * 0.5 + w * i / (nx - 1)) for i in range(nx)]
        py_list = [(-d * 0.5 + d * j / (ny - 1)) for j in range(ny)]
        for ix, px in enumerate(px_list):
            for iy, py in enumerate(py_list):
                if 0 < ix < nx - 1 and 0 < iy < ny - 1:
                    continue
                self.cylinder(px, py, z_floor, z_floor + 0.35, 0.36, "Mat_GraniteLight", sides=6, smooth=False, matrix=m)
                self.cylinder(px, py, z_floor + 0.35, z_floor + wall_h, 0.24, pillar_mat, sides=8, smooth=True, matrix=m)

        # Dougong eaves beam frieze
        self.box_z(0, 0, z_floor + wall_h - 0.55, z_floor + wall_h + 0.25, w + 0.6, d + 0.6, pillar_mat, matrix=m)
        if plaque:
            self.box_z(0, -(d * 0.5 + 0.45), z_floor + wall_h - 1.3, z_floor + wall_h - 0.2,
                       min(3.6, w * 0.24), 0.24, "Mat_PlaqueRed", matrix=m)
            self.box_z(0, -(d * 0.5 + 0.58), z_floor + wall_h - 1.15, z_floor + wall_h - 0.35,
                       min(3.1, w * 0.20), 0.12, gold_mat if gold_mat else "Mat_GoldTrim", matrix=m)

        # Roof(s)
        if double_eave:
            # Lower skirt eave
            self.add_upturned_roof(
                0, 0, z_floor + wall_h + 0.1, w, d, roof_h * 0.48,
                mat_tile=roof_mat, mat_ridge=ridge_mat, mat_wood=pillar_mat,
                mat_gold=None, mat_eave_light=eave_light,
                overhang=2.0, flare_z=0.95, flare_xy=0.75, ridge_ratio=0.72, steps=4, matrix=m,
            )
            # Upper clerestory tier
            uw, ud = w * 0.68, d * 0.64
            uz0 = z_floor + wall_h + roof_h * 0.38
            uh = wall_h * 0.42
            self.box_z(0, 0, uz0, uz0 + uh, uw, ud, pillar_mat, matrix=m)
            self.box_z(0, -(ud * 0.5 + 0.08), uz0 + 0.35, uz0 + uh - 0.35, uw * 0.72, 0.16, window_mat, matrix=m)
            self.box_z(0,  (ud * 0.5 + 0.08), uz0 + 0.35, uz0 + uh - 0.35, uw * 0.72, 0.16, window_mat, matrix=m)
            # Upper grand roof
            self.add_upturned_roof(
                0, 0, uz0 + uh, uw, ud, roof_h * 0.95,
                mat_tile=roof_mat, mat_ridge=ridge_mat, mat_wood=pillar_mat,
                mat_gold=gold_mat, mat_eave_light=eave_light,
                overhang=1.8, flare_z=1.35, flare_xy=0.95, ridge_ratio=0.55, steps=5, matrix=m,
            )
        else:
            self.add_upturned_roof(
                0, 0, z_floor + wall_h + 0.1, w, d, roof_h,
                mat_tile=roof_mat, mat_ridge=ridge_mat, mat_wood=pillar_mat,
                mat_gold=gold_mat, mat_eave_light=eave_light,
                overhang=1.6, flare_z=0.95, flare_xy=0.70, ridge_ratio=0.56, steps=4, matrix=m,
            )

    # ------------------------------------------------------------------
    # Hexagonal / Octagonal Suzhou Pavilion (亭)
    # ------------------------------------------------------------------
    def add_pavilion(
        self, cx, cy, z0, radius=4.2, col_h=3.6, roof_h=3.4,
        sides=6, double_eave=False, plinth_h=0.65,
        pillar_mat="Mat_DarkWood", roof_mat="Mat_DarkTile",
        gold_mat="Mat_GoldTrim", eave_light="Emissive_Gold_Eave",
        lantern_mat="Emissive_Warm_Lantern", matrix=None,
    ):
        m = Matrix.Translation((cx, cy, z0))
        if matrix is not None:
            m = matrix @ m

        if plinth_h > 0:
            self.prism(0, 0, -0.4, plinth_h, radius + 0.8, radius + 0.65, sides, "Mat_GraniteLight", matrix=m)

        # Perimeter bench railing (美人靠) + columns
        for i in range(sides):
            a = 2.0 * math.pi * i / sides
            px, py = radius * 0.86 * math.cos(a), radius * 0.86 * math.sin(a)
            self.cylinder(px, py, plinth_h, plinth_h + col_h, 0.18, pillar_mat, sides=6, smooth=True, matrix=m)
            if i % 2 == 0 or sides <= 6:
                na = 2.0 * math.pi * ((i + 1) % sides) / sides
                qx, qy = radius * 0.86 * math.cos(na), radius * 0.86 * math.sin(na)
                mx, my = 0.5 * (px + qx), 0.5 * (py + qy)
                seg = math.hypot(qx - px, qy - py)
                ang = math.atan2(qy - py, qx - px)
                # Leave 2 open entry bays
                if i not in (0, sides // 2):
                    self.box_z(mx, my, plinth_h + 0.35, plinth_h + 0.85, seg * 0.88, 0.16, pillar_mat, rot_z=ang, matrix=m)

        # Top lintel ring
        self.prism(0, 0, plinth_h + col_h - 0.35, plinth_h + col_h + 0.1,
                   radius * 0.95, radius * 0.95, sides, pillar_mat, cap_bottom=False, cap_top=False, matrix=m)

        # Central hanging warm lantern inside pavilion
        if lantern_mat:
            self.add_lantern(0, 0, plinth_h + col_h - 0.9, scale=1.1, glow_mat=lantern_mat, matrix=m)

        if double_eave:
            self.add_polygonal_roof(
                0, 0, plinth_h + col_h, radius * 0.65, radius * 1.42, roof_h * 0.45, sides=sides,
                mat_tile=roof_mat, mat_wood=pillar_mat, mat_gold=None,
                mat_eave_light=eave_light, flare_z=0.75, flare_r=0.45, finial=False, matrix=m,
            )
            uz = plinth_h + col_h + roof_h * 0.42
            self.prism(0, 0, uz, uz + col_h * 0.38, radius * 0.62, radius * 0.62, sides, "Emissive_Warm_Window", matrix=m)
            self.add_polygonal_roof(
                0, 0, uz + col_h * 0.38, 0.12, radius * 1.08, roof_h * 0.85, sides=sides,
                mat_tile=roof_mat, mat_wood=pillar_mat, mat_gold=gold_mat,
                mat_eave_light=eave_light, flare_z=0.95, flare_r=0.55, finial=True, matrix=m,
            )
        else:
            self.add_polygonal_roof(
                0, 0, plinth_h + col_h, 0.12, radius * 1.38, roof_h, sides=sides,
                mat_tile=roof_mat, mat_wood=pillar_mat, mat_gold=gold_mat,
                mat_eave_light=eave_light, flare_z=0.80, flare_r=0.48, finial=True, matrix=m,
            )

    # ------------------------------------------------------------------
    # Courtyard Walls & Covered Garden Corridors
    # ------------------------------------------------------------------
    def add_wall(
        self, x0, y0, x1, y1, z0=0.0, h=3.6, thickness=0.55,
        wall_mat="Mat_WhiteWall", tile_mat="Mat_DarkTile",
        pilaster_step=12.0, horse_head=False, leak_windows=False,
        window_mat="Emissive_Warm_Window",
    ):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length < 0.2:
            return
        ang = math.atan2(dy, dx)
        mx, my = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        m = Matrix.Translation((mx, my, z0)) @ Matrix.Rotation(ang, 4, 'Z')

        # Stone plinth base + wall body + pitched tile coping
        self.box_z(0, 0, -0.5, 0.55, length, thickness + 0.16, "Mat_GraniteDark", matrix=m)
        self.box_z(0, 0, 0.55, h, length, thickness, wall_mat, matrix=m)
        self.box_z(0, 0, h, h + 0.32, length + 0.2, thickness + 0.55, tile_mat, matrix=m)
        self.box_z(0, 0, h + 0.32, h + 0.52, length + 0.15, 0.28, "Mat_TileRidge", matrix=m)

        # Pilasters & optional stepped horse-head piers (马头墙)
        n_seg = max(1, int(length // pilaster_step))
        for i in range(n_seg + 1):
            px = -length * 0.5 + length * i / n_seg
            ph = h + (1.1 if horse_head and (i == 0 or i == n_seg) else 0.2)
            self.box_z(px, 0, 0.0, ph, thickness + 0.32, thickness + 0.32, wall_mat, matrix=m)
            self.box_z(px, 0, ph, ph + 0.30, thickness + 0.72, thickness + 0.72, tile_mat, matrix=m)

        # Carved Suzhou leak-windows (漏窗)
        if leak_windows and length > 5.0:
            n_win = max(1, int(length // 6.0))
            for i in range(n_win):
                wx = -length * 0.5 + (i + 0.5) * (length / n_win)
                self.box_z(wx, 0, h * 0.42, h * 0.78, 1.5, thickness + 0.14, "Mat_DarkWood", matrix=m)
                self.box_z(wx, 0, h * 0.47, h * 0.73, 1.2, thickness + 0.20, window_mat, matrix=m)

    def add_corridor(
        self, x0, y0, x1, y1, z0=0.0, width=3.0, h=3.1,
        back_wall=True, wall_side=1,
        wall_mat="Mat_WhiteWall", wood_mat="Mat_DarkWood",
        tile_mat="Mat_DarkTile", lantern_mat="Emissive_Warm_Lantern",
        leak_windows=True,
    ):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length < 1.0:
            return
        ang = math.atan2(dy, dx)
        mx, my = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        m = Matrix.Translation((mx, my, z0)) @ Matrix.Rotation(ang, 4, 'Z')

        # Stone walkway base
        self.box_z(0, 0, -0.4, 0.32, length + 0.3, width + 0.4, "Mat_GraniteLight", matrix=m)
        # Roof beam & curved dark tile roof
        self.box_z(0, 0, h - 0.25, h + 0.05, length + 0.2, width, wood_mat, matrix=m)
        self.add_upturned_roof(
            0, 0, h, length, width, 1.35,
            mat_tile=tile_mat, mat_ridge="Mat_TileRidge", mat_wood=wood_mat,
            mat_gold=None, mat_eave_light=None, overhang=0.65, flare_z=0.25, flare_xy=0.2,
            ridge_ratio=0.92, steps=3, matrix=m,
        )
        # Posts & hanging lanterns
        n_posts = max(2, int(length // 3.8) + 1)
        for i in range(n_posts):
            px = -length * 0.5 + length * i / (n_posts - 1)
            for sy in (-1, 1):
                self.cylinder(px, sy * (width * 0.44), 0.32, h, 0.12, wood_mat, sides=6, smooth=False, matrix=m)
            if lantern_mat and i < n_posts - 1 and i % 2 == 0:
                lx = px + 0.5 * (length / (n_posts - 1))
                self.add_lantern(lx, -wall_side * (width * 0.35), h - 0.65, scale=0.65, glow_mat=lantern_mat, matrix=m)

        # Optional back wall with Suzhou leak windows
        if back_wall:
            wy = wall_side * (width * 0.46)
            self.box_z(0, wy, 0.32, h - 0.1, length, 0.28, wall_mat, matrix=m)
            if leak_windows and length > 4.0:
                n_w = max(1, int(length // 4.5))
                for i in range(n_w):
                    wx = -length * 0.5 + (i + 0.5) * (length / n_w)
                    self.box_z(wx, wy, 1.25, 2.35, 1.35, 0.34, wood_mat, matrix=m)
                    self.box_z(wx, wy, 1.35, 2.25, 1.12, 0.40, "Emissive_Warm_Window", matrix=m)

    # ------------------------------------------------------------------
    # True Open-Arch Suzhou Stone Bridge (枫桥 / 吴门桥)
    # ------------------------------------------------------------------
    def add_arch_bridge(
        self, cx, cy, z_water, span_axis="X",
        clear_w=14.0, clear_h=6.5, deck_w=6.0,
        approach_len=12.0, arch_thick=1.1,
        stone_mat="Mat_GraniteLight", dark_stone="Mat_GraniteDark",
        lantern_mat="Emissive_Warm_Lantern", segs=16,
    ):
        """
        Builds a mathematically exact OPEN stone arch bridge.
        span_axis='X' means bridge deck runs along X (arch tunnel opens along Y).
        span_axis='Y' means bridge deck runs along Y (arch tunnel opens along X,
        so a drone flying East/West along X flies cleanly THROUGH the arch!).
        """
        rot = 0.0 if span_axis == "X" else (0.5 * math.pi)
        m = Matrix.Translation((cx, cy, z_water)) @ Matrix.Rotation(rot, 4, 'Z')

        rx = clear_w * 0.5          # half clear width of opening
        rz = clear_h                # clear crown height above z_water
        crown_z = rz + arch_thick   # top of stone deck at bridge apex
        hw = deck_w * 0.5
        total_half = rx + approach_len

        # 1. Arch vault ring (voussoirs) from theta=0 to pi
        # Ensure zero geometry intrudes inside (x/rx)^2 + (z/rz)^2 < 1 !
        ring_verts = []
        ring_faces = []
        for i in range(segs + 1):
            th = math.pi * (1.0 - i / segs)  # pi (left) -> 0 (right)
            ct, st = math.cos(th), math.sin(th)
            x_in = rx * ct
            z_in = rz * st
            x_out = (rx + arch_thick) * ct
            z_out = (rz + arch_thick) * st
            # 4 vertices per slice: front-in, back-in, back-out, front-out
            ring_verts.extend([
                (x_in,  -hw, z_in),
                (x_in,   hw, z_in),
                (x_out,  hw, z_out),
                (x_out, -hw, z_out),
            ])
        for i in range(segs):
            a = i * 4
            b = (i + 1) * 4
            # underside (intrados)
            ring_faces.append((a + 0, b + 0, b + 1, a + 1))
            # top (extrados)
            ring_faces.append((a + 3, a + 2, b + 2, b + 3))
            # front face (-Y)
            ring_faces.append((a + 0, a + 3, b + 3, b + 0))
            # back face (+Y)
            ring_faces.append((a + 1, b + 1, b + 2, a + 2))
        self.add_mesh_data(ring_verts, ring_faces, dark_stone, smooth=False, matrix=m)

        # 2. Spandrel + Stepped Bridge Deck profile (strictly ABOVE the arch extrados!)
        def deck_z_at(x):
            ax = abs(x)
            if ax >= total_half:
                return 0.4
            t = ax / total_half
            # Graceful Suzhou camelback curve: peaks at crown_z, meets bank cleanly
            return 0.4 + (crown_z - 0.4) * (math.cos(t * 0.5 * math.pi) ** 1.25)

        # Left and right spandrel walls & solid abutments outside clear_w/2
        # Build vertical slices along X from -total_half to +total_half
        xs = []
        n_app = 6
        for i in range(n_app):
            xs.append(-total_half + approach_len * i / n_app)
        for i in range(segs + 1):
            th = math.pi * (1.0 - i / segs)
            xs.append(rx * math.cos(th))
        for i in range(1, n_app + 1):
            xs.append(rx + approach_len * i / n_app)

        sp_verts = []
        sp_faces = []
        for x in xs:
            zt = deck_z_at(x)
            if abs(x) < rx - 1e-4:
                # Strictly above arch curve!
                u = min(1.0, abs(x) / rx)
                zb = rz * math.sqrt(max(0.0, 1.0 - u * u)) + arch_thick * 0.85
            else:
                zb = max(-2.4 - z_water, -1.6)  # abutment pier extends below water, clamped cleanly above Z=-2.4
            zb = min(zb, zt - 0.35)
            sp_verts.extend([
                (x, -hw, zb), (x, hw, zb), (x, hw, zt), (x, -hw, zt),
            ])
        for i in range(len(xs) - 1):
            a = i * 4
            b = (i + 1) * 4
            # top deck
            sp_faces.append((a + 3, b + 3, b + 2, a + 2))
            # front spandrel
            sp_faces.append((a + 0, b + 0, b + 3, a + 3))
            # back spandrel
            sp_faces.append((a + 1, a + 2, b + 2, b + 1))
            # bottom (abutments only)
            sp_faces.append((a + 0, a + 1, b + 1, b + 0))
        # End caps
        sp_faces.append((0, 3, 2, 1))
        last = (len(xs) - 1) * 4
        sp_faces.append((last + 0, last + 1, last + 2, last + 3))
        self.add_mesh_data(sp_verts, sp_faces, stone_mat, smooth=False, matrix=m)

        # 3. Parapet stone railings & carved posts along both sides of deck
        par_h = 1.05
        par_w = 0.38
        for side_y in (-hw + par_w * 0.5, hw - par_w * 0.5):
            for i in range(len(xs) - 1):
                x0, x1 = xs[i], xs[i + 1]
                z0, z1 = deck_z_at(x0), deck_z_at(x1)
                mid_x = 0.5 * (x0 + x1)
                mid_z = 0.5 * (z0 + z1) + par_h * 0.5
                seg_l = math.hypot(x1 - x0, z1 - z0)
                ang_y = -math.atan2(z1 - z0, x1 - x0)
                self.box(mid_x, side_y, mid_z, seg_l + 0.08, par_w, par_h, stone_mat, rot_y=ang_y, matrix=m)
            # Carved stone newel posts & lanterns
            n_posts = 7
            for k in range(n_posts):
                px = -total_half + (2.0 * total_half) * k / (n_posts - 1)
                pz = deck_z_at(px)
                self.box_z(px, side_y, pz, pz + par_h + 0.45, 0.55, 0.55, stone_mat, matrix=m)
                if lantern_mat and k in (0, 2, 3, 4, 6):
                    self.add_lantern(px, side_y, pz + par_h + 0.72, scale=0.68, glow_mat=lantern_mat, matrix=m)

        # Warm arch-lining lights tucked under the crown for nighttime silhouette
        if lantern_mat:
            for k in range(1, 6):
                th = math.pi * k / 6.0
                lx = (rx + 0.15) * math.cos(th)
                lz = (rz + 0.15) * math.sin(th)
                self.box(lx, -hw - 0.08, lz, 0.55, 0.18, 0.25, "Emissive_Gold_Eave", matrix=m)
                self.box(lx,  hw + 0.08, lz, 0.55, 0.18, 0.25, "Emissive_Gold_Eave", matrix=m)

    # ------------------------------------------------------------------
    # Pagoda Spire (塔刹) & Lanterns
    # ------------------------------------------------------------------
    def add_pagoda_spire(
        self, cx, cy, z_base, height=6.5, r_base=1.1,
        bronze_mat="Mat_Bronze", gold_mat="Mat_GoldTrim",
        glow_mat="Emissive_Gold_Crown", matrix=None,
    ):
        m = Matrix.Translation((cx, cy, z_base))
        if matrix is not None:
            m = matrix @ m
        # Inverted alms bowl (覆钵) & lotus base
        self.prism(0, 0, 0.0, height * 0.18, r_base, r_base * 0.65, 8, bronze_mat, matrix=m)
        self.prism(0, 0, height * 0.18, height * 0.30, r_base * 0.75, r_base * 0.42, 8, gold_mat, matrix=m)
        # Central pole
        self.cylinder(0, 0, height * 0.25, height * 0.94, r_base * 0.13, bronze_mat, sides=8, smooth=True, matrix=m)
        # 5 stacked rings (相轮)
        for i in range(5):
            rz_ring = height * (0.36 + i * 0.085)
            rr = r_base * (0.50 - i * 0.055)
            self.prism(0, 0, rz_ring, rz_ring + height * 0.035, rr, rr * 0.92, 8, gold_mat, matrix=m)
        # Canopy + glowing golden jewel
        self.prism(0, 0, height * 0.80, height * 0.86, r_base * 0.45, r_base * 0.18, 8, gold_mat, matrix=m)
        self.sphere(0, 0, height * 0.94, r_base * 0.26, r_base * 0.26, height * 0.08, 8, 5, glow_mat, smooth=True, matrix=m)

    def add_lantern(self, cx, cy, cz, scale=1.0, glow_mat="Emissive_Warm_Lantern",
                    wood_mat="Mat_DarkWood", matrix=None):
        m = Matrix.Translation((cx, cy, cz))
        if matrix is not None:
            m = matrix @ m
        r = 0.28 * scale
        h = 0.48 * scale
        self.prism(0, 0, -h * 0.5, h * 0.5, r * 0.82, r * 0.82, 6, glow_mat, matrix=m)
        self.prism(0, 0, h * 0.5, h * 0.68, r * 1.15, r * 0.45, 6, wood_mat, matrix=m)
        self.prism(0, 0, -h * 0.65, -h * 0.5, r * 0.55, r * 0.85, 6, wood_mat, matrix=m)

    def add_lantern_post(self, cx, cy, z0, h=3.4, glow_mat="Emissive_Warm_Lantern", matrix=None):
        m = Matrix.Translation((cx, cy, z0))
        if matrix is not None:
            m = matrix @ m
        self.prism(0, 0, 0.0, 0.45, 0.34, 0.26, 6, "Mat_GraniteDark", matrix=m)
        self.cylinder(0, 0, 0.45, h, 0.10, "Mat_DarkWood", sides=6, smooth=False, matrix=m)
        self.add_lantern(0, 0, h + 0.35, scale=0.95, glow_mat=glow_mat, matrix=m)

    # ------------------------------------------------------------------
    # Jiangnan Landscape: Willows, Pines, Maples, Bamboo, Taihu Rocks, Boats
    # ------------------------------------------------------------------
    def add_tree_willow(self, cx, cy, z0, scale=1.0, seed=0):
        rng = random.Random(seed + 101)
        lean_x = rng.uniform(-0.7, 0.7) * scale
        lean_y = rng.uniform(-0.7, 0.7) * scale
        h = 4.2 * scale
        # Gently leaning gnarled willow trunk
        m_t = Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(lean_x * 0.12, 4, 'Y') @ Matrix.Rotation(-lean_y * 0.12, 4, 'X')
        self.prism(0, 0, -0.3, h, 0.36 * scale, 0.18 * scale, 6, "Mat_TrunkBark", smooth=True, matrix=m_t)
        # Soft billowing layered weeping canopy (natural cloud-like silhouette, zero spiky cones!)
        top_x = cx + lean_x * 0.5
        top_y = cy + lean_y * 0.5
        top_z = z0 + h
        self.sphere(top_x, top_y, top_z + 1.5 * scale, 2.6 * scale, 2.6 * scale, 2.0 * scale, 7, 5, "Mat_WillowFoliage", smooth=True)
        for i in range(5):
            a = 2.0 * math.pi * i / 5.0 + rng.uniform(-0.25, 0.25)
            rad = rng.uniform(1.4, 2.1) * scale
            dx, dy = rad * math.cos(a), rad * math.sin(a)
            # Soft drooping ovoid bough cluster
            self.sphere(top_x + dx, top_y + dy, top_z + rng.uniform(0.1, 0.7) * scale,
                        1.55 * scale, 1.45 * scale, 2.15 * scale, 6, 4, "Mat_WillowFoliage", smooth=True)

    def add_tree_pine(self, cx, cy, z0, scale=1.0, seed=0):
        rng = random.Random(seed + 202)
        h = 6.2 * scale
        self.prism(cx, cy, z0 - 0.4, z0 + h * 0.78, 0.36 * scale, 0.14 * scale, 6, "Mat_TrunkBark", smooth=True)
        # Layered Chinese scholar pine flat needle pads (云片松)
        layers = [
            (0.0, 0.0, 0.92, 2.3, 0.85),
            (1.1, 0.6, 0.72, 2.0, 0.72),
            (-1.0, -0.7, 0.64, 1.9, 0.70),
            (0.4, -1.0, 0.80, 1.7, 0.68),
            (-0.7, 0.9, 0.52, 1.8, 0.65),
        ]
        rot = rng.uniform(0, 2.0 * math.pi)
        cr, sr = math.cos(rot), math.sin(rot)
        for lx, ly, lz_f, rad, hz in layers:
            rx = (lx * cr - ly * sr) * scale
            ry = (lx * sr + ly * cr) * scale
            self.sphere(cx + rx, cy + ry, z0 + h * lz_f,
                        rad * scale, rad * 0.9 * scale, hz * scale, 7, 4, "Mat_PineFoliage", smooth=True)

    def add_tree_maple(self, cx, cy, z0, scale=1.0, seed=0):
        rng = random.Random(seed + 303)
        h = 4.6 * scale
        self.prism(cx, cy, z0 - 0.3, z0 + h * 0.65, 0.28 * scale, 0.14 * scale, 6, "Mat_TrunkBark", smooth=True)
        for i in range(4):
            a = 2.0 * math.pi * i / 4.0 + rng.uniform(-0.3, 0.3)
            r = rng.uniform(0.7, 1.4) * scale
            self.sphere(cx + r * math.cos(a), cy + r * math.sin(a), z0 + h * rng.uniform(0.68, 0.96),
                        1.75 * scale, 1.65 * scale, 1.15 * scale, 6, 4, "Mat_MapleRed", smooth=True)

    def add_bamboo_cluster(self, cx, cy, z0, radius=4.5, count=14, h_min=6.5, h_max=11.0, seed=0):
        rng = random.Random(seed + 404)
        for i in range(count):
            a = rng.uniform(0, 2.0 * math.pi)
            r = radius * math.sqrt(rng.uniform(0.05, 1.0))
            bx = cx + r * math.cos(a)
            by = cy + r * math.sin(a)
            bh = rng.uniform(h_min, h_max)
            lean = rng.uniform(0.03, 0.11)
            m_b = Matrix.Translation((bx, by, z0)) @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(lean, 4, 'Y')
            self.prism(0, 0, -0.3, bh, 0.10, 0.045, 5, "Mat_BambooCulm", smooth=False, matrix=m_b)
            # Canopy tufts on upper third
            for fz in (0.68, 0.84, 0.97):
                self.sphere(0.25, 0.0, bh * fz, 1.15, 0.95, 0.65, 5, 3, "Mat_BambooGreen", smooth=True, matrix=m_b)

    def add_taihu_rock(self, cx, cy, z0, sx, sy, sz, seed=0, tall_peak=False):
        """
        Sculpted Suzhou Taihu limestone rockery.
        When tall_peak=True, sculpts the iconic 'Cloud-Capped Peak' (冠云峰):
        slender waist, flaring perforated crown ('瘦、皱、漏、透') with real through-holes!
        """
        rng = random.Random(seed + 505)
        if tall_peak:
            # Multi-lobe perforated vertical sculpture with real open cavities between pillars!
            # Narrow sculpted base & waist
            self.prism(cx, cy, z0, z0 + sz * 0.25, sx * 0.42, sx * 0.28, 7, "Mat_TaihuRock")
            # Left & right twisting stone pillars leaving an open central window (透/漏)!
            self.prism(cx - sx * 0.26, cy, z0 + sz * 0.20, z0 + sz * 0.68, sx * 0.22, sx * 0.30, 6, "Mat_TaihuRock")
            self.prism(cx + sx * 0.26, cy + sy * 0.08, z0 + sz * 0.20, z0 + sz * 0.72, sx * 0.20, sx * 0.32, 6, "Mat_TaihuRock")
            # Cross-bridge stone rib separating lower and upper cavities
            self.box(cx, cy, z0 + sz * 0.44, sx * 0.56, sy * 0.38, sz * 0.11, "Mat_TaihuRock", rot_z=0.2)
            # Dramatic flaring cloud-like crown (冠云)
            crown_lobes = [
                (0.0,   0.0,  0.80, 0.52, 0.36, 0.22),
                (-0.40, 0.08, 0.86, 0.36, 0.28, 0.20),
                ( 0.38,-0.06, 0.88, 0.38, 0.28, 0.22),
                ( 0.05, 0.04, 0.96, 0.32, 0.25, 0.16),
                (-0.22,-0.12, 0.65, 0.28, 0.24, 0.16),
            ]
            for lx, ly, lz, rx, ry, rz in crown_lobes:
                self.sphere(cx + lx * sx, cy + ly * sy, z0 + lz * sz,
                            rx * sx, ry * sy, rz * sz, 6, 4, "Mat_TaihuRock", smooth=False)
        else:
            # Craggy multi-boulder Taihu garden rockery cluster
            n_boulders = 5
            for i in range(n_boulders):
                ox = rng.uniform(-0.35, 0.35) * sx
                oy = rng.uniform(-0.35, 0.35) * sy
                oz = rng.uniform(0.18, 0.70) * sz
                rx = rng.uniform(0.32, 0.62) * sx
                ry = rng.uniform(0.30, 0.58) * sy
                rz = rng.uniform(0.28, 0.55) * sz
                self.sphere(cx + ox, cy + oy, z0 + oz, rx, ry, rz, 6, 4, "Mat_TaihuRock", smooth=False)

    def add_wooden_boat(self, cx, cy, z_water, rot_z=0.0, scale=1.0, lantern=True):
        """Traditional Suzhou black-awning boat (乌篷船) with warm bow lantern."""
        m = Matrix.Translation((cx, cy, z_water)) @ Matrix.Rotation(rot_z, 4, 'Z')
        L, W, H = 7.2 * scale, 1.9 * scale, 0.72 * scale
        # Tapered boat hull
        pts = [
            (-L * 0.50, 0.0), (-L * 0.28, -W * 0.48), (L * 0.28, -W * 0.48),
            ( L * 0.50, 0.0), ( L * 0.28,  W * 0.48), (-L * 0.28,  W * 0.48),
        ]
        self.extrude_polygon(pts, -0.25 * scale, H * 0.55, "Mat_DarkWood", matrix=m)
        # Black arched bamboo canopy (乌篷)
        self.box_z(-0.2 * scale, 0, H * 0.55, H * 1.45, L * 0.42, W * 0.76, "Mat_DarkTile", matrix=m)
        self.box_z(-0.2 * scale, 0, H * 1.45, H * 1.72, L * 0.40, W * 0.52, "Mat_DarkTile", matrix=m)
        # Bow fishing lantern (江枫渔火!)
        if lantern:
            self.cylinder(L * 0.38, 0, H * 0.5, H * 2.1, 0.05 * scale, "Mat_DarkWood", sides=5, smooth=False, matrix=m)
            self.add_lantern(L * 0.42, 0, H * 1.9, scale=0.65 * scale, glow_mat="Emissive_Warm_Lantern", matrix=m)

    # ------------------------------------------------------------------
    # Build Blender Object & Export GLB
    # ------------------------------------------------------------------
    def build_and_export(self, glb_path):
        reset_scene()
        os.makedirs(os.path.dirname(glb_path), exist_ok=True)

        # Ensure consistent outward normals
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)

        mesh = bpy.data.meshes.new(self.name + "_Mesh")
        self.bm.to_mesh(mesh)
        self.bm.free()

        for mname in self.mat_names:
            mesh.materials.append(create_material(mname))

        obj = bpy.data.objects.new(self.name, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Compute stats before export
        tri_count = sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]

        bpy.ops.export_scene.gltf(
            filepath=glb_path,
            export_format="GLB",
            export_materials="EXPORT",
            export_yup=True,
            export_apply=True,
        )

        fsize = os.path.getsize(glb_path)
        print(
            f"[EXPORT OK] {os.path.basename(glb_path)} | "
            f"Size: {fsize / (1024 * 1024):.2f} MB | "
            f"Tris: {tri_count:,} | Mats: {len(self.mat_names)} | "
            f"Blender BBox X:[{min(xs):.1f},{max(xs):.1f}] "
            f"Y:[{min(ys):.1f},{max(ys):.1f}] Z:[{min(zs):.1f},{max(zs):.1f}]"
        )
        return {
            "path": glb_path,
            "size_bytes": fsize,
            "triangles": tri_count,
            "materials": len(self.mat_names),
        }
