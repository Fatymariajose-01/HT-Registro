import inspect
from .base import FormField
from . import core, custom  # Importamos los módulos para que Python cargue las subclases en memoria

class FormRegistry:
    _fields: list[FormField] = []
    _initialized = False

    @classmethod
    def initialize(cls):
        """Descubre e inicializa dinámicamente todas las subclases concretas de FormField."""
        if cls._initialized:
            return
        
        seen = set()
        
        # Función auxiliar recursiva para encontrar subclases
        def get_all_subclasses(klass):
            all_subclasses = []
            for subclass in klass.__subclasses__():
                if not inspect.isabstract(subclass):
                    all_subclasses.append(subclass)
                all_subclasses.extend(get_all_subclasses(subclass))
            return all_subclasses

        subclasses = get_all_subclasses(FormField)
        
        instantiated_fields = []
        for sub_cls in subclasses:
            if sub_cls not in seen:
                seen.add(sub_cls)
                instantiated_fields.append(sub_cls())
        
        # Ordenar los campos por su atributo 'order'. Si no lo tienen, por defecto es 999
        instantiated_fields.sort(key=lambda f: getattr(f, 'order', 999))
        cls._fields = instantiated_fields
        cls._initialized = True

    @classmethod
    def get_fields(cls) -> list[FormField]:
        """Obtiene la lista de todas las instancias de campos registrados."""
        cls.initialize()
        return cls._fields

    @classmethod
    def get_field_by_name(cls, name: str) -> FormField | None:
        """Busca un campo por su nombre técnico."""
        cls.initialize()
        for field in cls._fields:
            if field.name == name:
                return field
        return None

    @classmethod
    def validate_data(cls, data: dict) -> tuple[bool, dict[str, str]]:
        """
        Valida un diccionario de datos (recibido por el frontend) contra todos los campos registrados.
        Retorna (es_valido, diccionario_de_errores).
        """
        cls.initialize()
        errors = {}
        for field in cls._fields:
            val = data.get(field.name)
            
            # Verificar si es requerido
            if field.required and (val is None or str(val).strip() == ""):
                errors[field.name] = f"El campo '{field.label}' es requerido."
                continue
            
            # Ejecutar la validación específica del campo si el valor no está vacío
            if val is not None and str(val).strip() != "":
                is_valid, err_msg = field.validate(val)
                if not is_valid:
                    errors[field.name] = err_msg
                    
        return len(errors) == 0, errors
