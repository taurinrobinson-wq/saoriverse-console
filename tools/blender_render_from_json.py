#!/usr/bin/env python3
"""
Headless Blender renderer that builds the scene directly from a JSON structure
(file produced by `tools/mgaia_converter.py`) and renders a PNG.

Usage:
blender --background --python tools/blender_render_from_json.py -- --json velinor/assets/structures/brickhouse-entrance.json --output renders/brickhouse-entrance.png --resolution 2048 2048 --engine EEVEE --samples 64

This avoids importing OBJ and creates one cube object per voxel with explicit
materials so colors render consistently.
"""
import sys
import os
import argparse
import json
from mathutils import Vector

import bpy


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--json", required=True, help="Input JSON structure file")
    p.add_argument("--output", required=True, help="Output PNG path")
    p.add_argument("--resolution", nargs=2, type=int, default=[1024,1024])
    p.add_argument("--engine", choices=["EEVEE","CYCLES"], default="EEVEE")
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--transparent", action="store_true")
    return p.parse_args(argv)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, color_rgb):
    # create non-node material and set diffuse_color
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = False
    r,g,b = color_rgb
    col = (r/255.0, g/255.0, b/255.0, 1.0)
    try:
        mat.diffuse_color = col
    except Exception:
        mat.diffuse_color = col
    mat.preview_render_type = 'FLAT'
    return mat


def build_scene_from_json(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(json_path)
    with open(json_path, 'r') as f:
        data = json.load(f)
    blocks = data.get('blocks', {})

    coll = bpy.data.collections.new(data.get('name','structure'))
    bpy.context.scene.collection.children.link(coll)

    materials_cache = {}
    objs = []

    for i, (coord_str, block) in enumerate(blocks.items()):
        x,y,z = map(int, coord_str.split(','))
        btype = block.get('type','brick')
        aesth = block.get('aesthetic',{})
        color = aesth.get('color', (150,150,150))
        mat_key = f"{btype}_{color}"
        if mat_key in materials_cache:
            mat = materials_cache[mat_key]
        else:
            mat = make_material(f"mat_{btype}", color)
            materials_cache[mat_key] = mat

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x,y,z))
        obj = bpy.context.active_object
        obj.name = f"block_{i}_{btype}"
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        try:
            obj.color = mat.diffuse_color
        except Exception:
            pass
        for c in obj.users_collection:
            c.objects.unlink(obj)
        coll.objects.link(obj)
        objs.append(obj)
        if (i+1) % 200 == 0:
            print(f"Built {i+1} blocks...")

    print(f"Built {len(objs)} block objects with {len(materials_cache)} materials")
    return objs


def bounds_of_objects(objs):
    mins = Vector((1e9,1e9,1e9))
    maxs = Vector((-1e9,-1e9,-1e9))
    for obj in objs:
        if obj.type != 'MESH':
            continue
        for v in obj.bound_box:
            co = obj.matrix_world @ Vector(v)
            mins.x = min(mins.x, co.x)
            mins.y = min(mins.y, co.y)
            mins.z = min(mins.z, co.z)
            maxs.x = max(maxs.x, co.x)
            maxs.y = max(maxs.y, co.y)
            maxs.z = max(maxs.z, co.z)
    return mins, maxs


def look_at(obj_camera, target_point):
    direction = target_point - obj_camera.location
    obj_camera.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()


def setup_camera_and_light(mins, maxs):
    center = (mins + maxs) / 2.0
    size = max((maxs - mins).length, 0.001)

    cam_data = bpy.data.cameras.new('RenderCam')
    cam = bpy.data.objects.new('RenderCam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = center + Vector((size*1.5, -size*1.5, size*0.8))
    look_at(cam, center)
    bpy.context.scene.camera = cam

    light_data = bpy.data.lights.new(name='Sun', type='SUN')
    light = bpy.data.objects.new(name='Sun', object_data=light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = center + Vector((size, -size, size*2))
    light.rotation_euler = (0.7, 0.0, 0.5)
    light.data.energy = 5.0


def main():
    args = parse_args()
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    clear_scene()
    objs = build_scene_from_json(os.path.abspath(args.json))
    if not objs:
        raise RuntimeError('No objects built')

    mins, maxs = bounds_of_objects(objs)
    setup_camera_and_light(mins, maxs)

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
