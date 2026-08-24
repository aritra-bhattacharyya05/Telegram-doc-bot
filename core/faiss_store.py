from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

faiss_store = {}
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
doc_chunk_count = {}


def store_document(user_id: str, text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.create_documents([text])
    faiss_store[user_id] = FAISS.from_documents(chunks, embeddings)
    doc_chunk_count[user_id] = len(chunks)


def get_relevant_chunks(user_id: str, question: str, k: int = None) -> str:
    if user_id not in faiss_store:
        return None                          
        
    # ← early exit if no doc

    # Dynamic k based on doc size (only runs if doc exists)
    if k is None:
        total_chunks = doc_chunk_count.get(user_id, 10)
        if total_chunks <= 5:
            k = total_chunks
        elif total_chunks <= 15:
            k = 6
        else:
            k = 12

    results = faiss_store[user_id].similarity_search(question, k=k)
    return "\n\n".join([r.page_content for r in results])


def has_document(user_id: str) -> bool:
    return user_id in faiss_store


def clear_document(user_id: str):
    if user_id in faiss_store:
        del faiss_store[user_id]
    if user_id in doc_chunk_count:
        del doc_chunk_count[user_id]