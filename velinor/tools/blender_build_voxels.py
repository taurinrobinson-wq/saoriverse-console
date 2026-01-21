#!/usr/bin/env python3
"""
Simple Blender 4.2 Script: Build Velinorian structure as individual voxel blocks.

This creates cube primitives for each block, grouped by material type,
so you see an actual building made of separate blocks.

Run in Blender Scripting workspace (Alt+P).
"""
import bpy
import json
from pathlib import Path


def create_velinorian_voxels(
    json_path: str = "velinor/assets/structures/brickhouse-entrance.json"
):
    """Create individual cube objects for each block in the structure."""
    
    # Load JSON
    try:
        with open(json_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {json_path} not found")
        return
    
    blocks = data["blocks"]
    print(f"\nBuilding {data['name']} ({len(blocks)} blocks)...")
    
    # Clear default cube
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # Create collection
    coll = bpy.data.collections.new(data['name'])
    bpy.context.scene.collection.children.link(coll)
    
    # Material color mapping
    materials = {}
    
    def get_material(block_type: str, color_rgb: tuple):
        """Get or create a Blender material for a block type.

        Create a viewport-friendly material (non-node) and set `diffuse_color`
        so Material Preview reliably shows the intended color.
        """
        key = f"{block_type}_{color_rgb}"
        if key in materials:
            return materials[key]

        mat = bpy.data.materials.new(name=f"mat_{block_type[:15]}")

        # Use simple non-node material to make viewport preview consistent
        mat.use_nodes = False

        # Set color (normalize RGB 0-255 to 0-1)
        r, g, b = color_rgb
        color4 = (r/255.0, g/255.0, b/255.0, 1.0)
        try:
            mat.diffuse_color = color4
        except Exception:
            # Fallback assignment
            mat.diffuse_color = (r/255.0, g/255.0, b/255.0, 1.0)

        # Make viewport display color explicit
        mat.preview_render_type = 'FLAT'

        materials[key] = mat
        return mat
    
    # Create cube for each block
    for i, (coord_str, block_data) in enumerate(blocks.items()):
        x, y, z = map(int, coord_str.split(','))
        block_type = block_data.get("type", "brick")
        aesth = block_data.get("aesthetic", {"color": (150, 150, 150)})
        color = aesth["color"]
        
        # Add cube
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z))
        obj = bpy.context.active_object
        obj.name = f"block_{i}_{block_type}"
        
        # Assign material (and set object viewport color)
        mat = get_material(block_type, color)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        # Ensure object viewport color matches material (useful in solid/preview)
        try:
            obj.color = mat.diffuse_color
        except Exception:
            # Some Blender builds use different attribute names
            try:
                obj.color = (color[0]/255.0, color[1]/255.0, color[2]/255.0, 1.0)
            except Exception:
                pass
        
        # Link to collection
        for coll_in in obj.users_collection:
            coll_in.objects.unlink(obj)
        coll.objects.link(obj)
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"  Created {i+1}/{len(blocks)} blocks...")
    
    print(f"✓ Done! Created {len(blocks)} block objects")
    print(f"Materials created: {list(materials.keys())[:10]}...")  # Show sample

    # Print a small sample of object -> material assignments for debugging
    sample_mappings = []
    for i, obj in enumerate(coll.objects):
        if i >= 5:
            break
        mat_name = obj.active_material.name if obj.active_material else None
        sample_mappings.append((obj.name, mat_name, tuple(getattr(obj, 'color', (None,)))))
    print(f"Sample object->material mappings: {sample_mappings}")
    
    # Select collection and frame view
    for obj in coll.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    
    # Frame all
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        with bpy.context.temp_override(area=area, region=region):
                            bpy.ops.view3d.view_all()
    except:
        pass


if __name__ == '__main__':
    # Find the JSON file
    workspace_dir = Path.cwd()
    json_file = workspace_dir / "velinor" / "assets" / "structures" / "brickhouse-entrance.json"
    
    if not json_file.exists():
        print(f"Looking in: {workspace_dir}")
        print(f"Available dirs: {list(workspace_dir.iterdir())[:10]}")
        json_file = Path.cwd() / "velinor" / "assets" / "structures" / "brickhouse-entrance.json"
    
    print(f"Using: {json_file}")
    create_velinorian_voxels(str(json_file))
