import fitz
from core.faiss_store import store_document, clear_document
from core.groq_client import call_groq_llm, clear_history
from core.session_manager import get_language


async def map_reduce_summary(pages: list, language: str, user_id: str) -> str:
    mini_summaries = []
    batch_size = 4

    for i in range(0, len(pages), batch_size):
        batch = " ".join(pages[i:i + batch_size])
        prompt = f"Summarize this section in 5 bullet points:\n\n{batch[:2000]}"
        mini = call_groq_llm(prompt, language=language, user_id=user_id)
        mini_summaries.append(mini)

    combined = "\n\n".join(mini_summaries)
    final_prompt = f"""These are section summaries of a large document.
Create one cohesive and detailed  final summary in 10-15 bullet points:\n\n{combined}"""

    return call_groq_llm(final_prompt, language=language, user_id=user_id)


async def handle_pdf(file_bytes: bytes, user_id: str) -> str:
    clear_document(user_id)
    clear_history(user_id)

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    full_text = " ".join(pages)
    page_count = len(doc)

    if not full_text.strip():
        return "⚠️ This PDF has no readable text. Try sending a scanned image instead."

    store_document(user_id, full_text)
    lang = get_language(user_id)

    if page_count > 7:
        summary = await map_reduce_summary(pages, lang, user_id)
    else:
        prompt = f"Summarize this document in details in  10-15 bullet points:\n\n{full_text[:8000]}"
        summary = call_groq_llm(prompt, language=lang, user_id=user_id)

    return f"📄 Document received! ({page_count} pages)\n\n{summary}\n\n✅ Ask me anything!"