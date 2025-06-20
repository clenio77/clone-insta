from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import re
from database import Base

# Tabela de associação para seguidores
followers_table = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# Tabela de associação para hashtags e posts
post_hashtags_table = Table(
    'post_hashtags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'), primary_key=True)
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

    # Notifications
    sent_notifications = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_notifications = relationship("Notification", foreign_keys="Notification.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    
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
    image_url = Column(String, nullable=True)  # Para compatibilidade com posts antigos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relacionamentos
    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    hashtags = relationship("Hashtag", secondary=post_hashtags_table, back_populates="posts")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    videos = relationship("PostVideo", back_populates="post", cascade="all, delete-orphan")

    def extract_hashtags(self):
        """Extrai hashtags do caption do post"""
        if not self.caption:
            return []
        hashtag_pattern = r'#(\w+)'
        return re.findall(hashtag_pattern, self.caption.lower())

    @property
    def primary_image_url(self):
        """Retorna a URL da primeira imagem ou a image_url legacy"""
        if self.images:
            return self.images[0].image_url
        return self.image_url

    @property
    def has_videos(self):
        """Verifica se o post tem vídeos"""
        return len(self.videos) > 0

    @property
    def media_type(self):
        """Retorna o tipo de mídia do post"""
        if self.videos:
            return "video" if len(self.videos) == 1 and len(self.images) == 0 else "mixed"
        elif self.images:
            return "image"
        else:
            return "image"  # fallback para posts antigos

class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    image_url = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    post = relationship("Post", back_populates="images")

class PostVideo(Base):
    __tablename__ = "post_videos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # em segundos
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    post = relationship("Post", back_populates="videos")

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

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    posts_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    posts = relationship("Post", secondary=post_hashtags_table, back_populates="hashtags")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notification_type = Column(String, nullable=False)  # like, comment, follow, message
    message = Column(Text, nullable=False)
    related_post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    related_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_notifications")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_notifications")
    related_post = relationship("Post", foreign_keys=[related_post_id])
    related_comment = relationship("Comment", foreign_keys=[related_comment_id])
