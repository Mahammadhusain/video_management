import pytest
from fastapi.testclient import TestClient
from api.main import app  # Adjust this import based on your project structure
from api.models import User
from api.dependencies import get_db
from api.schemas import UserCreate, UserLogin
from sqlalchemy.orm import Session
from api.models import SessionLocal  # Adjust this import based on your project structure
from api.auth import get_password_hash

# Create a test client
client = TestClient(app)

# Create a fixture for the database
@pytest.fixture(scope="function")
def test_db():
    db = SessionLocal()  # Create a new session for the test
    yield db
    db.rollback()  # Ensure session is rolled back between tests
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

# Test case for successful login
def test_login_success(test_db: Session):
    # First, ensure the test user exists with the correct password
    test_user = test_db.query(User).filter(User.username == "testuser").first()

    # If the user does not exist, handle this appropriately
    if not test_user:
        raise ValueError("Test user does not exist in the database")

    # Debugging: Check the user details
    print("User found:", test_user.username, test_user.email)

    # Prepare login data with correct username and password
    login_data = {
        "username": test_user.username,  # Use the retrieved user's username
        "password": "testpassword"                # The password you used when creating the user
    }

    # Make the login request
    response = client.post("/signin/", json=login_data)

    # Debugging: Print response details
    print("Login response:", response.status_code, response.json())

    # Assertions to verify successful login
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["username"] == test_user.username  # Assert using the actual username
    assert response.json()["email"] == test_user.email

# Test case for invalid login credentials
def test_login_invalid_credentials(test_db: Session):
    # First, ensure no duplicate users exist
    test_db.query(User).filter(User.username == "testuser").delete()
    test_db.commit()

    # Create a test user
    hashed_password = get_password_hash("testpassword")
    test_user = User(username="testuser", email="testuser@example.com", hashed_password=hashed_password)
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    # Prepare login data with an invalid password
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"  # Invalid password
    }

    # Make the login request
    response = client.post("/signin/", json=login_data)

    assert response.status_code == 401  # Unauthorized
    assert response.json()["detail"] == "Invalid credentials"

# Test case for non-existent user login
def test_login_non_existent_user(test_db: Session):
    # Clear the User table
    test_db.query(User).filter(User.username == "nonexistentuser").delete()
    test_db.commit()

    # Prepare login data for a non-existent user
    login_data = {
        "username": "nonexistentuser",
        "password": "somepassword"
    }

    # Make the login request
    response = client.post("/signin/", json=login_data)

    assert response.status_code == 401  # Unauthorized
    assert response.json()["detail"] == "Invalid credentials"
