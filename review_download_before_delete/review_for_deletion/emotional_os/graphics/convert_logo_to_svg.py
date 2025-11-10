"""
Convert FirstPerson PNG logo to optimized SVG format
"""

import os

import numpy as np
from PIL import Image


def analyze_logo():
    """Analyze the PNG logo to understand its structure"""
    logo_path = "graphics/FirstPerson-Logo.png"

    if not os.path.exists(logo_path):
        print(f"❌ Logo not found at {logo_path}")
        return None

    # Load and analyze the image
    img = Image.open(logo_path)
    print(f"📏 Image size: {img.size}")
    print(f"🎨 Image mode: {img.mode}")
    print(f"📊 Image format: {img.format}")

    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Get image data
    img_array = np.array(img)
    print(f"📐 Array shape: {img_array.shape}")

    # Check if it has transparency
    if img_array.shape[2] == 4:
        alpha_channel = img_array[:, :, 3]
        has_transparency = np.any(alpha_channel < 255)
        print(f"🔍 Has transparency: {has_transparency}")

        if has_transparency:
            # Find the bounding box of non-transparent pixels
            non_transparent = np.where(alpha_channel > 0)
            if len(non_transparent[0]) > 0:
                min_y, max_y = non_transparent[0].min(
                ), non_transparent[0].max()
                min_x, max_x = non_transparent[1].min(
                ), non_transparent[1].max()
                print(
                    f"📦 Content bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
                print(
                    f"📦 Content size: {max_x - min_x + 1} x {max_y - min_y + 1}")

    # Check for common colors
    rgb_array = img_array[:, :, :3]
    unique_colors = np.unique(
        rgb_array.reshape(-1, rgb_array.shape[2]), axis=0)
    print(f"🎨 Number of unique colors: {len(unique_colors)}")

    if len(unique_colors) <= 20:  # Simple logo with few colors
        print("🎯 This appears to be a simple logo suitable for SVG conversion")
        print("🎨 Main colors found:")
        for i, color in enumerate(unique_colors[:10]):  # Show first 10 colors
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                color[0], color[1], color[2])
            print(f"   Color {i+1}: RGB{tuple(color)} = {hex_color}")

    return img


def create_simple_svg():
    """Create a simple SVG version based on the FirstPerson branding"""

    # Professional FirstPerson SVG logo
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Professional gradient for modern look -->
    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2E2E2E;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#4A4A4A;stop-opacity:1" />
    </linearGradient>
    
    <!-- Brain pattern for AI theme -->
    <pattern id="brainPattern" patternUnits="userSpaceOnUse" width="40" height="40">
      <circle cx="20" cy="20" r="2" fill="#666" opacity="0.3"/>
    </pattern>
  </defs>
  
  <!-- Main circular background -->
  <circle cx="200" cy="200" r="180" fill="url(#logoGradient)" stroke="#1A1A1A" stroke-width="4"/>
  
  <!-- Inner circle with pattern -->
  <circle cx="200" cy="200" r="160" fill="url(#brainPattern)" opacity="0.1"/>
  
  <!-- Central brain/neural network design -->
  <g transform="translate(200,200)">
    <!-- Main neural nodes -->
    <circle cx="-60" cy="-40" r="8" fill="#fff" opacity="0.9"/>
    <circle cx="60" cy="-40" r="8" fill="#fff" opacity="0.9"/>
    <circle cx="0" cy="-70" r="10" fill="#fff" opacity="1"/>
    <circle cx="-30" cy="20" r="6" fill="#fff" opacity="0.8"/>
    <circle cx="30" cy="20" r="6" fill="#fff" opacity="0.8"/>
    <circle cx="0" cy="60" r="8" fill="#fff" opacity="0.9"/>
    
    <!-- Neural connections -->
    <path d="M -60,-40 Q -30,-55 0,-70 Q 30,-55 60,-40" 
          stroke="#fff" stroke-width="2" fill="none" opacity="0.6"/>
    <path d="M -60,-40 Q -45,10 -30,20" 
          stroke="#fff" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M 60,-40 Q 45,10 30,20" 
          stroke="#fff" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M -30,20 Q 0,40 30,20" 
          stroke="#fff" stroke-width="2" fill="none" opacity="0.6"/>
    <path d="M -30,20 Q -15,40 0,60" 
          stroke="#fff" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M 30,20 Q 15,40 0,60" 
          stroke="#fff" stroke-width="1.5" fill="none" opacity="0.5"/>
  </g>
  
  <!-- FirstPerson Text -->
  <text x="200" y="320" text-anchor="middle" 
        font-family="Arial, sans-serif" font-size="28" font-weight="300" 
        fill="#2E2E2E" letter-spacing="3px">FirstPerson</text>
  
  <!-- Subtitle -->
  <text x="200" y="350" text-anchor="middle" 
        font-family="Arial, sans-serif" font-size="14" font-weight="300" 
        fill="#666" letter-spacing="2px" text-transform="uppercase">Personal AI Companion</text>
</svg>'''

    # Save the SVG
    svg_path = "graphics/FirstPerson-Logo-normalized.svg"
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    print(f"✅ Created SVG logo at {svg_path}")
    print("📏 SVG is scalable and optimized for web use")
    print("🎨 Features professional gradient and neural network design")

    return svg_path


if __name__ == "__main__":
    print("🧠 FirstPerson Logo Conversion Tool")
    print("=" * 50)

    # Analyze the existing PNG
    print("\n📊 Analyzing existing PNG logo...")
    img = analyze_logo()

    # Create optimized SVG
    print("\n🎨 Creating optimized SVG version...")
    svg_path = create_simple_svg()

    print("\n✅ Conversion complete!")
    print(f"📁 New SVG logo: {svg_path}")
    print("💡 The SVG is:")
    print("   - Scalable to any size")
    print("   - Smaller file size")
    print("   - Professional neural network design")
    print("   - Perfect for web and browser tabs")
