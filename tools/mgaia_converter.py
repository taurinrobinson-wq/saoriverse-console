#!/usr/bin/env python3
"""
MGAIA Structure Loader and Exporter

Loads MGAIA pickled structures and exports to JSON for further processing.
Also generates a Velinorian 3D aesthetic representation (OBJ mesh).

Usage:
  python tools/mgaia_converter.py --export-json
  python tools/mgaia_converter.py --build-velinorian

The first command exports all MGAIA structures to JSON.
The second creates a unified Velinorian building asset (OBJ + MTL).
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add MGAIA to path so we can import its structure loader
sys.path.insert(0, str(Path(__file__).parent.parent / "third_party" / "MGAIA-Minecraft-GDMC"))

from assignment.utils.structure import load_structure


# Velinorian block type mappings (Minecraft block names to Velinorian aesthetic)
VELINORIAN_BLOCKS = {
    "brickhouse-brick": {
        "color": (180, 100, 60),        # warm terracotta
        "roughness": 0.8,
        "metallic": 0.0,
        "emissive": (0, 0, 0),
    },
    "dark-oak-wood": {
        "color": (60, 40, 20),          # dark walnut
        "roughness": 0.6,
        "metallic": 0.0,
        "emissive": (0, 0, 0),
    },
    "glass": {
        "color": (100, 150, 180),       # cool glass blue
        "roughness": 0.05,
        "metallic": 0.0,
        "emissive": (20, 30, 40),       # slight glow
    },
    "spruce-wood": {
        "color": (50, 50, 50),          # dark roof
        "roughness": 0.9,
        "metallic": 0.0,
        "emissive": (0, 0, 0),
    },
    "mossy-cobblestone": {
        "color": (100, 120, 100),       # mossy green
        "roughness": 0.95,
        "metallic": 0.0,
        "emissive": (0, 0, 0),
    },
}

# Default aesthetic
DEFAULT_AESTHETIC = {
    "color": (150, 150, 150),
    "roughness": 0.7,
    "metallic": 0.0,
    "emissive": (0, 0, 0),
}


def get_block_aesthetic(block_name: str) -> Dict:
    """Get Velinorian aesthetic for a Minecraft block."""
    for key, aesth in VELINORIAN_BLOCKS.items():
        if key.lower() in block_name.lower():
            return aesth
    return DEFAULT_AESTHETIC


def export_structures_to_json(
    structures_dir: str = "third_party/MGAIA-Minecraft-GDMC/structures",
    output_dir: str = "velinor/assets/structures",
) -> None:
    """Load all MGAIA structures and export metadata + aesthetics to JSON."""
    os.makedirs(output_dir, exist_ok=True)

    pkl_files = sorted(Path(structures_dir).glob("*.pkl"))
    print(f"Found {len(pkl_files)} structure files")

    for pkl_path in pkl_files:
        struct_name = pkl_path.stem
        try:
            # Load structure using MGAIA's loader
            struct = load_structure(struct_name, structures_dir)
            
            # Extract block data
            blocks_data = {}
            for (x, y, z), block in struct.blocks.items():
                block_name = getattr(block, "namespacedName", "unknown")
                aesth = get_block_aesthetic(block_name)
                blocks_data[f"{x},{y},{z}"] = {
                    "type": block_name,
                    "x": x, "y": y, "z": z,
                    "aesthetic": aesth,
                }
            
            # Export to JSON
            export_data = {
                "name": struct.name,
                "size": {
                    "x": struct.size.x if hasattr(struct.size, 'x') else 0,
                    "y": struct.size.y if hasattr(struct.size, 'y') else 0,
                    "z": struct.size.z if hasattr(struct.size, 'z') else 0,
                },
                "offset": {
                    "x": struct.offset.x if hasattr(struct.offset, 'x') else 0,
                    "y": struct.offset.y if hasattr(struct.offset, 'y') else 0,
                    "z": struct.offset.z if hasattr(struct.offset, 'z') else 0,
                },
                "block_count": len(blocks_data),
                "blocks": blocks_data,
            }
            
            output_file = Path(output_dir) / f"{struct_name}.json"
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"  ✓ {struct_name}: {len(blocks_data)} blocks")
        
        except Exception as e:
            print(f"  ✗ {struct_name}: {e}")


def build_velinorian_obj(
    input_json: str = "velinor/assets/structures/brickhouse-entrance.json",
    output_obj: str = "velinor/assets/velinorian_building.obj",
    output_mtl: str = "velinor/assets/velinorian_building.mtl",
) -> None:
    """Build a 3D OBJ mesh from a structure JSON, applying Velinorian aesthetic."""
    
    # Load structure JSON
    with open(input_json) as f:
        struct_data = json.load(f)
    
    blocks = struct_data["blocks"]
    
    # Build OBJ file with materials
    obj_lines = [
        f"# Velinorian Building: {struct_data['name']}",
        f"# Blocks: {struct_data['block_count']}",
        f"mtllib {Path(output_mtl).name}",
        "",
    ]
    
    mtl_lines = [
        f"# Velinorian Material Library",
        "",
    ]
    
    # Track unique materials
    materials = {}
    vertex_count = 0
    
    # Define a cube mesh for each block (simplified)
    def cube_verts(x: float, y: float, z: float, scale: float = 1.0):
        """Generate 8 vertices for a unit cube at (x,y,z)."""
        s = scale / 2
        return [
            (x - s, y - s, z - s),
            (x + s, y - s, z - s),
            (x + s, y + s, z - s),
            (x - s, y + s, z - s),
            (x - s, y - s, z + s),
            (x + s, y - s, z + s),
            (x + s, y + s, z + s),
            (x - s, y + s, z + s),
        ]
    
    def cube_faces(base_vi: int):
        """Generate 6 faces for a cube (quads as triangles)."""
        faces = []
        # Front, Back, Left, Right, Top, Bottom
        quads = [
            (0, 1, 2, 3),
            (5, 4, 7, 6),
            (4, 0, 3, 7),
            (1, 5, 6, 2),
            (3, 2, 6, 7),
            (4, 5, 1, 0),
        ]
        for a, b, c, d in quads:
            faces.append((base_vi + a + 1, base_vi + b + 1, base_vi + c + 1))
            faces.append((base_vi + c + 1, base_vi + d + 1, base_vi + a + 1))
        return faces
    
    # Generate geometry
    for coord_str, block_data in blocks.items():
        x, y, z = map(int, coord_str.split(','))
        aesth = block_data["aesthetic"]
        
        # Create material name
        r, g, b = aesth["color"]
        mat_name = f"mat_{r}_{g}_{b}"
        
        if mat_name not in materials:
            materials[mat_name] = aesth
            # Add material definition to MTL
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            mtl_lines.append(f"newmtl {mat_name}")
            mtl_lines.append(f"Ka 0.1 0.1 0.1")  # Ambient
            mtl_lines.append(f"Kd {r_norm} {g_norm} {b_norm}")  # Diffuse
            mtl_lines.append(f"Ks 0.5 0.5 0.5")  # Specular
            mtl_lines.append(f"Ns 32")  # Shininess
            mtl_lines.append("")
        
        # Add vertices
        verts = cube_verts(float(x), float(y), float(z), scale=1.0)
        for vx, vy, vz in verts:
            obj_lines.append(f"v {vx} {vy} {vz}")
        
        # Add faces
        faces = cube_faces(vertex_count)
        obj_lines.append(f"usemtl {mat_name}")
        for f_a, f_b, f_c in faces:
            obj_lines.append(f"f {f_a} {f_b} {f_c}")
        
        vertex_count += len(verts)
    
    # Write OBJ
    os.makedirs(Path(output_obj).parent, exist_ok=True)
    with open(output_obj, 'w') as f:
        f.write('\n'.join(obj_lines) + '\n')
    print(f"Wrote OBJ: {output_obj}")
    
    # Write MTL
    with open(output_mtl, 'w') as f:
        f.write('\n'.join(mtl_lines) + '\n')
    print(f"Wrote MTL: {output_mtl}")


def build_velinorian_gltf(
    input_json: str = "velinor/assets/structures/brickhouse-entrance.json",
    output_glb: str = "velinor/assets/brickhouse-entrance_velinorian.glb",
) -> None:
    """Build a glTF 2.0 binary mesh from a structure JSON (for Blender/engines)."""
    try:
        import trimesh
    except ImportError:
        print("trimesh not installed; skipping glTF export")
        return
    
    # Load structure JSON
    with open(input_json) as f:
        struct_data = json.load(f)
    
    blocks = struct_data["blocks"]
    
    # Build mesh
    meshes = []
    for coord_str, block_data in blocks.items():
        x, y, z = map(int, coord_str.split(','))
        
        # Create a cube at this position
        mesh = trimesh.creation.box(extents=[1.0, 1.0, 1.0])
        mesh.apply_translation([x, y, z])
        meshes.append(mesh)
    
    # Combine all meshes
    combined = trimesh.util.concatenate(meshes)
    
    # Export glTF
    os.makedirs(Path(output_glb).parent, exist_ok=True)
    combined.export(output_glb)
    print(f"Wrote glTF: {output_glb}")


def main():
    parser = argparse.ArgumentParser(description="MGAIA Structure Converter")
    parser.add_argument("--export-json", action="store_true", help="Export all structures to JSON")
    parser.add_argument("--build-velinorian", action="store_true", help="Build Velinorian OBJ mesh")
    parser.add_argument("--build-gltf", action="store_true", help="Build Velinorian glTF mesh (for Blender 4.2+)")
    parser.add_argument("--structure", type=str, default="brickhouse-entrance", 
                        help="Structure name for export (default: brickhouse-entrance)")
    args = parser.parse_args()
    
    if args.export_json:
        print("Exporting MGAIA structures to JSON...")
        export_structures_to_json()
        print("Done!")
    
    elif args.build_velinorian:
        print(f"Building Velinorian OBJ from {args.structure}...")
        json_file = f"velinor/assets/structures/{args.structure}.json"
        obj_file = f"velinor/assets/{args.structure}_velinorian.obj"
        mtl_file = f"velinor/assets/{args.structure}_velinorian.mtl"
        build_velinorian_obj(json_file, obj_file, mtl_file)
        print("Done!")
    
    elif args.build_gltf:
        print(f"Building Velinorian glTF from {args.structure}...")
        json_file = f"velinor/assets/structures/{args.structure}.json"
        glb_file = f"velinor/assets/{args.structure}_velinorian.glb"
        build_velinorian_gltf(json_file, glb_file)
        print("Done!")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
