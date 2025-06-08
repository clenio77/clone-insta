import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getCurrentUser: () => api.get('/users/me'),
};

// Users API
export const usersAPI = {
  getProfile: (username) => api.get(`/users/${username}`),
  followUser: (username) => api.post(`/users/${username}/follow`),
  unfollowUser: (username) => api.delete(`/users/${username}/follow`),
};

// Posts API
export const postsAPI = {
  createPost: (formData) => api.post('/posts', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getFeed: (skip = 0, limit = 20) => api.get(`/posts?skip=${skip}&limit=${limit}`),
  getPost: (postId) => api.get(`/posts/${postId}`),
  likePost: (postId) => api.post(`/posts/${postId}/like`),
  unlikePost: (postId) => api.delete(`/posts/${postId}/like`),
};

// Comments API
export const commentsAPI = {
  createComment: (postId, content) => api.post(`/posts/${postId}/comments`, { content }),
  getComments: (postId, skip = 0, limit = 50) => api.get(`/posts/${postId}/comments?skip=${skip}&limit=${limit}`),
};

// Stories API
export const storiesAPI = {
  createStory: (formData) => api.post('/stories', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getStories: () => api.get('/stories'),
  getUserStories: (username) => api.get(`/stories/user/${username}`),
  viewStory: (storyId) => api.post(`/stories/${storyId}/view`),
  getStoryViews: (storyId) => api.get(`/stories/${storyId}/views`),
};

export default api;
