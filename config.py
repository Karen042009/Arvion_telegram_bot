#
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PA_USERNAME = "8Khumaryan8" 
DB_FULL_PATH = f"/home/{PA_USERNAME}/Arvion_Lingua_AI/Arvion_Lingua_AI/lingua_ai_bot.db"
DB_NAME = os.getenv("DATABASE_NAME", DB_FULL_PATH)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
#
"""
import os
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if 'PYTHONANYWHERE_VERSION' in os.environ:
    PA_USERNAME = os.environ.get("USER")  # Ավտոմատ վերցնում է username-ը
    DB_NAME = f"/home/{PA_USERNAME}/Arvion_Lingua_AI/Arvion_Lingua_AI/lingua_ai_bot.db"
else:
    DB_NAME = os.getenv("DATABASE_NAME", "lingua_ai_bot.db")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
if not TELEGRAM_TOKEN:
    raise ValueError("CRITICAL: TELEGRAM_BOT_TOKEN is not found. Please set it in your .env file or environment variables.")
"""

# ... մնացած կոդը մնում է նույնը ...

SUPPORTED_LANGUAGES = {
    'en': {"display_name": "English", "gemini_name": "English"},
    'hy': {"display_name": "Հայերեն", "gemini_name": "Armenian"},
    'ru': {"display_name": "Русский", "gemini_name": "Russian"},
    'es': {"display_name": "Español", "gemini_name": "Spanish"},
    'fr': {"display_name": "Français", "gemini_name": "French"},
    'de': {"display_name": "Deutsch", "gemini_name": "German"},
    'it': {"display_name": "Italiano", "gemini_name": "Italian"},
    'pt': {"display_name": "Português", "gemini_name": "Portuguese"},
    'zh': {"display_name": "中文 (Chinese)", "gemini_name": "Chinese"},
    'ja': {"display_name": "日本語 (Japanese)", "gemini_name": "Japanese"},
    'ko': {"display_name": "한국어 (Korean)", "gemini_name": "Korean"},
    'hi': {"display_name": "हिन्दी (Hindi)", "gemini_name": "Hindi"},
    'ar': {"display_name": "العربية (Arabic)", "gemini_name": "Arabic"},
}

LEARNING_LEVELS = {
    "beginner": "A1/A2 (Beginner)",
    "intermediate": "B1/B2 (Intermediate)",
    "advanced": "C1/C2 (Advanced)"
}

SUPPORTED_PROGRAMMING_LANGUAGES = {
    "python": {"display_name": "Python"},
    "javascript": {"display_name": "JavaScript"},
    "java": {"display_name": "Java"},
    "csharp": {"display_name": "C#"},
    "cpp": {"display_name": "C++"},
    "php": {"display_name": "PHP"},
    "swift": {"display_name": "Swift"},
    "kotlin": {"display_name": "Kotlin"},
    "sql": {"display_name": "SQL"},
    "go": {"display_name": "Go"},
}

PROGRAMMING_LEVELS = {
    "beginner": "Beginner / Junior",
    "intermediate": "Intermediate / Middle",
    "advanced": "Advanced / Senior"
}