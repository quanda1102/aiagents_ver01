import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(scope="module")
def authenticated_user_headers():
    """
    Fixture to register and log in a user, then return auth headers.
    This ensures tests have a valid, authenticated user context.
    """
    random_id = str(uuid.uuid4())[:8]
    user_payload = {
        "email": f"test_chat_{random_id}@example.com",
        "password": "password123",
        "full_name": "Chat User",
        "role": "STUDENT"
    }
    
    # Register the user
    register_response = client.post("/api/v1/auth/register", json=user_payload)
    assert register_response.status_code == 200, "Failed to register user for chat test."
    
    # Log in to get the token
    login_response = client.post("/api/v1/auth/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    assert login_response.status_code == 200, "Failed to log in user for chat test."
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Return headers and the original email for verification
    return headers, user_payload["email"]

# --- Test Cases for Chat Route ---

def test_chat_response_success(authenticated_user_headers):
    """
    Tests that an authenticated user receives a successful chat response.
    """
    headers, user_email = authenticated_user_headers
    
    chat_payload = {
        "message": "Hello, can you help me?",
        "session_id": str(uuid.uuid4())
    }
    
    response = client.post("/api/v1/chat", json=chat_payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response content
    assert "response" in data
    assert "session_id" in data
    assert f"Hello {user_email}" in data["response"]
    assert data["session_id"] == chat_payload["session_id"]

def test_chat_response_unauthenticated():
    """
    Tests that an unauthenticated request to the chat endpoint fails.
    """
    chat_payload = {
        "message": "I have no token.",
        "session_id": str(uuid.uuid4())
    }
    
    response = client.post("/api/v1/chat", json=chat_payload)
    
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "Not authenticated"

def test_chat_response_missing_message():
    """
    Tests that the request fails if the 'message' field is missing.
    """
    headers, _ = authenticated_user_headers
    
    # Payload is missing the required 'message' field
    invalid_payload = {
        "session_id": str(uuid.uuid4())
    }
    
    response = client.post("/api/v1/chat", json=invalid_payload, headers=headers)
    
    # Expect a 422 Unprocessable Entity error for validation failure
    assert response.status_code == 422
