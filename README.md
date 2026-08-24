# 📄 Telegram Document Intelligence Bot

A production-ready AI-powered Telegram bot that lets users upload PDFs and images, extract text via OCR, and ask questions using a RAG pipeline. Supports voice input and multi-language responses.

---

## 🎯 Use Case

Common people (students, small business owners, farmers) can:
- 📄 Send a **PDF** (invoice, legal notice, bank statement, exam paper)
- 🖼️ Send an **image** of a document (scanned photo, screenshot)
- 🎙️ Ask questions via **voice note**
- 💬 Ask **follow-up questions** in their preferred language

---

## 🏗️ Architecture

```
User (Telegram)
      ↓
Telegram Bot API
      ↓
FastAPI-like Handler (python-telegram-bot)
   ↙        ↓        ↘
[PDF]    [Image]    [Voice/Text]
  ↓         ↓           ↓
PyMuPDF  Tesseract   Groq Whisper
(Extract)  (OCR)       (STT)
    ↘        ↓       ↙
      Extracted Text
           ↓
    Chunk + Embed
   (FAISS Vector DB)
           ↓
      RAG Pipeline
   (LangChain + Groq)
           ↓
      Final Response
           ↓
    Telegram → User
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Bot Interface | Telegram Bot API (`python-telegram-bot`) |
| PDF Extraction | PyMuPDF (`fitz`) |
| Image OCR | Tesseract OCR + Pillow |
| Speech-to-Text | Groq Whisper API |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector Store | FAISS (per-user in-memory) |
| LLM | Groq LLaMA 3.3 70B |
| RAG Framework | LangChain |
| Deployment | Docker + Railway |

---

## ✨ Features

- 📄 **PDF Intelligence** — Upload any PDF, get instant summary + Q&A
- 🖼️ **Image OCR** — Extract text from scanned documents and photos
- 🎙️ **Voice Input** — Ask questions via voice note (Whisper STT)
- 🔍 **RAG Pipeline** — Retrieval Augmented Generation for accurate answers
- 💬 **Chat History** — Follow-up questions with context memory
- 🌐 **Multi-language** — Supports English, Hindi, Bengali and more
- 📚 **Large Document Support** — Map-Reduce summarization for 10+ page docs
- 🧹 **Session Management** — Per-user FAISS index and chat history

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Tesseract OCR installed
- ffmpeg installed
- Groq API key
- Telegram Bot Token (from @BotFather)

### Installation

```bash
# Clone the repository
git clone https://github.com/AlimpanMukherjee/telegram-doc-bot.git
cd telegram-doc-bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
TESSERACT_PATH=C:/path/to/tesseract.exe  # Windows
# TESSERACT_PATH=tesseract               # Linux
FFMPEG_PATH=C:/path/to/ffmpeg.exe        # Windows
# FFMPEG_PATH=ffmpeg                     # Linux
FFPROBE_PATH=C:/path/to/ffprobe.exe      # Windows
# FFPROBE_PATH=ffprobe                   # Linux
```

### Run Locally

```bash
python main.py
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t telegram-doc-bot .

# Run container
docker run --env-file .env telegram-doc-bot
```

---

## 📁 Project Structure

```
telegram-doc-bot/
│
├── core/
│   ├── __init__.py
│   ├── groq_client.py       # Groq LLM + Whisper STT
│   ├── faiss_store.py       # Per-user FAISS vector store
│   └── session_manager.py   # Language preference management
│
├── handlers/
│   ├── __init__.py
│   ├── pdf_handler.py       # PDF extraction + Map-Reduce summary
│   ├── image_handler.py     # Tesseract OCR pipeline
│   ├── voice_handler.py     # Voice note → STT → RAG
│   └── question_handler.py  # RAG Q&A pipeline
│
├── main.py                  # Bot entry point + handler registration
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

## 💬 Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot and select language |
| `/language` | Change response language |
| `/clear` | Clear current document and chat history |
| `/stop` | End session |

---

## 🌐 Supported Languages

| Language | Support |
|---|---|
| English | ✅ Excellent |
| Hindi | ✅ Excellent |
| Bengali | ✅ Good |
| Others | ⚠️ Auto-detected |

---

## 📊 RAG Pipeline Details

```
Document Upload
      ↓
Text Extraction (PyMuPDF / Tesseract)
      ↓
Chunking (800 tokens, 100 overlap)
      ↓
Embedding (all-MiniLM-L6-v2)
      ↓
FAISS Vector Store (per user)
      ↓
Question → Similarity Search (dynamic k)
      ↓
Context + Question → Groq LLaMA 3.3
      ↓
Answer in user's language
```

---

## ⚠️ Known Limitations

- Sessions are in-memory — lost on server restart
- OCR quality depends on image clarity
- Groq free tier: 30 requests/minute
- Large documents (50+ pages) may have incomplete coverage

---

## 🔮 Future Improvements (V2)

- [ ] Redis for persistent session storage
- [ ] PostgreSQL for user data
- [ ] Rate limiting for multiple users
- [ ] Support for Word documents and Excel files
- [ ] User authentication / whitelist
- [ ] Web dashboard for document management

---

## 👨‍💻 Author

**Alimpan Mukherjee**  
B.Tech CSE | KIIT University (Batch 2027)  
AI/ML Engineer

[![GitHub](https://img.shields.io/badge/GitHub-AlimpanMukherjee-black?logo=github)](https://github.com/AlimpanMukherjee)

---

## 📄 License

This project is licensed under the MIT License.
