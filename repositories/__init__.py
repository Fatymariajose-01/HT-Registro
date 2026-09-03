from config import Config
from .base import BaseUserRepository
from .postgres import PostgresUserRepository
from .mysql import MySQLUserRepository

class DatabaseFactory:
    """
    Fábrica encargada de instanciar el repositorio de base de datos
    según la configuración DB_ENGINE del archivo .env.
    """
    _repositories = {
        "postgres": PostgresUserRepository,
        "postgresql": PostgresUserRepository,
        "mysql": MySQLUserRepository,
        "mariadb": MySQLUserRepository
    }
    
    _instance = None

    @classmethod
    def get_repository(cls) -> BaseUserRepository:
        engine = (Config.DB_ENGINE or "mysql").strip().lower()
        repo_class = cls._repositories.get(engine)
        if not repo_class:
            print(f"[DatabaseFactory] Advertencia: Motor '{engine}' no reconocido. Usando 'mysql' por defecto.")
            repo_class = MySQLUserRepository
            
        if cls._instance is None or not isinstance(cls._instance, repo_class):
            cls._instance = repo_class()
            
        return cls._instance
