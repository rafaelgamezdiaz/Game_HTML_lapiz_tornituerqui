import bpy
import math
import os

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_material(name, color, roughness=0.4, metallic=0.0):
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

# ==============================================================================
# 1. BARCO TORNITUERQUI (Steampunk Racing Boat - Strict Blueprint)
# Proportions: Length 4.80, Width 3.10, Height 2.45
# Forward direction is +Y in Blender (+Z in GLTF)
# ==============================================================================
def build_tornituerqui_boat():
    import sys
    tools_dir = os.path.dirname(__file__)
    if tools_dir not in sys.path:
        sys.path.append(tools_dir)
    import build_tornituerqui_boat as btb
    btb.build_tornituerqui_steamboat()

# ==============================================================================
# 2. BARCO KAIROS (Toy Sailboat - Strict Blueprint from image_4.png / reference blueprint)
# Proportions: Length 4.9, Width 2.3, Mast Height 2.5
# Forward direction is +Y in Blender (+Z in GLTF)
# ==============================================================================
def build_kairos_boat():
    import sys
    tools_dir = os.path.dirname(__file__)
    if tools_dir not in sys.path:
        sys.path.append(tools_dir)
    import build_kairos_boat as bkb
    bkb.build_kairos_sailboat()


# ==============================================================================
# 3. BARCO LÁPIZ (Pencil Racing Boat - Strict Blueprint from image_5.png)
# Proportions: Length 5.3, Width 2.3, Height 2.6
# Forward direction is +Y in Blender (+Z in GLTF)
# ==============================================================================
def build_lapiz_boat():
    import sys
    tools_dir = os.path.dirname(__file__)
    if tools_dir not in sys.path:
        sys.path.append(tools_dir)
    import build_lapiz_boat as blb
    blb.build_lapiz_racing_boat()

if __name__ == '__main__':
    base_dir = r"e:\Kairos\lapiz_y_tornituerqui\assets\models"

    print("Re-generating Tornituerqui Boat...")
    build_tornituerqui_boat()
    export_model(os.path.join(base_dir, "boat_tornituerqui.glb"))

    print("Re-generating Kairos Boat...")
    build_kairos_boat()
    export_model(os.path.join(base_dir, "boat_kairos.glb"))

    print("Re-generating Lápiz Boat...")
    build_lapiz_boat()
    export_model(os.path.join(base_dir, "boat_lapiz.glb"))
