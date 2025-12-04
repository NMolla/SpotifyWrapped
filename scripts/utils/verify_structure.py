#!/usr/bin/env python3
"""
Verify the refactored project structure is working correctly.
"""

import os
import sys
import json
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_directory(path, name):
    """Check if a directory exists."""
    if os.path.exists(path):
        print(f"{GREEN}✓{RESET} {name} directory exists: {path}")
        return True
    else:
        print(f"{RED}✗{RESET} {name} directory missing: {path}")
        return False

def check_file(path, name):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"{GREEN}✓{RESET} {name} exists: {os.path.basename(path)}")
        return True
    else:
        print(f"{RED}✗{RESET} {name} missing: {os.path.basename(path)}")
        return False

def verify_imports():
    """Verify that Python imports work correctly."""
    try:
        # Add backend to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Try importing modules
        import json_storage
        print(f"{GREEN}✓{RESET} Backend imports working")
        
        # Verify storage path
        expected_data_path = os.path.join(os.path.dirname(__file__), 'data')
        actual_data_path = json_storage.STORAGE_DIR
        
        if os.path.normpath(expected_data_path) == os.path.normpath(actual_data_path):
            print(f"{GREEN}✓{RESET} Storage path correctly configured: {actual_data_path}")
        else:
            print(f"{YELLOW}⚠{RESET} Storage path mismatch:")
            print(f"    Expected: {expected_data_path}")
            print(f"    Actual: {actual_data_path}")
        
        return True
    except ImportError as e:
        print(f"{RED}✗{RESET} Import error: {e}")
        return False

def main():
    """Main verification function."""
    print(f"\n{BLUE}🔍 Verifying Spotify Wrapped Project Structure{RESET}")
    print("=" * 60)
    
    root_dir = os.path.dirname(__file__)
    all_good = True
    
    # Check directories
    print(f"\n{BLUE}📁 Checking directories:{RESET}")
    directories = {
        'backend': 'backend',
        'frontend': 'frontend',
        'frontend/src': 'frontend/src',
        'frontend/src/components': 'frontend/src/components',
        'frontend/public': 'frontend/public',
        'tests': 'tests',
        'docs': 'docs',
        'scripts': 'scripts',
        'data': 'data',
        'config': 'config'
    }
    
    for name, path in directories.items():
        full_path = os.path.join(root_dir, path)
        if not check_directory(full_path, name):
            all_good = False
    
    # Check critical files
    print(f"\n{BLUE}📄 Checking critical files:{RESET}")
    files = {
        'Flask app': 'backend/app.py',
        'JSON storage': 'backend/json_storage.py',
        'Requirements': 'backend/requirements.txt',
        'React app': 'frontend/src/App.js',
        'Package.json': 'frontend/package.json',
        'Environment template': '.env.example',
        'Setup script': 'setup.sh',
        'Backend runner': 'run_backend.sh',
        'Frontend runner': 'run_frontend.sh',
        'Dev runner': 'run_dev.sh'
    }
    
    for name, path in files.items():
        full_path = os.path.join(root_dir, path)
        if not check_file(full_path, name):
            all_good = False
    
    # Check Python imports
    print(f"\n{BLUE}🐍 Checking Python imports:{RESET}")
    verify_imports()
    
    # Check environment file
    print(f"\n{BLUE}🔐 Checking environment:{RESET}")
    env_file = os.path.join(root_dir, '.env')
    if os.path.exists(env_file):
        print(f"{GREEN}✓{RESET} Environment file exists")
        # Check if it has required variables
        with open(env_file, 'r') as f:
            content = f.read()
            required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
            missing_vars = []
            for var in required_vars:
                if var not in content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"{YELLOW}⚠{RESET} Missing environment variables: {', '.join(missing_vars)}")
                print(f"    Please add these to your .env file")
            else:
                print(f"{GREEN}✓{RESET} All required environment variables present")
    else:
        print(f"{YELLOW}⚠{RESET} No .env file found - run ./setup.sh to create one")
    
    # Summary
    print(f"\n{BLUE}📊 Summary:{RESET}")
    print("=" * 60)
    
    if all_good:
        print(f"{GREEN}✅ Project structure is properly configured!{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print("1. Run ./setup.sh if you haven't already")
        print("2. Configure your .env file with Spotify credentials")
        print("3. Run ./run_dev.sh to start the application")
    else:
        print(f"{RED}❌ Some issues found with the project structure{RESET}")
        print("Please fix the issues above and run this script again")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
