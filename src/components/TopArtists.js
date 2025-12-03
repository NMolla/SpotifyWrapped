import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Users, Hash, Star } from 'lucide-react';

const TopArtists = ({ timeRange }) => {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
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
        {artists.slice(0, 3).map((artist, index) => (
          <motion.div
            key={artist.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
            className="glass rounded-2xl p-6 text-center relative overflow-hidden group"
          >
            <div className="absolute top-4 left-4 w-10 h-10 bg-spotify-green rounded-full flex items-center justify-center text-spotify-black font-bold text-lg">
              {index + 1}
            </div>
            
            <div className="relative z-10">
              {artist.image && (
                <img
                  src={artist.image}
                  alt={artist.name}
                  className="w-32 h-32 rounded-full mx-auto mb-4 object-cover ring-4 ring-spotify-green/20"
                />
              )}
              <h3 className="text-xl font-bold text-white mb-2">{artist.name}</h3>
              
              <div className="flex flex-wrap justify-center gap-2 mb-4">
                {artist.genres.slice(0, 3).map((genre, i) => (
                  <span key={i} className="text-xs px-2 py-1 bg-spotify-green/20 text-spotify-green rounded-full">
                    {genre}
                  </span>
                ))}
              </div>

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
        ))}
      </div>

      {/* Rest of the Artists */}
      <div className="grid gap-4">
        <AnimatePresence>
          {artists.slice(3).map((artist, index) => (
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
                {index + 4}
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
                <div className="flex flex-wrap gap-2 mt-1">
                  {artist.genres.slice(0, 3).map((genre, i) => (
                    <span key={i} className="text-xs text-spotify-lightgray">
                      {genre}
                    </span>
                  ))}
                </div>
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
          ))}
        </AnimatePresence>
      </div>

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
