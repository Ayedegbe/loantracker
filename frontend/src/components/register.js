import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './login.css';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setname] = useState('');
  const [email, setemail] = useState('');
  const [phone, setPhone] = useState('');
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();
    fetch('https://loantracker-backend.onrender.com/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        password,
        name,
        phone,
        email
      })
    })
      .then(res => {
        if (res.ok) {
          alert('Account created!');
          navigate('/login');
        } else {
          return res.json().then(data => {
            alert(data.message || 'Registration failed');
          });
        }
      })
      .catch(err => console.error('Registration error:', err));
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Create Account</h2>
        <form onSubmit={handleRegister}>
          <label>Full Name</label>
          <input
            type="text"
            placeholder="Enter your full name"
            value={name}
            onChange={(e) => setname(e.target.value)}
            required
          />

          <label>Phone Number</label>
          <input
            type="tel"
            placeholder="Enter phone number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />

          <label>Username</label>
          <input
            type="text"
            placeholder="Choose a username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <label>Email</label>
          <input
            type="text"
            placeholder="Enter Email"
            value={email}
            onChange={(e) => setemail(e.target.value)}
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Choose a password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">Register</button>
        </form>
        <div className="login-links">
          <a href="/login">Back to Login</a>
        </div>
      </div>
    </div>
  );
}

export default Register;
