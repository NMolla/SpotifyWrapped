"""
SQLite database module for storing Spotify data locally.
This provides persistent storage, enables complex analytics, and reduces API calls.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import os
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'spotify_data.db')

@contextmanager
def get_db_connection():
    """Context manager for database connections with proper timeout and WAL mode."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0, isolation_level='DEFERRED')
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        # Enable WAL mode for better concurrency
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')  # 30 second busy timeout
        conn.execute('PRAGMA synchronous=NORMAL')  # Faster writes with safety
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database with all necessary tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT,
                email TEXT,
                image_url TEXT,
                country TEXT,
                product TEXT,
                last_synced TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tracks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                album_name TEXT,
                album_id TEXT,
                duration_ms INTEGER,
                popularity INTEGER,
                preview_url TEXT,
                track_number INTEGER,
                disc_number INTEGER,
                explicit BOOLEAN,
                is_local BOOLEAN,
                release_date TEXT,
                album_image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                popularity INTEGER,
                followers INTEGER,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Track-Artist relationship table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS track_artists (
                track_id TEXT,
                artist_id TEXT,
                artist_position INTEGER,
                PRIMARY KEY (track_id, artist_id),
                FOREIGN KEY (track_id) REFERENCES tracks (track_id),
                FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
            )
        ''')
        
        # Artist genres table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artist_genres (
                artist_id TEXT,
                genre TEXT,
                PRIMARY KEY (artist_id, genre),
                FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
            )
        ''')
        
        # User top tracks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_top_tracks (
                user_id TEXT,
                track_id TEXT,
                time_range TEXT,
                position INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, track_id, time_range),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (track_id) REFERENCES tracks (track_id)
            )
        ''')
        
        # User top artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_top_artists (
                user_id TEXT,
                artist_id TEXT,
                time_range TEXT,
                position INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, artist_id, time_range),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
            )
        ''')
        
        # Sync metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                user_id TEXT,
                data_type TEXT,
                time_range TEXT,
                last_synced TIMESTAMP,
                total_items INTEGER,
                PRIMARY KEY (user_id, data_type, time_range)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_track_popularity ON tracks(popularity DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_artist_popularity ON artists(popularity DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_top_tracks_position ON user_top_tracks(user_id, time_range, position)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_top_artists_position ON user_top_artists(user_id, time_range, position)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_artist_genres_genre ON artist_genres(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_metadata ON sync_metadata(user_id, data_type, time_range, last_synced)')
        
        conn.commit()

def save_user(user_data: Dict[str, Any]) -> None:
    """Save or update user information."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, display_name, email, image_url, country, product, last_synced)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.get('id'),
            user_data.get('display_name', 'Spotify User'),
            user_data.get('email'),
            user_data.get('images', [{}])[0].get('url') if user_data.get('images') else None,
            user_data.get('country'),
            user_data.get('product'),
            datetime.now()
        ))
        conn.commit()

def save_track(track_data: Dict[str, Any]) -> None:
    """Save track information."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Save track
        cursor.execute('''
            INSERT OR REPLACE INTO tracks 
            (track_id, name, album_name, album_id, duration_ms, popularity, 
             preview_url, track_number, disc_number, explicit, is_local, 
             release_date, album_image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            track_data.get('id'),
            track_data.get('name'),
            track_data.get('album', {}).get('name'),
            track_data.get('album', {}).get('id'),
            track_data.get('duration_ms'),
            track_data.get('popularity'),
            track_data.get('preview_url'),
            track_data.get('track_number'),
            track_data.get('disc_number'),
            track_data.get('explicit'),
            track_data.get('is_local'),
            track_data.get('album', {}).get('release_date'),
            track_data.get('album', {}).get('images', [{}])[0].get('url') if track_data.get('album', {}).get('images') else None
        ))
        
        # Save associated artists
        for idx, artist in enumerate(track_data.get('artists', [])):
            save_artist(artist)
            cursor.execute('''
                INSERT OR REPLACE INTO track_artists 
                (track_id, artist_id, artist_position)
                VALUES (?, ?, ?)
            ''', (track_data.get('id'), artist.get('id'), idx))
        
        conn.commit()

def save_artist(artist_data: Dict[str, Any]) -> None:
    """Save artist information."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Save artist
        cursor.execute('''
            INSERT OR REPLACE INTO artists 
            (artist_id, name, popularity, followers, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            artist_data.get('id'),
            artist_data.get('name'),
            artist_data.get('popularity'),
            artist_data.get('followers', {}).get('total'),
            artist_data.get('images', [{}])[0].get('url') if artist_data.get('images') else None
        ))
        
        # Save genres
        for genre in artist_data.get('genres', []):
            cursor.execute('''
                INSERT OR REPLACE INTO artist_genres 
                (artist_id, genre)
                VALUES (?, ?)
            ''', (artist_data.get('id'), genre))
        
        conn.commit()

def save_user_top_tracks(user_id: str, tracks: List[Dict], time_range: str) -> None:
    """Save user's top tracks for a specific time range."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Clear existing data for this user and time range
        cursor.execute('''
            DELETE FROM user_top_tracks 
            WHERE user_id = ? AND time_range = ?
        ''', (user_id, time_range))
        
        # Save new data
        for position, track in enumerate(tracks, 1):
            save_track(track)
            cursor.execute('''
                INSERT INTO user_top_tracks 
                (user_id, track_id, time_range, position, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, track.get('id'), time_range, position, datetime.now()))
        
        # Update sync metadata
        cursor.execute('''
            INSERT OR REPLACE INTO sync_metadata 
            (user_id, data_type, time_range, last_synced, total_items)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'tracks', time_range, datetime.now(), len(tracks)))
        
        conn.commit()

def save_user_top_artists(user_id: str, artists: List[Dict], time_range: str) -> None:
    """Save user's top artists for a specific time range."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Clear existing data for this user and time range
        cursor.execute('''
            DELETE FROM user_top_artists 
            WHERE user_id = ? AND time_range = ?
        ''', (user_id, time_range))
        
        # Save new data
        for position, artist in enumerate(artists, 1):
            save_artist(artist)
            cursor.execute('''
                INSERT INTO user_top_artists 
                (user_id, artist_id, time_range, position, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, artist.get('id'), time_range, position, datetime.now()))
        
        # Update sync metadata
        cursor.execute('''
            INSERT OR REPLACE INTO sync_metadata 
            (user_id, data_type, time_range, last_synced, total_items)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'artists', time_range, datetime.now(), len(artists)))
        
        conn.commit()

def is_data_stale(user_id: str, data_type: str, time_range: str, days: int = 7) -> bool:
    """Check if data needs to be refreshed."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT last_synced FROM sync_metadata 
            WHERE user_id = ? AND data_type = ? AND time_range = ?
        ''', (user_id, data_type, time_range))
        
        result = cursor.fetchone()
        if not result:
            return True  # No data exists
        
        last_synced = datetime.fromisoformat(result['last_synced'])
        return datetime.now() - last_synced > timedelta(days=days)

def get_user_top_tracks(user_id: str, time_range: str, limit: Optional[int] = None) -> List[Dict]:
    """Get user's top tracks from database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                t.*,
                utt.position,
                GROUP_CONCAT(a.name, ', ') as artist_names,
                GROUP_CONCAT(a.artist_id, ', ') as artist_ids
            FROM user_top_tracks utt
            JOIN tracks t ON utt.track_id = t.track_id
            LEFT JOIN track_artists ta ON t.track_id = ta.track_id
            LEFT JOIN artists a ON ta.artist_id = a.artist_id
            WHERE utt.user_id = ? AND utt.time_range = ?
            GROUP BY t.track_id, utt.position
            ORDER BY utt.position
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id, time_range))
        tracks = []
        
        for row in cursor.fetchall():
            track = dict(row)
            # Parse artist information
            if track.get('artist_names'):
                track['artists'] = track['artist_names'].split(', ')
                track['artist_ids'] = track['artist_ids'].split(', ')
            else:
                track['artists'] = []
                track['artist_ids'] = []
            tracks.append(track)
        
        return tracks

