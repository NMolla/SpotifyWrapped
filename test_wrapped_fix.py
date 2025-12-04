#!/usr/bin/env python3
"""
Test script to verify the 2025 Wrapped cache_key fix
"""

import requests
from datetime import datetime

def test_wrapped_endpoint():
    """Test the Spotify Wrapped endpoint for cache_key error."""
    
    base_url = "http://127.0.0.1:5000"
    current_year = datetime.now().year
    
    print(f"🧪 Testing {current_year} Wrapped Endpoint")
    print("=" * 50)
    
    # Test the endpoint
    try:
        # You'll need to replace this with your actual session cookie
        response = requests.get(
            f"{base_url}/api/spotify-wrapped/{current_year}",
            cookies={'session': 'YOUR_SESSION_COOKIE_HERE'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! No cache_key error")
            print(f"   Year: {data.get('year')}")
            print(f"   Top Genre: {data.get('top_genre')}")
            if 'top_5_tracks' in data:
                print(f"   Top Track: {data['top_5_tracks'][0]['name'] if data['top_5_tracks'] else 'None'}")
            if 'top_5_artists' in data:
                print(f"   Top Artist: {data['top_5_artists'][0]['name'] if data['top_5_artists'] else 'None'}")
        elif response.status_code == 401:
            print("❌ Not authenticated. Please login first at http://127.0.0.1:5000/login")
            print("   Then copy your session cookie from browser DevTools")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the Flask server is running:")
        print("   source .venv/bin/activate")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📝 How to test properly:")
    print("1. Start server: source .venv/bin/activate && python app.py")
    print("2. Login at: http://127.0.0.1:5000/login")
    print("3. Get session cookie from browser DevTools")
    print("4. Replace 'YOUR_SESSION_COOKIE_HERE' in this script")
    print("5. Run this script again")

if __name__ == "__main__":
    test_wrapped_endpoint()
