import pytest
from fastapi.testclient import TestClient
from main import app
import uuid
from unittest.mock import patch, AsyncMock

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(scope="module")
def teacher_headers():
    """Fixture to create a TEACHER user and return their auth headers."""
    teacher_id = str(uuid.uuid4())[:8]
    teacher_payload = {
        "email": f"teacher_exam_{teacher_id}@example.com",
        "password": "teacher_password",
        "full_name": "Exam Creator",
        "role": "TEACHER"
    }
    reg_response = client.post("/api/v1/auth/register", json=teacher_payload)
    assert reg_response.status_code == 200
    
    login_response = client.post("/api/v1/auth/login", json={"email": teacher_payload["email"], "password": teacher_payload["password"]})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_agent_controller():
    """Mocks the UnifiedAgentController for all tests in this module."""
    # The actual path to the controller instance used by the router
    with patch('my_agents.exam_agents.unified_routes.controller', autospec=True) as mock_controller:
        # Mock the async methods
        mock_controller.chat = AsyncMock()
        mock_controller.get_session_status = AsyncMock()
        mock_controller.get_session_context = AsyncMock()
        mock_controller.delete_session = AsyncMock()
        mock_controller.export_exam = AsyncMock()
        
        # Mock the sync methods
        mock_controller.get_workflow_info.return_value = {"info": "Workflow details"}
        mock_controller.get_agents_status.return_value = {"status": "All agents operational"}
        mock_controller.health_check.return_value = {"status": "Healthy"}
        
        yield mock_controller

# --- Test Cases for Unified Exam Agents ---

def test_chat_with_agent_new_session(mock_agent_controller, teacher_headers):
    """Tests the main chat endpoint when no session_id is provided."""
    mock_agent_controller.chat.return_value = {"response": "Hello from the agent!", "agent_name": "triage", "session_id": "new_session_123"}
    
    chat_payload = {"message": "Start a new exam"}
    response = client.post("/api/v1/exam/chat", json=chat_payload, headers=teacher_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "triage"
    assert data["session_id"] == "new_session_123"
    mock_agent_controller.chat.assert_awaited_once()

def test_chat_with_agent_existing_session(mock_agent_controller, teacher_headers):
    """Tests the main chat endpoint with an existing session_id."""
    mock_agent_controller.chat.return_value = {"response": "Continuing conversation", "agent_name": "questions", "session_id": "existing_session_456"}

    chat_payload = {"message": "Add a question", "session_id": "existing_session_456"}
    response = client.post("/api/v1/exam/chat", json=chat_payload, headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["agent_name"] == "questions"
    # Ensure the correct session_id was passed to the controller
    mock_agent_controller.chat.assert_awaited_once_with(
        message="Add a question",
        session_id="existing_session_456"
    )

def test_get_session_status(mock_agent_controller, teacher_headers):
    """Tests retrieving the status of a session."""
    session_id = "test_session_1"
    mock_agent_controller.get_session_status.return_value = {"session_id": session_id, "status": "In progress"}
    
    response = client.get(f"/api/v1/exam/session/{session_id}/status", headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "In progress"
    mock_agent_controller.get_session_status.assert_awaited_once_with(session_id)

def test_delete_session(mock_agent_controller, teacher_headers):
    """Tests deleting a session."""
    session_id = "test_session_to_delete"
    mock_agent_controller.delete_session.return_value = {"message": "Session deleted"}
    
    response = client.delete(f"/api/v1/exam/session/{session_id}", headers=teacher_headers)
    
    assert response.status_code == 200
    assert "Session deleted" in response.json()["message"]
    mock_agent_controller.delete_session.assert_awaited_once_with(session_id)

def test_export_exam(mock_agent_controller, teacher_headers):
    """Tests exporting the exam as a file."""
    session_id = "test_session_to_export"
    # Mock the controller to return a StreamingResponse
    from fastapi.responses import StreamingResponse
    import io
    mock_response_content = io.BytesIO(b"Exam content")
    mock_agent_controller.export_exam.return_value = StreamingResponse(mock_response_content, media_type="application/json")

    response = client.get(f"/api/v1/exam/session/{session_id}/export", headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.content == b"Exam content"
    mock_agent_controller.export_exam.assert_awaited_once_with(session_id)

def test_get_workflow_info(mock_agent_controller, teacher_headers):
    """Tests the workflow info endpoint."""
    response = client.get("/api/v1/exam/workflow/info", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json() == {"info": "Workflow details"}
    mock_agent_controller.get_workflow_info.assert_called_once()

def test_health_check(mock_agent_controller, teacher_headers):
    """Tests the health check endpoint."""
    response = client.get("/api/v1/exam/health", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json() == {"status": "Healthy"}
    mock_agent_controller.health_check.assert_called_once()

def test_chat_unauthenticated():
    """Tests that an unauthenticated request to a protected endpoint fails."""
    response = client.post("/api/v1/exam/chat", json={"message": "test"})
    assert response.status_code == 401 # Unauthorized
