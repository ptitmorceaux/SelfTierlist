from dotenv import load_dotenv
load_dotenv()
import os

API_PORT = int(os.getenv("API_PORT", 8000))

URL_PATH_PREFIX = os.environ.get("URL_PATH_PREFIX")

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGO = os.getenv("JWT_ALGO")