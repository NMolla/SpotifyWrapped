import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Music, Sparkles, TrendingUp, Clock, Users, 
  Award, Star, Zap, Play, Pause, ChevronRight,
  Download, Share2, X
} from 'lucide-react';

const SpotifyWrapped2025 = () => {
  const [wrappedData, setWrappedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [playingTrack, setPlayingTrack] = useState(null);
  const [audio, setAudio] = useState(null);
  
  const year = new Date().getFullYear();

  useEffect(() => {
    fetchWrappedData();
    return () => {
      if (audio) {
        audio.pause();
      }
    };
  }, []);

  const fetchWrappedData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/spotify-wrapped/${year}`);
      setWrappedData(response.data);
    } catch (error) {
      console.error('Error fetching wrapped data:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePlay = (track) => {
    if (!track.preview_url) return;
    
    if (playingTrack === track.position) {
      audio.pause();
      setPlayingTrack(null);
    } else {
      if (audio) audio.pause();
      const newAudio = new Audio(track.preview_url);
      newAudio.play();
      setAudio(newAudio);
      setPlayingTrack(track.position);
      
      newAudio.onended = () => {
        setPlayingTrack(null);
      };
    }
  };

  const slides = wrappedData ? [
    // Slide 1: Welcome
    {
      id: 'welcome',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center text-center p-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <Sparkles className="w-20 h-20 text-spotify-green mx-auto" />
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-6xl md:text-8xl font-black text-white mb-4"
          >
            Your {year} Wrapped
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-xl text-spotify-lightgray"
          >
            {wrappedData.time_period}
          </motion.p>
        </motion.div>
      )
    },
    // Slide 2: Total Minutes
    {
      id: 'minutes',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center text-center p-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="mb-8"
          >
            <Clock className="w-16 h-16 text-spotify-green mx-auto" />
          </motion.div>
          <motion.p className="text-2xl text-spotify-lightgray mb-4">You listened for</motion.p>
          <motion.h2 
            initial={{ scale: 0 }}
            animate={{ scale: 1.2, transition: { type: "spring" } }}
            className="text-7xl md:text-9xl font-black text-white mb-2"
          >
            {wrappedData.total_minutes_listened.toLocaleString()}
          </motion.h2>
          <motion.p className="text-3xl text-spotify-green font-bold">Minutes</motion.p>
          <motion.p className="text-lg text-spotify-lightgray mt-4">
            That's {wrappedData.total_hours_listened} hours of pure vibes
          </motion.p>
        </motion.div>
      )
    },
    // Slide 3: Top Song
    {
      id: 'top-song',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.p className="text-xl text-spotify-lightgray mb-6">Your #1 Song</motion.p>
          {wrappedData.top_song && (
            <>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="mb-6"
              >
                {wrappedData.top_song.image && (
                  <img 
                    src={wrappedData.top_song.image} 
                    alt={wrappedData.top_song.name}
                    className="w-64 h-64 rounded-lg shadow-2xl"
                  />
                )}
              </motion.div>
              <motion.h2 className="text-4xl font-bold text-white mb-2 text-center">
                {wrappedData.top_song.name}
              </motion.h2>
              <motion.p className="text-xl text-spotify-green mb-6">
                {wrappedData.top_song.artist}
              </motion.p>
              {wrappedData.top_song.preview_url && (
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => togglePlay(wrappedData.top_song)}
                  className="bg-spotify-green text-black p-4 rounded-full"
                >
                  {playingTrack === wrappedData.top_song.position ? 
                    <Pause className="w-6 h-6" /> : 
                    <Play className="w-6 h-6" />
                  }
                </motion.button>
              )}
            </>
          )}
        </motion.div>
      )
    },
    // Slide 4: Top 10 Songs
    {
      id: 'top-songs',
      content: (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-3xl font-bold text-white mb-6 text-center">
            Your Top 10 Songs
          </motion.h2>
          <div className="grid grid-cols-2 gap-x-6 gap-y-3 max-w-5xl mx-auto w-full">
            {wrappedData.top_tracks.map((track, index) => (
              <motion.div
                key={track.position}
                initial={{ opacity: 0, x: index < 5 ? -50 : 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center space-x-3 bg-spotify-darkgray/50 p-3 rounded-lg"
              >
                <div className="text-2xl font-black text-spotify-green min-w-[30px]">
                  {track.position}
                </div>
                {track.image && (
                  <img 
                    src={track.image} 
                    alt={track.name}
                    className="w-12 h-12 rounded"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold text-sm truncate">{track.name}</p>
                  <p className="text-spotify-lightgray text-xs truncate">{track.artist}</p>
                </div>
                {track.preview_url && (
                  <button
                    onClick={() => togglePlay(track)}
                    className="text-spotify-green hover:text-white transition-colors"
                  >
                    {playingTrack === track.position ? 
                      <Pause className="w-5 h-5" /> : 
                      <Play className="w-5 h-5" />
                    }
                  </button>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )
    },
    // Slide 5: Top Artist
    {
      id: 'top-artist',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.p className="text-xl text-spotify-lightgray mb-6">Your #1 Artist</motion.p>
          {wrappedData.top_artist && (
            <>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="mb-6"
              >
                {wrappedData.top_artist.image && (
                  <img 
                    src={wrappedData.top_artist.image} 
                    alt={wrappedData.top_artist.name}
                    className="w-64 h-64 rounded-full shadow-2xl"
                  />
                )}
              </motion.div>
              <motion.h2 className="text-5xl font-bold text-white mb-4">
                {wrappedData.top_artist.name}
              </motion.h2>
              {wrappedData.top_artist_status && (
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="bg-gradient-to-r from-spotify-green to-green-400 px-6 py-3 rounded-full"
                >
                  <p className="text-black font-bold">
                    Top {wrappedData.top_artist_status.percentage}% of listeners
                  </p>
                </motion.div>
              )}
            </>
          )}
        </motion.div>
      )
    },
    // Slide 6: Top 10 Artists
    {
      id: 'top-artists',
      content: (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-3xl font-bold text-white mb-6 text-center">
            Your Top 10 Artists
          </motion.h2>
          <div className="grid grid-cols-2 gap-x-6 gap-y-3 max-w-5xl mx-auto w-full">
            {wrappedData.top_artists.map((artist, index) => (
              <motion.div
                key={artist.position}
                initial={{ opacity: 0, x: index < 5 ? -50 : 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center space-x-3 bg-spotify-darkgray/50 p-3 rounded-lg"
              >
                <div className="text-2xl font-black text-spotify-green min-w-[30px]">
                  {artist.position}
                </div>
                {artist.image && (
                  <img 
                    src={artist.image} 
                    alt={artist.name}
                    className="w-12 h-12 rounded-full"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold text-sm truncate">{artist.name}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )
    },
    // Slide 7: Audio Aura
    {
      id: 'audio-aura',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8">Your Audio Aura</motion.h2>
          <div className="relative w-80 h-80">
            {wrappedData.audio_aura.map((color, index) => (
              <motion.div
                key={index}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ 
                  scale: 1 - (index * 0.2), 
                  opacity: 0.7 - (index * 0.2),
                }}
                transition={{ delay: index * 0.2 }}
                className={`absolute inset-0 rounded-full bg-gradient-to-br ${color.gradient} blur-xl`}
              />
            ))}
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.6 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <Sparkles className="w-20 h-20 text-white" />
            </motion.div>
          </div>
          <motion.div className="mt-8 space-y-2">
            {wrappedData.audio_aura.map((color, index) => (
              <motion.p
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 + (index * 0.1) }}
                className="text-lg text-white"
              >
                {color.name}
              </motion.p>
            ))}
          </motion.div>
        </motion.div>
      )
    },
    // Slide 8: Top Genres
    {
      id: 'genres',
      content: (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8 text-center">
            Your Genre Mix
          </motion.h2>
          <div className="max-w-2xl mx-auto w-full space-y-4">
            {wrappedData.top_genres.map((genre, index) => (
              <motion.div
                key={genre.genre}
                initial={{ opacity: 0, scaleX: 0 }}
                animate={{ opacity: 1, scaleX: 1 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                <div className="flex justify-between mb-2">
                  <span className="text-white font-semibold capitalize">{genre.genre}</span>
                  <span className="text-spotify-green">{genre.percentage}%</span>
                </div>
                <div className="w-full bg-spotify-darkgray rounded-full h-8">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${genre.percentage}%` }}
                    transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
                    className="h-full bg-gradient-to-r from-spotify-green to-green-400 rounded-full"
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )
    },
    // Slide 9: Listening Personality
    {
      id: 'personality',
      content: (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8 text-center">
            Your Listening Personality
          </motion.h2>
          <div className="space-y-6 max-w-2xl mx-auto">
            {wrappedData.listening_personality.map((trait, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.2 }}
                className="bg-gradient-to-r from-spotify-darkgray to-spotify-black p-6 rounded-lg"
              >
                <div className="flex items-center space-x-4 mb-2">
                  <span className="text-4xl">{trait.icon}</span>
                  <h3 className="text-2xl font-bold text-spotify-green">{trait.type}</h3>
                </div>
                <p className="text-spotify-lightgray">{trait.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )
    },
    // Slide 10: Music Discovery Stats
    {
      id: 'discovery',
      content: (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-12 text-center">
            Your Music Discovery
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="text-center"
            >
              <Users className="w-16 h-16 text-spotify-green mx-auto mb-4" />
              <p className="text-5xl font-black text-white mb-2">
                {wrappedData.music_discovery.unique_artists}
              </p>
              <p className="text-spotify-lightgray">Different Artists</p>
            </motion.div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <Music className="w-16 h-16 text-spotify-green mx-auto mb-4" />
              <p className="text-5xl font-black text-white mb-2">
                {wrappedData.music_discovery.unique_genres}
              </p>
              <p className="text-spotify-lightgray">Unique Genres</p>
            </motion.div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <TrendingUp className="w-16 h-16 text-spotify-green mx-auto mb-4" />
              <p className="text-5xl font-black text-white mb-2">
                {wrappedData.music_discovery.avg_popularity}
              </p>
              <p className="text-spotify-lightgray">Avg. Popularity</p>
            </motion.div>
          </div>
        </motion.div>
      )
    },
    // Final Slide: Thank You
    {
      id: 'thanks',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="mb-8"
          >
            <Star className="w-20 h-20 text-spotify-green mx-auto" />
          </motion.div>
          <motion.h2 className="text-5xl md:text-7xl font-black text-white mb-6 text-center">
            That's Your {year}!
          </motion.h2>
          <motion.p className="text-xl text-spotify-lightgray mb-12 text-center">
            Thanks for listening with Spotify
          </motion.p>
          <motion.div className="flex space-x-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCurrentSlide(0)}
              className="px-8 py-4 bg-spotify-green text-black font-bold rounded-full"
            >
              Watch Again
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-transparent border-2 border-spotify-green text-spotify-green font-bold rounded-full"
            >
              <Share2 className="inline w-5 h-5 mr-2" />
              Share
            </motion.button>
          </motion.div>
        </motion.div>
      )
    }
  ] : [];

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
        >
          <Music className="w-16 h-16 text-spotify-green" />
        </motion.div>
      </div>
    );
  }

  if (!wrappedData) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <p className="text-white">No data available</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-spotify-black via-purple-900/20 to-spotify-black" />
        <motion.div
          animate={{
            background: [
              'radial-gradient(circle at 20% 50%, rgba(29, 185, 84, 0.3) 0%, transparent 50%)',
              'radial-gradient(circle at 80% 50%, rgba(29, 185, 84, 0.3) 0%, transparent 50%)',
              'radial-gradient(circle at 20% 50%, rgba(29, 185, 84, 0.3) 0%, transparent 50%)',
            ]
          }}
          transition={{ duration: 10, repeat: Infinity }}
          className="absolute inset-0"
        />
      </div>

      {/* Content */}
      <div className="relative z-10 h-screen flex flex-col">
        {/* Progress Bar */}
        <div className="w-full h-1 bg-spotify-darkgray">
          <motion.div 
            className="h-full bg-spotify-green"
            initial={{ width: 0 }}
            animate={{ width: `${((currentSlide + 1) / slides.length) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>

        {/* Slides */}
        <div className="flex-1 relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentSlide}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              {slides[currentSlide]?.content}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center p-8">
          <button
            onClick={prevSlide}
            className={`text-spotify-green ${currentSlide === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={currentSlide === 0}
          >
            {currentSlide > 0 && 'Back'}
          </button>

          <div className="flex space-x-2">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentSlide 
                    ? 'w-8 bg-spotify-green' 
                    : 'bg-spotify-darkgray hover:bg-spotify-lightgray'
                }`}
              />
            ))}
          </div>

          <button
            onClick={nextSlide}
            className={`text-spotify-green font-bold flex items-center ${
              currentSlide === slides.length - 1 ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={currentSlide === slides.length - 1}
          >
            {currentSlide < slides.length - 1 && (
              <>
                Next
                <ChevronRight className="w-5 h-5 ml-1" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SpotifyWrapped2025;
