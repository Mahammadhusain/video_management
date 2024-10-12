# tests/unit_tests.py

import pytest
from fastapi.testclient import TestClient
from api.main import app  # Adjust this import based on your project structure
from api.models import User
from api.dependencies import get_db
from api.schemas import UserCreate
from sqlalchemy.orm import Session
from api.models import SessionLocal  # Adjust this import based on your project structure
from api.services import generate_unique_string
# Create a test client
client = TestClient(app)

# Create a fixture for the database
@pytest.fixture(scope="function")
def test_db():
    db = SessionLocal()  # Create a new session for the test
    yield db
    db.close()  # Close the session after the test

# Override the default get_db dependency to use the test database
def override_get_db():
    db = SessionLocal()  # Create a new session for the test
    try:
        yield db
    finally:
        db.close()  # Close the session after the test

# Set the dependency override
app.dependency_overrides[get_db] = override_get_db


def test_register_existing_user(test_db: Session):
    # First register a user
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "is_admin": False  # Add the is_admin field
    }
    
    client.post("/signup/", json=user_data)
    
    # Now attempt to register the same user again
    response = client.post("/signup/", json=user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "User already registered!"


def test_register_new_user(test_db: Session):
    user_data = {
        "username": f"testuser{generate_unique_string(5)}",
        "email": f"testuser{generate_unique_string(5)}@example.com",  # Use unique email
        "password": "testpassword",
        "is_admin": True  # Add the is_admin field for the new user
    }

    response = client.post("/signup/", json=user_data)
    print(response.status_code, response.json())  # Debugging
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]

    # Verify that the user is actually created in the database
    db_user = test_db.query(User).filter(User.email == user_data["email"]).first()
    assert db_user is not None
    assert db_user.username == user_data["username"]
    assert db_user.is_admin == user_data["is_admin"]  # Verify is_admin field


def test_register_missing_fields(test_db: Session):
    # Test for missing required fields
    user_data = {
        "username": "missing_fields_user",
        "is_admin": False  # Optional, but can be included
        # Missing email and password
    }

    response = client.post("/signup/", json=user_data)
    
    assert response.status_code == 422  # Unprocessable Entity for validation errors
    assert "detail" in response.json()
