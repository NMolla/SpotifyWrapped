import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import html2canvas from 'html2canvas';
import axios from 'axios';
import { 
  Download, Share2, Music, Star, Hash, Clock, 
  Users, TrendingUp, Sparkles, Award, Heart, BarChart3 
} from 'lucide-react';

const WrappedCard = ({ stats, user, timeRange }) => {
  const cardRef = useRef(null);
  const [selectedCard, setSelectedCard] = useState('overview');
  const [topTracks, setTopTracks] = useState([]);
  const [topArtists, setTopArtists] = useState([]);

  useEffect(() => {
    fetchTopItems();
  }, [timeRange]);

  const fetchTopItems = async () => {
    try {
      const [tracksRes, artistsRes] = await Promise.all([
        axios.get(`http://127.0.0.1:5000/api/top/tracks/${timeRange}`),
        axios.get(`http://127.0.0.1:5000/api/top/artists/${timeRange}`)
      ]);
      setTopTracks(tracksRes.data.slice(0, 5));
      setTopArtists(artistsRes.data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching top items:', error);
    }
  };

  const downloadCard = async () => {
    if (cardRef.current) {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#191414',
        scale: 2
      });
      
      const link = document.createElement('a');
      const currentYear = new Date().getFullYear();
      link.download = `spotify-wrapped-${selectedCard}-${currentYear}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  const shareCard = async () => {
    if (navigator.share && cardRef.current) {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#191414',
        scale: 2
      });
      
      canvas.toBlob(async (blob) => {
        const file = new File([blob], 'spotify-wrapped.png', { type: 'image/png' });
        try {
          await navigator.share({
            files: [file],
            title: `My Spotify Wrapped ${new Date().getFullYear()}`,
            text: 'Check out my Spotify Wrapped!'
          });
        } catch (error) {
          console.error('Error sharing:', error);
        }
      });
    }
  };

  const gradientColors = [
    'from-purple-600 to-pink-600',
    'from-blue-600 to-cyan-600',
    'from-green-600 to-emerald-600',
    'from-orange-600 to-red-600',
    'from-indigo-600 to-purple-600'
  ];

  const cardTypes = [
    { id: 'overview', label: 'Overview', icon: <Sparkles className="w-4 h-4" /> },
    { id: 'top-artists', label: 'Top Artists', icon: <Users className="w-4 h-4" /> },
    { id: 'top-tracks', label: 'Top Tracks', icon: <Music className="w-4 h-4" /> },
    { id: 'stats', label: 'Stats', icon: <BarChart3 className="w-4 h-4" /> },
  ];

  const renderCard = () => {
    switch (selectedCard) {
      case 'overview':
        return renderOverviewCard();
      case 'top-artists':
        return renderTopArtistsCard();
      case 'top-tracks':
        return renderTopTracksCard();
      case 'stats':
        return renderStatsCard();
      default:
        return renderOverviewCard();
    }
  };

  const renderOverviewCard = () => (
    <div className="w-full aspect-[9/16] bg-gradient-to-br from-spotify-black via-purple-900/30 to-spotify-black rounded-3xl p-8 flex flex-col justify-between">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="inline-block mb-4"
        >
          <Sparkles className="w-16 h-16 text-spotify-green" />
        </motion.div>
        <h2 className="text-4xl font-black text-white mb-2">
          {user?.name || 'My'} {new Date().getFullYear()} Wrapped
        </h2>
        <p className="text-spotify-green text-lg font-medium">{stats?.time_period}</p>
      </div>

      {/* Main Stats */}
      <div className="flex-1 flex flex-col justify-center space-y-6">
        {/* Minutes Played */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center"
        >
          <p className="text-spotify-lightgray mb-2">Total Minutes</p>
          <p className="text-6xl font-black text-white">
            {stats?.total_minutes?.toLocaleString() || '0'}
          </p>
          <p className="text-xl text-spotify-green">
            {Math.round((stats?.total_minutes || 0) / 60)} hours of music
          </p>
        </motion.div>

        {/* Top Artist & Track */}
        <div className="grid grid-cols-2 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass rounded-2xl p-4"
          >
            <p className="text-xs text-spotify-lightgray mb-2">TOP ARTIST</p>
            {stats?.top_artist?.image && (
              <img 
                src={stats.top_artist.image} 
                alt={stats.top_artist.name}
                className="w-16 h-16 rounded-full mx-auto mb-2"
              />
            )}
            <p className="text-sm font-bold text-white truncate">
              {stats?.top_artist?.name || 'Unknown'}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass rounded-2xl p-4"
          >
            <p className="text-xs text-spotify-lightgray mb-2">TOP TRACK</p>
            {stats?.top_track?.image && (
              <img 
                src={stats.top_track.image} 
                alt={stats.top_track.name}
                className="w-16 h-16 rounded-lg mx-auto mb-2"
              />
            )}
            <p className="text-sm font-bold text-white truncate">
              {stats?.top_track?.name || 'Unknown'}
            </p>
          </motion.div>
        </div>

        {/* Key Stats */}
        <div className="grid grid-cols-3 gap-2">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
            className="text-center"
          >
            <p className="text-3xl font-bold text-spotify-green">
              {stats?.total_artists || 0}
            </p>
            <p className="text-xs text-spotify-lightgray">Artists</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
            className="text-center"
          >
            <p className="text-3xl font-bold text-spotify-green">
              {stats?.total_tracks || 0}
            </p>
            <p className="text-xs text-spotify-lightgray">Tracks</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center"
          >
            <p className="text-3xl font-bold text-spotify-green">
              {stats?.top_genres?.length || 0}
            </p>
            <p className="text-xs text-spotify-lightgray">Genres</p>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center">
        <p className="text-xs text-spotify-lightgray">
          Spotify Wrapped • {new Date().getFullYear()}
        </p>
      </div>
    </div>
  );

  const renderTopArtistsCard = () => (
    <div className="w-full aspect-[9/16] bg-gradient-to-br from-spotify-black via-blue-900/30 to-spotify-black rounded-3xl p-8 flex flex-col">
      {/* Header */}
      <div className="text-center mb-8">
        <Users className="w-12 h-12 text-spotify-green mx-auto mb-4" />
        <h2 className="text-3xl font-black text-white">Top Artists</h2>
        <p className="text-spotify-green">{stats?.time_period}</p>
      </div>

      {/* Artists List */}
      <div className="flex-1 space-y-4">
        {topArtists.map((artist, index) => (
          <motion.div
            key={artist.id || index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center space-x-4 glass rounded-xl p-3"
          >
            <div className="text-2xl font-black text-spotify-green w-8 text-center">
              {index + 1}
            </div>
            {artist.image && (
              <img 
                src={artist.image} 
                alt={artist.name}
                className="w-14 h-14 rounded-full"
              />
            )}
            <div className="flex-1">
              <p className="text-white font-bold truncate">{artist.name}</p>
              <div className="flex items-center space-x-4 text-xs text-spotify-lightgray">
                <span>{artist.followers ? `${(artist.followers / 1000000).toFixed(1)}M followers` : ''}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center mt-6">
        <p className="text-xs text-spotify-lightgray">
          Your Top {topArtists.length} Artists • Spotify Wrapped
        </p>
      </div>
    </div>
  );

  const renderTopTracksCard = () => (
    <div className="w-full aspect-[9/16] bg-gradient-to-br from-spotify-black via-green-900/30 to-spotify-black rounded-3xl p-8 flex flex-col">
      {/* Header */}
      <div className="text-center mb-8">
        <Music className="w-12 h-12 text-spotify-green mx-auto mb-4" />
        <h2 className="text-3xl font-black text-white">Top Tracks</h2>
        <p className="text-spotify-green">{stats?.time_period}</p>
      </div>

      {/* Tracks List */}
      <div className="flex-1 space-y-4">
        {topTracks.map((track, index) => (
          <motion.div
            key={track.id || index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center space-x-4 glass rounded-xl p-3"
          >
            <div className="text-2xl font-black text-spotify-green w-8 text-center">
              {index + 1}
            </div>
            {track.image && (
              <img 
                src={track.image} 
                alt={track.name}
                className="w-14 h-14 rounded-lg"
              />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-white font-bold truncate">{track.name}</p>
              <p className="text-sm text-spotify-lightgray truncate">{track.artist}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center mt-6">
        <p className="text-xs text-spotify-lightgray">
          Your Top {topTracks.length} Tracks • Spotify Wrapped
        </p>
      </div>
    </div>
  );

  const renderStatsCard = () => (
    <div className="w-full aspect-[9/16] bg-gradient-to-br from-spotify-black via-orange-900/30 to-spotify-black rounded-3xl p-8 flex flex-col">
      {/* Header */}
      <div className="text-center mb-8">
        <BarChart3 className="w-12 h-12 text-spotify-green mx-auto mb-4" />
        <h2 className="text-3xl font-black text-white">Your Stats</h2>
        <p className="text-spotify-green">{stats?.time_period}</p>
      </div>

      {/* Stats Grid */}
      <div className="flex-1 flex flex-col justify-center space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-6 text-center"
          >
            <Clock className="w-8 h-8 text-spotify-green mx-auto mb-3" />
            <p className="text-3xl font-black text-white">
              {Math.round((stats?.total_minutes || 0) / 60)}
            </p>
            <p className="text-xs text-spotify-lightgray">Hours Played</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-2xl p-6 text-center"
          >
            <Users className="w-8 h-8 text-spotify-green mx-auto mb-3" />
            <p className="text-3xl font-black text-white">
              {stats?.total_artists || 0}
            </p>
            <p className="text-xs text-spotify-lightgray">Different Artists</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="glass rounded-2xl p-6 text-center"
          >
            <Music className="w-8 h-8 text-spotify-green mx-auto mb-3" />
            <p className="text-3xl font-black text-white">
              {stats?.total_tracks || 0}
            </p>
            <p className="text-xs text-spotify-lightgray">Unique Tracks</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className="glass rounded-2xl p-6 text-center"
          >
            <Hash className="w-8 h-8 text-spotify-green mx-auto mb-3" />
            <p className="text-3xl font-black text-white">
              {stats?.top_genres?.length || 0}
            </p>
            <p className="text-xs text-spotify-lightgray">Genres Explored</p>
          </motion.div>
        </div>

        {/* Top Genre */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass rounded-2xl p-6 text-center"
        >
          <p className="text-sm text-spotify-lightgray mb-2">Your Top Genre</p>
          <p className="text-3xl font-black text-spotify-green capitalize">
            {stats?.top_genre || 'Unknown'}
          </p>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="text-center mt-6">
        <p className="text-xs text-spotify-lightgray">
          Your Music Stats • Spotify Wrapped
        </p>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-2">Your Wrapped Cards</h2>
      </div>

      {/* Card Type Selector */}
      <div className="flex justify-center mb-6">
        <div className="inline-flex glass rounded-full p-1">
          {cardTypes.map(type => (
            <button
              key={type.id}
              onClick={() => setSelectedCard(type.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all ${
                selectedCard === type.id
                  ? 'bg-spotify-green text-spotify-black'
                  : 'text-spotify-lightgray hover:text-white'
              }`}
            >
              {type.icon}
              <span className="text-sm font-medium">{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Card Display */}
      <div className="flex justify-center">
        <div className="w-full max-w-md">
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedCard}
              ref={cardRef}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              {renderCard()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={downloadCard}
          className="flex items-center space-x-2 px-8 py-3 bg-spotify-green text-spotify-black font-bold rounded-full hover:bg-green-400 transition-colors"
        >
          <Download className="w-5 h-5" />
          <span>Download Card</span>
        </motion.button>

        {navigator.share && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={shareCard}
            className="flex items-center space-x-2 px-8 py-3 bg-transparent border-2 border-spotify-green text-spotify-green font-bold rounded-full hover:bg-spotify-green hover:text-spotify-black transition-all"
          >
            <Share2 className="w-5 h-5" />
            <span>Share Card</span>
          </motion.button>
        )}
      </div>
    </div>
  );
};

export default WrappedCard;
