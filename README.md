# Formulario de Registro de Usuarios Extensible (Python + Flask + PostgreSQL)

Este es un proyecto web con diseño de interfaz moderno (Glassmorphism, Dark Mode) y arquitectura extensible siguiendo el principio de software **Open/Closed** (Abierto para extensión, Cerrado para modificación).

El formulario de registro valida y guarda campos obligatorios en columnas específicas de la base de datos y permite agregar nuevos campos adicionales dinámicamente sin modificar clases core, archivos de frontend ni esquemas de base de datos SQL.

---

## Estructura del Proyecto

*   `app.py`: Servidor backend de Flask con APIs para el esquema del formulario, registro y listado de usuarios.
*   `config.py`: Carga y almacena variables de entorno del archivo `.env`.
*   `database.py`: Conector e inicializador automático de PostgreSQL. Guarda los datos core en columnas específicas y los dinámicos en una columna JSONB (`extra_data`).
*   `fields/`: Contiene la lógica del patrón Strategy para campos de formulario.
    *   `base.py`: Clase abstracta `FormField` que define la interfaz común de validación y renderizado.
    *   `core.py`: Contiene los campos solicitados originalmente (Nombre, Apellido, Edad, Correo, Contraseña).
    *   `custom.py`: Módulo designado para que crees tus propios campos personalizados.
    *   `__init__.py`: Descubre automáticamente las subclases de `FormField` y expone utilidades para validación general.
*   `templates/index.html`: Plantilla de interfaz web.
*   `static/`:
    *   `css/style.css`: Estilos visuales con animaciones sutiles y diseño de vidrio esmerilado.
    *   `js/main.js`: Renderizado del formulario dinámico en base al esquema del API, validaciones en tiempo real y peticiones AJAX.
*   `.env`: Archivo de configuración de credenciales (base de datos y llaves).
*   `requirements.txt`: Dependencias de Python necesarias.

---

## Requisitos Previos

1.  **Python 3.8+** instalado.
2.  **PostgreSQL** instalado y ejecutándose localmente.

---

## Instrucciones de Instalación y Ejecución

### 1. Clonar o descargar el proyecto en una carpeta local
Asegúrate de que estás en la carpeta del proyecto en tu terminal.

### 2. Crear y activar un entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Windows (CMD):
.\venv\Scripts\activate.bat
```

### 3. Instalar dependencias
Instala los paquetes necesarios enumerados en `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configurar las credenciales en `.env`
Abre el archivo [.env](file:///C:/Users/fatim/OneDrive/Documentos/HT%20Ing%20Software/.env) y ajusta las siguientes variables con tus datos locales de PostgreSQL:
*   `DB_USER`: Tu usuario de PostgreSQL (normalmente `postgres`).
*   `DB_PASSWORD`: La contraseña de tu cuenta de PostgreSQL.
*   `DB_HOST`: Servidor de base de datos (`localhost` si está en tu misma máquina).
*   `DB_PORT`: Puerto de conexión (por defecto es `5432`).

### 5. Iniciar la aplicación
Ejecuta el servidor de desarrollo de Flask:
```bash
python app.py
```

Al iniciar, la aplicación **creará automáticamente la base de datos `register_db` y la tabla `users`** por ti en tu PostgreSQL local. 

Abre tu navegador e ingresa a: **`http://localhost:5000`**

---

## Cómo Extender el Formulario (Principio Abierto/Cerrado)

Para comprobar el principio Abierto/Cerrado, puedes añadir un nuevo campo al formulario **sin modificar una sola clase existente ni cambiar la estructura de la base de datos**.

### Ejemplo: Agregar un campo de Teléfono

1.  Abre el archivo [fields/custom.py](file:///C:/Users/fatim/OneDrive/Documentos/HT%20Ing%20Software/fields/custom.py).
2.  Añade una nueva clase (o descomenta el bloque de ejemplo) al final del archivo:

```python
from .base import FormField
import re

class PhoneField(FormField):
    order = 6                     # Se mostrará en 6ta posición, tras la contraseña
    name = "phone"                # Nombre de la clave que se enviará al servidor
    label = "Teléfono"            # Etiqueta en la UI
    field_type = "tel"            # Tipo de campo en HTML
    required = False              # No es obligatorio para el registro

    def validate(self, value) -> tuple[bool, str]:
        val_str = str(value).strip()
        if not val_str:
            return True, ""  # Al no ser requerido, si está vacío es válido
        # Comprobar formato simple de teléfono
        if not re.match(r"^\+?[\d\s-]{8,15}$", val_str):
            return False, "El teléfono debe tener entre 8 y 15 dígitos."
        return True, ""
```

3.  Guarda el archivo y reinicia el servidor (`python app.py`).
4.  Refresca el navegador (`http://localhost:5000`). Verás que:
    *   El campo **Teléfono** se dibuja automáticamente al final del formulario.
    *   La validación en tiempo real funciona de inmediato.
    *   Al guardar un usuario, el teléfono se almacena automáticamente en el campo `extra_data` (tipo JSONB de PostgreSQL) y se muestra en la tabla de la derecha como un badge.
