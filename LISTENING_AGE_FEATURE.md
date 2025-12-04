# 🎵 My Listening Age Feature

## 📊 Overview
The "My Listening Age" feature analyzes the release dates of your top songs to determine your musical era preferences. It calculates statistics about how old the music you listen to is and identifies your favorite music decade.

## 🎯 What It Calculates

### Core Metrics
1. **Favorite Decade** - The decade you listen to most (e.g., "2010s", "1990s")
2. **Average Song Age** - How old your music is on average (in years)
3. **Average Release Year** - The mean year of all your top songs
4. **Music Range** - Oldest to newest song years (e.g., "1975 - 2025")
5. **Decade Distribution** - Breakdown of songs by decade

## 🔧 Technical Implementation

### Backend (`app.py`)

#### Data Collection
```python
# Extract release dates from album metadata
release_years = []
for track in all_tracks:
    release_date = track.get('album', {}).get('release_date', '')
    if release_date:
        try:
            year = int(release_date.split('-')[0])
            release_years.append(year)
        except:
            pass
```

#### Calculations
- **Average Year**: Mean of all release years
- **Average Age**: Current year minus average year
- **Decade Distribution**: Count songs by decade (year // 10 * 10)
- **Favorite Decade**: Most common decade in distribution

### API Endpoints

#### `/api/wrapped-stats/<time_range>`
Returns listening age in the response:
```json
{
  "listening_age": {
    "average_year": 2015,
    "average_age": 10,
    "newest_year": 2025,
    "oldest_year": 1985,
    "favorite_decade": "2010s",
    "decade_distribution": {
      "1980s": 5,
      "1990s": 12,
      "2000s": 18,
      "2010s": 45,
      "2020s": 20
    }
  }
}
```

#### `/api/spotify-wrapped/<year>`
Includes the same listening age data for yearly wrapped summaries.

## 🎨 Frontend Display

### 1. **StatsOverview Component**
- New stat card with calendar icon
- Shows favorite decade as main value
- Shows average song age as subtext
- Amber/yellow gradient color scheme

### 2. **SpotifyWrapped2025 Component**
- **New Slide 11**: "Your Listening Age"
- Large display of favorite decade
- Two info cards:
  - Average Song Age (e.g., "10 years")
  - Music Range (e.g., "1985 - 2025")
- Bottom text showing total span

### 3. **WrappedHub Component**
- Two new stat cards in Overview tab:
  - Favorite Decade
  - Average Song Age

## 📱 User Experience

### Where It Appears
1. **Dashboard** → Stats Overview (when viewing wrapped stats)
2. **Wrapped 2025** → Slide 11 (dedicated slide)
3. **Wrapped Hub** → Overview tab (stat cards)

### Visual Design
- **Icon**: Calendar icon (from lucide-react)
- **Colors**: Amber to yellow gradient
- **Format**: 
  - Decades shown as "1990s", "2000s", etc.
  - Age shown as "X years"
  - Years shown as 4-digit numbers

## 🎮 Example Output

**User who loves 90s rock:**
```
Favorite Decade: 1990s
Average Song Age: 30 years
Music Range: 1975 - 2024
Your music taste spans 49 years
```

**User who loves current hits:**
```
Favorite Decade: 2020s
Average Song Age: 2 years
Music Range: 2015 - 2025
Your music taste spans 10 years
```

## 🔍 Data Requirements

### Spotify API Data
- Track must have `album.release_date` field
- Supports various date formats:
  - `YYYY-MM-DD` (full date)
  - `YYYY-MM` (year and month)
  - `YYYY` (year only)

### Handling Missing Data
- Tracks without release dates are skipped
- If no valid release dates found, feature shows "N/A"
- Graceful fallbacks for all calculations

## 💡 Insights Provided

1. **Musical Era Preference** - Are you nostalgic or contemporary?
2. **Music Diversity** - How wide is your temporal range?
3. **Discovery Patterns** - Do you stick to one era or explore?
4. **Generation Identity** - What musical generation defines you?

## 🚀 Future Enhancements

Potential improvements:
- Compare your listening age to your actual age
- Show evolution of listening age over time
- Recommend songs from underrepresented decades
- Create "time travel" playlists
- Show how your listening age compares to other users

## 📊 Benefits

- **Self-awareness** - Understand your musical preferences better
- **Discovery** - Identify gaps in your musical timeline
- **Nostalgia** - Celebrate your favorite musical era
- **Sharing** - Fun stat to share with friends
- **Unique insight** - Not available in official Spotify Wrapped!
