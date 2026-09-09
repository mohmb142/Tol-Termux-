import os
from pathlib import Path
from dotenv import load_dotenv

APP_DIR = Path.home() / ".termux-ai"
ENV_FILE = APP_DIR / ".env"
load_dotenv(ENV_FILE)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
