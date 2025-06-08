import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../services/api';

function Register({ onLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    bio: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authAPI.register(formData);
      
      // Auto login after registration
      const loginResponse = await authAPI.login({
        username: formData.username,
        password: formData.password
      });
      
      const { access_token } = loginResponse.data;
      const userResponse = await authAPI.getCurrentUser();
      onLogin(userResponse.data, access_token);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            name="full_name"
            placeholder="Full Name"
            value={formData.full_name}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            name="bio"
            placeholder="Bio (optional)"
            value={formData.bio}
            onChange={handleChange}
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Signing up...' : 'Sign Up'}
        </button>
        {error && <div className="error">{error}</div>}
      </form>
      <p style={{ textAlign: 'center', marginTop: '20px' }}>
        Have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}

export default Register;
