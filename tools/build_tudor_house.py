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

def build_fantasy_balcony_cottage():
    clear_scene()

    root = bpy.data.objects.new("House_Tudor_Root", None)
    bpy.context.collection.objects.link(root)

    # -------------------------------------------------------------
    # 1. PBR Color Palette (Sampled from Corrected Blueprint)
    # -------------------------------------------------------------
    mat_stucco       = create_pbr_material("Mat_PlasterOchre",    (0.96, 0.88, 0.74), roughness=0.72)
    mat_timber       = create_pbr_material("Mat_DarkTimber",      (0.35, 0.18, 0.09), roughness=0.55)
    mat_stone_base   = create_pbr_material("Mat_FoundationStone", (0.50, 0.48, 0.47), roughness=0.75)
    mat_stone_dark   = create_pbr_material("Mat_StoneMasonry",    (0.40, 0.38, 0.37), roughness=0.78)
    mat_chimney_rock = create_pbr_material("Mat_ChimneyRock",     (0.55, 0.52, 0.50), roughness=0.70)
    mat_roof_tile    = create_pbr_material("Mat_TerracottaRoof",  (0.82, 0.29, 0.17), roughness=0.48)
    mat_roof_trim    = create_pbr_material("Mat_RoofTrimWood",    (0.44, 0.22, 0.11), roughness=0.55)
    mat_wood_door    = create_pbr_material("Mat_WoodDoor",        (0.42, 0.22, 0.11), roughness=0.50)
    mat_window_glass = create_pbr_material("Mat_WindowGlass",     (0.18, 0.46, 0.70), roughness=0.08, metallic=0.15)
    mat_window_trim  = create_pbr_material("Mat_WindowTrim",      (0.32, 0.16, 0.08), roughness=0.55)
    mat_brass_knob   = create_pbr_material("Mat_BrassKnob",       (0.94, 0.76, 0.18), roughness=0.20, metallic=0.90)
    mat_grass        = create_pbr_material("Mat_LawnGrass",       (0.42, 0.64, 0.22), roughness=0.80)
    mat_path         = create_pbr_material("Mat_StonePath",       (0.68, 0.62, 0.54), roughness=0.75)
    mat_fence        = create_pbr_material("Mat_PicketFence",     (0.56, 0.36, 0.20), roughness=0.65)
    mat_foliage      = create_pbr_material("Mat_FoliageGreen",    (0.24, 0.56, 0.18), roughness=0.60)
    mat_flower_red   = create_pbr_material("Mat_FlowerRed",       (0.94, 0.18, 0.24), roughness=0.45)
    mat_flower_gold  = create_pbr_material("Mat_FlowerGold",      (0.98, 0.84, 0.12), roughness=0.45)
    mat_pot_clay     = create_pbr_material("Mat_ClayPot",         (0.76, 0.35, 0.17), roughness=0.60)

    # -------------------------------------------------------------
    # 2. Yard Base Ground Plate & Curved Stepping Stones Path
    # -------------------------------------------------------------
    yard = create_beveled_box("YardLawn", (8.4, 7.4, 0.2), (0.0, -0.1, -0.1), mat_grass, bevel_width=0.04)
    yard.parent = root

    # Stepping stones path curving from front gate around to front door
    stepping_stones = [
        ( 1.10, -3.20, 0.03, 0.52, 0.42),
        ( 0.95, -2.75, 0.03, 0.48, 0.44),
        ( 0.70, -2.35, 0.03, 0.50, 0.45),
        ( 0.40, -2.00, 0.03, 0.54, 0.46),
        ( 0.15, -1.65, 0.03, 0.56, 0.48),
        ( 0.00, -1.45, 0.03, 0.60, 0.48),
    ]
    for idx, (sx, sy, sz, sw, sd) in enumerate(stepping_stones):
        stone = create_beveled_box(f"StepStone_{idx}", (sw, sd, 0.04), (sx, sy, sz), mat_path, bevel_width=0.03)
        stone.parent = root

    # -------------------------------------------------------------
    # 3. Foundation Base (L-Shaped with Stone Masonry Quoins)
    # -------------------------------------------------------------
    # Main Foundation Block (Z: 0.0 to 0.44, X: -1.2 to 1.6, Y: -1.4 to 1.4)
    base_main = create_beveled_box("FoundationMain", (2.85, 2.85, 0.44), (0.15, 0.0, 0.22), mat_stone_base, bevel_width=0.04)
    base_main.parent = root

    # Left Wing Foundation Block (X: -2.35, Y: -0.1)
    base_wing = create_beveled_box("FoundationWing", (1.75, 2.35, 0.40), (-2.05, -0.1, 0.20), mat_stone_base, bevel_width=0.04)
    base_wing.parent = root

    # Chiseled masonry stones around base
    base_details = [
        (-1.25, -1.44, 0.22, 0.38, 0.14, 0.26),
        (-0.55, -1.44, 0.16, 0.42, 0.14, 0.22),
        ( 0.55, -1.44, 0.24, 0.38, 0.14, 0.24),
        ( 1.45, -1.44, 0.18, 0.36, 0.14, 0.25),
        (-2.85, -1.28, 0.20, 0.34, 0.14, 0.24),
        (-2.05, -1.28, 0.16, 0.44, 0.14, 0.20),
        (-1.25,  1.44, 0.20, 0.40, 0.14, 0.24),
        ( 0.15,  1.44, 0.18, 0.48, 0.14, 0.22),
        ( 1.45,  1.44, 0.22, 0.38, 0.14, 0.25),
        (-2.85,  1.08, 0.18, 0.35, 0.14, 0.22),
    ]
    for i, (bx, by, bz, bw, bd, bh) in enumerate(base_details):
        sblock = create_beveled_box(f"BaseStoneDetail_{i}", (bw, bd, bh), (bx, by, bz), mat_stone_dark, bevel_width=0.02)
        sblock.parent = root

    # -------------------------------------------------------------
    # 4. Main House Stucco Body & Gable Geometry
    # -------------------------------------------------------------
    # Main 2-story stucco core (Z: 0.44 to 3.75, Width: 2.60, Depth: 2.50, Center X: 0.15)
    main_body = create_beveled_box("HouseMainBody", (2.60, 2.50, 3.31), (0.15, 0.0, 2.095), mat_stucco, bevel_width=0.02)
    main_body.parent = root

    # Triangular Gables (Front and Back, Z: 3.75 to 5.30)
    for side_y in (-1, 1):
        mesh = bpy.data.meshes.new(f"GableWallMesh_{side_y}")
        obj = bpy.data.objects.new(f"GableWall_{side_y}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = root

        bm = bmesh.new()
        v1 = bm.verts.new((-1.15, side_y * 1.25, 3.75))
        v2 = bm.verts.new(( 1.45, side_y * 1.25, 3.75))
        v3 = bm.verts.new(( 0.15, side_y * 1.25, 5.30))
        v4 = bm.verts.new((-1.15, side_y * 1.05, 3.75))
        v5 = bm.verts.new(( 1.45, side_y * 1.05, 3.75))
        v6 = bm.verts.new(( 0.15, side_y * 1.05, 5.30))

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
        # Main Corner Vertical Posts
        ("Beam_Post_FL", (0.16, 0.16, 3.32), (-1.15, -1.26, 2.10)),
        ("Beam_Post_FR", (0.16, 0.16, 3.32), ( 1.45, -1.26, 2.10)),
        ("Beam_Post_BL", (0.16, 0.16, 3.32), (-1.15,  1.26, 2.10)),
        ("Beam_Post_BR", (0.16, 0.16, 3.32), ( 1.45,  1.26, 2.10)),

        # Horizontal Belt Beams (Between 1st and 2nd Floor at Z: 2.10)
        ("Beam_Belt_F", (2.64, 0.14, 0.16), (0.15, -1.26, 2.10)),
        ("Beam_Belt_B", (2.64, 0.14, 0.16), (0.15,  1.26, 2.10)),
        ("Beam_Belt_R", (0.14, 2.54, 0.16), (1.45,  0.00, 2.10)),

        # Top Eave Horizontal Beams (At Z: 3.72)
        ("Beam_Eave_F", (2.64, 0.14, 0.16), (0.15, -1.26, 3.72)),
        ("Beam_Eave_B", (2.64, 0.14, 0.16), (0.15,  1.26, 3.72)),

        # Bottom Foundation Sill Beams (At Z: 0.46)
        ("Beam_Sill_F", (2.64, 0.14, 0.14), (0.15, -1.26, 0.46)),
        ("Beam_Sill_B", (2.64, 0.14, 0.14), (0.15,  1.26, 0.46)),

        # Front Central Vertical Studs flanking the Arched Entrance
        ("Beam_Stud_DoorL", (0.12, 0.12, 1.60), (-0.48, -1.26, 1.28)),
        ("Beam_Stud_DoorR", (0.12, 0.12, 1.60), ( 0.48, -1.26, 1.28)),
    ]
    for name, sz, loc in timber_specs:
        b = create_beveled_box(name, sz, loc, mat_timber, bevel_width=0.015)
        b.parent = root

    # Diagonal Gable Barge Rafters (Front and Back)
    for sy in (-1.27, 1.27):
        suffix = "F" if sy < 0 else "B"
        r_left = create_beveled_box(f"Rafter_L_{suffix}", (0.15, 0.16, 2.15), (-0.50, sy, 4.52), mat_timber, bevel_width=0.015)
        r_left.rotation_euler = (0, math.radians(45), 0)
        r_left.parent = root

        r_right = create_beveled_box(f"Rafter_R_{suffix}", (0.15, 0.16, 2.15), (0.80, sy, 4.52), mat_timber, bevel_width=0.015)
        r_right.rotation_euler = (0, math.radians(-45), 0)
        r_right.parent = root

        tie = create_beveled_box(f"CollarTie_{suffix}", (1.45, 0.14, 0.12), (0.15, sy, 4.55), mat_timber, bevel_width=0.015)
        tie.parent = root

    # -------------------------------------------------------------
    # 6. Curved Terracotta Gable Roof with Shingle Courses
    # -------------------------------------------------------------
    roof_mesh = bpy.data.meshes.new("TudorTerracottaRoofMesh")
    roof_obj = bpy.data.objects.new("Roof_Terracotta_Main", roof_mesh)
    bpy.context.collection.objects.link(roof_obj)
    roof_obj.parent = root

    bm = bmesh.new()
    steps_x = 14
    steps_y = 12
    y_min, y_max = -1.56, 1.56
    eave_span = 1.75
    ridge_z = 5.40
    eave_z = 3.65
    center_x = 0.15

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

            px_l = center_x - tx * eave_span
            row_l.append(bm.verts.new((px_l, py, pz)))

            px_r = center_x + tx * eave_span
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

    # Roof Ridge Cap Beam
    ridge_cap = create_beveled_box("RoofRidgeCap", (0.18, 3.25, 0.16), (center_x, 0.0, 5.46), mat_roof_trim, bevel_width=0.03)
    ridge_cap.parent = root

    # Overlapping shingle row steps
    for side_x in (-1, 1):
        for row_i in range(1, 5):
            t_row = row_i / 5.0
            x_row = center_x + side_x * (t_row * eave_span * 0.95)
            z_row = eave_z + (ridge_z - eave_z) * ((1.0 - t_row) ** 1.35) + 0.04
            shingle_row = create_beveled_box(f"RoofTileRow_{side_x}_{row_i}", (0.12, 3.14, 0.07), (x_row, 0.0, z_row), mat_roof_trim, bevel_width=0.015)
            shingle_row.rotation_euler = (0, math.radians(-side_x * 42), 0)
            shingle_row.parent = root

    # -------------------------------------------------------------
    # 7. Side Wing Annex (1-Story Extension on the Left)
    # -------------------------------------------------------------
    wing_body = create_beveled_box("WingBody", (1.65, 2.15, 1.45), (-1.95, -0.10, 1.15), mat_stucco, bevel_width=0.02)
    wing_body.parent = root

    w_post_f = create_beveled_box("WingPost_F", (0.15, 0.15, 1.46), (-2.78, -1.18, 1.15), mat_timber, bevel_width=0.015)
    w_post_b = create_beveled_box("WingPost_B", (0.15, 0.15, 1.46), (-2.78,  0.98, 1.15), mat_timber, bevel_width=0.015)
    w_post_f.parent = root
    w_post_b.parent = root

    w_sill_f = create_beveled_box("WingSill_F", (1.68, 0.12, 0.12), (-1.95, -1.18, 0.46), mat_timber, bevel_width=0.015)
    w_eave_f = create_beveled_box("WingEave_F", (1.68, 0.12, 0.14), (-1.95, -1.18, 1.84), mat_timber, bevel_width=0.015)
    w_sill_f.parent = root
    w_eave_f.parent = root

    # Sloped Lean-to Roof over Wing
    wing_roof_mesh = bpy.data.meshes.new("TudorWingRoofMesh")
    wing_roof = bpy.data.objects.new("Roof_Terracotta_Wing", wing_roof_mesh)
    bpy.context.collection.objects.link(wing_roof)
    wing_roof.parent = root

    bm_w = bmesh.new()
    y_wf, y_wb = -1.34, 1.14
    x_high, x_low = -1.10, -3.02
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
        w_tile = create_beveled_box(f"WingTile_{ri}", (0.10, 2.50, 0.06), (x_rw, -0.10, z_rw), mat_roof_trim, bevel_width=0.01)
        w_tile.rotation_euler = (0, math.radians(-22), 0)
        w_tile.parent = root

    # -------------------------------------------------------------
    # 8. Front Wooden Balcony (Over Entrance Door on 2nd Floor)
    # -------------------------------------------------------------
    # Cantilevered support corbels / timber beams under balcony
    for cx in (-0.55, -0.18, 0.18, 0.55):
        corbel = create_beveled_box(f"BalconyCorbel_{cx}", (0.10, 0.85, 0.14), (cx, -1.60, 2.05), mat_timber, bevel_width=0.015)
        corbel.parent = root
        # Diagonal knee brace strut
        strut = create_beveled_box(f"BalconyStrut_{cx}", (0.08, 0.45, 0.08), (cx, -1.48, 1.80), mat_timber, bevel_width=0.01)
        strut.rotation_euler = (math.radians(-40), 0, 0)
        strut.parent = root

    # Balcony Floor Deck (Width: 1.55, Depth: 0.85, Z: 2.14)
    b_deck = create_beveled_box("BalconyFloorDeck", (1.55, 0.85, 0.08), (0.0, -1.65, 2.14), mat_timber, bevel_width=0.015)
    b_deck.parent = root

    # Balcony Balustrade Perimeter Railings (Front, Left, Right)
    rail_h = 0.65
    rail_t = 0.04
    # Top & Bottom Rails Front (Y: -2.04)
    for rz in (2.22, 2.14 + rail_h):
        r_f = create_beveled_box(f"BalconyRail_F_{rz}", (1.55, rail_t, 0.05), (0.0, -2.04, rz), mat_timber, bevel_width=0.008)
        r_f.parent = root
    # Top & Bottom Rails Left and Right
    for side_x in (-0.75, 0.75):
        for rz in (2.22, 2.14 + rail_h):
            r_s = create_beveled_box(f"BalconyRail_S_{side_x}_{rz}", (rail_t, 0.80, 0.05), (side_x, -1.64, rz), mat_timber, bevel_width=0.008)
            r_s.parent = root

    # Vertical Balusters along Front Balcony
    num_balusters = 8
    for bi in range(num_balusters):
        tb = (bi / (num_balusters - 1)) - 0.5
        bx = tb * 1.35
        bal = create_beveled_box(f"BalconyBaluster_F_{bi}", (0.05, 0.04, rail_h), (bx, -2.04, 2.14 + rail_h / 2.0), mat_timber, bevel_width=0.008)
        bal.parent = root

    # Side Balusters (3 each side)
    for side_x in (-0.75, 0.75):
        for sbi in range(3):
            sy_b = -1.40 - sbi * 0.25
            bal_s = create_beveled_box(f"BalconyBaluster_S_{side_x}_{sbi}", (0.04, 0.05, rail_h), (side_x, sy_b, 2.14 + rail_h / 2.0), mat_timber, bevel_width=0.008)
            bal_s.parent = root

    # Corner Posts on Balcony
    for cpx, cpy in [(-0.75, -2.04), (0.75, -2.04)]:
        cpost = create_beveled_box(f"BalconyCornerPost_{cpx}", (0.08, 0.08, rail_h + 0.08), (cpx, cpy, 2.14 + (rail_h + 0.08) / 2.0), mat_timber, bevel_width=0.01)
        cpost.parent = root

    # -------------------------------------------------------------
    # 9. Spiral Wooden Staircase (Wrapping Right Wall to 2nd Floor)
    # -------------------------------------------------------------
    # Staircase center hub (X: 1.85, Y: 0.25)
    stair_hub = create_beveled_box("StaircaseHub", (0.16, 0.16, 2.65), (1.85, 0.25, 1.325), mat_timber, bevel_width=0.02)
    stair_hub.parent = root

    # 2nd Floor Landing Platform (X: 1.75 to 2.35, Y: -0.45 to 0.45, Z: 2.14)
    stair_platform = create_beveled_box("StairPlatform", (0.75, 0.95, 0.08), (1.95, -0.05, 2.14), mat_timber, bevel_width=0.015)
    stair_platform.parent = root
    # Platform safety railing
    plat_rail = create_beveled_box("StairPlatRail", (0.04, 0.95, 0.65), (2.30, -0.05, 2.48), mat_timber, bevel_width=0.01)
    plat_rail.parent = root

    # Spiral Stair Treads (10 steps spiraling up from ground to platform)
    num_steps = 10
    total_angle = math.radians(160)
    start_angle = math.radians(-80)
    for si in range(num_steps):
        t_step = si / (num_steps - 1)
        ang = start_angle + t_step * total_angle
        sz = 0.20 + t_step * 1.94

        radius = 0.65
        step_x = 1.85 + math.cos(ang) * radius
        step_y = 0.25 + math.sin(ang) * radius

        step_tread = create_beveled_box(f"StairTread_{si}", (0.55, 0.26, 0.06), (step_x, step_y, sz), mat_timber, bevel_width=0.01)
        step_tread.rotation_euler = (0, 0, -ang)
        step_tread.parent = root

        # Outer Baluster & Curved Handrail Post
        rail_post_x = 1.85 + math.cos(ang) * (radius + 0.22)
        rail_post_y = 0.25 + math.sin(ang) * (radius + 0.22)
        post = create_beveled_box(f"StairHandrailPost_{si}", (0.04, 0.04, 0.65), (rail_post_x, rail_post_y, sz + 0.32), mat_timber, bevel_width=0.008)
        post.rotation_euler = (0, 0, -ang)
        post.parent = root

    # -------------------------------------------------------------
    # 10. Stone Chimney Stack (Right Side Masonry)
    # -------------------------------------------------------------
    chim_base = create_beveled_box("Chimney_Base", (0.78, 1.05, 2.25), (1.52, 0.85, 1.125), mat_chimney_rock, bevel_width=0.04)
    chim_base.parent = root

    chim_shoulder = create_beveled_box("Chimney_Shoulder", (0.84, 1.12, 0.14), (1.52, 0.85, 2.28), mat_stone_dark, bevel_width=0.03)
    chim_shoulder.parent = root

    chim_upper = create_beveled_box("Chimney_Stack", (0.65, 0.85, 3.45), (1.52, 0.85, 4.02), mat_chimney_rock, bevel_width=0.03)
    chim_upper.parent = root

    chim_cap = create_beveled_box("Chimney_Cap", (0.78, 0.98, 0.16), (1.52, 0.85, 5.76), mat_stone_base, bevel_width=0.03)
    chim_cap.parent = root

    flue_pot = create_beveled_box("Chimney_Flue", (0.34, 0.34, 0.38), (1.52, 0.85, 5.96), mat_roof_trim, bevel_width=0.02)
    flue_pot.parent = root

    # Masonry stone block details on chimney
    chim_stones = [
        (1.88,  0.65, 0.85, 0.22, 0.35, 0.22),
        (1.88,  1.10, 1.45, 0.20, 0.38, 0.24),
        (1.88,  0.75, 1.85, 0.22, 0.30, 0.20),
        (1.84,  0.95, 3.10, 0.18, 0.32, 0.22),
        (1.84,  0.72, 4.25, 0.18, 0.30, 0.20),
        (1.84,  1.02, 4.85, 0.18, 0.28, 0.22),
        (1.42,  1.38, 0.95, 0.30, 0.18, 0.24),
        (1.42,  1.35, 1.70, 0.28, 0.16, 0.22),
        (1.42,  1.30, 3.65, 0.25, 0.15, 0.20),
    ]
    for idx, (cx, cy, cz, cw, cd, ch) in enumerate(chim_stones):
        sb = create_beveled_box(f"TudorChimStone_{idx}", (cw, cd, ch), (cx, cy, cz), mat_stone_dark, bevel_width=0.02)
        sb.parent = root

    # -------------------------------------------------------------
    # 11. Arched Door & Windows with Blooming Flower Planters
    # -------------------------------------------------------------
    # Round-top Arched Door (Centered at X: 0.0, Y: -1.26, Z: 1.05)
    # Outer Door Timber Architrave
    door_arch = create_beveled_box("FrontDoorArch", (0.86, 0.10, 1.45), (0.0, -1.27, 1.15), mat_timber, bevel_width=0.02)
    door_panel = create_beveled_box("FrontDoorPanel", (0.72, 0.05, 1.35), (0.0, -1.29, 1.12), mat_wood_door, bevel_width=0.02)
    door_arch.parent = root
    door_panel.parent = root

    # Arched door decorative planks
    for px in (-0.18, 0.0, 0.18):
        plank = create_beveled_box(f"DoorPlank_{px}", (0.12, 0.02, 1.25), (px, -1.30, 1.12), mat_timber, bevel_width=0.005)
        plank.parent = root

    # Bronze Round Door Handle / Knocker
    knob = create_beveled_box("DoorKnob", (0.06, 0.08, 0.06), (0.24, -1.33, 1.12), mat_brass_knob, bevel_width=0.01)
    knob.parent = root

    step = create_beveled_box("DoorStep", (1.05, 0.38, 0.16), (0.0, -1.45, 0.08), mat_stone_base, bevel_width=0.02)
    step.parent = root

    # Window builder helper
    def create_open_window(name, center_pos, size=(0.52, 0.58), has_planter=True, flower_palette=0, is_wall_y=True):
        cx, cy, cz = center_pos
        w, h = size
        tf = 0.05
        df = 0.08

        if is_wall_y:
            glass = create_beveled_box(f"{name}_Glass", (w - tf, 0.02, h - tf), (cx, cy - 0.01, cz), mat_window_glass, bevel_width=0.004)
            jamb_l = create_beveled_box(f"{name}_JambL", (tf, df, h), (cx - w/2 + tf/2, cy - 0.02, cz), mat_window_trim, bevel_width=0.01)
            jamb_r = create_beveled_box(f"{name}_JambR", (tf, df, h), (cx + w/2 - tf/2, cy - 0.02, cz), mat_window_trim, bevel_width=0.01)
            rail_t = create_beveled_box(f"{name}_RailT", (w, df, tf), (cx, cy - 0.02, cz + h/2 - tf/2), mat_window_trim, bevel_width=0.01)
            sill_b = create_beveled_box(f"{name}_SillB", (w + 0.08, df + 0.04, tf * 1.2), (cx, cy - 0.03, cz - h/2 - tf * 0.4), mat_window_trim, bevel_width=0.01)
            m_vert = create_beveled_box(f"{name}_MuntinV", (0.035, df * 0.7, h - tf), (cx, cy - 0.02, cz), mat_window_trim, bevel_width=0.004)
            m_horiz = create_beveled_box(f"{name}_MuntinH", (w - tf, df * 0.7, 0.035), (cx, cy - 0.02, cz), mat_window_trim, bevel_width=0.004)
            glass.parent = root
            jamb_l.parent = root
            jamb_r.parent = root
            rail_t.parent = root
            sill_b.parent = root
            m_vert.parent = root
            m_horiz.parent = root

            if has_planter:
                box_z = cz - (h / 2.0) - 0.15
                pbox = create_beveled_box(f"{name}_PlanterBox", (w + 0.10, 0.20, 0.15), (cx, cy - 0.10, box_z), mat_timber, bevel_width=0.015)
                fol = create_beveled_box(f"{name}_Foliage", (w + 0.06, 0.16, 0.10), (cx, cy - 0.10, box_z + 0.08), mat_foliage, bevel_width=0.02)
                pbox.parent = root
                fol.parent = root

                num_buds = 5
                for bi in range(num_buds):
                    tb = (bi / (num_buds - 1)) - 0.5
                    bx = cx + tb * (w * 0.8)
                    bz = box_z + 0.14 + ((bi % 2) * 0.03)
                    by = cy - 0.11 + ((bi % 3) * 0.02)
                    f_mat = mat_flower_red if (bi + flower_palette) % 2 == 0 else mat_flower_gold
                    flower = create_beveled_box(f"{name}_Flower_{bi}", (0.08, 0.08, 0.08), (bx, by, bz), f_mat, bevel_width=0.015)
                    flower.parent = root
        else:
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

    # 1. Front Ground Floor Windows (Left and Right of Door)
    create_open_window("Win_Front_G_L", (-0.80, -1.26, 1.25), size=(0.48, 0.54), has_planter=True, flower_palette=1)
    create_open_window("Win_Front_G_R", ( 0.80, -1.26, 1.25), size=(0.48, 0.54), has_planter=True, flower_palette=0)

    # 2. Front 2nd Floor Balcony 3-Pane Window (Opening to Balcony)
    create_open_window("Win_Front_Balcony", (0.00, -1.26, 2.90), size=(0.95, 0.72), has_planter=True, flower_palette=0)

    # 3. Attic Gable Window (Top Gable Triangle)
    create_open_window("Win_Front_Attic", (0.15, -1.26, 4.45), size=(0.44, 0.44), has_planter=True, flower_palette=1)

    # 4. Front Wing Window (Single-story annex)
    create_open_window("Win_Front_Wing", (-1.95, -1.20, 1.15), size=(0.58, 0.58), has_planter=False)

    # 5. Side Windows on Right Wall
    create_open_window("Win_Side_G1", (1.45, -0.65, 1.25), size=(0.48, 0.48), has_planter=False, is_wall_y=False)

    # -------------------------------------------------------------
    # 12. Ceramic Pots, Shrubs & Wooden Picket Fence
    # -------------------------------------------------------------
    pot_coords = [
        (-0.52, -1.48, 0.08, 0.28, 0.32),
        ( 0.52, -1.48, 0.08, 0.28, 0.32),
        (-2.95, -1.40, 0.08, 0.28, 0.30),
        ( 1.75, -1.42, 0.08, 0.26, 0.30),
    ]
    for pi, (px, py, pz, pr, ph) in enumerate(pot_coords):
        pot = create_beveled_box(f"TudorPlantPot_{pi}", (pr, pr, ph), (px, py, pz + ph / 2.0), mat_pot_clay, bevel_width=0.03)
        pot.parent = root
        plant = create_beveled_box(f"TudorPlantFoliage_{pi}", (pr * 1.25, pr * 1.25, pr * 1.1), (px, py, pz + ph + pr * 0.45), mat_foliage, bevel_width=0.06)
        plant.parent = root

    # Corner Garden Shrubs
    shrub1 = create_beveled_box("TudorShrub_1", (0.75, 0.70, 0.65), (-3.20, -2.75, 0.35), mat_foliage, bevel_width=0.15)
    shrub2 = create_beveled_box("TudorShrub_2", (0.65, 0.60, 0.55), ( 2.80, -2.55, 0.30), mat_foliage, bevel_width=0.14)
    shrub1.parent = root
    shrub2.parent = root

    # Perimeter Picket Fence
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

    # Fence Perimeter Lines (Front opening aligned with stepping stones at X: 0.8 to 1.4)
    build_fence_segment("Fence_Front_Left", (-3.9, -3.4, 0), (0.7, -3.4, 0))
    build_fence_segment("Fence_Front_Right", (1.6, -3.4, 0), (3.9, -3.4, 0))
    build_fence_segment("Fence_Left_Side", (-3.9, -3.4, 0), (-3.9, 3.2, 0))
    build_fence_segment("Fence_Right_Side", (3.9, -3.4, 0), (3.9, 3.2, 0))
    build_fence_segment("Fence_Back", (-3.9, 3.2, 0), (3.9, 3.2, 0))

    # Gate Posts
    for g_name, gx in [("GatePost_L", 0.7), ("GatePost_R", 1.6)]:
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

    print("Fantasy Balcony Cottage (Tudor replacement) built successfully.")
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
    build_fantasy_balcony_cottage()

    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models"))
    blend_path = os.path.join(models_dir, "house_tudor.blend")
    glb_path = os.path.join(models_dir, "house_tudor.glb")

    save_blend_file(blend_path)
    export_model(glb_path)
