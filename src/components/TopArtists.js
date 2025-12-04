import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Users, Hash, Star, ChevronLeft, ChevronRight } from 'lucide-react';

const TopArtists = ({ timeRange }) => {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12; // 3 featured + 9 in list

  useEffect(() => {
    setCurrentPage(1); // Reset to first page when time range changes
    fetchArtists();
  }, [timeRange]);

  const fetchArtists = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/top/artists/${timeRange}`);
      setArtists(response.data);
    } catch (error) {
      console.error('Error fetching artists:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatFollowers = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
    return num.toString();
  };

  // Calculate pagination
  const totalPages = Math.ceil(artists.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentArtists = artists.slice(startIndex, endIndex);

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
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-2">Your Top Artists</h2>
        <p className="text-spotify-lightgray">The voices that accompanied your journey</p>
      </div>

      {/* Top 3 Artists - Featured */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {currentArtists.slice(0, 3).map((artist, index) => {
          const actualIndex = startIndex + index;
          return (
            <motion.div
              key={artist.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="glass rounded-2xl p-6 text-center relative overflow-hidden group"
            >
              <div className="absolute top-4 left-4 w-10 h-10 bg-spotify-green rounded-full flex items-center justify-center text-spotify-black font-bold text-lg">
                {actualIndex + 1}
              </div>
            
            <div className="relative z-10">
              {artist.image && (
                <img
                  src={artist.image}
                  alt={artist.name}
                  className="w-32 h-32 rounded-full mx-auto mb-4 object-cover ring-4 ring-spotify-green/20"
                />
              )}
              <h3 className="text-xl font-bold text-white mb-4">{artist.name}</h3>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-spotify-lightgray mb-1">Followers</p>
                  <p className="text-white font-semibold">{formatFollowers(artist.followers)}</p>
                </div>
                <div>
                  <p className="text-spotify-lightgray mb-1">Popularity</p>
                  <p className="text-white font-semibold">{artist.popularity}</p>
                </div>
              </div>
            </div>
          </motion.div>
          );
        })}
      </div>

      {/* Rest of the Artists */}
      <div className="grid gap-4">
        <AnimatePresence mode="wait">
          {currentArtists.slice(3).map((artist, index) => {
            const actualIndex = startIndex + index + 3;
            return (
              <motion.div
                key={artist.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.01 }}
                className="glass rounded-xl p-4 flex items-center space-x-4"
              >
                {/* Rank */}
                <div className="text-2xl font-bold text-spotify-green w-10 text-center">
                  {actualIndex + 1}
                </div>

              {/* Artist Image */}
              {artist.image && (
                <img
                  src={artist.image}
                  alt={artist.name}
                  className="w-16 h-16 rounded-full object-cover"
                />
              )}

              {/* Artist Info */}
              <div className="flex-1">
                <h3 className="text-white font-semibold text-lg">{artist.name}</h3>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-4 text-spotify-lightgray">
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">{formatFollowers(artist.followers)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4" />
                  <span className="text-sm">{artist.popularity}</span>
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

      {/* Genre Cloud */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass rounded-2xl p-6 mt-8"
      >
        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
          <Hash className="w-5 h-5 mr-2 text-spotify-green" />
          Your Genre Cloud
        </h3>
        <div className="flex flex-wrap gap-3">
          {Array.from(new Set(artists.flatMap(a => a.genres))).slice(0, 20).map((genre, index) => (
            <motion.span
              key={genre}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.02 }}
              className="px-4 py-2 bg-spotify-green/10 hover:bg-spotify-green/20 text-spotify-green rounded-full text-sm font-medium transition-colors cursor-pointer"
            >
              {genre}
            </motion.span>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default TopArtists;
