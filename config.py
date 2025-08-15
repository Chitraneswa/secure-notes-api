import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")

if not SECRET_KEY or not MONGO_URI:
    raise ValueError("SECRET_KEY and MONGO_URI must be set in environment variables.")
