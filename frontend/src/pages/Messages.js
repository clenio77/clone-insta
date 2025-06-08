import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { messagesAPI } from '../services/api';

function Messages({ currentUser }) {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (conversationId) {
      loadMessages(conversationId);
    }
  }, [conversationId]);

  const loadConversations = async () => {
    try {
      const response = await messagesAPI.getConversations();
      setConversations(response.data);
      
      // Se há um conversationId na URL, selecionar essa conversa
      if (conversationId) {
        const conv = response.data.find(c => c.id === parseInt(conversationId));
        if (conv) {
          setSelectedConversation(conv);
        }
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const response = await messagesAPI.getMessages(convId);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    navigate(`/messages/${conversation.id}`);
    loadMessages(conversation.id);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    setSendingMessage(true);
    try {
      const messageData = {
        receiver_id: selectedConversation.other_user.id,
        content: newMessage,
        message_type: 'text'
      };

      const response = await messagesAPI.sendMessage(messageData);
      setMessages(prev => [...prev, response.data]);
      setNewMessage('');
      
      // Atualizar lista de conversas
      loadConversations();
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSendingMessage(false);
    }
  };

  const sendImageMessage = async (file) => {
    if (!selectedConversation) return;

    setSendingMessage(true);
    try {
      const formData = new FormData();
      formData.append('receiver_id', selectedConversation.other_user.id);
      formData.append('image', file);

      const response = await messagesAPI.sendImageMessage(formData);
      setMessages(prev => [...prev, response.data]);
      
      // Atualizar lista de conversas
      loadConversations();
    } catch (error) {
      console.error('Error sending image:', error);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      sendImageMessage(file);
    }
  };

  if (loading) {
    return <div className="messages-loading">Loading messages...</div>;
  }

  return (
    <div className="messages-container">
      {/* Lista de conversas */}
      <div className="conversations-sidebar">
        <div className="conversations-header">
          <h2>Messages</h2>
        </div>
        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="no-conversations">
              <p>No conversations yet</p>
              <p>Start a conversation by visiting someone's profile</p>
            </div>
          ) : (
            conversations.map(conversation => (
              <div
                key={conversation.id}
                className={`conversation-item ${selectedConversation?.id === conversation.id ? 'active' : ''}`}
                onClick={() => selectConversation(conversation)}
              >
                <div className="conversation-avatar">
                  <div className="avatar-placeholder"></div>
                </div>
                <div className="conversation-info">
                  <div className="conversation-name">
                    {conversation.other_user.username}
                  </div>
                  <div className="conversation-last-message">
                    {conversation.last_message ? (
                      conversation.last_message.message_type === 'image' ? 
                        '📷 Photo' : 
                        conversation.last_message.content
                    ) : 'Start a conversation'}
                  </div>
                </div>
                {conversation.unread_count > 0 && (
                  <div className="unread-badge">
                    {conversation.unread_count}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Área de chat */}
      <div className="chat-area">
        {selectedConversation ? (
          <>
            {/* Header do chat */}
            <div className="chat-header">
              <div className="chat-user-info">
                <div className="chat-avatar">
                  <div className="avatar-placeholder"></div>
                </div>
                <div className="chat-user-name">
                  {selectedConversation.other_user.username}
                </div>
              </div>
            </div>

            {/* Mensagens */}
            <div className="messages-area">
              {messages.length === 0 ? (
                <div className="no-messages">
                  <p>No messages yet</p>
                  <p>Send a message to start the conversation</p>
                </div>
              ) : (
                messages.map(message => (
                  <div
                    key={message.id}
                    className={`message ${message.sender_id === currentUser.id ? 'sent' : 'received'}`}
                  >
                    {message.message_type === 'image' ? (
                      <div className="message-image">
                        <img 
                          src={`http://localhost:8000${message.image_url}`} 
                          alt="Sent image"
                        />
                      </div>
                    ) : (
                      <div className="message-text">
                        {message.content}
                      </div>
                    )}
                    <div className="message-time">
                      {new Date(message.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input de mensagem */}
            <div className="message-input-area">
              <form onSubmit={sendMessage} className="message-form">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  style={{ display: 'none' }}
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="image-upload-btn">
                  📷
                </label>
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="message-input"
                  disabled={sendingMessage}
                />
                <button 
                  type="submit" 
                  className="send-btn"
                  disabled={sendingMessage || !newMessage.trim()}
                >
                  {sendingMessage ? '...' : 'Send'}
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="no-conversation-selected">
            <h3>Select a conversation</h3>
            <p>Choose a conversation from the sidebar to start messaging</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Messages;
