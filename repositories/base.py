import abc

class BaseUserRepository(abc.ABC):
    """
    Contrato base abstracto para cualquier motor de base de datos (PostgreSQL, MySQL, SQLite, etc.).
    Garantiza que cualquier motor implemente exactamente la misma interfaz para el controlador.
    """

    @abc.abstractmethod
    def get_connection(self):
        """Establece y retorna una conexión a la base de datos de la aplicación."""
        pass

    @abc.abstractmethod
    def init_db(self):
        """Inicializa la base de datos y la tabla de usuarios automáticamente."""
        pass

    @abc.abstractmethod
    def save_user(self, form_data: dict, registered_fields: list) -> tuple[bool, str, str | None]:
        """
        Guarda un nuevo usuario con campos core y dinámicos, retornando:
        (éxito: bool, mensaje: str, verification_token: str | None)
        """
        pass

    @abc.abstractmethod
    def get_all_users(self) -> list[dict]:
        """Recupera la lista de todos los usuarios registrados."""
        pass

    @abc.abstractmethod
    def verify_user_token(self, token: str) -> tuple[bool, str]:
        """Verifica una cuenta buscando su token y actualizando su estado de verificación."""
        pass
