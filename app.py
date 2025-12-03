import os
import json
import base64
import secrets
from io import BytesIO
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, Any, Optional, List
from flask import Flask, redirect, request, jsonify, session, send_file
from flask_cors import CORS
from flask_caching import Cache
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageDraw, ImageFont
import requests
import hashlib
import json_storage as storage  # Import our JSON storage module
import statistics
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
try:
    import numpy as np
except ImportError:
    np = None  # Handle if numpy not installed

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Configure cache (now used for session data and temporary caching)
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use simple in-memory cache
    'CACHE_DEFAULT_TIMEOUT': 900  # 15 minutes default
})

# Initialize storage
storage.ensure_storage_dir()

# Spotify OAuth Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:5000/callback')
SCOPE = 'user-top-read user-read-private user-read-email user-read-recently-played playlist-modify-public playlist-modify-private user-follow-read'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=None
)

def get_spotify_client():
    """Get authenticated Spotify client from session."""
    token_info = session.get('token_info')
    if not token_info:
        return None
    
    # Check if token needs refresh
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    
    return spotipy.Spotify(auth=token_info['access_token'])

def get_user_id():
    """Get current user ID for cache key generation."""
    sp = get_spotify_client()
    if sp:
        try:
            user = sp.current_user()
            return user.get('id', 'unknown')
        except:
            pass
    return 'unknown'

def generate_cache_key(*args):
    """Generate a unique cache key based on user and arguments."""
    user_id = get_user_id()
    # Create a hash of all arguments including user ID
    key_parts = [str(user_id)] + [str(arg) for arg in args]
    key_string = '_'.join(key_parts)
    # Return a shorter hash to avoid extremely long cache keys
    return hashlib.md5(key_string.encode()).hexdigest()

def fetch_all_spotify_items(sp, fetch_func, **kwargs):
    """Fetch all items from Spotify API with pagination - NO LIMITS.
    
    Args:
        sp: Spotify client instance
        fetch_func: Function to call (e.g., sp.current_user_top_tracks)
        **kwargs: Arguments to pass to the function (e.g., time_range)
    
    Returns:
        List of ALL items fetched (no artificial limits)
    """
    all_items = []
    limit = 50  # Maximum allowed by Spotify API for most endpoints
    offset = 0
    
    # Debug logging
    print(f"Fetching items with params: {kwargs}")
    
    while True:
        # Call the function with current offset and limit
        results = fetch_func(limit=limit, offset=offset, **kwargs)
        
        # Add items to our collection
        items = results.get('items', [])
        all_items.extend(items)
        
        # Check if we've fetched all items
        # If 'next' is None or we got fewer items than requested, we're done
        if not results.get('next') or len(items) < limit:
            break
        
        # Move to next page
        offset += limit
        
        # NO LIMIT - Continue fetching until Spotify says we're done
        # The API itself will stop returning results when there's no more data
    
    print(f"Fetched {len(all_items)} total items for {kwargs.get('time_range', 'default')}")  # Log for debugging
    return all_items

# Audio Features Analysis Functions
def get_audio_features(sp: spotipy.Spotify, track_ids: List[str]) -> List[Dict[str, Any]]:
    """Get audio features for multiple tracks."""
    all_features = []
    
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i+100]
        try:
            features = sp.audio_features(batch)
            all_features.extend([f for f in features if f])
        except:
            pass
    
    return all_features

def analyze_music_characteristics(sp: spotipy.Spotify, tracks: List[Dict]) -> Dict[str, Any]:
    """Analyze musical characteristics of user's top tracks."""
    
    track_ids = [track.get('id') for track in tracks if track.get('id')]
    
    if not track_ids:
        return {}
    
    features = get_audio_features(sp, track_ids[:50])  # Analyze top 50
    
    if not features:
        return {}
    
    analysis = {
        'energy': {
            'average': statistics.mean([f['energy'] for f in features]),
            'description': get_energy_description(statistics.mean([f['energy'] for f in features]))
        },
        'danceability': {
            'average': statistics.mean([f['danceability'] for f in features]),
            'description': get_danceability_description(statistics.mean([f['danceability'] for f in features]))
        },
        'valence': {
            'average': statistics.mean([f['valence'] for f in features]),
            'description': get_mood_description(statistics.mean([f['valence'] for f in features]))
        },
        'tempo': {
            'average': statistics.mean([f['tempo'] for f in features]),
            'description': get_tempo_description(statistics.mean([f['tempo'] for f in features]))
        }
    }
    
    analysis['musical_profile'] = generate_musical_profile(analysis)
    analysis['listening_personality'] = get_listening_personality(analysis)
    
    return analysis

def get_energy_description(energy: float) -> str:
    if energy < 0.3:
        return "🧘 Very Chill"
    elif energy < 0.5:
        return "😌 Mellow"
    elif energy < 0.7:
        return "🎵 Balanced"
    elif energy < 0.85:
        return "⚡ Energetic"
    else:
        return "🔥 High Energy"

def get_danceability_description(danceability: float) -> str:
    if danceability < 0.3:
        return "🪑 Not for dancing"
    elif danceability < 0.5:
        return "🚶 Light groove"
    elif danceability < 0.7:
        return "🕺 Groovy"
    elif danceability < 0.85:
        return "💃 Very danceable"
    else:
        return "🕺💃 Dance machine"

def get_mood_description(valence: float) -> str:
    if valence < 0.2:
        return "😢 Melancholic"
    elif valence < 0.4:
        return "🌧️ Somewhat sad"
    elif valence < 0.6:
        return "😐 Neutral mood"
    elif valence < 0.8:
        return "😊 Upbeat"
    else:
        return "😄 Very happy"

def get_tempo_description(tempo: float) -> str:
    if tempo < 80:
        return "🐌 Slow tempo"
    elif tempo < 110:
        return "🚶 Moderate tempo"
    elif tempo < 130:
        return "🏃 Upbeat tempo"
    elif tempo < 150:
        return "🏃‍♀️ Fast tempo"
    else:
        return "🚀 Very fast"

def generate_musical_profile(analysis: Dict[str, Any]) -> str:
    energy = analysis['energy']['average']
    valence = analysis['valence']['average']
    danceability = analysis['danceability']['average']
    
    profiles = []
    
    if energy > 0.7 and valence > 0.7:
        profiles.append("🎉 Party Enthusiast")
    elif energy > 0.7 and valence < 0.3:
        profiles.append("🎸 Intense & Emotional")
    elif energy < 0.3 and valence > 0.7:
        profiles.append("☀️ Peaceful & Happy")
    elif energy < 0.3 and valence < 0.3:
        profiles.append("🌙 Deep & Introspective")
    
    if danceability > 0.75:
        profiles.append("💃 Dance Floor Regular")
    elif danceability < 0.25:
        profiles.append("🎧 Deep Listener")
    
    return " | ".join(profiles) if profiles else "🎵 Eclectic Listener"

