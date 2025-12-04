import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Music, User, LogOut, Download, Clock, TrendingUp, 
  Award, Hash, Calendar, Play, BarChart3, Loader2,
  ChevronLeft, ChevronRight, Sparkles
} from 'lucide-react';
import TopTracks from './TopTracks';
import TopArtists from './TopArtists';
import GenreChart from './GenreChart';
import WrappedCard from './WrappedCard';
import StatsOverview from './StatsOverview';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('medium_term');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showWrappedCard, setShowWrappedCard] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'tracks', label: 'Top Tracks', icon: <Music className="w-4 h-4" /> },
    { id: 'artists', label: 'Top Artists', icon: <User className="w-4 h-4" /> },
    { id: 'genres', label: 'Genres', icon: <Hash className="w-4 h-4" /> },
    { id: 'wrapped', label: 'Your Wrapped', icon: <Award className="w-4 h-4" /> }
  ];

  const timeRanges = [
    { value: 'short_term', label: '4 Weeks', icon: <Clock className="w-4 h-4" /> },
    { value: 'medium_term', label: '6 Months', icon: <Calendar className="w-4 h-4" /> },
    { value: 'long_term', label: 'All Time', icon: <TrendingUp className="w-4 h-4" /> }
  ];

  useEffect(() => {
    fetchUserData();
  }, []);

  useEffect(() => {
    fetchStats();
  }, [timeRange]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/user');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/wrapped-stats/${timeRange}`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.get('http://127.0.0.1:5000/logout');
      window.location.href = '/';
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const downloadWrappedCard = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/generate-wrapped-card?time_range=${timeRange}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'spotify-wrapped.png');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading wrapped card:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-spotify-black via-spotify-darkgray to-spotify-black">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-spotify-gray/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Music className="w-8 h-8 text-spotify-green" />
              <h1 className="text-2xl font-bold text-white">Your Spotify Wrapped</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/wrapped')}
                className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-spotify-green to-green-500 text-black font-bold rounded-full hover:scale-105 transition-transform"
              >
                <Sparkles className="w-4 h-4" />
                <span>2025 Wrapped</span>
              </button>
              <button
                onClick={() => navigate('/hub')}
                className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-full hover:scale-105 transition-transform"
              >
                <Sparkles className="w-4 h-4" />
                <span>All Features Hub</span>
              </button>
              {user && (
                <div className="flex items-center space-x-3">
                  {user.image && (
                    <img 
                      src={user.image} 
                      alt={user.name} 
                      className="w-8 h-8 rounded-full"
                    />
                  )}
                  <span className="text-white font-medium">{user.name}</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-spotify-lightgray hover:text-white transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Time Range Selector */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-full p-1 inline-flex">
            {timeRanges.map((range) => (
              <button
                key={range.value}
                onClick={() => setTimeRange(range.value)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-full transition-all duration-300 ${
                  timeRange === range.value
                    ? 'bg-spotify-green text-spotify-black font-semibold'
                    : 'text-spotify-lightgray hover:text-white'
                }`}
              >
                {range.icon}
                <span>{range.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-2xl p-2 inline-flex">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-spotify-green/20 text-spotify-green font-semibold'
                    : 'text-spotify-lightgray hover:text-white'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center py-20">
            <Loader2 className="w-8 h-8 text-spotify-green animate-spin" />
          </div>
        )}

        {/* Tab Content */}
        {!loading && stats && (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'overview' && <StatsOverview stats={stats} timeRange={timeRange} />}
              {activeTab === 'tracks' && <TopTracks timeRange={timeRange} />}
              {activeTab === 'artists' && <TopArtists timeRange={timeRange} />}
              {activeTab === 'genres' && <GenreChart stats={stats} />}
              {activeTab === 'wrapped' && (
                <div className="space-y-8">
                  <WrappedCard stats={stats} user={user} timeRange={timeRange} />
                  <div className="flex justify-center">
                    <button
                      onClick={downloadWrappedCard}
                      className="flex items-center space-x-2 px-8 py-4 bg-spotify-green text-spotify-black font-bold rounded-full hover:bg-green-400 transition-colors"
                    >
                      <Download className="w-5 h-5" />
                      <span>Download Your Wrapped Card</span>
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
