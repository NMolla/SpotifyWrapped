#!/usr/bin/env python3
"""
JSON-based storage system for Spotify data.
Stores API responses as JSON files with metadata.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib

# Storage directory
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'spotify_data')

def ensure_storage_dir():
    """Ensure the storage directory exists."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
        print(f"Created storage directory: {STORAGE_DIR}")

def get_user_dir(user_id: str) -> str:
    """Get the directory path for a specific user."""
    user_dir = os.path.join(STORAGE_DIR, user_id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def get_file_path(user_id: str, data_type: str, time_range: Optional[str] = None) -> str:
    """Get the file path for a specific data type."""
    user_dir = get_user_dir(user_id)
    if time_range:
        filename = f"{data_type}_{time_range}.json"
    else:
        filename = f"{data_type}.json"
    return os.path.join(user_dir, filename)

def save_data(user_id: str, data_type: str, data: Any, time_range: Optional[str] = None) -> bool:
    """Save data to a JSON file with metadata."""
    ensure_storage_dir()
    
    try:
        file_path = get_file_path(user_id, data_type, time_range)
        
        # Wrap data with metadata
        wrapped_data = {
            'user_id': user_id,
            'data_type': data_type,
            'time_range': time_range,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(wrapped_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_data(user_id: str, data_type: str, time_range: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load data from a JSON file."""
    try:
        file_path = get_file_path(user_id, data_type, time_range)
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            wrapped_data = json.load(f)
        
        return wrapped_data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def is_data_stale(user_id: str, data_type: str, time_range: Optional[str] = None, days: int = 7) -> bool:
    """Check if data is older than specified days."""
    wrapped_data = load_data(user_id, data_type, time_range)
    
    if not wrapped_data:
        return True  # No data exists, so it's "stale"
    
    try:
        timestamp = datetime.fromisoformat(wrapped_data['timestamp'])
        age = datetime.now() - timestamp
        return age.days >= days
    except:
        return True  # If we can't determine age, consider it stale

def save_user_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
    """Save user profile data."""
    return save_data(user_id, 'profile', profile_data)

def load_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user profile data."""
    wrapped = load_data(user_id, 'profile')
    return wrapped['data'] if wrapped else None

def save_top_tracks(user_id: str, tracks: List[Dict[str, Any]], time_range: str) -> bool:
    """Save top tracks for a specific time range."""
    return save_data(user_id, 'top_tracks', tracks, time_range)

def load_top_tracks(user_id: str, time_range: str) -> Optional[List[Dict[str, Any]]]:
    """Load top tracks for a specific time range."""
    wrapped = load_data(user_id, 'top_tracks', time_range)
    return wrapped['data'] if wrapped else None

def save_top_artists(user_id: str, artists: List[Dict[str, Any]], time_range: str) -> bool:
    """Save top artists for a specific time range."""
    return save_data(user_id, 'top_artists', artists, time_range)

def load_top_artists(user_id: str, time_range: str) -> Optional[List[Dict[str, Any]]]:
    """Load top artists for a specific time range."""
    wrapped = load_data(user_id, 'top_artists', time_range)
    return wrapped['data'] if wrapped else None

def get_storage_stats() -> Dict[str, Any]:
    """Get statistics about the storage."""
    ensure_storage_dir()
    
    stats = {
        'storage_dir': STORAGE_DIR,
        'users': 0,
        'total_files': 0,
        'total_size_mb': 0
    }
    
    if not os.path.exists(STORAGE_DIR):
        return stats
    
    # Count users and files
    for user_dir in os.listdir(STORAGE_DIR):
        user_path = os.path.join(STORAGE_DIR, user_dir)
        if os.path.isdir(user_path):
            stats['users'] += 1
            for file in os.listdir(user_path):
                if file.endswith('.json'):
                    stats['total_files'] += 1
                    file_path = os.path.join(user_path, file)
                    stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
    
    stats['total_size_mb'] = round(stats['total_size_mb'], 2)
    return stats

def clear_user_data(user_id: str) -> bool:
    """Clear all data for a specific user."""
    try:
        user_dir = get_user_dir(user_id)
        if os.path.exists(user_dir):
            import shutil
            shutil.rmtree(user_dir)
        return True
    except Exception as e:
        print(f"Error clearing user data: {e}")
        return False

def get_all_user_files(user_id: str) -> List[Dict[str, Any]]:
    """Get information about all files for a user."""
    user_dir = get_user_dir(user_id)
    files = []
    
    if not os.path.exists(user_dir):
        return files
    
    for filename in os.listdir(user_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(user_dir, filename)
            
            # Get file info
            size_kb = os.path.getsize(file_path) / 1024
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # Parse filename
            name_parts = filename[:-5].split('_')  # Remove .json
            data_type = name_parts[0]
            time_range = name_parts[1] if len(name_parts) > 1 else None
            
            # Check if stale
            is_stale = is_data_stale(user_id, data_type.replace('_', ' '), time_range)
            
            files.append({
                'filename': filename,
                'data_type': data_type,
                'time_range': time_range,
                'size_kb': round(size_kb, 2),
                'modified': modified.isoformat(),
                'age_days': (datetime.now() - modified).days,
                'is_stale': is_stale
            })
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)
