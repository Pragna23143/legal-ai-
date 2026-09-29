import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
UPLOADS_DIR = BASE_DIR / "uploads"

# Ensure runtime directories exist
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API configuration
# Fallback order: os.environ -> empty string (triggers smart simulated analysis)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Up-to-date standard Gemini model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Chunking Configuration
CHUNK_SIZE_TOKENS = int(os.getenv("CHUNK_SIZE_TOKENS", "450"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "80"))

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
