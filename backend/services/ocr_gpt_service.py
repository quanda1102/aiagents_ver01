import base64
from typing import Tuple, List
from fastapi import UploadFile
from io import BytesIO
from pdf2image import convert_from_bytes
from openai import OpenAI
import asyncio
import fitz  # PyMuPDF
from PIL import Image
import pypdfium2 as pdfium

client = OpenAI()


def encode_image_to_base64(file: UploadFile) -> Tuple[str, str]:
    content = file.file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    mime_type = file.content_type
    return f"data:{mime_type};base64,{encoded}", file.filename


def encode_bytes_to_base64_image(image_bytes: bytes, content_type: str = "image/png") -> str:
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{base64_str}"


async def ocr_image_with_gpt(file: UploadFile) -> str:
    image_bytes = await file.read()
    return await ocr_bytes_with_gpt(image_bytes, file.content_type)


async def ocr_bytes_with_gpt(image_bytes: bytes, content_type: str = "image/png") -> str:
    base64_image = encode_bytes_to_base64_image(image_bytes, content_type)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an OCR system. Extract ALL text from the image exactly as written. Do not provide any commentary, explanations, or conversational responses. Return ONLY the extracted text content.

Rules:
- Extract text exactly as it appears
- Preserve formatting and line breaks
- Support Vietnamese diacritics (ă, â, ê, ô, ơ, ư, đ, tone marks)
- Support English text
- If no text is found, return: [NO TEXT DETECTED]
- Do not add phrases like "I can help", "Here is the text", or any commentary
- Output ONLY the raw extracted text"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2048,
            temperature=0.0,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


async def ocr_bytes_with_gpt_optimized(image_bytes: bytes, page_number: int = 1, content_type: str = "image/png") -> str:
    """
    Optimized OCR function with better prompting and error handling for PDF pages
    """
    base64_image = encode_bytes_to_base64_image(image_bytes, content_type)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an OCR text extraction system. Extract ALL visible text from the image exactly as written. Do not provide explanations, commentary, or conversational responses.

CRITICAL RULES:
- Extract text exactly as it appears in the image
- Preserve all formatting, line breaks, and spacing
- Support Vietnamese diacritics: ă, â, ê, ô, ơ, ư, đ, and all tone marks
- Support English text with proper capitalization
- Handle mixed Vietnamese-English content
- If text is unclear, use [UNCLEAR: approximate_text]
- Maintain document structure (tables, lists, paragraphs)
- If no text exists, return: [NO TEXT DETECTED]
- NEVER respond with "I can help", "Here is the text", or similar phrases
- Output ONLY the extracted text content, nothing else"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Page {page_number} - extract text:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096,  # Increased for longer documents
            temperature=0.0,  # Zero temperature for consistent OCR output
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error processing page {page_number}: {str(e)}"


async def ocr_pdf_with_gpt(file: UploadFile) -> List[str]:
    try:
        pdf_bytes = await file.read()
        # Optimize DPI for better OCR accuracy (300 DPI is better for text)
        images = convert_from_bytes(pdf_bytes, dpi=300, fmt='PNG')

        results = []
        for idx, img in enumerate(images):
            buf = BytesIO()
            # Optimize image format and quality for OCR
            img.save(buf, format="PNG", optimize=True, quality=95)
            image_bytes = buf.getvalue()

            # Enhanced OCR with better prompting
            text = await ocr_bytes_with_gpt_optimized(image_bytes, page_number=idx+1)
            results.append(text)

        return results

    except Exception as e:
        return [f"Error processing PDF: {str(e)}"]


async def ocr_pdf_with_gpt_batch(file: UploadFile, max_concurrent: int = 3) -> List[str]:
    """
    Optimized batch processing for PDF OCR with concurrent processing
    """
    try:
        pdf_bytes = await file.read()
        # Optimize DPI for better OCR accuracy
        images = convert_from_bytes(pdf_bytes, dpi=300, fmt='PNG')

        # Process pages concurrently but limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_page(idx: int, img) -> str:
            async with semaphore:
                buf = BytesIO()
                img.save(buf, format="PNG", optimize=True, quality=95)
                image_bytes = buf.getvalue()
                return await ocr_bytes_with_gpt_optimized(image_bytes, page_number=idx+1)

        # Create tasks for all pages
        tasks = [process_page(idx, img) for idx, img in enumerate(images)]
        
        # Process all pages concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(f"Error processing page {idx+1}: {str(result)}")
            else:
                processed_results.append(result)
        
        return processed_results

    except Exception as e:
        return [f"Error processing PDF: {str(e)}"]


