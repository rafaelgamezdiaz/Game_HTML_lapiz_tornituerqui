import bpy
import math
import os

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def export_model(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported: {filepath}")

# ==========================================
# 1. VILLAGE HOUSE (Matching Image 2)
# ==========================================
def build_village_house():
    clear_scene()

    mat_plaster = create_material("PlasterWall", (0.96, 0.92, 0.82), roughness=0.7)
    mat_stone_base = create_material("StoneBase", (0.58, 0.58, 0.60), roughness=0.8)
    mat_timber = create_material("DarkTimber", (0.36, 0.22, 0.12), roughness=0.6)
    mat_tile_roof = create_material("TerracottaRoof", (0.82, 0.35, 0.22), roughness=0.55)
    mat_slate_roof = create_material("SlateRoof", (0.42, 0.46, 0.52), roughness=0.5)
    mat_door = create_material("WoodDoor", (0.48, 0.28, 0.16), roughness=0.6)
    mat_window = create_material("WindowGlass", (0.2, 0.4, 0.55), roughness=0.15, metallic=0.5)
    mat_chimney = create_material("ChimneyBrick", (0.68, 0.42, 0.35), roughness=0.7)

    # Stone Foundation Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.4))
    base = bpy.context.active_object
    base.name = "HouseFoundation"
    base.scale = (3.2, 2.6, 0.8)
    base.data.materials.append(mat_stone_base)

    # Main Stucco House Body (First & Second Floor)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.0))
    body = bpy.context.active_object
    body.name = "HouseBody"
    body.scale = (3.0, 2.4, 2.4)
    body.data.materials.append(mat_plaster)

    # Dark Timber corner vertical beams
    for sx in (-1, 1):
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx * 1.5, sy * 1.2, 2.0))
            beam = bpy.context.active_object
            beam.scale = (0.12, 0.12, 2.4)
            beam.data.materials.append(mat_timber)

    # Horizontal timber belt between floors
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.9))
    belt = bpy.context.active_object
    belt.scale = (3.04, 2.44, 0.12)
    belt.data.materials.append(mat_timber)

    # Steep Pitched Terracotta Roof (Prism / Gable)
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=2.3, depth=3.3, location=(0, 0, 4.2))
    roof = bpy.context.active_object
    roof.name = "HouseRoof"
    roof.rotation_euler = (0, math.radians(90), 0)
    roof.scale = (0.88, 1.45, 1.0)
    roof.data.materials.append(mat_tile_roof)

    # Overhanging roof trim
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=2.4, depth=3.45, location=(0, 0, 4.2))
    trim = bpy.context.active_object
    trim.rotation_euler = (0, math.radians(90), 0)
    trim.scale = (0.89, 1.46, 0.15)
    trim.data.materials.append(mat_timber)

    # Dormer Window on Roof (Buhardilla)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.65, -0.9, 4.0))
    dormer = bpy.context.active_object
    dormer.scale = (0.8, 0.9, 0.9)
    dormer.data.materials.append(mat_plaster)

    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.65, depth=1.0, location=(0.65, -0.9, 4.6))
    dormer_roof = bpy.context.active_object
    dormer_roof.rotation_euler = (0, math.radians(90), 0)
    dormer_roof.data.materials.append(mat_slate_roof)

    # Brick Chimney with Stone Cap
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.9, 0.4, 4.6))
    chimney = bpy.context.active_object
    chimney.scale = (0.55, 0.55, 1.8)
    chimney.data.materials.append(mat_chimney)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.9, 0.4, 5.55))
    chimney_cap = bpy.context.active_object
    chimney_cap.scale = (0.7, 0.7, 0.15)
    chimney_cap.data.materials.append(mat_stone_base)

    # Front Wooden Door
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.22, 1.2))
    door = bpy.context.active_object
    door.scale = (0.7, 0.08, 1.4)
    door.data.materials.append(mat_door)

    # Windows on First & Second Floors with Shutters & Flower Boxes
    mat_flowers = create_material("FlowerPetalsRed", (0.95, 0.22, 0.32), roughness=0.5)
    mat_flower_gold = create_material("FlowerPetalsGold", (0.98, 0.85, 0.15), roughness=0.5)
    mat_green_shutter = create_material("WoodShutter", (0.28, 0.48, 0.32), roughness=0.6)

    for wy in (1.3, 2.6):
        for wx in (-0.8, 0.8):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.21, wy))
            win = bpy.context.active_object
            win.scale = (0.5, 0.06, 0.6)
            win.data.materials.append(mat_window)

            # Timber window frame
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.22, wy))
            frame = bpy.context.active_object
            frame.scale = (0.58, 0.04, 0.68)
            frame.data.materials.append(mat_timber)

            # Window shutters on both sides
            for sx in (-0.38, 0.38):
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx + sx, -1.22, wy))
                shutter = bpy.context.active_object
                shutter.scale = (0.22, 0.03, 0.64)
                shutter.data.materials.append(mat_green_shutter)

            # Flower planter box under window
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.26, wy - 0.42))
            box = bpy.context.active_object
            box.scale = (0.62, 0.16, 0.16)
            box.data.materials.append(mat_timber)

            # Red & Gold Flowers in planter box
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.26, wy - 0.32))
            fl = bpy.context.active_object
            fl.scale = (0.58, 0.14, 0.1)
            fl.data.materials.append(mat_flowers if wx < 0 else mat_flower_gold)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 2. PARK BENCH (Banco de Madera y Hierro)
