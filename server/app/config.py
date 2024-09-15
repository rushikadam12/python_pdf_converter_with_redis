from dotenv import load_dotenv
import os
from datetime import timedelta


load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    REDIS_URL = os.environ.get("REDIS_URL")
    # SESSION_COOKIE_SAMESITE="None"
    # SESSION_COOKIE_SECURE=True
    # SESSION_PERMANENT=True
    # PERMANENT_SESSION_LIFETIME= timedelta(days=9999)
    DEBUG = True
