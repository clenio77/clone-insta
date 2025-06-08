import React from 'react';
import { Link } from 'react-router-dom';

function HashtagText({ text, className = "" }) {
  if (!text) return null;

  // Regex para encontrar hashtags
  const hashtagRegex = /#(\w+)/g;
  
  // Dividir o texto em partes, mantendo as hashtags
  const parts = text.split(hashtagRegex);
  
  return (
    <span className={className}>
      {parts.map((part, index) => {
        // Se o índice é ímpar, é uma hashtag (devido ao split com grupos de captura)
        if (index % 2 === 1) {
          return (
            <Link 
              key={index}
              to={`/hashtag/${part.toLowerCase()}`}
              className="hashtag-link"
              onClick={(e) => e.stopPropagation()}
            >
              #{part}
            </Link>
          );
        }
        // Caso contrário, é texto normal
        return part;
      })}
    </span>
  );
}

export default HashtagText;
