#!/usr/bin/env python3
"""Test script to verify the SQLite database implementation."""

import requests
import json
import time
import os
import sqlite3

def test_database_implementation():
    """Test the database implementation."""
    
    # Base URL
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Spotify Database Implementation")
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
            if sync_data.get('success'):
                stats = sync_data.get('stats', {})
                print(f"✅ Sync successful!")
                print(f"   - Tracks synced: {stats.get('tracks_synced', 0)}")
                print(f"   - Artists synced: {stats.get('artists_synced', 0)}")
                print(f"   - Time ranges: {', '.join(stats.get('time_ranges', []))}")
            else:
                print(f"❌ Sync failed: {sync_data}")
        else:
            print(f"❌ Error: Status code {response.status_code}")
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
            print(f"   Database stats:")
            db_stats = status_data.get('database_stats', {})
            for key, value in db_stats.items():
                print(f"     - {key}: {value}")
            
            sync_status = status_data.get('sync_status', [])
            if sync_status:
                print(f"   Sync status by time range:")
                for item in sync_status:
                    print(f"     - {item['data_type']} ({item['time_range']}): {item['status']} - {item['total_items']} items")
        else:
            print(f"❌ Error: Status code {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test database stats
    print("\n📊 Testing Database Statistics")
    print("-" * 40)
    
    try:
        response = requests.get(base_url + "/api/database-stats",
                               cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Database Statistics:")
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
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # Check database file
    print("\n📊 Database File Information")
    print("-" * 40)
    
    db_path = os.path.join(os.path.dirname(__file__), 'spotify_data.db')
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"✅ Database file exists: {db_path}")
        print(f"   Size: {size_mb:.2f} MB")
        
        # Check tables
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   Tables: {', '.join([t[0] for t in tables])}")
            conn.close()
        except Exception as e:
            print(f"   ❌ Error checking tables: {e}")
    else:
        print(f"❌ Database file not found: {db_path}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\n📝 How to test properly:")
    print("1. Login at http://127.0.0.1:5000/login")
    print("2. Open browser DevTools → Application → Cookies")
    print("3. Copy the 'session' cookie value")
    print("4. Replace 'YOUR_SESSION_COOKIE_HERE' in this script")
    print("5. Run this script again to see database performance")
    print("\n💡 Benefits of database approach:")
    print("- All data stored locally for instant access")
    print("- Complex analytics queries possible")
    print("- Reduces API calls significantly")
    print("- Data persists between sessions")
    print("- Auto-refresh when data is stale (>7 days)")

if __name__ == "__main__":
    test_database_implementation()
