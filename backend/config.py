import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    DB_BACKEND: str = os.getenv("DB_BACKEND", "mongodb")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "personal_assistant")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")

settings = Settings()
     