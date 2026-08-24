import pytesseract
from PIL import Image, ImageEnhance
from io import BytesIO
from core.faiss_store import store_document, clear_document
from core.groq_client import call_groq_llm, clear_history
from core.session_manager import get_language
import os

# Windows path for Tesseract
pytesseract.pytesseract.tesseract_cmd =os.getenv("TESSERACT_PATH", "tesseract")


async def handle_image_ocr(file_bytes: bytes, user_id: str) -> str:
    # Clear old document and chat history
    clear_document(user_id)
    clear_history(user_id)

    # Preprocess image for better OCR
    img = Image.open(BytesIO(file_bytes)).convert("L")  # grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)       # boost contrast

    # Extract text
    extracted_text = pytesseract.image_to_string(img)

    if not extracted_text.strip():
        return "⚠️ Could not read text from this image. Please send a clearer photo."

    # Store in FAISS
    store_document(user_id, extracted_text)

    # Get user language
    lang = get_language(user_id)

    # Auto summarize
    prompt = f"Summarize this document in details without missing important points in 10 clear bullet points:\n\n{extracted_text[:3000]}"
    summary = call_groq_llm(prompt, language=lang, user_id=user_id)

    return f"🖼️ Image scanned!\n\n{summary}\n\n✅ Ask me anything about this image."