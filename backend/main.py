from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import timedelta, datetime
import shutil
import os
from typing import List
import uuid

from database import SessionLocal, engine, get_db
from models import Base, User, Post, Like, Comment, Story, StoryView, Conversation, Message, Notification, Hashtag, PostImage
from schemas import UserCreate, UserLogin, Token, PostCreate, CommentCreate, User as UserSchema, Post as PostSchema, Comment as CommentSchema, UserProfile, StoryCreate, Story as StorySchema, StoryView as StoryViewSchema, MessageCreate, Message as MessageSchema, Conversation as ConversationSchema, Notification as NotificationSchema, Hashtag as HashtagSchema, PostImage as PostImageSchema
from auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Instagram Clone API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Função para criar notificações
def create_notification(db: Session, receiver_id: int, sender_id: int, notification_type: str, message: str, related_post_id: int = None, related_comment_id: int = None):
    if receiver_id == sender_id:
        return  # Não criar notificação para si mesmo

    notification = Notification(
        receiver_id=receiver_id,
        sender_id=sender_id,
        notification_type=notification_type,
        message=message,
        related_post_id=related_post_id,
        related_comment_id=related_comment_id
    )
    db.add(notification)
    db.commit()
    return notification

# Função para processar hashtags
def process_hashtags(db: Session, post: Post):
    hashtag_names = post.extract_hashtags()

    for hashtag_name in hashtag_names:
        # Buscar ou criar hashtag
        hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag_name).first()
        if not hashtag:
            hashtag = Hashtag(name=hashtag_name, posts_count=0)
            db.add(hashtag)
            db.flush()  # Para obter o ID

        # Associar hashtag ao post se ainda não estiver associada
        if hashtag not in post.hashtags:
            post.hashtags.append(hashtag)
            hashtag.posts_count += 1

    db.commit()

