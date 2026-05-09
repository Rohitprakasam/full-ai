"""OCR Service — PaddleOCR for images, PyMuPDF for PDFs. Runs locally."""
from paddleocr import PaddleOCR
import fitz  # PyMuPDF

ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)


def extract_text_from_image(image_path: str) -> str:
    result = ocr.ocr(image_path, cls=True)
    if not result or not result[0]:
        return ""
    lines = [word_info[1][0] for line in result for word_info in line]
    return "\n".join(lines)


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


def extract_text(file_path: str, file_type: str) -> str:
    file_type = file_type.lower().strip(".")
    if file_type in ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]:
        return extract_text_from_image(file_path)
    elif file_type == "pdf":
        return extract_text_from_pdf(file_path)
    return ""
