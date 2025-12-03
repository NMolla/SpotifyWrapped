#!/usr/bin/env python3
"""Test script to verify the JSON storage implementation."""

import requests
import json
import time
import os

def test_json_storage():
    """Test the JSON storage implementation."""
    
    # Base URL
    base_url = "http://127.0.0.1:5000"
    
    print("Testing JSON Storage Implementation")
    print("=" * 60)
    print("Note: You need to be logged in first at http://127.0.0.1:5000/login")
    print("=" * 60)
    
    # Test sync endpoint
    print("\n📊 Testing Data Sync")
    print("-" * 40)
    
    try:
        # Trigger a sync
        response = requests.post(base_url + "/api/sync", 
                                json={'force': False},
                                cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
        
        if response.status_code == 401:
            print("❌ Not authenticated. Please login first at http://127.0.0.1:5000/login")
            print("   Then copy your session cookie from browser DevTools")
            return
        elif response.status_code == 200:
            sync_data = response.json()
            stats = sync_data.get('stats', {})
            print(f"✅ Sync successful!")
            print(f"   - Tracks synced: {stats.get('tracks_synced', 0)}")
            print(f"   - Artists synced: {stats.get('artists_synced', 0)}")
            print(f"   - Time ranges: {', '.join(stats.get('time_ranges', []))}")
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test sync status
    print("\n📊 Testing Sync Status")
    print("-" * 40)
    
    try:
        response = requests.get(base_url + "/api/sync-status",
                               cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ User ID: {status_data.get('user_id')}")
            
            storage_stats = status_data.get('storage_stats', {})
            print(f"   Storage stats:")
            for key, value in storage_stats.items():
                print(f"     - {key}: {value}")
            
            files = status_data.get('files', [])
            if files:
                print(f"   Files stored:")
                for file in files:
                    print(f"     - {file['filename']}: {file['size_kb']}KB, age: {file['age_days']} days, stale: {file['is_stale']}")
        else:
            print(f"❌ Error: Status code {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test storage stats
    print("\n📊 Testing Storage Statistics")
    print("-" * 40)
    
    try:
        response = requests.get(base_url + "/api/storage-stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Storage Statistics:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        else:
            print(f"❌ Error: Status code {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test data retrieval performance
    print("\n📊 Testing Data Retrieval Performance")
    print("-" * 40)
    
    endpoints = [
        "/api/top/tracks/medium_term",
        "/api/top/artists/medium_term",
        "/api/wrapped-stats/medium_term"
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(base_url + endpoint,
                                   cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {endpoint}: {len(data)} items in {request_time:.3f}s")
                else:
                    print(f"✅ {endpoint}: Retrieved in {request_time:.3f}s")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                if response.status_code == 404:
                    print(f"   (Data not synced yet)")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # Check storage directory
    print("\n📊 Storage Directory Information")
    print("-" * 40)
    
    storage_dir = os.path.join(os.path.dirname(__file__), 'spotify_data')
    if os.path.exists(storage_dir):
        print(f"✅ Storage directory exists: {storage_dir}")
        
        # Count users and files
        user_count = 0
        file_count = 0
        total_size = 0
        
        for user_dir in os.listdir(storage_dir):
            user_path = os.path.join(storage_dir, user_dir)
            if os.path.isdir(user_path):
                user_count += 1
                print(f"   User: {user_dir}")
                for file in os.listdir(user_path):
                    if file.endswith('.json'):
                        file_count += 1
                        file_path = os.path.join(user_path, file)
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        print(f"     - {file}: {file_size / 1024:.2f} KB")
        
        print(f"   Total: {user_count} users, {file_count} files, {total_size / 1024:.2f} KB")
    else:
        print(f"❌ Storage directory not found: {storage_dir}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\n📝 How to test properly:")
    print("1. Login at http://127.0.0.1:5000/login")
    print("2. Open browser DevTools → Application → Cookies")
    print("3. Copy the 'session' cookie value")
    print("4. Replace 'YOUR_SESSION_COOKIE_HERE' in this script")
    print("5. Run this script again to see JSON storage performance")
    print("\n💡 Benefits of JSON storage approach:")
    print("- Simple file-based storage (no database locks)")
    print("- Easy to inspect and debug (human-readable JSON)")
    print("- Portable and easy to backup")
    print("- No complex database setup required")
    print("- Each user's data is isolated in separate folders")

if __name__ == "__main__":
    test_json_storage()
