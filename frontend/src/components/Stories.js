import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { storiesAPI } from '../services/api';

function Stories({ currentUser }) {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStory, setSelectedStory] = useState(null);
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      const response = await storiesAPI.getStories();
      // Agrupar stories por usuário
      const groupedStories = groupStoriesByUser(response.data);
      setStories(groupedStories);
    } catch (error) {
      console.error('Error loading stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupStoriesByUser = (storiesData) => {
    const grouped = {};
    storiesData.forEach(story => {
      const userId = story.author.id;
      if (!grouped[userId]) {
        grouped[userId] = {
          user: story.author,
          stories: [],
          hasUnviewed: false
        };
      }
      grouped[userId].stories.push(story);
      if (!story.is_viewed) {
        grouped[userId].hasUnviewed = true;
      }
    });
    return Object.values(grouped);
  };

  const openStoryViewer = (userStories, storyIndex = 0) => {
    setSelectedStory(userStories);
    setCurrentStoryIndex(storyIndex);
  };

  const closeStoryViewer = () => {
    setSelectedStory(null);
    setCurrentStoryIndex(0);
  };

  const nextStory = () => {
    if (selectedStory && currentStoryIndex < selectedStory.stories.length - 1) {
      setCurrentStoryIndex(currentStoryIndex + 1);
    } else {
      // Ir para o próximo usuário
      const currentUserIndex = stories.findIndex(s => s.user.id === selectedStory.user.id);
      if (currentUserIndex < stories.length - 1) {
        openStoryViewer(stories[currentUserIndex + 1], 0);
      } else {
        closeStoryViewer();
      }
    }
  };

  const prevStory = () => {
    if (currentStoryIndex > 0) {
      setCurrentStoryIndex(currentStoryIndex - 1);
    } else {
      // Ir para o usuário anterior
      const currentUserIndex = stories.findIndex(s => s.user.id === selectedStory.user.id);
      if (currentUserIndex > 0) {
        const prevUser = stories[currentUserIndex - 1];
        openStoryViewer(prevUser, prevUser.stories.length - 1);
      }
    }
  };

  const markAsViewed = async (storyId) => {
    try {
      await storiesAPI.viewStory(storyId);
    } catch (error) {
      console.error('Error marking story as viewed:', error);
    }
  };

  useEffect(() => {
    if (selectedStory && selectedStory.stories[currentStoryIndex]) {
      const currentStory = selectedStory.stories[currentStoryIndex];
      if (!currentStory.is_viewed) {
        markAsViewed(currentStory.id);
      }
    }
  }, [selectedStory, currentStoryIndex]);

  if (loading) {
    return <div className="stories-loading">Loading stories...</div>;
  }

  return (
    <>
      <div className="stories-container">
        <div className="stories-list">
          {/* Story do próprio usuário */}
          <div className="story-item own-story">
            <Link to="/create-story" className="story-avatar">
              <div className="avatar-placeholder">
                <span>+</span>
              </div>
            </Link>
            <span className="story-username">Your Story</span>
          </div>

          {/* Stories de outros usuários */}
          {stories.map((userStories) => (
            <div 
              key={userStories.user.id} 
              className="story-item"
              onClick={() => openStoryViewer(userStories)}
            >
              <div className={`story-avatar ${userStories.hasUnviewed ? 'unviewed' : 'viewed'}`}>
                <div className="avatar-placeholder"></div>
              </div>
              <span className="story-username">{userStories.user.username}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Story Viewer Modal */}
      {selectedStory && (
        <div className="story-viewer-overlay" onClick={closeStoryViewer}>
          <div className="story-viewer" onClick={(e) => e.stopPropagation()}>
            <div className="story-header">
              <div className="story-progress">
                {selectedStory.stories.map((_, index) => (
                  <div 
                    key={index} 
                    className={`progress-bar ${index <= currentStoryIndex ? 'active' : ''}`}
                  />
                ))}
              </div>
              <div className="story-user-info">
                <div className="story-avatar small">
                  <div className="avatar-placeholder"></div>
                </div>
                <span className="story-username">{selectedStory.user.username}</span>
                <span className="story-time">
                  {new Date(selectedStory.stories[currentStoryIndex].created_at).toLocaleTimeString()}
                </span>
              </div>
              <button className="close-story" onClick={closeStoryViewer}>×</button>
            </div>

            <div className="story-content">
              <img 
                src={`http://localhost:8000${selectedStory.stories[currentStoryIndex].image_url}`}
                alt="Story"
                className="story-image"
              />
              {selectedStory.stories[currentStoryIndex].text_content && (
                <div className="story-text">
                  {selectedStory.stories[currentStoryIndex].text_content}
                </div>
              )}
            </div>

            <div className="story-navigation">
              <button className="nav-btn prev" onClick={prevStory}>‹</button>
              <button className="nav-btn next" onClick={nextStory}>›</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Stories;
