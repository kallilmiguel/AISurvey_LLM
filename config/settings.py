import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
GEMINI_MODEL = "gemini-pro"

MAX_PAGES = 50
MIN_PAGES = 40
OUTPUT_DIR = "output/surveys"
TEMP_DIR = "output/temp"

# Rate limiting settings
GEMINI_REQUESTS_PER_MINUTE = 60
RETRY_ATTEMPTS = 3
RETRY_DELAY = 20