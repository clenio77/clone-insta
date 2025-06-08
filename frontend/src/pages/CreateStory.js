import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { storiesAPI } from '../services/api';

function CreateStory() {
  const [image, setImage] = useState(null);
  const [textContent, setTextContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState(null);
  const navigate = useNavigate();

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('image', image);
    formData.append('text_content', textContent);

    try {
      await storiesAPI.createStory(formData);
      navigate('/');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create story');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="create-story-container">
        <h2>Create Your Story</h2>
        
        <form onSubmit={handleSubmit} className="create-story-form">
          <div className="story-preview-section">
            {preview ? (
              <div className="story-preview">
                <img src={preview} alt="Story preview" className="preview-image" />
                {textContent && (
                  <div className="preview-text-overlay">
                    {textContent}
                  </div>
                )}
              </div>
            ) : (
              <div className="story-placeholder">
                <span>Select an image to preview your story</span>
              </div>
            )}
          </div>

          <div className="story-controls">
            <div className="file-input-section">
              <label htmlFor="story-image" className="file-input-label">
                Choose Image
              </label>
              <input
                id="story-image"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                required
                style={{ display: 'none' }}
              />
            </div>

            <div className="text-input-section">
              <textarea
                className="story-text-input"
                placeholder="Add text to your story (optional)..."
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                maxLength={200}
              />
              <div className="character-count">
                {textContent.length}/200
              </div>
            </div>

            <div className="story-actions">
              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => navigate('/')}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="btn-primary"
                disabled={loading || !image}
              >
                {loading ? 'Sharing...' : 'Share Story'}
              </button>
            </div>

            {error && <div className="error">{error}</div>}
          </div>
        </form>

        <div className="story-info">
          <p>📱 Your story will be visible to your followers for 24 hours</p>
          <p>👀 You can see who viewed your story</p>
        </div>
      </div>
    </div>
  );
}

export default CreateStory;
