import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { hashtagsAPI } from '../services/api';

function TrendingHashtags() {
  const [hashtags, setHashtags] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrendingHashtags();
  }, []);

  const loadTrendingHashtags = async () => {
    try {
      const response = await hashtagsAPI.getTrendingHashtags(5);
      setHashtags(response.data);
    } catch (error) {
      console.error('Error loading trending hashtags:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="trending-hashtags">
        <h3>Trending Hashtags</h3>
        <div className="trending-loading">Loading...</div>
      </div>
    );
  }

  if (hashtags.length === 0) {
    return null;
  }

  return (
    <div className="trending-hashtags">
      <h3>Trending Hashtags</h3>
      <div className="trending-list">
        {hashtags.map(hashtag => (
          <Link 
            key={hashtag.id}
            to={`/hashtag/${hashtag.name}`}
            className="trending-hashtag-item"
          >
            <div className="trending-hashtag-name">
              #{hashtag.name}
            </div>
            <div className="trending-hashtag-count">
              {hashtag.posts_count} post{hashtag.posts_count !== 1 ? 's' : ''}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default TrendingHashtags;
