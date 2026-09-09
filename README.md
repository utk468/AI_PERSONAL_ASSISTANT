# 🤖 AI Personal Assistant & Task Automation

A modern, intelligent Personal Assistant and Task Scheduling application powered by **FastAPI**, **LangChain**, **Groq LLM (LLaMA 3)**, **APScheduler**, and **MongoDB**. It converts natural language prompts into precisely scheduled tasks with real-time browser notifications (SSE) and Telegram alerts.

---

## ✨ Features

- 🧠 **Natural Language Intent Extraction**: Converts conversational requests into structured task details, priority, and execution timestamps using LangChain & Groq (`llama3-8b-8192`).
- 🛡️ **Hybrid Offline Fallback**: Automatically falls back to an offline rule-based parser (`parsedatetime` + Regex) if the LLM provider is unavailable.
- ⏰ **Dynamic & Recurring Scheduling**: Handles one-time reminders, relative dates (e.g. *"in 20 minutes"*, *"tomorrow at 5 PM"*), and recurring patterns (*"every Monday at 9 AM"*) using APScheduler.
- ⚡ **Real-Time Browser Notifications**: Instant push notifications to the web dashboard via **Server-Sent Events (SSE)**.
- 📱 **Telegram Bot Integration**: Delivers reminder notifications directly to your Telegram chat.
- 🎨 **Modern Glassmorphic UI**: Sleek, responsive dark-mode dashboard built with Vanilla CSS, modular ES6 JavaScript, and Lucide icons.
- 🗄️ **Persistent Database**: Asynchronous MongoDB storage powered by `motor`.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **AI & NLP**: [LangChain](https://www.langchain.com/), [Groq](https://groq.com/) (`ChatGroq` / `llama3-8b-8192`), `parsedatetime`
- **Scheduler**: [APScheduler](https://apscheduler.readthedocs.io/) (`AsyncIOScheduler`)
- **Database**: [MongoDB](https://www.mongodb.com/) via [Motor](https://motor.readthedocs.io/)
- **Real-Time Stream**: Server-Sent Events (SSE)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism design system), Vanilla JavaScript (ES6 Modules)

---

## 📁 Project Structure

```
PERSONAL_AI_ASSISITANT/
├── backend/
│   ├── __init__.py
│   ├── api.py               # REST API routes & SSE stream endpoint
│   ├── config.py            # Environment configuration & settings
│   ├── database.py          # Async MongoDB connection & CRUD operations
│   ├── intent_extractor.py  # LangChain Groq LLM + offline fallback parser
│   ├── main.py              # FastAPI application entry point & lifespan
│   ├── mongo_schema.py      # Pydantic schema for database records
│   ├── notifier.py          # SSE broadcaster & Telegram notification broker
│   ├── scheduler.py         # APScheduler instance & task execution lifecycle
│   └── schemas.py           # API request and response models
├── frontend/
│   ├── css/
│   │   └── styles.css       # Glassmorphism styling and animations
│   ├── html/
│   │   ├── components/      # UI component templates
│   │   └── index.html       # Single-page application entry
│   └── js/
│       ├── app.js           # Core frontend controller & SSE listener
│       └── api.js           # Frontend API client
├── .env.template            # Template for environment variables
├── requirements.txt         # Python project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.10+** installed
- **MongoDB** running locally (`mongodb://localhost:27017`) or a [MongoDB Atlas](https://www.mongodb.com/atlas) connection URI
- *(Optional)* **Groq Cloud API Key** for LLM intent extraction ([Get API Key](https://console.groq.com/))
- *(Optional)* **Telegram Bot Token & Chat ID** for Telegram notifications

---

### 2. Installation

1. **Clone or open the repository:**
   ```bash
   cd PERSONAL_AI_ASSISITANT
   ```

2. **Create and activate a virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Environment Configuration

Create a `.env` file in the root directory by copying `.env.template`:

```bash
# Windows
copy .env.template .env

# Linux / macOS
cp .env.template .env
```

Configure the variables inside `.env`:

```env
# Core Server Settings
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Database Backend
DB_BACKEND=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=personal_assistant

# LLM Provider (Groq)
GROQ_API_KEY=your_groq_api_key_here

# Telegram Notifications (Optional)
# 1. Message @BotFather on Telegram to obtain BOT TOKEN
# 2. Message @userinfobot to obtain your CHAT ID
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

> **Note:** If `GROQ_API_KEY` is not provided or fails, the application automatically uses its built-in rule-based offline parser.

---

### 4. Running the Application

Start the FastAPI development server:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access the web dashboard:
- **Dashboard UI**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reminders` | Parse natural language text and create a scheduled reminder |
| `GET` | `/api/reminders` | Retrieve all reminders (supports `?active_only=true`) |
| `DELETE` | `/api/reminders/{reminder_id}` | Cancel and remove a scheduled reminder |
| `GET` | `/api/stream` | Server-Sent Events (SSE) live notification stream |
| `GET` | `/api/status` | System health check and backend connection status |

---

## 💡 Example Prompts

You can type prompts naturally in the dashboard input box:

- *"Remind me to drink water every 2 hours"*
- *"Schedule team standup tomorrow at 10:00 AM"*
- *"Call mom tonight at 8 PM high priority"*
- *"Submit financial report on Friday at 4 PM"*
- *"Take vitamins every day at 8 AM"*

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
