#!/usr/bin/env python3
"""
Official Spotify Wrapped Style Instagram Card Generator
Matches the exact aesthetic of Spotify's official Wrapped with thumbnails
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
from io import BytesIO
from datetime import datetime
import os
import colorsys

class OfficialWrappedGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1350  # Instagram portrait ratio
        
        # Official Spotify colors
        self.spotify_green = '#1DB954'
        self.spotify_black = '#191414'
        self.spotify_white = '#FFFFFF'
        self.spotify_gray = '#B3B3B3'
        
        # Official Wrapped gradients
        self.wrapped_gradients = {
            'main': [(236, 64, 122), (168, 58, 180), (88, 81, 219)],  # Pink to purple
            'alt': [(29, 185, 84), (24, 24, 24)],  # Green to black
            'warm': [(255, 107, 107), (255, 230, 109)],  # Red to yellow
            'cool': [(70, 130, 180), (106, 90, 205)],  # Blue to purple
            'dark': [(25, 20, 20), (45, 40, 40)]  # Dark gradient
        }
        
        # Load fonts - try to match Spotify's Circular font family
        self.fonts = self.load_spotify_fonts()
    
    def load_spotify_fonts(self):
        """Load fonts that match Spotify's style."""
        fonts = {}
        
        # Try to load fonts similar to Spotify's Circular
        font_options = [
            # First try SF Pro (similar to Circular)
            "/System/Library/Fonts/SFNSDisplay.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Avenir Next.ttc",
            # Fallbacks
            "Arial.ttf",
            "Helvetica.ttf",
        ]
        
        for font_path in font_options:
            try:
                # Different sizes for different uses
                fonts['huge'] = ImageFont.truetype(font_path, 96)
                fonts['title'] = ImageFont.truetype(font_path, 72)
                fonts['header'] = ImageFont.truetype(font_path, 48)
                fonts['subheader'] = ImageFont.truetype(font_path, 40)
                fonts['body'] = ImageFont.truetype(font_path, 32)
                fonts['caption'] = ImageFont.truetype(font_path, 24)
                fonts['small'] = ImageFont.truetype(font_path, 20)
                fonts['tiny'] = ImageFont.truetype(font_path, 18)
                break
            except:
                continue
        
        # Fallback to default if no fonts found
        if not fonts:
            default = ImageFont.load_default()
            fonts = {size: default for size in ['huge', 'title', 'header', 'subheader', 'body', 'caption', 'small', 'tiny']}
        
        return fonts
    
    def create_spotify_gradient(self, img, gradient_type='main'):
        """Create official Spotify Wrapped gradient background."""
        draw = ImageDraw.Draw(img)
        colors = self.wrapped_gradients.get(gradient_type, self.wrapped_gradients['main'])
        
        # Create smooth gradient with multiple color stops
        for i in range(self.height):
            ratio = i / self.height
            
            if len(colors) == 3:
                # Three color gradient
                if ratio < 0.5:
                    r1, g1, b1 = colors[0]
                    r2, g2, b2 = colors[1]
                    local_ratio = ratio * 2
                else:
                    r1, g1, b1 = colors[1]
                    r2, g2, b2 = colors[2]
                    local_ratio = (ratio - 0.5) * 2
                
                r = int(r1 * (1 - local_ratio) + r2 * local_ratio)
                g = int(g1 * (1 - local_ratio) + g2 * local_ratio)
                b = int(b1 * (1 - local_ratio) + b2 * local_ratio)
            else:
                # Two color gradient
                r1, g1, b1 = colors[0]
                r2, g2, b2 = colors[1]
                r = int(r1 * (1 - ratio) + r2 * ratio)
                g = int(g1 * (1 - ratio) + g2 * ratio)
                b = int(b1 * (1 - ratio) + b2 * ratio)
            
            draw.rectangle([(0, i), (self.width, i + 1)], fill=(r, g, b))
        
        return img
    
    def download_and_process_image(self, image_url, size=(300, 300)):
        """Download and process album/artist images."""
        try:
            response = requests.get(image_url, timeout=5)
            img = Image.open(BytesIO(response.content))
            
            # Make square crop
            img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
            
            # Add rounded corners
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), size], radius=20, fill=255)
            
            output = Image.new('RGBA', size, (0, 0, 0, 0))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            return output
        except:
            # Return placeholder if download fails
            placeholder = Image.new('RGBA', size, (100, 100, 100, 255))
            return placeholder
    
    def create_official_wrapped_summary(self, user_data):
        """Create official Spotify Wrapped style summary card."""
        # Create base image with gradient
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        self.create_spotify_gradient(img, 'main')
        
        # Add overlay for better text visibility
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Add semi-transparent dark overlay at top and bottom
        for i in range(200):
            alpha = int(150 * (1 - i/200))
            draw_overlay.rectangle([(0, i), (self.width, i+1)], fill=(0, 0, 0, alpha))
            draw_overlay.rectangle([(0, self.height-i-1), (self.width, self.height-i)], fill=(0, 0, 0, alpha))
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        user_name = user_data.get('user_name', 'Your')
        
        # Header - matching official style
        y = 60
        draw.text((self.width // 2, y), f"#{year}Wrapped", 
                 fill=self.spotify_white, font=self.fonts['body'], anchor='mt')
        
        y += 80
        draw.text((self.width // 2, y), f"{user_name}'s", 
                 fill=self.spotify_white, font=self.fonts['header'], anchor='mt')
        y += 70
        draw.text((self.width // 2, y), f"{year}", 
                 fill=self.spotify_white, font=self.fonts['huge'], anchor='mt')
        y += 100
        
        # Top artist with image
        top_artist = user_data.get('top_artist', {})
        if top_artist and top_artist.get('image'):
            artist_img = self.download_and_process_image(top_artist['image'], (200, 200))
            img.paste(artist_img, ((self.width - 200) // 2, y), artist_img)
            y += 220
            
            draw.text((self.width // 2, y), "YOUR TOP ARTIST",
                     fill=self.spotify_gray, font=self.fonts['small'], anchor='mt')
            y += 35
            draw.text((self.width // 2, y), top_artist.get('name', 'Unknown'),
                     fill=self.spotify_white, font=self.fonts['subheader'], anchor='mt')
            y += 80
        
        # Stats in modern card style
        stats = [
            (f"{user_data.get('total_minutes', 0):,}", "minutes"),
            (f"{user_data.get('unique_tracks', 0)}", "songs"),
            (f"{user_data.get('unique_artists', 0)}", "artists"),
        ]
        
        # Draw stats cards
        card_width = 280
        card_height = 100
        x_positions = [
            self.width // 2 - card_width - 20,
            self.width // 2 + 20
        ]
        
        for i, (value, label) in enumerate(stats[:2]):
            x = x_positions[i]
            
            # Draw card background
            card_bg = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 25))
            draw_card = ImageDraw.Draw(card_bg)
            draw_card.rounded_rectangle([(0, 0), (card_width, card_height)], 
                                       radius=15, fill=(255, 255, 255, 25))
            img.paste(card_bg, (x, y), card_bg)
            
            # Draw stats
            draw.text((x + card_width // 2, y + 30), value,
                     fill=self.spotify_white, font=self.fonts['subheader'], anchor='mt')
            draw.text((x + card_width // 2, y + 65), label.upper(),
                     fill=self.spotify_gray, font=self.fonts['tiny'], anchor='mt')
        
        y += 130
        
        # Top genre
        top_genre = user_data.get('top_genre', 'eclectic')
        draw.text((self.width // 2, y), "YOUR MUSIC IS",
                 fill=self.spotify_gray, font=self.fonts['small'], anchor='mt')
        y += 35
        draw.text((self.width // 2, y), top_genre.upper(),
                 fill=self.spotify_green, font=self.fonts['header'], anchor='mt')
        
        # Footer
        y = self.height - 60
        draw.text((self.width // 2, y), "SPOTIFY WRAPPED",
                 fill=self.spotify_gray, font=self.fonts['tiny'], anchor='mt')
        
        return img
    
    def create_official_top_tracks(self, user_data):
        """Create official Spotify Wrapped style top tracks card."""
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        self.create_spotify_gradient(img, 'warm')
        
        # Add dark overlay for text visibility
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 40))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        
        # Header
        y = 50
        draw.text((self.width // 2, y), f"#{year}Wrapped",
                 fill=self.spotify_white, font=self.fonts['caption'], anchor='mt')
        y += 50
        draw.text((self.width // 2, y), "YOUR TOP 10 SONGS",
                 fill=self.spotify_white, font=self.fonts['header'], anchor='mt')
        y += 80
        
        # Top tracks with album art - now showing 10 with smaller spacing
        tracks = user_data.get('top_tracks', [])[:10]
        
        for i, track in enumerate(tracks, 1):
            # Smaller album art for 10 items
            if track.get('image'):
                album_img = self.download_and_process_image(track['image'], (80, 80))
                img.paste(album_img, (80, y), album_img)
            else:
                # Placeholder
                draw.rounded_rectangle([(80, y), (160, y + 80)], 
                                      radius=8, fill=(50, 50, 50))
            
            # Rank number
            draw.text((50, y + 40), str(i) if i < 10 else "10",
                     fill=self.spotify_white, font=self.fonts['subheader'], anchor='mm')
            
            # Track info with smaller fonts
            track_name = track.get('name', 'Unknown')[:28]
            artist_name = track.get('artist', 'Unknown')[:25]
            
            draw.text((175, y + 20), track_name,
                     fill=self.spotify_white, font=self.fonts['caption'], anchor='lm')
            draw.text((175, y + 50), artist_name,
                     fill=self.spotify_gray, font=self.fonts['small'], anchor='lm')
            
            y += 95  # Reduced spacing
        
        # Footer
        y = self.height - 60
        draw.text((self.width // 2, y), "SPOTIFY WRAPPED",
                 fill=self.spotify_gray, font=self.fonts['tiny'], anchor='mt')
        
        return img
    
    def create_official_top_artists(self, user_data):
        """Create official Spotify Wrapped style top artists card."""
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        self.create_spotify_gradient(img, 'cool')
        
        # Add overlay
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 30))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        
        # Header
        y = 50
        draw.text((self.width // 2, y), f"#{year}Wrapped",
                 fill=self.spotify_white, font=self.fonts['caption'], anchor='mt')
        y += 50
        draw.text((self.width // 2, y), "YOUR TOP 10 ARTISTS",
                 fill=self.spotify_white, font=self.fonts['header'], anchor='mt')
        y += 80
        
        # Top artists with images - now showing 10 with smaller spacing
        artists = user_data.get('top_artists', [])[:10]
        
        for i, artist in enumerate(artists, 1):
            # Smaller artist image (circular)
            if artist.get('image'):
                artist_img = self.download_and_process_image(artist['image'], (80, 80))
                
                # Make circular
                mask = Image.new('L', (80, 80), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse([(0, 0), (80, 80)], fill=255)
                
                circular_img = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
                circular_img.paste(artist_img, (0, 0))
                circular_img.putalpha(mask)
                
                img.paste(circular_img, (80, y), circular_img)
            else:
                # Placeholder circle
                draw.ellipse([(80, y), (160, y + 80)], fill=(50, 50, 50))
            
            # Rank
            draw.text((50, y + 40), str(i) if i < 10 else "10",
                     fill=self.spotify_white, font=self.fonts['subheader'], anchor='mm')
            
            # Artist info with smaller fonts
            artist_name = artist.get('name', 'Unknown')[:28]
            genres = ', '.join(artist.get('genres', [])[:1])  # Only 1 genre to save space
            
            draw.text((175, y + 20), artist_name,
                     fill=self.spotify_white, font=self.fonts['caption'], anchor='lm')
            if genres:
                draw.text((175, y + 50), genres.title()[:25],
                         fill=self.spotify_gray, font=self.fonts['small'], anchor='lm')
            
            y += 95  # Reduced spacing
        
        # Footer
        y = self.height - 60
        draw.text((self.width // 2, y), "SPOTIFY WRAPPED",
                 fill=self.spotify_gray, font=self.fonts['tiny'], anchor='mt')
        
        return img
    
    def create_official_listening_personality(self, user_data):
        """Create official Spotify Wrapped style listening personality card."""
        img = Image.new('RGB', (self.width, self.height), self.spotify_black)
        
        # Choose gradient based on personality
        personality = user_data.get('personality', {})
        personality_type = personality.get('type', '')
        
        if 'Party' in personality_type:
            gradient = 'warm'
        elif 'Deep' in personality_type or 'Thinker' in personality_type:
            gradient = 'cool'
        else:
            gradient = 'main'
        
        self.create_spotify_gradient(img, gradient)
        
        # Add overlay
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 20))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        year = user_data.get('year', datetime.now().year)
        
        # Header
        y = 60
        draw.text((self.width // 2, y), f"#{year}Wrapped",
                 fill=self.spotify_white, font=self.fonts['body'], anchor='mt')
        y += 80
        draw.text((self.width // 2, y), "YOUR LISTENING",
                 fill=self.spotify_white, font=self.fonts['header'], anchor='mt')
        y += 60
        draw.text((self.width // 2, y), "PERSONALITY",
                 fill=self.spotify_white, font=self.fonts['header'], anchor='mt')
        y += 120
        
        # Personality type
        draw.text((self.width // 2, y), personality.get('type', 'Music Explorer').upper(),
                 fill=self.spotify_green, font=self.fonts['title'], anchor='mt')
        y += 100
        
        # Description
        desc = personality.get('description', 'You have a unique taste in music.')
        words = desc.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 35:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines[:4]:
            draw.text((self.width // 2, y), line,
                     fill=self.spotify_white, font=self.fonts['caption'], anchor='mt')
            y += 40
        
        y += 60
        
        # Audio features visualization
        features = user_data.get('audio_features', {})
        if features:
            # Draw feature bars
            feature_data = [
                ('ENERGY', features.get('energy', 0)),
                ('MOOD', features.get('valence', 0)),
                ('DANCEABILITY', features.get('danceability', 0))
            ]
            
            bar_width = 600
            bar_height = 40
            x_start = (self.width - bar_width) // 2
            
            for label, value in feature_data:
                # Label
                draw.text((x_start, y), label,
                         fill=self.spotify_gray, font=self.fonts['small'], anchor='lm')
                
                # Background bar
                draw.rounded_rectangle([(x_start, y + 25), (x_start + bar_width, y + 25 + bar_height)],
                                      radius=20, fill=(255, 255, 255, 30))
                
                # Value bar
                fill_width = int(bar_width * value)
                if fill_width > 0:
                    draw.rounded_rectangle([(x_start, y + 25), (x_start + fill_width, y + 25 + bar_height)],
                                          radius=20, fill=self.spotify_green)
                
                # Percentage
                draw.text((x_start + bar_width + 20, y + 25 + bar_height // 2), 
                         f"{int(value * 100)}%",
                         fill=self.spotify_white, font=self.fonts['caption'], anchor='lm')
                
                y += 80
        
        # Footer
        y = self.height - 60
        draw.text((self.width // 2, y), "SPOTIFY WRAPPED",
                 fill=self.spotify_gray, font=self.fonts['tiny'], anchor='mt')
        
        return img
