import easyocr
import numpy as np
import cv2
from PIL import Image
import io
from fastapi import UploadFile
import logging
from typing import Dict

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo EasyOCR reader hỗ trợ tiếng Việt + tiếng Anh
reader = easyocr.Reader(['en', 'vi'], gpu=False)

async def ocr_image(file: UploadFile) -> Dict[str, str]:
    try:
        # Đọc file ảnh
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
        
        # Kiểm tra chất lượng ảnh
        height, width = image_np.shape[:2]
        if height < 300 or width < 300:
            logger.warning(f"Low resolution image: {file.filename}")
        
        # Tiền xử lý ảnh
        # 1. Chuyển sang grayscale
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # 2. Kiểm tra độ tương phản để chọn phương pháp threshold
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_sum = np.sum(hist)
        low_contrast = (hist[0] + hist[-1]) / hist_sum > 0.8  # Ảnh có độ tương phản thấp
        
        if low_contrast:
            # Áp dụng CLAHE và adaptive threshold cho ảnh độ tương phản thấp
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        else:
            # Sử dụng Otsu's threshold (tương tự code cũ) cho ảnh tương phản tốt
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 3. Deskew (chỉ áp dụng nếu cần)
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        if abs(angle) > 1.0:  # Chỉ xoay nếu góc nghiêng > 1 độ
            (h, w) = image_np.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # 4. OCR với tham số tối ưu cho tiếng Việt
        results = reader.readtext(
            thresh,
            detail=0,
            paragraph=True,
            contrast_ths=0.3,  # Tăng ngưỡng để giảm lỗi nhận diện
            adjust_contrast=0.7,
            text_threshold=0.8,  # Tăng độ tin cậy
            low_text=0.4,  # Giảm ngưỡng cho văn bản nhỏ
            mag_ratio=1.5  # Tăng độ phóng đại cho ảnh nhỏ
        )
        
        # Gộp và làm sạch kết quả
        text = " ".join([str(text) for text in results if text]).strip()
        
        if not text:
            logger.warning(f"No text detected in {file.filename}")
            return {
                "filename": file.filename,
                "text": "",
                "warning": "No text detected in the image"
            }
            
        return {
            "filename": file.filename,
            "text": text
        }
        
    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        raise Exception(f"Failed to process image: {str(e)}")