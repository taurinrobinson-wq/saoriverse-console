#!/usr/bin/env python3
"""
Headless Blender render helper.

Usage (run from a shell where `blender` is available):

blender --background --python tools/blender_render.py -- \
  --input velinor/assets/brickhouse-entrance_velinorian.obj \
  --output renders/brickhouse-entrance.png \
  --resolution 2048 2048 --engine EEVEE --samples 64

This script imports an OBJ (or uses JSON fallback), frames a camera on the model,
adds a light, ensures materials have visible base colors (fallback mapping),
and renders a PNG.
"""
import sys
import os
import argparse
from mathutils import Vector

# Blender imports
import bpy


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Headless Blender renderer for Velinorian OBJ/JSON")
    parser.add_argument("--input", required=True, help="Input OBJ or JSON file path")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--resolution", nargs=2, type=int, default=[1024,1024], help="Resolution: width height")
    parser.add_argument("--engine", choices=["EEVEE","CYCLES"], default="EEVEE")
    parser.add_argument("--samples", type=int, default=64, help="Render samples (EEVEE/CYCLES)")
    parser.add_argument("--transparent", action="store_true", help="Render with transparent background")
    return parser.parse_args(argv)


def clear_scene():
    # Remove all objects, materials, meshes, cameras, lights
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_obj(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    bpy.ops.import_scene.obj(filepath=path)


def bounds_of_objects(objs):
    mins = Vector((1e9,1e9,1e9))
    maxs = Vector((-1e9,-1e9,-1e9))
    for obj in objs:
        if obj.type != 'MESH':
            continue
        for v in obj.bound_box:
            co_world = obj.matrix_world @ Vector(v)
            mins.x = min(mins.x, co_world.x)
            mins.y = min(mins.y, co_world.y)
            mins.z = min(mins.z, co_world.z)
            maxs.x = max(maxs.x, co_world.x)
            maxs.y = max(maxs.y, co_world.y)
            maxs.z = max(maxs.z, co_world.z)
    return mins, maxs


def look_at(obj_camera, target_point):
    direction = target_point - obj_camera.location
    # Point the -Z axis to the target, Y up
    obj_camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def ensure_material_colors(fallback_map=None):
    # If materials have no obvious color, set Principled BSDF base color or diffuse_color
    fallback_map = fallback_map or {
        'brick': (180/255.0,100/255.0,60/255.0,1.0),
        'wood': (60/255.0,40/255.0,20/255.0,1.0),
        'glass': (100/255.0,150/255.0,180/255.0,1.0),
        'roof': (51/255.0,51/255.0,51/255.0,1.0),
        'moss': (100/255.0,120/255.0,100/255.0,1.0),
    }
    for mat in bpy.data.materials:
        color_set = False
        # Try node-based Principled BSDF
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    col = node.inputs.get('Base Color')
                    if col and hasattr(col, 'default_value'):
                        # If color is gray default, replace with fallback guess.
                        if tuple(col.default_value[:3]) == (0.8,0.8,0.8) or tuple(col.default_value[:3]) == (0.0,0.0,0.0):
                            # pick fallback by name
                            lname = mat.name.lower()
                            for k,v in fallback_map.items():
                                if k in lname:
                                    col.default_value = v
                                    color_set = True
                                    break
                        else:
                            color_set = True
                    break
        else:
            # Non-node material: check diffuse_color
            try:
                if hasattr(mat, 'diffuse_color'):
                    if tuple(mat.diffuse_color[:3]) == (0.8,0.8,0.8) or tuple(mat.diffuse_color[:3]) == (0.0,0.0,0.0):
                        lname = mat.name.lower()
                        for k,v in fallback_map.items():
                            if k in lname:
                                mat.diffuse_color = v
                                color_set = True
                                break
                    else:
                        color_set = True
            except Exception:
                pass
        if not color_set:
            # apply very light gray to at least make it visible
            if mat.use_nodes:
                try:
                    for node in mat.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.inputs['Base Color'].default_value = (0.7,0.7,0.7,1.0)
                            break
                except Exception:
                    pass
            else:
                try:
                    mat.diffuse_color = (0.7,0.7,0.7,1.0)
                except Exception:
                    pass


def setup_camera_and_lighting(mins, maxs, padding=0.5):
    center = (mins + maxs) / 2.0
    size = max((maxs - mins).length, 0.001)

    # Camera
    cam_data = bpy.data.cameras.new('RenderCam')
    cam = bpy.data.objects.new('RenderCam', cam_data)
    bpy.context.scene.collection.objects.link(cam)

    cam.location = center + Vector((size*1.5, -size*1.5, size*0.8))
    look_at(cam, center)

    bpy.context.scene.camera = cam

    # Light (Sun)
    light_data = bpy.data.lights.new(name='Sun', type='SUN')
    light = bpy.data.objects.new(name='Sun', object_data=light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = center + Vector((size, -size, size*2))
    light.rotation_euler = (0.7, 0.0, 0.5)
    light.data.energy = 5.0


def main():
    args = parse_args()

    # Ensure output dir exists
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    clear_scene()

    input_path = os.path.abspath(args.input)
    print('Importing:', input_path)
    if input_path.lower().endswith('.obj'):
        import_obj(input_path)
    else:
        # Fall back: try importing OBJ by replacing extension
        alt = os.path.splitext(input_path)[0] + '.obj'
        if os.path.exists(alt):
            import_obj(alt)
        else:
            raise RuntimeError('Unsupported input; provide OBJ')

    # Collect mesh objects
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not objs:
        raise RuntimeError('No mesh objects found after import')

    mins, maxs = bounds_of_objects(objs)

    # Ensure materials have colors
    ensure_material_colors()

    # Setup camera and lights
    setup_camera_and_lighting(mins, maxs)

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE' if args.engine == 'EEVEE' else 'CYCLES'
    scene.render.resolution_x = args.resolution[0]
    scene.render.resolution_y = args.resolution[1]
    scene.render.filepath = os.path.abspath(args.output)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = args.transparent

    if args.engine == 'EEVEE':
        scene.eevee.taa_render_samples = args.samples
    else:
        scene.cycles.samples = args.samples

    print('Rendering to', scene.render.filepath)
    bpy.ops.render.render(write_still=True)
    print('Done')


if __name__ == '__main__':
    main()