# ==========================================
def build_bench():
    clear_scene()
    mat_wood = create_material("BenchWood", (0.65, 0.40, 0.22), roughness=0.55)
    mat_iron = create_material("BenchIron", (0.15, 0.25, 0.20), roughness=0.4, metallic=0.8)

    # Cast Iron Legs
    for sx in (-0.75, 0.75):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.4))
        leg = bpy.context.active_object
        leg.scale = (0.08, 0.45, 0.8)
        leg.data.materials.append(mat_iron)

    # Wooden Seat Slats
    for sy in (-0.15, 0.0, 0.15):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sy, 0.48))
        slat = bpy.context.active_object
        slat.scale = (1.8, 0.12, 0.04)
        slat.data.materials.append(mat_wood)

    # Wooden Backrest Slats
    for sz in (0.7, 0.85):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22, sz))
        bslat = bpy.context.active_object
        bslat.scale = (1.8, 0.04, 0.12)
        bslat.data.materials.append(mat_wood)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = leg
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 3. WOODEN FENCE (Valla de Madera de Image 2)
# ==========================================
def build_fence():
    clear_scene()
    mat_fence = create_material("FenceWood", (0.78, 0.62, 0.42), roughness=0.7)

    # Vertical Fence Posts
    for sx in (-1.0, 0.0, 1.0):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.55))
        post = bpy.context.active_object
        post.scale = (0.12, 0.12, 1.1)
        post.data.materials.append(mat_fence)

        # Pointed top
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.08, depth=0.15, location=(sx, 0, 1.15))
        pt = bpy.context.active_object
        pt.rotation_euler = (0, 0, math.radians(45))
        pt.data.materials.append(mat_fence)

    # Horizontal Cross Rails
    for sz in (0.35, 0.8):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, sz))
        rail = bpy.context.active_object
        rail.scale = (2.1, 0.06, 0.08)
        rail.data.materials.append(mat_fence)

    # Vertical Palings
    for px in (-0.75, -0.5, -0.25, 0.25, 0.5, 0.75):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.02, 0.52))
        paling = bpy.context.active_object
        paling.scale = (0.08, 0.03, 0.95)
        paling.data.materials.append(mat_fence)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = post
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 4. FACETED DECIDUOUS TREE (Image 2)
# ==========================================
def build_tree():
    clear_scene()
    mat_trunk = create_material("TreeWood", (0.45, 0.28, 0.16), roughness=0.8)
    mat_leaves1 = create_material("LeafGreenWarm", (0.32, 0.68, 0.24), roughness=0.6)
    mat_leaves2 = create_material("LeafGreenDark", (0.22, 0.54, 0.20), roughness=0.65)
    mat_leaves3 = create_material("LeafGreenLime", (0.45, 0.78, 0.28), roughness=0.55)

    # Curved Trunk
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.28, depth=2.2, location=(0, 0, 1.1))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_trunk)

    # Low-poly faceted foliage spheres
    spheres = [
        ((0, 0, 2.5), 1.35, mat_leaves1),
        ((-0.4, 0.3, 3.1), 1.05, mat_leaves2),
        ((0.45, -0.25, 3.2), 1.15, mat_leaves3),
        ((0.1, 0.2, 3.8), 0.95, mat_leaves1)
    ]
    for pos, rad, mat in spheres:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rad, location=pos)
        f = bpy.context.active_object
        f.data.materials.append(mat)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 5. MOSSY RIVER ROCK (Obstacle)
