import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import LoadingScreen from './components/LoadingScreen';
import SpotifyWrapped2025 from './components/SpotifyWrapped2025';
import WrappedHub from './components/WrappedHub';

// Set up axios defaults
axios.defaults.withCredentials = true;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/');
      setIsAuthenticated(response.data.authenticated);
    } catch (error) {
      console.error('Error checking authentication:', error);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <LandingPage />} 
        />
        <Route 
          path="/dashboard" 
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/" />} 
        />
        <Route 
          path="/wrapped" 
          element={isAuthenticated ? <SpotifyWrapped2025 /> : <Navigate to="/" />} 
        />
        <Route 
          path="/hub" 
          element={isAuthenticated ? <WrappedHub /> : <Navigate to="/" />} 
        />
      </Routes>
    </Router>
  );
}

export default App;
