from fastapi import FastAPI,File, APIRouter, Depends, HTTPException, status
from .services import VideoService, UploadFile
from .dependencies import admin_only, get_db
from sqlalchemy.orm import Session
from .auth import create_access_token, verify_password, get_password_hash,ACCESS_TOKEN_EXPIRE_MINUTES
from .models import User
from .schemas import UserCreate, Token, UserLogin
from fastapi.responses import JSONResponse,FileResponse
from .redis_service import cache_block_status,is_video_blocked
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

# Doc Customization
app = FastAPI(
    title="Video management system",
    description="Fast api task",
    version="1.0.0",
    docs_url="/docs",        
    redoc_url="/redoc"       
)

video_service = VideoService()

# Create jwt access token using credentials (username and password)
@app.post('/token', response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Query the user from the database using the provided username (form_data.username)
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": str(user.id)}, expires_delta=token_expires)
    
    # Return the access token along with user details
    return {
        "username": user.username,  
        "email": user.email,        
        "access_token": token,     
        "token_type": "bearer"    
    }


# User signup
@app.post("/signup/", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered!"
        )
    
    # Hash the password before saving
    hashed_password = get_password_hash(user.password)
    
    # Create a new user instance, including the is_admin flag
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin  # Save the is_admin status
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create an access token for the new user
    token = create_access_token(data={"sub": db_user.id})
    
    return {
        "username": db_user.username,   
        "email": db_user.email,
        "is_admin": db_user.is_admin,   # Return the is_admin status
        "access_token": token,          
        "token_type": "bearer"          
    }



# User signin
@app.post("/signin/", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    token = create_access_token(data={"sub": db_user.id})
    return {
        "username": db_user.username,   
        "email": db_user.email,
        "access_token": token,          
        "token_type": "bearer"          
    }   

# Upload video
@app.post("/upload/", dependencies=[Depends(admin_only)])
async def upload_video(file: UploadFile = File(...)):
    video = await video_service.upload_video(file) 
    response = {
        "status": True,
        "data": {
            "size": video.size,               
            "name": video.name,               
            "is_blocked": video.is_blocked,  
            "path": video.path,               
            "id": video.id                    
        }
    }
    return JSONResponse(response)

# Search video using (size & name) query params
@app.get("/search/", dependencies=[Depends(admin_only)])
async def search_video(name: str = None, size: float = None):
    video = video_service.search_videos(name, size)
    response = {"status":True,"data":video}
    return response

# Block video by id
@app.post("/block/{video_id}/")
async def block_video(video_id: int):
    video = video_service.block_video(video_id)
    response = {"status":True,"data":video}
    return response


# Unblock video by id
@app.post("/unblock/{video_id}/")
async def unblock_video(video_id: int):
    video = video_service.unblock_video(video_id)
    response = {"status":True,"data":video}
    return response


# Download video by ID
@app.get("/download/{video_id}/")
async def download_video(video_id: int):
    # Check if the video is blocked from Redis cache
    if is_video_blocked(video_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This video is blocked and cannot be downloaded."
        )
    
    # Get the video details from the database
    video = video_service.get_video_by_id(video_id)
    
    # Return the video file if it's not blocked
    return FileResponse(video.path)