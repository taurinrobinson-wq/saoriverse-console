#!/usr/bin/env python3
"""
Blender 4.2+ Import Script for Velinorian Structures

This script imports MGAIA structure JSON files into Blender and creates
optimized 3D geometry with Velinorian materials and aesthetic.

Usage in Blender 4.2:
  1. Open Blender
  2. Go to Scripting workspace
  3. Open this file (Text > Open Text Block)
  4. Run (Alt+P) or Scripting > Run Script
  
  Or via command line:
  blender --python tools/blender_import_velinorian.py
"""

import bpy
import json
from pathlib import Path
from typing import Dict, List, Tuple


# Velinorian color palette and material definitions
VELINORIAN_MATERIALS = {
    "brick": {
        "color": (0.71, 0.39, 0.24, 1.0),  # warm terracotta (RGBA)
        "roughness": 0.8,
        "metallic": 0.0,
        "subsurface_weight": 0.1,
    },
    "dark_wood": {
        "color": (0.24, 0.16, 0.08, 1.0),  # dark walnut
        "roughness": 0.6,
        "metallic": 0.0,
        "subsurface_weight": 0.05,
    },
    "glass": {
        "color": (0.39, 0.59, 0.71, 0.3),  # cool glass blue, semi-transparent
        "roughness": 0.05,
        "metallic": 0.0,
        "transmission": 1.0,
        "ior": 1.45,
    },
    "roof": {
        "color": (0.20, 0.20, 0.20, 1.0),  # dark roof slate
        "roughness": 0.95,
        "metallic": 0.0,
    },
    "moss": {
        "color": (0.39, 0.47, 0.39, 1.0),  # mossy green
        "roughness": 0.95,
        "metallic": 0.0,
        "subsurface_weight": 0.2,
    },
}

DEFAULT_MATERIAL = {
    "color": (0.59, 0.59, 0.59, 1.0),
    "roughness": 0.7,
    "metallic": 0.0,
}


def get_material_name(block_type: str) -> str:
    """Map block type to Velinorian material name."""
    block_lower = block_type.lower()
    
    if "brick" in block_lower or "brickhouse" in block_lower:
        return "brick"
    elif "wood" in block_lower or "oak" in block_lower or "spruce" in block_lower:
        return "dark_wood"
    elif "glass" in block_lower or "window" in block_lower:
        return "glass"
    elif "roof" in block_lower or "slate" in block_lower or "shingles" in block_lower:
        return "roof"
    elif "moss" in block_lower or "vine" in block_lower or "overgrown" in block_lower:
        return "moss"
    else:
        return "brick"  # default to brick aesthetic