# Auth endpoints
@app.post("/auth/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar se usuário já existe
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Criar novo usuário
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints
@app.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/{username}", response_model=UserProfile)
async def get_user_profile(
    username: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    followers_count = len(user.followers)
    following_count = len(user.following)
    posts_count = len(user.posts)
    is_following = current_user in user.followers
    
    return UserProfile(
        **user.__dict__,
        followers_count=followers_count,
        following_count=following_count,
        posts_count=posts_count,
        is_following=is_following
    )

# Follow/Unfollow
@app.post("/users/{username}/follow")
async def follow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_to_follow = db.query(User).filter(User.username == username).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_follow == current_user:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    if current_user not in user_to_follow.followers:
        user_to_follow.followers.append(current_user)
        db.commit()

        # Criar notificação
        create_notification(
            db=db,
            receiver_id=user_to_follow.id,
            sender_id=current_user.id,
            notification_type="follow",
            message=f"{current_user.username} started following you"
        )

    return {"message": "User followed successfully"}

@app.delete("/users/{username}/follow")
async def unfollow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_to_unfollow = db.query(User).filter(User.username == username).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user in user_to_unfollow.followers:
        user_to_unfollow.followers.remove(current_user)
        db.commit()

    return {"message": "User unfollowed successfully"}

# Post endpoints
@app.post("/posts", response_model=PostSchema)
async def create_post(
    caption: str = Form(""),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not images or len(images) == 0:
        raise HTTPException(status_code=400, detail="At least one image is required")

    if len(images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

    # Criar post
    db_post = Post(
        caption=caption,
        author_id=current_user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    # Salvar imagens
    for index, image in enumerate(images):
        file_extension = image.filename.split(".")[-1]
        filename = f"post_{db_post.id}_{index}_{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/{filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Criar registro da imagem
        post_image = PostImage(
            post_id=db_post.id,
            image_url=f"/uploads/{filename}",
            order_index=index
        )
        db.add(post_image)

    # Para compatibilidade, definir image_url como a primeira imagem
    if images:
        db_post.image_url = f"/uploads/post_{db_post.id}_0_{uuid.uuid4().hex[:8]}.{images[0].filename.split('.')[-1]}"

    db.commit()
    db.refresh(db_post)

    # Processar hashtags
    process_hashtags(db, db_post)

    # Adicionar dados extras
    db_post.author = current_user
    db_post.likes_count = 0
    db_post.comments_count = 0
    db_post.is_liked = False

    return db_post

@app.get("/posts", response_model=List[PostSchema])
async def get_feed(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Buscar posts dos usuários seguidos + próprios posts
    following_ids = [user.id for user in current_user.following]
    following_ids.append(current_user.id)

    posts = db.query(Post).filter(Post.author_id.in_(following_ids)).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

    # Adicionar dados extras para cada post
    for post in posts:
        post.likes_count = len(post.likes)
        post.comments_count = len(post.comments)
        post.is_liked = any(like.user_id == current_user.id for like in post.likes)
        post.primary_image_url = post.primary_image_url

    return posts

@app.get("/posts/{post_id}", response_model=PostSchema)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.likes_count = len(post.likes)
    post.comments_count = len(post.comments)
    post.is_liked = any(like.user_id == current_user.id for like in post.likes)
    post.primary_image_url = post.primary_image_url

    return post

# Like endpoints
@app.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = db.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()

    # Criar notificação
    create_notification(
        db=db,
        receiver_id=post.author_id,
        sender_id=current_user.id,
        notification_type="like",
        message=f"{current_user.username} liked your post",
        related_post_id=post_id
    )

    return {"message": "Post liked successfully"}

@app.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    like = db.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()

    return {"message": "Post unliked successfully"}

# Comment endpoints
@app.post("/posts/{post_id}/comments", response_model=CommentSchema)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = Comment(
        content=comment.content,
        author_id=current_user.id,
        post_id=post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    # Criar notificação
    create_notification(
        db=db,
        receiver_id=post.author_id,
        sender_id=current_user.id,
        notification_type="comment",
        message=f"{current_user.username} commented on your post",
        related_post_id=post_id,
        related_comment_id=db_comment.id
    )

    db_comment.author = current_user
    return db_comment

@app.get("/posts/{post_id}/comments", response_model=List[CommentSchema])
async def get_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    return comments

# Story endpoints
@app.post("/stories", response_model=StorySchema)
async def create_story(
    text_content: str = Form(""),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Salvar imagem
    file_extension = image.filename.split(".")[-1]
    filename = f"story_{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Criar story
    db_story = Story(
        text_content=text_content,
        image_url=f"/uploads/{filename}",
        author_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)

    # Adicionar dados extras
    db_story.author = current_user
    db_story.views_count = 0
    db_story.is_viewed = False
    db_story.is_expired = False

    return db_story

@app.get("/stories", response_model=List[StorySchema])
async def get_stories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Buscar stories dos usuários seguidos + próprios stories (não expirados)
    following_ids = [user.id for user in current_user.following]
    following_ids.append(current_user.id)

    current_time = datetime.utcnow()
    stories = db.query(Story).filter(
        Story.author_id.in_(following_ids),
        Story.expires_at > current_time,
        Story.is_active == True
    ).order_by(Story.created_at.desc()).all()

    # Adicionar dados extras para cada story
    for story in stories:
        story.views_count = len(story.views)
        story.is_expired = story.expires_at <= current_time
        # Verificar se o usuário atual já viu este story
        story.is_viewed = any(view.viewer_id == current_user.id for view in story.views)

    return stories

@app.get("/stories/user/{username}", response_model=List[StorySchema])
async def get_user_stories(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_time = datetime.utcnow()
    stories = db.query(Story).filter(
        Story.author_id == user.id,
        Story.expires_at > current_time,
        Story.is_active == True
    ).order_by(Story.created_at.desc()).all()

    # Adicionar dados extras
    for story in stories:
        story.views_count = len(story.views)
        story.is_expired = story.expires_at <= current_time
        story.is_viewed = any(view.viewer_id == current_user.id for view in story.views)

    return stories

@app.post("/stories/{story_id}/view")
async def view_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    if story.is_expired:
        raise HTTPException(status_code=400, detail="Story has expired")

    # Verificar se já visualizou
    existing_view = db.query(StoryView).filter(
        StoryView.story_id == story_id,
        StoryView.viewer_id == current_user.id
    ).first()

    if not existing_view:
        view = StoryView(story_id=story_id, viewer_id=current_user.id)
        db.add(view)
        db.commit()

    return {"message": "Story viewed successfully"}

@app.get("/stories/{story_id}/views", response_model=List[StoryViewSchema])
async def get_story_views(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Apenas o autor pode ver quem visualizou
    if story.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view story views")

    views = db.query(StoryView).filter(StoryView.story_id == story_id).order_by(StoryView.viewed_at.desc()).all()
    return views

# Direct Messages endpoints
@app.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        )
    ).order_by(desc(Conversation.updated_at)).all()

    # Adicionar dados extras para cada conversa
    for conv in conversations:
        conv.other_user = conv.get_other_user(current_user.id)
        # Contar mensagens não lidas
        conv.unread_count = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).count()

    return conversations

@app.get("/conversations/{user_id}", response_model=ConversationSchema)
async def get_or_create_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot create conversation with yourself")

    # Verificar se o usuário existe
    other_user = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Buscar conversa existente
    conversation = db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == current_user.id, Conversation.user2_id == user_id),
            and_(Conversation.user1_id == user_id, Conversation.user2_id == current_user.id)
        )
    ).first()

    # Criar nova conversa se não existir
    if not conversation:
        conversation = Conversation(
            user1_id=min(current_user.id, user_id),
            user2_id=max(current_user.id, user_id)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Adicionar dados extras
    conversation.other_user = conversation.get_other_user(current_user.id)
    conversation.unread_count = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()

    return conversation

@app.get("/conversations/{conversation_id}/messages", response_model=List[MessageSchema])
async def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verificar se o usuário faz parte da conversa
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

    # Marcar mensagens como lidas
    unread_messages = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).all()

    for message in unread_messages:
        message.is_read = True

    if unread_messages:
        db.commit()

    return list(reversed(messages))  # Retornar em ordem cronológica

@app.post("/messages", response_model=MessageSchema)
async def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if message_data.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    # Verificar se o receptor existe
    receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Buscar ou criar conversa
    conversation = db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == current_user.id, Conversation.user2_id == message_data.receiver_id),
            and_(Conversation.user1_id == message_data.receiver_id, Conversation.user2_id == current_user.id)
        )
    ).first()

    if not conversation:
        conversation = Conversation(
            user1_id=min(current_user.id, message_data.receiver_id),
            user2_id=max(current_user.id, message_data.receiver_id)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Criar mensagem
    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content,
        message_type=message_data.message_type
    )
    db.add(message)

    # Atualizar timestamp da conversa
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    # Criar notificação
    create_notification(
        db=db,
        receiver_id=message_data.receiver_id,
        sender_id=current_user.id,
        notification_type="message",
        message=f"{current_user.username} sent you a message"
    )

    return message

@app.post("/messages/image", response_model=MessageSchema)
async def send_image_message(
    receiver_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    # Verificar se o receptor existe
    receiver = db.query(User).filter(User.id == receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Salvar imagem
    file_extension = image.filename.split(".")[-1]
    filename = f"message_{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Buscar ou criar conversa
    conversation = db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == current_user.id, Conversation.user2_id == receiver_id),
            and_(Conversation.user1_id == receiver_id, Conversation.user2_id == current_user.id)
        )
    ).first()

    if not conversation:
        conversation = Conversation(
            user1_id=min(current_user.id, receiver_id),
            user2_id=max(current_user.id, receiver_id)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Criar mensagem
    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        image_url=f"/uploads/{filename}",
        message_type="image"
    )
    db.add(message)

    # Atualizar timestamp da conversa
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    return message