# ==========================================
def build_rock():
    clear_scene()
    mat_rock = create_material("RiverStone", (0.55, 0.56, 0.60), roughness=0.7)
    mat_moss = create_material("GreenMoss", (0.28, 0.52, 0.22), roughness=0.85)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.9, location=(0, 0, 0.5))
    rock = bpy.context.active_object
    rock.scale = (1.25, 0.95, 0.75)
    rock.data.materials.append(mat_rock)

    # Top moss cap
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.6, location=(0.1, 0.05, 0.8))
    moss = bpy.context.active_object
    moss.scale = (1.0, 0.8, 0.4)
    moss.data.materials.append(mat_moss)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = rock
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 6. FLOODED STORM MANHOLE / DRAIN GRATE
# ==========================================
def build_manhole():
    clear_scene()
    mat_rim = create_material("IronRim", (0.42, 0.44, 0.46), roughness=0.45, metallic=0.75)
    mat_grate = create_material("GrateMetal", (0.16, 0.16, 0.18), roughness=0.4, metallic=0.9)

    # Outer round curb ring
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.85, depth=0.1, location=(0, 0, 0.05))
    rim = bpy.context.active_object
    rim.data.materials.append(mat_rim)

    # Inner circular metal slotted grate
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.74, depth=0.14, location=(0, 0, 0.07))
    grate = bpy.context.active_object
    grate.data.materials.append(mat_grate)

    # Grate cross slots
    for angle in (0, 45, 90, 135):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.15))
        bar = bpy.context.active_object
        bar.scale = (0.08, 1.35, 0.04)
        bar.rotation_euler = (0, 0, math.radians(angle))
        bar.data.materials.append(mat_rim)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = rim
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 7. STREET LAMP (Farola Victoriana)
# ==========================================
def build_lamp():
    clear_scene()
    mat_iron = create_material("LampIron", (0.16, 0.18, 0.20), roughness=0.35, metallic=0.85)
    mat_glow = create_material("LampGlow", (0.98, 0.94, 0.65), roughness=0.1)

    # Base & Fluted Pole
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.18, depth=0.4, location=(0, 0, 0.2))
    base = bpy.context.active_object
    base.data.materials.append(mat_iron)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.075, depth=2.8, location=(0, 0, 1.6))
    pole = bpy.context.active_object
    pole.data.materials.append(mat_iron)

    # Lantern housing
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.28, radius2=0.16, depth=0.5, location=(0, 0, 3.1))
    glass = bpy.context.active_object
    glass.data.materials.append(mat_glow)

    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.35, radius2=0.0, depth=0.3, location=(0, 0, 3.45))
    cap = bpy.context.active_object
    cap.data.materials.append(mat_iron)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = pole
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 8. VILLAGE HOUSE SLATE ROOF (Image 2 Variation)
# ==========================================
def build_slate_house():
    clear_scene()

    mat_plaster = create_material("PlasterCream", (0.94, 0.90, 0.85), roughness=0.7)
    mat_stone_base = create_material("StoneBaseDark", (0.50, 0.52, 0.55), roughness=0.8)
    mat_timber = create_material("DarkTimberSlate", (0.30, 0.20, 0.12), roughness=0.6)
    mat_slate_roof = create_material("SlateBlueRoof", (0.38, 0.44, 0.52), roughness=0.45)
    mat_door = create_material("WoodDoorDark", (0.42, 0.25, 0.15), roughness=0.6)
    mat_window = create_material("WindowGlassLit", (0.25, 0.5, 0.65), roughness=0.15, metallic=0.5)
    mat_flowers = create_material("FlowerPetals", (0.92, 0.25, 0.35), roughness=0.5)

    # Stone Foundation Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.4))
    base = bpy.context.active_object
    base.name = "HouseSlateFoundation"
    base.scale = (2.8, 3.2, 0.8)
    base.data.materials.append(mat_stone_base)

    # Main Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.1))
    body = bpy.context.active_object
    body.name = "HouseSlateBody"
    body.scale = (2.6, 3.0, 2.6)
    body.data.materials.append(mat_plaster)

    # Corner Quoins / Timbers
    for sx in (-1, 1):
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx * 1.3, sy * 1.5, 2.1))
            beam = bpy.context.active_object
            beam.scale = (0.14, 0.14, 2.6)
            beam.data.materials.append(mat_timber)

    # Steep Slate Roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=2.5, depth=3.3, location=(0, 0, 4.4))
    roof = bpy.context.active_object
    roof.rotation_euler = (math.radians(90), 0, 0)
    roof.scale = (1.1, 0.85, 1.0)
    roof.data.materials.append(mat_slate_roof)

    # Overhang trim
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=2.6, depth=3.45, location=(0, 0, 4.4))
    trim = bpy.context.active_object
    trim.rotation_euler = (math.radians(90), 0, 0)
    trim.scale = (1.12, 0.86, 0.12)
    trim.data.materials.append(mat_timber)

    # Front Door
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.32, 0, 1.2))
    door = bpy.context.active_object
    door.scale = (0.08, 0.8, 1.5)
    door.data.materials.append(mat_door)

    # Front Windows with Flower Boxes
    for wy in (-0.75, 0.75):
        for wz in (1.4, 2.8):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.31, wy, wz))
            win = bpy.context.active_object
            win.scale = (0.06, 0.55, 0.65)
            win.data.materials.append(mat_window)

            # Flower box under window
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.38, wy, wz - 0.4))
            box = bpy.context.active_object
            box.scale = (0.16, 0.6, 0.15)
            box.data.materials.append(mat_timber)

            # Flowers
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.38, wy, wz - 0.3))
            fl = bpy.context.active_object
            fl.scale = (0.14, 0.55, 0.1)
            fl.data.materials.append(mat_flowers)

    # Brick Chimney
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.6, 1.0, 4.8))
    chim = bpy.context.active_object
    chim.scale = (0.5, 0.5, 1.8)
    chim.data.materials.append(mat_stone_base)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 9. TUDOR VILLA HOUSE (Image 0 Central Feature)
