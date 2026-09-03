import re
from .base import FormField

class NameField(FormField):
    order = 1
    name = "name"
    label = "Nombre"
    field_type = "text"
    
    def validate(self, value) -> tuple[bool, str]:
        val_str = str(value).strip()
        if len(val_str) < 2:
            return False, "El nombre debe tener al menos 2 caracteres."
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", val_str):
            return False, "El nombre solo puede contener letras y espacios."
        return True, ""

class LastNameField(FormField):
    order = 2
    name = "last_name"
    label = "Apellido"
    field_type = "text"
    
    def validate(self, value) -> tuple[bool, str]:
        val_str = str(value).strip()
        if len(val_str) < 2:
            return False, "El apellido debe tener al menos 2 caracteres."
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", val_str):
            return False, "El apellido solo puede contener letras y espacios."
        return True, ""

class AgeField(FormField):
    order = 3
    name = "age"
    label = "Edad"
    field_type = "number"
    
    def validate(self, value) -> tuple[bool, str]:
        try:
            val_int = int(value)
            if val_int < 18 or val_int > 100:
                return False, "Debe ser mayor de 18 años pero menor de 100."
            return True, ""
        except ValueError:
            return False, "La edad debe ser un número entero válido."

class EmailField(FormField):
    order = 4
    name = "email"
    label = "Correo Electrónico"
    field_type = "email"
    
    def validate(self, value) -> tuple[bool, str]:
        val_str = str(value).strip()
        # Expresión regular estándar para correos
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, val_str):
            return False, "El formato del correo electrónico no es válido."
        return True, ""


class PasswordField(FormField):
    order = 5
    name = "password"
    label = "Contraseña"
    field_type = "password"

    def validate(self, value) -> tuple[bool, str]:
        val_str = str(value)
        if len(val_str) < 10:
            return False, "La contraseña debe tener al menos 10 caracteres."
        if not any(char.isdigit() for char in val_str):
            return False, "La contraseña debe contener al menos un número."
        if not any(char.isupper() for char in val_str):
            return False, "La contraseña debe contener al menos una letra mayúscula."
        if not any(char.islower() for char in val_str):
            return False, "La contraseña debe contener al menos una letra minúscula."
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?" for char in val_str):
            return False, "La contraseña debe contener al menos un carácter especial."
        return True, ""
