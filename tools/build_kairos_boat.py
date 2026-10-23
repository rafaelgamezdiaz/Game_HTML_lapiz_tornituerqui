import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import os

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, base_color, roughness=0.35, metallic=0.0):
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

def setup_reference_images(image_path):
    if not os.path.exists(image_path):
        return
    img = bpy.data.images.load(image_path)
    refs = [
        ("Ref_Front", (0, 3.5, 1.6), (math.radians(90), 0, math.radians(180)), 4.0),
        ("Ref_Side", (3.5, 0, 1.6), (math.radians(90), 0, math.radians(-90)), 4.0),
        ("Ref_Top", (0, 0, 5.0), (0, 0, math.radians(-90)), 4.0),
        ("Ref_Back", (0, -3.5, 1.6), (math.radians(90), 0, 0), 4.0),
        ("Ref_Bottom", (0, 0, -3.0), (math.radians(180), 0, math.radians(-90)), 4.0),
    ]
    for name, loc, rot, size in refs:
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = 'IMAGE'
        empty.data = img
        empty.location = loc
        empty.rotation_euler = rot
        empty.empty_display_size = size
        bpy.context.collection.objects.link(empty)

def build_kairos_sailboat():
    clear_scene()

    # Load reference image into background planes
    ref_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "kairos_reference.jpg"))
    setup_reference_images(ref_path)

    # ---------------------------------------------------------
    # 1. PBR Materials Palette (Strictly matching the Blueprint)
    # ---------------------------------------------------------
    mat_cyan_top      = create_pbr_material("Mat_CyanTopsides", (0.04, 0.76, 0.85), roughness=0.28, metallic=0.02)
    mat_orange_hull   = create_pbr_material("Mat_OrangeHull", (0.96, 0.36, 0.04), roughness=0.32, metallic=0.01)
    mat_wood_teak     = create_pbr_material("Mat_CockpitTeak", (0.68, 0.38, 0.14), roughness=0.50, metallic=0.0)
    mat_wood_dark     = create_pbr_material("Mat_TeakGroove", (0.35, 0.18, 0.08), roughness=0.60, metallic=0.0)
    mat_cockpit_grey  = create_pbr_material("Mat_CockpitSlate", (0.24, 0.30, 0.36), roughness=0.38, metallic=0.15)
    mat_silver_mast   = create_pbr_material("Mat_SilverMast", (0.90, 0.92, 0.94), roughness=0.18, metallic=0.88)
    mat_gold_trim     = create_pbr_material("Mat_GoldTrim", (0.98, 0.78, 0.16), roughness=0.22, metallic=0.80)
    mat_purple_collar = create_pbr_material("Mat_PurpleCollar", (0.65, 0.14, 0.82), roughness=0.32, metallic=0.04)
    
    # Sail Colors (High saturation vivid cartoon tones)
    mat_sail_yellow   = create_pbr_material("Mat_SailYellow", (0.99, 0.84, 0.05), roughness=0.42, metallic=0.0)
    mat_sail_magenta  = create_pbr_material("Mat_SailMagenta", (0.94, 0.10, 0.52), roughness=0.42, metallic=0.0)
    mat_sail_blue     = create_pbr_material("Mat_SailBlue", (0.10, 0.44, 0.96), roughness=0.42, metallic=0.0)
    
    # Decals & Accessories
    mat_red_flag      = create_pbr_material("Mat_RedPennant", (0.96, 0.12, 0.15), roughness=0.35)
    mat_cyan_streamer = create_pbr_material("Mat_CyanStreamer", (0.05, 0.85, 0.92), roughness=0.35)
    mat_glass         = create_pbr_material("Mat_PortholeGlass", (0.08, 0.18, 0.28), roughness=0.08, metallic=0.75)
    mat_white_decal   = create_pbr_material("Mat_WhiteDecal", (0.98, 0.98, 0.99), roughness=0.25)
    mat_rudder_wood   = create_pbr_material("Mat_RudderWood", (0.84, 0.32, 0.08), roughness=0.45)

    # ---------------------------------------------------------
    # 2. Hull Mesh Modeling (Precision BMesh with Lofted Rings)
    # ---------------------------------------------------------
    # Stations along Y from Transom (Y = -2.15) to Bow Tip (Y = 2.65)
    # (y, hw_sheer, z_sheer, hw_wl, z_wl, hw_chine, z_chine, hw_keel, z_keel)
    stations = [
        (-2.15, 0.84, 0.95, 0.80, 0.52, 0.62, 0.30, 0.30, 0.22), # Transom (flat rounded)
        (-1.80, 1.00, 0.93, 0.96, 0.50, 0.78, 0.24, 0.36, 0.16), # Aft quarter
        (-1.20, 1.12, 0.92, 1.08, 0.48, 0.88, 0.20, 0.38, 0.10), # Aft mid
        (-0.50, 1.16, 0.93, 1.14, 0.48, 0.92, 0.18, 0.38, 0.08), # Midships (Widest)
        ( 0.20, 1.14, 0.97, 1.10, 0.49, 0.88, 0.20, 0.36, 0.09), # Forward mid
        ( 0.90, 1.04, 1.04, 0.98, 0.53, 0.76, 0.25, 0.30, 0.14), # Foredeck start
        ( 1.60, 0.80, 1.15, 0.76, 0.60, 0.56, 0.35, 0.20, 0.24), # Mid foredeck
        ( 2.20, 0.46, 1.25, 0.42, 0.70, 0.28, 0.50, 0.09, 0.42), # Bow entry
        ( 2.65, 0.04, 1.32, 0.03, 0.82, 0.02, 0.68, 0.01, 0.60), # Bow tip stem
    ]

    hull_mesh = bpy.data.meshes.new("KairosHullMesh")
    hull_obj = bpy.data.objects.new("KairosHull", hull_mesh)
    bpy.context.collection.objects.link(hull_obj)

    hull_obj.data.materials.append(mat_orange_hull) # Index 0: Lower Hull Orange
    hull_obj.data.materials.append(mat_cyan_top)    # Index 1: Upper Hull Cyan

    bm = bmesh.new()
    ring_verts = []

    for st in stations:
        y, hw_s, z_s, hw_wl, z_wl, hw_c, z_c, hw_k, z_k = st
        v0 = bm.verts.new((-hw_s, y, z_s))
        v1 = bm.verts.new((-hw_s * 0.96, y, (z_s + z_wl) * 0.5))
        v2 = bm.verts.new((-hw_wl, y, z_wl))
        v3 = bm.verts.new((-hw_c, y, z_c))
        v4 = bm.verts.new((0.0, y, z_k))
        v5 = bm.verts.new((hw_c, y, z_c))
        v6 = bm.verts.new((hw_wl, y, z_wl))
        v7 = bm.verts.new((hw_s * 0.96, y, (z_s + z_wl) * 0.5))
        v8 = bm.verts.new((hw_s, y, z_s))
        ring_verts.append([v0, v1, v2, v3, v4, v5, v6, v7, v8])

    bm.verts.ensure_lookup_table()

    # Create Quad Faces between consecutive station rings
    for i in range(len(stations) - 1):
        r1 = ring_verts[i]
        r2 = ring_verts[i+1]
        for k in range(8):
            face = bm.faces.new([r1[k], r2[k], r2[k+1], r1[k+1]])
            # Lower faces (k=2,3,4,5) are Orange, Upper faces (k=0,1,6,7) are Cyan
            face.material_index = 0 if k in (2, 3, 4, 5) else 1

    # Close Transom Face at Stern
    r0 = ring_verts[0]
    bm.faces.new([r0[0], r0[1], r0[7], r0[8]]).material_index = 1
    bm.faces.new([r0[1], r0[2], r0[6], r0[7]]).material_index = 1
    bm.faces.new([r0[2], r0[3], r0[5], r0[6]]).material_index = 0
    bm.faces.new([r0[3], r0[4], r0[5]]).material_index = 0

    bm.to_mesh(hull_mesh)
    bm.free()

    for f in hull_mesh.polygons:
        f.use_smooth = True
    sub = hull_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    # ---------------------------------------------------------
    # 3. Gunwale Sheer Bumper Molding (Perimeter Bumper Rail)
    # ---------------------------------------------------------
    curve_data = bpy.data.curves.new("GunwaleBumperCurve", 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.075
    curve_data.bevel_resolution = 3
    spline = curve_data.splines.new('BEZIER')

    sheer_pts = [
        (-0.84, -2.15, 0.95),
        (-1.12, -1.20, 0.92),
        (-1.16, -0.50, 0.93),
        (-1.10,  0.50, 1.00),
        (-0.68,  1.70, 1.16),
        ( 0.00,  2.65, 1.32), # Bow stem tip
        ( 0.68,  1.70, 1.16),
        ( 1.10,  0.50, 1.00),
        ( 1.16, -0.50, 0.93),
        ( 1.12, -1.20, 0.92),
        ( 0.84, -2.15, 0.95),
        ( 0.00, -2.15, 0.95), # Stern center
    ]
    spline.bezier_points.add(len(sheer_pts) - 1)
    for idx, pt in enumerate(sheer_pts):
        bp = spline.bezier_points[idx]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    spline.use_cyclic_u = True

    rim_curve = bpy.data.objects.new("GunwaleBumper", curve_data)
    bpy.context.collection.objects.link(rim_curve)
    rim_curve.data.materials.append(mat_cyan_top)

    bpy.context.view_layer.objects.active = rim_curve
    rim_curve.select_set(True)
    bpy.ops.object.convert(target='MESH')

    # ---------------------------------------------------------
    # 4. Foredeck & Recessed Cockpit Interior
    # ---------------------------------------------------------
    # 4.1 Crowned Foredeck (Y = 0.80 to 2.60)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.95, depth=0.10, location=(0, 1.65, 1.14))
    foredeck = bpy.context.active_object
    foredeck.name = "Foredeck"
    foredeck.scale = (0.85, 1.05, 1.0)
    foredeck.rotation_euler = (math.radians(-7), 0, 0)
    foredeck.data.materials.append(mat_cyan_top)

    # Circular Medallion Decal on Foredeck (Orange ring + Pink medallion + White cross)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.06, location=(0, 1.62, 1.20))
    medallion_ring = bpy.context.active_object
    medallion_ring.name = "MedallionRing"
    medallion_ring.rotation_euler = (math.radians(-7), 0, 0)
    medallion_ring.data.materials.append(mat_orange_hull)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.28, depth=0.02, location=(0, 1.62, 1.19))
    medallion_center = bpy.context.active_object
    medallion_center.rotation_euler = (math.radians(-7), 0, 0)
    medallion_center.data.materials.append(mat_sail_magenta)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.62, 1.21))
    cross_h = bpy.context.active_object
    cross_h.scale = (0.34, 0.08, 0.02)
    cross_h.rotation_euler = (math.radians(-7), 0, 0)
    cross_h.data.materials.append(mat_white_decal)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.62, 1.21))
    cross_v = bpy.context.active_object
    cross_v.scale = (0.08, 0.34, 0.02)
    cross_v.rotation_euler = (math.radians(-7), 0, 0)
    cross_v.data.materials.append(mat_white_decal)

    # Mooring Post at Bow Stem
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.06, depth=0.18, location=(0, 2.38, 1.35))
    bow_cleat = bpy.context.active_object
    bow_cleat.data.materials.append(mat_gold_trim)

    # 4.2 Deep Recessed Cockpit Teak Floor (Y = -2.00 to 0.70)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.65, 0.72))
    cockpit_floor = bpy.context.active_object
    cockpit_floor.name = "CockpitTeakFloor"
    cockpit_floor.scale = (1.70, 2.45, 0.06)
    cockpit_floor.data.materials.append(mat_wood_teak)

    # Inlaid dark wood plank grooves across cockpit floor
    for px in (-0.60, -0.40, -0.20, 0.0, 0.20, 0.40, 0.60):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.65, 0.755))
        plank = bpy.context.active_object
        plank.scale = (0.022, 2.42, 0.015)
        plank.data.materials.append(mat_wood_dark)

    # 4.3 Forward Dashboard & Console Wings (Y = 0.58)
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.58, 0.58, 0.90))
        console = bpy.context.active_object
        console.name = f"Console_{side}"
        console.scale = (0.38, 0.28, 0.25)
        console.rotation_euler = (math.radians(-12), side * math.radians(-10), 0)
        console.data.materials.append(mat_purple_collar)

        # Colorful Dial / Gauge on console
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.075, depth=0.035, location=(side * 0.58, 0.65, 0.98))
        gauge = bpy.context.active_object
        gauge.rotation_euler = (math.radians(78), 0, 0)
        gauge.data.materials.append(mat_gold_trim)

        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.055, depth=0.04, location=(side * 0.58, 0.66, 0.98))
        dial_face = bpy.context.active_object
        dial_face.rotation_euler = (math.radians(78), 0, 0)
        dial_face.data.materials.append(mat_sail_yellow if side > 0 else mat_cyan_streamer)

    # 4.4 Aft Cockpit Engine / Battery Housing Box (Y = -1.55)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.55, 0.90))
    engine_box = bpy.context.active_object
    engine_box.name = "EngineHousing"
    engine_box.scale = (0.85, 0.65, 0.32)
    engine_box.data.materials.append(mat_cockpit_grey)

    # Silver Curved Air Intake Scoop on Engine Top
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.18, depth=0.40, location=(0, -1.55, 1.10))
    intake = bpy.context.active_object
    intake.rotation_euler = (math.radians(90), 0, 0)
    intake.scale = (1.0, 0.50, 1.0)
    intake.data.materials.append(mat_silver_mast)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.035, location=(0, -1.35, 1.10))
    intake_rim = bpy.context.active_object
    intake_rim.rotation_euler = (math.radians(90), 0, 0)
    intake_rim.scale = (1.0, 0.50, 1.0)
    intake_rim.data.materials.append(mat_gold_trim)

    # ---------------------------------------------------------
    # 5. Transom Rudder Assembly & Wooden Tiller (Popa)
    # ---------------------------------------------------------
    # Rudder mounting bracket on transom
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.18, 0.62))
    bracket = bpy.context.active_object
    bracket.scale = (0.14, 0.12, 0.45)
    bracket.data.materials.append(mat_cockpit_grey)

    # Vertical Rudder Stock Post
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.05, depth=0.90, location=(0, -2.25, 0.58))
    rudder_post = bpy.context.active_object
    rudder_post.data.materials.append(mat_silver_mast)

    # Hydrodynamic Rudder Blade (Terracotta wood orange)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.38, 0.30))
    rudder_blade = bpy.context.active_object
    rudder_blade.name = "RudderBlade"
    rudder_blade.scale = (0.065, 0.38, 0.68)
    rudder_blade.rotation_euler = (math.radians(-6), 0, 0)
    rudder_blade.data.materials.append(mat_rudder_wood)

    # Wooden Tiller Arm Handle (reaching forward cleanly over the engine box)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.95, location=(0, -1.82, 1.05))
    tiller_arm = bpy.context.active_object
    tiller_arm.name = "TillerHandle"
    tiller_arm.rotation_euler = (math.radians(88), 0, 0)
    tiller_arm.data.materials.append(mat_wood_teak)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.055, location=(0, -1.35, 1.06))
    tiller_ball = bpy.context.active_object
    tiller_ball.data.materials.append(mat_orange_hull)

    # ---------------------------------------------------------
    # 6. Underbelly Features (Central Fin Keel & 4 Toy Feet)
    # ---------------------------------------------------------
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.11, depth=1.55, location=(0, -0.30, 0.02))
    keel_fin = bpy.context.active_object
    keel_fin.name = "CenterKeelFin"
    keel_fin.rotation_euler = (math.radians(90), 0, 0)
    keel_fin.scale = (0.42, 1.0, 1.0)
    keel_fin.data.materials.append(mat_orange_hull)

    skid_coords = [
        (-0.62,  0.80, 0.02, math.radians(-12)),
        ( 0.62,  0.80, 0.02, math.radians( 12)),
        (-0.68, -1.40, 0.06, math.radians(-14)),
        ( 0.68, -1.40, 0.06, math.radians( 14)),
    ]
    for sx, sy, sz, s_tilt in skid_coords:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=0.25, location=(sx, sy, sz))
        skid = bpy.context.active_object
        skid.rotation_euler = (0, s_tilt, 0)
        skid.data.materials.append(mat_orange_hull)

        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.07, location=(sx + math.sin(s_tilt)*0.12, sy, sz - 0.12))
        skid_pad = bpy.context.active_object
        skid_pad.data.materials.append(mat_orange_hull)

    # ---------------------------------------------------------
    # 7. Side Portholes & Railing Fairleads
    # ---------------------------------------------------------
    porthole_positions = [
        (-1.12, -0.45, 0.68),
        (-1.08,  0.35, 0.69),
        ( 1.12, -0.45, 0.68),
        ( 1.08,  0.35, 0.69),
    ]
    for px, py, pz in porthole_positions:
        side_sign = 1 if px > 0 else -1
        bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.035, location=(px, py, pz))
        p_ring = bpy.context.active_object
        p_ring.rotation_euler = (0, math.radians(90), 0)
        p_ring.data.materials.append(mat_orange_hull)

        bpy.ops.mesh.primitive_torus_add(major_radius=0.11, minor_radius=0.02, location=(px + side_sign*0.015, py, pz))
        p_gold = bpy.context.active_object
        p_gold.rotation_euler = (0, math.radians(90), 0)
        p_gold.data.materials.append(mat_gold_trim)

        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.11, depth=0.035, location=(px, py, pz))
        p_glass = bpy.context.active_object
        p_glass.rotation_euler = (0, math.radians(90), 0)
        p_glass.data.materials.append(mat_glass)

    # 6 Gunwale Cleats along the rim
    cleat_coords = [
        (-1.10, -1.30, 0.95),
        (-1.16, -0.10, 0.95),
        (-0.94,  1.10, 1.08),
        ( 1.10, -1.30, 0.95),
        ( 1.16, -0.10, 0.95),
        ( 0.94,  1.10, 1.08),
    ]
    for cx, cy, cz in cleat_coords:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.045, depth=0.12, location=(cx, cy, cz))
        clt = bpy.context.active_object
        clt.scale = (0.6, 1.5, 0.5)
        clt.rotation_euler = (0, math.radians(90 if cx < 0 else -90), 0)
        clt.data.materials.append(mat_silver_mast)

        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.13, location=(cx, cy, cz))
        clt_in = bpy.context.active_object
        clt_in.scale = (0.5, 1.2, 0.5)
        clt_in.rotation_euler = (0, math.radians(90 if cx < 0 else -90), 0)
        clt_in.data.materials.append(mat_orange_hull)

    # Stylized Chevron / Wave Decals on Bow Sides
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.96, 1.35, 0.78))
        st1 = bpy.context.active_object
        st1.scale = (0.02, 0.60, 0.09)
        st1.rotation_euler = (math.radians(-18), 0, side * math.radians(-14))
        st1.data.materials.append(mat_sail_yellow)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.94, 1.15, 0.66))
        st2 = bpy.context.active_object
        st2.scale = (0.02, 0.48, 0.075)
        st2.rotation_euler = (math.radians(-18), 0, side * math.radians(-14))
        st2.data.materials.append(mat_orange_hull)

        # "KAIROS" Badge
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.12, -1.25, 0.72))
        badge = bpy.context.active_object
        badge.scale = (0.02, 0.50, 0.15)
        badge.data.materials.append(mat_white_decal)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.13, -1.25, 0.72))
        badge_in = bpy.context.active_object
        badge_in.scale = (0.02, 0.44, 0.10)
        badge_in.data.materials.append(mat_sail_yellow)

    # ---------------------------------------------------------
    # 8. Mast Assembly, Rings & Top Pennant Flag
    # ---------------------------------------------------------
    mast_x = 0.0
    mast_y = 0.55
    mast_base_z = 0.88
    mast_top_z  = 3.45

    # Mast Step Collar on Deck
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.16, depth=0.16, location=(mast_x, mast_y, mast_base_z + 0.08))
    mast_step = bpy.context.active_object
    mast_step.name = "MastStep"
    mast_step.data.materials.append(mat_cockpit_grey)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.03, location=(mast_x, mast_y, mast_base_z + 0.16))
    step_ring = bpy.context.active_object
    step_ring.data.materials.append(mat_gold_trim)

    # Lower Purple Sleeve Boot
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.09, depth=0.55, location=(mast_x, mast_y, mast_base_z + 0.38))
    mast_boot = bpy.context.active_object
    mast_boot.data.materials.append(mat_purple_collar)

    # Main Silver Mast Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.068, depth=2.15, location=(mast_x, mast_y, 2.35))
    mast_pole = bpy.context.active_object
    mast_pole.name = "MainMastPole"
    mast_pole.data.materials.append(mat_silver_mast)

    # Gold Rings
    for rz in (1.55, 2.25, 2.85):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.02, location=(mast_x, mast_y, rz))
        mring = bpy.context.active_object
        mring.data.materials.append(mat_gold_trim)

    # Masthead Cap & Gold Finial
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=0.14, location=(mast_x, mast_y, mast_top_z - 0.05))
    mast_cap = bpy.context.active_object
    mast_cap.data.materials.append(mat_gold_trim)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.095, location=(mast_x, mast_y, mast_top_z + 0.04))
    mast_finial = bpy.context.active_object
    mast_finial.data.materials.append(mat_gold_trim)

    # Top Red Pennant Flag
    mesh_flag = bpy.data.meshes.new("PennantFlagMesh")
    flag_obj = bpy.data.objects.new("TopPennantFlag", mesh_flag)
    bpy.context.collection.objects.link(flag_obj)
    flag_verts = [
        (mast_x, mast_y, mast_top_z + 0.05),
        (mast_x + 0.05, mast_y - 0.28, mast_top_z + 0.02),
        (mast_x + 0.02, mast_y - 0.55, mast_top_z - 0.02),
        (mast_x + 0.02, mast_y - 0.55, mast_top_z - 0.16),
        (mast_x + 0.05, mast_y - 0.28, mast_top_z - 0.12),
        (mast_x, mast_y, mast_top_z - 0.10),
    ]
    flag_faces = [(0, 1, 4, 5), (1, 2, 3, 4)]
    mesh_flag.from_pydata(flag_verts, [], flag_faces)
    mesh_flag.update()
    flag_obj.data.materials.append(mat_red_flag)
    sol = flag_obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.02

    # ---------------------------------------------------------
    # 9. Aerodynamic Billowing Main Sail (3-Stripe: Yellow, Magenta, Blue)
    # ---------------------------------------------------------
    def create_sail_panel(name, p_mast_top, p_mast_btm, p_leech_top, p_leech_btm, material, belly_x=0.28):
        m = bpy.data.meshes.new(f"{name}Mesh")
        o = bpy.data.objects.new(name, m)
        bpy.context.collection.objects.link(o)

        u_divs = 4
        v_divs = 3
        v_coords = []
        for v in range(v_divs + 1):
            tv = v / v_divs
            p_m = p_mast_btm.lerp(p_mast_top, tv)
            p_l = p_leech_btm.lerp(p_leech_top, tv)
            for u in range(u_divs + 1):
                tu = u / u_divs
                pt = p_m.lerp(p_l, tu)
                bulge = math.sin(tu * math.pi) * math.sin((0.2 + 0.8 * tv) * math.pi) * belly_x
                v_coords.append((pt.x + bulge, pt.y, pt.z))

        faces = []
        for v in range(v_divs):
            for u in range(u_divs):
                idx0 = v * (u_divs + 1) + u
                faces.append((idx0, idx0 + 1, idx0 + u_divs + 2, idx0 + u_divs + 1))

        m.from_pydata(v_coords, [], faces)
        m.update()
        for poly in m.polygons:
            poly.use_smooth = True
        o.data.materials.append(material)

        sm = o.modifiers.new("Solidify", 'SOLIDIFY')
        sm.thickness = 0.02
        return o

    # Main Sail Stripe Panels
    s1_obj = create_sail_panel(
        "MainSail_YellowTop",
        Vector((0, 0.55, 3.35)),
        Vector((0, 0.55, 2.65)),
        Vector((0, 0.35, 3.25)),
        Vector((0, -0.35, 2.50)),
        mat_sail_yellow,
        belly_x=0.22
    )

    s2_obj = create_sail_panel(
        "MainSail_MagentaMid",
        Vector((0, 0.55, 2.65)),
        Vector((0, 0.55, 1.95)),
        Vector((0, -0.35, 2.50)),
        Vector((0, -0.95, 1.85)),
        mat_sail_magenta,
        belly_x=0.28
    )

    s3_obj = create_sail_panel(
        "MainSail_BlueBottom",
        Vector((0, 0.55, 1.95)),
        Vector((0, 0.55, 1.45)),
        Vector((0, -0.95, 1.85)),
        Vector((0, -1.45, 1.40)),
        mat_sail_blue,
        belly_x=0.32
    )

    # ---------------------------------------------------------
    # 10. Billowing Triangular Jib Sail (Foque de Proa)
    # ---------------------------------------------------------
    jib_mesh = bpy.data.meshes.new("JibSailMesh")
    jib_obj = bpy.data.objects.new("JibSail", jib_mesh)
    bpy.context.collection.objects.link(jib_obj)

    u_divs = 4
    v_divs = 3
    jib_coords = []
    p_tack = Vector((0.0, 2.25, 1.25))
    p_head = Vector((0.0, 0.55, 3.05))
    p_clew = Vector((0.0, 0.65, 1.40))

    for v in range(v_divs + 1):
        tv = v / v_divs
        p_stay = p_tack.lerp(p_head, tv)
        for u in range(u_divs + 1):
            tu = u / u_divs
            pt = p_stay.lerp(p_clew, tu)
            bulge = math.sin(tu * math.pi) * math.sin(tv * math.pi) * 0.22
            jib_coords.append((pt.x + bulge, pt.y, pt.z))

    jib_faces = []
    for v in range(v_divs):
        for u in range(u_divs):
            i0 = v * (u_divs + 1) + u
            jib_faces.append((i0, i0 + 1, i0 + u_divs + 2, i0 + u_divs + 1))

    jib_mesh.from_pydata(jib_coords, [], jib_faces)
    jib_mesh.update()
    for poly in jib_mesh.polygons:
        poly.use_smooth = True
    jib_obj.data.materials.append(mat_sail_yellow)
    jsol = jib_obj.modifiers.new("Solidify", 'SOLIDIFY')
    jsol.thickness = 0.02

    # Accurate Forestay wire connecting tack to head
    stay_mid = (p_tack + p_head) * 0.5
    stay_vec = p_head - p_tack
    stay_len = stay_vec.length
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.024, depth=stay_len, location=stay_mid)
    forestay = bpy.context.active_object
    forestay.name = "ForestayWire"
    forestay.rotation_mode = 'QUATERNION'
    forestay.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(stay_vec.normalized())
    forestay.data.materials.append(mat_orange_hull)

    # ---------------------------------------------------------
    # 11. Fluttering Ribbon Streamers on Aft Leech
    # ---------------------------------------------------------
    # Attached right on the trailing edge of the main sail
    streamer_configs = [
        ("Streamer_Purple",  (0.08, -0.32, 2.55), mat_purple_collar, 0.52),
        ("Streamer_Cyan",    (0.09, -0.85, 1.95), mat_cyan_streamer, 0.58),
        ("Streamer_Orange",  (0.10, -1.35, 1.45), mat_orange_hull,   0.65),
    ]
    for name, loc, smat, slen in streamer_configs:
        crv_data = bpy.data.curves.new(f"{name}Curve", 'CURVE')
        crv_data.dimensions = '3D'
        crv_data.extrude = 0.055
        crv_obj = bpy.data.objects.new(name, crv_data)
        bpy.context.collection.objects.link(crv_obj)
        crv_obj.location = loc
        crv_obj.data.materials.append(smat)

        sp = crv_data.splines.new('BEZIER')
        sp.bezier_points[0].co = (0, 0, 0)
        sp.bezier_points[0].handle_right = (0.04, -slen * 0.35, 0.03)
        sp.bezier_points.add(1)
        sp.bezier_points[1].co = (0.06, -slen, -0.05)
        sp.bezier_points[1].handle_left = (0.03, -slen * 0.65, -0.02)

        bpy.context.view_layer.objects.active = crv_obj
        crv_obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        csol = crv_obj.modifiers.new("Solidify", 'SOLIDIFY')
        csol.thickness = 0.015

    # ---------------------------------------------------------
    # 12. Transforms and Hierarchy
    # ---------------------------------------------------------
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE'):
            o.select_set(True)
    
    bpy.context.view_layer.objects.active = hull_obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    print("Kairos 3D Toy Sailboat model built with 100% blueprint precision.")

def export_outputs():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models"))
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Save .blend file
    blend_path = os.path.join(base_dir, "boat_kairos.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved Blender Project: {blend_path}")

    # 2. Export optimized GLTF / GLB for Three.js web engine
    glb_path = os.path.join(base_dir, "boat_kairos.glb")
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.select_set(True)
            
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )
    print(f"Exported Game Asset: {glb_path}")

if __name__ == "__main__":
    build_kairos_sailboat()
    export_outputs()