# Notifications endpoints
@app.get("/notifications", response_model=List[NotificationSchema])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    notifications = db.query(Notification).filter(
        Notification.receiver_id == current_user.id
    ).order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

    return notifications

@app.get("/notifications/unread-count")
async def get_unread_notifications_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    count = db.query(Notification).filter(
        Notification.receiver_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {"unread_count": count}

@app.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.receiver_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()

    return {"message": "Notification marked as read"}

@app.post("/notifications/mark-all-read")
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    notifications = db.query(Notification).filter(
        Notification.receiver_id == current_user.id,
        Notification.is_read == False
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.commit()

    return {"message": f"Marked {len(notifications)} notifications as read"}

# Search endpoints
@app.get("/search/users", response_model=List[UserSchema])
async def search_users(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not q or len(q.strip()) < 2:
        return []

    search_term = f"%{q.strip()}%"

    users = db.query(User).filter(
        or_(
            User.username.ilike(search_term),
            User.full_name.ilike(search_term)
        ),
        User.id != current_user.id  # Excluir o próprio usuário
    ).limit(limit).all()

    return users

@app.get("/search/hashtags", response_model=List[HashtagSchema])
async def search_hashtags(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not q or len(q.strip()) < 1:
        return []

    search_term = f"%{q.strip().lower()}%"

    hashtags = db.query(Hashtag).filter(
        Hashtag.name.ilike(search_term)
    ).order_by(desc(Hashtag.posts_count)).limit(limit).all()

    return hashtags

@app.get("/hashtags/{hashtag_name}", response_model=HashtagSchema)
async def get_hashtag(
    hashtag_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag_name.lower()).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    return hashtag

@app.get("/hashtags/{hashtag_name}/posts", response_model=List[PostSchema])
async def get_hashtag_posts(
    hashtag_name: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag_name.lower()).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    posts = db.query(Post).join(Post.hashtags).filter(
        Hashtag.id == hashtag.id
    ).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()

    # Adicionar dados extras para cada post
    for post in posts:
        post.likes_count = len(post.likes)
        post.comments_count = len(post.comments)
        post.is_liked = any(like.user_id == current_user.id for like in post.likes)

    return posts

@app.get("/hashtags/trending", response_model=List[HashtagSchema])
async def get_trending_hashtags(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hashtags = db.query(Hashtag).filter(
        Hashtag.posts_count > 0
    ).order_by(desc(Hashtag.posts_count)).limit(limit).all()

    return hashtags

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
