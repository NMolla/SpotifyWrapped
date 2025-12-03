import React from 'react';
import { motion } from 'framer-motion';
import { Music } from 'lucide-react';

const LoadingScreen = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-spotify-black">
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="relative"
      >
        <Music className="w-16 h-16 text-spotify-green" />
        <div className="absolute inset-0 bg-spotify-green blur-xl opacity-50"></div>
      </motion.div>
    </div>
  );
};

export default LoadingScreen;
