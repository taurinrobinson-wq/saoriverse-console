#!/bin/bash
# Link Velinor game assets to web public folder for Next.js to serve

VELINOR_ROOT="../velinor"
PUBLIC_ASSETS="./public/assets"

echo "Syncing Velinor assets to web public folder..."

# Ensure directories exist
mkdir -p "$PUBLIC_ASSETS/backgrounds"
mkdir -p "$PUBLIC_ASSETS/npcs"
mkdir -p "$PUBLIC_ASSETS/overlays"

# Copy backgrounds (or create symlinks)
echo "Copying backgrounds..."
cp "$VELINOR_ROOT/backgrounds/Velhara_background_title(blur).png" "$PUBLIC_ASSETS/backgrounds/" || true
cp "$VELINOR_ROOT/backgrounds/Velhara_background_title.png" "$PUBLIC_ASSETS/backgrounds/" || true
cp "$VELINOR_ROOT/backgrounds/velinor_title_eyes_closed.png" "$PUBLIC_ASSETS/backgrounds/" || true

# Copy NPCs
echo "Copying NPCs..."
cp "$VELINOR_ROOT/npcs/velinor_eyesclosed2.png" "$PUBLIC_ASSETS/npcs/" || true
cp "$VELINOR_ROOT/npcs/velinor_eyesclosed.png" "$PUBLIC_ASSETS/npcs/" || true
cp "$VELINOR_ROOT/npcs/velinor_eyesopen.png" "$PUBLIC_ASSETS/npcs/" || true

# Copy overlays
echo "Copying overlays..."
cp "$VELINOR_ROOT/overlays/velinor_title_transparent2.png" "$PUBLIC_ASSETS/overlays/" || true
cp "$VELINOR_ROOT/overlays/velinor_title_transparent.png" "$PUBLIC_ASSETS/overlays/" || true

echo "Asset sync complete!"
echo ""
echo "Velinor assets are now available at:"
echo "  - /assets/backgrounds/Velhara_background_title(blur).png"
echo "  - /assets/npcs/velinor_eyesclosed2.png"
echo "  - /assets/overlays/velinor_title_transparent2.png"
