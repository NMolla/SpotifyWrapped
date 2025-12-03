import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import html2canvas from 'html2canvas';
import { Download, Share2, Music, Star, Hash, Clock } from 'lucide-react';

const WrappedCard = ({ stats, user, timeRange }) => {
  const cardRef = useRef(null);

  const downloadCard = async () => {
    if (cardRef.current) {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#191414',
        scale: 2
      });
      
      const link = document.createElement('a');
      const currentYear = new Date().getFullYear();
      link.download = `spotify-wrapped-${currentYear}.png`;
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

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-2">Your {new Date().getFullYear()} Wrapped</h2>
        <p className="text-spotify-lightgray">A year of music, captured in a card</p>
      </div>

      {/* Wrapped Card */}
      <div className="flex justify-center">
        <motion.div
          ref={cardRef}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="relative w-full max-w-md"
        >
          <div className="bg-gradient-to-br from-spotify-black via-spotify-darkgray to-spotify-black rounded-3xl p-8 shadow-2xl">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="flex justify-center mb-4">
                <Music className="w-12 h-12 text-spotify-green" />
              </div>
              <h3 className="text-3xl font-black text-white mb-2">
                {user?.name || 'Your'} {new Date().getFullYear()} Wrapped
              </h3>
              <p className="text-spotify-green font-semibold">{stats.time_period}</p>
            </div>

            {/* Top Artist */}
            {stats.top_artist && (
              <div className="mb-6">
                <div className="flex items-center space-x-4">
                  {stats.top_artist.image && (
                    <img
                      src={stats.top_artist.image}
                      alt={stats.top_artist.name}
                      className="w-20 h-20 rounded-full object-cover ring-4 ring-spotify-green/30"
                    />
                  )}
                  <div>
                    <p className="text-spotify-lightgray text-sm">TOP ARTIST</p>
                    <p className="text-xl font-bold text-white">{stats.top_artist.name}</p>
                    <p className="text-sm text-spotify-green">{stats.top_artist.genres?.[0]}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Top Track */}
            {stats.top_track && (
              <div className="mb-6">
                <div className="flex items-center space-x-4">
                  {stats.top_track.image && (
                    <img
                      src={stats.top_track.image}
                      alt={stats.top_track.name}
                      className="w-20 h-20 rounded-lg object-cover ring-4 ring-spotify-green/30"
                    />
                  )}
                  <div className="flex-1">
                    <p className="text-spotify-lightgray text-sm">TOP TRACK</p>
                    <p className="text-lg font-bold text-white truncate">{stats.top_track.name}</p>
                    <p className="text-sm text-spotify-green">{stats.top_track.artist}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="glass rounded-xl p-4 text-center">
                <Hash className="w-6 h-6 text-spotify-green mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{stats.top_genre}</p>
                <p className="text-xs text-spotify-lightgray">Top Genre</p>
              </div>
              <div className="glass rounded-xl p-4 text-center">
                <Clock className="w-6 h-6 text-spotify-green mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{Math.round(stats.total_minutes / 60)}</p>
                <p className="text-xs text-spotify-lightgray">Hours Played</p>
              </div>
            </div>

            {/* Top Genres Bar */}
            <div className="mb-6">
              <p className="text-sm text-spotify-lightgray mb-3">TOP GENRES</p>
              <div className="space-y-2">
                {stats.top_genres?.slice(0, 5).map((genre, index) => (
                  <div key={genre.genre} className="relative">
                    <div className="flex justify-between mb-1">
                      <span className="text-xs text-white">{genre.genre}</span>
                      <span className="text-xs text-spotify-lightgray">{genre.count}</span>
                    </div>
                    <div className="h-2 bg-spotify-darkgray rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(genre.count / stats.top_genres[0].count) * 100}%` }}
                        transition={{ duration: 1, delay: index * 0.1 }}
                        className={`h-full bg-gradient-to-r ${gradientColors[index]}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Characteristics */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              {stats.characteristics?.map((char, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-spotify-green/20 text-spotify-green rounded-full text-xs font-medium"
                >
                  {char}
                </span>
              ))}
            </div>

            {/* Footer */}
            <div className="text-center pt-4 border-t border-spotify-gray/20">
              <p className="text-xs text-spotify-lightgray">
                Spotify Wrapped Dashboard • {new Date().getFullYear()}
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={downloadCard}
          className="flex items-center space-x-2 px-6 py-3 bg-spotify-green text-spotify-black font-bold rounded-full hover:bg-green-400 transition-colors"
        >
          <Download className="w-5 h-5" />
          <span>Download Card</span>
        </motion.button>
        
        {navigator.share && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={shareCard}
            className="flex items-center space-x-2 px-6 py-3 glass text-white font-bold rounded-full hover:bg-white/10 transition-colors"
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
