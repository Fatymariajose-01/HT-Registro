import abc

class FormField(abc.ABC):
    """
    Clase abstracta base para los campos del formulario.
    Cualquier campo nuevo debe heredar de esta clase e implementar sus métodos.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Nombre técnico del campo (se usará en DB, JSON y el name del HTML)."""
        pass

    @property
    @abc.abstractmethod
    def label(self) -> str:
        """Etiqueta visible del campo en la interfaz de usuario."""
        pass

    @property
    @abc.abstractmethod
    def field_type(self) -> str:
        """Tipo de campo HTML (text, email, number, password, tel, etc.)."""
        pass

    @property
    def required(self) -> bool:
        """Indica si el campo es obligatorio. Por defecto, True."""
        return True

    @abc.abstractmethod
    def validate(self, value) -> tuple[bool, str]:
        """
        Realiza la validación del valor ingresado por el usuario.
        Retorna una tupla: (es_valido: bool, mensaje_de_error: str).
        """
        pass

    def to_dict(self) -> dict:
        """Serializa el esquema del campo para que el frontend lo pueda dibujar."""
        return {
            "name": self.name,
            "label": self.label,
            "field_type": self.field_type,
            "required": self.required
        }