def get_user_top_artists(user_id: str, time_range: str, limit: Optional[int] = None) -> List[Dict]:
    """Get user's top artists from database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                a.*,
                uta.position,
                GROUP_CONCAT(ag.genre, ', ') as genres
            FROM user_top_artists uta
            JOIN artists a ON uta.artist_id = a.artist_id
            LEFT JOIN artist_genres ag ON a.artist_id = ag.artist_id
            WHERE uta.user_id = ? AND uta.time_range = ?
            GROUP BY a.artist_id, uta.position
            ORDER BY uta.position
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id, time_range))
        artists = []
        
        for row in cursor.fetchall():
            artist = dict(row)
            # Parse genres
            if artist.get('genres'):
                artist['genres'] = artist['genres'].split(', ')
            else:
                artist['genres'] = []
            artists.append(artist)
        
        return artists

def get_genre_statistics(user_id: str, time_range: str) -> Dict[str, int]:
    """Get genre statistics for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ag.genre, COUNT(*) as count
            FROM user_top_artists uta
            JOIN artist_genres ag ON uta.artist_id = ag.artist_id
            WHERE uta.user_id = ? AND uta.time_range = ?
            GROUP BY ag.genre
            ORDER BY count DESC
        ''', (user_id, time_range))
        
        return {row['genre']: row['count'] for row in cursor.fetchall()}

def get_listening_stats(user_id: str, time_range: str) -> Dict[str, Any]:
    """Get comprehensive listening statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total listening time
        cursor.execute('''
            SELECT 
                SUM(t.duration_ms) as total_ms,
                AVG(t.popularity) as avg_popularity,
                COUNT(DISTINCT t.track_id) as total_tracks,
                COUNT(DISTINCT ta.artist_id) as unique_artists
            FROM user_top_tracks utt
            JOIN tracks t ON utt.track_id = t.track_id
            LEFT JOIN track_artists ta ON t.track_id = ta.track_id
            WHERE utt.user_id = ? AND utt.time_range = ?
        ''', (user_id, time_range))
        
        track_stats = dict(cursor.fetchone())
        
        # Artist stats
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT a.artist_id) as total_artists,
                AVG(a.popularity) as avg_artist_popularity,
                COUNT(DISTINCT ag.genre) as unique_genres
            FROM user_top_artists uta
            JOIN artists a ON uta.artist_id = a.artist_id
            LEFT JOIN artist_genres ag ON a.artist_id = ag.artist_id
            WHERE uta.user_id = ? AND uta.time_range = ?
        ''', (user_id, time_range))
        
        artist_stats = dict(cursor.fetchone())
        
        # Combine stats
        return {
            'total_minutes': track_stats['total_ms'] // 60000 if track_stats['total_ms'] else 0,
            'total_hours': (track_stats['total_ms'] // 60000) // 60 if track_stats['total_ms'] else 0,
            'avg_track_popularity': round(track_stats['avg_popularity'], 1) if track_stats['avg_popularity'] else 0,
            'total_tracks': track_stats['total_tracks'] or 0,
            'unique_artists_from_tracks': track_stats['unique_artists'] or 0,
            'total_artists': artist_stats['total_artists'] or 0,
            'avg_artist_popularity': round(artist_stats['avg_artist_popularity'], 1) if artist_stats['avg_artist_popularity'] else 0,
            'unique_genres': artist_stats['unique_genres'] or 0
        }

def get_sync_status(user_id: str) -> List[Dict]:
    """Get synchronization status for all data types."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                data_type,
                time_range,
                last_synced,
                total_items,
                CASE 
                    WHEN julianday('now') - julianday(last_synced) > 7 THEN 'stale'
                    WHEN julianday('now') - julianday(last_synced) > 3 THEN 'aging'
                    ELSE 'fresh'
                END as status
            FROM sync_metadata
            WHERE user_id = ?
            ORDER BY data_type, time_range
        ''', (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]

def get_database_stats() -> Dict[str, Any]:
    """Get overall database statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        tables = ['users', 'tracks', 'artists', 'user_top_tracks', 'user_top_artists']
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
            stats[f'{table}_count'] = cursor.fetchone()['count']
        
        # Get database file size
        if os.path.exists(DB_PATH):
            stats['database_size_mb'] = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)
        
        return stats

# Initialize database on module import
if not os.path.exists(DB_PATH):
    init_database()
