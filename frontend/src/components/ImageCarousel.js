import React, { useState } from 'react';

function ImageCarousel({ images, className = "" }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!images || images.length === 0) {
    return null;
  }

  // Se há apenas uma imagem, não mostrar controles
  if (images.length === 1) {
    return (
      <img 
        src={`http://localhost:8000${images[0].image_url}`}
        alt="Post"
        className={`carousel-single-image ${className}`}
      />
    );
  }

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const goToImage = (index) => {
    setCurrentIndex(index);
  };

  return (
    <div className={`image-carousel ${className}`}>
      {/* Imagem atual */}
      <div className="carousel-image-container">
        <img 
          src={`http://localhost:8000${images[currentIndex].image_url}`}
          alt={`Post image ${currentIndex + 1}`}
          className="carousel-image"
        />
        
        {/* Botões de navegação */}
        {images.length > 1 && (
          <>
            <button 
              className="carousel-btn carousel-btn-prev"
              onClick={prevImage}
              aria-label="Previous image"
            >
              ‹
            </button>
            <button 
              className="carousel-btn carousel-btn-next"
              onClick={nextImage}
              aria-label="Next image"
            >
              ›
            </button>
          </>
        )}
      </div>

      {/* Indicadores */}
      {images.length > 1 && (
        <div className="carousel-indicators">
          {images.map((_, index) => (
            <button
              key={index}
              className={`carousel-indicator ${index === currentIndex ? 'active' : ''}`}
              onClick={() => goToImage(index)}
              aria-label={`Go to image ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Contador */}
      {images.length > 1 && (
        <div className="carousel-counter">
          {currentIndex + 1} / {images.length}
        </div>
      )}
    </div>
  );
}

export default ImageCarousel;