# Rich ochre plaster, criss-cross timber framing & flower boxes
# ==========================================
def build_tudor_house():
    clear_scene()

    mat_plaster_ochre = create_material("PlasterOchre", (0.95, 0.82, 0.50), roughness=0.68)
    mat_stone_base = create_material("TudorStoneBase", (0.52, 0.54, 0.58), roughness=0.8)
    mat_dark_timber = create_material("TudorDarkTimber", (0.28, 0.16, 0.08), roughness=0.6)
    mat_terracotta = create_material("TudorTerracotta", (0.86, 0.38, 0.22), roughness=0.55)
    mat_window = create_material("TudorWindow", (0.2, 0.42, 0.60), roughness=0.15, metallic=0.4)
    mat_flowers = create_material("TudorFlowers", (0.95, 0.20, 0.35), roughness=0.5)
    mat_door = create_material("TudorDoor", (0.42, 0.22, 0.12), roughness=0.65)

    # Stone Foundation Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.45))
    base = bpy.context.active_object
    base.name = "TudorFoundation"
    base.scale = (3.4, 3.0, 0.9)
    base.data.materials.append(mat_stone_base)

    # Main Ochre Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.2))
    body = bpy.context.active_object
    body.name = "TudorBody"
    body.scale = (3.2, 2.8, 2.6)
    body.data.materials.append(mat_plaster_ochre)

    # Corner Vertical Beams
    for sx in (-1, 1):
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx * 1.6, sy * 1.4, 2.2))
            beam = bpy.context.active_object
            beam.scale = (0.14, 0.14, 2.6)
            beam.data.materials.append(mat_dark_timber)

    # Mid Horizontal Belt
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.1))
    belt = bpy.context.active_object
    belt.scale = (3.24, 2.84, 0.14)
    belt.data.materials.append(mat_dark_timber)

    # Steep Terracotta Gable Roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=2.6, depth=3.5, location=(0, 0, 4.5))
    roof = bpy.context.active_object
    roof.rotation_euler = (0, math.radians(90), 0)
    roof.scale = (0.88, 1.45, 1.0)
    roof.data.materials.append(mat_terracotta)

    # Roof Overhang Trim
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=2.7, depth=3.65, location=(0, 0, 4.5))
    rtrim = bpy.context.active_object
    rtrim.rotation_euler = (0, math.radians(90), 0)
    rtrim.scale = (0.89, 1.46, 0.15)
    rtrim.data.materials.append(mat_dark_timber)

    # Dormer Windows
    for dx in (-0.75, 0.75):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(dx, -1.1, 4.2))
        dorm = bpy.context.active_object
        dorm.scale = (0.65, 0.8, 0.85)
        dorm.data.materials.append(mat_plaster_ochre)

        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.55, depth=0.9, location=(dx, -1.1, 4.75))
        d_roof = bpy.context.active_object
        d_roof.rotation_euler = (0, math.radians(90), 0)
        d_roof.data.materials.append(mat_terracotta)

    # Brick Chimney
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.0, 0.5, 4.8))
    chim = bpy.context.active_object
    chim.scale = (0.6, 0.6, 2.0)
    chim.data.materials.append(mat_terracotta)

    # Windows with flower boxes on facade
    for wy in (1.4, 2.8):
        for wx in (-0.85, 0.85):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.41, wy))
            win = bpy.context.active_object
            win.scale = (0.55, 0.05, 0.65)
            win.data.materials.append(mat_window)

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.42, wy))
            frame = bpy.context.active_object
            frame.scale = (0.62, 0.04, 0.72)
            frame.data.materials.append(mat_dark_timber)

            # Planter box
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.46, wy - 0.45))
            pbox = bpy.context.active_object
            pbox.scale = (0.66, 0.16, 0.18)
            pbox.data.materials.append(mat_dark_timber)

            # Lush flowers
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.46, wy - 0.35))
            pfl = bpy.context.active_object
            pfl.scale = (0.62, 0.14, 0.12)
            pfl.data.materials.append(mat_flowers)

    # Front Door
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.42, 1.3))
    fdoor = bpy.context.active_object
    fdoor.scale = (0.8, 0.08, 1.5)
    fdoor.data.materials.append(mat_door)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ==========================================
