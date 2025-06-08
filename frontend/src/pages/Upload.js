import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsAPI } from '../services/api';

function Upload() {
  const [image, setImage] = useState(null);
  const [caption, setCaption] = useState('');
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
    formData.append('caption', caption);

    try {
      await postsAPI.createPost(formData);
      navigate('/');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to upload post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="upload-form">
        <h2>Create New Post</h2>
        <form onSubmit={handleSubmit}>
          <div className="file-input">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              required
            />
          </div>
          
          {preview && (
            <div style={{ marginBottom: '16px' }}>
              <img 
                src={preview} 
                alt="Preview" 
                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }}
              />
            </div>
          )}
          
          <textarea
            className="caption-input"
            placeholder="Write a caption..."
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
          />
          
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Uploading...' : 'Share'}
          </button>
          
          {error && <div className="error">{error}</div>}
        </form>
      </div>
    </div>
  );
}

export default Upload;
