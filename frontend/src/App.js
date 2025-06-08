import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Upload from './pages/Upload';
import CreateStory from './pages/CreateStory';
import Messages from './pages/Messages';
import Notifications from './pages/Notifications';
import { authAPI } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authAPI.getCurrentUser()
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        {user && <Header user={user} onLogout={handleLogout} />}
        <main className="main-content">
          <Routes>
            <Route 
              path="/login" 
              element={user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />} 
            />
            <Route 
              path="/register" 
              element={user ? <Navigate to="/" /> : <Register onLogin={handleLogin} />} 
            />
            <Route 
              path="/" 
              element={user ? <Home user={user} /> : <Navigate to="/login" />} 
            />
            <Route
              path="/upload"
              element={user ? <Upload /> : <Navigate to="/login" />}
            />
            <Route
              path="/create-story"
              element={user ? <CreateStory /> : <Navigate to="/login" />}
            />
            <Route
              path="/messages"
              element={user ? <Messages currentUser={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/messages/:conversationId"
              element={user ? <Messages currentUser={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/notifications"
              element={user ? <Notifications /> : <Navigate to="/login" />}
            />
            <Route
              path="/profile/:username"
              element={user ? <Profile currentUser={user} /> : <Navigate to="/login" />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
