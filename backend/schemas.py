from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = ""

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    profile_picture: Optional[str] = ""
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(User):
    followers_count: int
    following_count: int
    posts_count: int
    is_following: bool = False

# Post Image schemas
class PostImageBase(BaseModel):
    image_url: str
    order_index: int = 0

class PostImage(PostImageBase):
    id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Post schemas
class PostBase(BaseModel):
    caption: Optional[str] = ""

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    image_url: Optional[str] = None  # Para compatibilidade
    created_at: datetime
    author_id: int
    author: User
    likes_count: int
    comments_count: int
    is_liked: bool = False
    images: List[PostImage] = []
    primary_image_url: Optional[str] = None

    class Config:
        from_attributes = True

# Comment schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    created_at: datetime
    author_id: int
    post_id: int
    author: User
    
    class Config:
        from_attributes = True

# Like schema
class Like(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Story schemas
class StoryBase(BaseModel):
    text_content: Optional[str] = ""

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int
    image_url: str
    created_at: datetime
    expires_at: datetime
    author_id: int
    author: User
    is_active: bool
    is_expired: bool
    views_count: int
    is_viewed: bool = False

    class Config:
        from_attributes = True

class StoryView(BaseModel):
    id: int
    story_id: int
    viewer_id: int
    viewed_at: datetime
    viewer: User

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    content: Optional[str] = None
    message_type: str = "text"

class MessageCreate(MessageBase):
    receiver_id: int

class Message(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    receiver_id: int
    image_url: Optional[str] = None
    is_read: bool
    created_at: datetime
    sender: User
    receiver: User

    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    pass

class Conversation(ConversationBase):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    updated_at: datetime
    user1: User
    user2: User
    last_message: Optional[Message] = None
    unread_count: int = 0
    other_user: Optional[User] = None

    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    notification_type: str
    message: str

class Notification(NotificationBase):
    id: int
    receiver_id: int
    sender_id: Optional[int] = None
    related_post_id: Optional[int] = None
    related_comment_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    sender: Optional[User] = None
    related_post: Optional[Post] = None

    class Config:
        from_attributes = True

# Hashtag schemas
class HashtagBase(BaseModel):
    name: str

class Hashtag(HashtagBase):
    id: int
    posts_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
