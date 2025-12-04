# 📜 Scripts Directory

Organized collection of utility scripts for the Spotify Wrapped project.

## 📁 Directory Structure

```
scripts/
├── dev/           # Development & server management
├── setup/         # Setup variations
└── utils/         # Maintenance & utilities
```

## 🚀 Development Scripts (`dev/`)

### Server Management
- **`run_backend.sh`** - Starts Flask backend server on port 5000
- **`run_frontend.sh`** - Starts React frontend server on port 3000
- **`run_dev_iterm.sh`** - Opens both servers in iTerm2 tabs
- **`run_dev_no_browser.sh`** - Starts servers without opening browser
- **`kill_servers.sh`** - Stops all running servers

## 🔧 Setup Scripts (`setup/`)

- **`setup_python313.sh`** - Special setup for Python 3.13 compatibility

## 🛠️ Utility Scripts (`utils/`)

- **`verify_structure.py`** - Validates project structure after refactoring
- **`cleanup_for_commit.sh`** - Cleans temporary files before git commit
- **`cleanup_storage.py`** - Manages and cleans user data storage
- **`fix_db_lock.py`** - Fixes SQLite database lock issues (legacy)

## 💡 Quick Usage

Most common tasks are available from project root:
```bash
# From project root:
./setup.sh                     # Main setup
./run_dev.sh                   # Start development

# Stop servers:
./scripts/dev/kill_servers.sh

# Verify structure:
python scripts/utils/verify_structure.py
```

## 📝 Notes

- Main entry points (`setup.sh`, `run_dev.sh`) remain at project root for discoverability
- All other scripts are organized here to reduce root directory clutter
- Scripts are organized by function: development, setup, or utility
