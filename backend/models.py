from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from database import Base

# Tabela de associação para seguidores
followers_table = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    bio = Column(Text, default="")
    profile_picture = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="author", cascade="all, delete-orphan")
    story_views = relationship("StoryView", back_populates="viewer", cascade="all, delete-orphan")

    # Direct Messages
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    conversations_as_user1 = relationship("Conversation", foreign_keys="Conversation.user1_id", back_populates="user1", cascade="all, delete-orphan")
    conversations_as_user2 = relationship("Conversation", foreign_keys="Conversation.user2_id", back_populates="user2", cascade="all, delete-orphan")
    
    # Seguidores e seguindo
    followers = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.followed_id,
        secondaryjoin=id == followers_table.c.follower_id,
        back_populates="following"
    )
    following = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.follower_id,
        secondaryjoin=id == followers_table.c.followed_id,
        back_populates="followers"
    )

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    caption = Column(Text, default="")
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relacionamentos
    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    # Relacionamentos
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    text_content = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relacionamentos
    author = relationship("User", back_populates="stories")
    views = relationship("StoryView", back_populates="story", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            # Stories expiram em 24 horas
            self.expires_at = datetime.utcnow() + timedelta(hours=24)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    @property
    def views_count(self):
        return len(self.views)

class StoryView(Base):
    __tablename__ = "story_views"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    viewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    story = relationship("Story", back_populates="views")
    viewer = relationship("User", back_populates="story_views")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="conversations_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="conversations_as_user2")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    @property
    def last_message(self):
        if self.messages:
            return max(self.messages, key=lambda m: m.created_at)
        return None

    def get_other_user(self, current_user_id):
        return self.user2 if self.user1_id == current_user_id else self.user1

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    message_type = Column(String, default="text")  # text, image
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