def get_listening_personality(analysis: Dict[str, Any]) -> Dict[str, str]:
    energy = analysis['energy']['average']
    valence = analysis['valence']['average']
    dance = analysis['danceability']['average']
    
    personality = {
        'type': '',
        'description': '',
        'emoji': ''
    }
    
    if energy > 0.6 and valence > 0.6 and dance > 0.6:
        personality['type'] = "The Life of the Party"
        personality['description'] = "You love upbeat, energetic music that gets everyone moving."
        personality['emoji'] = "🎉"
    elif energy < 0.4 and valence < 0.4:
        personality['type'] = "The Deep Thinker"
        personality['description'] = "You prefer introspective, emotional music that speaks to the soul."
        personality['emoji'] = "🤔"
    elif dance > 0.7:
        personality['type'] = "The Rhythm Seeker"
        personality['description'] = "The beat is what moves you."
        personality['emoji'] = "🕺"
    elif valence > 0.7:
        personality['type'] = "The Optimist"
        personality['description'] = "Your music choices reflect your positive outlook."
        personality['emoji'] = "😊"
    else:
        personality['type'] = "The Explorer"
        personality['description'] = "Your taste is diverse and adventurous."
        personality['emoji'] = "🌎"
    
    return personality

def sync_user_data(user_id: str, force: bool = False) -> Dict[str, Any]:
    """Sync all user data from Spotify API to JSON storage.
    
    Args:
        user_id: The user's Spotify ID
        force: Force sync even if data is fresh
    
    Returns:
        Dictionary with sync status and statistics
    """
    sp = get_spotify_client()
    if not sp:
        return {'error': 'Not authenticated'}
    
    sync_stats = {
        'tracks_synced': 0,
        'artists_synced': 0,
        'time_ranges': [],
        'forced': force
    }
    
    time_ranges = ['short_term', 'medium_term', 'long_term']
    
    try:
        # Sync user profile
        user_data = sp.current_user()
        storage.save_user_profile(user_id, user_data)
        
        for time_range in time_ranges:
            # Check if sync is needed
            tracks_stale = force or storage.is_data_stale(user_id, 'top_tracks', time_range, days=7)
            artists_stale = force or storage.is_data_stale(user_id, 'top_artists', time_range, days=7)
            
            if tracks_stale:
                # Sync top tracks
                all_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=time_range)
                storage.save_top_tracks(user_id, all_tracks, time_range)
                sync_stats['tracks_synced'] += len(all_tracks)
            
            if artists_stale:
                # Sync top artists
                all_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=time_range)
                storage.save_top_artists(user_id, all_artists, time_range)
                sync_stats['artists_synced'] += len(all_artists)
            
            if tracks_stale or artists_stale:
                sync_stats['time_ranges'].append(time_range)
        
        # Sync recently played tracks
        try:
            recent_items = sp.current_user_recently_played(limit=50)
            if recent_items and 'items' in recent_items:
                storage.save_data(user_id, 'recently_played', recent_items['items'])
                sync_stats['recently_played'] = len(recent_items['items'])
        except Exception as e:
            print(f"Error syncing recently played: {e}")
        
        # Sync followed artists
        try:
            followed = sp.current_user_followed_artists(limit=50)
            if followed and 'artists' in followed:
                storage.save_data(user_id, 'followed_artists', followed['artists']['items'])
                sync_stats['followed_artists'] = len(followed['artists']['items'])
        except Exception as e:
            print(f"Error syncing followed artists: {e}")
        
        sync_stats['sync_time'] = datetime.now().isoformat()
        return sync_stats
        
    except Exception as e:
        return {'error': f'Storage error: {str(e)}'}

def ensure_data_freshness(user_id: str, data_type: str, time_range: str) -> bool:
    """Ensure data is fresh, syncing if necessary.
    
    Returns:
        True if data is available (either was fresh or successfully synced)
    """
    storage_type = 'top_tracks' if data_type == 'tracks' else 'top_artists'
    
    # Check if data exists at all or is stale
    existing_data = storage.load_top_tracks(user_id, time_range) if data_type == 'tracks' else storage.load_top_artists(user_id, time_range)
    
    if existing_data is None or storage.is_data_stale(user_id, storage_type, time_range, days=7):
        sp = get_spotify_client()
        if not sp:
            return False
        
        try:
            print(f"Syncing {data_type} for time_range: {time_range}")
            if data_type == 'tracks':
                all_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=time_range)
                storage.save_top_tracks(user_id, all_tracks, time_range)
                print(f"Saved {len(all_tracks)} tracks for {time_range}")
            elif data_type == 'artists':
                all_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=time_range)
                storage.save_top_artists(user_id, all_artists, time_range)
                print(f"Saved {len(all_artists)} artists for {time_range}")
            return True
        except Exception as e:
            print(f"Error syncing {data_type} for {time_range}: {e}")
            return False
    return True

