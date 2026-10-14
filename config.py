import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-before-deployment")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "500")) * 1024 * 1024
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    THUMBNAIL_FOLDER = os.getenv("THUMBNAIL_FOLDER", str(BASE_DIR / "static" / "thumbnails"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "videos.db"))
    FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg")
