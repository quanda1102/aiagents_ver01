import pytest
from fastapi.testclient import TestClient
from main import app
import uuid
from unittest.mock import patch, MagicMock

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(scope="module")
def admin_headers():
    """Fixture to create an ADMIN user and return their auth headers."""
    admin_id = str(uuid.uuid4())[:8]
    admin_payload = {
        "email": f"admin_{admin_id}@example.com",
        "password": "admin_password",
        "full_name": "Admin User",
        "role": "ADMIN"
    }
    # Register admin
    reg_response = client.post("/api/v1/auth/register", json=admin_payload)
    assert reg_response.status_code == 200
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": admin_payload["email"], "password": admin_payload["password"]})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def normal_user_payload():
    """Provides a sample payload for creating a new user."""
    user_id = str(uuid.uuid4())[:8]
    return {
        "email": f"new_user_{user_id}@example.com",
        "password": "user_password",
        "full_name": "New Regular User",
        "role": "STUDENT"
    }

# --- Mocked Service ---

@pytest.fixture
def mock_auth_service():
    """Mocks the AuthService for all tests in this module."""
    with patch('routes.user_routes.AuthService', autospec=True) as mock_service:
        yield mock_service

# --- Test Cases for User Management Routes (Admin Required) ---

def test_get_users_as_admin(mock_auth_service, admin_headers):
    """Tests that an admin can successfully retrieve a list of users."""
    mock_auth_service.get_users.return_value = [
        MagicMock(role='ADMIN', email='admin@example.com', full_name='Admin', age=30, class_name=[], gender='male'),
        MagicMock(role='STUDENT', email='student@example.com', full_name='Student', age=20, class_name=['A1'], gender='female')
    ]
    
    response = client.get("/api/v1/users/", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[1]["email"] == "student@example.com"
    mock_auth_service.get_users.assert_called_once()

def test_get_users_permission_denied():
    """Tests that a request without admin headers is denied."""
    # No headers provided
    response = client.get("/api/v1/users/")
    assert response.status_code == 401 # No auth at all

def test_create_user_as_admin(mock_auth_service, admin_headers, normal_user_payload):
    """Tests that an admin can create a new user."""
    mock_auth_service.create_user.return_value = MagicMock(role='STUDENT', **normal_user_payload)
    
    response = client.post("/api/v1/users/", json=normal_user_payload, headers=admin_headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == normal_user_payload["email"]
    mock_auth_service.create_user.assert_called_once()

def test_update_user_as_admin(mock_auth_service, admin_headers):
    """Tests that an admin can update an existing user."""
    user_id_to_update = 123
    update_payload = {"full_name": "Updated Name"}
    
    # Mock the return value of the update service
    mock_auth_service.update_user.return_value = MagicMock(
        id=user_id_to_update,
        full_name="Updated Name",
        email="user@example.com",
        role="STUDENT",
        age=21,
        class_name=["B2"],
        gender="other"
    )
    
    response = client.put(f"/api/v1/users/{user_id_to_update}", json=update_payload, headers=admin_headers)
    
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    mock_auth_service.update_user.assert_called_once()

def test_delete_user_as_admin(mock_auth_service, admin_headers):
    """Tests that an admin can delete a user."""
    user_id_to_delete = 456
    mock_auth_service.delete_user.return_value = {"message": "User deleted"}
    
    response = client.delete(f"/api/v1/users/{user_id_to_delete}", headers=admin_headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted"
    mock_auth_service.delete_user.assert_called_once_with(user_id_to_delete, unittest.mock.ANY)