@app.route('/')
def index():
    """Check if user is authenticated."""
    if session.get('token_info'):
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@app.route('/sync-ui')
def sync_ui():
    """Serve the sync UI page."""
    if not session.get('token_info'):
        return redirect('/login')
    
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Data Sync Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 36px;
            margin-bottom: 10px;
            color: #1a1a1a;
        }
        
        .header p {
            font-size: 18px;
            color: #546e7a;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card-title {
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .status-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 16px;
            border: 2px solid #e9ecef;
            transition: all 0.3s;
        }
        
        .status-item:hover {
            border-color: #1DB954;
            transform: translateY(-2px);
        }
        
        .status-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .status-title {
            font-size: 18px;
            font-weight: 600;
            color: #495057;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-badge.synced {
            background: #d4edda;
            color: #155724;
        }
        
        .status-badge.stale {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-badge.missing {
            background: #f8d7da;
            color: #721c24;
        }
        
        .status-badge.syncing {
            background: #cce5ff;
            color: #004085;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .status-details {
            font-size: 14px;
            color: #6c757d;
            line-height: 1.5;
        }
        
        .status-details div {
            margin-bottom: 4px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-primary {
            background: #1DB954;
            color: white;
        }
        
        .btn-primary:hover {
            background: #1ed760;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
            margin-left: 10px;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn:disabled {
            background: #dee2e6;
            color: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .alert {
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert.show {
            display: block;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .storage-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #1DB954;
        }
        
        .stat-label {
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            margin-top: 4px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .user-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #1DB954;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        
        .user-details h3 {
            color: #333;
            margin-bottom: 4px;
        }
        
        .user-details p {
            color: #6c757d;
            font-size: 14px;
        }
        
        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #1DB954;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 8px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Spotify Data Sync Manager</h1>
            <p>Manage and refresh your Spotify data</p>
        </div>
        
        <div id="alert" class="alert"></div>
        
        <div class="card">
            <div class="card-title">👤 User Profile</div>
            <div id="user-info" class="user-info">
                <div class="user-avatar" id="user-avatar">?</div>
                <div class="user-details">
                    <h3 id="user-name">Loading...</h3>
                    <p id="user-id">Fetching user data...</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">📊 Data Status</div>
            <div class="status-grid" id="status-grid">
                <!-- Status items will be populated here -->
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" onclick="syncAll()">
                    🔄 Sync All Data
                </button>
                <button class="btn btn-secondary" onclick="checkStatus()">
                    🔍 Refresh Status
                </button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">💾 Storage Statistics</div>
            <div class="storage-stats" id="storage-stats">
                <div class="stat-card">
                    <div class="stat-value" id="stat-users">0</div>
                    <div class="stat-label">Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="stat-files">0</div>
                    <div class="stat-label">Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="stat-size">0</div>
                    <div class="stat-label">Size (MB)</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">🛠️ Quick Actions</div>
            <div class="btn-group">
                <button class="btn btn-primary" onclick="syncTimeRange('short_term')">
                    Sync Short Term (4 weeks)
                </button>
                <button class="btn btn-primary" onclick="syncTimeRange('medium_term')">
                    Sync Medium Term (6 months)
                </button>
                <button class="btn btn-primary" onclick="syncTimeRange('long_term')">
                    Sync Long Term (All time)
                </button>
                <button class="btn btn-danger" onclick="clearCache()">
                    Clear Cache
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let currentUser = null;
        
        async function loadUserInfo() {
            try {
                const response = await fetch('/api/user');
                if (response.ok) {
                    const user = await response.json();
                    currentUser = user;
                    
                    document.getElementById('user-name').textContent = user.name || 'Spotify User';
                    document.getElementById('user-id').textContent = `ID: ${user.id || 'Unknown'}`;
                    
                    if (user.name) {
                        document.getElementById('user-avatar').textContent = user.name.charAt(0).toUpperCase();
                    }
                }
            } catch (error) {
                console.error('Error loading user info:', error);
            }
        }
        
        async function checkStatus() {
            try {
                showAlert('Checking data status...', 'info');
                const response = await fetch('/api/sync-status');
                
                if (!response.ok) {
                    throw new Error('Failed to fetch status');
                }
                
                const data = await response.json();
                displayStatus(data);
                updateStorageStats(data.storage_stats);
                showAlert('Status updated successfully', 'success');
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'error');
            }
        }
        
        function displayStatus(data) {
            const grid = document.getElementById('status-grid');
            const files = data.files || [];
            
            const timeRanges = [
                { id: 'short_term', name: 'Short Term', desc: 'Last 4 weeks' },
                { id: 'medium_term', name: 'Medium Term', desc: 'Last 6 months' },
                { id: 'long_term', name: 'Long Term', desc: 'All time' }
            ];
            
            grid.innerHTML = '';
            
            timeRanges.forEach(range => {
                const trackFile = files.find(f => f.filename === `top_tracks_${range.id}.json`);
                const artistFile = files.find(f => f.filename === `top_artists_${range.id}.json`);
                
                let status = 'missing';
                let statusText = 'Not Synced';
                let details = '';
                
                if (trackFile && artistFile) {
                    const isStale = trackFile.is_stale || artistFile.is_stale;
                    status = isStale ? 'stale' : 'synced';
                    statusText = isStale ? 'Stale' : 'Synced';
                    
                    details = `
                        <div>📁 Tracks: ${trackFile.size_kb} KB</div>
                        <div>📁 Artists: ${artistFile.size_kb} KB</div>
                        <div>📅 Age: ${trackFile.age_days} days</div>
                    `;
                } else {
                    details = '<div>No data available</div>';
                }
                
                const item = document.createElement('div');
                item.className = 'status-item';
                item.innerHTML = `
                    <div class="status-header">
                        <div class="status-title">${range.name}</div>
                        <span class="status-badge ${status}">${statusText}</span>
                    </div>
                    <div class="status-details">
                        <div style="color: #6c757d; font-size: 13px; margin-bottom: 8px;">${range.desc}</div>
                        ${details}
                    </div>
                    <button class="btn btn-primary" style="margin-top: 12px; width: 100%;" 
                            onclick="syncTimeRange('${range.id}')">
                        Sync ${range.name}
                    </button>
                `;
                
                grid.appendChild(item);
            });
        }
        
        function updateStorageStats(stats) {
            if (stats) {
                document.getElementById('stat-users').textContent = stats.users || 0;
                document.getElementById('stat-files').textContent = stats.total_files || 0;
                document.getElementById('stat-size').textContent = stats.total_size_mb || 0;
            }
        }
        
        async function syncTimeRange(timeRange) {
            try {
                showAlert(`Syncing ${timeRange.replace('_', ' ')} data...`, 'info');
                
                // Update UI to show syncing
                const badges = document.querySelectorAll('.status-badge');
                badges.forEach(badge => {
                    if (badge.closest('.status-item').innerHTML.includes(timeRange)) {
                        badge.className = 'status-badge syncing';
                        badge.textContent = 'Syncing...';
                    }
                });
                
                const response = await fetch('/api/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ time_range: timeRange, force: true })
                });
                
                if (!response.ok) {
                    throw new Error('Sync failed');
                }
                
                const result = await response.json();
                showAlert(
                    `✅ Synced ${result.stats.tracks_synced} tracks and ${result.stats.artists_synced} artists for ${timeRange.replace('_', ' ')}`,
                    'success'
                );
                
                // Refresh status
                await checkStatus();
            } catch (error) {
                showAlert(`Error syncing: ${error.message}`, 'error');
                await checkStatus();
            }
        }
        
        async function syncAll() {
            try {
                showAlert('Syncing all data... This may take a moment.', 'info');
                
                const response = await fetch('/api/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ force: true })
                });
                
                if (!response.ok) {
                    throw new Error('Sync failed');
                }
                
                const result = await response.json();
                showAlert(
                    `✅ Successfully synced ${result.stats.tracks_synced} tracks and ${result.stats.artists_synced} artists`,
                    'success'
                );
                
                await checkStatus();
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'error');
            }
        }
        
        async function clearCache() {
            if (confirm('Are you sure you want to clear the cache?')) {
                try {
                    const response = await fetch('/api/clear-cache', { method: 'POST' });
                    
                    if (response.ok) {
                        showAlert('Cache cleared successfully', 'success');
                    } else {
                        throw new Error('Failed to clear cache');
                    }
                } catch (error) {
                    showAlert(`Error: ${error.message}`, 'error');
                }
            }
        }
        
        function showAlert(message, type = 'info') {
            const alert = document.getElementById('alert');
            alert.className = `alert alert-${type} show`;
            alert.textContent = message;
            
            if (type === 'success') {
                setTimeout(() => {
                    alert.className = 'alert';
                }, 5000);
            }
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', async () => {
            await loadUserInfo();
            await checkStatus();
        });
    </script>
</body>
</html>
    '''
    return html_content

@app.route('/login')
def login():
    """Redirect to Spotify authorization."""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback."""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        
        # Trigger initial sync in background (non-blocking)
        try:
            user_id = get_user_id()
            if user_id != 'unknown':
                # Check if this is a new user or data is stale
                if storage.is_data_stale(user_id, 'top_tracks', 'medium_term', days=1):
                    sync_user_data(user_id, force=False)
        except:
            pass  # Don't block login if sync fails
        
        # Redirect to frontend dashboard
        frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:3000')
        return redirect(f'{frontend_url}/dashboard')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Clear session and log out."""
    # Clear cache for this user before logging out
    try:
        user_id = get_user_id()
        if user_id != 'unknown':
            # Clear user-specific cache entries
            clear_user_cache()
    except:
        pass
    
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache_endpoint():
    """Clear cache for the current user."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        clear_user_cache()
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def clear_user_cache():
    """Clear all cache entries for the current user."""
    # Clear all cache entries (simple implementation)
    # In production, you might want to track user-specific keys
    cache.clear()

@app.route('/api/sync', methods=['POST', 'GET'])
def sync_data():
    """Sync user data from Spotify API to database."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        force = False
        specific_range = None
        
        if request.method == 'POST' and request.is_json:
            force = request.json.get('force', False)
            specific_range = request.json.get('time_range', None)
        
        # If specific range requested, only sync that
        if specific_range and specific_range in ['short_term', 'medium_term', 'long_term']:
            sync_stats = {
                'tracks_synced': 0,
                'artists_synced': 0,
                'time_ranges': [specific_range],
                'forced': force
            }
            
            # Force sync for the specific range
            all_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=specific_range)
            storage.save_top_tracks(user_id, all_tracks, specific_range)
            sync_stats['tracks_synced'] = len(all_tracks)
            
            all_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=specific_range)
            storage.save_top_artists(user_id, all_artists, specific_range)
            sync_stats['artists_synced'] = len(all_artists)
            
            sync_stats['sync_time'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'message': f'Data synchronized for {specific_range}',
                'stats': sync_stats
            })
        else:
            # Perform full sync
            sync_stats = sync_user_data(user_id, force=force)
            
            if 'error' in sync_stats:
                return jsonify(sync_stats), 500
            
            return jsonify({
                'success': True,
                'message': 'Data synchronized successfully',
                'stats': sync_stats
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync-status')
def sync_status():
    """Get synchronization status for all data types."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        files = storage.get_all_user_files(user_id)
        stats = storage.get_storage_stats()
        
        return jsonify({
            'user_id': user_id,
            'files': files,
            'storage_stats': stats,
            'refresh_threshold_days': 7
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/storage-stats')
def storage_stats():
    """Get storage statistics."""
    try:
        stats = storage.get_storage_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/check-data')
def debug_check_data():
    """Debug endpoint to check if data exists in storage."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        
        # Check what's in storage
        tracks_medium = storage.load_top_tracks(user_id, 'medium_term')
        artists_medium = storage.load_top_artists(user_id, 'medium_term')
        
        return jsonify({
            'user_id': user_id,
            'has_tracks': bool(tracks_medium),
            'track_count': len(tracks_medium) if tracks_medium else 0,
            'sample_track': tracks_medium[0] if tracks_medium else None,
            'has_artists': bool(artists_medium),
            'artist_count': len(artists_medium) if artists_medium else 0,
            'sample_artist': artists_medium[0] if artists_medium else None,
            'message': 'If counts are 0, please visit /api/sync to sync your data'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user')
def get_user():
    """Get current user profile."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user = sp.current_user()
        user_id = user.get('id')
        
        # Save user profile to storage
        storage.save_user_profile(user_id, user)
        
        # Check if this is first time or data is stale - trigger sync
        if storage.is_data_stale(user_id, 'top_tracks', 'medium_term', days=1):
            # Do a quick sync for medium_term only on first access
            try:
                all_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range='medium_term')
                all_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range='medium_term')
                storage.save_top_tracks(user_id, all_tracks, 'medium_term')
                storage.save_top_artists(user_id, all_artists, 'medium_term')
            except:
                pass  # Don't fail the user endpoint if sync fails
        
        user_data = {
            'name': user.get('display_name', 'Spotify User'),
            'email': user.get('email'),
            'image': user.get('images', [{}])[0].get('url') if user.get('images') else None,
            'id': user_id
        }
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top/<item_type>/<time_range>')
def get_top_items(item_type, time_range):
    """Get user's top tracks or artists from database."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if item_type not in ['tracks', 'artists']:
        return jsonify({'error': 'Invalid item type'}), 400
    
    if time_range not in ['short_term', 'medium_term', 'long_term']:
        return jsonify({'error': 'Invalid time range'}), 400
    
    try:
        user_id = get_user_id()
        
        # Ensure data is fresh (auto-syncs if stale)
        data_type = 'tracks' if item_type == 'tracks' else 'artists'
        if not ensure_data_freshness(user_id, data_type, time_range):
            return jsonify({'error': 'Failed to sync data'}), 500
        
        # Get data from storage
        if item_type == 'tracks':
            stored_items = storage.load_top_tracks(user_id, time_range)
            if not stored_items:
                return jsonify({'error': 'No data available. Please sync first.'}), 404
            
            items = []
            for track in stored_items:
                # Extract artist names from track data
                artists_list = [artist['name'] for artist in track.get('artists', [])]
                
                items.append({
                    'id': track.get('id', ''),
                    'name': track.get('name', 'Unknown'),
                    'artist': artists_list[0] if artists_list else 'Unknown',
                    'artists': artists_list,
                    'album': track.get('album', {}).get('name', 'Unknown'),
                    'image': track.get('album', {}).get('images', [{}])[0].get('url', '') if track.get('album', {}).get('images') else '',
                    'duration_ms': track.get('duration_ms', 0),
                    'popularity': track.get('popularity', 0),
                    'preview_url': track.get('preview_url', '')
                })
        else:
            stored_items = storage.load_top_artists(user_id, time_range)
            if not stored_items:
                return jsonify({'error': 'No data available. Please sync first.'}), 404
            
            items = []
            for artist in stored_items:
                items.append({
                    'id': artist.get('id', ''),
                    'name': artist.get('name', 'Unknown'),
                    'genres': artist.get('genres', []),
                    'image': artist.get('images', [{}])[0].get('url', '') if artist.get('images') else '',
                    'popularity': artist.get('popularity', 0),
                    'followers': artist.get('followers', {}).get('total', 0)
                })
        
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wrapped-stats/<time_range>')
def get_wrapped_stats(time_range):
    """Get comprehensive wrapped statistics from storage."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if time_range not in ['short_term', 'medium_term', 'long_term']:
        return jsonify({'error': 'Invalid time range'}), 400
    
    try:
        user_id = get_user_id()
        
        # Ensure data is fresh
        ensure_data_freshness(user_id, 'tracks', time_range)
        ensure_data_freshness(user_id, 'artists', time_range)
        
        # Get data from storage
        all_top_tracks = storage.load_top_tracks(user_id, time_range) or []
        all_top_artists = storage.load_top_artists(user_id, time_range) or []
        
        # Calculate genre statistics
        all_genres = []
        for artist in all_top_artists:
            all_genres.extend(artist.get('genres', []))
        
        genre_counts = Counter(all_genres)
        top_genres = genre_counts.most_common(10)
        
        # Calculate listening stats
        total_duration = sum(track.get('duration_ms', 0) for track in all_top_tracks)
        avg_popularity = sum(track.get('popularity', 0) for track in all_top_tracks) / len(all_top_tracks) if all_top_tracks else 0
        
        # Determine music characteristics
        characteristics = analyze_music_taste(all_top_tracks, all_top_artists, genre_counts)
        
        stats = {
            'top_artist': {
                'name': all_top_artists[0]['name'] if all_top_artists else 'Unknown',
                'image': all_top_artists[0]['images'][0]['url'] if all_top_artists and all_top_artists[0].get('images') else None,
                'genres': all_top_artists[0]['genres'][:3] if all_top_artists else []
            },
            'top_track': {
                'name': all_top_tracks[0]['name'] if all_top_tracks else 'Unknown',
                'artist': all_top_tracks[0]['artists'][0]['name'] if all_top_tracks and all_top_tracks[0].get('artists') else 'Unknown',
                'image': all_top_tracks[0]['album']['images'][0]['url'] if all_top_tracks and all_top_tracks[0].get('album', {}).get('images') else None
            },
            'top_genre': top_genres[0][0] if top_genres else 'Unknown',
            'top_genres': [{'genre': genre, 'count': count} for genre, count in top_genres],
            'total_minutes': total_duration // 60000,
            'avg_popularity': round(avg_popularity, 1),
            'total_artists': len(all_top_artists),
            'total_tracks': len(all_top_tracks),
            'characteristics': characteristics,
            'time_period': get_time_period_label(time_range)
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_music_taste(tracks, artists, genre_counts):
    """Analyze user's music taste characteristics."""
    characteristics = []
    
    # Determine dominant music era
    if genre_counts:
        top_genre = max(genre_counts, key=genre_counts.get)
        if any(g in top_genre for g in ['indie', 'alternative']):
            characteristics.append('Indie Explorer')
        elif any(g in top_genre for g in ['pop', 'dance']):
            characteristics.append('Pop Enthusiast')
        elif any(g in top_genre for g in ['rap', 'hip hop']):
            characteristics.append('Hip-Hop Head')
        elif any(g in top_genre for g in ['rock', 'metal']):
            characteristics.append('Rock Devotee')
        elif any(g in top_genre for g in ['electronic', 'edm']):
            characteristics.append('Electronic Vibes')
    
    # Check for diversity
    if len(genre_counts) > 15:
        characteristics.append('Genre Adventurer')
    elif len(genre_counts) < 5:
        characteristics.append('Loyal Listener')
    
    # Check popularity
    avg_pop = sum(t['popularity'] for t in tracks) / len(tracks) if tracks else 0
    if avg_pop > 70:
        characteristics.append('Mainstream Maven')
    elif avg_pop < 40:
        characteristics.append('Underground Explorer')
    
    return characteristics[:3]  # Return top 3 characteristics

def get_time_period_label(time_range):
    """Convert time range to readable label."""
    labels = {
        'short_term': 'Last 4 Weeks',
        'medium_term': 'Last 6 Months',
        'long_term': 'All Time'
    }
    return labels.get(time_range, time_range)

@app.route('/api/spotify-wrapped/<int:year>')
def spotify_wrapped(year):
    """Generate official Spotify Wrapped style data from database."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Use medium_term for current year (approximates Jan-Oct)
        # Use long_term for previous years
        time_range = 'medium_term' if year == current_year else 'long_term'
        
        # Ensure data is fresh
        ensure_data_freshness(user_id, 'tracks', time_range)
        ensure_data_freshness(user_id, 'artists', time_range)
        
        # Get all data from storage
        all_tracks = storage.load_top_tracks(user_id, time_range) or []
        all_artists = storage.load_top_artists(user_id, time_range) or []
        
        # Get just top 5 for display (like official Wrapped)
        top_5_tracks = all_tracks[:5]
        top_5_artists = all_artists[:5]
        
        # Calculate total listening time (estimated from all tracks)
        total_ms = sum(track['duration_ms'] for track in all_tracks)
        total_minutes = total_ms // 60000
        total_hours = total_minutes // 60
        
        # Get all genres from all artists for better analysis
        all_genres = []
        genre_artists_map = {}
        for artist in all_artists:
            for genre in artist['genres']:
                all_genres.append(genre)
                if genre not in genre_artists_map:
                    genre_artists_map[genre] = []
                genre_artists_map[genre].append(artist['name'])
        
        # Calculate genre statistics
        genre_counts = Counter(all_genres)
        top_genres = genre_counts.most_common(5)
        total_genre_counts = sum(genre_counts.values())
        
        # Calculate genre percentages
        genre_percentages = [
            {
                'genre': genre,
                'percentage': round((count / total_genre_counts) * 100, 1),
                'count': count
            }
            for genre, count in top_genres
        ]
        
        # Create Audio Aura (color palette based on top genres)
        audio_aura = generate_audio_aura(top_genres)
        
        # Determine listening personality
        listening_personality = determine_listening_personality(
            all_tracks,
            all_artists,
            genre_counts
        )
        
        # Calculate music discovery stats
        unique_artists = len(all_artists)
        unique_genres = len(set(all_genres))
        avg_track_popularity = sum(t['popularity'] for t in all_tracks) / len(all_tracks) if all_tracks else 0
        
        # Format top 5 tracks with play count estimates
        formatted_tracks = []
        for i, track in enumerate(top_5_tracks, 1):
            formatted_tracks.append({
                'position': i,
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'duration_ms': track['duration_ms'],
                'preview_url': track['preview_url']
            })
        
        # Format top 5 artists
        formatted_artists = []
        for i, artist in enumerate(top_5_artists, 1):
            formatted_artists.append({
                'position': i,
                'name': artist['name'],
                'image': artist['images'][0]['url'] if artist['images'] else None,
                'genres': artist['genres'][:2],  # Top 2 genres
                'followers': artist['followers']['total']
            })
        
        # Check if user is in top percentage of any artist's listeners
        top_artist_status = None
        if top_5_artists:
            # This is estimated - actual data not available via API
            top_artist_status = {
                'artist': top_5_artists[0]['name'],
                'percentage': 0.5  # Estimate top 0.5%
            }
        
        wrapped_data = {
            'year': year,
            'time_period': f"January - {'October' if year == current_year else 'December'} {year}",
            'top_tracks': formatted_tracks,
            'top_artists': formatted_artists,
            'total_minutes_listened': total_minutes,
            'total_hours_listened': total_hours,
            'top_genres': genre_percentages,
            'audio_aura': audio_aura,
            'listening_personality': listening_personality,
            'music_discovery': {
                'unique_artists': unique_artists,
                'unique_genres': unique_genres,
                'avg_popularity': round(avg_track_popularity, 1)
            },
            'top_artist_status': top_artist_status,
            'top_song': formatted_tracks[0] if formatted_tracks else None,
            'top_artist': formatted_artists[0] if formatted_artists else None,
            'generated_at': datetime.now().isoformat()
        }
        
        # Cache for 1 hour (wrapped data is expensive to compute)
        cache.set(cache_key, wrapped_data, timeout=3600)
        
        return jsonify(wrapped_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_audio_aura(top_genres):
    """Generate Audio Aura color palette based on genres."""
    # Map genres to colors (similar to Spotify's approach)
    genre_colors = {
        'pop': {'name': 'Pink Pop', 'hex': '#FF69B4', 'gradient': 'from-pink-400 to-pink-600'},
        'rock': {'name': 'Electric Blue', 'hex': '#00CED1', 'gradient': 'from-cyan-400 to-blue-600'},
        'hip hop': {'name': 'Purple Vibes', 'hex': '#9370DB', 'gradient': 'from-purple-400 to-purple-700'},
        'rap': {'name': 'Purple Vibes', 'hex': '#9370DB', 'gradient': 'from-purple-400 to-purple-700'},
        'electronic': {'name': 'Neon Green', 'hex': '#39FF14', 'gradient': 'from-green-400 to-emerald-600'},
        'edm': {'name': 'Neon Green', 'hex': '#39FF14', 'gradient': 'from-green-400 to-emerald-600'},
        'indie': {'name': 'Sunset Orange', 'hex': '#FF8C00', 'gradient': 'from-orange-400 to-orange-600'},
        'alternative': {'name': 'Sunset Orange', 'hex': '#FF8C00', 'gradient': 'from-orange-400 to-orange-600'},
        'jazz': {'name': 'Golden Hour', 'hex': '#FFD700', 'gradient': 'from-yellow-400 to-amber-600'},
        'classical': {'name': 'Royal Purple', 'hex': '#6A0DAD', 'gradient': 'from-purple-600 to-purple-900'},
        'metal': {'name': 'Crimson Red', 'hex': '#DC143C', 'gradient': 'from-red-600 to-red-900'},
        'country': {'name': 'Desert Sand', 'hex': '#F4A460', 'gradient': 'from-orange-300 to-orange-500'},
        'r&b': {'name': 'Velvet Blue', 'hex': '#4B0082', 'gradient': 'from-indigo-500 to-indigo-700'},
        'soul': {'name': 'Velvet Blue', 'hex': '#4B0082', 'gradient': 'from-indigo-500 to-indigo-700'},
        'latin': {'name': 'Tropical Teal', 'hex': '#00CED1', 'gradient': 'from-teal-400 to-cyan-600'}
    }
    
    aura_colors = []
    default_color = {'name': 'Cosmic Purple', 'hex': '#8A2BE2', 'gradient': 'from-violet-500 to-purple-600'}
    
    for genre, count in top_genres[:3]:  # Top 3 genres for aura
        # Find matching color
        color_found = False
        for key, color in genre_colors.items():
            if key in genre.lower():
                aura_colors.append(color)
                color_found = True
                break
        
        if not color_found:
            aura_colors.append(default_color)
    
    # Ensure we have at least 3 colors
    while len(aura_colors) < 3:
        aura_colors.append(default_color)
    
    return aura_colors[:3]

def determine_listening_personality(tracks, artists, genre_counts):
    """Determine user's listening personality based on their music data."""
    personalities = []
    
    # Calculate various metrics
    avg_popularity = sum(t['popularity'] for t in tracks) / len(tracks) if tracks else 0
    genre_diversity = len(genre_counts)
    
    # Time-based personality traits
    track_durations = [t['duration_ms'] for t in tracks]
    avg_duration = sum(track_durations) / len(track_durations) if track_durations else 0
    
    # Main personality type based on top genre
    if genre_counts:
        top_genre = max(genre_counts, key=genre_counts.get)
        
        # Genre-based personalities
        if any(g in top_genre for g in ['indie', 'alternative']):
            personalities.append({
                'type': 'The Indie Explorer',
                'description': 'You venture off the beaten path to discover hidden gems',
                'icon': '🎸'
            })
        elif any(g in top_genre for g in ['pop', 'dance']):
            personalities.append({
                'type': 'The Pop Perfectionist', 
                'description': 'You know every word to every chart-topper',
                'icon': '✨'
            })
        elif any(g in top_genre for g in ['rap', 'hip hop']):
            personalities.append({
                'type': 'The Beat Seeker',
                'description': 'You live for the rhythm and the bars',
                'icon': '🎤'
            })
        elif any(g in top_genre for g in ['rock', 'metal']):
            personalities.append({
                'type': 'The Rock Revolutionary',
                'description': 'You prefer your music loud and legendary',
                'icon': '🤘'
            })
        elif any(g in top_genre for g in ['electronic', 'edm', 'house']):
            personalities.append({
                'type': 'The Electronic Enthusiast',
                'description': 'You ride the waves of synthesized soundscapes',
                'icon': '🎛️'
            })
        elif any(g in top_genre for g in ['jazz', 'classical']):
            personalities.append({
                'type': 'The Sophisticated Listener',
                'description': 'You appreciate the finer nuances of musical composition',
                'icon': '🎼'
            })
        else:
            personalities.append({
                'type': 'The Eclectic Collector',
                'description': 'Your taste knows no boundaries',
                'icon': '🎵'
            })
    
    # Secondary traits based on behavior
    if genre_diversity > 20:
        personalities.append({
            'type': 'Genre Hopper',
            'description': f'You explored {genre_diversity} different genres this year',
            'icon': '🌈'
        })
    elif genre_diversity < 5:
        personalities.append({
            'type': 'Loyalist',
            'description': 'You know what you like and stick to it',
            'icon': '💯'
        })
    
    if avg_popularity > 75:
        personalities.append({
            'type': 'Trendsetter',
            'description': 'You\'re always on top of what\'s hot',
            'icon': '🔥'
        })
    elif avg_popularity < 40:
        personalities.append({
            'type': 'Underground Scout',
            'description': 'You find the best music before it\'s cool',
            'icon': '🔍'
        })
    
    if avg_duration > 240000:  # > 4 minutes average
        personalities.append({
            'type': 'Deep Diver',
            'description': 'You prefer longer, more complex compositions',
            'icon': '🌊'
        })
    elif avg_duration < 180000:  # < 3 minutes average
        personalities.append({
            'type': 'Quick Hitter',
            'description': 'You like your music punchy and to the point',
            'icon': '⚡'
        })
    
    return personalities[:3]  # Return top 3 personality traits

@app.route('/api/generate-wrapped-card')
def generate_wrapped_card():
    """Generate a shareable wrapped summary card."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get user data
        user = sp.current_user()
        user_name = user.get('display_name', 'Spotify User')
        
        # Get stats
        time_range = request.args.get('time_range', 'medium_term')
        
        # Generate cache keys for tracks and artists
        tracks_cache_key = generate_cache_key('wrapped_card_tracks', time_range)
        artists_cache_key = generate_cache_key('wrapped_card_artists', time_range)
        
        # Try to get from cache
        all_tracks = cache.get(tracks_cache_key)
        all_artists = cache.get(artists_cache_key)
        
        # If not in cache, fetch from Spotify
        if all_tracks is None:
            all_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=time_range)
            cache.set(tracks_cache_key, all_tracks, timeout=900)  # Cache for 15 minutes
        
        if all_artists is None:
            all_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=time_range)
            cache.set(artists_cache_key, all_artists, timeout=900)  # Cache for 15 minutes
        
        # Create wrapped card image with top 5 items
        img = create_wrapped_image(user_name, all_tracks[:5], all_artists[:5], time_range)
        
        # Convert to bytes
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='spotify-wrapped.png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_wrapped_image(user_name, tracks, artists, time_range):
    """Create a beautiful wrapped summary image."""
    # Create gradient background
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create gradient
    for y in range(height):
        color_r = int(29 + (y/height) * (147-29))  # From #1DB954 to #191414
        color_g = int(185 - (y/height) * (165))
        color_b = int(84 - (y/height) * (64))
        draw.rectangle([(0, y), (width, y+1)], fill=(color_r, color_g, color_b))
    
    # Add overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # Try to use a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add content
    y_position = 100
    
    # Title
    draw.text((width/2, y_position), f"{user_name}'s", anchor="mt", fill='white', font=header_font)
    y_position += 80
    current_year = datetime.now().year
    draw.text((width/2, y_position), f"{current_year} WRAPPED", anchor="mt", fill='#1DB954', font=title_font)
    y_position += 120
    
    # Time period
    period_label = get_time_period_label(time_range)
    draw.text((width/2, y_position), period_label.upper(), anchor="mt", fill='#B3B3B3', font=small_font)
    y_position += 100
    
    # Top Artists Section
    draw.text((width/2, y_position), "TOP ARTISTS", anchor="mt", fill='#1DB954', font=header_font)
    y_position += 70
    
    for i, artist in enumerate(artists[:5], 1):
        draw.text((100, y_position), f"{i}. {artist['name'][:40]}", fill='white', font=body_font)
        y_position += 60
    
    y_position += 60
    
    # Top Tracks Section
    draw.text((width/2, y_position), "TOP TRACKS", anchor="mt", fill='#1DB954', font=header_font)
    y_position += 70
    
    for i, track in enumerate(tracks[:5], 1):
        track_name = track['name'][:30]
        artist_name = track['artists'][0]['name'][:25] if track['artists'] else 'Unknown'
        draw.text((100, y_position), f"{i}. {track_name}", fill='white', font=body_font)
        y_position += 45
        draw.text((120, y_position), f"   by {artist_name}", fill='#B3B3B3', font=small_font)
        y_position += 55
    
    # Footer
    y_position = height - 150
    draw.text((width/2, y_position), "Generated with Spotify Wrapped Dashboard", anchor="mt", fill='#B3B3B3', font=small_font)
    y_position += 50
    current_year = datetime.now().year
    draw.text((width/2, y_position), f"© {current_year}", anchor="mt", fill='#B3B3B3', font=small_font)
    
    return img

# New Enhancement Endpoints

@app.route('/api/audio-features/<time_range>')
def get_audio_features_analysis(time_range):
    """Get audio features analysis for user's top tracks."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if time_range not in ['short_term', 'medium_term', 'long_term']:
        return jsonify({'error': 'Invalid time range'}), 400
    
    try:
        user_id = get_user_id()
        
        # Get top tracks
        tracks = storage.load_top_tracks(user_id, time_range)
        
        if not tracks:
            # Try to sync if no data
            ensure_data_freshness(user_id, 'tracks', time_range)
            tracks = storage.load_top_tracks(user_id, time_range)
        
        if not tracks:
            return jsonify({'error': 'No tracks found. Please sync first.'}), 404
        
        # Analyze audio characteristics
        analysis = analyze_music_characteristics(sp, tracks)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recently-played')
def get_recently_played():
    """Get user's recently played tracks."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        
        # Load from storage first
        recent = storage.load_data(user_id, 'recently_played')
        
        if not recent or storage.is_data_stale(user_id, 'recently_played', None, days=1):
            # Fetch fresh data
            recent_items = sp.current_user_recently_played(limit=50)
            if recent_items and 'items' in recent_items:
                storage.save_data(user_id, 'recently_played', recent_items['items'])
                recent = recent_items['items']
        
        if isinstance(recent, dict) and 'data' in recent:
            recent = recent['data']
        
        # Analyze listening patterns
        patterns = analyze_listening_patterns(recent) if recent else {}
        
        return jsonify({
            'items': recent,
            'patterns': patterns
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_listening_patterns(recent_items):
    """Analyze patterns in recently played tracks."""
    if not recent_items:
        return {}
    
    # Time of day analysis
    hours = {}
    days = {}
    repeated_tracks = {}
    
    for item in recent_items:
        if 'played_at' in item:
            timestamp = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
            hour = timestamp.hour
            day = timestamp.strftime('%A')
            
            hours[hour] = hours.get(hour, 0) + 1
            days[day] = days.get(day, 0) + 1
        
        # Track repeats
        track_id = item.get('track', {}).get('id')
        if track_id:
            repeated_tracks[track_id] = repeated_tracks.get(track_id, 0) + 1
    
    # Find peak listening time
    peak_hour = max(hours.keys(), key=hours.get) if hours else None
    peak_day = max(days.keys(), key=days.get) if days else None
    
    # Most repeated tracks
    most_repeated = [k for k, v in repeated_tracks.items() if v > 1]
    
    return {
        'peak_listening_hour': peak_hour,
        'peak_listening_day': peak_day,
        'hourly_distribution': hours,
        'daily_distribution': days,
        'repeated_tracks_count': len(most_repeated),
        'total_unique_tracks': len(repeated_tracks)
    }

@app.route('/api/create-playlist', methods=['POST'])
def create_playlist():
    """Create a playlist from user's top tracks."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        data = request.json
        
        playlist_type = data.get('type', 'top_tracks')
        time_range = data.get('time_range', 'medium_term')
        name = data.get('name', None)
        description = data.get('description', None)
        
        if playlist_type == 'top_tracks':
            # Create playlist from top tracks
            tracks = storage.load_top_tracks(user_id, time_range)
            
            if not tracks:
                return jsonify({'error': 'No tracks found'}), 404
            
            # Default name
            if not name:
                period_label = get_time_period_label(time_range)
                name = f"My Top Tracks - {period_label}"
            
            if not description:
                description = f"My top {len(tracks[:50])} tracks from Spotify Wrapped"
            
            # Create playlist
            playlist = sp.user_playlist_create(
                user=user_id,
                name=name,
                public=data.get('public', True),
                description=description
            )
            
            # Add tracks (max 100 at a time)
            track_uris = [f"spotify:track:{track['id']}" for track in tracks[:50] if track.get('id')]
            
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i:i+100]
                sp.playlist_add_items(playlist['id'], batch)
            
            return jsonify({
                'success': True,
                'playlist_id': playlist['id'],
                'playlist_url': playlist['external_urls']['spotify'],
                'tracks_added': len(track_uris),
                'name': name
            })
        
        elif playlist_type == 'mood':
            # Create mood-based playlist
            tracks = storage.load_top_tracks(user_id, time_range)
            if not tracks:
                return jsonify({'error': 'No tracks found'}), 404
            
            mood = data.get('mood', 'happy')
            mood_tracks = create_mood_playlist(sp, tracks, mood)
            
            if not name:
                name = f"Mood: {mood.title()}"
            
            # Create playlist
            playlist = sp.user_playlist_create(
                user=user_id,
                name=name,
                public=data.get('public', True),
                description=f"Tracks matching your {mood} mood"
            )
            
            # Add tracks
            track_uris = [f"spotify:track:{track['id']}" for track in mood_tracks if track.get('id')]
            if track_uris:
                sp.playlist_add_items(playlist['id'], track_uris)
            
            return jsonify({
                'success': True,
                'playlist_id': playlist['id'],
                'playlist_url': playlist['external_urls']['spotify'],
                'tracks_added': len(track_uris),
                'name': name,
                'mood': mood
            })
        
        elif playlist_type == 'discovery':
            # Create discovery playlist based on recommendations
            return create_discovery_playlist(sp, user_id, data)
        
        else:
            return jsonify({'error': 'Invalid playlist type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_mood_playlist(sp, tracks, mood):
    """Filter tracks by mood using audio features."""
    track_ids = [t['id'] for t in tracks[:50] if t.get('id')]
    
    if not track_ids:
        return []
    
    features = get_audio_features(sp, track_ids)
    mood_tracks = []
    
    for track, feature in zip(tracks[:50], features):
        if feature:
            if mood == 'happy' and feature['valence'] > 0.6:
                mood_tracks.append(track)
            elif mood == 'sad' and feature['valence'] < 0.4:
                mood_tracks.append(track)
            elif mood == 'energetic' and feature['energy'] > 0.7:
                mood_tracks.append(track)
            elif mood == 'chill' and feature['energy'] < 0.4:
                mood_tracks.append(track)
            elif mood == 'dance' and feature['danceability'] > 0.7:
                mood_tracks.append(track)
    
    return mood_tracks[:30]  # Limit to 30 tracks

def create_discovery_playlist(sp, user_id, data):
    """Create a discovery playlist based on recommendations."""
    # Get top tracks and artists for seeds
    tracks = storage.load_top_tracks(user_id, 'short_term') or []
    artists = storage.load_top_artists(user_id, 'short_term') or []
    
    if not tracks and not artists:
        return jsonify({'error': 'Not enough data for recommendations'}), 404
    
    # Get seeds (max 5 total)
    seed_tracks = [t['id'] for t in tracks[:2] if t.get('id')]
    seed_artists = [a['id'] for a in artists[:2] if a.get('id')]
    seed_genres = []
    
    # Get a genre
    for artist in artists:
        if artist.get('genres'):
            seed_genres.append(artist['genres'][0])
            break
    
    # Get recommendations
    try:
        recommendations = sp.recommendations(
            seed_artists=seed_artists[:2],
            seed_tracks=seed_tracks[:2],
            seed_genres=seed_genres[:1],
            limit=30
        )
        
        # Create playlist
        name = data.get('name', f"Discover New Music - {datetime.now().strftime('%B %Y')}")
        playlist = sp.user_playlist_create(
            user=user_id,
            name=name,
            public=data.get('public', True),
            description="Fresh recommendations based on your favorite music"
        )
        
        # Add tracks
        track_uris = [f"spotify:track:{track['id']}" for track in recommendations['tracks']]
        if track_uris:
            sp.playlist_add_items(playlist['id'], track_uris)
        
        return jsonify({
            'success': True,
            'playlist_id': playlist['id'],
            'playlist_url': playlist['external_urls']['spotify'],
            'tracks_added': len(track_uris),
            'name': name,
            'type': 'discovery'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500

@app.route('/api/recommendations')
def get_recommendations():
    """Get track recommendations based on user's taste."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        time_range = request.args.get('time_range', 'medium_term')
        
        # Get top items for seeds
        tracks = storage.load_top_tracks(user_id, time_range) or []
        artists = storage.load_top_artists(user_id, time_range) or []
        
        if not tracks and not artists:
            return jsonify({'error': 'Not enough data for recommendations'}), 404
        
        # Prepare seeds
        seed_tracks = [t['id'] for t in tracks[:2] if t.get('id')]
        seed_artists = [a['id'] for a in artists[:2] if a.get('id')]
        seed_genres = []
        
        for artist in artists:
            if artist.get('genres') and len(seed_genres) < 1:
                seed_genres.append(artist['genres'][0])
        
        # Get recommendations
        recommendations = sp.recommendations(
            seed_artists=seed_artists,
            seed_tracks=seed_tracks,
            seed_genres=seed_genres,
            limit=20
        )
        
        # Format response
        rec_tracks = []
        for track in recommendations['tracks']:
            rec_tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artists': [a['name'] for a in track['artists']],
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track.get('preview_url'),
                'uri': track['uri']
            })
        
        return jsonify({
            'recommendations': rec_tracks,
            'seeds_used': {
                'tracks': len(seed_tracks),
                'artists': len(seed_artists),
                'genres': len(seed_genres)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music-evolution')
def get_music_evolution():
    """Track how user's music taste has evolved over time."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        
        evolution = {
            'short_term': {},
            'medium_term': {},
            'long_term': {}
        }
        
        for time_range in evolution.keys():
            tracks = storage.load_top_tracks(user_id, time_range) or []
            artists = storage.load_top_artists(user_id, time_range) or []
            
            if tracks:
                # Get audio features for analysis
                track_ids = [t['id'] for t in tracks[:20] if t.get('id')]
                if track_ids:
                    features = get_audio_features(sp, track_ids)
                    if features:
                        evolution[time_range] = {
                            'avg_energy': statistics.mean([f['energy'] for f in features]),
                            'avg_valence': statistics.mean([f['valence'] for f in features]),
                            'avg_danceability': statistics.mean([f['danceability'] for f in features]),
                            'avg_tempo': statistics.mean([f['tempo'] for f in features]),
                            'top_genre': artists[0]['genres'][0] if artists and artists[0].get('genres') else 'Unknown',
                            'unique_artists': len(set(a['id'] for a in artists if a.get('id'))),
                            'unique_tracks': len(tracks)
                        }
        
        # Calculate trends
        trends = {}
        if evolution['short_term'] and evolution['long_term']:
            for key in ['avg_energy', 'avg_valence', 'avg_danceability']:
                if key in evolution['short_term'] and key in evolution['long_term']:
                    change = evolution['short_term'][key] - evolution['long_term'][key]
                    trends[key] = {
                        'change': change,
                        'direction': 'increasing' if change > 0 else 'decreasing',
                        'percentage': abs(change) * 100
                    }
        
        return jsonify({
            'evolution': evolution,
            'trends': trends
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listening-stats')
def get_listening_stats():
    """Get comprehensive listening statistics."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = get_user_id()
        
        stats = {
            'total_unique_tracks': 0,
            'total_unique_artists': 0,
            'estimated_minutes': 0,
            'top_time_range': {},
            'diversity_score': 0
        }
        
        all_track_ids = set()
        all_artist_ids = set()
        total_duration = 0
        
        for time_range in ['short_term', 'medium_term', 'long_term']:
            tracks = storage.load_top_tracks(user_id, time_range) or []
            artists = storage.load_top_artists(user_id, time_range) or []
            
            # Collect unique IDs
            for track in tracks:
                if track.get('id'):
                    all_track_ids.add(track['id'])
                    total_duration += track.get('duration_ms', 0)
            
            for artist in artists:
                if artist.get('id'):
                    all_artist_ids.add(artist['id'])
            
            # Stats per time range
            if tracks or artists:
                stats['top_time_range'][time_range] = {
                    'tracks': len(tracks),
                    'artists': len(artists),
                    'top_genre': artists[0]['genres'][0] if artists and artists[0].get('genres') else None
                }
        
        stats['total_unique_tracks'] = len(all_track_ids)
        stats['total_unique_artists'] = len(all_artist_ids)
        stats['estimated_minutes'] = total_duration // 60000
        
        # Calculate diversity score (based on genre variety)
        all_genres = set()
        for time_range in ['short_term', 'medium_term', 'long_term']:
            artists = storage.load_top_artists(user_id, time_range) or []
            for artist in artists:
                for genre in artist.get('genres', []):
                    all_genres.add(genre)
        
        stats['diversity_score'] = min(len(all_genres) / 10, 1.0) * 100  # Normalize to 0-100
        stats['total_genres'] = len(all_genres)
        
        # Get recently played for more accuracy
        recent = storage.load_data(user_id, 'recently_played')
        if recent:
            if isinstance(recent, dict) and 'data' in recent:
                recent = recent['data']
            stats['recent_plays'] = len(recent) if recent else 0
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port)
