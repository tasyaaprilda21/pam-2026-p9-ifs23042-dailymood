import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_PORT = int(os.getenv('APP_PORT', 5000))
    SECRET_KEY = 'dailymood-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dailymood.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LLM_BASE_URL = os.getenv('LLM_BASE_URL')
    LLM_TOKEN = os.getenv('LLM_TOKEN')