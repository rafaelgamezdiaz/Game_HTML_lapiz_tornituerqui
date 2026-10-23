import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import os

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, base_color, roughness=0.35, metallic=0.0, alpha=1.0, transmission=0.0):
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
        if 'Alpha' in bsdf.inputs and alpha < 1.0:
            bsdf.inputs['Alpha'].default_value = alpha
            mat.blend_method = 'BLEND'
        if 'Transmission Weight' in bsdf.inputs and transmission > 0.0:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs and transmission > 0.0:
            bsdf.inputs['Transmission'].default_value = transmission
    return mat

def create_textured_material(name, image_path, roughness=0.35, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')

    if os.path.exists(image_path):
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = bpy.data.images.load(image_path)
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        if 'Alpha' in tex_node.outputs and 'Alpha' in bsdf.inputs:
            links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
            mat.blend_method = 'CLIP'
    if bsdf:
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
        ("Ref_Front",  (0, 4.0, 1.3),  (math.radians(90), 0, math.radians(180)), 4.8),
        ("Ref_Side",   (4.0, 0, 1.3),  (math.radians(90), 0, math.radians(-90)), 4.8),
        ("Ref_Back",   (0, -4.0, 1.3), (math.radians(90), 0, 0),                 4.8),
        ("Ref_Top",    (0, 0, 4.5),    (0, 0, math.radians(-90)),                4.8),
        ("Ref_Bottom", (0, 0, -3.2),   (math.radians(180), 0, math.radians(-90)), 4.8),
    ]
    for name, loc, rot, size in refs:
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = 'IMAGE'
        empty.data = img
        empty.location = loc
        empty.rotation_euler = rot
        empty.empty_display_size = size
        bpy.context.collection.objects.link(empty)

def join_objects_into(target_obj, other_objs):
    if not other_objs:
        return target_obj
    bpy.ops.object.select_all(action='DESELECT')
    for o in other_objs:
        if o and o != target_obj:
            o.select_set(True)
    target_obj.select_set(True)
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.join()
    return target_obj

