import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Post from '../components/Post';
import { hashtagsAPI } from '../services/api';

function Hashtag({ currentUser }) {
  const { hashtagName } = useParams();
  const [hashtag, setHashtag] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHashtagData();
  }, [hashtagName]);

  const loadHashtagData = async () => {
    setLoading(true);
    setError('');

    try {
      // Carregar dados da hashtag
      const hashtagResponse = await hashtagsAPI.getHashtag(hashtagName);
      setHashtag(hashtagResponse.data);

      // Carregar posts da hashtag
      const postsResponse = await hashtagsAPI.getHashtagPosts(hashtagName);
      setPosts(postsResponse.data);
    } catch (error) {
      setError('Hashtag not found');
      console.error('Error loading hashtag:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMorePosts = async () => {
    try {
      const response = await hashtagsAPI.getHashtagPosts(hashtagName, posts.length);
      setPosts(prev => [...prev, ...response.data]);
    } catch (error) {
      console.error('Error loading more posts:', error);
    }
  };

  if (loading) {
    return <div className="hashtag-loading">Loading hashtag...</div>;
  }

  if (error) {
    return (
      <div className="container">
        <div className="hashtag-error">
          <div className="error-icon">#</div>
          <h2>Hashtag not found</h2>
          <p>The hashtag #{hashtagName} doesn't exist or has no posts.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="hashtag-page">
        {/* Header da hashtag */}
        <div className="hashtag-header">
          <div className="hashtag-icon">#</div>
          <div className="hashtag-info">
            <h1>#{hashtag.name}</h1>
            <div className="hashtag-stats">
              <span>{hashtag.posts_count} post{hashtag.posts_count !== 1 ? 's' : ''}</span>
            </div>
          </div>
        </div>

        {/* Grid de posts */}
        <div className="hashtag-content">
          {posts.length === 0 ? (
            <div className="no-posts">
              <div className="no-posts-icon">#</div>
              <h3>No posts yet</h3>
              <p>Be the first to post with #{hashtag.name}</p>
            </div>
          ) : (
            <>
              {/* Grid view para posts */}
              <div className="hashtag-posts-grid">
                {posts.map(post => (
                  <div key={post.id} className="hashtag-post-item">
                    <img 
                      src={`http://localhost:8000${post.image_url}`}
                      alt={post.caption}
                      className="hashtag-post-image"
                    />
                    <div className="hashtag-post-overlay">
                      <div className="hashtag-post-stats">
                        <span>❤️ {post.likes_count}</span>
                        <span>💬 {post.comments_count}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Feed view para posts */}
              <div className="hashtag-posts-feed" style={{ display: 'none' }}>
                {posts.map(post => (
                  <Post 
                    key={post.id} 
                    post={post} 
                    onUpdate={loadHashtagData}
                  />
                ))}
              </div>

              {/* Botão para carregar mais */}
              {posts.length >= 20 && (
                <div className="load-more-container">
                  <button onClick={loadMorePosts} className="load-more-btn">
                    Load More Posts
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Hashtag;
