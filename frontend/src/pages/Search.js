import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { searchAPI } from '../services/api';
import MessageButton from '../components/MessageButton';

function Search({ currentUser }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    const queryParam = searchParams.get('q');
    if (queryParam) {
      setQuery(queryParam);
      performSearch(queryParam);
    }
  }, [searchParams]);

  const performSearch = async (searchQuery) => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setResults([]);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setHasSearched(true);

    try {
      const response = await searchAPI.searchUsers(searchQuery.trim());
      setResults(response.data);
    } catch (error) {
      console.error('Error searching users:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query.trim() });
      performSearch(query.trim());
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <div className="container">
      <div className="search-page">
        <div className="search-page-header">
          <h2>Search Users</h2>
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search for users..."
              value={query}
              onChange={handleInputChange}
              className="search-page-input"
            />
            <button type="submit" className="search-btn" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>
        </div>

        <div className="search-results-container">
          {loading ? (
            <div className="search-loading-state">
              <div className="loading-spinner"></div>
              <p>Searching users...</p>
            </div>
          ) : hasSearched ? (
            results.length === 0 ? (
              <div className="search-empty-state">
                <div className="empty-state-icon">🔍</div>
                <h3>No users found</h3>
                <p>Try searching for a different username or name.</p>
              </div>
            ) : (
              <div className="search-results-list">
                <div className="search-results-header">
                  <h3>{results.length} user{results.length !== 1 ? 's' : ''} found</h3>
                </div>
                {results.map(user => (
                  <div key={user.id} className="search-user-item">
                    <Link to={`/profile/${user.username}`} className="search-user-link">
                      <div className="search-user-avatar">
                        <div className="avatar-placeholder"></div>
                      </div>
                      <div className="search-user-info">
                        <div className="search-user-username">
                          {user.username}
                        </div>
                        <div className="search-user-name">
                          {user.full_name}
                        </div>
                        {user.bio && (
                          <div className="search-user-bio">
                            {user.bio}
                          </div>
                        )}
                      </div>
                    </Link>
                    <div className="search-user-actions">
                      <MessageButton 
                        userId={user.id} 
                        username={user.username}
                        className="search-message-btn"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : (
            <div className="search-initial-state">
              <div className="initial-state-icon">👥</div>
              <h3>Discover People</h3>
              <p>Search for users by their username or full name to connect with them.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Search;
