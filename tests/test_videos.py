import pytest
from fastapi.testclient import TestClient
from api.main import app  # Assuming the app is imported from api.main
from api.models import SessionLocal
from api.dependencies import get_db
from sqlalchemy.orm import Session
from fastapi import UploadFile
from io import BytesIO

# Create a test client
client = TestClient(app)

# Test fixture for database session
@pytest.fixture(scope="function")
def test_db():
    db = SessionLocal()  # Replace with test database session
    yield db
    db.close()

# Dependency override for testing purposes
def override_get_db():
    db = SessionLocal()  # Replace with test database session
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_upload_video():
    # Step 1: Simulate an admin login to get the access token
    admin_credentials = {
        "username": "admin",
        "password": "admin"
    }
    
    # Assuming you have an endpoint for login
    response = client.post("/signin/", json=admin_credentials)
    assert response.status_code == 200
    token = response.json()["access_token"]

    print(token,"GGGGGGGGG")

    # Step 2: Use the token in the upload request
    file_data = BytesIO(b"Test video content")
    file = UploadFile(filename="test_video.wmv", file=file_data)
    
    headers = {
        "Authorization": f"Bearer {token}"  # Set the token in the Authorization header
    }

    # Step 3: Make the upload request with the authorization header
    response = client.post("/upload/", files={"file": (file.filename, file.file, "video/mp4")}, headers=headers)
    
    print(response.text, "TTTTTTTTTTTTTTT")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] is True
    assert "size" in json_response["data"]
    assert "name" in json_response["data"]
    assert "is_blocked" in json_response["data"]
    assert "path" in json_response["data"]
    assert "id" in json_response["data"]

# Test search video
def test_search_video():
    
    admin_credentials = {
        "username": "admin",
        "password": "admin"
    }
    
    # Assuming you have an endpoint for login
    response = client.post("/signin/", json=admin_credentials)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}" 
    }
    # Search by name
    response = client.get("/search/", params={"name": "test_video"}, headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] is True
    assert isinstance(json_response["data"], list)

# Test block video
def test_block_video():
    video_id = 1  # Assuming this video exists in the test database
    response = client.post(f"/block/{video_id}/")
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] is True
    assert "data" in json_response

# Test download video
def test_download_video():
    video_id = 1  # Assuming this video exists in the test database and is not blocked
    response = client.get(f"/download/{video_id}/")
    
    if response.status_code == 403:
        assert response.json()["detail"] == "This video is blocked and cannot be downloaded."
    else:
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
