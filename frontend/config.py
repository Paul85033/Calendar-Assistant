import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
AUTH_URL = os.getenv("AUTH_URL")