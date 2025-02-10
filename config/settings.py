import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

DEEPSEEK_MODEL = "deepseek_ai/deepseek-coder-33b-instruct"
GEMINI_MODEL = "gemini-pro"

MAX_PAGES = 50
MIN_PAGES = 40
OUTPUT_DIR = "output/surveys"
TEMP_DIR = "output/temp"