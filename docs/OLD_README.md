# Spotify Wrapped Dashboard 🎵

A beautiful, interactive web dashboard that connects to your Spotify account to create personalized Wrapped-style visualizations of your listening habits.

![Spotify Wrapped Dashboard](https://img.shields.io/badge/Spotify-1DB954?style=for-the-badge&logo=spotify&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

## ✨ Features

### 🔐 Spotify OAuth Integration
- Secure authentication with Spotify
- Access to user's top tracks and artists
- Multiple time range support (4 weeks, 6 months, all time)

### 📊 Data Visualizations
- **Top Tracks**: Interactive list with preview playback
- **Top Artists**: Beautiful cards with follower counts and genres
- **Genre Analysis**: Doughnut and bar charts showing genre distribution
- **Stats Overview**: Comprehensive listening statistics

### 🎨 Wrapped Summary Card
- Personalized, shareable Wrapped card
- Download as image
- Share directly from the browser
- Beautiful gradient designs

### 🎯 Key Metrics
- Most listened-to genre
- Favorite artist with image
- Song of the year
- Total listening time
- Average track popularity
- Music taste characteristics

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- Spotify Developer Account

### 1. Set up Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create App"
3. Fill in the app details:
   - App Name: "Spotify Wrapped Dashboard"
   - App Description: "Personal Spotify statistics dashboard"
   - Redirect URI: `http://127.0.0.1:5000/callback`
4. Save your **Client ID** and **Client Secret**

### 2. Backend Setup

```bash
# Clone the repository
cd SpotifyWrapped

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env file and add your Spotify credentials
# SPOTIFY_CLIENT_ID=your_client_id_here
# SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### 3. Frontend Setup

```bash
# Install Node dependencies
npm install

# Build CSS with Tailwind
npm run build:css
```

### 4. Run the Application

```bash
# Terminal 1: Start Flask backend
python app.py

# Terminal 2: Start React frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:5000

## 🎨 Tech Stack

### Frontend
- **React** - UI framework
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **Chart.js** - Data visualizations
- **Lucide React** - Icons
- **Axios** - API calls

### Backend
- **Flask** - Python web framework
- **Spotipy** - Spotify Web API wrapper
- **Flask-CORS** - Cross-origin support
- **Pillow** - Image generation
- **python-dotenv** - Environment management

## 📱 Features Overview

### Landing Page
- Beautiful animated design
- Feature highlights
- One-click Spotify login

### Dashboard
- **Overview Tab**: Key statistics and listening summary
- **Top Tracks Tab**: Your most played songs with audio preview
- **Top Artists Tab**: Favorite artists with genres and followers
- **Genres Tab**: Interactive genre distribution charts
- **Your Wrapped Tab**: Personalized shareable card

### Time Ranges
- **Last 4 Weeks**: Recent favorites
- **Last 6 Months**: Medium-term trends
- **All Time**: Your all-time classics

## 🛡️ Security

- OAuth 2.0 authentication flow
- No password storage
- Secure token management
- Session-based authentication
- Environment variable protection

## 🤝 Contributing

Feel free to fork this project and submit pull requests. Here are some ideas for contributions:
- Additional visualizations
- Social sharing features
- Playlist generation
- Music recommendations
- Historical data tracking

## 📄 License

This project is for educational purposes and is not affiliated with Spotify AB.

## 🐛 Troubleshooting

### Common Issues

**"No token provided" error**
- Make sure you're logged in
- Check that cookies are enabled
- Try logging out and back in

**Charts not showing**
- Ensure you have enough listening history
- Try different time ranges
- Check browser console for errors

**Can't login**
- Verify Spotify app credentials in .env
- Check redirect URI matches exactly
- Ensure backend is running on port 5000

## 📞 Support

If you encounter any issues:
1. Check the browser console for errors
2. Verify all environment variables are set
3. Ensure both frontend and backend are running
4. Check that your Spotify app settings are correct

---

Built with 💚 using the Spotify Web API