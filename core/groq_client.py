import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_histories = {}  # { user_id: [ {role, content}, ... ] }


def detect_language(text: str) -> str:
    """Auto detect if user typed Hindi, Bengali or English"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"Detect the language of this text and reply with ONLY one word - either 'Hindi', 'Bengali' or 'English':\n\n{text}"
            }
        ],
        max_tokens=10
    )
    detected = response.choices[0].message.content.strip()
    if detected in ["Hindi", "Bengali", "English"]:
        return detected
    return "English"  # fallback


MAX_HISTORY = 20  # keep last 10 turns (user + assistant pairs)

def call_groq_llm(prompt: str, language: str = "English", user_id: str = None) -> str:

    # Initialize history for new user
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # Add user message to history
    chat_histories[user_id].append({
        "role": "user",
        "content": prompt
    })

    # Trim to last 10 turns to prevent token overflow
    if len(chat_histories[user_id]) > MAX_HISTORY:
        chat_histories[user_id] = chat_histories[user_id][-MAX_HISTORY:]

    # Build full message list
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful document assistant. "
                       f"Always respond in {language} only. Be concise and clear."
        }
    ] + chat_histories[user_id]

    # Call Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000
    )

    reply = response.choices[0].message.content

    # Save assistant reply to history
    chat_histories[user_id].append({
        "role": "assistant",
        "content": reply
    })

    return reply


def transcribe_audio(audio_path: str) -> str:
    """Convert voice note to text using Groq Whisper"""
    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f
        )
    return transcription.text


def clear_history(user_id: str):
    """Reset chat history when user sends a new document"""
    if user_id in chat_histories:
        chat_histories[user_id] = []