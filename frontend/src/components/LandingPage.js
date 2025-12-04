import React from 'react';
import { motion } from 'framer-motion';
import { Music, Sparkles, BarChart3, Users, TrendingUp, LogIn } from 'lucide-react';

const LandingPage = () => {
  const features = [
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Top Tracks & Artists',
      description: 'Discover your most played songs and favorite artists'
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'Listening Trends',
      description: 'Analyze your music taste over different time periods'
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: 'Genre Insights',
      description: 'Explore your music diversity and genre preferences'
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'Wrapped Card',
      description: 'Generate and share your personalized Wrapped summary'
    }
  ];

  const handleLogin = () => {
    window.location.href = 'http://127.0.0.1:5000/login';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-spotify-black via-spotify-darkgray to-spotify-black overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            rotate: 360,
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute -top-32 -left-32 w-96 h-96 bg-spotify-green rounded-full opacity-5 blur-3xl"
        />
        <motion.div
          animate={{
            rotate: -360,
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute -bottom-32 -right-32 w-96 h-96 bg-spotify-green rounded-full opacity-5 blur-3xl"
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <nav className="px-8 py-6">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div className="flex items-center space-x-2">
              <Music className="w-8 h-8 text-spotify-green" />
              <span className="text-2xl font-bold text-white">Spotify Wrapped</span>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="px-8 py-20">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center"
            >
              <h1 className="text-6xl md:text-8xl font-black text-white mb-6">
                Your <span className="text-spotify-green">{new Date().getFullYear()}</span> Wrapped
              </h1>
              <p className="text-xl md:text-2xl text-spotify-lightgray mb-12 max-w-2xl mx-auto">
                Discover your music journey with personalized insights, top tracks, and shareable stats
              </p>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogin}
                className="inline-flex items-center px-8 py-4 bg-spotify-green text-spotify-black font-bold text-lg rounded-full hover:bg-green-400 transition-all duration-300 shadow-2xl shadow-spotify-green/30"
              >
                <LogIn className="mr-3" />
                Connect with Spotify
              </motion.button>
            </motion.div>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-20"
            >
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 * index }}
                  whileHover={{ y: -5 }}
                  className="glass rounded-2xl p-6 hover:border-spotify-green/50 transition-all duration-300"
                >
                  <div className="w-12 h-12 bg-spotify-green/20 rounded-lg flex items-center justify-center mb-4 text-spotify-green">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-spotify-lightgray text-sm">{feature.description}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* Visual Preview */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="mt-20 relative"
            >
              <div className="glass rounded-3xl p-8 max-w-4xl mx-auto">
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="space-y-4">
                    <div className="h-32 bg-gradient-to-br from-spotify-green/20 to-transparent rounded-xl animate-pulse"></div>
                    <div className="h-20 bg-gradient-to-br from-spotify-green/10 to-transparent rounded-xl animate-pulse delay-100"></div>
                  </div>
                  <div className="space-y-4">
                    <div className="h-20 bg-gradient-to-br from-spotify-green/10 to-transparent rounded-xl animate-pulse delay-200"></div>
                    <div className="h-32 bg-gradient-to-br from-spotify-green/20 to-transparent rounded-xl animate-pulse delay-300"></div>
                  </div>
                  <div className="space-y-4">
                    <div className="h-24 bg-gradient-to-br from-spotify-green/15 to-transparent rounded-xl animate-pulse delay-400"></div>
                    <div className="h-28 bg-gradient-to-br from-spotify-green/15 to-transparent rounded-xl animate-pulse delay-500"></div>
                  </div>
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-spotify-black via-transparent to-transparent pointer-events-none"></div>
            </motion.div>
          </div>
        </div>

        {/* Footer */}
        <footer className="px-8 py-6 border-t border-spotify-gray/20">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-spotify-lightgray text-sm">
              Built with Spotify Web API • Not affiliated with Spotify AB
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;
