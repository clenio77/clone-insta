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

# Post schemas
class PostBase(BaseModel):
    caption: Optional[str] = ""

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    image_url: str
    created_at: datetime
    author_id: int
    author: User
    likes_count: int
    comments_count: int
    is_liked: bool = False
    
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

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