def build_lapiz_racing_boat():
    clear_scene()

    textures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "textures"))
    ref_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "lapiz_reference.jpg"))
    setup_reference_images(ref_path)

    # ---------------------------------------------------------
    # 1. PBR Materials Palette (Matching Blueprint Aesthetics)
    # ---------------------------------------------------------
    mat_pencil_yellow = create_pbr_material("Mat_PencilYellow", (0.95, 0.64, 0.12), roughness=0.28, metallic=0.0)
    mat_cedar_wood    = create_pbr_material("Mat_CedarWood",    (0.93, 0.82, 0.66), roughness=0.60, metallic=0.0)
    mat_graphite      = create_pbr_material("Mat_GraphiteDark", (0.12, 0.13, 0.15), roughness=0.22, metallic=0.60)
    mat_ferrule       = create_pbr_material("Mat_FerruleBrass", (0.82, 0.68, 0.44), roughness=0.20, metallic=0.90)
    mat_eraser        = create_pbr_material("Mat_PinkEraser",   (0.84, 0.28, 0.44), roughness=0.60, metallic=0.0)
    mat_spoiler_pink  = create_pbr_material("Mat_SpoilerPink",  (0.88, 0.25, 0.42), roughness=0.18, metallic=0.05)
    mat_spoiler_strut = create_pbr_material("Mat_SpoilerStrut", (0.70, 0.16, 0.28), roughness=0.25, metallic=0.35)
    mat_windshield    = create_pbr_material("Mat_Windshield",   (0.24, 0.58, 0.82), roughness=0.08, metallic=0.10, alpha=0.50, transmission=0.82)
    mat_windshield_frame = create_pbr_material("Mat_WindshieldFrame", (0.84, 0.86, 0.90), roughness=0.18, metallic=0.92)
    mat_cockpit_tub   = create_pbr_material("Mat_CockpitTub",   (0.18, 0.12, 0.08), roughness=0.75, metallic=0.0)
    mat_leather_seat  = create_pbr_material("Mat_BrownLeather", (0.36, 0.17, 0.07), roughness=0.50, metallic=0.0)
    mat_steering_wheel= create_pbr_material("Mat_SteeringWheel",(0.10, 0.11, 0.12), roughness=0.30, metallic=0.55)

    cal_tex_path = os.path.join(textures_dir, "decal_calendar_2.png")
    rnd_tex_path = os.path.join(textures_dir, "decal_roundel_2.png")
    mat_decal_cal = create_textured_material("Mat_DecalCalendar", cal_tex_path, roughness=0.25)
    mat_decal_rnd = create_textured_material("Mat_DecalRoundel", rnd_tex_path, roughness=0.25)

    # ---------------------------------------------------------
    # 2. Hull_Pencil (Hexagonal Fuselage with Scalloped Nose)
    # Fuselage Radius R = 0.82, Central axis at Z = 0.90
    # Length: Y = -1.25 to Y = +2.45
    # Cockpit cutout: Y = +0.02 to Y = -0.92
    # ---------------------------------------------------------
    R_hex = 0.82
    cz = 0.90

    # 12-gon beveled hexagon vertices
    def get_beveled_hex_points(scale=1.0, y=0.0, y_offset_array=None):
        r = R_hex * scale
        corners = []
        for a in [90, 30, -30, -90, -150, 150]:
            rad = math.radians(a)
            corners.append(Vector((r * math.cos(rad), cz + r * math.sin(rad))))

        pts = []
        bevel_ratio = 0.10
        for i in range(6):
            c_curr = corners[i]
            c_prev = corners[(i - 1) % 6]
            c_next = corners[(i + 1) % 6]
            p1 = c_curr + (c_prev - c_curr) * bevel_ratio
            p2 = c_curr + (c_next - c_curr) * bevel_ratio
            y1 = y + (y_offset_array[2 * i] if y_offset_array else 0.0)
            y2 = y + (y_offset_array[2 * i + 1] if y_offset_array else 0.0)
            pts.append((p1.x, y1, p1.y))
            pts.append((p2.x, y2, p2.y))
        return pts

    hull_mesh = bpy.data.meshes.new("HullPencilMesh")
    hull_obj = bpy.data.objects.new("Hull_Pencil", hull_mesh)
    bpy.context.collection.objects.link(hull_obj)

    hull_obj.data.materials.append(mat_pencil_yellow) # 0: Yellow lacquer
    hull_obj.data.materials.append(mat_cedar_wood)    # 1: Cedar wood cone
    hull_obj.data.materials.append(mat_cockpit_tub)   # 2: Cockpit interior tub

    bm = bmesh.new()

    # Straight fuselage stations
    fuselage_y = [-1.25, -1.05, -0.92, -0.65, -0.35, 0.02, 0.25, 0.45]
    rings = []
    for y in fuselage_y:
        pts = get_beveled_hex_points(scale=1.0, y=y)
        ring_v = [bm.verts.new(p) for p in pts]
        rings.append(ring_v)

    # The Scalloped Carve: The 6 flat facets extend further forward (+Y)
    # than the 6 corner ridges!
    # Corner ridges begin cut at Y = 0.55; facet centers extend to Y = 0.95.
    scallop_offsets = [
        0.00, 0.35, # Corner 0 (Top) -> Facet 0
        0.35, 0.00, # Facet 0 -> Corner 1 (Top-Right)
        0.00, 0.35, # Corner 1 -> Facet 1 (Right)
        0.35, 0.00, # Facet 1 -> Corner 2 (Bottom-Right)
        0.00, 0.35, # Corner 2 -> Facet 2 (Bottom)
        0.35, 0.00, # Facet 2 -> Corner 3 (Bottom-Left)
    ]
    # Ring A: Base of scallop (Yellow lacquer side)
    scallop_ring_pts = get_beveled_hex_points(scale=1.0, y=0.55, y_offset_array=scallop_offsets)
    scallop_ring_v = [bm.verts.new(p) for p in scallop_ring_pts]
    rings.append(scallop_ring_v)

    # Shaved Cedar Wood Cone Stations (Y = 1.05 to Y = 1.90)
    cone_stations = [1.10, 1.30, 1.52, 1.72, 1.90]
    for yc in cone_stations:
        t = (yc - 1.05) / (1.90 - 1.05) # 0 to 1
        rc = R_hex * 0.92 * (1.0 - t) + 0.26 * t
        pts = get_beveled_hex_points(scale=(rc / R_hex), y=yc)
        ring_v = [bm.verts.new(p) for p in pts]
        rings.append(ring_v)

    # Skin all rings
    scallop_ring_index = len(fuselage_y) # Index of scallop boundary
    for i in range(len(rings) - 1):
        rA = rings[i]
        rB = rings[i + 1]
        mat_i = 1 if i >= scallop_ring_index else 0
        for j in range(12):
            jn = (j + 1) % 12
            f = bm.faces.new([rA[j], rA[jn], rB[jn], rB[j]])
            f.material_index = mat_i

    # Watertight caps
    bm.faces.new(reversed(rings[0]))
    f_cone_tip = bm.faces.new(rings[-1])
    f_cone_tip.material_index = 1

    bm.to_mesh(hull_mesh)
    bm.free()

    # Carve cockpit tub with Boolean Cutter
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.48, depth=0.96, location=(0.0, -0.45, cz + 0.55))
    cutter = bpy.context.active_object
    cutter.rotation_euler = (math.radians(90), 0, 0)
    cutter.scale = (1.0, 0.85, 1.0)

    bool_mod = hull_obj.modifiers.new(name="CockpitCarve", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    bool_mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = hull_obj
    bpy.ops.object.modifier_apply(modifier="CockpitCarve")

    bpy.data.objects.remove(cutter, do_unlink=True)

    # Bottom Keel Fin (Centerline stabilizer at X = 0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.05, cz - R_hex - 0.04))
    keel_fin = bpy.context.active_object
    keel_fin.name = "Hull_KeelFin"
    keel_fin.scale = (0.05, 0.42, 0.09)
    keel_fin.data.materials.append(mat_cedar_wood)

    join_objects_into(hull_obj, [keel_fin])

    # ---------------------------------------------------------
    # 3. Graphite_Tip (Dark pencil lead cone at proa)
    # From Y = 1.90 (R = 0.26) to Y = 2.45 (R = 0.0)
    # ---------------------------------------------------------
    tip_mesh = bpy.data.meshes.new("GraphiteTipMesh")
    tip_obj = bpy.data.objects.new("Graphite_Tip", tip_mesh)
    bpy.context.collection.objects.link(tip_obj)
    tip_obj.data.materials.append(mat_graphite)

    bm_tip = bmesh.new()
    apex = bm_tip.verts.new((0.0, 2.45, cz))
    base_v = []
    seg = 16
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        base_v.append(bm_tip.verts.new((0.26 * math.cos(a), 1.90, cz + 0.26 * math.sin(a))))
    mid_v = []
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        mid_v.append(bm_tip.verts.new((0.14 * math.cos(a), 2.18, cz + 0.14 * math.sin(a))))

    for i in range(seg):
        nxt = (i + 1) % seg
        bm_tip.faces.new([base_v[i], base_v[nxt], mid_v[nxt], mid_v[i]])
        bm_tip.faces.new([mid_v[i], mid_v[nxt], apex])
    bm_tip.faces.new(reversed(base_v))

    bm_tip.to_mesh(tip_mesh)
    bm_tip.free()

    # ---------------------------------------------------------
    # 4. Cockpit_Seat_Wheel (Windshield, Seat, Wheel, Decals)
    # ---------------------------------------------------------
    cockpit_mesh = bpy.data.meshes.new("CockpitMesh")
    cockpit_obj = bpy.data.objects.new("Cockpit_Seat_Wheel", cockpit_mesh)
    bpy.context.collection.objects.link(cockpit_obj)
    cockpit_obj.data.materials.append(mat_cockpit_tub)
    cockpit_obj.data.materials.append(mat_windshield)
    cockpit_obj.data.materials.append(mat_windshield_frame)
    cockpit_obj.data.materials.append(mat_leather_seat)
    cockpit_obj.data.materials.append(mat_steering_wheel)

    # Windshield Aero Deflector
    bm_ws = bmesh.new()
    ws_layers = []
    for r_i in range(5):
        tilt_y = 0.02 - r_i * 0.07
        lift_z = cz + 0.58 + r_i * 0.11
        rx = 0.44 * (1.0 - r_i * 0.16)
        rz = 0.30 * (1.0 - r_i * 0.16)
        layer = []
        for s in range(11):
            ang = math.pi * s / 10.0
            x = rx * math.cos(ang)
            z = lift_z + rz * math.sin(ang)
            y = tilt_y - 0.06 * math.sin(ang)
            layer.append(bm_ws.verts.new((x, y, z)))
        ws_layers.append(layer)

    for i in range(len(ws_layers) - 1):
        for j in range(10):
            f = bm_ws.faces.new([ws_layers[i][j], ws_layers[i][j + 1], ws_layers[i + 1][j + 1], ws_layers[i + 1][j]])
            f.material_index = 1 # Mat_Windshield

    # Windshield Frame
    for j in range(10):
        v0 = ws_layers[0][j]
        v1 = ws_layers[0][j + 1]
        v_ext0 = bm_ws.verts.new((v0.co.x, v0.co.y - 0.03, v0.co.z - 0.03))
        v_ext1 = bm_ws.verts.new((v1.co.x, v1.co.y - 0.03, v1.co.z - 0.03))
        f_fr = bm_ws.faces.new([v0, v1, v_ext1, v_ext0])
        f_fr.material_index = 2 # Mat_WindshieldFrame

    bm_ws.to_mesh(cockpit_mesh)
    bm_ws.free()

    cockpit_parts = []

    # Racing Bucket Seat
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.66, cz + 0.62))
    backrest = bpy.context.active_object
    backrest.scale = (0.36, 0.10, 0.38)
    backrest.rotation_euler = (math.radians(-12), 0, 0)
    backrest.data.materials.append(mat_leather_seat)
    cockpit_parts.append(backrest)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.50, cz + 0.42))
    cushion = bpy.context.active_object
    cushion.scale = (0.36, 0.26, 0.12)
    cushion.data.materials.append(mat_leather_seat)
    cockpit_parts.append(cushion)

    # Vertical Cushion Ribs
    for rib_x in (-0.11, 0.0, 0.11):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.36, location=(rib_x, -0.65, cz + 0.63))
        rib = bpy.context.active_object
        rib.rotation_euler = (math.radians(-12), 0, 0)
        rib.data.materials.append(mat_leather_seat)
        cockpit_parts.append(rib)

    # Sports Steering Wheel & Column
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.32, location=(0.0, -0.30, cz + 0.60))
    col = bpy.context.active_object
    col.rotation_euler = (math.radians(38), 0, 0)
    col.data.materials.append(mat_steering_wheel)
    cockpit_parts.append(col)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.022, location=(0.0, -0.20, cz + 0.73))
    wheel = bpy.context.active_object
    wheel.rotation_euler = (math.radians(38), 0, 0)
    wheel.data.materials.append(mat_steering_wheel)
    cockpit_parts.append(wheel)

    for a in (0, 120, 240):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.16, location=(0.0, -0.20, cz + 0.73))
        spoke = bpy.context.active_object
        spoke.rotation_euler = (math.radians(38), 0, math.radians(a))
        spoke.data.materials.append(mat_steering_wheel)
        cockpit_parts.append(spoke)

    # Side Calendar "#2" Decal Planes (UPRIGHT with red bar at top)
    side_dist = R_hex * math.sqrt(3.0) / 2.0 + 0.012
    for side in (-1, 1):
        sx = side * side_dist
        bpy.ops.mesh.primitive_plane_add(size=0.36, location=(sx, -0.78, cz + 0.10))
        decal_p = bpy.context.active_object
        # Make local Y point to world +Z and local normal point outward
        decal_p.rotation_euler = (math.radians(90), 0, math.radians(-90 if side > 0 else 90))
        decal_p.data.materials.append(mat_decal_cal)
        cockpit_parts.append(decal_p)

    join_objects_into(cockpit_obj, cockpit_parts)

    # ---------------------------------------------------------
    # 5. Fins_L_R (Hydrofoil Stabilizer Wings)
    # Wingspan: 2.30 (from X = -1.15 to +1.15)
    # ---------------------------------------------------------
    fin_mesh = bpy.data.meshes.new("HydrofoilMesh")
    fin_obj = bpy.data.objects.new("Fins_L_R", fin_mesh)
    bpy.context.collection.objects.link(fin_obj)
    fin_obj.data.materials.append(mat_cedar_wood)

    bm_f = bmesh.new()
    for side in (-1, 1):
        xr = side * 0.70
        xt = side * 1.15
        cr = [
            (xr, -0.48, cz - 0.20),
            (xr, -0.72, cz - 0.16),
            (xr, -0.96, cz - 0.22),
            (xr, -0.72, cz - 0.24),
        ]
        ct = [
            (xt, -0.58, cz - 0.21),
            (xt, -0.76, cz - 0.19),
            (xt, -0.92, cz - 0.22),
            (xt, -0.76, cz - 0.23),
        ]
        vr = [bm_f.verts.new(p) for p in cr]
        vt = [bm_f.verts.new(p) for p in ct]
        bm_f.faces.new([vr[0], vr[1], vt[1], vt[0]])
        bm_f.faces.new([vr[1], vr[2], vt[2], vt[1]])
        bm_f.faces.new([vr[2], vr[3], vt[3], vt[2]])
        bm_f.faces.new([vr[3], vr[0], vt[0], vt[3]])
        bm_f.faces.new([vt[0], vt[1], vt[2], vt[3]] if side > 0 else [vt[3], vt[2], vt[1], vt[0]])

    bm_f.to_mesh(fin_mesh)
    bm_f.free()

    fin_parts = []
    for side in (-1, 1):
        fx = side * 0.94
        bpy.ops.mesh.primitive_plane_add(size=0.22, location=(fx, -0.74, cz - 0.155))
        rnd_plane = bpy.context.active_object
        rnd_plane.rotation_euler = (0, 0, math.radians(90))
        rnd_plane.data.materials.append(mat_decal_rnd)
        fin_parts.append(rnd_plane)

    join_objects_into(fin_obj, fin_parts)

    # ---------------------------------------------------------
    # 6. Ferrule_Eraser (Brass Collar with 3 Crimps + Pink Eraser Stern)
    # Ferrule: Y = -1.25 to Y = -1.85 (length 0.60, R = 0.84)
    # Eraser:  Y = -1.85 to Y = -2.85 (length 1.00, R = 0.82)
    # ---------------------------------------------------------
    ferrule_mesh = bpy.data.meshes.new("FerruleMesh")
    ferrule_obj = bpy.data.objects.new("Ferrule_Eraser", ferrule_mesh)
    bpy.context.collection.objects.link(ferrule_obj)
    ferrule_obj.data.materials.append(mat_ferrule)
    ferrule_obj.data.materials.append(mat_eraser)

    bm_fe = bmesh.new()
    num_f_seg = 24
    crimp_ys = [-1.35, -1.55, -1.75]
    f_rings = []
    fer_station_ys = [-1.25, -1.31, -1.35, -1.39, -1.48, -1.52, -1.55, -1.58, -1.68, -1.72, -1.75, -1.78, -1.85]
    for yf in fer_station_ys:
        is_crimp = any(abs(yf - cy) < 0.03 for cy in crimp_ys)
        rf = 0.86 if is_crimp else 0.835
        r_v = []
        for i in range(num_f_seg):
            ang = 2.0 * math.pi * i / num_f_seg
            x = rf * math.cos(ang)
            z = cz + rf * math.sin(ang)
            r_v.append(bm_fe.verts.new((x, yf, z)))
        f_rings.append(r_v)

    for i in range(len(f_rings) - 1):
        for j in range(num_f_seg):
            nxt = (j + 1) % num_f_seg
            f = bm_fe.faces.new([f_rings[i][j], f_rings[i][nxt], f_rings[i + 1][nxt], f_rings[i + 1][j]])
            f.material_index = 0 # Mat_FerruleBrass

    # Pink Eraser Cylinder & Dome Cap
    er_rings = []
    er_stations = [
        (-1.85, 0.82),
        (-2.15, 0.82),
        (-2.45, 0.82),
        (-2.60, 0.80),
        (-2.72, 0.72),
        (-2.81, 0.54),
        (-2.85, 0.28),
    ]
    for ye, re in er_stations:
        r_v = []
        for i in range(num_f_seg):
            ang = 2.0 * math.pi * i / num_f_seg
            x = re * math.cos(ang)
            z = cz + re * math.sin(ang)
            r_v.append(bm_fe.verts.new((x, ye, z)))
        er_rings.append(r_v)

    for i in range(len(er_rings) - 1):
        for j in range(num_f_seg):
            nxt = (j + 1) % num_f_seg
            f = bm_fe.faces.new([er_rings[i][j], er_rings[i][nxt], er_rings[i + 1][nxt], er_rings[i + 1][j]])
            f.material_index = 1 # Mat_PinkEraser

    f_cap = bm_fe.faces.new(er_rings[-1])
    f_cap.material_index = 1

    bm_fe.to_mesh(ferrule_mesh)
    bm_fe.free()

    # ---------------------------------------------------------
    # 7. Rear_Spoiler (Racing Aerofoil Wing & Twin Tubular Struts)
    # Total Height: 2.58 (from base Z = 0 to top Z = 2.58 ~ 26")
    # ---------------------------------------------------------
    spoiler_mesh = bpy.data.meshes.new("SpoilerMesh")
    spoiler_obj = bpy.data.objects.new("Rear_Spoiler", spoiler_mesh)
    bpy.context.collection.objects.link(spoiler_obj)
    spoiler_obj.data.materials.append(mat_spoiler_pink)
    spoiler_obj.data.materials.append(mat_spoiler_strut)

    spoiler_parts = []
    for side in (-1, 1):
        sx = side * 0.42
        p_start = Vector((sx, -1.50, cz + 0.82))
        p_end   = Vector((sx, -1.75, 2.34))
        mid_p   = (p_start + p_end) * 0.5
        v_diff  = p_end - p_start
        length  = v_diff.length

        bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=length, location=mid_p)
        strut = bpy.context.active_object
        rot_axis = Vector((0, 0, 1)).cross(v_diff.normalized())
        rot_angle = math.acos(Vector((0, 0, 1)).dot(v_diff.normalized()))
        strut.rotation_mode = 'AXIS_ANGLE'
        strut.rotation_axis_angle = (rot_angle, rot_axis.x, rot_axis.y, rot_axis.z)
        strut.data.materials.append(mat_spoiler_strut)
        spoiler_parts.append(strut)

        # Base collar clamp
        bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.08, location=p_start)
        clamp = bpy.context.active_object
        clamp.data.materials.append(mat_spoiler_strut)
        spoiler_parts.append(clamp)

        # Top cylindrical mount
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.12, location=p_end)
        top_c = bpy.context.active_object
        top_c.rotation_euler = (math.radians(90), 0, 0)
        top_c.data.materials.append(mat_spoiler_strut)
        spoiler_parts.append(top_c)

    # Crossbar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.88, location=(0.0, -1.75, 2.34))
    crossbar = bpy.context.active_object
    crossbar.rotation_euler = (0, math.radians(90), 0)
    crossbar.data.materials.append(mat_spoiler_strut)
    spoiler_parts.append(crossbar)

    # Curved Aerodynamic Racing Wing Blade
    bm_sp = bmesh.new()
    span_xs = [-0.78, -0.62, -0.42, -0.18, 0.0, 0.18, 0.42, 0.62, 0.78]
    chord_pts = [
        (-1.60, 2.46), # Leading edge
        (-1.76, 2.54), # Crest (Z = 2.54)
        (-1.98, 2.48), # Trailing edge
        (-1.76, 2.42), # Lower suction surface
    ]

    sp_rings = []
    for x in span_xs:
        tip_lift = 0.035 * (abs(x) / 0.78) ** 2
        r_v = []
        for y, z in chord_pts:
            r_v.append(bm_sp.verts.new((x, y, z + tip_lift)))
        sp_rings.append(r_v)

    for i in range(len(sp_rings) - 1):
        for j in range(4):
            nxt = (j + 1) % 4
            f = bm_sp.faces.new([sp_rings[i][j], sp_rings[i][nxt], sp_rings[i + 1][nxt], sp_rings[i + 1][j]])
            f.material_index = 0

    for side in (-1, 1):
        edge_ring = sp_rings[0] if side < 0 else sp_rings[-1]
        f_end = bm_sp.faces.new(edge_ring if side > 0 else reversed(edge_ring))
        f_end.material_index = 0

    bm_sp.to_mesh(spoiler_mesh)
    bm_sp.free()

    join_objects_into(spoiler_obj, spoiler_parts)

    # Smooth Shading on all curved components
    final_objs = [hull_obj, tip_obj, cockpit_obj, fin_obj, ferrule_obj, spoiler_obj]
    for obj in final_objs:
        for poly in obj.data.polygons:
            poly.use_smooth = True

    print(f"Boat generation complete with {len(final_objs)} hierarchy objects.")

if __name__ == "__main__":
    build_lapiz_racing_boat()

    blend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models", "boat_lapiz.blend"))
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved: {blend_path}")

    glb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models", "boat_lapiz.glb"))
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported: {glb_path}")
