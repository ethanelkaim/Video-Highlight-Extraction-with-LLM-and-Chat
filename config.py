import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "video_highlights")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")  # IMPORTANT: Change this

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# LLM API Configuration
LLM_API_KEY = "AIzaSyDL2Fm4Dau3zAUpBFcAVFn6UaRdJbIECr4"  #  Set Gemini API key directly.
LLM_MODEL_NAME = "gemini-2.0-flash"  #  Use Gemini flash model
LLM_EMBEDDING_MODEL = "models/embedding-001"

# Paths
VIDEO_STORAGE_PATH = os.getenv("VIDEO_STORAGE_PATH", "data/videos")
HIGHLIGHT_STORAGE_PATH = os.getenv("HIGHLIGHT_STORAGE_PATH", "data/highlights")

# Ensure directories exist
os.makedirs(VIDEO_STORAGE_PATH, exist_ok=True)
os.makedirs(HIGHLIGHT_STORAGE_PATH, exist_ok=True)