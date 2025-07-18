import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

# --- Helper Functions & Fixtures ---

def get_unique_user_payload(role: str = "STUDENT"):
    """Generates a unique user payload for registration."""
    random_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{random_id}@example.com",
        "password": "strong_password_123",
        "full_name": f"Test User {random_id}",
        "age": 25,
        "role": role.upper(),
        "class_name": [f"CLASS_{random_id}"],
        "gender": "male"
    }

@pytest.fixture(scope="module")
def registered_user():
    """Fixture to register a new user and provide their credentials for tests."""
    payload = get_unique_user_payload()
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200, "Setup failed: Could not register user for tests."
    return payload # Return the original payload for login tests

@pytest.fixture(scope="module")
def auth_headers(registered_user):
    """Fixture to log in a user and return the authorization headers."""
    login_payload = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200, "Setup failed: Could not log in to get auth token."
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Test Cases for Auth Routes ---

def test_register_user_success():
    """Tests successful user registration."""
    payload = get_unique_user_payload()
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_user_duplicate_email(registered_user):
    """Tests that registering with a duplicate email fails."""
    # The `registered_user` fixture has already created this user.
    # Attempting to register again with the same email should fail.
    payload = {**registered_user, "password": "another_password"} # Use same email
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400 # Assuming 400 for duplicate entry
    assert "already registered" in response.json()["detail"]

def test_login_success(registered_user):
    """Tests successful user login with correct credentials."""
    payload = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(registered_user):
    """Tests that login fails with an incorrect password."""
    payload = {
        "email": registered_user["email"],
        "password": "wrong_password"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401 # Unauthorized
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_me_success(auth_headers, registered_user):
    """Tests fetching the current user's data with valid authentication."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == registered_user["email"]
    assert data["role"] == registered_user["role"]

def test_get_me_unauthenticated():
    """Tests that fetching user data fails without authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401 # Unauthorized

def test_update_class_name_success(auth_headers):
    """Tests successfully updating the user's class name list."""
    new_class_names = ["CLASS_A", "CLASS_B"]
    payload = {"class_name": new_class_names}
    
    response = client.put("/api/v1/auth/me/class-name", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Class names updated successfully"
    
    # Verify the change
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["class_name"] == new_class_names

def test_update_class_name_invalid_payload(auth_headers):
    """Tests that updating with an invalid payload fails."""
    # Payload should be a dict with a list, not just a list.
    invalid_payload = ["CLASS_C"]
    response = client.put("/api/v1/auth/me/class-name", json=invalid_payload, headers=auth_headers)
    assert response.status_code == 422 # Unprocessable Entity
