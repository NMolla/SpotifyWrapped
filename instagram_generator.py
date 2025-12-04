#!/usr/bin/env python3
"""
Instagram Wrapped Card Generator
Creates beautiful, shareable wrapped summary images
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
from datetime import datetime
import os

class InstagramWrappedGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1350  # Instagram portrait ratio
        self.spotify_green = '#1DB954'
        self.spotify_black = '#191414'
        
        # Try to load system fonts
        self.fonts = self.load_fonts()
    
    def load_fonts(self):
        """Load fonts with fallbacks."""
        fonts = {}
        
        # Try different font paths for different OS
        font_paths = [
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Avenir.ttc",
            # Common
            "Arial.ttf",
            "Helvetica.ttf",
        ]
        
        for path in font_paths:
            try:
                fonts['title'] = ImageFont.truetype(path, 72)
                fonts['header'] = ImageFont.truetype(path, 56)
                fonts['body'] = ImageFont.truetype(path, 36)
                fonts['caption'] = ImageFont.truetype(path, 28)
                fonts['small'] = ImageFont.truetype(path, 24)
                return fonts
            except:
                continue
        
        # Fallback to default
        default = ImageFont.load_default()
        return {
            'title': default,
            'header': default,
            'body': default,
            'caption': default,
            'small': default
        }
    
    def create_gradient_background(self, img, colors=None):
        """Create a gradient background."""
        if not colors:
            colors = [(25, 20, 20), (29, 185, 84)]  # Dark to Spotify green
        
        draw = ImageDraw.Draw(img)
        
        for i in range(self.height):
            ratio = i / self.height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.rectangle([(0, i), (self.width, i + 1)], fill=(r, g, b))
        
        return img
    
    def download_artist_image(self, image_url):
        """Download and process artist image."""
        try:
            response = requests.get(image_url, timeout=5)
            img = Image.open(BytesIO(response.content))
            # Make it square and resize
            size = min(img.size)
            img = img.crop((
                (img.width - size) // 2,
                (img.height - size) // 2,
                (img.width + size) // 2,
                (img.height + size) // 2
            ))
            return img.resize((400, 400), Image.Resampling.LANCZOS)
        except:
            # Return placeholder
            img = Image.new('RGB', (400, 400), color=(100, 100, 100))
            return img
    
    def create_wrapped_summary_card(self, user_data):
        """Create main wrapped summary card."""
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        self.create_gradient_background(img)
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        user_name = user_data.get('user_name', 'My')
        
        # Header
        y = 80
        draw.text((self.width // 2, y), f"{user_name}'s", 
                 fill='white', font=self.fonts['header'], anchor='mt')
        y += 70
        draw.text((self.width // 2, y), f"{year} WRAPPED", 
                 fill=self.spotify_green, font=self.fonts['title'], anchor='mt')
        y += 100
        
        # Stats boxes
        stats = [
            (user_data.get('total_minutes', 0), 'MINUTES LISTENED'),
            (user_data.get('top_genre', 'Unknown'), 'TOP GENRE'),
            (user_data.get('unique_tracks', 0), 'UNIQUE TRACKS'),
            (user_data.get('unique_artists', 0), 'DIFFERENT ARTISTS')
        ]
        
        # Draw stats in 2x2 grid
        box_width = 400
        box_height = 150
        x_positions = [self.width // 2 - 220, self.width // 2 + 20]
        y_position = y + 50
        
        for i, (value, label) in enumerate(stats):
            x = x_positions[i % 2]
            y_box = y_position + (i // 2) * 170
            
            # Draw box
            draw.rounded_rectangle(
                [(x, y_box), (x + box_width, y_box + box_height)],
                radius=20,
                fill=(255, 255, 255, 30)
            )
            
            # Draw value
            value_str = str(value) if isinstance(value, int) else value.upper()
            draw.text((x + box_width // 2, y_box + 50),
                     value_str,
                     fill=self.spotify_green,
                     font=self.fonts['header'],
                     anchor='mt')
            
            # Draw label
            draw.text((x + box_width // 2, y_box + 100),
                     label,
                     fill='white',
                     font=self.fonts['small'],
                     anchor='mt')
        
        y = y_position + 350
        
        # Top artist section
        top_artist = user_data.get('top_artist', {})
        if top_artist:
            draw.text((self.width // 2, y), "TOP ARTIST",
                     fill=self.spotify_green, font=self.fonts['body'], anchor='mt')
            y += 50
            draw.text((self.width // 2, y), top_artist.get('name', 'Unknown'),
                     fill='white', font=self.fonts['header'], anchor='mt')
            y += 80
        
        # Top track section
        top_track = user_data.get('top_track', {})
        if top_track:
            draw.text((self.width // 2, y), "TOP TRACK",
                     fill=self.spotify_green, font=self.fonts['body'], anchor='mt')
            y += 50
            draw.text((self.width // 2, y), top_track.get('name', 'Unknown')[:40],
                     fill='white', font=self.fonts['header'], anchor='mt')
            y += 60
            draw.text((self.width // 2, y), 
                     f"by {top_track.get('artist', 'Unknown')}",
                     fill=(200, 200, 200), font=self.fonts['caption'], anchor='mt')
        
        # Footer
        y = self.height - 100
        draw.text((self.width // 2, y), "Generated with Spotify Wrapped Dashboard",
                 fill=(150, 150, 150), font=self.fonts['small'], anchor='mt')
        
        # Add Spotify logo/branding
        draw.text((self.width // 2, y + 35), "♫",
                 fill=self.spotify_green, font=self.fonts['header'], anchor='mt')
        
        return img
    
    def create_top_5_card(self, user_data, item_type='tracks'):
        """Create a top 5 tracks or artists card."""
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        
        # Different gradient for variety
        colors = [(29, 185, 84), (25, 20, 20)] if item_type == 'tracks' else [(139, 69, 255), (25, 20, 20)]
        self.create_gradient_background(img, colors)
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        user_name = user_data.get('user_name', 'My')
        
        # Header
        y = 80
        draw.text((self.width // 2, y), f"{user_name}'s {year}",
                 fill='white', font=self.fonts['header'], anchor='mt')
        y += 70
        title = "TOP TRACKS" if item_type == 'tracks' else "TOP ARTISTS"
        draw.text((self.width // 2, y), title,
                 fill='white', font=self.fonts['title'], anchor='mt')
        y += 120
        
        # Top 5 list
        items = user_data.get(f'top_{item_type}', [])[:5]
        
        for i, item in enumerate(items, 1):
            # Rank circle
            draw.ellipse([(80, y - 25), (130, y + 25)],
                        fill=self.spotify_green if item_type == 'tracks' else (139, 69, 255))
            draw.text((105, y), str(i),
                     fill='white', font=self.fonts['header'], anchor='mm')
            
            # Item name
            if item_type == 'tracks':
                name = item.get('name', 'Unknown')[:35]
                artist = item.get('artist', 'Unknown')[:30]
                draw.text((160, y - 10), name,
                         fill='white', font=self.fonts['body'], anchor='lm')
                draw.text((160, y + 20), f"by {artist}",
                         fill=(200, 200, 200), font=self.fonts['caption'], anchor='lm')
                y += 140
            else:
                name = item.get('name', 'Unknown')[:35]
                genres = ', '.join(item.get('genres', [])[:2])
                draw.text((160, y - 10), name,
                         fill='white', font=self.fonts['body'], anchor='lm')
                if genres:
                    draw.text((160, y + 20), genres,
                             fill=(200, 200, 200), font=self.fonts['caption'], anchor='lm')
                y += 140
        
        # Footer
        y = self.height - 100
        draw.text((self.width // 2, y), "Spotify Wrapped Dashboard",
                 fill=(150, 150, 150), font=self.fonts['small'], anchor='mt')
        draw.text((self.width // 2, y + 35), "♫",
                 fill=self.spotify_green, font=self.fonts['header'], anchor='mt')
        
        return img
    
    def create_personality_card(self, user_data):
        """Create a music personality card."""
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        
        # Personality-based gradient
        personality = user_data.get('personality', {})
        if 'Party' in personality.get('type', ''):
            colors = [(255, 107, 107), (255, 230, 109)]  # Warm, energetic
        elif 'Deep' in personality.get('type', ''):
            colors = [(70, 70, 150), (20, 20, 60)]  # Deep, introspective
        elif 'Explorer' in personality.get('type', ''):
            colors = [(102, 126, 234), (118, 75, 162)]  # Adventurous
        else:
            colors = [(29, 185, 84), (25, 20, 20)]  # Default Spotify
        
        self.create_gradient_background(img, colors)
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        user_name = user_data.get('user_name', 'My')
        
        # Header
        y = 100
        draw.text((self.width // 2, y), f"{user_name}'s",
                 fill='white', font=self.fonts['header'], anchor='mt')
        y += 70
        draw.text((self.width // 2, y), "MUSIC PERSONALITY",
                 fill='white', font=self.fonts['title'], anchor='mt')
        y += 120
        
        # Big emoji
        emoji = personality.get('emoji', '🎵')
        draw.text((self.width // 2, y), emoji,
                 fill='white', font=ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 120) if os.path.exists("/System/Library/Fonts/Apple Color Emoji.ttc") else self.fonts['title'],
                 anchor='mt')
        y += 150
        
        # Personality type
        draw.text((self.width // 2, y), personality.get('type', 'Music Lover'),
                 fill='white', font=self.fonts['title'], anchor='mt')
        y += 100
        
        # Description
        desc = personality.get('description', '')
        # Word wrap
        words = desc.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 30:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines[:3]:  # Max 3 lines
            draw.text((self.width // 2, y), line,
                     fill=(230, 230, 230), font=self.fonts['body'], anchor='mt')
            y += 50
        
        y += 50
        
        # Audio features
        features = user_data.get('audio_features', {})
        if features:
            feature_stats = [
                (f"{int(features.get('energy', 0) * 100)}%", "Energy"),
                (f"{int(features.get('valence', 0) * 100)}%", "Happiness"),
                (f"{int(features.get('danceability', 0) * 100)}%", "Danceability"),
            ]
            
            x_positions = [self.width // 3 - 50, self.width // 2, 2 * self.width // 3 + 50]
            
            for i, (value, label) in enumerate(feature_stats):
                x = x_positions[i]
                draw.text((x, y), value,
                         fill='white', font=self.fonts['header'], anchor='mt')
                draw.text((x, y + 50), label,
                         fill=(200, 200, 200), font=self.fonts['caption'], anchor='mt')
        
        # Footer
        y = self.height - 100
        draw.text((self.width // 2, y), f"{year} Wrapped",
                 fill=(150, 150, 150), font=self.fonts['small'], anchor='mt')
        draw.text((self.width // 2, y + 35), "♫",
                 fill='white', font=self.fonts['header'], anchor='mt')
        
        return img
    
    def create_story_slides(self, user_data):
        """Create multiple Instagram story slides (1080x1920)."""
        slides = []
        story_height = 1920
        
        # Slide 1: Main summary
        # Slide 2: Top tracks
        # Slide 3: Top artists
        # Slide 4: Personality
        # Each optimized for story format
        
        # For now, return adapted versions
        slides.append(self.create_wrapped_summary_card(user_data))
        slides.append(self.create_top_5_card(user_data, 'tracks'))
        slides.append(self.create_top_5_card(user_data, 'artists'))
        if user_data.get('personality'):
            slides.append(self.create_personality_card(user_data))
        
        return slides
