#!/bin/bash

echo "🧹 Cleaning up files for git commit..."
echo "======================================="
echo ""

# Files and directories that are already gitignored
echo "📝 The following files/directories are already gitignored:"
echo "  - .venv/ (virtual environment)"
echo "  - .env (sensitive credentials)"
echo "  - .cache (Spotify cache)"
echo "  - .idea/ (IDE settings)"
echo "  - data/ (user data storage)"
echo "  - frontend/node_modules/ (npm packages)"
echo ""

# Files to delete
echo "🗑️  Files that can be safely deleted:"
echo ""

# 1. Duplicate setup.sh in scripts folder
if [ -f "scripts/setup.sh" ]; then
    echo "  ✓ scripts/setup.sh (duplicate - use root setup.sh instead)"
    rm scripts/setup.sh
fi

# 2. Python cache files
if [ -d "backend/__pycache__" ]; then
    echo "  ✓ backend/__pycache__/ (Python cache)"
    rm -rf backend/__pycache__
fi

# 3. Old database file in data folder (if using JSON storage now)
if [ -f "data/spotify_data.db" ]; then
    echo "  ✓ data/spotify_data.db (old SQLite database - already gitignored)"
fi

# 4. Temporary verification script (optional - keep if you want)
if [ -f "verify_structure.py" ]; then
    echo "  ? verify_structure.py (optional - useful for testing but not required)"
fi

# 5. Migration checklist (optional - keep for reference)
if [ -f "MIGRATION_CHECKLIST.md" ]; then
    echo "  ? MIGRATION_CHECKLIST.md (optional - keep for migration reference)"
fi

echo ""
echo "📋 Recommended files to KEEP and commit:"
echo "  ✅ README.md (main documentation)"
echo "  ✅ setup.sh (main setup script)"
echo "  ✅ run_*.sh (convenience scripts)"
echo "  ✅ .env.example (template for others)"
echo "  ✅ .gitignore (important!)"
echo "  ✅ backend/ (all application code)"
echo "  ✅ frontend/src/ (React source)"
echo "  ✅ frontend/public/ (static assets)"
echo "  ✅ frontend/package*.json (dependencies)"
echo "  ✅ frontend/*.config.js (configs)"
echo "  ✅ tests/ (all test files)"
echo "  ✅ docs/ (all documentation)"
echo "  ✅ scripts/cleanup_storage.py"
echo "  ✅ scripts/fix_db_lock.py"
echo ""

echo "🔍 Optional files (you decide):"
echo "  • verify_structure.py - Helpful for testing structure"
echo "  • MIGRATION_CHECKLIST.md - Good reference for the refactoring"
echo "  • docs/REFACTORING_SUMMARY.md - Detailed refactoring documentation"
echo ""

echo "💡 To see what will be committed:"
echo "  git status"
echo ""
echo "💡 To see ignored files:"
echo "  git status --ignored"
echo ""

# Clean Python cache everywhere
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name ".DS_Store" -delete 2>/dev/null

echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "  1. Review with: git status"
echo "  2. Add files: git add ."
echo "  3. Commit: git commit -m 'Refactor: Reorganize project structure'"
