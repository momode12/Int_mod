import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI      = os.getenv("MONGO_URI")
    JWT_SECRET     = os.getenv("JWT_SECRET", "secret")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))