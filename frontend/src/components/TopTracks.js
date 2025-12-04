import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Play, Pause, Clock, Heart, ChevronLeft, ChevronRight } from 'lucide-react';

const TopTracks = ({ timeRange }) => {
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [playingTrack, setPlayingTrack] = useState(null);
  const [audio, setAudio] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    setCurrentPage(1); // Reset to first page when time range changes
    fetchTracks();
    return () => {
      if (audio) {
        audio.pause();
      }
    };
  }, [timeRange]);

  const fetchTracks = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/top/tracks/${timeRange}`);
      setTracks(response.data);
    } catch (error) {
      console.error('Error fetching tracks:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePlay = (track) => {
    if (!track.preview_url) return;

    if (playingTrack === track.id) {
      audio.pause();
      setPlayingTrack(null);
      setAudio(null);
    } else {
      if (audio) {
        audio.pause();
      }
      const newAudio = new Audio(track.preview_url);
      newAudio.play();
      newAudio.addEventListener('ended', () => {
        setPlayingTrack(null);
        setAudio(null);
      });
      setAudio(newAudio);
      setPlayingTrack(track.id);
    }
  };

  const formatDuration = (ms) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  // Calculate pagination
  const totalPages = Math.ceil(tracks.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentTracks = tracks.slice(startIndex, endIndex);

  const handlePreviousPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };

  const handlePageInputChange = (e) => {
    const value = e.target.value;
    
    // Allow empty input for typing
    if (value === '') {
      setCurrentPage('');
      return;
    }
    
    const page = parseInt(value);
    
    // Validate and set page
    if (!isNaN(page)) {
      if (page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      } else if (page > totalPages) {
        setCurrentPage(totalPages);
      } else if (page < 1) {
        setCurrentPage(1);
      }
    }
  };

  const handlePageInputBlur = () => {
    // Reset to 1 if empty or invalid
    if (currentPage === '' || currentPage < 1) {
      setCurrentPage(1);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-spotify-green border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-2">Your Top Tracks</h2>
        <p className="text-spotify-lightgray">The songs that defined your listening</p>
      </div>

      <div className="grid gap-4">
        <AnimatePresence mode="wait">
          {currentTracks.map((track, index) => {
            const actualIndex = startIndex + index;
            return (
              <motion.div
                key={track.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.01 }}
                className="glass rounded-xl p-4 flex items-center space-x-4 group"
              >
                {/* Rank */}
                <div className="text-3xl font-bold text-spotify-green w-12 text-center">
                  {actualIndex + 1}
                </div>

              {/* Album Cover */}
              <div className="relative">
                <img
                  src={track.image}
                  alt={track.name}
                  className="w-16 h-16 rounded-lg object-cover"
                />
                {track.preview_url && (
                  <button
                    onClick={() => togglePlay(track)}
                    className="absolute inset-0 bg-black/60 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                  >
                    {playingTrack === track.id ? (
                      <Pause className="w-6 h-6 text-white" />
                    ) : (
                      <Play className="w-6 h-6 text-white" />
                    )}
                  </button>
                )}
              </div>

              {/* Track Info */}
              <div className="flex-1">
                <h3 className="text-white font-semibold text-lg">{track.name}</h3>
                <p className="text-spotify-lightgray text-sm">
                  {track.artists.join(', ')} • {track.album}
                </p>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-4 text-spotify-lightgray">
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">{formatDuration(track.duration_ms)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Heart className="w-4 h-4" />
                  <span className="text-sm">{track.popularity}</span>
                </div>
              </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-4 mt-6">
          <button
            onClick={handlePreviousPage}
            disabled={currentPage === 1}
            className={`p-2 rounded-lg ${
              currentPage === 1
                ? 'bg-spotify-darkgray text-spotify-lightgray/50 cursor-not-allowed'
                : 'bg-spotify-green text-spotify-black hover:bg-green-400'
            } transition-colors`}
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-2 text-white">
            <span>Page</span>
            <input
              type="number"
              min="1"
              max={totalPages}
              value={currentPage}
              onChange={handlePageInputChange}
              onBlur={handlePageInputBlur}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.target.blur();
                } else if (e.key === 'ArrowUp') {
                  e.preventDefault();
                  setCurrentPage(prev => Math.min(prev + 1, totalPages));
                } else if (e.key === 'ArrowDown') {
                  e.preventDefault();
                  setCurrentPage(prev => Math.max(prev - 1, 1));
                }
              }}
              className="w-16 px-2 py-1 text-center bg-spotify-darkgray border border-spotify-lightgray/20 rounded-lg text-white focus:outline-none focus:border-spotify-green transition-colors"
            />
            <span>of {totalPages}</span>
          </div>
          
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className={`p-2 rounded-lg ${
              currentPage === totalPages
                ? 'bg-spotify-darkgray text-spotify-lightgray/50 cursor-not-allowed'
                : 'bg-spotify-green text-spotify-black hover:bg-green-400'
            } transition-colors`}
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Summary Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass rounded-2xl p-6 mt-8"
      >
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div>
            <p className="text-spotify-lightgray text-sm mb-1">Total Duration</p>
            <p className="text-2xl font-bold text-white">
              {Math.round(tracks.reduce((sum, t) => sum + t.duration_ms, 0) / 60000)} min
            </p>
          </div>
          <div>
            <p className="text-spotify-lightgray text-sm mb-1">Avg Popularity</p>
            <p className="text-2xl font-bold text-white">
              {Math.round(tracks.reduce((sum, t) => sum + t.popularity, 0) / tracks.length)}
            </p>
          </div>
          <div>
            <p className="text-spotify-lightgray text-sm mb-1">Unique Artists</p>
            <p className="text-2xl font-bold text-white">
              {new Set(tracks.flatMap(t => t.artists)).size}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default TopTracks;
