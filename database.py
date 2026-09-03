"""
Módulo de Base de Datos (Patrón Fachada / Facade).
Proporciona una interfaz unificada y retrocompatible para el controlador (app.py),
delegando la ejecución real al repositorio del motor activo (MySQL, PostgreSQL, etc.)
configurado a través de DatabaseFactory.
"""

from repositories import DatabaseFactory

def get_connection():
    """Establece conexión a la base de datos a través del repositorio activo."""
    return DatabaseFactory.get_repository().get_connection()

def init_db():
    """Inicializa el esquema y tablas a través del repositorio activo."""
    return DatabaseFactory.get_repository().init_db()

def save_user(form_data: dict, registered_fields: list) -> tuple[bool, str, str | None]:
    """Guarda un usuario a través del repositorio activo."""
    return DatabaseFactory.get_repository().save_user(form_data, registered_fields)

def get_all_users() -> list[dict]:
    """Recupera la lista de todos los usuarios registrados a través del repositorio activo."""
    return DatabaseFactory.get_repository().get_all_users()

def verify_user_token(token: str) -> tuple[bool, str]:
    """Verifica la cuenta del usuario a través del repositorio activo."""
    return DatabaseFactory.get_repository().verify_user_token(token)
