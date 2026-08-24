from core.faiss_store import get_relevant_chunks, has_document
from core.groq_client import call_groq_llm, detect_language
from core.session_manager import get_language, set_language

SUMMARY_KEYWORDS = [
    "summarize", "summary", "overview", "explain all",
    "what is this document", "tell me about this"
]

async def handle_question(question: str, user_id: str) -> str:
    if not has_document(user_id):
        return "⚠️ Please send a PDF or image first."

    lang = get_language(user_id)

    # If summary question → use more chunks
    is_summary = any(
        keyword in question.lower() 
        for keyword in SUMMARY_KEYWORDS
    )

    context = get_relevant_chunks(
        user_id, 
        question,
        k=12 if is_summary else None  # get more for summaries
    )

    prompt = f"""You are a document assistant. Answer ONLY using the context below.
If the answer is not in the context, say "I couldn't find that in the document."

Context:
{context}

Question: {question}"""

    return call_groq_llm(prompt, language=lang, user_id=user_id)