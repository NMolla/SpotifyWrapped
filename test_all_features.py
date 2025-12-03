#!/usr/bin/env python3
"""
Test script for all new Spotify Wrapped enhancements
"""

import requests
import json
import time

def test_all_features():
    """Test all new enhancement features."""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🎵 Testing All Spotify Wrapped Enhancements")
    print("=" * 60)
    print("Note: You need to be logged in first at http://127.0.0.1:5000/login")
    print("=" * 60)
    
    # Test endpoints
    tests = [
        {
            'name': 'Audio Features Analysis',
            'method': 'GET',
            'endpoint': '/api/audio-features/medium_term',
            'description': 'Analyzing music personality'
        },
        {
            'name': 'Recently Played',
            'method': 'GET',
            'endpoint': '/api/recently-played',
            'description': 'Getting listening patterns'
        },
        {
            'name': 'Recommendations',
            'method': 'GET',
            'endpoint': '/api/recommendations?time_range=medium_term',
            'description': 'Getting smart recommendations'
        },
        {
            'name': 'Music Evolution',
            'method': 'GET',
            'endpoint': '/api/music-evolution',
            'description': 'Tracking taste evolution'
        },
        {
            'name': 'Listening Statistics',
            'method': 'GET',
            'endpoint': '/api/listening-stats',
            'description': 'Getting comprehensive stats'
        }
    ]
    
    results = {}
    
    for test in tests:
        print(f"\n📊 Testing: {test['name']}")
        print(f"   {test['description']}...")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(base_url + test['endpoint'], 
                                       cookies={'session': 'YOUR_SESSION_COOKIE_HERE'})
            
            if response.status_code == 401:
                print("   ❌ Not authenticated. Please login first.")
                results[test['name']] = 'Not authenticated'
            elif response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                
                # Show sample data
                if test['name'] == 'Audio Features Analysis':
                    if 'listening_personality' in data:
                        personality = data['listening_personality']
                        print(f"      Personality: {personality['type']}")
                        print(f"      Description: {personality['description']}")
                        print(f"      Energy: {data['energy']['description']}")
                        print(f"      Mood: {data['valence']['description']}")
                
                elif test['name'] == 'Recently Played':
                    if 'patterns' in data:
                        patterns = data['patterns']
                        print(f"      Peak hour: {patterns.get('peak_listening_hour', 'N/A')}")
                        print(f"      Peak day: {patterns.get('peak_listening_day', 'N/A')}")
                        print(f"      Unique tracks: {patterns.get('total_unique_tracks', 0)}")
                
                elif test['name'] == 'Recommendations':
                    if 'recommendations' in data:
                        print(f"      Found {len(data['recommendations'])} recommendations")
                        if data['recommendations']:
                            first = data['recommendations'][0]
                            print(f"      Sample: {first['name']} by {', '.join(first['artists'])}")
                
                elif test['name'] == 'Music Evolution':
                    if 'trends' in data:
                        print(f"      Trends found: {len(data['trends'])} metrics")
                        for metric, trend in data['trends'].items():
                            print(f"      {metric}: {trend['direction']} by {trend['percentage']:.1f}%")
                
                elif test['name'] == 'Listening Statistics':
                    print(f"      Unique tracks: {data.get('total_unique_tracks', 0)}")
                    print(f"      Unique artists: {data.get('total_unique_artists', 0)}")
                    print(f"      Estimated minutes: {data.get('estimated_minutes', 0)}")
                    print(f"      Diversity score: {data.get('diversity_score', 0):.1f}%")
                
                results[test['name']] = 'Success'
                
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                results[test['name']] = f"Status {response.status_code}"
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[test['name']] = f"Error: {str(e)}"
    
    # Test playlist creation (requires authentication)
    print("\n📊 Testing: Playlist Creation")
    print("   Creating a test playlist...")
    
    try:
        response = requests.post(
            base_url + "/api/create-playlist",
            json={
                'type': 'top_tracks',
                'time_range': 'short_term',
                'name': 'Test Playlist from Enhanced Features',
                'description': 'Testing the new playlist creation feature',
                'public': False
            },
            cookies={'session': 'YOUR_SESSION_COOKIE_HERE'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Playlist created: {data['name']}")
                print(f"      Tracks added: {data['tracks_added']}")
                print(f"      URL: {data['playlist_url']}")
                results['Playlist Creation'] = 'Success'
        else:
            print(f"   ⚠️ Status: {response.status_code}")
            results['Playlist Creation'] = f"Status {response.status_code}"
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['Playlist Creation'] = f"Error: {str(e)}"
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    for test_name, result in results.items():
        status = "✅" if result == "Success" else "❌"
        print(f"   {status} {test_name}: {result}")
    
    success_count = sum(1 for r in results.values() if r == "Success")
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print(f"✨ {success_count}/{total_count} tests passed")
    
    print("\n💡 New Features Available:")
    print("1. 🎵 Audio Features - Analyze energy, mood, danceability")
    print("2. ⏰ Recently Played - See listening patterns and peak times")
    print("3. 📝 Playlist Creation - Auto-create playlists by mood")
    print("4. 🎯 Recommendations - Get personalized track suggestions")
    print("5. 📈 Music Evolution - Track taste changes over time")
    print("6. 📊 Deep Statistics - Comprehensive listening analytics")
    
    print("\n🌐 Access the Enhanced UI:")
    print("   Open: file:///Users/nmolla/PycharmProjects/SpotifyWrapped/wrapped_enhanced.html")
    print("\n📝 How to test properly:")
    print("1. Login at http://127.0.0.1:5000/login")
    print("2. Open browser DevTools → Application → Cookies")
    print("3. Copy the 'session' cookie value")
    print("4. Replace 'YOUR_SESSION_COOKIE_HERE' in this script")
    print("5. Run this script again")

if __name__ == "__main__":
    test_all_features()
