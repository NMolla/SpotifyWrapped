#!/usr/bin/env python3
"""
Audio Features Enhancement for Spotify Wrapped
Adds mood, energy, and musical characteristic analysis
"""

import spotipy
from typing import List, Dict, Any
import statistics

def get_audio_features(sp: spotipy.Spotify, track_ids: List[str]) -> List[Dict[str, Any]]:
    """Get audio features for multiple tracks."""
    # Spotify limits to 100 tracks per request
    all_features = []
    
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i+100]
        features = sp.audio_features(batch)
        all_features.extend([f for f in features if f])  # Filter out None values
    
    return all_features

def analyze_music_characteristics(sp: spotipy.Spotify, tracks: List[Dict]) -> Dict[str, Any]:
    """Analyze musical characteristics of user's top tracks."""
    
    # Extract track IDs
    track_ids = [track['id'] for track in tracks if track.get('id')]
    
    if not track_ids:
        return {}
    
    # Get audio features
    features = get_audio_features(sp, track_ids)
    
    if not features:
        return {}
    
    # Calculate averages
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
        'acousticness': {
            'average': statistics.mean([f['acousticness'] for f in features]),
            'description': get_acousticness_description(statistics.mean([f['acousticness'] for f in features]))
        },
        'tempo': {
            'average': statistics.mean([f['tempo'] for f in features]),
            'description': get_tempo_description(statistics.mean([f['tempo'] for f in features]))
        },
        'instrumentalness': {
            'average': statistics.mean([f['instrumentalness'] for f in features]),
            'description': get_instrumentalness_description(statistics.mean([f['instrumentalness'] for f in features]))
        }
    }
    
    # Add musical profile
    analysis['musical_profile'] = generate_musical_profile(analysis)
    
    # Find extremes
    analysis['most_energetic'] = max(features, key=lambda x: x['energy'])
    analysis['most_danceable'] = max(features, key=lambda x: x['danceability'])
    analysis['happiest'] = max(features, key=lambda x: x['valence'])
    analysis['saddest'] = min(features, key=lambda x: x['valence'])
    analysis['fastest'] = max(features, key=lambda x: x['tempo'])
    
    return analysis

def get_energy_description(energy: float) -> str:
    """Get description for energy level."""
    if energy < 0.3:
        return "🧘 Very Chill - You prefer calm, relaxing music"
    elif energy < 0.5:
        return "😌 Mellow - Your music is laid-back and easy-going"
    elif energy < 0.7:
        return "🎵 Balanced - A good mix of calm and energetic tracks"
    elif energy < 0.85:
        return "⚡ Energetic - You like music that gets you moving"
    else:
        return "🔥 High Energy - Your playlist is full of bangers!"

def get_danceability_description(danceability: float) -> str:
    """Get description for danceability."""
    if danceability < 0.3:
        return "🪑 Not for dancing - More for listening and contemplation"
    elif danceability < 0.5:
        return "🚶 Light groove - Subtle rhythm, not dance-focused"
    elif danceability < 0.7:
        return "🕺 Groovy - Good rhythm that makes you move"
    elif danceability < 0.85:
        return "💃 Very danceable - Perfect for the dancefloor"
    else:
        return "🕺💃 Dance machine - Your music demands movement!"

def get_mood_description(valence: float) -> str:
    """Get description for mood (valence)."""
    if valence < 0.2:
        return "😢 Melancholic - Deep, emotional, introspective music"
    elif valence < 0.4:
        return "🌧️ Somewhat sad - Thoughtful and contemplative vibes"
    elif valence < 0.6:
        return "😐 Neutral mood - Balanced emotional content"
    elif valence < 0.8:
        return "😊 Upbeat - Generally positive and cheerful"
    else:
        return "😄 Very happy - Your music radiates joy and positivity!"

def get_acousticness_description(acousticness: float) -> str:
    """Get description for acousticness."""
    if acousticness < 0.2:
        return "🎹 Electronic - Heavily produced and synthesized"
    elif acousticness < 0.5:
        return "🎸 Mixed - Good balance of acoustic and electronic"
    elif acousticness < 0.8:
        return "🎻 Mostly acoustic - Natural instruments dominate"
    else:
        return "🪕 Very acoustic - Raw, unplugged sound"

