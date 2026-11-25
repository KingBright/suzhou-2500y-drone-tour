"""
Shared procedural geometry & PBR material library for Act II Ancient Gusu landmarks.
Compatible with Blender 5.2.2 LTS headless CLI.
"""
import math
import os
import random
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

MODEL_DIR = "/Users/jinliang/workspace/experiment/suzhou-drone-tour/web/public/assets/models"


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_mat(name, base_color, roughness=0.75, metallic=0.0,
             emission_color=None, emission_strength=0.0, alpha=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*base_color[:3], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if emission_color is not None and emission_strength > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*emission_color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 0.999:
        mat.blend_method = "BLEND" if hasattr(mat, "blend_method") else "HASHED"
    return mat


def create_gusu_palette():
    """Return dictionary of classical Suzhou & Pei Museum PBR materials."""
    return {
        "white_wall": make_mat("Suzhou_WhiteWall", (0.87, 0.85, 0.79), roughness=0.84),
        "cream_wall": make_mat("Suzhou_CreamWall", (0.82, 0.78, 0.70), roughness=0.86),
        "ochre_wall": make_mat("Temple_OchreWall", (0.76, 0.57, 0.24), roughness=0.82),
        "dark_tile": make_mat("Suzhou_DarkTile", (0.14, 0.16, 0.19), roughness=0.56, metallic=0.05),
        "tile_ridge": make_mat("Suzhou_TileRidge", (0.24, 0.26, 0.29), roughness=0.62),
        "dark_wood": make_mat("Suzhou_DarkWood", (0.20, 0.11, 0.07), roughness=0.52),
        "warm_wood": make_mat("Suzhou_WarmWood", (0.36, 0.21, 0.12), roughness=0.55),
        "vermilion": make_mat("Suzhou_Vermilion", (0.64, 0.14, 0.10), roughness=0.46),
        "pagoda_brick": make_mat("Pagoda_Brick", (0.58, 0.44, 0.31), roughness=0.80),
        "pagoda_brick_dark": make_mat("Pagoda_BrickDark", (0.42, 0.32, 0.23), roughness=0.82),
        "flagstone": make_mat("Suzhou_Flagstone", (0.48, 0.48, 0.46), roughness=0.76),
        "stone_light": make_mat("Suzhou_StoneLight", (0.66, 0.64, 0.59), roughness=0.78),
        "stone_dark": make_mat("Suzhou_StoneDark", (0.32, 0.33, 0.35), roughness=0.74),
        "courtyard": make_mat("Suzhou_Courtyard", (0.62, 0.59, 0.53), roughness=0.88),
        "taihu_rock": make_mat("Taihu_Rock", (0.50, 0.49, 0.46), roughness=0.84),
        "taihu_dark": make_mat("Taihu_RockDark", (0.36, 0.36, 0.35), roughness=0.86),
        "pei_white": make_mat("Pei_WhiteWall", (0.93, 0.92, 0.89), roughness=0.74),
        "pei_granite": make_mat("Pei_DarkGranite", (0.14, 0.16, 0.19), roughness=0.40, metallic=0.12),
        "pei_stone": make_mat("Pei_SlicedStone", (0.28, 0.30, 0.34), roughness=0.70),
        "pei_glass": make_mat("Pei_Glass", (0.16, 0.24, 0.29), roughness=0.10, metallic=0.25),
        "pei_wood": make_mat("Pei_TimberLouver", (0.52, 0.36, 0.22), roughness=0.58),
        "water": make_mat("Garden_Water", (0.07, 0.20, 0.19), roughness=0.07, metallic=0.12),
        "grass": make_mat("Garden_Grass", (0.22, 0.34, 0.15), roughness=0.90),
        "willow": make_mat("Foliage_Willow", (0.28, 0.45, 0.18), roughness=0.85),
        "pine": make_mat("Foliage_Pine", (0.12, 0.24, 0.13), roughness=0.86),
        "bamboo": make_mat("Foliage_Bamboo", (0.23, 0.44, 0.19), roughness=0.76),
        "lotus_pad": make_mat("Foliage_Lotus", (0.18, 0.37, 0.16), roughness=0.68),
        "lotus_pink": make_mat("Flower_Lotus", (0.88, 0.45, 0.56), roughness=0.55),
        "bark": make_mat("Tree_Bark", (0.24, 0.18, 0.13), roughness=0.90),
        "bronze": make_mat("Pagoda_Bronze", (0.68, 0.53, 0.22), roughness=0.32, metallic=0.82),
        "boat_awning": make_mat("Boat_Awning", (0.22, 0.17, 0.12), roughness=0.78),
        # Emissive materials (tagged for dynamic sunset->night scaling in Three.js)
        "emissive_warm": make_mat(
            "Emissive_Warm", (1.0, 0.78, 0.42), roughness=0.35,
            emission_color=(1.0, 0.68, 0.28), emission_strength=4.2
        ),
        "emissive_red": make_mat(
            "Emissive_Warm_LanternRed", (0.90, 0.16, 0.10), roughness=0.38,
            emission_color=(1.0, 0.26, 0.10), emission_strength=5.2
        ),
        "emissive_win": make_mat(
            "Emissive_Warm_Window", (1.0, 0.82, 0.52), roughness=0.30,
            emission_color=(1.0, 0.72, 0.36), emission_strength=2.8
        ),
        "emissive_gold": make_mat(
            "Emissive_Gold", (1.0, 0.85, 0.48), roughness=0.28, metallic=0.45,
            emission_color=(1.0, 0.78, 0.34), emission_strength=5.5
        ),
    }


class SceneBuilder:
    """
    Collects procedural bmesh geometry grouped by material key.
    Produces ultra-clean, low-draw-call merged meshes (one object per material
    or one multi-material mesh object for modular instancing kits).
    """

    def __init__(self, palette=None):
        self.palette = palette if palette is not None else create_gusu_palette()
        self.bms = {}

    def bm(self, mat_key):
        if mat_key not in self.bms:
            self.bms[mat_key] = bmesh.new()
        return self.bms[mat_key]

    def _xform(self, verts, center=(0, 0, 0), rot_z=0.0):
        if rot_z != 0.0:
            rm = Matrix.Rotation(rot_z, 4, "Z")
            t = Vector(center)
            for v in verts:
                v.co = (rm @ v.co) + t
        elif center != (0, 0, 0):
            t = Vector(center)
            for v in verts:
                v.co += t

    def add_box(self, mat_key, sx, sy, sz, center=(0, 0, 0), rot_z=0.0, rot_euler=None):
        bm = self.bm(mat_key)
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret["verts"]
        sm = Matrix.Diagonal((sx, sy, sz, 1.0))
        if rot_euler is not None:
            rm = Euler(rot_euler, "XYZ").to_matrix().to_4x4()
        elif rot_z != 0.0:
            rm = Matrix.Rotation(rot_z, 4, "Z")
        else:
            rm = Matrix.Identity(4)
        tm = Matrix.Translation(Vector(center))
        m = tm @ rm @ sm
        bmesh.ops.transform(bm, matrix=m, verts=verts)
        return verts

    def add_cylinder(self, mat_key, radius1, radius2, depth, segments=8,
                     center=(0, 0, 0), rot_z=0.0, rot_euler=None, cap_ends=True):
        bm = self.bm(mat_key)
        ret = bmesh.ops.create_cone(
            bm,
            cap_ends=cap_ends,
            cap_tris=False,
            segments=segments,
            radius1=radius1,
            radius2=radius2,
            depth=depth,
        )
        verts = ret["verts"]
        if rot_euler is not None:
            rm = Euler(rot_euler, "XYZ").to_matrix().to_4x4()
        elif rot_z != 0.0:
            rm = Matrix.Rotation(rot_z, 4, "Z")
        else:
            rm = Matrix.Identity(4)
        tm = Matrix.Translation(Vector(center))
        bmesh.ops.transform(bm, matrix=tm @ rm, verts=verts)
        return verts

    def add_ico(self, mat_key, radius=1.0, subdivisions=1, scale=(1, 1, 1),
                center=(0, 0, 0), rot_euler=None, jitter=0.0, rng=None):
        bm = self.bm(mat_key)
        ret = bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
        verts = ret["verts"]
        if jitter > 0.0:
            r = rng if rng is not None else random
            for v in verts:
                f = 1.0 + r.uniform(-jitter, jitter)
                v.co *= f
        sm = Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
        rm = Euler(rot_euler, "XYZ").to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)
        tm = Matrix.Translation(Vector(center))
        bmesh.ops.transform(bm, matrix=tm @ rm @ sm, verts=verts)
        return verts

    def add_prism(self, mat_key, pts_2d, z0, z1, center=(0, 0, 0), rot_z=0.0):
        """Extrude a 2D polygon [(x,y),...] from z0 to z1."""
        bm = self.bm(mat_key)
        n = len(pts_2d)
        if n < 3:
            return
        bot = [bm.verts.new((p[0], p[1], z0)) for p in pts_2d]
        top = [bm.verts.new((p[0], p[1], z1)) for p in pts_2d]
        bm.faces.new(list(reversed(bot)))
        bm.faces.new(top)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((bot[i], bot[j], top[j], top[i]))
        self._xform(bot + top, center=center, rot_z=rot_z)

    def add_loft(self, mat_key, rings, closed_caps=True, center=(0, 0, 0), rot_z=0.0):
        """
        Loft a closed tubular mesh through a list of rings; each ring is a list of (x,y,z) of equal length.
        """
        bm = self.bm(mat_key)
        n_rings = len(rings)
        n_pts = len(rings[0])
        v_rings = []
        for r in rings:
            v_rings.append([bm.verts.new(p) for p in r])
        for k in range(n_rings - 1):
            r0 = v_rings[k]
            r1 = v_rings[k + 1]
            for i in range(n_pts):
                j = (i + 1) % n_pts
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        if closed_caps:
            bm.faces.new(list(reversed(v_rings[0])))
            bm.faces.new(v_rings[-1])
        all_v = [v for r in v_rings for v in r]
        self._xform(all_v, center=center, rot_z=rot_z)

    def add_suzhou_roof(self, w, d, h, center=(0, 0, 0), rot_z=0.0,
                        eave_overhang=0.85, curve_drop=0.22, corner_lift=0.42,
                        mat_tile="dark_tile", mat_ridge="tile_ridge",
                        hip_gable=True, add_ribs=True):
        """
        Classic concave Jiangnan swept roof (歇山顶/硬山顶) with upturned flying corners.
        center = (cx, cy, z_eave_base).
        """
        bm = self.bm(mat_tile)
        hw = w * 0.5 + eave_overhang
        hd = d * 0.5 + eave_overhang
        ridge_hw = (w * 0.5 - d * 0.28) if hip_gable else (w * 0.5 + eave_overhang * 0.4)
        ridge_hw = max(0.3, ridge_hw)

        # Build a curved multi-step roof grid (4 slope bands from ridge to eave)
        # Front (+Y) and Back (-Y) slopes + Left/Right hip/gable
        steps = 4
        x_segs = 6

        def slope_pt(u, s, side):
            # u in [-1, 1] along X; s in [0, 1] from ridge (0) to eave (1); side in (+1, -1)
            cur_hw = ridge_hw + (hw - ridge_hw) * (s ** 0.85)
            x = u * cur_hw
            y = side * (hd * s)
            # Concave sag + upturned corner lift near s=1, |u|->1
            z = h * (1.0 - s) - curve_drop * h * math.sin(math.pi * s)
            corner_factor = (s ** 2.2) * (abs(u) ** 2.4)
            z += corner_lift * corner_factor
            return (x, y, z)

        all_verts = []
        for side in (1.0, -1.0):
            grid = []
            for si in range(steps + 1):
                s = si / steps
                row = []
                for xi in range(x_segs + 1):
                    u = -1.0 + 2.0 * xi / x_segs
                    v = bm.verts.new(slope_pt(u, s, side))
                    row.append(v)
                    all_verts.append(v)
                grid.append(row)
            for si in range(steps):
                for xi in range(x_segs):
                    v00 = grid[si][xi]
                    v01 = grid[si][xi + 1]
                    v11 = grid[si + 1][xi + 1]
                    v10 = grid[si + 1][xi]
                    if side > 0:
                        bm.faces.new((v00, v10, v11, v01))
                    else:
                        bm.faces.new((v00, v01, v11, v10))

        # Left and Right hip/gable triangular-ish side slopes
        for xside in (1.0, -1.0):
            u = xside
            grid = []
            for si in range(steps + 1):
                s = si / steps
                p_front = slope_pt(u, s, 1.0)
                p_back = slope_pt(u, s, -1.0)
                row = []
                for yi in range(4):
                    t = yi / 3.0
                    px = p_back[0] * (1.0 - t) + p_front[0] * t
                    py = p_back[1] * (1.0 - t) + p_front[1] * t
                    # Slight bulge outwards on hip slope
                    if hip_gable and s > 0.05:
                        px += xside * (0.12 * s * math.sin(math.pi * t))
                    pz = p_back[2] * (1.0 - t) + p_front[2] * t
                    v = bm.verts.new((px, py, pz))
                    row.append(v)
                    all_verts.append(v)
                grid.append(row)
            for si in range(steps):
                for yi in range(3):
                    v00 = grid[si][yi]
                    v01 = grid[si][yi + 1]
                    v11 = grid[si + 1][yi + 1]
                    v10 = grid[si + 1][yi]
                    if xside > 0:
                        bm.faces.new((v00, v01, v11, v10))
                    else:
                        bm.faces.new((v00, v10, v11, v01))

        # Bottom eave soffit plate to prevent looking hollow from below
        s0 = bm.verts.new((-hw, -hd, 0.0))
        s1 = bm.verts.new((hw, -hd, 0.0))
        s2 = bm.verts.new((hw, hd, 0.0))
        s3 = bm.verts.new((-hw, hd, 0.0))
        bm.faces.new((s0, s3, s2, s1))
        all_verts.extend([s0, s1, s2, s3])

        self._xform(all_verts, center=center, rot_z=rot_z)

        # Main ridge beam + upturned ridge ends (正脊翘吻)
        self.add_box(mat_ridge, ridge_hw * 2.0 + 0.35, 0.28, 0.32,
                     center=(center[0], center[1], center[2] + h + 0.14), rot_z=rot_z)
        for xs in (-1.0, 1.0):
            rx = xs * (ridge_hw + 0.15)
            cx = center[0] + rx * math.cos(rot_z)
            cy = center[1] + rx * math.sin(rot_z)
            self.add_box(mat_ridge, 0.32, 0.30, 0.55,
                         center=(cx, cy, center[2] + h + 0.32), rot_z=rot_z)

        # Optional decorative tile ribs on long roofs
        if add_ribs and w >= 5.0:
            n_ribs = max(3, min(9, int(w / 2.2)))
            for ri in range(n_ribs):
                u = -0.82 + 1.64 * ri / max(1, n_ribs - 1)
                for side in (-1.0, 1.0):
                    lx = u * (ridge_hw * 0.5 + hw * 0.5)
                    ly = side * hd * 0.52
                    wx = center[0] + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                    wy = center[1] + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                    slope_ang = math.atan2(h, hd)
                    self.add_box(
                        mat_ridge, 0.12, math.hypot(hd * 0.92, h * 0.92), 0.12,
                        center=(wx, wy, center[2] + h * 0.44),
                        rot_euler=(side * slope_ang, 0.0, rot_z)
                    )

    def add_radial_roof(self, sides, radius, height, center=(0, 0, 0), rot_z=0.0,
                        corner_lift=0.55, mat_tile="dark_tile", mat_ridge="tile_ridge",
                        finial=True, finial_mat="emissive_gold"):
        """Conical polygonal upturned roof (攒尖顶) for pavilions and pagoda tops."""
        bm = self.bm(mat_tile)
        rings = 4
        v_rings = []
        for ri in range(1, rings + 1):
            s = ri / rings
            r_base = radius * s
            # Concave sweep
            z_base = height * (1.0 - s) - 0.18 * height * math.sin(math.pi * s)
            ring = []
            for k in range(sides):
                ang = (2.0 * math.pi * k / sides) + math.pi / sides
                # Corner lift & slight outward flare at vertices
                z_v = z_base + corner_lift * (s ** 2.3)
                r_v = r_base * (1.0 + 0.07 * (s ** 2.0))
                ring.append(bm.verts.new((r_v * math.cos(ang), r_v * math.sin(ang), z_v)))
                # Mid-edge vertex for curved flying eave dip between corners
                ang_m = ang + math.pi / sides
                r_m = r_base * math.cos(math.pi / sides)
                z_m = z_base
                ring.append(bm.verts.new((r_m * math.cos(ang_m), r_m * math.sin(ang_m), z_m)))
            v_rings.append(ring)

        apex = bm.verts.new((0.0, 0.0, height))
        n_ring_pts = sides * 2
        for i in range(n_ring_pts):
            j = (i + 1) % n_ring_pts
            bm.faces.new((apex, v_rings[0][i], v_rings[0][j]))
        for ri in range(len(v_rings) - 1):
            r0 = v_rings[ri]
            r1 = v_rings[ri + 1]
            for i in range(n_ring_pts):
                j = (i + 1) % n_ring_pts
                bm.faces.new((r0[i], r1[i], r1[j], r0[j]))

        # Underside soffit cap
        bot_ring = v_rings[-1]
        center_bot = bm.verts.new((0.0, 0.0, 0.0))
        for i in range(n_ring_pts):
            j = (i + 1) % n_ring_pts
            bm.faces.new((center_bot, bot_ring[j], bot_ring[i]))

        all_v = [apex, center_bot] + [v for r in v_rings for v in r]
        self._xform(all_v, center=center, rot_z=rot_z)

        # Corner hip ridges
        for k in range(sides):
            ang = rot_z + (2.0 * math.pi * k / sides) + math.pi / sides
            rx = radius * 0.52 * math.cos(ang)
            ry = radius * 0.52 * math.sin(ang)
            diag = math.hypot(radius * 0.98, height * 0.92)
            pitch = math.atan2(height * 0.92, radius * 0.98)
            self.add_box(
                mat_ridge, diag, 0.16, 0.16,
                center=(center[0] + rx, center[1] + ry, center[2] + height * 0.48),
                rot_euler=(0.0, pitch, ang)
            )

        if finial:
            self.add_cylinder(finial_mat, 0.28, 0.04, 1.05, segments=8,
                              center=(center[0], center[1], center[2] + height + 0.50))
            self.add_ico(finial_mat, radius=0.22, subdivisions=1,
                         center=(center[0], center[1], center[2] + height + 0.25))

    def add_oct_pagoda_eave(self, inner_r, outer_r, eave_h, center=(0, 0, 0), rot_z=0.0,
                            corner_lift=0.65, mat_tile="dark_tile", mat_ridge="tile_ridge",
                            emissive_band="emissive_warm"):
        """Single tier octagonal upturned flying eave ring for Song/Ming pagodas."""
        bm = self.bm(mat_tile)
        sides = 8
        steps = 3
        v_rings = []
        for si in range(steps + 1):
            s = si / steps
            r_cur = inner_r + (outer_r - inner_r) * s
            z_cur = eave_h * (1.0 - s) - 0.16 * eave_h * math.sin(math.pi * s)
            ring = []
            for k in range(sides):
                ang = (2.0 * math.pi * k / sides) + math.pi / sides
                r_v = r_cur * (1.0 + 0.08 * (s ** 2.0))
                z_v = z_cur + corner_lift * (s ** 2.2)
                ring.append(bm.verts.new((r_v * math.cos(ang), r_v * math.sin(ang), z_v)))
                ang_m = ang + math.pi / sides
                r_m = r_cur * math.cos(math.pi / sides)
                ring.append(bm.verts.new((r_m * math.cos(ang_m), r_m * math.sin(ang_m), z_cur)))
            v_rings.append(ring)

        n_pts = sides * 2
        for si in range(steps):
            r0, r1 = v_rings[si], v_rings[si + 1]
            for i in range(n_pts):
                j = (i + 1) % n_pts
                bm.faces.new((r0[i], r1[i], r1[j], r0[j]))

        # Underside soffit ring
        r_in = v_rings[0]
        r_out = v_rings[-1]
        r_in_bot = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in r_in]
        for i in range(n_pts):
            j = (i + 1) % n_pts
            bm.faces.new((r_out[i], r_in_bot[i], r_in_bot[j], r_out[j]))

        all_v = [v for r in v_rings for v in r] + r_in_bot
        self._xform(all_v, center=center, rot_z=rot_z)

        # Glowing under-eave warm uplight band
        if emissive_band:
            self.add_cylinder(
                emissive_band,
                radius1=outer_r * 0.90,
                radius2=outer_r * 0.92,
                depth=0.22,
                segments=8,
                center=(center[0], center[1], center[2] + 0.06),
                rot_z=rot_z + math.pi / 8,
                cap_ends=False,
            )

    def add_oct_pagoda(self, center=(0, 0, 0), stories=7, total_height=33.3,
                       base_radius=5.2, taper=0.58, has_balcony=True,
                       has_podium=True, podium_h=2.2, brick_mat="pagoda_brick",
                       eave_mat="dark_tile", spire_ratio=0.19,
                       emissive_eave="emissive_warm", emissive_spire="emissive_gold"):
        """
        Full architectural octagonal Chinese pagoda (Song/Ming style).
        Total height from center.z to spire tip = total_height.
        """
        cx, cy, cz = center
        cur_z = cz
        if has_podium:
            # Stepped octagonal Sumeru stone podium + skirt down to -2.5
            self.add_cylinder("stone_dark", base_radius * 1.48, base_radius * 1.45,
                              2.5, segments=8, center=(cx, cy, cz - 1.25), rot_z=math.pi / 8)
            self.add_cylinder("stone_light", base_radius * 1.45, base_radius * 1.38,
                              podium_h * 0.65, segments=8,
                              center=(cx, cy, cz + podium_h * 0.325), rot_z=math.pi / 8)
            self.add_cylinder("stone_dark", base_radius * 1.32, base_radius * 1.28,
                              podium_h * 0.35, segments=8,
                              center=(cx, cy, cz + podium_h * 0.825), rot_z=math.pi / 8)
            # Warm perimeter uplight ring at base
            self.add_cylinder(emissive_eave, base_radius * 1.25, base_radius * 1.25,
                              0.26, segments=8,
                              center=(cx, cy, cz + podium_h + 0.12), rot_z=math.pi / 8,
                              cap_ends=False)
            cur_z += podium_h

        spire_h = total_height * spire_ratio
        top_roof_h = (total_height - podium_h - spire_h) * 0.12
        body_h = total_height - (cur_z - cz) - spire_h - top_roof_h

        # Story heights taper slightly upwards
        weights = [1.0 - 0.25 * (i / max(1, stories - 1)) for i in range(stories)]
        w_sum = sum(weights)

        for i in range(stories):
            t = i / max(1, stories - 1)
            sh = body_h * (weights[i] / w_sum)
            r_core = base_radius * (1.0 - (1.0 - taper) * t)
            r_next = base_radius * (1.0 - (1.0 - taper) * min(1.0, (i + 1) / max(1, stories)))

            # Core octagonal wall shaft
            self.add_cylinder(brick_mat, r_core, r_core * 0.97, sh * 0.82,
                              segments=8, center=(cx, cy, cur_z + sh * 0.41),
                              rot_z=math.pi / 8)

            # Recessed dark-wood arched doors / niches on 4 cardinal faces (alternating)
            for k in range(4):
                ang = (math.pi * 0.5 * k) + (math.pi * 0.25 if (i % 2 == 1) else 0.0)
                dist = r_core * 0.91
                dx = cx + dist * math.cos(ang)
                dy = cy + dist * math.sin(ang)
                door_w = r_core * 0.34
                door_h = sh * 0.46
                self.add_box("dark_wood", 0.32, door_w, door_h,
                             center=(dx, dy, cur_z + door_h * 0.52), rot_z=ang)
                # Subtle warm interior light behind arched door
                self.add_box("emissive_win", 0.16, door_w * 0.56, door_h * 0.64,
                             center=(cx + (dist + 0.12) * math.cos(ang),
                                     cy + (dist + 0.12) * math.sin(ang),
                                     cur_z + door_h * 0.52), rot_z=ang)

            # Wrap-around dark timber balcony (平座) with railing
            if has_balcony:
                bal_r = r_core * 1.18
                self.add_cylinder("dark_wood", bal_r, bal_r, 0.30,
                                  segments=8, center=(cx, cy, cur_z + 0.15),
                                  rot_z=math.pi / 8)
                # Railing ring
                for k in range(8):
                    ang = 2.0 * math.pi * k / 8
                    ang2 = 2.0 * math.pi * (k + 1) / 8
                    mx = cx + bal_r * 0.94 * math.cos((ang + ang2) * 0.5)
                    my = cy + bal_r * 0.94 * math.sin((ang + ang2) * 0.5)
                    side_len = 2.0 * bal_r * 0.94 * math.sin(math.pi / 8)
                    self.add_box("vermilion" if stories >= 9 else "dark_wood",
                                 0.14, side_len, 0.72,
                                 center=(mx, my, cur_z + 0.62), rot_z=(ang + ang2) * 0.5)
                    # Corner column
                    px = cx + bal_r * 0.92 * math.cos(ang + math.pi / 8)
                    py = cy + bal_r * 0.92 * math.sin(ang + math.pi / 8)
                    self.add_cylinder("dark_wood", 0.16, 0.15, sh * 0.74,
                                      segments=6, center=(px, py, cur_z + sh * 0.37))

            # Dougong bracket band beneath eaves
            self.add_cylinder("dark_wood", r_core * 1.06, r_core * 1.16, sh * 0.14,
                              segments=8, center=(cx, cy, cur_z + sh * 0.76),
                              rot_z=math.pi / 8)

            # Sweeping octagonal upturned eave
            eave_outer = r_core * (1.46 if stories >= 9 else 1.38)
            eave_h = sh * 0.34
            self.add_oct_pagoda_eave(
                inner_r=r_core * 0.96,
                outer_r=eave_outer,
                eave_h=eave_h,
                center=(cx, cy, cur_z + sh * 0.76),
                corner_lift=0.68 if stories >= 9 else 0.45,
                mat_tile=eave_mat,
                emissive_band=emissive_eave,
            )
            cur_z += sh

        # Topmost pyramidal octagonal roof
        top_r = base_radius * taper * 1.35
        self.add_radial_roof(
            sides=8, radius=top_r, height=top_roof_h,
            center=(cx, cy, cur_z - 0.15), corner_lift=0.75,
            mat_tile=eave_mat, finial=False
        )
        cur_z += top_roof_h - 0.15

        # Ornate bronze & golden spire finial (塔刹: 覆盆 + 相轮 + 宝瓶)
        self.add_cylinder("bronze", top_r * 0.36, top_r * 0.22, spire_h * 0.16,
                          segments=8, center=(cx, cy, cur_z + spire_h * 0.08))
        # Spire shaft
        self.add_cylinder("bronze", top_r * 0.09, top_r * 0.02, spire_h * 0.88,
                          segments=8, center=(cx, cy, cur_z + spire_h * 0.56))
        # Stacked glowing golden rings (相轮)
        for ri in range(5):
            rz = cur_z + spire_h * (0.24 + ri * 0.11)
            rr = top_r * (0.22 - ri * 0.025)
            self.add_cylinder(emissive_spire, rr, rr * 0.92, spire_h * 0.055,
                              segments=8, center=(cx, cy, rz))
        # Crown gourd / jewel at apex
        self.add_ico(emissive_spire, radius=top_r * 0.11, subdivisions=1,
                     scale=(1.0, 1.0, 1.55),
                     center=(cx, cy, cur_z + spire_h * 0.90))

    def add_pavilion(self, center=(0, 0, 0), radius=3.6, sides=6, col_h=3.4,
                     podium_h=0.6, double_eave=False, rot_z=0.0,
                     col_mat="dark_wood", bench_mat="warm_wood", lantern=True):
        """Classical Suzhou garden pavilion (hexagonal/octagonal/square) with bench & lantern."""
        cx, cy, cz = center
        # Stone base
        self.add_cylinder("stone_light", radius * 1.08, radius * 1.04, podium_h,
                          segments=sides, center=(cx, cy, cz + podium_h * 0.5),
                          rot_z=rot_z + math.pi / sides)
        z0 = cz + podium_h
        # Columns + curved Meirenkao bench rail
        for k in range(sides):
            ang = rot_z + (2.0 * math.pi * k / sides) + math.pi / sides
            px = cx + radius * 0.84 * math.cos(ang)
            py = cy + radius * 0.84 * math.sin(ang)
            self.add_cylinder(col_mat, 0.13, 0.12, col_h, segments=6,
                              center=(px, py, z0 + col_h * 0.5))
            # Bench segment on all sides except entrance (k == 0)
            if k != 0:
                ang2 = rot_z + (2.0 * math.pi * (k + 1) / sides) + math.pi / sides
                mx = cx + radius * 0.82 * math.cos((ang + ang2) * 0.5)
                my = cy + radius * 0.82 * math.sin((ang + ang2) * 0.5)
                seg_len = 2.0 * radius * 0.82 * math.sin(math.pi / sides)
                self.add_box(bench_mat, 0.36, seg_len * 0.92, 0.52,
                             center=(mx, my, z0 + 0.35), rot_z=(ang + ang2) * 0.5)

        # Top lintel ring
        self.add_cylinder(col_mat, radius * 0.88, radius * 0.88, 0.30,
                          segments=sides, center=(cx, cy, z0 + col_h - 0.15),
                          rot_z=rot_z + math.pi / sides)

        # Swept upturned roof
        if double_eave:
            self.add_radial_roof(sides, radius * 1.48, 1.5,
                                 center=(cx, cy, z0 + col_h - 0.15), rot_z=rot_z,
                                 corner_lift=0.55, finial=False)
            self.add_cylinder("white_wall", radius * 0.65, radius * 0.65, 1.0,
                              segments=sides, center=(cx, cy, z0 + col_h + 1.15),
                              rot_z=rot_z + math.pi / sides)
            self.add_radial_roof(sides, radius * 1.08, 2.2,
                                 center=(cx, cy, z0 + col_h + 1.55), rot_z=rot_z,
                                 corner_lift=0.65, finial=True)
        else:
            self.add_radial_roof(sides, radius * 1.45, radius * 0.72,
                                 center=(cx, cy, z0 + col_h - 0.15), rot_z=rot_z,
                                 corner_lift=0.55, finial=True)

        # Hanging warm palace lantern inside
        if lantern:
            self.add_cylinder("dark_wood", 0.03, 0.03, 0.8, segments=4,
                              center=(cx, cy, z0 + col_h - 0.45))
            self.add_ico("emissive_warm", radius=0.34, subdivisions=1,
                         scale=(1.0, 1.0, 1.3), center=(cx, cy, z0 + col_h - 1.05))

    def add_suzhou_house(self, w=9.0, d=6.2, h=6.4, stories=2, center=(0, 0, 0),
                         rot_z=0.0, matouqiang=True, warm_windows=True,
                         waterfront_balcony=False, wall_mat="white_wall"):
        """Classic Suzhou white-wall dark-tile courtyard/canal house."""
        cx, cy, cz = center
        # Stone plinth
        self.add_box("stone_dark", w + 0.25, d + 0.25, 0.45,
                     center=(cx, cy, cz + 0.225), rot_z=rot_z)
        # Main white plaster body
        self.add_box(wall_mat, w, d, h, center=(cx, cy, cz + 0.45 + h * 0.5), rot_z=rot_z)

        # Dark timber horizontal stringcourse between floors + corner pilasters
        if stories >= 2:
            self.add_box("dark_wood", w + 0.12, d + 0.12, 0.22,
                         center=(cx, cy, cz + 0.45 + h * 0.48), rot_z=rot_z)
        for sx in (-1, 1):
            for sy in (-1, 1):
                lx = sx * (w * 0.49)
                ly = sy * (d * 0.49)
                wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                self.add_box("dark_wood", 0.22, 0.22, h,
                             center=(wx, wy, cz + 0.45 + h * 0.5), rot_z=rot_z)

        # Warm glowing wooden lattice windows on front & back facades
        if warm_windows:
            n_win = max(2, int(w / 2.6))
            for st in range(stories):
                wz = cz + 0.45 + (st + 0.52) * (h / stories)
                for side in (-1.0, 1.0):
                    for wi in range(n_win):
                        lx = (-0.36 + 0.72 * wi / max(1, n_win - 1)) * w
                        ly = side * (d * 0.5 + 0.04)
                        wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                        wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                        # Timber frame
                        self.add_box("dark_wood", 1.35, 0.14, 1.45,
                                     center=(wx, wy, wz), rot_z=rot_z)
                        # Warm glowing pane
                        ly2 = side * (d * 0.5 + 0.08)
                        wx2 = cx + lx * math.cos(rot_z) - ly2 * math.sin(rot_z)
                        wy2 = cy + lx * math.sin(rot_z) + ly2 * math.cos(rot_z)
                        self.add_box("emissive_win", 1.05, 0.08, 1.15,
                                     center=(wx2, wy2, wz), rot_z=rot_z)

        # Optional cantilevered wooden waterfront balcony
        if waterfront_balcony:
            ly = -(d * 0.5 + 0.55)
            wx = cx - ly * math.sin(rot_z)
            wy = cy + ly * math.cos(rot_z)
            bz = cz + 0.45 + h * 0.48
            self.add_box("dark_wood", w * 0.78, 1.1, 0.18, center=(wx, wy, bz), rot_z=rot_z)
            self.add_box("warm_wood", w * 0.78, 0.12, 0.75,
                         center=(cx - (ly - 0.5) * math.sin(rot_z),
                                 cy + (ly - 0.5) * math.cos(rot_z), bz + 0.42),
                         rot_z=rot_z)

        # Swept Jiangnan tiled roof
        roof_h = max(1.8, d * 0.36)
        self.add_suzhou_roof(
            w=w, d=d, h=roof_h,
            center=(cx, cy, cz + 0.45 + h - 0.15), rot_z=rot_z,
            eave_overhang=0.72, corner_lift=0.35, hip_gable=not matouqiang,
            add_ribs=False
        )

        # Stepped Horse-Head Gable Walls (马头墙) on East & West ends
        if matouqiang:
            for xs in (-1.0, 1.0):
                lx = xs * (w * 0.5 + 0.12)
                for step_i, (sd, sh_add) in enumerate([(d + 0.9, 0.7), (d * 0.62, 1.55), (d * 0.30, 2.35)]):
                    wx = cx + lx * math.cos(rot_z)
                    wy = cy + lx * math.sin(rot_z)
                    z_top = cz + 0.45 + h + sh_add
                    self.add_box(wall_mat, 0.32, sd, sh_add + 0.4,
                                 center=(wx, wy, cz + 0.45 + h + sh_add * 0.5 - 0.2), rot_z=rot_z)
                    self.add_box("dark_tile", 0.54, sd + 0.28, 0.18,
                                 center=(wx, wy, z_top + 0.06), rot_z=rot_z)

    def add_hall(self, w=14.0, d=9.0, h=4.6, center=(0, 0, 0), rot_z=0.0,
                 podium_h=0.9, double_eave=False, col_mat="dark_wood", wall_mat="white_wall",
                 open_front=True):
        """Classical Suzhou garden hall (堂/轩) with stone terrace, colonnade & double/single upturned roof."""
        cx, cy, cz = center
        # Stone terrace
        self.add_box("stone_light", w + 2.4, d + 2.6, podium_h,
                     center=(cx, cy, cz + podium_h * 0.5), rot_z=rot_z)
        z0 = cz + podium_h

        # Inner core room (recessed behind veranda columns)
        core_w = w - 1.6
        core_d = d - 2.0
        self.add_box(wall_mat, core_w, core_d, h, center=(cx, cy, z0 + h * 0.5), rot_z=rot_z)

        # Warm glowing lattice window panels along front & back
        n_bays = max(3, int(w / 3.0))
        for side in (-1.0, 1.0):
            if not open_front and side < 0:
                continue
            for bi in range(n_bays):
                lx = (-0.40 + 0.80 * bi / max(1, n_bays - 1)) * core_w
                ly = side * (core_d * 0.5 + 0.06)
                wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                self.add_box("dark_wood", 1.8, 0.16, h * 0.68,
                             center=(wx, wy, z0 + h * 0.48), rot_z=rot_z)
                self.add_box("emissive_win", 1.4, 0.10, h * 0.54,
                             center=(wx + side * 0.05 * (-math.sin(rot_z)),
                                     wy + side * 0.05 * math.cos(rot_z),
                                     z0 + h * 0.48), rot_z=rot_z)

        # Perimeter veranda columns
        n_cols = n_bays + 1
        for ci in range(n_cols):
            lx = -w * 0.48 + (w * 0.96) * ci / max(1, n_cols - 1)
            for sy in (-1.0, 1.0):
                ly = sy * (d * 0.48)
                wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                self.add_cylinder(col_mat, 0.17, 0.16, h, segments=6,
                                  center=(wx, wy, z0 + h * 0.5))

        # Roof(s)
        if double_eave:
            self.add_suzhou_roof(w + 0.6, d + 0.6, 2.2,
                                 center=(cx, cy, z0 + h - 0.15), rot_z=rot_z,
                                 eave_overhang=1.1, corner_lift=0.60, hip_gable=True)
            self.add_box(wall_mat, w * 0.72, d * 0.66, 1.35,
                         center=(cx, cy, z0 + h + 1.65), rot_z=rot_z)
            self.add_suzhou_roof(w * 0.76, d * 0.70, 2.8,
                                 center=(cx, cy, z0 + h + 2.25), rot_z=rot_z,
                                 eave_overhang=1.0, corner_lift=0.68, hip_gable=True)
        else:
            self.add_suzhou_roof(w + 0.4, d + 0.4, max(2.4, d * 0.34),
                                 center=(cx, cy, z0 + h - 0.15), rot_z=rot_z,
                                 eave_overhang=1.1, corner_lift=0.55, hip_gable=True)

    def add_corridor_segment(self, p0, p1, width=2.4, height=3.1, z0=0.0,
                             col_mat="dark_wood", has_back_wall=False,
                             vermilion=False, lantern=False):
        """Covered Suzhou garden corridor (长廊) connecting p0=(x,y) to p1=(x,y)."""
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        length = math.hypot(dx, dy)
        if length < 0.5:
            return
        ang = math.atan2(dy, dx)
        mx = (p0[0] + p1[0]) * 0.5
        my = (p0[1] + p1[1]) * 0.5
        cm = "vermilion" if vermilion else col_mat

        # Floor deck
        self.add_box("stone_light", length + 0.5, width, 0.35,
                     center=(mx, my, z0 + 0.175), rot_z=ang)
        # Columns along both edges
        n_bays = max(2, int(round(length / 3.2)))
        for i in range(n_bays + 1):
            t = i / n_bays
            px = p0[0] + dx * t
            py = p0[1] + dy * t
            for side in (-1.0, 1.0):
                ox = -math.sin(ang) * side * (width * 0.44)
                oy = math.cos(ang) * side * (width * 0.44)
                self.add_cylinder(cm, 0.11, 0.10, height, segments=6,
                                  center=(px + ox, py + oy, z0 + 0.35 + height * 0.5))
        # Side railing / bench
        for side in (-1.0, 1.0):
            if has_back_wall and side > 0:
                ox = -math.sin(ang) * side * (width * 0.46)
                oy = math.cos(ang) * side * (width * 0.46)
                self.add_box("white_wall", length, 0.28, height,
                             center=(mx + ox, my + oy, z0 + 0.35 + height * 0.5), rot_z=ang)
            else:
                ox = -math.sin(ang) * side * (width * 0.44)
                oy = math.cos(ang) * side * (width * 0.44)
                self.add_box(cm, length, 0.14, 0.65,
                             center=(mx + ox, my + oy, z0 + 0.35 + 0.42), rot_z=ang)

        # Swept roof
        self.add_suzhou_roof(
            w=length + 0.6, d=width + 0.3, h=1.15,
            center=(mx, my, z0 + 0.35 + height - 0.12), rot_z=ang,
            eave_overhang=0.55, corner_lift=0.22, hip_gable=False, add_ribs=False
        )
        if lantern:
            self.add_ico("emissive_red" if vermilion else "emissive_warm",
                         radius=0.24, subdivisions=1, scale=(1.0, 1.0, 1.25),
                         center=(mx, my, z0 + 0.35 + height - 0.55))

    def add_garden_wall(self, p0, p1, height=3.6, thickness=0.42, z0=0.0,
                        wall_mat="white_wall", cap_mat="dark_tile", wave_cap=True):
        """White Suzhou perimeter wall with dark grey tile coping."""
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        length = math.hypot(dx, dy)
        if length < 0.3:
            return
        ang = math.atan2(dy, dx)
        mx = (p0[0] + p1[0]) * 0.5
        my = (p0[1] + p1[1]) * 0.5
        # Skirt + wall
        self.add_box(wall_mat, length + 0.2, thickness, height + 0.6,
                     center=(mx, my, z0 + height * 0.5 - 0.3), rot_z=ang)
        if wave_cap and length > 8.0:
            segs = max(4, int(length / 4.5))
            for i in range(segs):
                t0 = i / segs
                t1 = (i + 1) / segs
                tm = (t0 + t1) * 0.5
                seg_l = length / segs
                wave = 0.28 * math.sin(math.pi * 2.0 * tm * max(1, int(length / 16.0)))
                sx = p0[0] + dx * tm
                sy = p0[1] + dy * tm
                self.add_box(cap_mat, seg_l + 0.15, thickness + 0.42, 0.26,
                             center=(sx, sy, z0 + height + 0.10 + wave), rot_z=ang)
        else:
            self.add_box(cap_mat, length + 0.3, thickness + 0.42, 0.26,
                         center=(mx, my, z0 + height + 0.10), rot_z=ang)

    def add_arch_bridge(self, span=14.0, width=3.4, arch_h=3.2, center=(0, 0, 0),
                        rot_z=0.0, mat_stone="stone_light", mat_dark="stone_dark",
                        lanterns=True):
        """
        True vaulted stone arch bridge spanning along local X from -span/2 to +span/2.
        Leaves clean open arch underneath!
        """
        cx, cy, cz = center
        segs = 10
        half_s = span * 0.5
        half_w = width * 0.5
        bm = self.bm(mat_stone)

        # Build arch deck ribbon with thickness
        rings = []
        for i in range(segs + 1):
            u = -1.0 + 2.0 * i / segs  # -1..1
            x = u * half_s
            # Parabolic arch crown
            arch_z = arch_h * (1.0 - u * u)
            thick = 0.52 + 0.45 * (u * u)
            z_top = arch_z + 0.35
            z_bot = max(-2.2, arch_z - thick)
            rings.append([
                (x, -half_w, z_bot),
                (x, half_w, z_bot),
                (x, half_w, z_top),
                (x, -half_w, z_top),
            ])
        self.add_loft(mat_stone, rings, closed_caps=True, center=(cx, cy, cz), rot_z=rot_z)

        # Abutment piers down to Z=-2.5
        for xs in (-1.0, 1.0):
            lx = xs * (half_s + 0.7)
            wx = cx + lx * math.cos(rot_z)
            wy = cy + lx * math.sin(rot_z)
            self.add_box(mat_dark, 1.8, width + 0.35, 3.0,
                         center=(wx, wy, cz - 1.15), rot_z=rot_z)

        # Carved stone parapets + posts following the arch curve
        for side in (-1.0, 1.0):
            ly = side * (half_w - 0.16)
            for i in range(segs):
                u0 = -1.0 + 2.0 * i / segs
                u1 = -1.0 + 2.0 * (i + 1) / segs
                um = (u0 + u1) * 0.5
                x0, x1 = u0 * half_s, u1 * half_s
                z0 = arch_h * (1.0 - u0 * u0) + 0.35
                z1 = arch_h * (1.0 - u1 * u1) + 0.35
                seg_l = math.hypot(x1 - x0, z1 - z0)
                pitch = -math.atan2(z1 - z0, x1 - x0)
                lx = um * half_s
                wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                self.add_box(mat_stone, seg_l + 0.08, 0.24, 0.82,
                             center=(wx, wy, cz + (z0 + z1) * 0.5 + 0.41),
                             rot_euler=(0.0, pitch, rot_z))
            # Crown & end stone finials
            for u_p in (-0.95, 0.0, 0.95):
                lx = u_p * half_s
                pz = arch_h * (1.0 - u_p * u_p) + 0.35
                wx = cx + lx * math.cos(rot_z) - ly * math.sin(rot_z)
                wy = cy + lx * math.sin(rot_z) + ly * math.cos(rot_z)
                self.add_box(mat_dark, 0.34, 0.34, 1.08,
                             center=(wx, wy, cz + pz + 0.54), rot_z=rot_z)
                if lanterns and abs(u_p) < 0.1:
                    self.add_ico("emissive_warm", radius=0.22, subdivisions=1,
                                 center=(wx, wy, cz + pz + 1.24))

    def add_zigzag_bridge(self, pts, width=1.8, z_deck=0.25, mat_deck="stone_light",
                          mat_rail="stone_dark", with_rails=True):
        """Classical nine-turn zigzag stone bridge (九曲桥) over pond water."""
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i + 1]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            length = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            mx, my = (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5
            self.add_box(mat_deck, length + 0.3, width, 0.24,
                         center=(mx, my, z_deck), rot_z=ang)
            # Support pier at vertex
            self.add_box(mat_rail, 0.45, 0.45, 1.8, center=(p0[0], p0[1], z_deck - 0.95))
            if with_rails:
                for side in (-1.0, 1.0):
                    ox = -math.sin(ang) * side * (width * 0.44)
                    oy = math.cos(ang) * side * (width * 0.44)
                    self.add_box(mat_deck, length, 0.12, 0.48,
                                 center=(mx + ox, my + oy, z_deck + 0.34), rot_z=ang)
        # Last pier
        p_end = pts[-1]
        self.add_box(mat_rail, 0.45, 0.45, 1.8, center=(p_end[0], p_end[1], z_deck - 0.95))

    def add_taihu_rock_cluster(self, center=(0, 0, 0), radius=6.0, height=5.5,
                               lobes=9, seed=42, mat="taihu_rock", mat_dark="taihu_dark"):
        """Sculpted craggy Taihu limestone rockery with overhanging peaks & crevices."""
        rng = random.Random(seed)
        cx, cy, cz = center
        for i in range(lobes):
            ang = (2.0 * math.pi * i / max(1, lobes)) + rng.uniform(-0.35, 0.35)
            dist = radius * rng.uniform(0.05, 0.72) if i > 0 else 0.0
            rx = cx + dist * math.cos(ang)
            ry = cy + dist * math.sin(ang)
            h_scale = height * (rng.uniform(0.75, 1.15) if i < 2 else rng.uniform(0.35, 0.80))
            w_scale = radius * rng.uniform(0.24, 0.46)
            m = mat if i % 3 != 0 else mat_dark
            # Wider top / narrow waist Taihu silhouette (瘦皱漏透)
            self.add_ico(
                m, radius=1.0, subdivisions=1,
                scale=(w_scale, w_scale * rng.uniform(0.7, 1.25), h_scale * 0.55),
                center=(rx, ry, cz + h_scale * 0.42),
                rot_euler=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, 6.28)),
                jitter=0.32, rng=rng
            )
            if i < 3:
                # Upper overhanging crag
                self.add_ico(
                    mat, radius=1.0, subdivisions=1,
                    scale=(w_scale * 0.85, w_scale * 0.75, h_scale * 0.38),
                    center=(rx + rng.uniform(-0.8, 0.8), ry + rng.uniform(-0.8, 0.8),
                            cz + h_scale * 0.82),
                    rot_euler=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 6.28)),
                    jitter=0.35, rng=rng
                )

    def add_willow_tree(self, center=(0, 0, 0), height=8.5, lean=(0.6, 0.0), seed=11):
        """Graceful Jiangnan weeping willow with leaning trunk and cascading foliage curtains."""
        rng = random.Random(seed)
        cx, cy, cz = center
        trunk_h = height * 0.52
        # Lower leaning trunk
        tilt_x = math.atan2(lean[1], trunk_h)
        tilt_y = math.atan2(lean[0], trunk_h)
        self.add_cylinder("bark", 0.34, 0.22, trunk_h, segments=6,
                          center=(cx + lean[0] * 0.5, cy + lean[1] * 0.5, cz + trunk_h * 0.5),
                          rot_euler=(-tilt_x, tilt_y, 0.0))
        top_x = cx + lean[0]
        top_y = cy + lean[1]
        top_z = cz + trunk_h
        # Upper crown dome
        self.add_ico("willow", radius=height * 0.28, subdivisions=1,
                     scale=(1.15, 1.15, 0.75),
                     center=(top_x, top_y, top_z + height * 0.20), jitter=0.18, rng=rng)
        # Drooping willow frond curtains hanging downwards
        n_fronds = 7
        for i in range(n_fronds):
            ang = (2.0 * math.pi * i / n_fronds) + rng.uniform(-0.25, 0.25)
            r_off = height * rng.uniform(0.18, 0.34)
            fx = top_x + r_off * math.cos(ang)
            fy = top_y + r_off * math.sin(ang)
            drop_h = height * rng.uniform(0.38, 0.56)
            self.add_cylinder("willow", height * 0.11, height * 0.04, drop_h,
                              segments=5, center=(fx, fy, top_z + height * 0.10 - drop_h * 0.45))

    def add_pine_tree(self, center=(0, 0, 0), height=9.5, seed=21):
        """Sculptural classical Chinese garden pine (迎客松/古松) with layered flat canopy pads."""
        rng = random.Random(seed)
        cx, cy, cz = center
        self.add_cylinder("bark", 0.32, 0.16, height * 0.76, segments=6,
                          center=(cx, cy, cz + height * 0.38),
                          rot_euler=(rng.uniform(-0.10, 0.10), rng.uniform(-0.10, 0.10), 0.0))
        # Layered horizontal cloud-pad canopies
        pads = [
            (0.0, 0.0, 0.90, 0.28, 0.10),
            (0.20, 0.08, 0.74, 0.26, 0.09),
            (-0.18, -0.10, 0.64, 0.24, 0.09),
            (0.06, -0.22, 0.54, 0.21, 0.08),
        ]
        rot = rng.uniform(0, 6.28)
        for ox, oy, hz, rad, th in pads:
            rx = (ox * math.cos(rot) - oy * math.sin(rot)) * height
            ry = (ox * math.sin(rot) + oy * math.cos(rot)) * height
            self.add_ico("pine", radius=height * rad, subdivisions=1,
                         scale=(1.1, 0.9, th / rad),
                         center=(cx + rx, cy + ry, cz + height * hz),
                         jitter=0.16, rng=rng)

    def add_bamboo_clump(self, center=(0, 0, 0), count=6, height=6.5, spread=1.6, seed=31):
        """Slender emerald bamboo grove."""
        rng = random.Random(seed)
        cx, cy, cz = center
        for _ in range(count):
            bx = cx + rng.uniform(-spread, spread)
            by = cy + rng.uniform(-spread, spread)
            bh = height * rng.uniform(0.75, 1.15)
            self.add_cylinder("bamboo", 0.07, 0.04, bh, segments=5,
                              center=(bx, by, cz + bh * 0.5),
                              rot_euler=(rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), 0.0))
            self.add_ico("bamboo", radius=0.65, subdivisions=1,
                         scale=(1.2, 1.2, 0.55), center=(bx, by, cz + bh * 0.88),
                         jitter=0.22, rng=rng)

    def add_wooden_boat(self, center=(0, 0, 0), rot_z=0.0, length=6.8, width=1.65):
        """Traditional Suzhou wooden awning boat (摇橹乌篷船) with glowing bow lantern."""
        cx, cy, cz = center
        # Tapered hull loft
        hl = length * 0.5
        hw = width * 0.5
        rings = [
            [(-hl, -0.10, 0.35), (-hl, 0.10, 0.35), (-hl, 0.08, 0.12), (-hl, -0.08, 0.12)],
            [(-hl * 0.55, -hw * 0.85, 0.42), (-hl * 0.55, hw * 0.85, 0.42),
             (-hl * 0.55, hw * 0.65, -0.12), (-hl * 0.55, -hw * 0.65, -0.12)],
            [(0.0, -hw, 0.44), (0.0, hw, 0.44), (0.0, hw * 0.78, -0.16), (0.0, -hw * 0.78, -0.16)],
            [(hl * 0.55, -hw * 0.82, 0.42), (hl * 0.55, hw * 0.82, 0.42),
             (hl * 0.55, hw * 0.62, -0.12), (hl * 0.55, -hw * 0.62, -0.12)],
            [(hl, -0.10, 0.42), (hl, 0.10, 0.42), (hl, 0.08, 0.16), (hl, -0.08, 0.16)],
        ]
        self.add_loft("dark_wood", rings, closed_caps=True, center=(cx, cy, cz), rot_z=rot_z)
        # Arched dark bamboo-mat canopy awning in center
        self.add_cylinder("boat_awning", hw * 0.92, hw * 0.92, length * 0.46, segments=8,
                          center=(cx, cy, cz + 0.55),
                          rot_euler=(0.0, math.pi * 0.5, rot_z))
        # Warm glowing bow lantern
        bx = cx + (hl * 0.72) * math.cos(rot_z)
        by = cy + (hl * 0.72) * math.sin(rot_z)
        self.add_cylinder("dark_wood", 0.03, 0.03, 0.95, segments=4,
                          center=(bx, by, cz + 0.82))
        self.add_ico("emissive_red", radius=0.22, subdivisions=1, scale=(1.0, 1.0, 1.3),
                     center=(bx, by, cz + 1.25))

    def add_lantern_string(self, p0, p1, count=6, sag=0.8, lantern_r=0.24, mat="emissive_red"):
        """Catenary string of glowing red lanterns."""
        for i in range(count):
            t = (i + 0.5) / count
            x = p0[0] + (p1[0] - p0[0]) * t
            y = p0[1] + (p1[1] - p0[1]) * t
            z = p0[2] + (p1[2] - p0[2]) * t - sag * math.sin(math.pi * t)
            self.add_ico(mat, radius=lantern_r, subdivisions=1,
                         scale=(1.0, 1.0, 1.28), center=(x, y, z))

    def build_objects_by_material(self, prefix="Gusu"):
        """Convert each material's bmesh into a clean Blender object (low draw calls!)."""
        objs = []
        for mat_key, bm in self.bms.items():
            if len(bm.verts) == 0:
                bm.free()
                continue
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            mesh = bpy.data.meshes.new(f"{prefix}_{mat_key}_Mesh")
            bm.to_mesh(mesh)
            bm.free()
            obj = bpy.data.objects.new(f"{prefix}_{mat_key}", mesh)
            bpy.context.collection.objects.link(obj)
            obj.data.materials.append(self.palette[mat_key])
            objs.append(obj)
        self.bms.clear()
        return objs

    def build_single_named_object(self, name):
        """
        Combine all bmeshes in this builder into ONE multi-material Blender Mesh object
        with exact name `name` and origin at (0,0,0). Ideal for THREE.InstancedMesh kits!
        """
        merged_bm = bmesh.new()
        mat_list = []
        for mat_key, bm in self.bms.items():
            if len(bm.verts) == 0:
                bm.free()
                continue
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            mat_idx = len(mat_list)
            mat_list.append(self.palette[mat_key])
            # Copy geometry into merged_bm
            bm.verts.index_update()
            bm.verts.ensure_lookup_table()
            vert_map = {}
            for v in bm.verts:
                vert_map[v.index] = merged_bm.verts.new(v.co)
            merged_bm.verts.ensure_lookup_table()
            for f in bm.faces:
                try:
                    nf = merged_bm.faces.new([vert_map[v.index] for v in f.verts])
                    nf.material_index = mat_idx
                except ValueError:
                    pass
            bm.free()
        self.bms.clear()

        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        merged_bm.to_mesh(mesh)
        merged_bm.free()
        for m in mat_list:
            mesh.materials.append(m)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        return obj


def export_glb(filename):
    os.makedirs(MODEL_DIR, exist_ok=True)
    filepath = os.path.join(MODEL_DIR, filename)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_materials="EXPORT",
        export_yup=True,
    )
    size_kb = os.path.getsize(filepath) / 1024.0
    print(f"[EXPORTED] {filepath} ({size_kb:.1f} KB)")
    return filepath
