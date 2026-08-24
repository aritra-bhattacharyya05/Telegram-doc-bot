import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from handlers.pdf_handler import handle_pdf
from handlers.image_handler import handle_image_ocr
from handlers.voice_handler import handle_voice_note
from handlers.question_handler import handle_question
from core.groq_client import clear_history
from core.faiss_store import clear_document
from core.session_manager import set_language

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_English"),
            InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_Hindi"),
        ],
        [
            InlineKeyboardButton("🇮🇳 Bengali", callback_data="lang_Bengali"),
            InlineKeyboardButton("🌍 Other", callback_data="lang_English"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to Document Assistant Bot!\n\n"
        "I can read your PDFs and images and answer questions about them.\n\n"
        "📌 Please select your language first:",
        reply_markup=reply_markup
    )


# Language button handler
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    lang = query.data.replace("lang_", "")
    set_language(user_id, lang)

    await query.edit_message_text(
        f"✅ Language set to {lang}!\n\n"
        f"Now send me:\n"
        f"📄 A PDF document\n"
        f"🖼️ An image of a document\n"
        f"🎙️ A voice note with your question"
    )


# PDF / Document handler
async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text("⏳ Processing your document...")

    file = await update.message.document.get_file()
    file_bytes = await file.download_as_bytearray()
    mime = update.message.document.mime_type or ""

    if "pdf" in mime:
        reply = await handle_pdf(bytes(file_bytes), user_id)
    else:
        reply = await handle_image_ocr(bytes(file_bytes), user_id)

    await update.message.reply_text(reply)


# Photo handler
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text("⏳ Scanning your image...")

    file = await update.message.photo[-1].get_file()
    file_bytes = await file.download_as_bytearray()
    reply = await handle_image_ocr(bytes(file_bytes), user_id)

    await update.message.reply_text(reply)


# Voice handler
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text("🎙️ Transcribing your voice note...")

    file = await update.message.voice.get_file()
    file_bytes = await file.download_as_bytearray()
    reply = await handle_voice_note(bytes(file_bytes), user_id)

    await update.message.reply_text(reply)


# Text / question handler
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    question = update.message.text
    reply = await handle_question(question, user_id)
    await update.message.reply_text(reply)


# /clear command
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    clear_history(user_id)
    clear_document(user_id)
    await update.message.reply_text(
        "🗑️ Cleared! Send a new document to start fresh."
    )


# /language command — show language buttons again
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_English"),
            InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_Hindi"),
        ],
        [
            InlineKeyboardButton("🇧🇩 Bengali", callback_data="lang_Bengali"),
            InlineKeyboardButton("🌍 Other", callback_data="lang_English"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose your language:",
        reply_markup=reply_markup
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Clear everything for this user
    clear_history(user_id)
    clear_document(user_id)
    
    await update.message.reply_text(
        "👋 Session ended! All your data has been cleared.\n\n"
        "Send /start to begin a new session."
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("stop", stop_command))

    # Callback for language buttons
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    # Message handlers
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()