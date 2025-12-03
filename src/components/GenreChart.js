import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { Hash, PieChart, BarChart3 } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const GenreChart = ({ stats }) => {
  const chartColors = [
    '#1DB954', '#1ED760', '#21E065', '#2FE56D', '#3EEA76',
    '#4DEE7F', '#5CF188', '#6BF491', '#7AF79A', '#89FAA3'
  ];

  const doughnutData = {
    labels: stats.top_genres?.slice(0, 10).map(g => g.genre) || [],
    datasets: [{
      data: stats.top_genres?.slice(0, 10).map(g => g.count) || [],
      backgroundColor: chartColors,
      borderColor: '#191414',
      borderWidth: 2,
      hoverOffset: 4
    }]
  };

  const barData = {
    labels: stats.top_genres?.slice(0, 10).map(g => g.genre) || [],
    datasets: [{
      label: 'Track Count',
      data: stats.top_genres?.slice(0, 10).map(g => g.count) || [],
      backgroundColor: chartColors.map(color => color + '80'),
      borderColor: chartColors,
      borderWidth: 2,
      borderRadius: 8
    }]
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#B3B3B3',
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14
        },
        bodyFont: {
          size: 12
        },
        padding: 12,
        borderColor: '#1DB954',
        borderWidth: 1
      }
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14
        },
        bodyFont: {
          size: 12
        },
        padding: 12,
        borderColor: '#1DB954',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          borderColor: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#B3B3B3'
        }
      },
      y: {
        grid: {
          display: false
        },
        ticks: {
          color: '#B3B3B3'
        }
      }
    }
  };

  const totalTracks = stats.top_genres?.reduce((sum, g) => sum + g.count, 0) || 0;

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-2">Your Genre Landscape</h2>
        <p className="text-spotify-lightgray">Exploring the diversity of your music taste</p>
      </div>

      {/* Main Genre Stats */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6 text-center"
        >
          <Hash className="w-10 h-10 text-spotify-green mx-auto mb-4" />
          <p className="text-3xl font-bold text-white">{stats.top_genres?.length || 0}</p>
          <p className="text-spotify-lightgray">Unique Genres</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-2xl p-6 text-center"
        >
          <PieChart className="w-10 h-10 text-spotify-green mx-auto mb-4" />
          <p className="text-3xl font-bold text-white">{stats.top_genre || 'N/A'}</p>
          <p className="text-spotify-lightgray">Most Played Genre</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-2xl p-6 text-center"
        >
          <BarChart3 className="w-10 h-10 text-spotify-green mx-auto mb-4" />
          <p className="text-3xl font-bold text-white">{totalTracks}</p>
          <p className="text-spotify-lightgray">Total Genre Plays</p>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-xl font-bold text-white mb-4">Genre Distribution</h3>
          <div style={{ height: '400px' }}>
            <Doughnut data={doughnutData} options={doughnutOptions} />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-xl font-bold text-white mb-4">Genre Frequency</h3>
          <div style={{ height: '400px' }}>
            <Bar data={barData} options={barOptions} />
          </div>
        </motion.div>
      </div>

      {/* Genre Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass rounded-2xl p-6"
      >
        <h3 className="text-xl font-bold text-white mb-6">Genre Breakdown</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stats.top_genres?.slice(0, 12).map((genre, index) => (
            <motion.div
              key={genre.genre}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-3 bg-spotify-darkgray/50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <div 
                  className="w-4 h-4 rounded-full" 
                  style={{ backgroundColor: chartColors[index % chartColors.length] }}
                />
                <span className="text-white font-medium">{genre.genre}</span>
              </div>
              <span className="text-spotify-lightgray text-sm">{genre.count} tracks</span>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Genre Characteristics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="glass rounded-2xl p-6 text-center"
      >
        <p className="text-spotify-lightgray mb-4">Your music taste is</p>
        <div className="flex flex-wrap justify-center gap-3">
          {stats.characteristics?.map((char, index) => (
            <span
              key={index}
              className="px-6 py-3 bg-gradient-to-r from-spotify-green/20 to-spotify-green/10 text-spotify-green rounded-full text-lg font-semibold"
            >
              {char}
            </span>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default GenreChart;
