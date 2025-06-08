import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsAPI } from '../services/api';

function Upload() {
  const [images, setImages] = useState([]);
  const [caption, setCaption] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previews, setPreviews] = useState([]);
  const navigate = useNavigate();

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);

    if (files.length === 0) return;

    if (files.length > 10) {
      setError('Maximum 10 images allowed');
      return;
    }

    setImages(files);
    setError('');

    // Criar previews
    const newPreviews = [];
    files.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        newPreviews[index] = e.target.result;
        if (newPreviews.length === files.length) {
          setPreviews([...newPreviews]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (images.length === 0) {
      setError('Please select at least one image');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    images.forEach((image) => {
      formData.append('images', image);
    });
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

  const removeImage = (indexToRemove) => {
    const newImages = images.filter((_, index) => index !== indexToRemove);
    const newPreviews = previews.filter((_, index) => index !== indexToRemove);
    setImages(newImages);
    setPreviews(newPreviews);
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
              multiple
              onChange={handleImageChange}
              required
            />
            <p className="file-input-help">
              Select up to 10 images (hold Ctrl/Cmd to select multiple)
            </p>
          </div>

          {previews.length > 0 && (
            <div className="upload-previews">
              <h4>Selected Images ({previews.length}/10)</h4>
              <div className="preview-grid">
                {previews.map((preview, index) => (
                  <div key={index} className="preview-item">
                    <img
                      src={preview}
                      alt={`Preview ${index + 1}`}
                      className="preview-image"
                    />
                    <button
                      type="button"
                      className="remove-image-btn"
                      onClick={() => removeImage(index)}
                      aria-label={`Remove image ${index + 1}`}
                    >
                      ×
                    </button>
                    <div className="preview-index">{index + 1}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <textarea
            className="caption-input"
            placeholder="Write a caption..."
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
          />

          <button type="submit" className="btn" disabled={loading || images.length === 0}>
            {loading ? 'Uploading...' : 'Share'}
          </button>

          {error && <div className="error">{error}</div>}
        </form>
      </div>
    </div>
  );
}

export default Upload;