async def ocr_pdf_with_structured_output(file: UploadFile) -> dict:
    """
    Enhanced OCR with structured output for better data extraction
    """
    try:
        pdf_bytes = await file.read()
        images = convert_from_bytes(pdf_bytes, dpi=300, fmt='PNG')

        pages_data = []
        for idx, img in enumerate(images):
            buf = BytesIO()
            img.save(buf, format="PNG", optimize=True, quality=95)
            image_bytes = buf.getvalue()
            
            # Extract structured data
            structured_text = await ocr_bytes_with_structured_output(image_bytes, page_number=idx+1)
            pages_data.append({
                "page_number": idx + 1,
                "content": structured_text
            })

        return {
            "filename": file.filename,
            "total_pages": len(images),
            "pages": pages_data
        }

    except Exception as e:
        return {
            "filename": file.filename,
            "error": f"Error processing PDF: {str(e)}",
            "pages": []
        }


async def ocr_bytes_with_structured_output(image_bytes: bytes, page_number: int = 1) -> dict:
    """
    OCR with structured output for better data organization
    """
    base64_image = encode_bytes_to_base64_image(image_bytes)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an OCR data extraction system. Extract text and output structured JSON. Do not provide explanations or commentary.

REQUIRED JSON FORMAT:
{
  "raw_text": "complete extracted text",
  "sections": [{"header": "section title", "content": "section text"}],
  "tables": [{"rows": ["table data"]}],
  "metadata": {"languages": ["vi", "en"], "quality": "high/medium/low"}
}

EXTRACTION RULES:
- Extract ALL visible text exactly as written
- Support Vietnamese diacritics: ă, â, ê, ô, ơ, ư, đ, tone marks
- Support English text with proper formatting
- Preserve document structure and formatting
- If no text: {"raw_text": "[NO TEXT DETECTED]", "sections": [], "tables": [], "metadata": {"quality": "empty"}}
- Output ONLY valid JSON, no conversational responses"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Page {page_number} JSON:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "raw_text": f"Error processing page {page_number}: {str(e)}",
            "sections": [],
            "tables": [],
            "metadata": {"error": True, "page_number": page_number}
        }


# PyMuPDF-based implementations (No external dependencies needed)

async def ocr_pdf_with_pymupdf(file: UploadFile) -> List[str]:
    """
    PDF OCR using PyMuPDF (fitz) - No external dependencies required
    """
    try:
        pdf_bytes = await file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        results = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Convert page to image (PNG format)
            # mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for even better OCR quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            
            # Process with optimized OCR
            text = await ocr_bytes_with_gpt_optimized(img_data, page_number=page_num+1)
            results.append(text)
        
        pdf_document.close()
        return results
        
    except Exception as e:
        return [f"Error processing PDF with PyMuPDF: {str(e)}"]


async def ocr_pdf_with_pymupdf_batch(file: UploadFile, max_concurrent: int = 3) -> List[str]:
    """
    Batch PDF OCR using PyMuPDF with concurrent processing
    """
    try:
        pdf_bytes = await file.read()
        
        # Convert all pages to images first to avoid document sharing issues
        page_images = []
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            page_images.append(img_data)
        
        pdf_document.close()
        
        # Process images concurrently
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_image(page_num: int, img_data: bytes) -> str:
            async with semaphore:
                try:
                    return await ocr_bytes_with_gpt_optimized(img_data, page_number=page_num+1)
                except Exception as e:
                    return f"Error processing page {page_num+1}: {str(e)}"
        
        # Create tasks for all pages
        tasks = [process_image(idx, img_data) for idx, img_data in enumerate(page_images)]
        
        # Process all pages concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(f"Error processing page {idx+1}: {str(result)}")
            else:
                processed_results.append(result)
        
        return processed_results
        
    except Exception as e:
        return [f"Error processing PDF with PyMuPDF: {str(e)}"]


async def ocr_pdf_with_pymupdf_structured(file: UploadFile) -> dict:
    """
    PyMuPDF-based PDF OCR with structured output
    """
    try:
        pdf_bytes = await file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(pdf_document)
        
        pages_data = []
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            
            # Convert page to high-quality image
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Extract structured data
            structured_text = await ocr_bytes_with_structured_output(img_data, page_number=page_num+1)
            pages_data.append({
                "page_number": page_num + 1,
                "content": structured_text
            })
        
        pdf_document.close()
        
        return {
            "filename": file.filename,
            "total_pages": total_pages,
            "pages": pages_data,
            "processing_method": "PyMuPDF"
        }
        
    except Exception as e:
        return {
            "filename": file.filename,
            "error": f"Error processing PDF with PyMuPDF: {str(e)}",
            "pages": [],
            "processing_method": "PyMuPDF"
        }


def get_pdf_info_with_pymupdf(pdf_bytes: bytes) -> dict:
    """
    Get PDF information using PyMuPDF
    """
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        info = {
            "page_count": len(pdf_document),
            "metadata": pdf_document.metadata,
            "is_encrypted": pdf_document.is_encrypted,
            "processing_method": "PyMuPDF"
        }
        
        pdf_document.close()
        return info
        
    except Exception as e:
        return {
            "error": f"Error getting PDF info: {str(e)}",
            "processing_method": "PyMuPDF"
        }


# pypdfium2-based implementations (Google PDFium, liberal license)

