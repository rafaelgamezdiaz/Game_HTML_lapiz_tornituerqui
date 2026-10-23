import bpy
import math
import os

def render_preview():
    blend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models", "boat_lapiz.blend"))
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    for o in list(bpy.data.objects):
        if o.type in ('CAMERA', 'LIGHT'):
            bpy.data.objects.remove(o, do_unlink=True)

    # Key Sun Light
    bpy.ops.object.light_add(type='SUN', location=(6, 4, 8))
    sun = bpy.context.active_object
    sun.data.energy = 3.2
    sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(45))

    # Fill Area Light
    bpy.ops.object.light_add(type='AREA', location=(-5, -4, 5))
    fill = bpy.context.active_object
    fill.data.energy = 95.0
    fill.data.size = 6.0
    fill.rotation_euler = (math.radians(50), 0, math.radians(-135))

    # Ground Bounce Warm Light
    bpy.ops.object.light_add(type='AREA', location=(0, 0, -2))
    bounce = bpy.context.active_object
    bounce.data.energy = 40.0
    bounce.data.size = 6.0
    bounce.rotation_euler = (math.radians(180), 0, 0)

    # World background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("StudioWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.88, 0.90, 0.93, 1.0)
        bg.inputs['Strength'].default_value = 0.45

    for o in bpy.data.objects:
        if o.type == 'EMPTY':
            o.hide_render = True

    scene = bpy.context.scene
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # 1. Isometric Perspective View (Matching blueprint bottom-right angle)
    # Looking from front-right (+X, +Y) back towards origin
    bpy.ops.object.camera_add(location=(5.2, 4.5, 3.4))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(64), 0, math.radians(130))
    cam.data.lens = 42
    scene.camera = cam

    out_iso = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_lapiz_iso.png"))
    scene.render.filepath = out_iso
    bpy.ops.render.render(write_still=True)

    # 2. Side View Camera (from +X looking along -X, Nose to the left if seen from right)
    cam.location = (7.2, -0.15, 1.1)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    cam.data.lens = 48
    out_side = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_lapiz_side.png"))
    scene.render.filepath = out_side
    bpy.ops.render.render(write_still=True)

    # 3. Front View Camera (from +Y looking along -Y directly into pencil point)
    cam.location = (0.0, 7.0, 1.1)
    cam.rotation_euler = (math.radians(90), 0, math.radians(180))
    cam.data.lens = 48
    out_front = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_lapiz_front.png"))
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # 4. Top View Camera (from +Z looking down)
    cam.location = (0.0, -0.15, 7.5)
    cam.rotation_euler = (0, 0, math.radians(-90))
    cam.data.lens = 48
    out_top = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_lapiz_top.png"))
    scene.render.filepath = out_top
    bpy.ops.render.render(write_still=True)

    # 5. Rear View Camera (from -Y looking at pink eraser and spoiler)
    cam.location = (0.0, -6.8, 1.6)
    cam.rotation_euler = (math.radians(85), 0, 0)
    cam.data.lens = 48
    out_rear = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "preview_lapiz_rear.png"))
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    print("Lapiz preview renders completed successfully.")

if __name__ == "__main__":
    render_preview()
