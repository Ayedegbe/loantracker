import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem('loggedIn') === 'true') {
      navigate('/dashboard');
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    // TODO: Connect to backend login route
    
   fetch('https://loantracker-backend.onrender.com/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier: username, password })
    })
      .then(async (res) => {
        const text = await res.text();
        console.log('Raw login response:', text);
        let data;
        try {
          data =JSON.parse(text);
        } catch(e) {
          throw new Error('Invalid JSON response from backend');
        }
        if (res.ok) {
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('loggedIn', 'true');
          navigate('/dashboard');
        } else {
          alert(data.message || 'Login failed');
        }
      
      })
      .catch(err => {
        console.error('Login error:', err);
        alert('Login failed. Please try again')
      });

        };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Worker Login</h2>
        <form onSubmit={handleLogin}>
          <label>Username</label>
          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">Login</button>
        </form>
        <div className="login-links">
          <a href="#">Forgot password?</a>
          <Link to="/register">Create a new account</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
