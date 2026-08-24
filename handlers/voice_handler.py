import os
from pydub import AudioSegment
from core.groq_client import transcribe_audio, detect_language
from core.session_manager import get_language, set_language
import shutil

# Try env first, then system PATH, then fallback
ffmpeg_path = os.getenv("FFMPEG_PATH") or shutil.which("ffmpeg") or "ffmpeg"
ffprobe_path = os.getenv("FFPROBE_PATH") or shutil.which("ffprobe") or "ffprobe"

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

async def handle_voice_note(file_bytes: bytes, user_id: str) -> str:
    # Save as ogg first
    ogg_path = f"temp_{user_id}.ogg"
    wav_path = f"temp_{user_id}.wav"

    try:
        with open(ogg_path, "wb") as f:
            f.write(file_bytes)

        # Convert ogg → wav
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")
    finally:
        # Always clean up ogg, even if conversion fails
        if os.path.exists(ogg_path):
            os.remove(ogg_path)

    try:
        # Transcribe with Groq Whisper
        transcribed_text = transcribe_audio(wav_path)
    finally:
        # Always clean up wav, even if transcription fails
        if os.path.exists(wav_path):
            os.remove(wav_path)

    if not transcribed_text.strip():
        return "⚠️ Could not understand the voice note. Please speak clearly and try again."

    # Auto detect language from transcription
    detected_lang = detect_language(transcribed_text)
    set_language(user_id, detected_lang)

    from handlers.question_handler import handle_question
    return await handle_question(transcribed_text, user_id)