import pytest
from fastapi.testclient import TestClient
from main import app
import uuid
import datetime
from unittest.mock import patch, MagicMock

client = TestClient(app)

# --- Reusable Fixtures ---

@pytest.fixture(scope="module")
def auth_headers_for_role():
    """A factory fixture to create users and headers for different roles."""
    created_users = {}

    def _get_headers(role: str = "STUDENT"):
        role = role.upper()
        if role in created_users:
            return created_users[role]

        random_id = str(uuid.uuid4())[:8]
        payload = {
            "email": f"test_quiz_{random_id}@{role.lower()}.com",
            "password": "password123",
            "full_name": f"Test {role}",
            "role": role
        }
        
        # Register
        reg_response = client.post("/api/v1/auth/register", json=payload)
        assert reg_response.status_code == 200
        
        # Login
        login_response = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        created_users[role] = headers
        return headers

    return _get_headers

# --- Mocked Service ---

@pytest.fixture
def mock_quiz_service():
    """Mocks the MySQLQuizService for all tests in this module."""
    with patch('routes.quiz_routes.quiz_service', autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_quiz_agent():
    """Mocks the QuizGenerationAgent for all tests in this module."""
    with patch('routes.quiz_routes.quiz_generation_agent', autospec=True) as mock_agent:
        yield mock_agent

# --- Test Cases ---

def test_health_check():
    """Tests the health check endpoint."""
    response = client.get("/api/v1/quiz/health")
    # This might fail if DB isn't actually running, but we test the endpoint exists.
    # A better health check would mock the service call.
    assert response.status_code in [200, 503]

def test_create_quiz_by_teacher(mock_quiz_service, auth_headers_for_role):
    """A teacher should be able to create a quiz."""
    teacher_headers = auth_headers_for_role("TEACHER")
    mock_quiz_service.create_quiz.return_value = "new_quiz_id"
    mock_quiz_service.get_quiz.return_value = {
        "quiz_id": "new_quiz_id", "title": "New Quiz", "created_at": datetime.datetime.now(),
        "created_by": "teacher@example.com", "questions": []
    }
    
    quiz_payload = {"title": "New Quiz", "questions": []}
    response = client.post("/api/v1/quiz/create", json=quiz_payload, headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["data"]["quiz_id"] == "new_quiz_id"
    mock_quiz_service.create_quiz.assert_called_once()

def test_list_quizzes(mock_quiz_service, auth_headers_for_role):
    """Any authenticated user should be able to list quizzes."""
    student_headers = auth_headers_for_role("STUDENT")
    mock_quiz_service.list_quizzes.return_value = [{"quiz_id": "quiz1", "title": "Math Quiz", "created_at": datetime.datetime.now(), "created_by": "test", "questions": []}]
    
    response = client.get("/api/v1/quiz/list", headers=student_headers)
    
    assert response.status_code == 200
    assert len(response.json()["quizzes"]) == 1

def test_submit_quiz(mock_quiz_service, auth_headers_for_role):
    """A student should be able to submit a quiz."""
    student_headers = auth_headers_for_role("STUDENT")
    mock_quiz_service.submit_quiz_attempt.return_value = {"attempt_id": "attempt1", "score": 90}
    
    submit_payload = {"quiz_id": "quiz1", "user_id": "user1", "answers": []}
    response = client.post("/api/v1/quiz/submit", json=submit_payload, headers=student_headers)
    
    assert response.status_code == 200
    assert response.json()["data"]["attempt_id"] == "attempt1"

def test_get_quiz_attempt(mock_quiz_service, auth_headers_for_role):
    """An authenticated user should be able to retrieve an attempt."""
    student_headers = auth_headers_for_role("STUDENT")
    mock_quiz_service.get_quiz_attempt.return_value = {"attempt_id": "attempt1", "score": 90}
    
    response = client.get("/api/v1/quiz/attempt/attempt1", headers=student_headers)
    
    assert response.status_code == 200
    assert response.json()["data"]["attempt_id"] == "attempt1"

def test_generate_quiz_by_teacher(mock_quiz_agent, mock_quiz_service, auth_headers_for_role):
    """A teacher should be able to generate a quiz using the AI agent."""
    teacher_headers = auth_headers_for_role("TEACHER")
    mock_quiz_agent.process.return_value = {"quiz_id": "generated_quiz_1"}
    mock_quiz_service.get_quiz.return_value = {
        "quiz_id": "generated_quiz_1", "title": "Generated Quiz", "created_at": datetime.datetime.now(),
        "created_by": "teacher@example.com", "questions": []
    }

    generate_payload = {"document_text": "Some text to make a quiz from.", "quiz_title": "Generated Quiz"}
    response = client.post("/api/v1/quiz/generate", json=generate_payload, headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["quiz_id"] == "generated_quiz_1"
    mock_quiz_agent.process.assert_awaited_once()

def test_assign_quiz_by_teacher(mock_quiz_service, auth_headers_for_role):
    """A teacher should be able to assign a quiz to a class."""
    teacher_headers = auth_headers_for_role("TEACHER")
    mock_quiz_service.assign_quiz_to_class.return_value = True
    
    response = client.post("/api/v1/quiz/assign/quiz1/classA", headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_quiz_service.assign_quiz_to_class.assert_called_once_with("quiz1", "classA")

def test_assign_quiz_permission_denied(mock_quiz_service, auth_headers_for_role):
    """A student should not be able to assign a quiz."""
    student_headers = auth_headers_for_role("STUDENT")
    
    response = client.post("/api/v1/quiz/assign/quiz1/classA", headers=student_headers)
    
    assert response.status_code == 403 # Forbidden
    mock_quiz_service.assign_quiz_to_class.assert_not_called()

def test_get_all_attempts_by_teacher(mock_quiz_service, auth_headers_for_role):
    """A teacher should be able to get all attempts."""
    teacher_headers = auth_headers_for_role("TEACHER")
    mock_quiz_service.get_all_attempts_with_student_info.return_value = [{"attempt_id": "atm1"}]
    
    response = client.get("/api/v1/quiz/all-attempts", headers=teacher_headers)
    
    assert response.status_code == 200
    assert len(response.json()["data"]["recent_attempts"]) == 1

def test_get_all_attempts_permission_denied(mock_quiz_service, auth_headers_for_role):
    """A student should not be able to get all attempts."""
    student_headers = auth_headers_for_role("STUDENT")
    
    response = client.get("/api/v1/quiz/all-attempts", headers=student_headers)
    
    assert response.status_code == 403 # Forbidden
    mock_quiz_service.get_all_attempts_with_student_info.assert_not_called()

def test_delete_quiz_by_teacher(mock_quiz_service, auth_headers_for_role):
    """A teacher should be able to delete a quiz."""
    teacher_headers = auth_headers_for_role("TEACHER")
    mock_quiz_service.delete_quiz.return_value = True
    
    response = client.delete("/api/v1/quiz/quiz1", headers=teacher_headers)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_quiz_service.delete_quiz.assert_called_once_with("quiz1")
