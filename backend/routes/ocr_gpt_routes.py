from fastapi import APIRouter, UploadFile, File
from typing import List
from config import config
from services import ocr_gpt_service as ocr
import asyncio

from openai import OpenAI
client = OpenAI(api_key=config.OPENAI_API_KEY)

router = APIRouter(prefix="/api/v1/ocr-ai", tags=["ocr-ai"])


@router.post("/images", response_model=List[dict])
async def ocr_images_with_gpt(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            # Use the optimized OCR function
            text = await ocr.ocr_image_with_gpt(file)
            results.append({"filename": file.filename, "text": text})

        except Exception as e:
            results.append({"filename": file.filename, "text": f"Error: {str(e)}"})

    return results


@router.post("/images-batch", response_model=List[dict])
async def ocr_images_batch(files: List[UploadFile] = File(...)):
    """
    Batch processing for multiple images with concurrent processing
    """
    async def process_image(file: UploadFile) -> dict:
        try:
            text = await ocr.ocr_image_with_gpt(file)
            return {"filename": file.filename, "text": text}
        except Exception as e:
            return {"filename": file.filename, "text": f"Error: {str(e)}"}

    # Process up to 5 images concurrently
    semaphore = asyncio.Semaphore(5)
    
    async def process_with_semaphore(file: UploadFile) -> dict:
        async with semaphore:
            return await process_image(file)
    
    # Process all images concurrently
    tasks = [process_with_semaphore(file) for file in files]
    results = await asyncio.gather(*tasks)
    
    return results


@router.post("/pdf", response_model=dict)
async def ocr_pdf(file: UploadFile = File(...)):
    pages = await ocr.ocr_pdf_with_gpt(file)
    return {"filename": file.filename, "pages": pages}


@router.post("/pdf-batch", response_model=dict)
async def ocr_pdf_batch(file: UploadFile = File(...)):
    """
    Optimized batch processing for PDF OCR with concurrent processing
    """
    pages = await ocr.ocr_pdf_with_gpt_batch(file)
    return {"filename": file.filename, "pages": pages}


@router.post("/pdf-structured", response_model=dict)
async def ocr_pdf_structured(file: UploadFile = File(...)):
    """
    Enhanced OCR with structured output for better data extraction
    """
    return await ocr.ocr_pdf_with_structured_output(file)


# PyMuPDF-based endpoints (No external dependencies)

@router.post("/pdf-pymupdf", response_model=dict)
async def ocr_pdf_pymupdf(file: UploadFile = File(...)):
    """
    PDF OCR using PyMuPDF (no external dependencies required)
    """
    pages = await ocr.ocr_pdf_with_pymupdf(file)
    return {"filename": file.filename, "pages": pages, "method": "PyMuPDF"}


@router.post("/pdf-pymupdf-batch", response_model=dict)
async def ocr_pdf_pymupdf_batch(file: UploadFile = File(...)):
    """
    Batch PDF OCR using PyMuPDF with concurrent processing
    """
    pages = await ocr.ocr_pdf_with_pymupdf_batch(file)
    return {"filename": file.filename, "pages": pages, "method": "PyMuPDF-Batch"}


@router.post("/pdf-pymupdf-structured", response_model=dict)
async def ocr_pdf_pymupdf_structured(file: UploadFile = File(...)):
    """
    PyMuPDF-based PDF OCR with structured output
    """
    return await ocr.ocr_pdf_with_pymupdf_structured(file)


# pypdfium2-based endpoints (Google PDFium, liberal license)

@router.post("/pdf-pypdfium2", response_model=dict)
async def ocr_pdf_pypdfium2(file: UploadFile = File(...)):
    """
    PDF OCR using pypdfium2 (Google PDFium) - Liberal license, no external deps
    """
    pages = await ocr.ocr_pdf_with_pypdfium2(file)
    return {"filename": file.filename, "pages": pages, "method": "pypdfium2"}


@router.post("/pdf-pypdfium2-batch", response_model=dict)
async def ocr_pdf_pypdfium2_batch(file: UploadFile = File(...)):
    """
    Batch PDF OCR using pypdfium2 with concurrent processing
    """
    pages = await ocr.ocr_pdf_with_pypdfium2_batch(file)
    return {"filename": file.filename, "pages": pages, "method": "pypdfium2-Batch"}


@router.post("/pdf-pypdfium2-structured", response_model=dict)
async def ocr_pdf_pypdfium2_structured(file: UploadFile = File(...)):
    """
    pypdfium2-based PDF OCR with structured output
    """
    return await ocr.ocr_pdf_with_pypdfium2_structured(file)
