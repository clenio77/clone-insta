import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { notificationsAPI } from '../services/api';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await notificationsAPI.getNotifications();
      setNotifications(response.data);
    } catch (error) {
      setError('Failed to load notifications');
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificationsAPI.markAsRead(notificationId);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, is_read: true }
            : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationsAPI.markAllAsRead();
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, is_read: true }))
      );
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'like':
        return '❤️';
      case 'comment':
        return '💬';
      case 'follow':
        return '👤';
      case 'message':
        return '📩';
      default:
        return '🔔';
    }
  };

  const getNotificationLink = (notification) => {
    switch (notification.notification_type) {
      case 'like':
      case 'comment':
        return notification.related_post_id ? `/post/${notification.related_post_id}` : '#';
      case 'follow':
        return notification.sender ? `/profile/${notification.sender.username}` : '#';
      case 'message':
        return '/messages';
      default:
        return '#';
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) {
      return 'just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}d ago`;
    }
  };

  if (loading) {
    return <div className="notifications-loading">Loading notifications...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="container">
      <div className="notifications-container">
        <div className="notifications-header">
          <h2>Notifications</h2>
          {unreadCount > 0 && (
            <button 
              onClick={markAllAsRead}
              className="mark-all-read-btn"
            >
              Mark all as read ({unreadCount})
            </button>
          )}
        </div>

        <div className="notifications-list">
          {notifications.length === 0 ? (
            <div className="no-notifications">
              <div className="no-notifications-icon">🔔</div>
              <h3>No notifications yet</h3>
              <p>When someone likes, comments, or follows you, you'll see it here.</p>
            </div>
          ) : (
            notifications.map(notification => (
              <div
                key={notification.id}
                className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                onClick={() => {
                  if (!notification.is_read) {
                    markAsRead(notification.id);
                  }
                }}
              >
                <div className="notification-icon">
                  {getNotificationIcon(notification.notification_type)}
                </div>

                <div className="notification-content">
                  <div className="notification-avatar">
                    {notification.sender && (
                      <div className="avatar-placeholder"></div>
                    )}
                  </div>

                  <div className="notification-text">
                    <Link 
                      to={getNotificationLink(notification)}
                      className="notification-link"
                    >
                      {notification.message}
                    </Link>
                    <div className="notification-time">
                      {formatTime(notification.created_at)}
                    </div>
                  </div>

                  {notification.related_post && notification.related_post.image_url && (
                    <div className="notification-post-preview">
                      <img 
                        src={`http://localhost:8000${notification.related_post.image_url}`}
                        alt="Post preview"
                      />
                    </div>
                  )}
                </div>

                {!notification.is_read && (
                  <div className="unread-indicator"></div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default Notifications;
