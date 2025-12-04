#!/bin/bash
# Script to migrate to ultra-minimal setup with dev.sh

echo "🎯 Migrating to Ultra-Minimal Setup"
echo "==================================="
echo ""
echo "This will consolidate all scripts into the single dev.sh command."
echo ""

# Files that can be removed (replaced by dev.sh)
OLD_FILES=(
    "run_dev.sh"
    "setup.sh"
    "setup_python313.sh"
    "kill_servers.sh"
    "list_scripts.sh"
    "scripts/dev/run_backend.sh"
    "scripts/dev/run_frontend.sh"
    "scripts/dev/run_dev_iterm.sh"
    "scripts/dev/run_dev_no_browser.sh"
    "scripts/dev/kill_servers.sh"
    "scripts/setup/setup_python313.sh"
)

# Files to keep
KEEP_FILES=(
    "dev.sh"                           # Main unified script
    "scripts/utils/cleanup_storage.py" # Data management
    "scripts/utils/verify_structure.py" # Structure verification
)

echo "📋 Files that will be REMOVED (replaced by dev.sh):"
echo ""
for file in "${OLD_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ❌ $file"
    fi
done

echo ""
echo "✅ Files that will be KEPT:"
echo ""
for file in "${KEEP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    fi
done

echo ""
echo "📝 New workflow will be:"
echo "  ./dev.sh setup    # Initial setup"
echo "  ./dev.sh start    # Start development"
echo "  ./dev.sh stop     # Stop servers"
echo "  ./dev.sh status   # Check status"
echo "  ./dev.sh help     # See all commands"
echo ""

read -p "Continue with migration? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🗑️  Removing old scripts..."
    
    for file in "${OLD_FILES[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "  Removed: $file"
        fi
    done
    
    # Clean up empty directories
    if [ -d "scripts/dev" ]; then
        rmdir scripts/dev 2>/dev/null && echo "  Removed: scripts/dev/"
    fi
    if [ -d "scripts/setup" ]; then
        rmdir scripts/setup 2>/dev/null && echo "  Removed: scripts/setup/"
    fi
    
    # Remove scripts/README.md if exists
    if [ -f "scripts/README.md" ]; then
        rm scripts/README.md
        echo "  Removed: scripts/README.md"
    fi
    
    # Check if scripts/utils has files
    if [ -d "scripts/utils" ]; then
        utils_count=$(ls scripts/utils | wc -l)
        if [ $utils_count -eq 0 ]; then
            rmdir scripts/utils 2>/dev/null
            rmdir scripts 2>/dev/null
            echo "  Removed: empty scripts directory"
        else
            echo ""
            echo "📁 Keeping scripts/utils/ with:"
            ls scripts/utils/ | while read file; do
                echo "    - $file"
            done
        fi
    fi
    
    echo ""
    echo "✨ Migration complete!"
    echo ""
    echo "🚀 Your new ultra-minimal setup:"
    echo "   Main script: ./dev.sh"
    echo "   Utils:       scripts/utils/*.py"
    echo ""
    echo "Try it now:"
    echo "   ./dev.sh help"
    
    # Clean myself up
    echo ""
    echo "🧹 Removing migration script..."
    rm "$0"
else
    echo "Migration cancelled."
fi
