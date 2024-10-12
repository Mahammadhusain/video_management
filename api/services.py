import os
import shutil
import aiofiles
import random
import string   
from fastapi import UploadFile, File, status
from sqlalchemy.orm import Session
from .models import Video, SessionLocal
from .schemas import VideoCreate
from fastapi import UploadFile, File, HTTPException
from .redis_service import cache_block_status, is_video_blocked
def generate_unique_string(length: int) -> str:
    characters = string.ascii_letters + string.digits  # Character set: a-z, A-Z, 0-9
    unique_string = ''.join(random.choices(characters, k=length))
    return unique_string

class VideoService:
    def __init__(self):
        self.db = SessionLocal()

    async def upload_video(self, file: UploadFile):
        unique_string = generate_unique_string(5)
        filename = f"{file.filename}{unique_string}"
        file_path = f"uploads/{filename}"

        # Save the video file asynchronously
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await file.read())

        # Simulate conversion to .mp4 (you should implement actual conversion logic)
        mp4_path = f"uploads/{filename}.mp4"
        os.rename(file_path, mp4_path)
        
        # Get the file size
        file_size = os.path.getsize(mp4_path)

        # Create a video record in the database
        video = Video(name=filename, size=file_size, path=mp4_path)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        cache_block_status(video.id, False)
        return video


    def search_videos(self, name: str = None, size: float = None):
        query = self.db.query(Video)
        if name:
            query = query.filter(Video.name.contains(name))
        if size:
            query = query.filter(Video.size == size)

        # For each result, cache the block status
        videos = query.all()
        for video in videos:
            cache_block_status(video.id, video.is_blocked)
        return videos

    
    def get_video_by_id(self, video_id: int):
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video with ID {video_id} not found."
            )
        return video
    
    def block_video(self, video_id: int):
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.is_blocked = 1
            self.db.commit()
            self.db.refresh(video)
            
            # Update Redis cache
            cache_block_status(video.id, True)
        return video

    def unblock_video(self, video_id: int):
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.is_blocked = 0
            self.db.commit()
            self.db.refresh(video)
            
            # Update Redis cache
            cache_block_status(video.id, False)
        return video