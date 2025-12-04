# 🎵 Spotify Wrapped Dashboard

A full-stack application that recreates the Spotify Wrapped experience with enhanced features and real-time data access.

## 📁 Project Structure

```
spotify-wrapped/
├── backend/              # Flask API server
│   ├── app.py           # Main Flask application
│   ├── json_storage.py  # Data persistence layer
│   ├── enhancements/    # Enhancement modules
│   └── templates/       # HTML templates
├── frontend/            # React application
│   ├── src/            # React source code
│   │   ├── components/ # React components
│   │   └── App.js     # Main app component
│   └── public/         # Static assets
├── tests/              # Test suites
├── docs/               # Documentation
├── scripts/            # Organized utility scripts
│   ├── dev/           # Development & server scripts
│   ├── setup/         # Setup variations
│   └── utils/         # Maintenance utilities
├── data/               # User data storage
├── config/             # Configuration files
├── setup.sh           # Main setup script
└── run_dev.sh         # Primary dev command
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Spotify Developer Account

### Setup

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd spotify-wrapped
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Spotify API credentials
   ```

3. **Run the application**

   **Option 1: Run in separate Terminal tabs (Recommended)**
   ```bash
   ./run_dev.sh                      # Primary dev command
   ./scripts/dev/run_dev_iterm.sh    # For iTerm2 users
   ```

   **Option 2: Run servers manually**
   
   Backend:
   ```bash
   ./scripts/dev/run_backend.sh
   ```
   
   Frontend (in new terminal):
   ```bash
   ./scripts/dev/run_frontend.sh
   ```
   
   **Stop all servers:**
   ```bash
   ./scripts/dev/kill_servers.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://127.0.0.1:5000

## 🎯 Features

- **OAuth Authentication**: Secure Spotify login
- **Multiple Time Ranges**: Last 4 weeks, 6 months, all-time data
- **Wrapped Experience**: Official Spotify Wrapped-style presentation
- **Data Visualizations**: Interactive charts and statistics
- **Shareable Cards**: Download and share your music stats
- **Wrapped Hub**: Access historical Wrapped data
- **Music Analysis**: Genre distribution, listening personality
- **Playlist Generator**: Create playlists from your top tracks

## 🛠️ Development

### Backend Development
```bash
cd backend
source ../.venv/bin/activate
python app.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Running Tests
```bash
cd tests
python test_all_features.py
```

## 📚 Documentation

- [Setup Guide](docs/START_HERE.md)
- [Frontend Access Guide](docs/FRONTEND_ACCESS_GUIDE.md)
- [Enhancement Features](docs/ENHANCED_FEATURES.md)
- [API Documentation](docs/README.md)

## 🔧 Configuration

### Spotify App Settings
1. Create app at https://developer.spotify.com
2. Set redirect URI to `http://127.0.0.1:5000/callback`
3. Add client ID and secret to `.env`

### Environment Variables
```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/callback
FLASK_SECRET_KEY=your_secret_key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is for educational purposes. Spotify and Spotify Wrapped are trademarks of Spotify AB.
