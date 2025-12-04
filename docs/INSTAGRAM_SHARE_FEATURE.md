# 📸 Instagram Sharable Wrapped Summary

## ✨ New Feature: Instagram-Ready Wrapped Cards

Your Spotify Wrapped can now be downloaded as beautiful, Instagram-ready images!

## 🎨 What's Included

### 4 Different Card Types

1. **📊 Wrapped Summary Card**
   - Total minutes listened
   - Top genre
   - Unique tracks & artists count
   - Top artist and track highlights
   - Year overview stats

2. **🎵 Top 5 Tracks Card**
   - Your most played songs
   - Artist names included
   - Beautiful gradient design
   - Numbered ranking

3. **🎤 Top 5 Artists Card**
   - Your favorite artists
   - Genre tags
   - Numbered ranking
   - Stylish layout

4. **🎭 Music Personality Card**
   - Your unique listening personality type
   - Energy, happiness, and danceability scores
   - Personalized description
   - Custom gradient based on personality

## 📱 Features

- **Instagram Portrait Format**: 1080x1350 pixels (perfect for feed posts)
- **High Quality**: PNG format with crisp text and graphics
- **Beautiful Gradients**: Spotify-inspired color schemes
- **Downloadable**: Save directly to your device
- **Shareable**: Ready to post on Instagram, Stories, or any social media
- **Time Period Selection**: Choose from All Time, Last 6 Months, or Last 4 Weeks

## 🚀 How to Use

### Access the Instagram Share Page

1. **Start the server**:
   ```bash
   source .venv/bin/activate
   python app.py
   ```

2. **Login** (if needed):
   ```
   http://127.0.0.1:5000/login
   ```

3. **Visit the Instagram Share page**:
   ```
   http://127.0.0.1:5000/instagram-share
   ```

### Download Individual Cards

Click the download button under each card type to save it to your device.

### Download All Cards at Once

Click "Download All Cards as ZIP" to get all 4 cards in a single ZIP file.

## 🔗 API Endpoints

### Individual Card Download
```
GET /api/instagram-wrapped/<card_type>?time_range=<period>
```

Card types:
- `summary` - Overall wrapped summary
- `tracks` - Top 5 tracks
- `artists` - Top 5 artists  
- `personality` - Music personality analysis

Time ranges:
- `short_term` - Last 4 weeks
- `medium_term` - Last 6 months
- `long_term` - All time

Example:
```
http://127.0.0.1:5000/api/instagram-wrapped/summary?time_range=long_term
```

### Download All Cards
```
GET /api/instagram-wrapped-download?time_range=<period>
```

Downloads a ZIP file containing all 4 card types.

## 📐 Technical Details

### Image Specifications
- **Format**: PNG
- **Resolution**: 1080x1350 pixels
- **Aspect Ratio**: 4:5 (Instagram portrait)
- **File Size**: ~200-400KB per image
- **Quality**: 95% PNG compression

### Design Elements
- Custom gradients for each card type
- Spotify green (#1DB954) accent colors
- Clean, modern typography
- Emoji icons for visual appeal
- Rounded corners and shadows

## 🎯 Perfect For

- **Instagram Feed Posts**: 4:5 aspect ratio optimized
- **Instagram Stories**: Can be centered with background
- **Twitter/X**: Share your music taste
- **WhatsApp Status**: Share with friends
- **Dating Apps**: Show your music personality
- **Year-End Reviews**: Document your music journey

## 💡 Tips for Sharing

1. **Best Time**: Post when your followers are most active
2. **Hashtags**: Use #SpotifyWrapped #[YourYear]Wrapped #MusicWrapped
3. **Caption Ideas**:
   - "My music personality is [type]. What's yours? 🎵"
   - "[X] minutes of pure vibes this year 🎧"
   - "These artists got me through [year] 💚"
4. **Stories**: Share all 4 cards as a story sequence
5. **Carousel Post**: Upload all cards as a multi-image post

## 🐛 Troubleshooting

### Cards won't download
1. Make sure you're logged in
2. Sync your data first at `/sync-ui`
3. Check that you have data for the selected time period

### Images look wrong
1. Make sure you have Pillow installed: `pip install Pillow`
2. Fonts may vary by system (fallback to default if custom fonts unavailable)

### No personality card
1. Personality requires audio features analysis
2. Make sure you have tracks synced
3. Try refreshing your data

## 🎉 Share Your Wrapped!

Now you can share your Spotify Wrapped anytime, not just in December! Create beautiful Instagram posts that showcase your unique music taste and personality.

Enjoy sharing your music journey! 🎵📸
