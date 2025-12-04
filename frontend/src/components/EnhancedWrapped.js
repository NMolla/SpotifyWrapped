import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Music, Sparkles, TrendingUp, Clock, Users, 
  Award, Star, Zap, Play, Pause, ChevronRight, ChevronLeft,
  Heart, Disc, Radio, Sun, Moon, Coffee, Sunset,
  BarChart2, PieChart, Activity, Compass, Target,
  Calendar, Headphones, Volume2, ArrowUp, ArrowDown
} from 'lucide-react';

const EnhancedWrapped = () => {
  const [wrappedData, setWrappedData] = useState(null);
  const [audioFeatures, setAudioFeatures] = useState(null);
  const [recentlyPlayed, setRecentlyPlayed] = useState(null);
  const [savedAnalysis, setSavedAnalysis] = useState(null);
  const [obscurityScore, setObscurityScore] = useState(null);
  const [artistLoyalty, setArtistLoyalty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [playingTrack, setPlayingTrack] = useState(null);
  const [audio, setAudio] = useState(null);
  
  const year = new Date().getFullYear();

  useEffect(() => {
    fetchAllData();
    return () => {
      if (audio) audio.pause();
    };
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [wrapped, features, recent, saved, obscurity, loyalty] = await Promise.all([
        axios.get(`http://127.0.0.1:5000/api/enhanced-wrapped/${year}`),
        axios.get('http://127.0.0.1:5000/api/audio-features'),
        axios.get('http://127.0.0.1:5000/api/recently-played'),
        axios.get('http://127.0.0.1:5000/api/saved-tracks-analysis'),
        axios.get('http://127.0.0.1:5000/api/obscurity-score'),
        axios.get('http://127.0.0.1:5000/api/artist-loyalty')
      ]);
      
      setWrappedData(wrapped.data);
      setAudioFeatures(features.data);
      setRecentlyPlayed(recent.data);
      setSavedAnalysis(saved.data);
      setObscurityScore(obscurity.data);
      setArtistLoyalty(loyalty.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePlay = (track) => {
    if (!track?.preview_url) return;
    
    if (playingTrack === track.name) {
      audio?.pause();
      setPlayingTrack(null);
    } else {
      if (audio) audio.pause();
      const newAudio = new Audio(track.preview_url);
      newAudio.play();
      setAudio(newAudio);
      setPlayingTrack(track.name);
      newAudio.onended = () => setPlayingTrack(null);
    }
  };

  const getTimeIcon = (hour) => {
    if (hour >= 5 && hour < 12) return <Coffee className="w-8 h-8" />;
    if (hour >= 12 && hour < 17) return <Sun className="w-8 h-8" />;
    if (hour >= 17 && hour < 21) return <Sunset className="w-8 h-8" />;
    return <Moon className="w-8 h-8" />;
  };

  const slides = wrappedData ? [
    // Slide 1: Welcome
    {
      id: 'welcome',
      bg: 'from-purple-900 via-black to-green-900',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center text-center p-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.8, type: "spring" }}
            className="mb-8"
          >
            <Sparkles className="w-24 h-24 text-spotify-green" />
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-5xl md:text-7xl font-black text-white mb-4"
          >
            Your {year}
          </motion.h1>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-6xl md:text-8xl font-black text-spotify-green mb-6"
          >
            ENHANCED
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-xl text-spotify-lightgray"
          >
            Beyond what Spotify shows you
          </motion.p>
        </motion.div>
      )
    },

    // Slide 2: Mood Analysis
    {
      id: 'mood',
      bg: audioFeatures?.mood?.color ? `from-[${audioFeatures.mood.color}]/30 via-black to-black` : 'from-yellow-900/30 via-black to-black',
      content: audioFeatures && (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.p className="text-2xl text-spotify-lightgray mb-4">Your music mood is</motion.p>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", bounce: 0.5 }}
            className="text-8xl mb-6"
          >
            {audioFeatures.mood?.emoji}
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-5xl md:text-7xl font-black text-white mb-4"
          >
            {audioFeatures.mood?.name}
          </motion.h2>
          <motion.p className="text-xl text-spotify-lightgray text-center max-w-md">
            {audioFeatures.mood?.description}
          </motion.p>
        </motion.div>
      )
    },

    // Slide 3: Audio Profile Radar
    {
      id: 'audio-profile',
      bg: 'from-blue-900/30 via-black to-purple-900/30',
      content: wrappedData?.audio_profile && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8 text-center">
            Your Audio DNA
          </motion.h2>
          <div className="max-w-2xl mx-auto w-full space-y-6">
            {[
              { label: 'Danceability', value: wrappedData.audio_profile.danceability, icon: '💃', color: 'from-pink-500 to-rose-500' },
              { label: 'Energy', value: wrappedData.audio_profile.energy, icon: '⚡', color: 'from-yellow-500 to-orange-500' },
              { label: 'Happiness', value: wrappedData.audio_profile.happiness, icon: '😊', color: 'from-green-500 to-emerald-500' },
              { label: 'Acousticness', value: wrappedData.audio_profile.acousticness, icon: '🎸', color: 'from-blue-500 to-cyan-500' },
            ].map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex justify-between mb-2">
                  <span className="text-white font-semibold flex items-center gap-2">
                    <span>{item.icon}</span> {item.label}
                  </span>
                  <span className="text-spotify-green font-bold">{Math.round(item.value * 100)}%</span>
                </div>
                <div className="w-full bg-spotify-darkgray rounded-full h-4">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${item.value * 100}%` }}
                    transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
                    className={`h-full bg-gradient-to-r ${item.color} rounded-full`}
                  />
                </div>
              </motion.div>
            ))}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="text-center mt-8"
            >
              <p className="text-spotify-lightgray">Average Tempo</p>
              <p className="text-4xl font-bold text-spotify-green">{wrappedData.audio_profile.avg_tempo} BPM</p>
            </motion.div>
          </div>
        </motion.div>
      )
    },

    // Slide 4: Listening Time Patterns
    {
      id: 'time-patterns',
      bg: 'from-indigo-900/30 via-black to-black',
      content: recentlyPlayed && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-4 text-center">
            When You Listen
          </motion.h2>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="text-6xl text-center mb-4"
          >
            {recentlyPlayed.time_personality?.emoji}
          </motion.div>
          <motion.h3 className="text-3xl font-bold text-spotify-green text-center mb-2">
            {recentlyPlayed.time_personality?.type}
          </motion.h3>
          <motion.p className="text-spotify-lightgray text-center mb-8">
            {recentlyPlayed.time_personality?.description}
          </motion.p>
          
          <div className="max-w-3xl mx-auto w-full">
            <p className="text-white text-center mb-4">Listening by Hour</p>
            <div className="flex items-end justify-center gap-1 h-32">
              {recentlyPlayed.listening_by_hour?.map((count, hour) => (
                <motion.div
                  key={hour}
                  initial={{ height: 0 }}
                  animate={{ height: `${(count / Math.max(...recentlyPlayed.listening_by_hour)) * 100}%` }}
                  transition={{ delay: hour * 0.02 }}
                  className={`w-3 rounded-t ${hour === recentlyPlayed.peak_hour ? 'bg-spotify-green' : 'bg-spotify-darkgray'}`}
                  title={`${hour}:00 - ${count} plays`}
                />
              ))}
            </div>
            <div className="flex justify-between text-xs text-spotify-lightgray mt-2">
              <span>12am</span>
              <span>6am</span>
              <span>12pm</span>
              <span>6pm</span>
              <span>12am</span>
            </div>
          </div>
          
          <motion.div className="text-center mt-8">
            <p className="text-spotify-lightgray">Peak listening time</p>
            <p className="text-2xl font-bold text-white flex items-center justify-center gap-2">
              {getTimeIcon(recentlyPlayed.peak_hour)}
              {recentlyPlayed.peak_hour}:00 - {recentlyPlayed.peak_hour + 1}:00
            </p>
            <p className="text-spotify-green">on {recentlyPlayed.peak_day}s</p>
          </motion.div>
        </motion.div>
      )
    },

    // Slide 5: Obscurity Score
    {
      id: 'obscurity',
      bg: 'from-violet-900/30 via-black to-black',
      content: obscurityScore && (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.h2 className="text-3xl font-bold text-white mb-8">How Mainstream Are You?</motion.h2>
          
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="relative w-64 h-64 mb-8"
          >
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="128"
                cy="128"
                r="100"
                fill="none"
                stroke="#282828"
                strokeWidth="20"
              />
              <motion.circle
                cx="128"
                cy="128"
                r="100"
                fill="none"
                stroke={obscurityScore.level?.color}
                strokeWidth="20"
                strokeLinecap="round"
                initial={{ strokeDasharray: "0 628" }}
                animate={{ strokeDasharray: `${obscurityScore.obscurity_score * 6.28} 628` }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-5xl font-black text-white">{Math.round(obscurityScore.obscurity_score)}</span>
              <span className="text-spotify-lightgray">Obscurity</span>
            </div>
          </motion.div>
          
          <motion.div className="text-center">
            <span className="text-5xl mb-4 block">{obscurityScore.level?.emoji}</span>
            <h3 className="text-3xl font-bold text-white mb-2">{obscurityScore.level?.name}</h3>
            <p className="text-spotify-lightgray max-w-md">{obscurityScore.level?.description}</p>
          </motion.div>
          
          <motion.div className="grid grid-cols-2 gap-8 mt-8 max-w-lg">
            <div className="text-center">
              <p className="text-spotify-lightgray text-sm">Most Underground</p>
              <p className="text-white font-semibold">{obscurityScore.most_obscure_track?.name}</p>
              <p className="text-spotify-green text-sm">{obscurityScore.most_obscure_track?.popularity} popularity</p>
            </div>
            <div className="text-center">
              <p className="text-spotify-lightgray text-sm">Most Mainstream</p>
              <p className="text-white font-semibold">{obscurityScore.most_mainstream_track?.name}</p>
              <p className="text-spotify-green text-sm">{obscurityScore.most_mainstream_track?.popularity} popularity</p>
            </div>
          </motion.div>
        </motion.div>
      )
    },

    // Slide 6: Artist Loyalty
    {
      id: 'loyalty',
      bg: 'from-amber-900/30 via-black to-black',
      content: artistLoyalty && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-4 text-center">
            Artist Loyalty
          </motion.h2>
          
          <motion.div className="text-center mb-8">
            <span className="text-6xl">{artistLoyalty.personality?.emoji}</span>
            <h3 className="text-3xl font-bold text-spotify-green mt-2">{artistLoyalty.personality?.type}</h3>
            <p className="text-spotify-lightgray">{artistLoyalty.personality?.description}</p>
          </motion.div>
          
          <div className="max-w-2xl mx-auto w-full">
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <Heart className="w-5 h-5 text-red-500" /> Ride or Die Artists
                </h4>
                <div className="space-y-3">
                  {artistLoyalty.loyal_artists?.slice(0, 5).map((artist, i) => (
                    <motion.div
                      key={artist.name}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      {artist.image && (
                        <img src={artist.image} alt={artist.name} className="w-10 h-10 rounded-full" />
                      )}
                      <span className="text-white">{artist.name}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <ArrowUp className="w-5 h-5 text-green-500" /> Rising Stars
                </h4>
                <div className="space-y-3">
                  {artistLoyalty.rising_artists?.slice(0, 5).map((artist, i) => (
                    <motion.div
                      key={artist.name}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      {artist.image && (
                        <img src={artist.image} alt={artist.name} className="w-10 h-10 rounded-full" />
                      )}
                      <span className="text-white">{artist.name}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          <motion.div className="text-center mt-8">
            <p className="text-spotify-lightgray">Loyalty Score</p>
            <p className="text-5xl font-black text-spotify-green">{Math.round(artistLoyalty.loyalty_score)}%</p>
          </motion.div>
        </motion.div>
      )
    },

    // Slide 7: Decade Breakdown
    {
      id: 'decades',
      bg: 'from-pink-900/30 via-black to-black',
      content: savedAnalysis && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-4 text-center">
            Your Music Time Machine
          </motion.h2>
          
          {savedAnalysis.era_personality && (
            <motion.div className="text-center mb-8">
              <span className="text-6xl">{savedAnalysis.era_personality.emoji}</span>
              <h3 className="text-3xl font-bold text-spotify-green mt-2">{savedAnalysis.era_personality.name}</h3>
              <p className="text-spotify-lightgray">{savedAnalysis.era_personality.description}</p>
            </motion.div>
          )}
          
          <div className="max-w-2xl mx-auto w-full">
            <div className="flex items-end justify-center gap-4 h-48">
              {savedAnalysis.decades?.map((decade, i) => (
                <motion.div
                  key={decade.decade}
                  initial={{ height: 0 }}
                  animate={{ height: `${(decade.count / Math.max(...savedAnalysis.decades.map(d => d.count))) * 100}%` }}
                  transition={{ delay: i * 0.1 }}
                  className="w-16 bg-gradient-to-t from-spotify-green to-green-400 rounded-t flex flex-col items-center justify-end pb-2"
                >
                  <span className="text-black font-bold text-sm">{decade.count}</span>
                </motion.div>
              ))}
            </div>
            <div className="flex justify-center gap-4 mt-2">
              {savedAnalysis.decades?.map((decade) => (
                <span key={decade.decade} className="w-16 text-center text-spotify-lightgray text-sm">
                  {decade.decade}
                </span>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-8 mt-8 max-w-lg mx-auto">
            {savedAnalysis.oldest_track && (
              <div className="text-center">
                <p className="text-spotify-lightgray text-sm">Oldest Track</p>
                <p className="text-white font-semibold">{savedAnalysis.oldest_track.name}</p>
                <p className="text-spotify-green">{savedAnalysis.oldest_track.year}</p>
              </div>
            )}
            {savedAnalysis.newest_track && (
              <div className="text-center">
                <p className="text-spotify-lightgray text-sm">Newest Track</p>
                <p className="text-white font-semibold">{savedAnalysis.newest_track.name}</p>
                <p className="text-spotify-green">{savedAnalysis.newest_track.year}</p>
              </div>
            )}
          </div>
        </motion.div>
      )
    },

    // Slide 8: Top 5 Songs
    {
      id: 'top-songs',
      bg: 'from-green-900/30 via-black to-black',
      content: wrappedData && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8 text-center">
            Your Top 5 Songs
          </motion.h2>
          <div className="space-y-4 max-w-2xl mx-auto w-full">
            {wrappedData.top_tracks?.map((track, index) => (
              <motion.div
                key={track.position}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center space-x-4 bg-spotify-darkgray/50 p-4 rounded-lg hover:bg-spotify-darkgray transition-colors"
              >
                <div className="text-4xl font-black text-spotify-green w-12">
                  {track.position}
                </div>
                {track.image && (
                  <img src={track.image} alt={track.name} className="w-16 h-16 rounded shadow-lg" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold truncate">{track.name}</p>
                  <p className="text-spotify-lightgray text-sm truncate">{track.artist}</p>
                </div>
                {track.preview_url && (
                  <button
                    onClick={() => togglePlay(track)}
                    className="p-3 bg-spotify-green rounded-full text-black hover:scale-110 transition-transform"
                  >
                    {playingTrack === track.name ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )
    },

    // Slide 9: Top 5 Artists
    {
      id: 'top-artists',
      bg: 'from-cyan-900/30 via-black to-black',
      content: wrappedData && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8 text-center">
            Your Top 5 Artists
          </motion.h2>
          <div className="space-y-4 max-w-2xl mx-auto w-full">
            {wrappedData.top_artists?.map((artist, index) => (
              <motion.div
                key={artist.position}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center space-x-4 bg-spotify-darkgray/50 p-4 rounded-lg"
              >
                <div className="text-4xl font-black text-spotify-green w-12">
                  {artist.position}
                </div>
                {artist.image && (
                  <img src={artist.image} alt={artist.name} className="w-16 h-16 rounded-full shadow-lg" />
                )}
                <div className="flex-1">
                  <p className="text-white font-semibold">{artist.name}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )
    },

    // Slide 10: Audio Aura
    {
      id: 'aura',
      bg: 'from-purple-900/30 via-black to-pink-900/30',
      content: wrappedData?.audio_aura && (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-8">Your Audio Aura</motion.h2>
          <div className="relative w-80 h-80">
            {wrappedData.audio_aura.map((color, index) => (
              <motion.div
                key={index}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1 - (index * 0.15), opacity: 0.8 - (index * 0.2) }}
                transition={{ delay: index * 0.2, duration: 0.8 }}
                className={`absolute inset-0 rounded-full bg-gradient-to-br ${color.gradient} blur-2xl`}
              />
            ))}
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.8 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <Sparkles className="w-24 h-24 text-white drop-shadow-lg" />
            </motion.div>
          </div>
          <motion.div className="mt-8 flex gap-4">
            {wrappedData.audio_aura.map((color, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 + (index * 0.1) }}
                className="text-center"
              >
                <div 
                  className="w-8 h-8 rounded-full mx-auto mb-2"
                  style={{ backgroundColor: color.hex }}
                />
                <p className="text-white text-sm">{color.name}</p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      )
    },

    // Slide 11: Summary Stats
    {
      id: 'summary',
      bg: 'from-spotify-green/20 via-black to-black',
      content: wrappedData && (
        <motion.div className="h-full flex flex-col justify-center p-8">
          <motion.h2 className="text-4xl font-bold text-white mb-12 text-center">
            Your {year} By The Numbers
          </motion.h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {[
              { icon: <Music className="w-8 h-8" />, value: wrappedData.stats?.total_tracks_analyzed, label: 'Top Tracks' },
              { icon: <Users className="w-8 h-8" />, value: wrappedData.stats?.total_artists_analyzed, label: 'Top Artists' },
              { icon: <Radio className="w-8 h-8" />, value: wrappedData.stats?.unique_genres, label: 'Genres' },
              { icon: <Clock className="w-8 h-8" />, value: `${wrappedData.stats?.estimated_minutes}`, label: 'Est. Minutes' },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-spotify-green mb-2 flex justify-center">{stat.icon}</div>
                <p className="text-4xl font-black text-white">{stat.value}</p>
                <p className="text-spotify-lightgray">{stat.label}</p>
              </motion.div>
            ))}
          </div>
          
          {wrappedData.listening_personality && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-12 text-center"
            >
              <p className="text-spotify-lightgray mb-4">Your Listening Personality</p>
              <div className="flex justify-center gap-4 flex-wrap">
                {wrappedData.listening_personality.map((trait, i) => (
                  <div key={i} className="bg-spotify-darkgray px-6 py-3 rounded-full">
                    <span className="mr-2">{trait.icon}</span>
                    <span className="text-white font-semibold">{trait.type}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )
    },

    // Slide 12: Thank You
    {
      id: 'thanks',
      bg: 'from-spotify-green/30 via-black to-purple-900/30',
      content: (
        <motion.div className="h-full flex flex-col items-center justify-center p-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", bounce: 0.5 }}
            className="mb-8"
          >
            <Star className="w-24 h-24 text-spotify-green" />
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-5xl md:text-7xl font-black text-white mb-4 text-center"
          >
            That's Your {year}!
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-xl text-spotify-lightgray mb-8 text-center"
          >
            Enhanced Edition • More than Spotify shows you
          </motion.p>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex gap-4"
          >
            <button
              onClick={() => setCurrentSlide(0)}
              className="px-8 py-4 bg-spotify-green text-black font-bold rounded-full hover:scale-105 transition-transform"
            >
              Watch Again
            </button>
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="px-8 py-4 bg-transparent border-2 border-white text-white font-bold rounded-full hover:bg-white hover:text-black transition-all"
            >
              Back to Dashboard
            </button>
          </motion.div>
        </motion.div>
      )
    }
  ] : [];

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) setCurrentSlide(currentSlide + 1);
  };

  const prevSlide = () => {
    if (currentSlide > 0) setCurrentSlide(currentSlide - 1);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentSlide]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
        >
          <Music className="w-16 h-16 text-spotify-green" />
        </motion.div>
        <p className="text-spotify-lightgray mt-4">Loading your enhanced experience...</p>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br ${slides[currentSlide]?.bg || 'from-black to-black'} text-white overflow-hidden relative transition-all duration-500`}>
      {/* Animated Background */}
      <motion.div
        animate={{
          background: [
            'radial-gradient(circle at 20% 50%, rgba(29, 185, 84, 0.2) 0%, transparent 50%)',
            'radial-gradient(circle at 80% 50%, rgba(29, 185, 84, 0.2) 0%, transparent 50%)',
            'radial-gradient(circle at 20% 50%, rgba(29, 185, 84, 0.2) 0%, transparent 50%)',
          ]
        }}
        transition={{ duration: 10, repeat: Infinity }}
        className="absolute inset-0"
      />

      {/* Content */}
      <div className="relative z-10 h-screen flex flex-col">
        {/* Progress Bar */}
        <div className="w-full h-1 bg-spotify-darkgray flex">
          {slides.map((_, i) => (
            <div 
              key={i} 
              className={`flex-1 transition-all duration-300 ${i <= currentSlide ? 'bg-spotify-green' : 'bg-transparent'}`}
            />
          ))}
        </div>

        {/* Slides */}
        <div className="flex-1 relative overflow-hidden">
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
        <div className="flex justify-between items-center p-6">
          <button
            onClick={prevSlide}
            className={`flex items-center gap-2 text-white px-4 py-2 rounded-full transition-all ${
              currentSlide === 0 ? 'opacity-0 pointer-events-none' : 'hover:bg-white/10'
            }`}
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </button>

          <div className="flex gap-2">
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
            className={`flex items-center gap-2 text-black bg-spotify-green px-6 py-2 rounded-full font-bold transition-all ${
              currentSlide === slides.length - 1 ? 'opacity-0 pointer-events-none' : 'hover:scale-105'
            }`}
          >
            Next
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedWrapped;