def get_tempo_description(tempo: float) -> str:
    """Get description for tempo (BPM)."""
    if tempo < 80:
        return "🐌 Slow tempo - Relaxed and unhurried pace"
    elif tempo < 110:
        return "🚶 Moderate tempo - Walking pace rhythm"
    elif tempo < 130:
        return "🏃 Upbeat tempo - Energizing rhythm"
    elif tempo < 150:
        return "🏃‍♀️ Fast tempo - High-energy beats"
    else:
        return "🚀 Very fast - Intense, rapid-fire rhythm"

def get_instrumentalness_description(instrumentalness: float) -> str:
    """Get description for instrumentalness."""
    if instrumentalness < 0.1:
        return "🎤 Vocal-focused - Lyrics are central"
    elif instrumentalness < 0.3:
        return "🎵 Mostly vocals - Some instrumental breaks"
    elif instrumentalness < 0.6:
        return "🎼 Balanced - Good mix of vocals and instruments"
    elif instrumentalness < 0.8:
        return "🎹 Mostly instrumental - Limited vocals"
    else:
        return "🎻 Pure instrumental - No vocals, just instruments"

def generate_musical_profile(analysis: Dict[str, Any]) -> str:
    """Generate a musical profile description based on characteristics."""
    energy = analysis['energy']['average']
    valence = analysis['valence']['average']
    danceability = analysis['danceability']['average']
    acousticness = analysis['acousticness']['average']
    
    profiles = []
    
    # Energy + Mood combinations
    if energy > 0.7 and valence > 0.7:
        profiles.append("🎉 Party Enthusiast")
    elif energy > 0.7 and valence < 0.3:
        profiles.append("🎸 Intense & Emotional")
    elif energy < 0.3 and valence > 0.7:
        profiles.append("☀️ Peaceful & Happy")
    elif energy < 0.3 and valence < 0.3:
        profiles.append("🌙 Deep & Introspective")
    
    # Danceability profile
    if danceability > 0.75:
        profiles.append("💃 Dance Floor Regular")
    elif danceability < 0.25:
        profiles.append("🎧 Deep Listener")
    
    # Acoustic profile
    if acousticness > 0.7:
        profiles.append("🎸 Acoustic Lover")
    elif acousticness < 0.2:
        profiles.append("🎹 Electronic Fan")
    
    return " | ".join(profiles) if profiles else "🎵 Eclectic Listener"

def get_listening_personality(analysis: Dict[str, Any]) -> Dict[str, str]:
    """Generate a listening personality based on audio features."""
    
    energy = analysis['energy']['average']
    valence = analysis['valence']['average']
    dance = analysis['danceability']['average']
    acoustic = analysis['acousticness']['average']
    
    personality = {
        'type': '',
        'description': '',
        'emoji': ''
    }
    
    if energy > 0.6 and valence > 0.6 and dance > 0.6:
        personality['type'] = "The Life of the Party"
        personality['description'] = "You love upbeat, energetic music that gets everyone moving. Your playlists are perfect for celebrations and workouts."
        personality['emoji'] = "🎉"
    elif energy < 0.4 and valence < 0.4:
        personality['type'] = "The Deep Thinker"
        personality['description'] = "You prefer introspective, emotional music that speaks to the soul. Your playlists are perfect for late-night contemplation."
        personality['emoji'] = "🤔"
    elif acoustic > 0.7:
        personality['type'] = "The Purist"
        personality['description'] = "You appreciate authentic, acoustic sounds. Raw talent and genuine emotion matter more to you than production value."
        personality['emoji'] = "🎸"
    elif dance > 0.7:
        personality['type'] = "The Rhythm Seeker"
        personality['description'] = "The beat is what moves you. If it doesn't make you want to dance, it's not worth your time."
        personality['emoji'] = "🕺"
    elif valence > 0.7:
        personality['type'] = "The Optimist"
        personality['description'] = "Your music choices reflect your positive outlook. You use music to uplift your mood and spread good vibes."
        personality['emoji'] = "😊"
    else:
        personality['type'] = "The Explorer"
        personality['description'] = "Your taste is diverse and adventurous. You appreciate all types of music and aren't confined to one style."
        personality['emoji'] = "🌎"
    
    return personality

# Example usage in Flask endpoint
def audio_features_endpoint(sp, user_id, time_range='medium_term'):
    """Add this to your Flask app."""
    
    # Get top tracks
    tracks = storage.load_top_tracks(user_id, time_range)
    
    if not tracks:
        return {'error': 'No tracks found'}
    
    # Analyze audio characteristics
    analysis = analyze_music_characteristics(sp, tracks)
    
    # Get personality
    personality = get_listening_personality(analysis)
    
    return {
        'audio_analysis': analysis,
        'listening_personality': personality
    }
