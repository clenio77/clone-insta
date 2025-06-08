import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { searchAPI } from '../services/api';

function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const searchRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (query.trim().length >= 2) {
      setLoading(true);
      timeoutRef.current = setTimeout(async () => {
        try {
          const response = await searchAPI.searchUsers(query.trim());
          setResults(response.data);
          setIsOpen(true);
        } catch (error) {
          console.error('Error searching users:', error);
          setResults([]);
        } finally {
          setLoading(false);
        }
      }, 300); // Debounce de 300ms
    } else {
      setResults([]);
      setIsOpen(false);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [query]);

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const handleResultClick = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
  };

  return (
    <div className="search-container" ref={searchRef}>
      <div className="search-input-container">
        <input
          type="text"
          placeholder="Search users..."
          value={query}
          onChange={handleInputChange}
          className="search-input"
          onFocus={() => query.trim().length >= 2 && setIsOpen(true)}
        />
        {query && (
          <button onClick={clearSearch} className="search-clear-btn">
            ×
          </button>
        )}
        {loading && (
          <div className="search-loading">
            <div className="loading-spinner"></div>
          </div>
        )}
      </div>

      {isOpen && (
        <div className="search-results">
          {results.length === 0 ? (
            <div className="search-no-results">
              {loading ? 'Searching...' : 'No users found'}
            </div>
          ) : (
            results.map(user => (
              <Link
                key={user.id}
                to={`/profile/${user.username}`}
                className="search-result-item"
                onClick={handleResultClick}
              >
                <div className="search-result-avatar">
                  <div className="avatar-placeholder"></div>
                </div>
                <div className="search-result-info">
                  <div className="search-result-username">
                    {user.username}
                  </div>
                  <div className="search-result-name">
                    {user.full_name}
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default SearchBar;
