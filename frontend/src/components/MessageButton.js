import React from 'react';
import { useNavigate } from 'react-router-dom';
import { messagesAPI } from '../services/api';

function MessageButton({ userId, username, className = "message-btn" }) {
  const navigate = useNavigate();

  const startConversation = async () => {
    try {
      const response = await messagesAPI.getOrCreateConversation(userId);
      navigate(`/messages/${response.data.id}`);
    } catch (error) {
      console.error('Error starting conversation:', error);
    }
  };

  return (
    <button 
      onClick={startConversation}
      className={className}
    >
      Message
    </button>
  );
}

export default MessageButton;
