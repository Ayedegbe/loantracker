import os
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "your-jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
