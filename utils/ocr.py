import pdfplumber
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
import os

def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".txt"):
        # Handle text files directly
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Text file error: {e}")
            return ""
    elif file_path.lower().endswith(".pdf"):
        text = ""
        
        # First try with pdfplumber for text-based PDFs
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber error: {e}")
        
        # If no text found, try OCR on PDF pages as images
        if not text.strip():
            print("No text found with pdfplumber, trying OCR on PDF pages...")
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text.strip():
                        text += f"Page {page_num + 1}:\n{ocr_text}\n"
                doc.close()
            except Exception as e:
                print(f"PDF OCR error: {e}")
        
        return text.strip()
    else:
        # Handle image files
        try:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Image OCR error: {e}")
            return ""
