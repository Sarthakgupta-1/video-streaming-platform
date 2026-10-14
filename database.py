import sqlite3
from pathlib import Path
from config import Config

def connect():
    connection = sqlite3.connect(Config.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    Path(Config.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL UNIQUE,
                thumbnail_filename TEXT,
                file_size INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

def create_video(**video):
    with connect() as db:
        cursor = db.execute("""
            INSERT INTO videos
            (title, description, original_filename, stored_filename, thumbnail_filename, file_size, created_at)
            VALUES (:title, :description, :original_filename, :stored_filename, :thumbnail_filename, :file_size, :created_at)
        """, video)
        return cursor.lastrowid

def list_videos(exclude_id=None, limit=100):
    sql = "SELECT * FROM videos"
    params = []
    if exclude_id is not None:
        sql += " WHERE id != ?"
        params.append(exclude_id)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with connect() as db:
        return [dict(row) for row in db.execute(sql, params).fetchall()]

def get_video(video_id):
    with connect() as db:
        row = db.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
        return dict(row) if row else None

def update_video(video_id, title, description):
    with connect() as db:
        db.execute("UPDATE videos SET title = ?, description = ? WHERE id = ?",
                   (title, description, video_id))

def delete_video(video_id):
    with connect() as db:
        db.execute("DELETE FROM videos WHERE id = ?", (video_id,))

def video_count():
    with connect() as db:
        return db.execute("SELECT COUNT(*) FROM videos").fetchone()[0]

def total_video_bytes():
    with connect() as db:
        return db.execute("SELECT COALESCE(SUM(file_size), 0) FROM videos").fetchone()[0]
