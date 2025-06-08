from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import shutil
import os
from typing import List
import uuid

from database import SessionLocal, engine, get_db
from models import Base, User, Post, Like, Comment, Story, StoryView
from schemas import UserCreate, UserLogin, Token, PostCreate, CommentCreate, User as UserSchema, Post as PostSchema, Comment as CommentSchema, UserProfile, StoryCreate, Story as StorySchema, StoryView as StoryViewSchema
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
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Salvar imagem
    file_extension = image.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Criar post
    db_post = Post(
        caption=caption,
        image_url=f"/uploads/{filename}",
        author_id=current_user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
