import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    UNIPARTHENOPE_LOGIN_URL = os.getenv(
        "UNIPARTHENOPE_LOGIN_URL",
        "https://api.uniparthenope.it/UniparthenopeApp/v2/login",
    )
    UNIPARTHENOPE_TIMEOUT_SECONDS = float(os.getenv("UNIPARTHENOPE_TIMEOUT_SECONDS", "10"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
