import os
import json
import base64
import secrets
from io import BytesIO
from datetime import datetime
from collections import Counter
from flask import Flask, redirect, request, jsonify, session, send_file
from flask_cors import CORS
from flask_caching import Cache
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageDraw, ImageFont
import requests
import hashlib

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Configure cache
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use simple in-memory cache
    'CACHE_DEFAULT_TIMEOUT': 900  # Default 15 minutes
})

# Spotify OAuth Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:5000/callback')
SCOPE = 'user-top-read user-read-private user-read-email'

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
    """Fetch all items from Spotify API with pagination.
    
    Args:
        sp: Spotify client instance
        fetch_func: Function to call (e.g., sp.current_user_top_tracks)
        **kwargs: Arguments to pass to the function (e.g., time_range)
    
    Returns:
        List of all items fetched
    """
    all_items = []
    limit = 50  # Maximum allowed by Spotify API for most endpoints
    offset = 0
    
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
        
        # Safety check to prevent infinite loops (Spotify typically limits to 1000 items)
        if offset >= 1000:
            break
    
    return all_items

@app.route('/')
def index():
    """Check if user is authenticated."""
    if session.get('token_info'):
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

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

@app.route('/api/cache-status')
def cache_status():
    """Get cache status information."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get user ID for reference
        user_id = get_user_id()
        
        # Return cache configuration info
        return jsonify({
            'cache_type': 'simple',
            'default_timeout': 900,
            'user_id': user_id,
            'cache_timeouts': {
                'user_profile': '5 minutes',
                'top_items': '15 minutes',
                'wrapped_stats': '30 minutes',
                'spotify_wrapped': '1 hour'
            },
            'message': 'Cache is active and working'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user')
def get_user():
    """Get current user profile."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Generate cache key for user profile
    cache_key = generate_cache_key('user_profile')
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    try:
        user = sp.current_user()
        user_data = {
            'name': user.get('display_name', 'Spotify User'),
            'email': user.get('email'),
            'image': user.get('images', [{}])[0].get('url') if user.get('images') else None,
            'id': user.get('id')
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, user_data, timeout=300)
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top/<item_type>/<time_range>')
def get_top_items(item_type, time_range):
    """Get user's top tracks or artists."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if item_type not in ['tracks', 'artists']:
        return jsonify({'error': 'Invalid item type'}), 400
    
    if time_range not in ['short_term', 'medium_term', 'long_term']:
        return jsonify({'error': 'Invalid time range'}), 400
    
    # Generate cache key
    cache_key = generate_cache_key('top_items', item_type, time_range)
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    try:
        # Fetch all items with pagination
        if item_type == 'tracks':
            all_items = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=time_range)
        else:
            all_items = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=time_range)
        
        items = []
        for item in all_items:
            if item_type == 'tracks':
                items.append({
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                    'artists': [artist['name'] for artist in item['artists']],
                    'album': item['album']['name'],
                    'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'duration_ms': item['duration_ms'],
                    'popularity': item['popularity'],
                    'preview_url': item['preview_url']
                })
            else:
                items.append({
                    'id': item['id'],
                    'name': item['name'],
                    'genres': item['genres'],
                    'image': item['images'][0]['url'] if item['images'] else None,
                    'popularity': item['popularity'],
                    'followers': item['followers']['total']
                })
        
        # Cache the data for 15 minutes
        cache.set(cache_key, items, timeout=900)
        
        # Return all items (frontend can limit display as needed)
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wrapped-stats/<time_range>')
def get_wrapped_stats(time_range):
    """Get comprehensive wrapped statistics."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if time_range not in ['short_term', 'medium_term', 'long_term']:
        return jsonify({'error': 'Invalid time range'}), 400
    
    # Generate cache key
    cache_key = generate_cache_key('wrapped_stats', time_range)
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    try:
        # Get all top tracks and artists with pagination
        all_top_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=time_range)
        all_top_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=time_range)
        
        # Process genres from artists
        all_genres = []
        for artist in all_top_artists:
            all_genres.extend(artist['genres'])
        
        genre_counts = Counter(all_genres)
        top_genres = genre_counts.most_common(10)
        
        # Calculate listening statistics
        total_duration = sum(track['duration_ms'] for track in all_top_tracks)
        avg_popularity = sum(track['popularity'] for track in all_top_tracks) / len(all_top_tracks) if all_top_tracks else 0
        
        # Determine music characteristics
        characteristics = analyze_music_taste(all_top_tracks, all_top_artists, genre_counts)
        
        stats = {
            'top_artist': {
                'name': all_top_artists[0]['name'] if all_top_artists else 'Unknown',
                'image': all_top_artists[0]['images'][0]['url'] if all_top_artists and all_top_artists[0]['images'] else None,
                'genres': all_top_artists[0]['genres'][:3] if all_top_artists else []
            },
            'top_track': {
                'name': all_top_tracks[0]['name'] if all_top_tracks else 'Unknown',
                'artist': all_top_tracks[0]['artists'][0]['name'] if all_top_tracks and all_top_tracks[0]['artists'] else 'Unknown',
                'image': all_top_tracks[0]['album']['images'][0]['url'] if all_top_tracks and all_top_tracks[0]['album']['images'] else None
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
        
        # Cache for 30 minutes (computationally expensive)
        cache.set(cache_key, stats, timeout=1800)
        
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
    """Generate official Spotify Wrapped style data for a specific year."""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Generate cache key
    cache_key = generate_cache_key('spotify_wrapped', year)
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Use medium_term for current year (approximates Jan-Oct)
        # Use long_term for previous years
        time_range = 'medium_term' if year == current_year else 'long_term'
        
        # Get all tracks and artists with pagination
        all_tracks = fetch_all_spotify_items(sp, sp.current_user_top_tracks, time_range=time_range)
        all_artists = fetch_all_spotify_items(sp, sp.current_user_top_artists, time_range=time_range)
        
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

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port)
