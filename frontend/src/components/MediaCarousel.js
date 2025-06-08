import React, { useState } from 'react';
import VideoPlayer from './VideoPlayer';

function MediaCarousel({ images = [], videos = [], className = "" }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Combinar imagens e vídeos em uma lista ordenada
  const mediaItems = [];
  
  // Adicionar imagens
  images.forEach(image => {
    mediaItems.push({
      type: 'image',
      url: image.image_url,
      order: image.order_index,
      id: `img_${image.id}`
    });
  });

  // Adicionar vídeos
  videos.forEach(video => {
    mediaItems.push({
      type: 'video',
      url: video.video_url,
      thumbnail: video.thumbnail_url,
      order: video.order_index,
      id: `vid_${video.id}`
    });
  });

  // Ordenar por order_index
  mediaItems.sort((a, b) => a.order - b.order);

  if (mediaItems.length === 0) {
    return null;
  }

  // Se há apenas um item, não mostrar controles
  if (mediaItems.length === 1) {
    const item = mediaItems[0];
    return (
      <div className={`media-carousel-single ${className}`}>
        {item.type === 'image' ? (
          <img 
            src={`http://localhost:8000${item.url}`}
            alt="Post media"
            className="carousel-single-media"
          />
        ) : (
          <VideoPlayer 
            src={`http://localhost:8000${item.url}`}
            className="carousel-single-media"
            autoPlay={false}
            muted={true}
            loop={true}
          />
        )}
      </div>
    );
  }

  const nextMedia = () => {
    setCurrentIndex((prev) => (prev + 1) % mediaItems.length);
  };

  const prevMedia = () => {
    setCurrentIndex((prev) => (prev - 1 + mediaItems.length) % mediaItems.length);
  };

  const goToMedia = (index) => {
    setCurrentIndex(index);
  };

  const currentItem = mediaItems[currentIndex];

  return (
    <div className={`media-carousel ${className}`}>
      {/* Mídia atual */}
      <div className="carousel-media-container">
        {currentItem.type === 'image' ? (
          <img 
            src={`http://localhost:8000${currentItem.url}`}
            alt={`Post media ${currentIndex + 1}`}
            className="carousel-media"
          />
        ) : (
          <VideoPlayer 
            src={`http://localhost:8000${currentItem.url}`}
            className="carousel-media"
            autoPlay={false}
            muted={true}
            loop={true}
          />
        )}
        
        {/* Botões de navegação */}
        {mediaItems.length > 1 && (
          <>
            <button 
              className="carousel-btn carousel-btn-prev"
              onClick={prevMedia}
              aria-label="Previous media"
            >
              ‹
            </button>
            <button 
              className="carousel-btn carousel-btn-next"
              onClick={nextMedia}
              aria-label="Next media"
            >
              ›
            </button>
          </>
        )}

        {/* Indicador de tipo de mídia */}
        <div className="media-type-indicator">
          {currentItem.type === 'video' && (
            <span className="video-indicator">📹</span>
          )}
        </div>
      </div>

      {/* Indicadores */}
      {mediaItems.length > 1 && (
        <div className="carousel-indicators">
          {mediaItems.map((item, index) => (
            <button
              key={item.id}
              className={`carousel-indicator ${index === currentIndex ? 'active' : ''} ${item.type}`}
              onClick={() => goToMedia(index)}
              aria-label={`Go to ${item.type} ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Contador */}
      {mediaItems.length > 1 && (
        <div className="carousel-counter">
          {currentIndex + 1} / {mediaItems.length}
        </div>
      )}
    </div>
  );
}

export default MediaCarousel;
