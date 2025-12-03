#!/usr/bin/env python3
"""Test script to verify caching is working correctly."""

import requests
import time
import json

def test_caching():
    """Test the caching implementation."""
    
    # Base URL
    base_url = "http://127.0.0.1:5000"
    
    # Test endpoints with their cache timeouts
    test_endpoints = [
        ("/api/user", "User Profile", 300),  # 5 minutes
        ("/api/top/tracks/medium_term", "Top Tracks", 900),  # 15 minutes
        ("/api/top/artists/medium_term", "Top Artists", 900),  # 15 minutes
        ("/api/wrapped-stats/medium_term", "Wrapped Stats", 1800),  # 30 minutes
    ]
    
    print("Testing Spotify API Caching Implementation")
    print("=" * 60)
    print("Note: You need to be logged in first at http://127.0.0.1:5000/login")
    print("=" * 60)
    
    for endpoint, name, cache_timeout in test_endpoints:
        print(f"\n📊 Testing: {name} ({endpoint})")
        print(f"   Cache timeout: {cache_timeout} seconds")
        print("-" * 40)
        
        try:
            # First request (should hit Spotify API)
            start_time = time.time()
            response1 = requests.get(base_url + endpoint, 
                                    cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
            first_request_time = time.time() - start_time
            
            if response1.status_code == 401:
                print("❌ Not authenticated. Please login first at http://127.0.0.1:5000/login")
                print("   Then copy your session cookie from browser DevTools")
                continue
            elif response1.status_code != 200:
                print(f"❌ Error: Status code {response1.status_code}")
                continue
            
            # Second request (should hit cache)
            start_time = time.time()
            response2 = requests.get(base_url + endpoint, 
                                    cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
            second_request_time = time.time() - start_time
            
            # Compare response times
            print(f"✅ First request (API):   {first_request_time:.3f} seconds")
            print(f"✅ Second request (Cache): {second_request_time:.3f} seconds")
            
            # Calculate speedup
            if first_request_time > 0:
                speedup = first_request_time / second_request_time
                print(f"🚀 Speed improvement: {speedup:.1f}x faster")
                
                if speedup > 5:
                    print("   ✨ Cache is working excellently!")
                elif speedup > 2:
                    print("   ✅ Cache is working well!")
                else:
                    print("   ⚠️  Cache may not be working as expected")
            
            # Verify data consistency
            if response1.text == response2.text:
                print("✅ Data consistency verified")
            else:
                print("⚠️  Warning: Cached data differs from original")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure Flask app is running.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test cache clearing endpoint
    print("\n" + "=" * 60)
    print("📊 Testing Cache Clearing")
    print("-" * 40)
    
    try:
        response = requests.post(base_url + "/api/clear-cache", 
                                cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
        
        if response.status_code == 200:
            print("✅ Cache cleared successfully")
        else:
            print(f"❌ Failed to clear cache: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\n📝 How to test properly:")
    print("1. Login at http://127.0.0.1:5000/login")
    print("2. Open browser DevTools → Application → Cookies")
    print("3. Copy the 'session' cookie value")
    print("4. Replace 'YOUR_SESSION_COOKIE_HERE' in this script with the actual value")
    print("5. Run this script again to see cache performance")
    print("\n💡 Tip: The second API call should be significantly faster due to caching!")

if __name__ == "__main__":
    test_caching()
