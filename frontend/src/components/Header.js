import React from 'react';
import { Link } from 'react-router-dom';

function Header({ user, onLogout }) {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          Instagram Clone
        </Link>
        <nav className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/upload">Upload</Link>
          <Link to="/create-story">Story</Link>
          <Link to={`/profile/${user.username}`}>Profile</Link>
          <button onClick={onLogout}>Logout</button>
        </nav>
      </div>
    </header>
  );
}

export default Header;
