import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

# Create a warm desert rock texture
width, height = 512, 512

# Base warm sandy brown color (similar to your DesertGround_URP material)
base_color = (194, 161, 115)  # RGB for warm tan

# Create image with noise for rocky texture
img_array = np.zeros((height, width, 3), dtype=np.uint8)

# Add Perlin-like noise using multiple octaves of simplex noise
# For simplicity, we'll use fractional Brownian motion-style noise
for y in range(height):
    for x in range(width):
        # Create natural rock variation using simplex-like approach
        noise = 0
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0
        
        # Multiple octaves for natural look
        for octave in range(4):
            sample_x = x / (width * 0.5) * frequency
            sample_y = y / (height * 0.5) * frequency
            
            # Pseudo-random based on position (deterministic)
            hash_val = abs(np.sin(sample_x * 12.9898 + sample_y * 78.233) * 43758.5453)
            hash_val = hash_val - int(hash_val)
            
            noise += hash_val * amplitude
            max_amplitude += amplitude
            
            amplitude *= 0.5
            frequency *= 2.0
        
        noise = noise / max_amplitude
        
        # Create rocky surface variation (0.7 to 1.3 range)
        variation = 0.7 + (noise * 0.6)
        
        # Apply to base color
        for c in range(3):
            value = int(base_color[c] * variation)
            img_array[y, x, c] = min(255, max(0, value))

# Convert to PIL image
img = Image.fromarray(img_array, 'RGB')

# Add some additional texture detail with edge enhancement
# This creates the rocky surface look
img = img.filter(ImageFilter.GaussianBlur(radius=2))

# Add some roughness/grain
img_array = np.array(img)
grain = np.random.randint(-20, 20, (height, width, 3), dtype=np.int16)
img_array = img_array.astype(np.int16) + grain
img_array = np.clip(img_array, 0, 255).astype(np.uint8)
img = Image.fromarray(img_array, 'RGB')

# Save the texture
output_path = r'C:\saoriverse-console\Velinor-Unity\Assets\PolishedSurfaces\System_RockSet_Sample\Art\Textures\2. Medium\T_RockSet_01_Medium_01_Desert_A.png'
img.save(output_path)
print(f"Texture created: {output_path}")
print(f"Texture size: {width}x{height}")
print(f"Base color (RGB): {base_color}")
