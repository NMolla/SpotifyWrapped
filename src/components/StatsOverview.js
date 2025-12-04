import React from 'react';
import { motion } from 'framer-motion';
import { Music, User, Hash, Clock, Award, TrendingUp, Headphones, Star, Calendar } from 'lucide-react';

const StatsOverview = ({ stats, timeRange }) => {
  const statCards = [
    {
      icon: <Music className="w-6 h-6" />,
      label: 'Top Track',
      value: stats.top_track?.name || 'N/A',
      subvalue: stats.top_track?.artist || '',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <User className="w-6 h-6" />,
      label: 'Top Artist',
      value: stats.top_artist?.name || 'N/A',
      subvalue: stats.top_artist?.genres?.[0] || '',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <Hash className="w-6 h-6" />,
      label: 'Top Genre',
      value: stats.top_genre || 'N/A',
      subvalue: `${stats.top_genres?.[0]?.count || 0} tracks`,
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: <Clock className="w-6 h-6" />,
      label: 'Total Minutes',
      value: stats.total_minutes?.toLocaleString() || '0',
      subvalue: `${Math.round(stats.total_minutes / 60)} hours`,
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: <Headphones className="w-6 h-6" />,
      label: 'Tracks Played',
      value: stats.total_tracks || '0',
      subvalue: 'unique tracks',
      color: 'from-indigo-500 to-purple-500'
    },
    {
      icon: <Star className="w-6 h-6" />,
      label: 'Artists Discovered',
      value: stats.total_artists || '0',
      subvalue: 'unique artists',
      color: 'from-pink-500 to-rose-500'
    },
    {
      icon: <Calendar className="w-6 h-6" />,
      label: 'My Listening Age',
      value: stats.listening_age?.favorite_decade || 'N/A',
      subvalue: stats.listening_age?.average_age ? `Avg: ${stats.listening_age.average_age} years old` : '',
      color: 'from-amber-500 to-yellow-500'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Hero Stats */}
      <div className="text-center mb-12">
        <motion.h2
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl font-black text-white mb-4"
        >
          Your {stats.time_period} Stats
        </motion.h2>
        <div className="flex justify-center space-x-4 text-spotify-lightgray">
          {stats.characteristics?.map((char, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="px-4 py-2 glass rounded-full text-sm font-medium"
            >
              {char}
            </motion.span>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="glass rounded-2xl p-6 relative overflow-hidden group"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-5 group-hover:opacity-10 transition-opacity`}></div>
            
            <div className="relative z-10">
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} p-2.5 text-white mb-4`}>
                {stat.icon}
              </div>
              <p className="text-spotify-lightgray text-sm font-medium mb-2">{stat.label}</p>
              <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
              {stat.subvalue && (
                <p className="text-sm text-spotify-lightgray">{stat.subvalue}</p>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Featured Content */}
      <div className="grid md:grid-cols-2 gap-6 mt-8">
        {/* Top Track Card */}
        {stats.top_track?.image && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl overflow-hidden"
          >
            <div className="flex items-center p-6">
              <img
                src={stats.top_track.image}
                alt={stats.top_track.name}
                className="w-24 h-24 rounded-lg object-cover mr-6"
              />
              <div>
                <p className="text-spotify-lightgray text-sm mb-2">Your #1 Track</p>
                <p className="text-xl font-bold text-white mb-1">{stats.top_track.name}</p>
                <p className="text-spotify-lightgray">{stats.top_track.artist}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Top Artist Card */}
        {stats.top_artist?.image && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl overflow-hidden"
          >
            <div className="flex items-center p-6">
              <img
                src={stats.top_artist.image}
                alt={stats.top_artist.name}
                className="w-24 h-24 rounded-full object-cover mr-6"
              />
              <div>
                <p className="text-spotify-lightgray text-sm mb-2">Your #1 Artist</p>
                <p className="text-xl font-bold text-white mb-1">{stats.top_artist.name}</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Popularity Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass rounded-2xl p-8 text-center"
      >
        <TrendingUp className="w-12 h-12 text-spotify-green mx-auto mb-4" />
        <p className="text-spotify-lightgray mb-2">Average Track Popularity</p>
        <div className="flex items-center justify-center">
          <span className="text-6xl font-black text-white">{Math.round(stats.avg_popularity || 0)}</span>
          <span className="text-2xl text-spotify-lightgray ml-2">/100</span>
        </div>
        <div className="w-full max-w-md mx-auto mt-4">
          <div className="h-3 bg-spotify-darkgray rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${stats.avg_popularity || 0}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className="h-full bg-gradient-to-r from-spotify-green to-green-400"
            />
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default StatsOverview;
