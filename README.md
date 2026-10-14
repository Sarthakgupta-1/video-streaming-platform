# Video Streaming Platform

A beginner-friendly video upload and streaming web app built with **Python, Flask, SQLite, and FFmpeg**. Users can upload videos, browse a video library, play videos in the browser, and manage uploads from a dashboard.

## Features

- Responsive home page with uploaded video cards
- Video upload with title and description
- Browser video playback using the HTML5 video player and HTTP range support
- SQLite metadata storage
- Dashboard showing video count and total stored file size
- Delete uploaded videos
- Optional FFmpeg validation and thumbnail generation
- Health endpoint

**Storage note:** This starter stores video files on the local disk. AWS S3 is not configured by default, so the app runs locally without AWS credentials. An S3 adapter can be added for cloud deployment.

## Project structure

```text
video_streaming_platform/
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── uploads/
│   └── .gitkeep
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── watch.html
├── static/
│   ├── style.css
│   ├── script.js
│   └── thumbnails/
│       └── .gitkeep
└── tests/
    └── test_app.py
```

## Requirements

- Python 3.10+
- Optional but recommended: FFmpeg installed and available in PATH
- VS Code

## Run on Windows

1. Extract the ZIP and open the `video_streaming_platform` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use a Command Prompt terminal and run `.venv\Scripts\activate.bat`.

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Optional: install FFmpeg and ensure `ffmpeg -version` works in a new terminal. Without FFmpeg, uploads and playback still work, but thumbnail generation and video validation are skipped.
6. Run:

   ```bash
   python app.py
   ```

7. Open http://127.0.0.1:5000

The SQLite database (`videos.db`) and upload folders are created automatically.

## Upload and stream

- Open **Dashboard**.
- Enter a title, optional description, and select a video (`.mp4`, `.webm`, `.mov`, `.m4v`, `.ogv`).
- Upload, then use **Watch** to stream it in the browser.
- The browser can seek through supported media files because Flask serves the file with conditional/range support.

## AWS S3 (not enabled in this starter)

For a real cloud deployment, store video files in a private S3 bucket and serve them through short-lived presigned URLs or a CDN. Add `boto3`, configure AWS credentials through environment variables or an IAM role, and replace local file operations with S3 upload/delete operations. Never commit AWS access keys to GitHub.

## API / routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Browse videos |
| GET | `/dashboard` | Manage uploads and see storage summary |
| POST | `/upload` | Upload a video |
| GET | `/watch/<id>` | Play a video |
| GET | `/media/<filename>` | Serve video bytes |
| POST | `/delete/<id>` | Delete a video |
| GET | `/health` | Health check |

## Run tests

```bash
python -m pytest
```

## Push to GitHub

Create a new empty GitHub repository, then run these commands in the VS Code terminal:

```bash
git init
git add .
git commit -m "Build video streaming platform"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the example remote URL with your own. Uploaded video files and the SQLite database are excluded from Git by `.gitignore`; do not push private or copyrighted videos.

## Security before public deployment

This is a local/demo starter, not a production-ready public hosting service. It has no user login or video ownership controls. Add authentication, authorization, CSRF protection, upload quotas, rate limiting, and private media access before exposing it to the internet. Use a production server and HTTPS, and change `SECRET_KEY`.
