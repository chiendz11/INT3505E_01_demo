import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")
    BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL")
    TRANSACTION_SERVICE_URL = os.environ.get("TRANSACTION_SERVICE_URL")
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN")