#!/bin/bash
# Sync parallel folders: velinor (Python engine) ↔ velinor-web (Next.js frontend)
# Usage: cd velinor-web; bash sync-parallel.sh

set -e

VELINOR_ROOT="../velinor"
WEB_ROOT="."

echo ""
echo "=== PARALLEL FOLDER SYNCHRONIZATION ===" 
echo "Source (Engine):  $VELINOR_ROOT"
echo "Target (Web):     $WEB_ROOT"
echo ""

# Verify both folders exist
if [ ! -d "$VELINOR_ROOT" ]; then
    echo "ERROR: velinor folder not found at $VELINOR_ROOT"
    exit 1
fi

if [ ! -d "$WEB_ROOT" ]; then
    echo "ERROR: velinor-web folder not found at $WEB_ROOT"
    exit 1
fi

# Track stats
FILES_SYNCED=0
FILES_SKIPPED=0
ERRORS=0

# ============================================================================
# PART 1: Sync Data Files (JSON)
# ============================================================================

echo "PART 1: Syncing Data Files (JSON)"
echo "---"

# Ensure data directory exists
mkdir -p "$WEB_ROOT/src/data"

for filename in "npc_profiles.json" "influence_map.json"; do
    SRC_PATH="$VELINOR_ROOT/data/$filename"
    DST_PATH="$WEB_ROOT/src/data/$filename"

    if [ -f "$SRC_PATH" ]; then
        if [ -f "$DST_PATH" ]; then
            if cmp -s "$SRC_PATH" "$DST_PATH"; then
                echo "  [SKIP] $filename (no changes)"
                ((FILES_SKIPPED++))
            else
                cp "$SRC_PATH" "$DST_PATH"
                echo "  [SYNC] $filename"
                ((FILES_SYNCED++))
            fi
        else
            cp "$SRC_PATH" "$DST_PATH"
            echo "  [SYNC] $filename (new)"
            ((FILES_SYNCED++))
        fi
    else
        echo "  [WARN] Source not found: $SRC_PATH"
        ((ERRORS++))
    fi
done

# ============================================================================
# PART 2: Sync Image Assets (Backgrounds, NPCs, Overlays)
# ============================================================================

echo ""
echo "PART 2: Syncing Image Assets"
echo "---"

# Helper function to sync directory
sync_asset_directory() {
    local source_dir="$1"
    local dest_dir="$2"
    local label="$3"

    if [ ! -d "$source_dir" ]; then
        echo "  [WARN] Source directory not found: $source_dir"
        return
    fi

    # Create destination if needed
    mkdir -p "$dest_dir"

    # Count PNG files
    local source_count=$(find "$source_dir" -maxdepth 1 -name "*.png" -type f | wc -l)

    if [ "$source_count" -eq 0 ]; then
        echo "  [SKIP] $label - no PNG files found"
        return
    fi

    # Sync files
    local sync_count=0
    for file in "$source_dir"/*.png; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            dest_file="$dest_dir/$filename"

            if [ -f "$dest_file" ]; then
                if cmp -s "$file" "$dest_file"; then
                    continue
                fi
            fi

            cp "$file" "$dest_file"
            ((sync_count++))
        fi
    done

    if [ "$sync_count" -gt 0 ]; then
        echo "  [SYNC] $label ($sync_count/$source_count files)"
        ((FILES_SYNCED += sync_count))
    else
        echo "  [SKIP] $label (all current)"
        ((FILES_SKIPPED += source_count))
    fi
}

# Sync each asset type
sync_asset_directory "$VELINOR_ROOT/backgrounds" "$WEB_ROOT/public/assets/backgrounds" "Backgrounds"
sync_asset_directory "$VELINOR_ROOT/npcs" "$WEB_ROOT/public/assets/npcs" "NPCs"
sync_asset_directory "$VELINOR_ROOT/overlays" "$WEB_ROOT/public/assets/overlays" "Overlays"

# ============================================================================
# PART 3: Verification
# ============================================================================

echo ""
echo "PART 3: Verification"
echo "---"

VERIFY_OK=true

# Check JSON files
for filepath in "src/data/npc_profiles.json" "src/data/influence_map.json"; do
    if [ -f "$WEB_ROOT/$filepath" ]; then
        echo "  [OK] $(basename $filepath) exists"
    else
        echo "  [ERROR] $(basename $filepath) missing"
        VERIFY_OK=false
    fi
done

# Check asset directories
for dir in "public/assets/backgrounds" "public/assets/npcs" "public/assets/overlays"; do
    if [ -d "$WEB_ROOT/$dir" ]; then
        file_count=$(find "$WEB_ROOT/$dir" -maxdepth 1 -name "*.png" -type f | wc -l)
        if [ "$file_count" -gt 0 ]; then
            echo "  [OK] $(basename $dir) ($file_count files)"
        else
            echo "  [WARN] $(basename $dir) empty"
        fi
    else
        echo "  [ERROR] $(basename $dir) directory missing"
        VERIFY_OK=false
    fi
done

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "=== SYNC SUMMARY ===" 
echo "Files synced:  $FILES_SYNCED"
echo "Files skipped: $FILES_SKIPPED"
echo "Errors:        $ERRORS"
echo ""

if [ "$VERIFY_OK" = true ]; then
    echo "Status: READY - All folders properly synced!"
    echo ""
    echo "Next steps:"
    echo "  - Run: npm run dev"
    echo "  - Visit: http://localhost:3000"
    echo "  - Verify all assets load correctly"
    echo ""
else
    echo "Status: WARNING - Some files may be missing"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check both folders exist"
    echo "  - Verify file permissions"
    echo "  - Re-run sync script"
    echo ""
    exit 1
fi

echo "Sync completed at $(date '+%Y-%m-%d %H:%M:%S')"
