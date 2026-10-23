import bpy
import math
import os

def render_preview():
    blend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models", "boat_tornituerqui.blend"))
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    for o in list(bpy.data.objects):
        if o.type in ('CAMERA', 'LIGHT'):
            bpy.data.objects.remove(o, do_unlink=True)

    # Key Sun Light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 8))
    sun = bpy.context.active_object
    sun.data.energy = 2.6
    sun.rotation_euler = (math.radians(48), math.radians(20), math.radians(40))

    # Fill Area Light
    bpy.ops.object.light_add(type='AREA', location=(-4, -3, 4))
    fill = bpy.context.active_object
    fill.data.energy = 70.0
    fill.data.size = 4.0
    fill.rotation_euler = (math.radians(55), 0, math.radians(-135))

    # World background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("StudioWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.86, 0.88, 0.92, 1.0)
        bg.inputs['Strength'].default_value = 0.75

    for o in bpy.data.objects:
        if o.type == 'EMPTY':
            o.hide_render = True

    scene = bpy.context.scene
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # 1. Isometric Camera
    bpy.ops.object.camera_add(location=(5.6, -5.6, 4.0))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(64), 0, math.radians(45))
    cam.data.lens = 45
    scene.camera = cam

    out_iso = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tornituerqui_iso.png"))
    scene.render.filepath = out_iso
    bpy.ops.render.render(write_still=True)

    # 2. Side View Camera
    cam.location = (7.5, 0.2, 1.4)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    cam.data.lens = 45
    out_side = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tornituerqui_side.png"))
    scene.render.filepath = out_side
    bpy.ops.render.render(write_still=True)

    # 3. Front View Camera
    cam.location = (0.0, 6.5, 1.4)
    cam.rotation_euler = (math.radians(90), 0, math.radians(180))
    cam.data.lens = 45
    out_front = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tornituerqui_front.png"))
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # 4. Rear View Camera
    cam.location = (0.0, -6.0, 2.5)
    cam.rotation_euler = (math.radians(75), 0, 0)
    cam.data.lens = 45
    out_rear = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_tornituerqui_rear.png"))
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    print("Tornituerqui preview renders completed successfully.")

if __name__ == "__main__":
    render_preview()
