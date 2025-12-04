#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to fix database lock issues and clean up WAL files."""

import sqlite3
import os
import sys
import time

def fix_database_lock():
    """Fix database lock issues."""
    
    db_path = 'spotify_data.db'
    wal_path = 'spotify_data.db-wal'
    shm_path = 'spotify_data.db-shm'
    
    print("🔧 Fixing database lock issues...")
    print("-" * 40)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print(f"📁 Database found: {db_path}")
    print(f"   Size: {os.path.getsize(db_path) / 1024:.2f} KB")
    
    # Check for WAL files
    if os.path.exists(wal_path):
        print(f"📄 WAL file found: {wal_path}")
        print(f"   Size: {os.path.getsize(wal_path) / 1024:.2f} KB")
    
    if os.path.exists(shm_path):
        print(f"📄 SHM file found: {shm_path}")
        print(f"   Size: {os.path.getsize(shm_path) / 1024:.2f} KB")
    
    print("\n🔄 Attempting to checkpoint and clean up...")
    
    try:
        # Connect with longer timeout
        conn = sqlite3.connect(db_path, timeout=30.0)
        
        # Force checkpoint to merge WAL file
        cursor = conn.cursor()
        cursor.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        result = cursor.fetchone()
        print(f"✅ Checkpoint complete: {result}")
        
        # Optimize database
        cursor.execute('VACUUM')
        print("✅ Database optimized")
        
        # Close connection
        conn.close()
        print("✅ Connection closed properly")
        
        # Check if WAL files are removed
        time.sleep(1)
        
        if os.path.exists(wal_path):
            print(f"⚠️  WAL file still exists (size: {os.path.getsize(wal_path)} bytes)")
            if os.path.getsize(wal_path) == 0:
                print("   (Empty WAL file is normal)")
        else:
            print("✅ WAL file cleaned up")
            
        print("\n✅ Database lock issues should be resolved!")
        print("   You can now try syncing again.")
        
    except sqlite3.OperationalError as e:
        if 'database is locked' in str(e):
            print(f"\n❌ Database is still locked!")
            print("   Possible solutions:")
            print("   1. Close any other Python processes using the database")
            print("   2. Restart the Flask server")
            print("   3. If all else fails, restart your computer")
            
            # Try to find processes using the database
            print("\n📊 Checking for processes...")
            os.system(f"lsof {db_path} 2>/dev/null || echo '   No lsof available'")
            
        else:
            print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "=" * 40)
    print("Script complete!")

if __name__ == "__main__":
    fix_database_lock()
