#!/usr/bin/env python3
"""
Visual Card Generator for Spotify Wrapped
Create shareable image cards from your wrapped data
"""

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Any, Tuple
import numpy as np

class WrappedCardGenerator:
    """Generate visual cards for Spotify Wrapped data."""
    
    def __init__(self):
        # Define color schemes
        self.spotify_green = '#1DB954'
        self.spotify_black = '#191414'
        self.gradient_colors = [
            '#FF6B6B',  # Red
            '#4ECDC4',  # Teal
            '#45B7D1',  # Blue
            '#96E6B3',  # Green
            '#F7B731',  # Yellow
            '#5F27CD',  # Purple
        ]
    
    def create_top_artists_card(self, artists: List[Dict], user_name: str = "Your") -> Image.Image:
        """Create a visual card for top artists."""
        
        # Create base image
        width, height = 1080, 1350
        img = Image.new('RGB', (width, height), self.spotify_black)
        draw = ImageDraw.Draw(img)
        
        # Try to load custom font, fall back to default
        try:
            title_font = ImageFont.truetype("Arial-Bold.ttf", 72)
            artist_font = ImageFont.truetype("Arial.ttf", 48)
            subtitle_font = ImageFont.truetype("Arial.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            artist_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw gradient background
        for i in range(height):
            color_ratio = i / height
            r = int(25 * (1 - color_ratio) + 29 * color_ratio)
            g = int(20 * (1 - color_ratio) + 185 * color_ratio)
            b = int(20 * (1 - color_ratio) + 84 * color_ratio)
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
        
        # Add title
        title = f"{user_name} Top Artists"
        draw.text((width//2, 100), title, fill='white', font=title_font, anchor='mt')
        
        # Add subtitle
        subtitle = "Spotify Wrapped 2024"
        draw.text((width//2, 200), subtitle, fill=(200, 200, 200), font=subtitle_font, anchor='mt')
        
        # Add artists
        y_position = 350
        for i, artist in enumerate(artists[:5], 1):
            # Draw rank circle
            draw.ellipse([(50, y_position-30), (110, y_position+30)], 
                        fill=self.spotify_green, outline='white', width=3)
            draw.text((80, y_position), str(i), fill='white', font=artist_font, anchor='mm')
            
            # Draw artist name
            name = artist.get('name', 'Unknown')
            draw.text((150, y_position), name, fill='white', font=artist_font, anchor='lm')
            
            # Draw genres
            genres = ', '.join(artist.get('genres', [])[:3])
            if genres:
                draw.text((150, y_position + 40), genres, 
                         fill=(180, 180, 180), font=subtitle_font, anchor='lm')
            
            y_position += 180
        
        # Add Spotify branding
        draw.text((width//2, height - 50), "Generated with ♫ Spotify Wrapped Dashboard", 
                 fill=(150, 150, 150), font=subtitle_font, anchor='mb')
        
        return img
    
    def create_genre_pie_chart(self, genre_stats: Dict[str, int], user_name: str = "Your") -> Image.Image:
        """Create a pie chart visualization of genre distribution."""
        
        # Prepare data
        genres = list(genre_stats.keys())[:8]  # Top 8 genres
        sizes = [genre_stats[g] for g in genres]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 12), facecolor=self.spotify_black)
        ax.set_facecolor(self.spotify_black)
        
        # Create pie chart
        colors = self.gradient_colors * 2  # Ensure enough colors
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=genres,
            colors=colors[:len(genres)],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': 'white', 'fontsize': 14}
        )
        
        # Beautify the text
        for text in texts:
            text.set_color('white')
            text.set_fontsize(16)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Add title
        plt.title(f"{user_name} Music Taste Distribution", 
                 color='white', fontsize=24, pad=20, fontweight='bold')
        
        # Add subtitle
        plt.text(0, -1.3, "Spotify Wrapped 2024", 
                ha='center', color='gray', fontsize=16)
        
        # Convert to PIL Image
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor=self.spotify_black, 
                   bbox_inches='tight', dpi=100)
        buf.seek(0)
        img = Image.open(buf)
        plt.close()
        
        return img
    
    def create_stats_card(self, stats: Dict[str, Any], user_name: str = "Your") -> Image.Image:
        """Create a statistics summary card."""
        
        # Create base image
        width, height = 1080, 1350
        img = Image.new('RGB', (width, height), self.spotify_black)
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("Arial-Bold.ttf", 72)
            stat_font = ImageFont.truetype("Arial-Bold.ttf", 96)
            label_font = ImageFont.truetype("Arial.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
        
        # Draw gradient
        for i in range(height):
            color_ratio = i / height
            r = int(91 * (1 - color_ratio) + 29 * color_ratio)
            g = int(39 * (1 - color_ratio) + 185 * color_ratio)
            b = int(205 * (1 - color_ratio) + 84 * color_ratio)
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
        
        # Title
        draw.text((width//2, 100), f"{user_name} Year in Music", 
                 fill='white', font=title_font, anchor='mt')
        
        # Stats grid
        stats_data = [
            (stats.get('total_minutes', 0), "Minutes Listened"),
            (stats.get('total_tracks', 0), "Unique Tracks"),
            (stats.get('total_artists', 0), "Different Artists"),
            (stats.get('top_genre', 'Unknown'), "Top Genre"),
            (f"{stats.get('avg_popularity', 0):.0f}%", "Avg Track Popularity"),
            (stats.get('discovery_score', 'High'), "Discovery Level")
        ]
        
        # Draw stats in 2x3 grid
        x_positions = [width//3, 2*width//3]
        y_positions = [400, 650, 900]
        
        for i, (value, label) in enumerate(stats_data):
            x = x_positions[i % 2]
            y = y_positions[i // 2]
            
            # Draw stat box
            box_width, box_height = 280, 180
            box_x = x - box_width//2
            box_y = y - box_height//2
            
            # Draw rounded rectangle
            draw.rounded_rectangle(
                [(box_x, box_y), (box_x + box_width, box_y + box_height)],
                radius=20,
                fill=(255, 255, 255, 30),
                outline=self.spotify_green,
                width=3
            )
            
            # Draw value
            draw.text((x, y - 20), str(value), 
                     fill=self.spotify_green, font=stat_font, anchor='mm')
            
            # Draw label
            draw.text((x, y + 40), label, 
                     fill='white', font=label_font, anchor='mm')
        
        # Footer
        draw.text((width//2, height - 50), "Spotify Wrapped Dashboard", 
                 fill=(200, 200, 200), font=label_font, anchor='mb')
        
        return img
    
    def create_timeline_visualization(self, evolution_data: Dict) -> Image.Image:
        """Create a timeline showing music taste evolution."""
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.spotify_black)
        ax.set_facecolor(self.spotify_black)
        
        # Sample data structure
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Simulate energy/mood over time
        energy_values = evolution_data.get('energy', np.random.rand(12) * 0.3 + 0.5)
        mood_values = evolution_data.get('mood', np.random.rand(12) * 0.3 + 0.4)
        
        x = np.arange(len(months))
        
        # Plot lines
        ax.plot(x, energy_values, color=self.spotify_green, linewidth=3, 
               label='Energy Level', marker='o', markersize=8)
        ax.plot(x, mood_values, color='#FF6B6B', linewidth=3, 
               label='Mood (Happiness)', marker='s', markersize=8)
        
        # Styling
        ax.set_xlabel('Month', color='white', fontsize=14)
        ax.set_ylabel('Level', color='white', fontsize=14)
        ax.set_title('Your Music Journey Through 2024', 
                    color='white', fontsize=18, pad=20, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(months, color='white')
        ax.tick_params(colors='white')
        
        # Grid
        ax.grid(True, alpha=0.2, color='white')
        
        # Legend
        legend = ax.legend(loc='upper left', framealpha=0.9)
        legend.get_frame().set_facecolor(self.spotify_black)
        for text in legend.get_texts():
            text.set_color('white')
        
        # Convert to image
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor=self.spotify_black, 
                   bbox_inches='tight', dpi=100)
        buf.seek(0)
        img = Image.open(buf)
        plt.close()
        
        return img
    
    def combine_images_grid(self, images: List[Image.Image]) -> Image.Image:
        """Combine multiple images into a grid."""
        
        if not images:
            return None
        
        # Calculate grid dimensions
        n = len(images)
        cols = 2
        rows = (n + 1) // 2
        
        # Get max dimensions
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # Create combined image
        combined_width = max_width * cols
        combined_height = max_height * rows
        combined = Image.new('RGB', (combined_width, combined_height), self.spotify_black)
        
        # Paste images
        for i, img in enumerate(images):
            x = (i % cols) * max_width
            y = (i // cols) * max_height
            combined.paste(img, (x, y))
        
        return combined
    
    def save_all_cards(self, user_data: Dict, output_dir: str = "wrapped_cards"):
        """Generate and save all card types."""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        cards = []
        
        # Top artists card
        if user_data.get('top_artists'):
            artist_card = self.create_top_artists_card(
                user_data['top_artists'], 
                user_data.get('user_name', 'Your')
            )
            artist_card.save(f"{output_dir}/top_artists.png")
            cards.append(artist_card)
        
        # Genre pie chart
        if user_data.get('genre_stats'):
            genre_card = self.create_genre_pie_chart(
                user_data['genre_stats'],
                user_data.get('user_name', 'Your')
            )
            genre_card.save(f"{output_dir}/genres.png")
            cards.append(genre_card)
        
        # Stats card
        if user_data.get('stats'):
            stats_card = self.create_stats_card(
                user_data['stats'],
                user_data.get('user_name', 'Your')
            )
            stats_card.save(f"{output_dir}/stats.png")
            cards.append(stats_card)
        
        # Timeline
        if user_data.get('evolution'):
            timeline_card = self.create_timeline_visualization(
                user_data['evolution']
            )
            timeline_card.save(f"{output_dir}/timeline.png")
            cards.append(timeline_card)
        
        # Create combined image
        if cards:
            combined = self.combine_images_grid(cards)
            combined.save(f"{output_dir}/all_cards.png")
        
        return f"Cards saved to {output_dir}/"

# Flask endpoint integration
@app.route('/api/generate-visual-cards', methods=['POST'])
def generate_visual_cards():
    """Generate visual cards from wrapped data."""
    
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = get_user_id()
    time_range = request.json.get('time_range', 'medium_term')
    
    # Get data
    top_artists = storage.load_top_artists(user_id, time_range)
    top_tracks = storage.load_top_tracks(user_id, time_range)
    
    # Calculate genre stats
    genre_stats = {}
    for artist in top_artists:
        for genre in artist.get('genres', []):
            genre_stats[genre] = genre_stats.get(genre, 0) + 1
    
    # Get user info
    user = sp.current_user()
    
    # Prepare data
    user_data = {
        'user_name': user.get('display_name', 'Your'),
        'top_artists': top_artists[:10],
        'genre_stats': genre_stats,
        'stats': {
            'total_minutes': sum(t.get('duration_ms', 0) for t in top_tracks) // 60000,
            'total_tracks': len(top_tracks),
            'total_artists': len(top_artists),
            'top_genre': max(genre_stats.keys(), key=genre_stats.get) if genre_stats else 'Unknown',
            'avg_popularity': sum(t.get('popularity', 0) for t in top_tracks) / len(top_tracks) if top_tracks else 0
        }
    }
    
    # Generate cards
    generator = WrappedCardGenerator()
    result = generator.save_all_cards(user_data)
    
    return jsonify({'success': True, 'message': result})
