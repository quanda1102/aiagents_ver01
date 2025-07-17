import pytest
from fastapi.testclient import TestClient
from main import app
import io
from unittest.mock import patch, AsyncMock

client = TestClient(app)

# --- Helper Functions to Create Mock Files ---

def create_mock_image_bytes() -> io.BytesIO:
    """Creates a dummy image file in memory."""
    # Using a simple text file to simulate an image upload for API contract testing
    return io.BytesIO(b"fake_image_content")

def create_mock_pdf_bytes() -> io.BytesIO:
    """Creates a dummy PDF file in memory."""
    return io.BytesIO(b"fake_pdf_content")

# --- Mocked Service Fixture ---

@pytest.fixture
def mock_ocr_service():
    """Mocks all functions in the ocr_gpt_service module."""
    # We patch the entire module as it's imported in the router file
    with patch('routes.ocr_gpt_routes.ocr', autospec=True) as mock_service:
        # Set up async mock return values for all functions
        mock_service.ocr_image_with_gpt = AsyncMock(return_value="Extracted text from image.")
        mock_service.ocr_pdf_with_gpt = AsyncMock(return_value=["Page 1 text."])
        mock_service.ocr_pdf_with_gpt_batch = AsyncMock(return_value=["Page 1 batch text."])
        mock_service.ocr_pdf_with_structured_output = AsyncMock(return_value={"filename": "test.pdf", "pages": []})
        
        mock_service.ocr_pdf_with_pymupdf = AsyncMock(return_value=["PyMuPDF text."])
        mock_service.ocr_pdf_with_pymupdf_batch = AsyncMock(return_value=["PyMuPDF batch text."])
        mock_service.ocr_pdf_with_pymupdf_structured = AsyncMock(return_value={"filename": "test.pdf", "pages": [], "method": "PyMuPDF"})

        mock_service.ocr_pdf_with_pypdfium2 = AsyncMock(return_value=["pypdfium2 text."])
        mock_service.ocr_pdf_with_pypdfium2_batch = AsyncMock(return_value=["pypdfium2 batch text."])
        mock_service.ocr_pdf_with_pypdfium2_structured = AsyncMock(return_value={"filename": "test.pdf", "pages": [], "method": "pypdfium2"})
        
        yield mock_service

# --- Test Cases ---

def test_ocr_images(mock_ocr_service):
    """Tests the /images endpoint."""
    mock_file = create_mock_image_bytes()
    files = {'files': ('test_image.jpg', mock_file, 'image/jpeg')}
    
    response = client.post("/api/v1/ocr-ai/images", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "test_image.jpg"
    assert data[0]["text"] == "Extracted text from image."
    mock_ocr_service.ocr_image_with_gpt.assert_awaited_once()

def test_ocr_images_batch(mock_ocr_service):
    """Tests the /images-batch endpoint."""
    # For batch, we need to mock the service differently as it's called inside a loop
    mock_ocr_service.ocr_image_with_gpt.return_value = "Batch processed text."
    
    mock_file1 = create_mock_image_bytes()
    mock_file2 = create_mock_image_bytes()
    files = [
        ('files', ('image1.jpg', mock_file1, 'image/jpeg')),
        ('files', ('image2.jpg', mock_file2, 'image/jpeg'))
    ]
    
    response = client.post("/api/v1/ocr-ai/images-batch", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["filename"] == "image1.jpg"
    assert data[1]["text"] == "Batch processed text."
    assert mock_ocr_service.ocr_image_with_gpt.await_count == 2

@pytest.mark.parametrize("endpoint, mock_function_name", [
    ("/api/v1/ocr-ai/pdf", "ocr_pdf_with_gpt"),
    ("/api/v1/ocr-ai/pdf-batch", "ocr_pdf_with_gpt_batch"),
    ("/api/v1/ocr-ai/pdf-pymupdf", "ocr_pdf_with_pymupdf"),
    ("/api/v1/ocr-ai/pdf-pymupdf-batch", "ocr_pdf_with_pymupdf_batch"),
    ("/api/v1/ocr-ai/pdf-pypdfium2", "ocr_pdf_with_pypdfium2"),
    ("/api/v1/ocr-ai/pdf-pypdfium2-batch", "ocr_pdf_with_pypdfium2_batch"),
])
def test_pdf_ocr_endpoints(mock_ocr_service, endpoint, mock_function_name):
    """Tests various single-file PDF OCR endpoints."""
    mock_file = create_mock_pdf_bytes()
    files = {'file': ('test.pdf', mock_file, 'application/pdf')}
    
    response = client.post(endpoint, files=files)
    
    assert response.status_code == 200
    # The mocked function for this endpoint should have been called
    mocked_function = getattr(mock_ocr_service, mock_function_name)
    mocked_function.assert_awaited_once()
    # Check if the response contains part of the mocked return value
    assert "text" in response.text

@pytest.mark.parametrize("endpoint, mock_function_name", [
    ("/api/v1/ocr-ai/pdf-structured", "ocr_pdf_with_structured_output"),
    ("/api/v1/ocr-ai/pdf-pymupdf-structured", "ocr_pdf_with_pymupdf_structured"),
    ("/api/v1/ocr-ai/pdf-pypdfium2-structured", "ocr_pdf_with_pypdfium2_structured"),
])
def test_pdf_structured_ocr_endpoints(mock_ocr_service, endpoint, mock_function_name):
    """Tests various structured PDF OCR endpoints."""
    mock_file = create_mock_pdf_bytes()
    files = {'file': ('test_structured.pdf', mock_file, 'application/pdf')}
    
    response = client.post(endpoint, files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_structured.pdf"
    assert "pages" in data
    mocked_function = getattr(mock_ocr_service, mock_function_name)
    mocked_function.assert_awaited_once()
