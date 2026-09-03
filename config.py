import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    DB_ENGINE = os.getenv("DB_ENGINE", "mysql")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306" if os.getenv("DB_ENGINE", "mysql").lower() in ("mysql", "mariadb") else "5432"))
    DB_USER = os.getenv("DB_USER", "root" if os.getenv("DB_ENGINE", "mysql").lower() in ("mysql", "mariadb") else "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "register_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-secret-key")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    
    # Configuración del Servicio de Correo Electrónico
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_SENDER = os.getenv("SMTP_SENDER", "noreply@sistemaextensible.com")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "SG.mock_key_123456789")
