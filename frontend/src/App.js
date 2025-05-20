import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Login from './components/login';
import Register from './components/register'; 
import Dashboard from './components/dashboard';

function App() {
  return (
  <Router>
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} /> {/* ✅ */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="*" element={<Login />} /> {/* Redirect all unknown routes to login */}
    </Routes>
  </Router>
  );
}

export default App;
