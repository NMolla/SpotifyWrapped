#!/usr/bin/env python3
"""Test script to verify pagination is working correctly."""

import requests
import json

# Note: You'll need to have a valid session to test this
# First login through the browser at http://127.0.0.1:5000/login

def test_pagination():
    """Test the pagination endpoints."""
    
    # Base URL
    base_url = "http://127.0.0.1:5000"
    
    # Test endpoints
    endpoints = [
        "/api/top/tracks/medium_term",
        "/api/top/artists/medium_term",
        "/api/wrapped-stats/medium_term",
        "/api/spotify-wrapped/2025"
    ]
    
    print("Testing Spotify API Pagination Implementation")
    print("=" * 50)
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        print("-" * 30)
        
        try:
            response = requests.get(base_url + endpoint, 
                                   cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
            
            if response.status_code == 401:
                print("❌ Not authenticated. Please login first at http://127.0.0.1:5000/login")
                print("   Then copy your session cookie and update this script.")
            elif response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    print(f"✅ Success! Fetched {len(data)} total items")
                    if len(data) > 50:
                        print(f"   📊 Pagination working! (More than single page limit of 50)")
                    else:
                        print(f"   📊 Total items: {len(data)} (within single page)")
                elif isinstance(data, dict):
                    if 'total_tracks' in data:
                        print(f"✅ Success! Total tracks: {data['total_tracks']}, Total artists: {data['total_artists']}")
                    elif 'top_tracks' in data:
                        print(f"✅ Success! Wrapped data generated with {len(data['top_tracks'])} top tracks")
                    else:
                        print(f"✅ Success! Response received")
            else:
                print(f"❌ Error: Status code {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure Flask app is running.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nNote: To properly test pagination:")
    print("1. Login at http://127.0.0.1:5000/login")
    print("2. Check browser DevTools for session cookie")
    print("3. Update the 'YOUR_SESSION_COOKIE_HERE' in this script")
    print("4. Run this script again")

if __name__ == "__main__":
    test_pagination()
