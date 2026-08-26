from .base import FormField

"""
=============================================================================
MÓDULO DE CAMPOS PERSONALIZADOS (EXTENSIÓN)
=============================================================================
Para agregar un nuevo campo al formulario de registro y a la base de datos:
1. Crea una clase aquí que herede de 'FormField'.
2. Define sus propiedades (order, name, label, field_type, required).
3. Implementa su método 'validate(self, value)'.

¡Eso es todo! La aplicación detectará automáticamente el campo, lo renderizará
en la interfaz de usuario, aplicará sus reglas de validación en el servidor
y guardará su valor dentro del JSONB 'extra_data' en PostgreSQL.

-----------------------------------------------------------------------------
EJEMPLO (Descomenta las líneas de abajo si deseas habilitar un campo Teléfono):

class PhoneField(FormField):
    order = 6                     # Se mostrará después de la contraseña
    name = "phone"                # Nombre técnico que se guardará en extra_data
    label = "Teléfono de Contacto" # Etiqueta visible
    field_type = "tel"            # Tipo de input HTML
    required = False              # No es obligatorio para el registro

    def validate(self, value) -> tuple[bool, str]:
        import re
        val_str = str(value).strip()
        # Si no es requerido y está vacío, es válido
        if not val_str:
            return True, ""
        # Validar formato telefónico simple
        if not re.match(r"^\+?[\d\s-]{8,15}$", val_str):
            return False, "El teléfono debe tener entre 8 y 15 dígitos."
        return True, ""
-----------------------------------------------------------------------------
"""
