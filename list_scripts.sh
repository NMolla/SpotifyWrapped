#!/bin/bash
# List all available scripts with descriptions

echo "🎵 Spotify Wrapped - Available Scripts"
echo "======================================"
echo ""

echo "📍 Main Scripts (at root):"
echo "  ./setup.sh           - Initial project setup"
echo "  ./run_dev.sh         - Start both servers in Terminal tabs"
echo ""

echo "🚀 Development Scripts (scripts/dev/):"
echo "  run_backend.sh       - Start Flask backend only"
echo "  run_frontend.sh      - Start React frontend only"
echo "  run_dev_iterm.sh     - Start servers in iTerm2 tabs"
echo "  run_dev_no_browser.sh- Start servers without browser"
echo "  kill_servers.sh      - Stop all running servers"
echo ""

echo "🔧 Setup Scripts (scripts/setup/):"
echo "  setup_python313.sh   - Setup for Python 3.13+ compatibility"
echo ""

echo "🛠️  Utility Scripts (scripts/utils/):"
echo "  verify_structure.py  - Verify project structure"
echo "  cleanup_for_commit.sh- Clean files before git commit"
echo "  cleanup_storage.py   - Manage user data storage"
echo "  fix_db_lock.py      - Fix database locks (legacy)"
echo ""

echo "💡 Quick Commands:"
echo "  Start dev:    ./run_dev.sh"
echo "  Stop all:     ./scripts/dev/kill_servers.sh"
echo "  Verify:       python scripts/utils/verify_structure.py"