async def ocr_pdf_with_pypdfium2(file: UploadFile) -> List[str]:
    """
    PDF OCR using pypdfium2 (Google PDFium) - Liberal license, no external dependencies
    """
    try:
        pdf_bytes = await file.read()
        
        # Open PDF with pypdfium2
        pdf = pdfium.PdfDocument(pdf_bytes)
        
        results = []
        for page_index in range(len(pdf)):
            page = pdf.get_page(page_index)
            
            # Render page to bitmap with high DPI for better OCR
            bitmap = page.render(
                scale=3.0,  # 3x scale for better quality
                rotation=0
            )
            
            # Convert to PIL Image
            pil_image = bitmap.to_pil()
            
            # Convert PIL image to bytes
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            # Process with optimized OCR
            text = await ocr_bytes_with_gpt_optimized(img_data, page_number=page_index+1)
            results.append(text)
        
        pdf.close()
        return results
        
    except Exception as e:
        return [f"Error processing PDF with pypdfium2: {str(e)}"]


async def ocr_pdf_with_pypdfium2_batch(file: UploadFile, max_concurrent: int = 3) -> List[str]:
    """
    Batch PDF OCR using pypdfium2 with concurrent processing
    """
    try:
        pdf_bytes = await file.read()
        
        # Convert all pages to images first to avoid document sharing issues
        page_images = []
        pdf = pdfium.PdfDocument(pdf_bytes)
        
        for page_index in range(len(pdf)):
            page = pdf.get_page(page_index)
            bitmap = page.render(scale=3.0, rotation=0)
            pil_image = bitmap.to_pil()
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            page_images.append(img_data)
        
        pdf.close()
        
        # Process images concurrently
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_image(page_index: int, img_data: bytes) -> str:
            async with semaphore:
                try:
                    return await ocr_bytes_with_gpt_optimized(img_data, page_number=page_index+1)
                except Exception as e:
                    return f"Error processing page {page_index+1}: {str(e)}"
        
        # Create tasks for all pages
        tasks = [process_image(idx, img_data) for idx, img_data in enumerate(page_images)]
        
        # Process all pages concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(f"Error processing page {idx+1}: {str(result)}")
            else:
                processed_results.append(result)
        
        return processed_results
        
    except Exception as e:
        return [f"Error processing PDF with pypdfium2: {str(e)}"]


async def ocr_pdf_with_pypdfium2_structured(file: UploadFile) -> dict:
    """
    pypdfium2-based PDF OCR with structured output
    """
    try:
        pdf_bytes = await file.read()
        
        # Open PDF with pypdfium2
        pdf = pdfium.PdfDocument(pdf_bytes)
        total_pages = len(pdf)
        
        pages_data = []
        for page_index in range(total_pages):
            page = pdf.get_page(page_index)
            
            # Render page to bitmap with high DPI
            bitmap = page.render(
                scale=3.0,  # 3x scale for better quality
                rotation=0
            )
            
            # Convert to PIL Image then to bytes
            pil_image = bitmap.to_pil()
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            # Extract structured data
            structured_text = await ocr_bytes_with_structured_output(img_data, page_number=page_index+1)
            pages_data.append({
                "page_number": page_index + 1,
                "content": structured_text
            })
        
        pdf.close()
        
        return {
            "filename": file.filename,
            "total_pages": total_pages,
            "pages": pages_data,
            "processing_method": "pypdfium2"
        }
        
    except Exception as e:
        return {
            "filename": file.filename,
            "error": f"Error processing PDF with pypdfium2: {str(e)}",
            "pages": [],
            "processing_method": "pypdfium2"
        }


# Enhanced Vietnamese OCR functions

async def ocr_vietnamese_optimized(image_bytes: bytes, content_type: str = "image/png") -> str:
    """
    Vietnamese-optimized OCR with specific handling for Vietnamese diacritics
    """
    base64_image = encode_bytes_to_base64_image(image_bytes, content_type)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a Vietnamese text extraction system. Extract ALL text with perfect Vietnamese diacritics. Do not provide explanations or conversational responses.

VIETNAMESE DIACRITICS:
- Base vowels: a, ă, â, e, ê, i, o, ô, ơ, u, ư, y
- Special consonant: đ (d with stroke)
- Tone marks: ` ´ ˜ ˆ ˇ (grave, acute, tilde, circumflex, caron)
- Examples: á, à, ả, ã, ạ, ắ, ằ, ẳ, ẵ, ặ, ấ, ầ, ẩ, ẫ, ậ

EXTRACTION RULES:
- Extract text exactly as written in the image
- Preserve ALL Vietnamese diacritics perfectly
- Support Vietnamese + English mixed content
- Maintain original formatting and line breaks
- If no text: [NO TEXT DETECTED]
- NEVER respond with "Tôi có thể giúp", explanations, or commentary
- Output ONLY the extracted text content"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract text:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.0,  # Zero temperature for consistent OCR output
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


async def ocr_image_with_vietnamese_support(file: UploadFile) -> str:
    """
    Enhanced image OCR with Vietnamese language support
    """
    image_bytes = await file.read()
    return await ocr_vietnamese_optimized(image_bytes, file.content_type)
