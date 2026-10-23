import bpy
import math
import os

def render_preview():
    blend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models", "house_tudor.blend"))
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    for o in list(bpy.data.objects):
        if o.type in ('CAMERA', 'LIGHT'):
            bpy.data.objects.remove(o, do_unlink=True)

    # 1. Warm Sun Light
    bpy.ops.object.light_add(type='SUN', location=(10, -12, 16))
    sun = bpy.context.active_object
    sun.data.energy = 2.4
    sun.rotation_euler = (math.radians(52), math.radians(15), math.radians(-35))

    # 2. Ambient Sky Fill Light
    bpy.ops.object.light_add(type='AREA', location=(-8, -4, 10))
    fill = bpy.context.active_object
    fill.data.energy = 55.0
    fill.data.size = 12.0
    fill.rotation_euler = (math.radians(55), 0, math.radians(65))

    # 3. Soft Rim Light from Back
    bpy.ops.object.light_add(type='AREA', location=(6, 10, 8))
    rim = bpy.context.active_object
    rim.data.energy = 45.0
    rim.data.size = 8.0
    rim.rotation_euler = (math.radians(65), 0, math.radians(-160))

    # World background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("StudioWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.90, 0.92, 0.95, 1.0)
        bg.inputs['Strength'].default_value = 0.55

    for o in bpy.data.objects:
        if o.type == 'EMPTY':
            o.hide_render = True

    scene = bpy.context.scene
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # 1. Isometric Camera (Framing cottage with front balcony and spiral stair)
    bpy.ops.object.camera_add(location=(11.5, -11.5, 9.8))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(60), 0, math.radians(45))
    cam.data.lens = 40
    scene.camera = cam

    out_iso = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tudor_house_iso.png"))
    scene.render.filepath = out_iso
    bpy.ops.render.render(write_still=True)

    # 2. Front View Camera (Directly facing front balcony and entrance)
    cam.location = (0.0, -12.5, 2.9)
    cam.rotation_euler = (math.radians(90), 0, 0)
    cam.data.lens = 42
    out_front = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tudor_house_front.png"))
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # 3. Side View Camera (Looking at right spiral staircase facade)
    cam.location = (12.5, 0.0, 2.9)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    cam.data.lens = 42
    out_side = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tudor_house_side.png"))
    scene.render.filepath = out_side
    bpy.ops.render.render(write_still=True)

    # 4. Rear View Camera (Looking at back facade)
    cam.location = (0.0, 12.5, 2.9)
    cam.rotation_euler = (math.radians(90), 0, math.radians(180))
    cam.data.lens = 42
    out_rear = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tudor_house_rear.png"))
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # 5. Top View Camera (Ortho bird's eye view)
    cam.location = (0.0, -0.1, 14.5)
    cam.rotation_euler = (0, 0, math.radians(-90))
    cam.data.lens = 38
    out_top = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tudor_house_top.png"))
    scene.render.filepath = out_top
    bpy.ops.render.render(write_still=True)

    print("Tudor House multi-angle preview renders generated successfully.")

if __name__ == "__main__":
    render_preview()
