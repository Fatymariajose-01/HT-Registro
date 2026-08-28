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
    
    # Configuración del Servicio de Correo Electrónico
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "sendgrid")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.mailtrap.io")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_SENDER = os.getenv("SMTP_SENDER", "noreply@sistemaextensible.com")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "SG.mock_key_123456789")
