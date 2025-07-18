import pytest
from fastapi.testclient import TestClient
from main import app
import uuid
import io
from unittest.mock import patch, AsyncMock

# Import schemas for creating mock objects
from schemas.lecture import LectureContext, LectureStructure

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(scope="module")
def teacher_headers():
    """Fixture to create a TEACHER user and return their auth headers."""
    teacher_id = str(uuid.uuid4())[:8]
    teacher_payload = {
        "email": f"teacher_{teacher_id}@example.com",
        "password": "teacher_password",
        "full_name": "Lecturer",
        "role": "TEACHER"
    }
    # Register teacher
    reg_response = client.post("/api/v1/auth/register", json=teacher_payload)
    assert reg_response.status_code == 200
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": teacher_payload["email"], "password": teacher_payload["password"]})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- Mocked Services ---

@pytest.fixture
def mock_lecture_service():
    """Mocks the LectureService for all tests in this module."""
    with patch('routes.lecture_routes.LectureService', autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_router_agent():
    """Mocks the RouterAgent for the chat-lesson endpoint."""
    with patch('routes.lecture_routes.RouterAgent', autospec=True) as mock_agent:
        # We need to mock the instance and its method
        mock_instance = mock_agent.return_value
        mock_instance.route = AsyncMock(return_value={"response": "Chat response"})
        yield mock_instance

# --- Test Cases for Lecture Routes ---

def test_upload_lecture_success(mock_lecture_service, teacher_headers):
    """Tests successful file upload for a lecture."""
    mock_lecture_service.collect_context.return_value = LectureContext(
        objectives=["Objective 1"], skills=["Skill 1"], activities=["Activity 1"],
        equipment=["Laptop"], assessment=["Quiz"]
    )
    
    mock_file = io.BytesIO(b"This is the content of the lecture file.")
    
    response = client.post(
        "/api/v1/lectures/upload",
        files={"file": ("lecture.txt", mock_file, "text/plain")},
        data={"grade_level": "10", "subject": "Math"},
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    assert response.json()["objectives"] == ["Objective 1"]
    mock_lecture_service.collect_context.assert_awaited_once()

@patch('routes.lecture_routes.LectureService.save_lecture')
@patch('routes.lecture_routes.LectureService.write_content', new_callable=AsyncMock)
@patch('routes.lecture_routes.LectureService.structure_lecture', new_callable=AsyncMock)
@patch('routes.lecture_routes.LectureService.collect_context', new_callable=AsyncMock)
def test_create_lecture_success(mock_collect, mock_structure, mock_write, mock_save, teacher_headers):
    """Tests the full lecture creation flow with mocked services."""
    mock_collect.return_value = MagicMock()
    mock_structure.return_value = MagicMock()
    mock_write.return_value = MagicMock()
    mock_save.return_value = {"id": 1, "title": "New Lecture", "content": {}} # Simplified return

    create_payload = {"title": "New Lecture", "raw_content": "Some text.", "grade_level": "10", "subject": "History"}
    
    response = client.post("/api/v1/lectures/create", json=create_payload, headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_collect.assert_awaited_once()
    mock_structure.assert_awaited_once()
    mock_write.assert_awaited_once()
    mock_save.assert_called_once()

def test_edit_lecture_success(mock_lecture_service, teacher_headers):
    """Tests the lecture editing endpoint."""
    mock_lecture_service.edit_lecture.return_value = LectureStructure(
        title="Edited Title", objectives=[], knowledge_standards=[], activities={},
        questions=[], equipment=[], assessment=[]
    )
    
    edit_payload = {
        "structure": {"title": "Old Title", "objectives": [], "knowledge_standards": [], "activities": {}, "questions": [], "equipment": [], "assessment": []},
        "edit_request": "Change the title to 'Edited Title'"
    }
    
    # The endpoint expects structure and edit_request as separate JSON parts, which is unusual.
    # A common way to handle this is to send them as a single JSON body.
    # Assuming the endpoint logic can handle a combined payload.
    # If not, this test reveals a potential API design issue.
    # Let's try to match the function signature `edit_lecture(structure: LectureStructure, edit_request: str)`
    # This is not directly possible with a single JSON body. Let's assume the request body is a JSON that contains both.
    # A better API design would be a single Pydantic model for the request body.
    # For now, let's assume the client sends a JSON that FastAPI can map.
    # The test will likely fail if the endpoint isn't designed to handle this.
    # Let's try sending `edit_request` as a query parameter, a common pattern.
    
    request_body = {"title": "Old Title", "objectives": [], "knowledge_standards": [], "activities": {}, "questions": [], "equipment": [], "assessment": []}

    response = client.post(
        "/api/v1/lectures/edit",
        params={"edit_request": "Change the title"},
        json=request_body,
        headers=teacher_headers
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Edited Title"
    mock_lecture_service.edit_lecture.assert_awaited_once()

def test_chat_lesson_success(mock_router_agent, teacher_headers):
    """Tests the chat-lesson endpoint."""
    chat_payload = {"agent_name": "some_agent", "input": {"query": "hello"}}
    
    response = client.post("/api/v1/lectures/chat-lesson", json=chat_payload, headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json() == {"response": "Chat response"}
    mock_router_agent.route.assert_awaited_once()

@pytest.mark.parametrize("endpoint", [
    "/api/v1/lectures/upload",
    "/api/v1/lectures/create",
    "/api/v1/lectures/edit",
    "/api/v1/lectures/chat-lesson"
])
def test_lecture_routes_permission_denied(endpoint):
    """Tests that a user without teacher role cannot access lecture routes."""
    # Create a student user
    student_id = str(uuid.uuid4())[:8]
    student_payload = {"email": f"student_{student_id}@example.com", "password": "password", "role": "STUDENT"}
    client.post("/api/v1/auth/register", json=student_payload)
    login_res = client.post("/api/v1/auth/login", json={"email": student_payload["email"], "password": "password"})
    student_token = login_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    response = None
    if "upload" in endpoint:
        mock_file = io.BytesIO(b"content")
        response = client.post(endpoint, files={"file": ("f.txt", mock_file)}, data={"grade_level": "1", "subject": "s"}, headers=student_headers)
    elif "edit" in endpoint:
         response = client.post(endpoint, params={"edit_request": "test"}, json={}, headers=student_headers)
    else:
        response = client.post(endpoint, json={}, headers=student_headers)

    assert response.status_code == 403 # Forbidden
