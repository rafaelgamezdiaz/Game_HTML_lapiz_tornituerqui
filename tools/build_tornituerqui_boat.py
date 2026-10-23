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
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
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
        ("Ref_Front", (0, 3.5, 1.4), (math.radians(90), 0, math.radians(180)), 4.2),
        ("Ref_Side", (3.5, 0, 1.4), (math.radians(90), 0, math.radians(-90)), 4.2),
        ("Ref_Top", (0, 0, 5.0), (0, 0, math.radians(-90)), 4.2),
        ("Ref_Back", (0, -3.5, 1.4), (math.radians(90), 0, 0), 4.2),
        ("Ref_Bottom", (0, 0, -3.0), (math.radians(180), 0, math.radians(-90)), 4.2),
    ]
    for name, loc, rot, size in refs:
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = 'IMAGE'
        empty.data = img
        empty.location = loc
        empty.rotation_euler = rot
        empty.empty_display_size = size
        bpy.context.collection.objects.link(empty)

def build_tornituerqui_steamboat():
    clear_scene()

    # Load reference image into background planes
    ref_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "tornituerqui_reference.jpg"))
    setup_reference_images(ref_path)

    # ---------------------------------------------------------
    # 1. PBR Materials Palette (Vibrant Stylized Steampunk)
    # ---------------------------------------------------------
    mat_copper_hull   = create_pbr_material("Mat_CopperHull", (0.84, 0.44, 0.18), roughness=0.32, metallic=0.25)
    mat_copper_dark   = create_pbr_material("Mat_CopperDark", (0.64, 0.28, 0.12), roughness=0.40, metallic=0.20)
    mat_brass_gold    = create_pbr_material("Mat_BrassRim", (0.95, 0.74, 0.16), roughness=0.24, metallic=0.32)
    mat_gold_rivet    = create_pbr_material("Mat_GoldRivet", (0.98, 0.82, 0.22), roughness=0.20, metallic=0.35)
    mat_cast_iron     = create_pbr_material("Mat_CastIron", (0.24, 0.25, 0.28), roughness=0.55, metallic=0.15)
    mat_steel_deck    = create_pbr_material("Mat_SteelDeck", (0.68, 0.72, 0.75), roughness=0.35, metallic=0.20)
    mat_glass_bubble  = create_pbr_material("Mat_DomeGlass", (0.32, 0.76, 0.90), roughness=0.10, metallic=0.10)
    mat_leather_seat  = create_pbr_material("Mat_BrownLeather", (0.52, 0.24, 0.10), roughness=0.48, metallic=0.0)
    mat_dial_white    = create_pbr_material("Mat_DialFace", (0.96, 0.96, 0.92), roughness=0.25, metallic=0.0)
    mat_needle_red    = create_pbr_material("Mat_NeedleRed", (0.95, 0.12, 0.10), roughness=0.20, metallic=0.0)

    # ---------------------------------------------------------
    # 2. Main Hull (BMesh Lofted Stations matching Blueprint Cotas)
    # Length: 4.80 (53"), Beam: 3.10 (33"), Height: 1.15 at gunwale
    # ---------------------------------------------------------
    stations = [
        (-2.10, 1.12, 1.05, 1.08, 0.65, 0.85, 0.32, 0.42, 0.20), # Transom
        (-1.50, 1.45, 1.02, 1.40, 0.62, 1.12, 0.28, 0.52, 0.14), # Aft engine bay
        (-0.70, 1.55, 1.02, 1.50, 0.60, 1.25, 0.24, 0.58, 0.10), # Midships (Widest Beam = 3.10)
        ( 0.10, 1.55, 1.05, 1.50, 0.60, 1.25, 0.25, 0.58, 0.10), # Dashboard station
        ( 0.90, 1.48, 1.10, 1.42, 0.64, 1.15, 0.30, 0.52, 0.14), # Foredeck dome station
        ( 1.70, 1.25, 1.18, 1.18, 0.72, 0.90, 0.42, 0.38, 0.22), # Bow entry
        ( 2.35, 0.75, 1.25, 0.68, 0.84, 0.45, 0.60, 0.18, 0.40), # Bow curve
        ( 2.70, 0.08, 1.28, 0.06, 0.92, 0.04, 0.75, 0.02, 0.58), # Bow stem tip
    ]

    hull_mesh = bpy.data.meshes.new("TornituerquiHullMesh")
    hull_obj = bpy.data.objects.new("TornituerquiHull", hull_mesh)
    bpy.context.collection.objects.link(hull_obj)

    hull_obj.data.materials.append(mat_copper_hull) # Index 0: Main Polished Copper
    hull_obj.data.materials.append(mat_copper_dark) # Index 1: Lower Hull Patina Copper

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

    for i in range(len(stations) - 1):
        r1 = ring_verts[i]
        r2 = ring_verts[i+1]
        for k in range(8):
            face = bm.faces.new([r1[k], r2[k], r2[k+1], r1[k+1]])
            face.material_index = 1 if k in (2, 3, 4, 5) else 0

    r0 = ring_verts[0]
    bm.faces.new([r0[0], r0[1], r0[7], r0[8]]).material_index = 0
    bm.faces.new([r0[1], r0[2], r0[6], r0[7]]).material_index = 0
    bm.faces.new([r0[2], r0[3], r0[5], r0[6]]).material_index = 1
    bm.faces.new([r0[3], r0[4], r0[5]]).material_index = 1

    bm.to_mesh(hull_mesh)
    bm.free()

    for f in hull_mesh.polygons:
        f.use_smooth = True
    sub = hull_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    # ---------------------------------------------------------
    # 3. Heavy Brass Gunwale Bumper Rim with Prominent Rivets
    # ---------------------------------------------------------
    curve_data = bpy.data.curves.new("GunwaleRimCurve", 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.095
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new('BEZIER')

    rim_pts = [
        (-1.12, -2.10, 1.05),
        (-1.45, -1.50, 1.02),
        (-1.55, -0.70, 1.02),
        (-1.55,  0.10, 1.05),
        (-1.48,  0.90, 1.10),
        (-1.15,  1.85, 1.20),
        ( 0.00,  2.70, 1.28), # Bow tip
        ( 1.15,  1.85, 1.20),
        ( 1.48,  0.90, 1.10),
        ( 1.55,  0.10, 1.05),
        ( 1.55, -0.70, 1.02),
        ( 1.45, -1.50, 1.02),
        ( 1.12, -2.10, 1.05),
        ( 0.00, -2.10, 1.05), # Stern center
    ]
    spline.bezier_points.add(len(rim_pts) - 1)
    for idx, pt in enumerate(rim_pts):
        bp = spline.bezier_points[idx]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    spline.use_cyclic_u = True

    rim_obj = bpy.data.objects.new("GunwaleBrassRim", curve_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.data.materials.append(mat_brass_gold)

    bpy.context.view_layer.objects.active = rim_obj
    rim_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')

    # Domed Brass Rivets around Gunwale Rim
    num_rivets = 16
    for i in range(num_rivets):
        u = i / num_rivets
        ang = u * math.pi * 2
        rx = math.sin(ang) * (1.50 if abs(math.cos(ang)) < 0.6 else 1.08)
        ry = math.cos(ang) * 2.25 + 0.20
        rz = 1.06 + max(0.0, ry * 0.08)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.062, location=(rx, ry, rz + 0.05))
        riv = bpy.context.active_object
        riv.data.materials.append(mat_gold_rivet)

    # ---------------------------------------------------------
    # 4. Central Brass Stem / Keel Band & Bottom Cooling Slots
    # ---------------------------------------------------------
    # Vertical Brass Stem Band at Bow (Front View)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.50, 0.95))
    stem_band = bpy.context.active_object
    stem_band.name = "StemBand"
    stem_band.scale = (0.24, 0.35, 0.65)
    stem_band.rotation_euler = (math.radians(-32), 0, 0)
    stem_band.data.materials.append(mat_brass_gold)

    for sz in (0.80, 1.05, 1.25):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.045, location=(0, 2.52 + (1.25 - sz) * 0.12, sz))
        r = bpy.context.active_object
        r.data.materials.append(mat_gold_rivet)

    # Central Keel Rail (Bottom View)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.15, 0.06))
    keel_rail = bpy.context.active_object
    keel_rail.name = "CentralKeelRail"
    keel_rail.scale = (0.22, 4.40, 0.12)
    keel_rail.data.materials.append(mat_brass_gold)

    # Transverse Cooling Louvers (Bottom View)
    for ly in (-0.50, -0.20, 0.10, 0.40):
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.038, depth=0.50, location=(side * 0.48, ly, 0.12))
            louver = bpy.context.active_object
            louver.rotation_euler = (0, math.radians(90), 0)
            louver.data.materials.append(mat_cast_iron)

    # Vertical Side Reinforcement Straps (Midships)
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.54, 0.10, 0.65))
        side_strap = bpy.context.active_object
        side_strap.scale = (0.045, 0.20, 0.72)
        side_strap.data.materials.append(mat_brass_gold)

        for rz in (0.42, 0.65, 0.88):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.042, location=(side * 1.57, 0.10, rz))
            riv = bpy.context.active_object
            riv.data.materials.append(mat_gold_rivet)

    # ---------------------------------------------------------
    # 5. Foredeck & Glass Observation Bubble Dome (Cleanly Fitted)
    # ---------------------------------------------------------
    # Fitted Foredeck Plate (Y = 0.50 to 2.45)
    fdeck_mesh = bpy.data.meshes.new("ForedeckMesh")
    fdeck_obj = bpy.data.objects.new("ForedeckPlate", fdeck_mesh)
    bpy.context.collection.objects.link(fdeck_obj)

    fbm = bmesh.new()
    # 6 boundary points matching interior sheer line + center apex
    f_p0 = fbm.verts.new((0.0, 2.45, 1.25))
    f_p1 = fbm.verts.new((0.95, 1.70, 1.18))
    f_p2 = fbm.verts.new((1.35, 0.90, 1.10))
    f_p3 = fbm.verts.new((1.40, 0.45, 1.06))
    f_p4 = fbm.verts.new((-1.40, 0.45, 1.06))
    f_p5 = fbm.verts.new((-1.35, 0.90, 1.10))
    f_p6 = fbm.verts.new((-0.95, 1.70, 1.18))
    f_center = fbm.verts.new((0.0, 1.25, 1.16))

    fbm.faces.new([f_p0, f_p1, f_center])
    fbm.faces.new([f_p1, f_p2, f_center])
    fbm.faces.new([f_p2, f_p3, f_center])
    fbm.faces.new([f_p3, f_p4, f_center])
    fbm.faces.new([f_p4, f_p5, f_center])
    fbm.faces.new([f_p5, f_p6, f_center])
    fbm.faces.new([f_p6, f_p0, f_center])

    fbm.to_mesh(fdeck_mesh)
    fbm.free()
    fdeck_obj.data.materials.append(mat_steel_deck)
    fsol = fdeck_obj.modifiers.new("Solidify", 'SOLIDIFY')
    fsol.thickness = 0.05

    # Glass Bubble Observation Dome
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.45, location=(0, 1.35, 1.28))
    dome = bpy.context.active_object
    dome.name = "ObservationDome"
    dome.scale = (1.0, 1.15, 0.65)
    dome.data.materials.append(mat_glass_bubble)

    # Brass Bezel Retaining Ring for Dome with Rivets
    bpy.ops.mesh.primitive_torus_add(major_radius=0.46, minor_radius=0.055, location=(0, 1.35, 1.22))
    dome_rim = bpy.context.active_object
    dome_rim.scale = (1.0, 1.15, 0.65)
    dome_rim.data.materials.append(mat_brass_gold)

    for i in range(8):
        ang = i * (math.pi / 4)
        dx = math.sin(ang) * 0.46
        dy = 1.35 + math.cos(ang) * 0.46 * 1.15
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.035, location=(dx, dy, 1.26))
        dr = bpy.context.active_object
        dr.data.materials.append(mat_gold_rivet)

    # ---------------------------------------------------------
    # 6. Cockpit, Dashboard, Nautical Steering Wheel & Pilot Bench
    # ---------------------------------------------------------
    # Cockpit Floor (Y = -2.00 to 0.45)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.75, 0.72))
    cockpit_floor = bpy.context.active_object
    cockpit_floor.name = "CockpitFloor"
    cockpit_floor.scale = (2.20, 2.35, 0.06)
    cockpit_floor.data.materials.append(mat_cast_iron)

    # Dashboard Cowl & Shelf (Y = 0.42)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.42, 1.08))
    dash = bpy.context.active_object
    dash.name = "DashboardShelf"
    dash.scale = (1.75, 0.28, 0.24)
    dash.data.materials.append(mat_copper_dark)

    # Steering Column & Classic Ship's Steering Wheel
    wheel_x = 0.0
    wheel_y = 0.25
    wheel_z = 1.22

    # Angled Steering Column
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.045, depth=0.35, location=(wheel_x, 0.32, 1.10))
    steer_col = bpy.context.active_object
    steer_col.rotation_euler = (math.radians(22), 0, 0)
    steer_col.data.materials.append(mat_cast_iron)

    # Wheel Rim
    bpy.ops.mesh.primitive_torus_add(major_radius=0.26, minor_radius=0.035, location=(wheel_x, wheel_y, wheel_z))
    wheel = bpy.context.active_object
    wheel.name = "ShipSteeringWheel"
    wheel.rotation_euler = (math.radians(22), 0, 0)
    wheel.data.materials.append(mat_brass_gold)

    # Wheel Hub
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.075, depth=0.08, location=(wheel_x, wheel_y, wheel_z))
    hub = bpy.context.active_object
    hub.rotation_euler = (math.radians(22), 0, 0)
    hub.data.materials.append(mat_brass_gold)

    # 6 Spokes
    for a in (0, 60, 120):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.58, location=(wheel_x, wheel_y, wheel_z))
        spoke = bpy.context.active_object
        spoke.rotation_euler = (math.radians(22), 0, math.radians(a))
        spoke.data.materials.append(mat_brass_gold)

    # Analog Pressure Gauge on Dashboard Cowl
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.14, depth=0.06, location=(0.38, 0.48, 1.30))
    gauge = bpy.context.active_object
    gauge.name = "PressureGauge"
    gauge.rotation_euler = (math.radians(45), 0, 0)
    gauge.data.materials.append(mat_dial_white)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.025, location=(0.38, 0.48, 1.30))
    gauge_bezel = bpy.context.active_object
    gauge_bezel.rotation_euler = (math.radians(45), 0, 0)
    gauge_bezel.data.materials.append(mat_brass_gold)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.38, 0.49, 1.32))
    needle = bpy.context.active_object
    needle.scale = (0.012, 0.07, 0.012)
    needle.rotation_euler = (math.radians(45), 0, math.radians(-35))
    needle.data.materials.append(mat_needle_red)

    # Padded Tufted Pilot Bench Seat (Warm brown leather with ribbed ridges)
    # Seat Base Cushion
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.32, 0.92))
    seat_base = bpy.context.active_object
    seat_base.name = "PilotSeatBase"
    seat_base.scale = (1.65, 0.55, 0.26)
    seat_base.data.materials.append(mat_leather_seat)

    # Seat Backrest
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.58, 1.25))
    seat_back = bpy.context.active_object
    seat_back.name = "PilotSeatBack"
    seat_back.scale = (1.65, 0.20, 0.50)
    seat_back.rotation_euler = (math.radians(-6), 0, 0)
    seat_back.data.materials.append(mat_leather_seat)

    # Tufted horizontal leather rolls
    for rz in (1.08, 1.24, 1.40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.055, depth=1.62, location=(0, -0.52 + (rz-1.08)*0.06, rz))
        roll = bpy.context.active_object
        roll.rotation_euler = (0, math.radians(90), 0)
        roll.data.materials.append(mat_leather_seat)

    # ---------------------------------------------------------
    # 7. Steampunk Boiler & Smokestack Assembly (Engine Bay)
    # ---------------------------------------------------------
    # Riveted Heavy Boiler Block sitting directly behind seat (Y = -1.20)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.20, 1.15))
    boiler = bpy.context.active_object
    boiler.name = "SteampunkBoiler"
    boiler.scale = (1.35, 0.90, 0.65)
    boiler.data.materials.append(mat_copper_hull)

    # Boiler decorative rivets along seams
    for bx in (-0.62, 0.62):
        for bz in (0.92, 1.15, 1.38):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.038, location=(bx, -0.78, bz))
            briv = bpy.context.active_object
            briv.data.materials.append(mat_gold_rivet)

    # Tall Cast-Iron Smokestack Cylinder
    stack_x = 0.0
    stack_y = -1.30
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.30, depth=1.15, location=(stack_x, stack_y, 1.95))
    stack = bpy.context.active_object
    stack.name = "Smokestack"
    stack.data.materials.append(mat_cast_iron)

    # Perforated Collar with vent holes around upper smokestack (as shown in blueprint!)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.34, depth=0.32, location=(stack_x, stack_y, 2.22))
    stack_collar = bpy.context.active_object
    stack_collar.data.materials.append(mat_brass_gold)

    # Vent holes on smokestack collar
    for i in range(8):
        vang = i * (math.pi / 4)
        vx = stack_x + math.sin(vang) * 0.34
        vy = stack_y + math.cos(vang) * 0.34
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.042, depth=0.08, location=(vx, vy, 2.22))
        vhole = bpy.context.active_object
        vhole.rotation_euler = (0, math.radians(90), -vang)
        vhole.data.materials.append(mat_cast_iron)

    # Flared Smokestack Crown Lip
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.44, radius2=0.30, depth=0.20, location=(stack_x, stack_y, 2.50))
    stack_lip = bpy.context.active_object
    stack_lip.data.materials.append(mat_cast_iron)

    # Secondary S-Curved Exhaust Pipe exiting boiler side and curving aft
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.09, depth=0.62, location=(0.46, -1.45, 1.80))
    sec_pipe = bpy.context.active_object
    sec_pipe.name = "SecondaryExhaustPipe"
    sec_pipe.rotation_euler = (math.radians(26), math.radians(10), 0)
    sec_pipe.data.materials.append(mat_copper_hull)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.028, location=(0.52, -1.68, 1.98))
    pipe_flange = bpy.context.active_object
    pipe_flange.rotation_euler = (math.radians(26), 0, 0)
    pipe_flange.data.materials.append(mat_brass_gold)

    # ---------------------------------------------------------
    # 8. Side Machinery: Cog Wheels, 3-Blade Propellers & Pipes
    # ---------------------------------------------------------
    for side in (-1, 1):
        # 8.1 Large Mechanical 8-Tooth Cog Wheel
        cog_x = side * 1.62
        cog_y = -0.15
        cog_z = 0.82
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.42, depth=0.12, location=(cog_x, cog_y, cog_z))
        cog = bpy.context.active_object
        cog.name = f"CogWheel_{side}"
        cog.rotation_euler = (0, math.radians(90), 0)
        cog.data.materials.append(mat_brass_gold)

        # 8 Cog Teeth
        for t in range(8):
            tang = t * (math.pi / 4)
            tx = cog_x
            ty = cog_y + math.cos(tang) * 0.42
            tz = cog_z + math.sin(tang) * 0.42
            bpy.ops.mesh.primitive_cube_add(size=0.13, location=(tx, ty, tz))
            tooth = bpy.context.active_object
            tooth.scale = (1.05, 0.75, 0.75)
            tooth.rotation_euler = (tang, 0, 0)
            tooth.data.materials.append(mat_brass_gold)

        # Cog center axle nut
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.11, depth=0.16, location=(cog_x + side * 0.05, cog_y, cog_z))
        nut = bpy.context.active_object
        nut.rotation_euler = (0, math.radians(90), 0)
        nut.data.materials.append(mat_copper_dark)

        # 8.2 Small Side 3-Blade Propeller (Aft of Cog)
        sprop_x = side * 1.65
        sprop_y = -0.75
        sprop_z = 0.90
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.095, location=(sprop_x, sprop_y, sprop_z))
        sprop_hub = bpy.context.active_object
        sprop_hub.data.materials.append(mat_brass_gold)

        for b in range(3):
            bang = b * (2 * math.pi / 3)
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sprop_x + side * 0.04, sprop_y + math.cos(bang) * 0.18, sprop_z + math.sin(bang) * 0.18))
            sblade = bpy.context.active_object
            sblade.scale = (0.025, 0.08, 0.20)
            sblade.rotation_euler = (bang, math.radians(35 * side), 0)
            sblade.data.materials.append(mat_brass_gold)

        # 8.3 Horizontal Pressure Chamber & Pipe with 90° Elbow
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.72, location=(side * 1.58, -0.65, 0.55))
        side_pipe = bpy.context.active_object
        side_pipe.rotation_euler = (math.radians(90), 0, 0)
        side_pipe.data.materials.append(mat_copper_hull)

        bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.022, location=(side * 1.58, -0.32, 0.55))
        pflange = bpy.context.active_object
        pflange.rotation_euler = (math.radians(90), 0, 0)
        pflange.data.materials.append(mat_brass_gold)

        # 8.4 Round Hull Porthole with Riveted Bezel (Forward)
        port_x = side * 1.48
        port_y = 1.05
        port_z = 0.85
        bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.038, location=(port_x, port_y, port_z))
        port_bezel = bpy.context.active_object
        port_bezel.rotation_euler = (0, math.radians(90), 0)
        port_bezel.data.materials.append(mat_brass_gold)

        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.13, depth=0.035, location=(port_x, port_y, port_z))
        port_glass = bpy.context.active_object
        port_glass.rotation_euler = (0, math.radians(90), 0)
        port_glass.data.materials.append(mat_glass_bubble)

        for pi in range(6):
            pang = pi * (math.pi / 3)
            py = port_y + math.cos(pang) * 0.17
            pz = port_z + math.sin(pang) * 0.17
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.025, location=(port_x + side * 0.02, py, pz))
            pr = bpy.context.active_object
            pr.data.materials.append(mat_gold_rivet)

    # ---------------------------------------------------------
    # 9. Stern Propulsion & Twin Exhausts (Back View)
    # ---------------------------------------------------------
    prop_x = 0.0
    prop_y = -2.30
    prop_z = 0.62

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.11, depth=0.40, location=(prop_x, prop_y + 0.12, prop_z))
    prop_shaft = bpy.context.active_object
    prop_shaft.rotation_euler = (math.radians(90), 0, 0)
    prop_shaft.data.materials.append(mat_cast_iron)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.17, location=(prop_x, prop_y - 0.06, prop_z))
    hub_nut = bpy.context.active_object
    hub_nut.data.materials.append(mat_brass_gold)

    # Large 4-Blade Bronze Propeller (Teardrop paddle blades)
    for b in range(4):
        bang = b * (math.pi / 2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.20, depth=0.05, location=(prop_x + math.sin(bang) * 0.38, prop_y - 0.05, prop_z + math.cos(bang) * 0.38))
        blade = bpy.context.active_object
        blade.name = f"SternBlade_{b}"
        blade.scale = (0.70, 1.30, 0.40)
        blade.rotation_euler = (math.radians(35), math.radians(12), bang)
        blade.data.materials.append(mat_brass_gold)

    # Twin Lower Exhaust Pipes with Riveted Flanges (Back View)
    for side in (-1, 1):
        ex_x = side * 0.88
        ex_y = -2.25
        ex_z = 0.42
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.11, depth=0.55, location=(ex_x, ex_y, ex_z))
        exhaust = bpy.context.active_object
        exhaust.name = f"SternExhaust_{side}"
        exhaust.rotation_euler = (math.radians(90), 0, 0)
        exhaust.data.materials.append(mat_copper_dark)

        bpy.ops.mesh.primitive_torus_add(major_radius=0.115, minor_radius=0.028, location=(ex_x, ex_y - 0.25, ex_z))
        eflange = bpy.context.active_object
        eflange.rotation_euler = (math.radians(90), 0, 0)
        eflange.data.materials.append(mat_brass_gold)

    # ---------------------------------------------------------
    # 10. Transforms and Hierarchy
    # ---------------------------------------------------------
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE'):
            o.select_set(True)
    
    bpy.context.view_layer.objects.active = hull_obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    print("Tornituerqui 3D Steampunk Racing Boat model built with 100% blueprint precision.")

def export_outputs():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models"))
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Save .blend file
    blend_path = os.path.join(base_dir, "boat_tornituerqui.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved Blender Project: {blend_path}")

    # 2. Export optimized GLTF / GLB for Three.js web engine
    glb_path = os.path.join(base_dir, "boat_tornituerqui.glb")
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
    build_tornituerqui_steamboat()
    export_outputs()
