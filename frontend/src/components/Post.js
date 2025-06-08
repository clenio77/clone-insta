import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { postsAPI, commentsAPI } from '../services/api';

function Post({ post, onUpdate }) {
  const [isLiked, setIsLiked] = useState(post.is_liked);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  const [comment, setComment] = useState('');
  const [comments, setComments] = useState([]);
  const [showComments, setShowComments] = useState(false);

  const handleLike = async () => {
    try {
      if (isLiked) {
        await postsAPI.unlikePost(post.id);
        setIsLiked(false);
        setLikesCount(prev => prev - 1);
      } else {
        await postsAPI.likePost(post.id);
        setIsLiked(true);
        setLikesCount(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;

    try {
      const response = await commentsAPI.createComment(post.id, comment);
      setComments(prev => [response.data, ...prev]);
      setComment('');
    } catch (error) {
      console.error('Error creating comment:', error);
    }
  };

  const loadComments = async () => {
    if (!showComments) {
      try {
        const response = await commentsAPI.getComments(post.id);
        setComments(response.data);
        setShowComments(true);
      } catch (error) {
        console.error('Error loading comments:', error);
      }
    } else {
      setShowComments(false);
    }
  };

  return (
    <article className="post">
      <header className="post-header">
        <div className="post-avatar"></div>
        <Link to={`/profile/${post.author.username}`} className="post-username">
          {post.author.username}
        </Link>
      </header>
      
      <img 
        src={`http://localhost:8000${post.image_url}`} 
        alt={post.caption} 
        className="post-image"
      />
      
      <div className="post-actions">
        <button onClick={handleLike}>
          {isLiked ? '❤️' : '🤍'}
        </button>
        <button onClick={loadComments}>
          💬
        </button>
      </div>
      
      <div className="post-likes">
        {likesCount} {likesCount === 1 ? 'like' : 'likes'}
      </div>
      
      {post.caption && (
        <div className="post-caption">
          <span className="username">{post.author.username}</span>
          {post.caption}
        </div>
      )}
      
      {showComments && (
        <div className="comments">
          {comments.map(comment => (
            <div key={comment.id} className="comment">
              <span className="username">{comment.author.username}</span>
              {comment.content}
            </div>
          ))}
        </div>
      )}
      
      <form onSubmit={handleComment} className="comment-form">
        <input
          type="text"
          placeholder="Add a comment..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
        <button type="submit">Post</button>
      </form>
    </article>
  );
}

export default Post;
