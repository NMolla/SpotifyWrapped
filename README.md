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

2. **Run setup and configure**
   ```bash
   ./dev.sh setup    # Install all dependencies
   cp .env.example .env
   # Edit .env with your Spotify API credentials
   ```

3. **Run the application**

   ```bash
   ./dev.sh start    # Start both servers
   ./dev.sh stop     # Stop all servers
   ./dev.sh status   # Check server status
   ./dev.sh help     # See all commands
   ```
   
   **Individual server control:**
   ```bash
   ./dev.sh backend   # Start backend only
   ./dev.sh frontend  # Start frontend only
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

### All-in-one Development Tool
```bash
./dev.sh help     # Show all available commands
./dev.sh start    # Start development servers
./dev.sh stop     # Stop all servers
./dev.sh status   # Check what's running
./dev.sh clean    # Clean temporary files
./dev.sh setup    # Run initial setup
```

### Manual Development
```bash
# Backend only
./dev.sh backend

# Frontend only
./dev.sh frontend
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
