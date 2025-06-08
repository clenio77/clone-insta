import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { usersAPI, postsAPI } from '../services/api';
import MessageButton from '../components/MessageButton';

function Profile({ currentUser }) {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfile();
  }, [username]);

  const loadProfile = async () => {
    try {
      const response = await usersAPI.getProfile(username);
      setProfile(response.data);
      
      // Load user's posts (this would need to be implemented in the backend)
      // For now, we'll show an empty array
      setPosts([]);
    } catch (error) {
      setError('Failed to load profile');
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    try {
      if (profile.is_following) {
        await usersAPI.unfollowUser(username);
        setProfile(prev => ({
          ...prev,
          is_following: false,
          followers_count: prev.followers_count - 1
        }));
      } else {
        await usersAPI.followUser(username);
        setProfile(prev => ({
          ...prev,
          is_following: true,
          followers_count: prev.followers_count + 1
        }));
      }
    } catch (error) {
      console.error('Error toggling follow:', error);
    }
  };

  if (loading) {
    return <div>Loading profile...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!profile) {
    return <div>Profile not found</div>;
  }

  const isOwnProfile = currentUser.username === username;

  return (
    <div className="container">
      <div className="profile-header">
        <div className="profile-avatar"></div>
        <div className="profile-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <h1>{profile.username}</h1>
            {!isOwnProfile && (
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  className={profile.is_following ? 'unfollow-btn' : 'follow-btn'}
                  onClick={handleFollow}
                >
                  {profile.is_following ? 'Unfollow' : 'Follow'}
                </button>
                <MessageButton
                  userId={profile.id}
                  username={profile.username}
                />
              </div>
            )}
          </div>
          
          <div className="profile-stats">
            <span>{profile.posts_count} posts</span>
            <span>{profile.followers_count} followers</span>
            <span>{profile.following_count} following</span>
          </div>
          
          <div>
            <strong>{profile.full_name}</strong>
            {profile.bio && <p>{profile.bio}</p>}
          </div>
        </div>
      </div>
      
      <div className="posts-grid">
        {posts.length === 0 ? (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '50px' }}>
            <p>No posts yet</p>
          </div>
        ) : (
          posts.map(post => (
            <img
              key={post.id}
              src={`http://localhost:8000${post.image_url}`}
              alt={post.caption}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default Profile;
