import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
    DB_NAME = os.getenv("DB_NAME", "register_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-secret-key")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
