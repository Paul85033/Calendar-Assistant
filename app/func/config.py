import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GCA = os.getenv("GOOGLE_CALENDAR_API")
PCI = os.getenv("PRIMARY_CALENDAR_ID")
AUTH = os.getenv("GOOGLE_AUTH_ENDPOINT")
TOKEN = os.getenv("GOOGLE_TOKEN_ENDPOINT")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI",)
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]
STREAMLIT_URL = os.getenv("STREAMLIT_URL")
