import io
import os
import tempfile
import pytest

@pytest.fixture()
def client(monkeypatch):
    temp_dir = tempfile.TemporaryDirectory()
    monkeypatch.setenv("DATABASE_PATH", os.path.join(temp_dir.name, "test.db"))
    monkeypatch.setenv("UPLOAD_FOLDER", os.path.join(temp_dir.name, "uploads"))
    monkeypatch.setenv("THUMBNAIL_FOLDER", os.path.join(temp_dir.name, "thumbs"))

    # Reload config-dependent modules so tests use isolated temporary paths.
    import config
    config.Config.DATABASE_PATH = os.environ["DATABASE_PATH"]
    config.Config.UPLOAD_FOLDER = os.environ["UPLOAD_FOLDER"]
    config.Config.THUMBNAIL_FOLDER = os.environ["THUMBNAIL_FOLDER"]
    import database
    database.Config.DATABASE_PATH = config.Config.DATABASE_PATH
    import app as app_module
    app_module.app.config["DATABASE_PATH"] = config.Config.DATABASE_PATH
    app_module.app.config["UPLOAD_FOLDER"] = config.Config.UPLOAD_FOLDER
    app_module.app.config["THUMBNAIL_FOLDER"] = config.Config.THUMBNAIL_FOLDER
    os.makedirs(config.Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.Config.THUMBNAIL_FOLDER, exist_ok=True)
    database.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client
    temp_dir.cleanup()

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"FrameFlow" in response.data

def test_dashboard_page(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Your dashboard" in response.data

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_upload_rejects_wrong_extension(client):
    response = client.post("/upload", data={
        "title": "Not a video",
        "video": (io.BytesIO(b"plain text"), "hello.txt"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Unsupported file type" in response.data
