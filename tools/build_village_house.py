import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, base_color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get('Principled BSDF')
    if bsdf:
        if 'Base Color' in bsdf.inputs:
            bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        if 'Roughness' in bsdf.inputs:
            bsdf.inputs['Roughness'].default_value = roughness
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = metallic
    return mat

def create_beveled_box(name, size, location, mat, bevel_width=0.02, bevel_segments=2):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()

    obj.data.materials.append(mat)
    if bevel_width > 0:
        mod = obj.modifiers.new(name="Bevel", type='BEVEL')
        mod.width = bevel_width
        mod.segments = bevel_segments
        mod.limit_method = 'ANGLE'
    return obj

def build_fantasy_cottage():
    clear_scene()

    root = bpy.data.objects.new("House_Village_Root", None)
    bpy.context.collection.objects.link(root)

    # -------------------------------------------------------------
    # 1. PBR Color Palette (Strictly matching Blueprint Reference)
    # -------------------------------------------------------------
    mat_stucco       = create_pbr_material("Mat_PlasterStucco",   (0.96, 0.89, 0.74), roughness=0.72)
    mat_timber       = create_pbr_material("Mat_DarkTimber",      (0.36, 0.19, 0.09), roughness=0.55)
    mat_stone_base   = create_pbr_material("Mat_FoundationStone", (0.52, 0.50, 0.49), roughness=0.75)
    mat_stone_dark   = create_pbr_material("Mat_StoneMasonry",    (0.42, 0.40, 0.39), roughness=0.78)
    mat_chimney_rock = create_pbr_material("Mat_ChimneyRock",     (0.56, 0.53, 0.51), roughness=0.70)
    mat_roof_tile    = create_pbr_material("Mat_TerracottaRoof",  (0.85, 0.32, 0.18), roughness=0.48)
    mat_roof_trim    = create_pbr_material("Mat_RoofTrimWood",    (0.45, 0.22, 0.11), roughness=0.55)
    mat_wood_door    = create_pbr_material("Mat_WoodDoor",        (0.44, 0.23, 0.11), roughness=0.50)
    mat_window_glass = create_pbr_material("Mat_WindowGlass",     (0.18, 0.45, 0.70), roughness=0.08, metallic=0.10)
    mat_window_trim  = create_pbr_material("Mat_WindowTrim",      (0.32, 0.16, 0.08), roughness=0.55)
    mat_brass_knob   = create_pbr_material("Mat_BrassKnob",       (0.95, 0.78, 0.18), roughness=0.20, metallic=0.90)
    mat_grass        = create_pbr_material("Mat_LawnGrass",       (0.42, 0.64, 0.22), roughness=0.80)
    mat_path         = create_pbr_material("Mat_StonePath",       (0.68, 0.62, 0.54), roughness=0.75)
    mat_fence        = create_pbr_material("Mat_PicketFence",     (0.56, 0.36, 0.20), roughness=0.65)
    mat_foliage      = create_pbr_material("Mat_FoliageGreen",    (0.24, 0.56, 0.18), roughness=0.60)
    mat_flower_red   = create_pbr_material("Mat_FlowerRed",       (0.94, 0.18, 0.24), roughness=0.45)
    mat_flower_gold  = create_pbr_material("Mat_FlowerGold",      (0.98, 0.84, 0.12), roughness=0.45)
    mat_pot_clay     = create_pbr_material("Mat_ClayPot",         (0.76, 0.35, 0.17), roughness=0.60)

    # -------------------------------------------------------------
    # 2. Yard Base Ground Plate & Path
    # -------------------------------------------------------------
    yard = create_beveled_box("YardLawn", (8.4, 7.2, 0.2), (0.0, -0.2, -0.1), mat_grass, bevel_width=0.04)
    yard.parent = root

    path = create_beveled_box("GardenPath", (1.1, 2.4, 0.04), (0.0, -2.45, 0.02), mat_path, bevel_width=0.03)
    path.parent = root

    # -------------------------------------------------------------
    # 3. Stone Foundations
    # -------------------------------------------------------------
    base_main = create_beveled_box("FoundationMain", (3.26, 2.76, 0.44), (0.0, 0.0, 0.22), mat_stone_base, bevel_width=0.04)
    base_main.parent = root

    base_wing = create_beveled_box("FoundationWing", (1.85, 2.45, 0.40), (-2.42, 0.0, 0.20), mat_stone_base, bevel_width=0.04)
    base_wing.parent = root

    stone_locs = [
        (-1.58, -1.39, 0.22, 0.35, 0.12, 0.26),
        (-0.75, -1.39, 0.16, 0.42, 0.12, 0.22),
        ( 0.75, -1.39, 0.24, 0.38, 0.12, 0.24),
        ( 1.48, -1.39, 0.18, 0.36, 0.12, 0.25),
        (-3.25, -1.24, 0.20, 0.32, 0.12, 0.24),
        (-2.25, -1.24, 0.16, 0.44, 0.12, 0.20),
        (-1.62,  1.39, 0.20, 0.40, 0.12, 0.24),
        ( 0.00,  1.39, 0.18, 0.48, 0.12, 0.22),
        ( 1.48,  1.39, 0.22, 0.38, 0.12, 0.25),
        (-3.25,  1.24, 0.18, 0.35, 0.12, 0.22),
    ]
    for i, (sx, sy, sz, w, d, h) in enumerate(stone_locs):
        sblock = create_beveled_box(f"StoneDetail_{i}", (w, d, h), (sx, sy, sz), mat_stone_dark, bevel_width=0.02)
        sblock.parent = root

    # -------------------------------------------------------------
    # 4. Main House Stucco Body & Gable Geometry
    # -------------------------------------------------------------
    main_box = create_beveled_box("HouseMainBody", (3.0, 2.5, 3.31), (0.0, 0.0, 2.095), mat_stucco, bevel_width=0.02)
    main_box.parent = root

    # Triangular Gables (Front and Back, Z: 3.75 to 5.25)
    for side_y in (-1, 1):
        mesh = bpy.data.meshes.new(f"GableWallMesh_{side_y}")
        obj = bpy.data.objects.new(f"GableWall_{side_y}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = root

        bm = bmesh.new()
        v1 = bm.verts.new((-1.5, side_y * 1.25, 3.75))
        v2 = bm.verts.new(( 1.5, side_y * 1.25, 3.75))
        v3 = bm.verts.new(( 0.0, side_y * 1.25, 5.25))
        v4 = bm.verts.new((-1.5, side_y * 1.05, 3.75))
        v5 = bm.verts.new(( 1.5, side_y * 1.05, 3.75))
        v6 = bm.verts.new(( 0.0, side_y * 1.05, 5.25))

        bm.faces.new((v1, v2, v3))
        bm.faces.new((v6, v5, v4))
        bm.faces.new((v1, v3, v6, v4))
        bm.faces.new((v3, v2, v5, v6))
        bm.faces.new((v2, v1, v4, v5))
        bm.to_mesh(mesh)
        bm.free()
        obj.data.materials.append(mat_stucco)

    # -------------------------------------------------------------
    # 5. Half-Timbering Framing Beams (Exposed Wood)
    # -------------------------------------------------------------
    timber_specs = [
        # 4 Main Corner Vertical Posts (Z: 0.44 to 3.75)
        ("Beam_Post_FL", (0.16, 0.16, 3.32), (-1.5, -1.26, 2.10)),
        ("Beam_Post_FR", (0.16, 0.16, 3.32), ( 1.5, -1.26, 2.10)),
        ("Beam_Post_BL", (0.16, 0.16, 3.32), (-1.5,  1.26, 2.10)),
        ("Beam_Post_BR", (0.16, 0.16, 3.32), ( 1.5,  1.26, 2.10)),

        # Horizontal Belt Beams (Between 1st and 2nd Floor at Z: 2.10)
        ("Beam_Belt_F", (3.04, 0.14, 0.16), (0.0, -1.26, 2.10)),
        ("Beam_Belt_B", (3.04, 0.14, 0.16), (0.0,  1.26, 2.10)),
        ("Beam_Belt_R", (0.14, 2.54, 0.16), (1.5,   0.00, 2.10)),

        # Top Eave Horizontal Beams (At Z: 3.72)
        ("Beam_Eave_F", (3.04, 0.14, 0.16), (0.0, -1.26, 3.72)),
        ("Beam_Eave_B", (3.04, 0.14, 0.16), (0.0,  1.26, 3.72)),

        # Bottom Foundation Sill Beams (At Z: 0.46)
        ("Beam_Sill_F", (3.04, 0.14, 0.14), (0.0, -1.26, 0.46)),
        ("Beam_Sill_B", (3.04, 0.14, 0.14), (0.0,  1.26, 0.46)),

        # Front Central Vertical Studs (Framing Door at Center)
        ("Beam_Stud_DoorL", (0.12, 0.12, 1.60), (-0.46, -1.26, 1.28)),
        ("Beam_Stud_DoorR", (0.12, 0.12, 1.60), ( 0.46, -1.26, 1.28)),

        # Front Upper Floor Vertical Stud
        ("Beam_Stud_UpperM", (0.12, 0.12, 1.60), (0.00, -1.26, 2.92)),
    ]
    for name, sz, loc in timber_specs:
        b = create_beveled_box(name, sz, loc, mat_timber, bevel_width=0.015)
        b.parent = root

    # Diagonal Gable Barge Rafters (Front and Back)
    for sy in (-1.27, 1.27):
        suffix = "F" if sy < 0 else "B"
        r_left = create_beveled_box(f"Rafter_L_{suffix}", (0.15, 0.16, 2.25), (-0.75, sy, 4.50), mat_timber, bevel_width=0.015)
        r_left.rotation_euler = (0, math.radians(45), 0)
        r_left.parent = root

        r_right = create_beveled_box(f"Rafter_R_{suffix}", (0.15, 0.16, 2.25), (0.75, sy, 4.50), mat_timber, bevel_width=0.015)
        r_right.rotation_euler = (0, math.radians(-45), 0)
        r_right.parent = root

        tie = create_beveled_box(f"CollarTie_{suffix}", (1.5, 0.14, 0.12), (0.0, sy, 4.50), mat_timber, bevel_width=0.015)
        tie.parent = root

    # -------------------------------------------------------------
    # 6. Stylized Curved Terracotta Roof (Main Cottage)
    # -------------------------------------------------------------
    roof_mesh = bpy.data.meshes.new("TerracottaRoofMesh")
    roof_obj = bpy.data.objects.new("Roof_Terracotta_Main", roof_mesh)
    bpy.context.collection.objects.link(roof_obj)
    roof_obj.parent = root

    bm = bmesh.new()
    steps_x = 14
    steps_y = 12
    y_min, y_max = -1.56, 1.56
    eave_span = 1.95
    ridge_z = 5.35
    eave_z = 3.65

    grid_left = []
    grid_right = []
    for iy in range(steps_y + 1):
        ty = iy / steps_y
        py = y_min + ty * (y_max - y_min)
        y_sag = math.sin(ty * math.pi) * 0.06

        row_l = []
        row_r = []
        for ix in range(steps_x + 1):
            tx = ix / steps_x
            flare = (1.0 - tx) ** 1.35
            pz = eave_z + (ridge_z - eave_z) * flare - y_sag

            px_l = -tx * eave_span
            row_l.append(bm.verts.new((px_l, py, pz)))

            px_r = tx * eave_span
            row_r.append(bm.verts.new((px_r, py, pz)))
        grid_left.append(row_l)
        grid_right.append(row_r)

    for iy in range(steps_y):
        for ix in range(steps_x):
            v0 = grid_left[iy][ix]
            v1 = grid_left[iy + 1][ix]
            v2 = grid_left[iy + 1][ix + 1]
            v3 = grid_left[iy][ix + 1]
            bm.faces.new((v0, v3, v2, v1))

    for iy in range(steps_y):
        for ix in range(steps_x):
            v0 = grid_right[iy][ix]
            v1 = grid_right[iy + 1][ix]
            v2 = grid_right[iy + 1][ix + 1]
            v3 = grid_right[iy][ix + 1]
            bm.faces.new((v0, v1, v2, v3))

    bm.to_mesh(roof_mesh)
    bm.free()

    sol = roof_obj.modifiers.new("RoofThickness", type='SOLIDIFY')
    sol.thickness = 0.14
    sol.offset = -1.0
    roof_obj.data.materials.append(mat_roof_tile)

    # Roof Crest Ridge Beam
    ridge_cap = create_beveled_box("RoofRidgeCap", (0.18, 3.25, 0.16), (0.0, 0.0, 5.42), mat_roof_trim, bevel_width=0.03)
    ridge_cap.parent = root

    # Roof Shingle Rows on slopes
    for side_x in (-1, 1):
        for row_i in range(1, 5):
            t_row = row_i / 5.0
            x_row = side_x * (t_row * eave_span * 0.95)
            z_row = eave_z + (ridge_z - eave_z) * ((1.0 - t_row) ** 1.35) + 0.04
            shingle_row = create_beveled_box(f"RoofTileRow_{side_x}_{row_i}", (0.12, 3.14, 0.07), (x_row, 0.0, z_row), mat_roof_trim, bevel_width=0.015)
            shingle_row.rotation_euler = (0, math.radians(-side_x * 42), 0)
            shingle_row.parent = root

    # -------------------------------------------------------------
    # 7. Side Wing Annex (1-Story Extension on the Left)
    # -------------------------------------------------------------
    wing_body = create_beveled_box("WingBody", (1.78, 2.24, 1.45), (-2.40, 0.0, 1.15), mat_stucco, bevel_width=0.02)
    wing_body.parent = root

    w_post_f = create_beveled_box("WingPost_F", (0.15, 0.15, 1.46), (-3.28, -1.11, 1.15), mat_timber, bevel_width=0.015)
    w_post_b = create_beveled_box("WingPost_B", (0.15, 0.15, 1.46), (-3.28,  1.11, 1.15), mat_timber, bevel_width=0.015)
    w_post_f.parent = root
    w_post_b.parent = root

    w_sill_f = create_beveled_box("WingSill_F", (1.80, 0.12, 0.12), (-2.40, -1.11, 0.46), mat_timber, bevel_width=0.015)
    w_eave_f = create_beveled_box("WingEave_F", (1.80, 0.12, 0.14), (-2.40, -1.11, 1.84), mat_timber, bevel_width=0.015)
    w_sill_f.parent = root
    w_eave_f.parent = root

    # Sloped Lean-To / Shed Roof over Wing
    wing_roof_mesh = bpy.data.meshes.new("WingRoofMesh")
    wing_roof = bpy.data.objects.new("Roof_Terracotta_Wing", wing_roof_mesh)
    bpy.context.collection.objects.link(wing_roof)
    wing_roof.parent = root

    bm_w = bmesh.new()
    y_wf, y_wb = -1.28, 1.28
    x_high, x_low = -1.45, -3.52
    z_high, z_low = 2.45, 1.62
    v0 = bm_w.verts.new((x_high, y_wb, z_high))
    v1 = bm_w.verts.new((x_high, y_wf, z_high))
    v2 = bm_w.verts.new((x_low,  y_wf, z_low))
    v3 = bm_w.verts.new((x_low,  y_wb, z_low))
    bm_w.faces.new((v0, v1, v2, v3))
    bm_w.to_mesh(wing_roof_mesh)
    bm_w.free()

    w_sol = wing_roof.modifiers.new("WingRoofSolidify", type='SOLIDIFY')
    w_sol.thickness = 0.12
    w_sol.offset = -1.0
    wing_roof.data.materials.append(mat_roof_tile)

    # Shingle courses on wing roof
    for ri in (1, 2):
        t_w = ri / 3.0
        x_rw = x_high + t_w * (x_low - x_high)
        z_rw = z_high + t_w * (z_low - z_high) + 0.03
        w_tile = create_beveled_box(f"WingTile_{ri}", (0.10, 2.54, 0.06), (x_rw, 0.0, z_rw), mat_roof_trim, bevel_width=0.01)
        w_tile.rotation_euler = (0, math.radians(-22), 0)
        w_tile.parent = root

    # -------------------------------------------------------------
    # 8. Dual Stone Chimneys (Right Side of Cottage)
    # -------------------------------------------------------------
    chim_base = create_beveled_box("Chimney_Main_Base", (0.85, 1.15, 2.25), (1.68, 0.0, 1.125), mat_chimney_rock, bevel_width=0.04)
    chim_base.parent = root

    chim_shoulder = create_beveled_box("Chimney_Shoulder", (0.92, 1.22, 0.14), (1.68, 0.0, 2.28), mat_stone_dark, bevel_width=0.03)
    chim_shoulder.parent = root

    chim_upper = create_beveled_box("Chimney_Main_Stack", (0.72, 0.92, 3.35), (1.68, 0.0, 3.98), mat_chimney_rock, bevel_width=0.03)
    chim_upper.parent = root

    chim_cap = create_beveled_box("Chimney_Main_Cap", (0.86, 1.05, 0.16), (1.68, 0.0, 5.72), mat_stone_base, bevel_width=0.03)
    chim_cap.parent = root

    flue_pot = create_beveled_box("Chimney_Flue_Pot", (0.35, 0.35, 0.40), (1.68, 0.0, 5.92), mat_roof_trim, bevel_width=0.02)
    flue_pot.parent = root

    chim_sec_base = create_beveled_box("Chimney_Sec_Base", (0.65, 0.70, 2.80), (1.62, 0.85, 1.40), mat_chimney_rock, bevel_width=0.03)
    chim_sec_upper = create_beveled_box("Chimney_Sec_Upper", (0.55, 0.60, 2.30), (1.62, 0.85, 3.95), mat_chimney_rock, bevel_width=0.03)
    chim_sec_cap = create_beveled_box("Chimney_Sec_Cap", (0.68, 0.72, 0.14), (1.62, 0.85, 5.16), mat_stone_base, bevel_width=0.03)
    chim_sec_base.parent = root
    chim_sec_upper.parent = root
    chim_sec_cap.parent = root

    chim_stones = [
        (1.98, -0.25, 0.85, 0.22, 0.35, 0.22),
        (1.98,  0.28, 1.45, 0.20, 0.40, 0.24),
        (1.98, -0.15, 1.85, 0.22, 0.32, 0.20),
        (1.94,  0.18, 3.10, 0.18, 0.34, 0.22),
        (1.94, -0.12, 4.25, 0.18, 0.30, 0.20),
        (1.94,  0.22, 4.85, 0.18, 0.28, 0.22),
        (1.55, -0.52, 0.95, 0.32, 0.18, 0.25),
        (1.55, -0.48, 1.70, 0.28, 0.16, 0.22),
        (1.55, -0.42, 3.65, 0.25, 0.15, 0.20),
        (1.55, -0.42, 4.60, 0.24, 0.15, 0.22),
    ]
    for idx, (cx, cy, cz, cw, cd, ch) in enumerate(chim_stones):
        sb = create_beveled_box(f"ChimStone_{idx}", (cw, cd, ch), (cx, cy, cz), mat_stone_dark, bevel_width=0.02)
        sb.parent = root

    # -------------------------------------------------------------
    # 9. Entrance Door & True-Open Windows with Glass & Planters
    # -------------------------------------------------------------
    # Front Entrance Door (Centered at X: 0.0, Y: -1.26, Z: 1.15)
    door_architrave = create_beveled_box("FrontDoorArchitrave", (0.84, 0.08, 1.54), (0.0, -1.28, 1.20), mat_timber, bevel_width=0.02)
    door_panel = create_beveled_box("FrontDoorPanel", (0.70, 0.04, 1.40), (0.0, -1.29, 1.18), mat_wood_door, bevel_width=0.015)
    # Recessed door panels for tongue-and-groove plank effect
    for dx in (-0.18, 0.18):
        d_sub = create_beveled_box(f"DoorGroove_{dx}", (0.14, 0.02, 1.30), (dx, -1.30, 1.18), mat_timber, bevel_width=0.005)
        d_sub.parent = root
    door_architrave.parent = root
    door_panel.parent = root

    knob = create_beveled_box("DoorKnob", (0.06, 0.08, 0.06), (0.24, -1.33, 1.18), mat_brass_knob, bevel_width=0.01)
    knob.parent = root

    step = create_beveled_box("DoorStep", (1.05, 0.38, 0.16), (0.0, -1.45, 0.08), mat_stone_base, bevel_width=0.02)
    step.parent = root

    # Open Window Construction (Border rails + exposed blue glass + cross muntins)
    def create_open_window(name, center_pos, size=(0.58, 0.62), has_planter=True, flower_palette=0, is_wall_y=True):
        cx, cy, cz = center_pos
        w, h = size
        tf = 0.055 # frame rail thickness
        df = 0.08  # frame depth

        if is_wall_y:
            # 1. Glass Pane (Front-facing at Y: cy - 0.01)
            glass = create_beveled_box(f"{name}_Glass", (w - tf, 0.02, h - tf), (cx, cy - 0.01, cz), mat_window_glass, bevel_width=0.004)
            glass.parent = root

            # 2. Outer Timber Frame Rails
            # Left & Right frame jambs
            jamb_l = create_beveled_box(f"{name}_JambL", (tf, df, h), (cx - w/2 + tf/2, cy - 0.02, cz), mat_window_trim, bevel_width=0.01)
            jamb_r = create_beveled_box(f"{name}_JambR", (tf, df, h), (cx + w/2 - tf/2, cy - 0.02, cz), mat_window_trim, bevel_width=0.01)
            # Top rail & Bottom windowsill
            rail_t = create_beveled_box(f"{name}_RailT", (w, df, tf), (cx, cy - 0.02, cz + h/2 - tf/2), mat_window_trim, bevel_width=0.01)
            sill_b = create_beveled_box(f"{name}_SillB", (w + 0.08, df + 0.04, tf * 1.2), (cx, cy - 0.03, cz - h/2 - tf * 0.4), mat_window_trim, bevel_width=0.01)
            jamb_l.parent = root
            jamb_r.parent = root
            rail_t.parent = root
            sill_b.parent = root

            # 3. Cross Muntins (Vertical and Horizontal dividers)
            m_vert = create_beveled_box(f"{name}_MuntinV", (0.035, df * 0.7, h - tf), (cx, cy - 0.02, cz), mat_window_trim, bevel_width=0.004)
            m_horiz = create_beveled_box(f"{name}_MuntinH", (w - tf, df * 0.7, 0.035), (cx, cy - 0.02, cz), mat_window_trim, bevel_width=0.004)
            m_vert.parent = root
            m_horiz.parent = root

            # 4. Planter Box with blooming flowers
            if has_planter:
                box_z = cz - (h / 2.0) - 0.16
                pbox = create_beveled_box(f"{name}_PlanterBox", (w + 0.10, 0.20, 0.16), (cx, cy - 0.10, box_z), mat_timber, bevel_width=0.015)
                pbox.parent = root

                fol = create_beveled_box(f"{name}_Foliage", (w + 0.06, 0.16, 0.10), (cx, cy - 0.10, box_z + 0.09), mat_foliage, bevel_width=0.02)
                fol.parent = root

                num_buds = 5
                for bi in range(num_buds):
                    tb = (bi / (num_buds - 1)) - 0.5
                    bx = cx + tb * (w * 0.8)
                    bz = box_z + 0.15 + ((bi % 2) * 0.03)
                    by = cy - 0.11 + ((bi % 3) * 0.02)
                    f_mat = mat_flower_red if (bi + flower_palette) % 2 == 0 else mat_flower_gold
                    flower = create_beveled_box(f"{name}_Flower_{bi}", (0.08, 0.08, 0.08), (bx, by, bz), f_mat, bevel_width=0.015)
                    flower.parent = root
        else:
            # Side-facing window (X-aligned)
            glass = create_beveled_box(f"{name}_Glass", (0.02, w - tf, h - tf), (cx + 0.01, cy, cz), mat_window_glass, bevel_width=0.004)
            jamb_f = create_beveled_box(f"{name}_JambF", (df, tf, h), (cx + 0.02, cy - w/2 + tf/2, cz), mat_window_trim, bevel_width=0.01)
            jamb_b = create_beveled_box(f"{name}_JambB", (df, tf, h), (cx + 0.02, cy + w/2 - tf/2, cz), mat_window_trim, bevel_width=0.01)
            rail_t = create_beveled_box(f"{name}_RailT", (df, w, tf), (cx + 0.02, cy, cz + h/2 - tf/2), mat_window_trim, bevel_width=0.01)
            sill_b = create_beveled_box(f"{name}_SillB", (df + 0.04, w + 0.08, tf * 1.2), (cx + 0.03, cy, cz - h/2 - tf * 0.4), mat_window_trim, bevel_width=0.01)
            m_vert = create_beveled_box(f"{name}_MuntinV", (df * 0.7, 0.035, h - tf), (cx + 0.02, cy, cz), mat_window_trim, bevel_width=0.004)
            m_horiz = create_beveled_box(f"{name}_MuntinH", (df * 0.7, w - tf, 0.035), (cx + 0.02, cy, cz), mat_window_trim, bevel_width=0.004)
            glass.parent = root
            jamb_f.parent = root
            jamb_b.parent = root
            rail_t.parent = root
            sill_b.parent = root
            m_vert.parent = root
            m_horiz.parent = root

    # 1. Front 2nd Floor Windows (2 windows)
    create_open_window("Win_Front_UpperL", (-0.68, -1.26, 2.85), size=(0.58, 0.62), has_planter=True, flower_palette=0)
    create_open_window("Win_Front_UpperR", ( 0.68, -1.26, 2.85), size=(0.58, 0.62), has_planter=True, flower_palette=1)

    # 2. Front 1st Floor Windows (Left and Right of Door)
    create_open_window("Win_Front_LowerL", (-0.95, -1.26, 1.25), size=(0.52, 0.58), has_planter=True, flower_palette=1)
    create_open_window("Win_Front_LowerR", ( 0.95, -1.26, 1.25), size=(0.52, 0.58), has_planter=True, flower_palette=0)

    # 3. Attic Gable Window (Centred at top of Front Gable)
    create_open_window("Win_Front_Attic", (0.0, -1.26, 4.45), size=(0.44, 0.44), has_planter=False)

    # 4. Front Wing Window (Wide window on the single-story annex)
    create_open_window("Win_Front_Wing", (-2.40, -1.13, 1.15), size=(0.78, 0.58), has_planter=False)

    # 5. Side Window (1st floor on Right Wall, behind chimney)
    create_open_window("Win_Side_Right", (1.50, 0.48, 1.25), size=(0.52, 0.52), has_planter=False, is_wall_y=False)

    # -------------------------------------------------------------
    # 10. Ceramic Potted Plants & Garden Bush
    # -------------------------------------------------------------
    pot_coords = [
        (-0.54, -1.48, 0.08, 0.28, 0.32),
        ( 0.54, -1.48, 0.08, 0.28, 0.32),
        ( 1.48, -1.45, 0.08, 0.26, 0.30),
        (-3.35, -1.35, 0.08, 0.28, 0.30),
        ( 1.72,  0.55, 0.08, 0.25, 0.28),
    ]
    for pi, (px, py, pz, pr, ph) in enumerate(pot_coords):
        pot = create_beveled_box(f"PlantPot_{pi}", (pr, pr, ph), (px, py, pz + ph / 2.0), mat_pot_clay, bevel_width=0.03)
        pot.parent = root
        plant = create_beveled_box(f"PlantFoliage_{pi}", (pr * 1.25, pr * 1.25, pr * 1.1), (px, py, pz + ph + pr * 0.45), mat_foliage, bevel_width=0.06)
        plant.parent = root

    shrub1 = create_beveled_box("GardenShrub_Main", (0.75, 0.70, 0.65), (-3.20, -2.75, 0.35), mat_foliage, bevel_width=0.15)
    shrub2 = create_beveled_box("GardenShrub_Sub",  (0.55, 0.50, 0.48), (-2.85, -2.95, 0.26), mat_foliage, bevel_width=0.12)
    shrub1.parent = root
    shrub2.parent = root

    # -------------------------------------------------------------
    # 11. Wooden Picket Fence Surrounding the Yard
    # -------------------------------------------------------------
    fence_h = 0.82
    picket_w = 0.09
    picket_t = 0.035
    rail_h = 0.05

    def build_fence_segment(seg_name, start_pt, end_pt, spacing=0.22):
        p1 = Vector(start_pt)
        p2 = Vector(end_pt)
        vec = p2 - p1
        dist = vec.length
        if dist < 0.05:
            return
        direction = vec.normalized()
        yaw = math.atan2(direction.x, direction.y)

        mid_pt = (p1 + p2) * 0.5
        for rz in (0.22, 0.62):
            rail = create_beveled_box(f"{seg_name}_Rail_{rz}", (picket_t, dist, rail_h), (mid_pt.x, mid_pt.y, rz), mat_fence, bevel_width=0.01)
            rail.rotation_euler = (0, 0, -yaw)
            rail.parent = root

        count = max(2, int(dist / spacing) + 1)
        step_vec = vec / (count - 1)
        for vi in range(count):
            pt = p1 + step_vec * vi
            picket = create_beveled_box(f"{seg_name}_Picket_{vi}", (picket_t * 1.2, picket_w, fence_h), (pt.x, pt.y, fence_h / 2.0), mat_fence, bevel_width=0.01)
            picket.rotation_euler = (0, 0, -yaw)
            picket.parent = root

            tip = create_beveled_box(f"{seg_name}_Tip_{vi}", (picket_t * 1.1, picket_w * 0.9, 0.08), (pt.x, pt.y, fence_h + 0.03), mat_fence, bevel_width=0.02)
            tip.rotation_euler = (0, 0, -yaw)
            tip.parent = root

    build_fence_segment("Fence_Front_Left", (-3.9, -3.4, 0), (-0.7, -3.4, 0))
    build_fence_segment("Fence_Front_Right", (0.7, -3.4, 0), (3.9, -3.4, 0))
    build_fence_segment("Fence_Left_Side", (-3.9, -3.4, 0), (-3.9, 3.2, 0))
    build_fence_segment("Fence_Right_Side", (3.9, -3.4, 0), (3.9, 3.2, 0))
    build_fence_segment("Fence_Back", (-3.9, 3.2, 0), (3.9, 3.2, 0))

    for g_name, gx in [("GatePost_L", -0.7), ("GatePost_R", 0.7)]:
        g_post = create_beveled_box(g_name, (0.14, 0.14, 0.96), (gx, -3.4, 0.48), mat_timber, bevel_width=0.015)
        g_post.parent = root
        g_cap = create_beveled_box(f"{g_name}_Cap", (0.18, 0.18, 0.06), (gx, -3.4, 0.98), mat_timber, bevel_width=0.015)
        g_cap.parent = root

    for cp_name, (cx, cy) in [
        ("CornerPost_FL", (-3.9, -3.4)),
        ("CornerPost_FR", ( 3.9, -3.4)),
        ("CornerPost_BL", (-3.9,  3.2)),
        ("CornerPost_BR", ( 3.9,  3.2)),
    ]:
        c_post = create_beveled_box(cp_name, (0.13, 0.13, 0.94), (cx, cy, 0.47), mat_timber, bevel_width=0.015)
        c_post.parent = root

    print("Fantasy Cottage model built with true open windows and glass.")
    return root

def export_model(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported glTF: {filepath}")

def save_blend_file(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"Saved Blend file: {filepath}")

if __name__ == "__main__":
    build_fantasy_cottage()

    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models"))
    blend_path = os.path.join(models_dir, "house_village.blend")
    glb_path = os.path.join(models_dir, "house_village.glb")

    save_blend_file(blend_path)
    export_model(glb_path)
