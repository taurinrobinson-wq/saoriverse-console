"""
Label Overworld Map - Velhara Regions
Programmatically adds region labels to OverworldMap.png

This script reads the clean line-art map and overlays region names
with proper positioning to match the map's visual layout.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
MAP_PATH = os.path.join(os.path.dirname(__file__), "Assets", "Resources", "DesignDocs", "OverworldMap.png")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "Assets", "Resources", "DesignDocs", "OverworldMap_Labeled.png")

# Region definitions: (name, x, y, font_size, rotation)
# Coordinates are approximate based on the map layout
REGIONS = [
    # Eastern regions (Ruins of Past Velhara)
    ("ARCHIVE DISTRICT\n(Ruins of Past Velhara)", 1100, 180, 18, 0),
    ("CONCOURSE\nRUINS", 950, 320, 14, 0),
    ("NEALLING\nALOUF", 850, 280, 12, 0),
    ("HEARTS", 920, 250, 12, 0),
    
    # Northern region
    ("SHRINE RIDGE", 550, 120, 20, 0),
    ("CR GARDENS\nRUINS", 500, 240, 12, 0),
    
    # Central region
    ("MARKET BASIN", 480, 380, 22, 0),
    ("TRAINING\nRUINS", 570, 350, 12, 0),
    ("TEMPLE\nRUINS", 440, 340, 11, 0),
    
    # Harbor area
    ("HARBOR AIR\nLOWLANDS", 1050, 500, 16, 0),
    
    # Southern regions
    ("SWAMID SWAMPS\nLOWLANDS", 650, 600, 14, 0),
    ("WARKET\nTTRALCOUNS\nBOATS", 720, 650, 11, 0),
    
    # Western regions
    ("DESERT &\nMOUNTAIN EXPANSE", 280, 380, 16, 0),
    ("HORSEGROVE\nFORTISS", 150, 200, 11, 0),
    
    # Southwest
    ("BURIED TOMB\nARCHIVES", 200, 550, 12, 0),
    ("NOCDHIDAR", 180, 650, 11, 0),
    ("HIDDEN\nSHRINES", 380, 620, 11, 0),
]

def load_font(size):
    """Load a serif font, fallback to default if unavailable."""
    font_names = [
        "C:\\Windows\\Fonts\\times.ttf",      # Times New Roman (Windows)
        "C:\\Windows\\Fonts\\georgia.ttf",    # Georgia (Windows)
        "/System/Library/Fonts/Times.ttc",   # Times (macOS)
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",  # Linux
    ]
    
    for font_path in font_names:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
    
    # Fallback to default
    return ImageFont.load_default()

def add_labels_to_map(map_path, output_path, regions):
    """
    Add region labels to the overworld map.
    
    Args:
        map_path: Path to the original map image
        output_path: Path to save the labeled map
        regions: List of (name, x, y, font_size, rotation) tuples
    """
    
    if not os.path.exists(map_path):
        raise FileNotFoundError(f"Map not found at {map_path}")
    
    # Open the map image
    img = Image.open(map_path).convert('RGB')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Define text styling
    text_color = (60, 40, 20, 220)  # Dark brown with slight transparency
    outline_color = (240, 230, 210, 180)  # Cream/parchment outline
    
    # Add each region label
    for region_name, x, y, font_size, rotation in regions:
        try:
            font = load_font(font_size)
        except:
            font = load_font(16)
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), region_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text at the given position
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        
        # Draw text with outline effect for better readability
        outline_width = 1
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text(
                        (text_x + adj_x, text_y + adj_y),
                        region_name,
                        font=font,
                        fill=outline_color
                    )
        
        # Draw main text
        draw.text(
            (text_x, text_y),
            region_name,
            font=font,
            fill=text_color
        )
    
    # Save the labeled map
    img.save(output_path, quality=95)
    print(f"✓ Labeled map saved to: {output_path}")
    print(f"  Image size: {img.size}")
    print(f"  Regions labeled: {len(regions)}")

if __name__ == "__main__":
    try:
        add_labels_to_map(MAP_PATH, OUTPUT_PATH, REGIONS)
        print("\n✓ Map labeling complete!")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
