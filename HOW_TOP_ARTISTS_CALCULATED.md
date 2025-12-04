# 🎤 How Top Artists Are Calculated

## 📊 Overview
Top artists in your Spotify Wrapped app are **NOT calculated by us** - they come directly from Spotify's official algorithm through their Web API.

## 🔍 The Process

### 1. **Spotify API Call**
```python
sp.current_user_top_artists(limit=50, offset=0, time_range='long_term')
```

We call Spotify's official endpoint: `GET /v1/me/top/artists`

### 2. **What Spotify Returns**
Spotify provides your top artists based on their proprietary algorithm, which considers:
- **Play count** - How many times you've played songs by the artist
- **Recency** - Recent plays are weighted more heavily
- **Completion rate** - Full song plays vs skips
- **User engagement** - Saves, playlist adds, follows
- **Listening duration** - Total time spent listening to the artist

### 3. **Time Ranges**
Spotify calculates top artists for three periods:
- **`short_term`** - Last 4 weeks
- **`medium_term`** - Last 6 months  
- **`long_term`** - Several years of data

### 4. **Pagination**
Our app fetches ALL your top artists (not just first 50):
```python
def fetch_all_spotify_items(sp, fetch_func, **kwargs):
    all_items = []
    limit = 50  # Spotify's max per request
    offset = 0
    
    while True:
        results = fetch_func(limit=limit, offset=offset, **kwargs)
        items = results.get('items', [])
        all_items.extend(items)
        
        if not results.get('next') or len(items) < limit:
            break
        
        offset += limit
    
    return all_items
```

### 5. **Data Stored**
For each artist, we store what Spotify provides:
- **ID** - Spotify's unique identifier
- **Name** - Artist name
- **Genres** - Associated music genres
- **Popularity** - 0-100 score
- **Followers** - Total follower count
- **Images** - Profile photos

### 6. **Ranking**
The order/ranking comes directly from Spotify:
- Position 1 = Your most played artist
- Position 2 = Second most played
- And so on...

## ❗ Important Notes

### We Don't Calculate Rankings
- **Spotify decides** who your top artists are
- **Spotify determines** the ranking order
- **We just display** what Spotify tells us

### Why Rankings Might Seem Off
1. **Spotify's algorithm is complex** - It's not just play count
2. **Recency bias** - Recent plays weighted heavily
3. **Full catalog** - Includes plays from all devices/apps
4. **Historical data** - `long_term` includes years of history

### What Affects Your Top Artists
- ✅ Playing full songs (not skipping)
- ✅ Repeat plays
- ✅ Adding to playlists
- ✅ Following the artist
- ✅ Saving their songs
- ❌ Just browsing their page
- ❌ Partial song plays (skips)

## 🔄 Data Freshness

### Auto-Sync
- Data older than 7 days refreshes automatically
- Manual sync available via UI

### Cache
- Results cached for 15 minutes
- Reduces API calls
- Improves performance

## 📱 In Your App

### Where Top Artists Appear
1. **Dashboard** - `/dashboard` → Top Artists tab
2. **Wrapped 2025** - `/wrapped` → Slides 5-6
3. **Wrapped Hub** - `/hub` → Overview tab
4. **API Endpoint** - `/api/top/artists/<time_range>`
5. **Instagram Cards** - Top 10 artists card

### Display Format
- **Top 10** shown in main views (was Top 5)
- **2-column layout** to prevent scrolling
- **With images** - Artist profile photos
- **With genres** - Musical styles

## 🎯 Summary

Your top artists are:
1. **Calculated by Spotify** using their proprietary algorithm
2. **Fetched via official API** with proper authentication
3. **Stored locally** for performance
4. **Displayed exactly as ranked** by Spotify

The app is essentially a beautiful viewer for Spotify's official data - we don't modify or recalculate the rankings in any way. What you see is what Spotify has determined based on your complete listening history across all devices and platforms.
