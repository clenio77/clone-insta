import React, { useState, useEffect } from 'react';
import Post from '../components/Post';
import Stories from '../components/Stories';
import TrendingHashtags from '../components/TrendingHashtags';
import { postsAPI } from '../services/api';

function Home({ user }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      const response = await postsAPI.getFeed();
      setPosts(response.data);
    } catch (error) {
      setError('Failed to load posts');
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading posts...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (posts.length === 0) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <h2>Welcome to Instagram Clone!</h2>
        <p>No posts to show yet. Follow some users or upload your first post!</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="home-layout">
        <div className="home-main">
          <Stories currentUser={user} />
          {posts.map(post => (
            <Post
              key={post.id}
              post={post}
              onUpdate={loadPosts}
            />
          ))}
        </div>
        <div className="home-sidebar">
          <TrendingHashtags />
        </div>
      </div>
    </div>
  );
}

export default Home;