# 10. STONE CANAL ARCH BRIDGE (Puente de Piedra)
# Spans over the flooded canal street
# ==========================================
def build_canal_bridge():
    clear_scene()

    mat_bridge_stone = create_material("BridgeStone", (0.62, 0.62, 0.65), roughness=0.75)
    mat_cobble = create_material("BridgeCobble", (0.45, 0.46, 0.48), roughness=0.85)
    mat_iron = create_material("RailingIron", (0.15, 0.18, 0.20), roughness=0.4, metallic=0.85)

    # Bridge Deck Span
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 6.2))
    deck = bpy.context.active_object
    deck.scale = (20.0, 4.8, 1.2)
    deck.data.materials.append(mat_bridge_stone)

    # Cobblestone pathway surface
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 6.85))
    path = bpy.context.active_object
    path.scale = (19.8, 4.4, 0.15)
    path.data.materials.append(mat_cobble)

    # Left & Right Stone Abutment Pillars
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 9.2, 0, 3.0))
        pillar = bpy.context.active_object
        pillar.scale = (3.2, 4.8, 6.2)
        pillar.data.materials.append(mat_bridge_stone)

    # Parapet / Railings on both sides
    for sy in (-2.2, 2.2):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sy, 7.5))
        parapet = bpy.context.active_object
        parapet.scale = (19.8, 0.25, 0.95)
        parapet.data.materials.append(mat_bridge_stone)

        # Iron decorative posts
        for px in (-8, -4, 0, 4, 8):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=1.2, location=(px, sy, 7.6))
            p = bpy.context.active_object
            p.data.materials.append(mat_iron)

    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = deck
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

if __name__ == '__main__':
    base_dir = r"e:\Kairos\lapiz_y_tornituerqui\assets\models"
    build_village_house()
    export_model(os.path.join(base_dir, "house_village.glb"))

    build_slate_house()
    export_model(os.path.join(base_dir, "house_slate.glb"))

    build_tudor_house()
    export_model(os.path.join(base_dir, "house_tudor.glb"))

    build_canal_bridge()
    export_model(os.path.join(base_dir, "bridge_arch.glb"))

    build_bench()
    export_model(os.path.join(base_dir, "prop_bench.glb"))

    build_fence()
    export_model(os.path.join(base_dir, "prop_fence.glb"))

    build_tree()
    export_model(os.path.join(base_dir, "tree_lowpoly.glb"))

    build_rock()
    export_model(os.path.join(base_dir, "obstacle_rock.glb"))

    build_manhole()
    export_model(os.path.join(base_dir, "obstacle_manhole.glb"))

    build_lamp()
    export_model(os.path.join(base_dir, "prop_lamp.glb"))
