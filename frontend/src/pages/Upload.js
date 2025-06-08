import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsAPI } from '../services/api';

function Upload() {
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  const [caption, setCaption] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previews, setPreviews] = useState([]);
  const navigate = useNavigate();

  const handleMediaChange = (e) => {
    const files = Array.from(e.target.files);

    if (files.length === 0) return;

    const totalMedia = images.length + videos.length + files.length;
    if (totalMedia > 10) {
      setError('Maximum 10 media files allowed');
      return;
    }

    // Separar imagens e vídeos
    const newImages = [];
    const newVideos = [];

    files.forEach(file => {
      const fileType = file.type.split('/')[0];
      if (fileType === 'image') {
        newImages.push(file);
      } else if (fileType === 'video') {
        newVideos.push(file);
      }
    });

    setImages(prev => [...prev, ...newImages]);
    setVideos(prev => [...prev, ...newVideos]);
    setError('');

    // Criar previews
    const allFiles = [...images, ...videos, ...files];
    const newPreviews = [];

    allFiles.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        newPreviews[index] = {
          src: e.target.result,
          type: file.type.split('/')[0],
          name: file.name
        };
        if (newPreviews.filter(p => p).length === allFiles.length) {
          setPreviews([...newPreviews]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (images.length === 0 && videos.length === 0) {
      setError('Please select at least one image or video');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();

    images.forEach((image) => {
      formData.append('images', image);
    });

    videos.forEach((video) => {
      formData.append('videos', video);
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

  const removeMedia = (indexToRemove) => {
    const allMedia = [...images, ...videos];
    const mediaToRemove = allMedia[indexToRemove];

    if (mediaToRemove.type.startsWith('image/')) {
      const imageIndex = images.indexOf(mediaToRemove);
      setImages(prev => prev.filter((_, index) => index !== imageIndex));
    } else {
      const videoIndex = videos.indexOf(mediaToRemove);
      setVideos(prev => prev.filter((_, index) => index !== videoIndex));
    }

    setPreviews(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  return (
    <div className="container">
      <div className="upload-form">
        <h2>Create New Post</h2>
        <form onSubmit={handleSubmit}>
          <div className="file-input">
            <input
              type="file"
              accept="image/*,video/*"
              multiple
              onChange={handleMediaChange}
              required
            />
            <p className="file-input-help">
              Select up to 10 images and/or videos (hold Ctrl/Cmd to select multiple)
            </p>
          </div>

          {previews.length > 0 && (
            <div className="upload-previews">
              <h4>Selected Media ({previews.length}/10)</h4>
              <div className="preview-grid">
                {previews.map((preview, index) => (
                  <div key={index} className="preview-item">
                    {preview.type === 'image' ? (
                      <img
                        src={preview.src}
                        alt={`Preview ${index + 1}`}
                        className="preview-media"
                      />
                    ) : (
                      <video
                        src={preview.src}
                        className="preview-media"
                        muted
                      />
                    )}
                    <button
                      type="button"
                      className="remove-media-btn"
                      onClick={() => removeMedia(index)}
                      aria-label={`Remove ${preview.type} ${index + 1}`}
                    >
                      ×
                    </button>
                    <div className="preview-index">{index + 1}</div>
                    <div className="media-type-badge">
                      {preview.type === 'video' ? '📹' : '🖼️'}
                    </div>
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

          <button type="submit" className="btn" disabled={loading || (images.length === 0 && videos.length === 0)}>
            {loading ? 'Uploading...' : 'Share'}
          </button>

          {error && <div className="error">{error}</div>}
        </form>
      </div>
    </div>
  );
}

export default Upload;
