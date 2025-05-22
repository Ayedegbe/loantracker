import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Login from './components/login';
import Register from './components/register'; 
import Dashboard from './components/dashboard';
import Profile from './components/Profile';

function App() {
  const token = localStorage.getItem('token');
  
  return (
  <Router>
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} /> {/* ✅ */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/Profile" element={<Profile />} />
      <Route path="*" element={<Login />} /> {/* Redirect all unknown routes to login */}
    </Routes>
  </Router>
  );
}

export default App;
