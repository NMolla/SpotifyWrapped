import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './WrappedHub.css';

const WrappedHub = () => {
  const [loading, setLoading] = useState(false);
  const [wrappedData, setWrappedData] = useState(null);
  const [wrappedStats, setWrappedStats] = useState(null);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedTimeRange, setSelectedTimeRange] = useState('long_term');
  const [activeTab, setActiveTab] = useState('overview');
  const [audioFeatures, setAudioFeatures] = useState(null);
  const [recentlyPlayed, setRecentlyPlayed] = useState(null);
  const [musicEvolution, setMusicEvolution] = useState(null);
  const [listeningStats, setListeningStats] = useState(null);

  useEffect(() => {
    fetchWrappedData();
    fetchWrappedStats(); // Fetch stats on initial load too
  }, []);

  useEffect(() => {
    fetchWrappedData();
  }, [selectedYear]);

  useEffect(() => {
    fetchWrappedStats();
    // Also clear audio features when time range changes so they'll be refetched
    setAudioFeatures(null);
  }, [selectedTimeRange]);

  const fetchWrappedData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/spotify-wrapped/${selectedYear}`);
      setWrappedData(response.data);
    } catch (error) {
      console.error('Error fetching wrapped data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWrappedStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/wrapped-stats/${selectedTimeRange}`);
      
      // Also fetch top tracks and artists for the overview
      const tracksResponse = await axios.get(`http://127.0.0.1:5000/api/top/tracks/${selectedTimeRange}`);
      const artistsResponse = await axios.get(`http://127.0.0.1:5000/api/top/artists/${selectedTimeRange}`);
      
      // The API returns arrays directly, not objects with items property
      const combinedData = {
        ...response.data,
        top_tracks: Array.isArray(tracksResponse.data) ? tracksResponse.data.slice(0, 10) : [],
        top_artists: Array.isArray(artistsResponse.data) ? artistsResponse.data.slice(0, 10) : []
      };
      
      setWrappedStats(combinedData);
    } catch (error) {
      console.error('Error fetching wrapped stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAudioFeatures = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/audio-features/${selectedTimeRange}`);
      setAudioFeatures(response.data);
    } catch (error) {
      console.error('Error fetching audio features:', error);
    }
  };

  const fetchRecentlyPlayed = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/recently-played');
      setRecentlyPlayed(response.data);
    } catch (error) {
      console.error('Error fetching recently played:', error);
    }
  };

  const fetchMusicEvolution = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/music-evolution');
      setMusicEvolution(response.data);
    } catch (error) {
      console.error('Error fetching music evolution:', error);
    }
  };

  const fetchListeningStats = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/listening-stats');
      setListeningStats(response.data);
    } catch (error) {
      console.error('Error fetching listening stats:', error);
    }
  };

  const createPlaylist = async (type, mood = null) => {
    try {
      const body = {
        type: type,
        time_range: selectedTimeRange,
        public: true
      };
      
      if (mood) {
        body.mood = mood;
      }

      const response = await axios.post('http://127.0.0.1:5000/api/create-playlist', body);
      if (response.data.success) {
        alert(`Playlist created! ${response.data.tracks_added} tracks added.`);
        window.open(response.data.playlist_url, '_blank');
      }
    } catch (error) {
      console.error('Error creating playlist:', error);
      alert('Failed to create playlist');
    }
  };

  const downloadInstagramCard = (cardType) => {
    const url = `http://127.0.0.1:5000/api/instagram-wrapped/${cardType}?time_range=${selectedTimeRange}`;
    window.open(url, '_blank');
  };

  const downloadAllCards = () => {
    const url = `http://127.0.0.1:5000/api/instagram-wrapped-download?time_range=${selectedTimeRange}`;
    window.open(url, '_blank');
  };

  const syncData = async () => {
    setLoading(true);
    try {
      await axios.post('http://127.0.0.1:5000/api/sync', { force: true });
      alert('Data synced successfully!');
      fetchWrappedData();
    } catch (error) {
      console.error('Error syncing data:', error);
      alert('Failed to sync data');
    } finally {
      setLoading(false);
    }
  };

  const getTimeRangeLabel = (range) => {
    switch(range) {
      case 'short_term': return 'Last 4 Weeks';
      case 'medium_term': return 'Last 6 Months';
      case 'long_term': return 'All Time';
      default: return range;
    }
  };

  const renderOverviewTab = () => (
    <div className="overview-tab">
      {wrappedStats && (
        <>
          <div className="time-range-indicator">
            <p>Showing data for: <strong>{getTimeRangeLabel(selectedTimeRange)}</strong></p>
          </div>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{wrappedStats.total_minutes?.toLocaleString() || '0'}</h3>
              <p>Minutes Listened</p>
            </div>
            <div className="stat-card">
              <h3>{wrappedStats.top_genre || 'N/A'}</h3>
              <p>Top Genre</p>
            </div>
            <div className="stat-card">
              <h3>{wrappedStats.total_artists || 0}</h3>
              <p>Different Artists</p>
            </div>
            <div className="stat-card">
              <h3>{wrappedStats.top_genres?.length || 0}</h3>
              <p>Genres Explored</p>
            </div>
          </div>

          <div className="top-items">
            <div className="top-section">
              <h2>Top 10 Tracks</h2>
              <div className="items-grid">
                {wrappedStats.top_tracks && wrappedStats.top_tracks.length > 0 ? (
                  wrappedStats.top_tracks.map((track, index) => (
                    <div key={track.id || index} className="item-compact">
                      <span className="rank">{index + 1}</span>
                      {track.image && <img src={track.image} alt={track.name} />}
                      <div className="item-info">
                        <p className="name">{track.name}</p>
                        <p className="artist">{track.artist || 'Unknown'}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="no-data">No tracks data available</p>
                )}
              </div>
            </div>

            <div className="top-section">
              <h2>Top 10 Artists</h2>
              <div className="items-grid">
                {wrappedStats.top_artists && wrappedStats.top_artists.length > 0 ? (
                  wrappedStats.top_artists.map((artist, index) => (
                    <div key={artist.id || index} className="item-compact">
                      <span className="rank">{index + 1}</span>
                      {artist.image && <img src={artist.image} alt={artist.name} className="artist-img" />}
                      <div className="item-info">
                        <p className="name">{artist.name}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="no-data">No artists data available</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderPersonalityTab = () => (
    <div className="personality-tab">
      <button onClick={fetchAudioFeatures} className="btn btn-primary">
        Analyze My Music Personality
      </button>
      
      {audioFeatures && (
        <div className="personality-display">
          {audioFeatures.listening_personality && (
            <div className="personality-card">
              <div className="personality-emoji">{audioFeatures.listening_personality.emoji}</div>
              <h2>{audioFeatures.listening_personality.type}</h2>
              <p>{audioFeatures.listening_personality.description}</p>
            </div>
          )}
          
          <div className="audio-features">
            <div className="feature">
              <div className="feature-bar">
                <div className="feature-fill" style={{width: `${audioFeatures.energy?.average * 100}%`}}></div>
              </div>
              <p>Energy: {audioFeatures.energy?.description}</p>
            </div>
            <div className="feature">
              <div className="feature-bar">
                <div className="feature-fill" style={{width: `${audioFeatures.valence?.average * 100}%`}}></div>
              </div>
              <p>Mood: {audioFeatures.valence?.description}</p>
            </div>
            <div className="feature">
              <div className="feature-bar">
                <div className="feature-fill" style={{width: `${audioFeatures.danceability?.average * 100}%`}}></div>
              </div>
              <p>Danceability: {audioFeatures.danceability?.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPatternsTab = () => (
    <div className="patterns-tab">
      <div className="patterns-actions">
        <button onClick={fetchRecentlyPlayed} className="btn btn-primary">
          Analyze Listening Patterns
        </button>
        <button onClick={fetchMusicEvolution} className="btn btn-secondary">
          Show Music Evolution
        </button>
        <button onClick={fetchListeningStats} className="btn btn-secondary">
          Get Deep Stats
        </button>
      </div>
      
      {recentlyPlayed?.patterns && (
        <div className="patterns-display">
          <h3>Your Listening Patterns</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <h4>{recentlyPlayed.patterns.peak_listening_hour}:00</h4>
              <p>Peak Hour</p>
            </div>
            <div className="stat-card">
              <h4>{recentlyPlayed.patterns.peak_listening_day || 'N/A'}</h4>
              <p>Most Active Day</p>
            </div>
            <div className="stat-card">
              <h4>{recentlyPlayed.patterns.total_unique_tracks}</h4>
              <p>Unique Tracks</p>
            </div>
            <div className="stat-card">
              <h4>{recentlyPlayed.patterns.repeated_tracks_count}</h4>
              <p>On Repeat</p>
            </div>
          </div>
        </div>
      )}
      
      {musicEvolution?.trends && (
        <div className="evolution-display">
          <h3>Music Evolution Trends</h3>
          {Object.entries(musicEvolution.trends).map(([key, trend]) => (
            <div key={key} className="trend-item">
              <span>{key.replace('avg_', '').replace('_', ' ')}</span>
              <span className={`trend-direction ${trend.direction}`}>
                {trend.direction === 'increasing' ? '↑' : '↓'} {trend.percentage.toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      )}
      
      {listeningStats && (
        <div className="deep-stats">
          <h3>Comprehensive Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <h4>{listeningStats.total_unique_tracks}</h4>
              <p>Unique Tracks</p>
            </div>
            <div className="stat-card">
              <h4>{listeningStats.total_unique_artists}</h4>
              <p>Different Artists</p>
            </div>
            <div className="stat-card">
              <h4>{listeningStats.estimated_minutes}</h4>
              <p>Minutes Total</p>
            </div>
            <div className="stat-card">
              <h4>{listeningStats.diversity_score?.toFixed(0)}%</h4>
              <p>Diversity Score</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPlaylistsTab = () => (
    <div className="playlists-tab">
      <h2>Create Spotify Playlists</h2>
      <div className="playlist-options">
        <button onClick={() => createPlaylist('top_tracks')} className="playlist-btn">
          📝 Top Tracks Playlist
        </button>
        <button onClick={() => createPlaylist('mood', 'happy')} className="playlist-btn">
          😊 Happy Mood
        </button>
        <button onClick={() => createPlaylist('mood', 'sad')} className="playlist-btn">
          😢 Sad Mood
        </button>
        <button onClick={() => createPlaylist('mood', 'energetic')} className="playlist-btn">
          ⚡ Energetic
        </button>
        <button onClick={() => createPlaylist('mood', 'chill')} className="playlist-btn">
          😌 Chill Vibes
        </button>
        <button onClick={() => createPlaylist('discovery')} className="playlist-btn">
          🔍 Discovery
        </button>
      </div>
    </div>
  );

  const renderShareTab = () => (
    <div className="share-tab">
      <h2>Instagram Share Cards</h2>
      <p>Download beautiful cards to share on Instagram</p>
      
      <div className="cards-grid">
        <div className="card-option">
          <div className="card-preview summary-preview">
            <span>📊</span>
            <h3>Wrapped Summary</h3>
          </div>
          <button onClick={() => downloadInstagramCard('summary')} className="btn btn-primary">
            Download
          </button>
        </div>
        
        <div className="card-option">
          <div className="card-preview tracks-preview">
            <span>🎵</span>
            <h3>Top 10 Tracks</h3>
          </div>
          <button onClick={() => downloadInstagramCard('tracks')} className="btn btn-primary">
            Download
          </button>
        </div>
        
        <div className="card-option">
          <div className="card-preview artists-preview">
            <span>🎤</span>
            <h3>Top 10 Artists</h3>
          </div>
          <button onClick={() => downloadInstagramCard('artists')} className="btn btn-primary">
            Download
          </button>
        </div>
        
        <div className="card-option">
          <div className="card-preview personality-preview">
            <span>🎭</span>
            <h3>Music Personality</h3>
          </div>
          <button onClick={() => downloadInstagramCard('personality')} className="btn btn-primary">
            Download
          </button>
        </div>
      </div>
      
      <div className="download-all-section">
        <button onClick={downloadAllCards} className="btn btn-success btn-large">
          📦 Download All Cards as ZIP
        </button>
      </div>
    </div>
  );

  return (
    <div className="wrapped-hub">
      <header className="hub-header">
        <h1>🎵 Spotify Wrapped Hub</h1>
        <p>All your Wrapped features in one place</p>
        
        <div className="controls">
          <select value={selectedYear} onChange={(e) => setSelectedYear(e.target.value)}>
            <option value="2025">2025</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
          </select>
          
          <select value={selectedTimeRange} onChange={(e) => setSelectedTimeRange(e.target.value)}>
            <option value="long_term">All Time</option>
            <option value="medium_term">Last 6 Months</option>
            <option value="short_term">Last 4 Weeks</option>
          </select>
          
          <button onClick={syncData} className="btn btn-secondary">
            🔄 Sync Data
          </button>
        </div>
      </header>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'personality' ? 'active' : ''}`}
          onClick={() => setActiveTab('personality')}
        >
          Personality
        </button>
        <button 
          className={`tab ${activeTab === 'patterns' ? 'active' : ''}`}
          onClick={() => setActiveTab('patterns')}
        >
          Patterns & Stats
        </button>
        <button 
          className={`tab ${activeTab === 'playlists' ? 'active' : ''}`}
          onClick={() => setActiveTab('playlists')}
        >
          Create Playlists
        </button>
        <button 
          className={`tab ${activeTab === 'share' ? 'active' : ''}`}
          onClick={() => setActiveTab('share')}
        >
          Instagram Share
        </button>
      </div>
      
      <div className="tab-content">
        {loading && <div className="loading">Loading...</div>}
        {!loading && activeTab === 'overview' && renderOverviewTab()}
        {!loading && activeTab === 'personality' && renderPersonalityTab()}
        {!loading && activeTab === 'patterns' && renderPatternsTab()}
        {!loading && activeTab === 'playlists' && renderPlaylistsTab()}
        {!loading && activeTab === 'share' && renderShareTab()}
      </div>
    </div>
  );
};

export default WrappedHub;
