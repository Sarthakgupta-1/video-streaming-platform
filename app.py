import os
import uuid
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from database import init_db, create_video, list_videos, get_video, update_video, delete_video, video_count, total_video_bytes

app = Flask(__name__)
app.config.from_object(Config)
Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
Path(app.config["THUMBNAIL_FOLDER"]).mkdir(parents=True, exist_ok=True)
init_db()

ALLOWED_EXTENSIONS = {"mp4", "webm", "mov", "m4v", "ogv"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def make_thumbnail(video_path, thumbnail_path):
    """Create a thumbnail with FFmpeg if it is installed; otherwise skip gracefully."""
    ffmpeg = app.config["FFMPEG_BINARY"]
    try:
        subprocess.run(
            [ffmpeg, "-y", "-ss", "00:00:01", "-i", str(video_path),
             "-frames:v", "1", "-vf", "scale=480:-1", str(thumbnail_path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

@app.get("/")
def index():
    videos = list_videos()
    return render_template("index.html", videos=videos)

@app.get("/dashboard")
def dashboard():
    videos = list_videos()
    return render_template(
        "dashboard.html",
        videos=videos,
        video_count=video_count(),
        total_bytes=total_video_bytes(),
        ffmpeg_available=ffmpeg_available(),
    )

def ffmpeg_available():
    try:
        subprocess.run([app.config["FFMPEG_BINARY"], "-version"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

@app.post("/upload")
def upload():
    uploaded = request.files.get("video")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        flash("Please enter a video title.", "error")
        return redirect(url_for("dashboard"))
    if len(title) > 120 or len(description) > 2000:
        flash("Title must be at most 120 characters and description at most 2000 characters.", "error")
        return redirect(url_for("dashboard"))
    if not uploaded or not uploaded.filename:
        flash("Please choose a video file.", "error")
        return redirect(url_for("dashboard"))
    if not allowed_file(uploaded.filename):
        flash("Unsupported file type. Use MP4, WebM, MOV, M4V, or OGV.", "error")
        return redirect(url_for("dashboard"))

    original_name = secure_filename(uploaded.filename)
    suffix = Path(original_name).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    destination = Path(app.config["UPLOAD_FOLDER"]) / stored_name
    uploaded.save(destination)

    # Basic post-upload validation. FFmpeg checks the file when available.
    if ffmpeg_available():
        try:
            subprocess.run(
                [app.config["FFMPEG_BINARY"], "-v", "error", "-i", str(destination), "-f", "null", "-"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            destination.unlink(missing_ok=True)
            flash("The uploaded file could not be read as a valid video.", "error")
            return redirect(url_for("dashboard"))

    thumbnail_name = f"{Path(stored_name).stem}.jpg"
    thumbnail_path = Path(app.config["THUMBNAIL_FOLDER"]) / thumbnail_name
    has_thumbnail = make_thumbnail(destination, thumbnail_path)

    try:
        video_id = create_video(
            title=title, description=description, original_filename=original_name,
            stored_filename=stored_name, thumbnail_filename=thumbnail_name if has_thumbnail else None,
            file_size=destination.stat().st_size,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds")
        )
    except Exception:
        destination.unlink(missing_ok=True)
        thumbnail_path.unlink(missing_ok=True)
        raise

    flash("Video uploaded successfully!", "success")
    return redirect(url_for("watch", video_id=video_id))

@app.get("/watch/<int:video_id>")
def watch(video_id):
    video = get_video(video_id)
    if not video:
        abort(404)
    return render_template("watch.html", video=video, related=list_videos(exclude_id=video_id, limit=4))

@app.get("/media/<path:filename>")
def media(filename):
    # Files are stored under the configured upload folder; no user-controlled path is accepted.
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, conditional=True)

@app.get("/thumbnails/<path:filename>")
def thumbnail(filename):
    return send_from_directory(app.config["THUMBNAIL_FOLDER"], filename)

@app.post("/delete/<int:video_id>")
def delete(video_id):
    video = get_video(video_id)
    if not video:
        abort(404)
    # Demo has no authentication: only run locally, or add login/ownership checks before deployment.
    (Path(app.config["UPLOAD_FOLDER"]) / video["stored_filename"]).unlink(missing_ok=True)
    if video["thumbnail_filename"]:
        (Path(app.config["THUMBNAIL_FOLDER"]) / video["thumbnail_filename"]).unlink(missing_ok=True)
    delete_video(video_id)
    flash("Video deleted.", "success")
    return redirect(url_for("dashboard"))

@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    flash("File is too large. The maximum upload size is configured in the app.", "error")
    return redirect(url_for("dashboard"))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Local development only. Use a production WSGI server for deployment.
    app.run(debug=True)