def create_velinorian_material(name: str, props: Dict) -> bpy.types.Material:
    """Create a Blender material with Velinorian aesthetic."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.shadow_method = 'HASHED'  # for transparency
    
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = props["color"]
    bsdf.inputs["Roughness"].default_value = props["roughness"]
    bsdf.inputs["Metallic"].default_value = props["metallic"]
    
    if "transmission" in props:
        bsdf.inputs["Transmission"].default_value = props["transmission"]
    if "ior" in props:
        bsdf.inputs["IOR"].default_value = props["ior"]
    if "subsurface_weight" in props:
        bsdf.inputs["Coat Weight"].default_value = props["subsurface_weight"]
    
    return mat


def import_structure_json(
    json_path: str,
    collection_name: str = "Structure",
    merge_materials: bool = True,
) -> bpy.types.Collection:
    """Import a structure JSON and create Blender objects."""
    
    # Load JSON
    try:
        with open(json_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path}: {e}")
        return None
    
    print(f"Importing {data['name']} ({data['block_count']} blocks)...")
    
    # Create collection for this structure
    coll = bpy.data.collections.new(collection_name or data['name'])
    bpy.context.scene.collection.children.link(coll)
    
    # Create/get materials
    materials_cache = {}
    
    # Group blocks by material to batch-create geometry
    blocks_by_mat = {}
    
    for coord_str, block_data in data['blocks'].items():
        block_type = block_data.get("type", "unknown")
        mat_name = get_material_name(block_type)
        
        if mat_name not in materials_cache:
            mat_props = VELINORIAN_MATERIALS.get(mat_name, DEFAULT_MATERIAL)
            materials_cache[mat_name] = create_velinorian_material(mat_name, mat_props)
        
        if mat_name not in blocks_by_mat:
            blocks_by_mat[mat_name] = []
        
        x, y, z = map(int, coord_str.split(','))
        blocks_by_mat[mat_name].append((x, y, z))
    
    # Create geometry for each material group
    for mat_name, positions in blocks_by_mat.items():
        # Create a merged mesh if requested
        if merge_materials and len(positions) > 1:
            mesh = bpy.data.meshes.new(name=f"mesh_{mat_name}")
            obj = bpy.data.objects.new(f"{mat_name}_merged", mesh)
            
            # Build vertex data for all blocks in this group
            verts = []
            faces = []
            
            for x, y, z in positions:
                base_vi = len(verts)
                # Create cube vertices at this position
                cube_verts = [
                    (x - 0.5, y - 0.5, z - 0.5),
                    (x + 0.5, y - 0.5, z - 0.5),
                    (x + 0.5, y + 0.5, z - 0.5),
                    (x - 0.5, y + 0.5, z - 0.5),
                    (x - 0.5, y - 0.5, z + 0.5),
                    (x + 0.5, y - 0.5, z + 0.5),
                    (x + 0.5, y + 0.5, z + 0.5),
                    (x - 0.5, y + 0.5, z + 0.5),
                ]
                verts.extend(cube_verts)
                
                # Define cube faces (quads as tris for simplicity)
                cube_faces = [
                    (0, 1, 2, 3),  # front
                    (5, 4, 7, 6),  # back
                    (4, 0, 3, 7),  # left
                    (1, 5, 6, 2),  # right
                    (3, 2, 6, 7),  # top
                    (4, 5, 1, 0),  # bottom
                ]
                for a, b, c, d in cube_faces:
                    faces.append((base_vi + a, base_vi + b, base_vi + c))
                    faces.append((base_vi + c, base_vi + d, base_vi + a))
            
            # Assign geometry
            mesh.from_pydata(verts, [], faces)
            mesh.update()
            
            # Assign material
            mat = materials_cache[mat_name]
            obj.data.materials.append(mat)
            
            # Link to collection
            coll.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
        else:
            # Individual blocks (for small groups)
            for x, y, z in positions:
                mesh = bpy.data.meshes.new(name=f"block_{x}_{y}_{z}")
                obj = bpy.data.objects.new(f"block_{x}_{y}_{z}", mesh)
                
                # Single cube
                verts = [
                    (x - 0.5, y - 0.5, z - 0.5),
                    (x + 0.5, y - 0.5, z - 0.5),
                    (x + 0.5, y + 0.5, z - 0.5),
                    (x - 0.5, y + 0.5, z - 0.5),
                    (x - 0.5, y - 0.5, z + 0.5),
                    (x + 0.5, y - 0.5, z + 0.5),
                    (x + 0.5, y + 0.5, z + 0.5),
                    (x - 0.5, y + 0.5, z + 0.5),
                ]
                faces = [
                    (0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7),
                    (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0),
                ]
                mesh.from_pydata(verts, [], faces)
                mesh.update()
                
                # Assign material
                mat = materials_cache[mat_name]
                obj.data.materials.append(mat)
                
                # Link to collection
                coll.objects.link(obj)
    
    print(f"  ✓ Created {len(blocks_by_mat)} material groups")
    return coll


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("VELINORIAN IMPORTER STARTING...")
    print("="*60)
    
    # Clear default cube if present
    if "Cube" in bpy.data.objects:
        print("Clearing default cube...")
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # Get the workspace/script directory
    # Handle both direct execution and Blender's text editor execution
    try:
        script_path = Path(__file__).resolve()
        workspace_dir = script_path.parent.parent
        print(f"Script path: {script_path}")
        print(f"Workspace dir: {workspace_dir}")
    except (TypeError, AttributeError):
        # Running from Blender text editor; use current project or bpy context
        workspace_dir = Path(bpy.path.abspath("//")).parent if bpy.data.filepath else Path.cwd()
        if not workspace_dir.exists():
            workspace_dir = Path.cwd()
        print(f"Using Blender context dir: {workspace_dir}")
    
    structures_dir = workspace_dir / "velinor" / "assets" / "structures"
    print(f"Looking for structures at: {structures_dir}")
    print(f"Exists: {structures_dir.exists()}")
    
    # Fallback: if structures not found, try relative from CWD
    if not structures_dir.exists():
        print(f"Not found, trying CWD: {Path.cwd()}")
        structures_dir = Path.cwd() / "velinor" / "assets" / "structures"
        print(f"New path: {structures_dir}")
        print(f"Exists: {structures_dir.exists()}")
    
    if not structures_dir.exists():
        print(f"\nERROR: Could not find structures directory!")
        print(f"Tried: {workspace_dir / 'velinor' / 'assets' / 'structures'}")
        print(f"Tried: {Path.cwd() / 'velinor' / 'assets' / 'structures'}")
        print(f"Current working directory: {Path.cwd()}")
        print(f"Available dirs in CWD: {list(Path.cwd().iterdir())[:10]}")
        return
    
    # Import all structures found
    json_files = sorted(structures_dir.glob("*.json"))
    print(f"\nFound {len(json_files)} structure files at {structures_dir}")
    
    # Create a parent collection for all structures
    parent_coll = bpy.data.collections.new("Velinorian_Settlement")
    bpy.context.scene.collection.children.link(parent_coll)
    
    for json_file in json_files:
        try:
            coll = import_structure_json(
                str(json_file),
                collection_name=json_file.stem,
                merge_materials=True,
            )
            if coll is None:
                continue
            # Move to parent collection
            parent_coll.children.link(coll)
            bpy.context.scene.collection.children.unlink(coll)
        except Exception as e:
            print(f"  ✗ Failed to import {json_file.stem}: {e}")
            import traceback
            traceback.print_exc()
    
    # Frame all in viewport (Blender 4.2+ compatible)
    try:
        # Try using context override (Blender 4.2+)
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        # Use temp_override for proper context in Blender 4.2+
                        with bpy.context.temp_override(area=area, region=region):
                            bpy.ops.view3d.view_all()
                        break
    except Exception as e:
        print(f"Warning: Could not frame viewport: {e}")
    
    print("\n✓ Import complete! Velinorian structures loaded.")


if __name__ == '__main__':
    main()
