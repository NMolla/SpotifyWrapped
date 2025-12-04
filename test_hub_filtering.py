#!/usr/bin/env python3
"""
Test script to verify time filtering works in the Wrapped Hub.
Run this after starting the Flask backend.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_time_filtering():
    """Test that different time ranges return different data."""
    
    # Test all three time ranges
    time_ranges = ['short_term', 'medium_term', 'long_term']
    results = {}
    
    print("Testing Wrapped Hub time filtering...")
    print("-" * 50)
    
    for time_range in time_ranges:
        print(f"\nTesting {time_range}...")
        
        # Test wrapped-stats endpoint
        try:
            response = requests.get(f"{BASE_URL}/api/wrapped-stats/{time_range}")
            if response.status_code == 200:
                data = response.json()
                results[time_range] = {
                    'total_minutes': data.get('total_minutes', 0),
                    'top_genre': data.get('top_genre', 'N/A'),
                    'total_artists': data.get('total_artists', 0),
                    'total_tracks': data.get('total_tracks', 0),
                    'top_track': data.get('top_track', {}).get('name', 'N/A'),
                    'top_artist': data.get('top_artist', {}).get('name', 'N/A')
                }
                print(f"  ✓ Stats fetched successfully")
                print(f"    - Top Track: {results[time_range]['top_track']}")
                print(f"    - Top Artist: {results[time_range]['top_artist']}")
                print(f"    - Total Minutes: {results[time_range]['total_minutes']}")
            else:
                print(f"  ✗ Failed to fetch stats: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Compare results
    print("\n" + "=" * 50)
    print("COMPARISON:")
    print("-" * 50)
    
    # Check if data differs between time ranges
    if len(results) == 3:
        short = results['short_term']
        medium = results['medium_term']
        long = results['long_term']
        
        # Usually, longer time ranges have more data
        if long['total_minutes'] >= medium['total_minutes'] >= short['total_minutes']:
            print("✅ Total minutes correctly increase with longer time ranges")
        else:
            print("⚠️  Total minutes don't follow expected pattern")
        
        # Check if top tracks/artists differ
        tracks_differ = not (short['top_track'] == medium['top_track'] == long['top_track'])
        artists_differ = not (short['top_artist'] == medium['top_artist'] == long['top_artist'])
        
        if tracks_differ:
            print("✅ Top tracks differ between time ranges")
        else:
            print("⚠️  Top tracks are the same across all time ranges")
            
        if artists_differ:
            print("✅ Top artists differ between time ranges")
        else:
            print("⚠️  Top artists are the same across all time ranges")
    
    print("\n" + "=" * 50)
    print("Test complete! The Hub should now filter data by time range.")
    print("\nTo verify in the UI:")
    print("1. Navigate to http://localhost:3000/hub")
    print("2. Change the time range dropdown")
    print("3. Observe that the Overview tab data updates")

if __name__ == "__main__":
    print("Note: Make sure the Flask backend is running on port 5000")
    print("and you are logged in via the web app first.\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/user")
        if response.status_code == 401:
            print("⚠️  Not authenticated. Please login via the web app first.")
        elif response.status_code == 200:
            print("✅ Backend is running and authenticated\n")
            test_time_filtering()
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except requests.ConnectionError:
        print("❌ Cannot connect to backend. Make sure Flask is running on port 5000.")
