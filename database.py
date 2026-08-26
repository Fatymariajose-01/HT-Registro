import json
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from config import Config

def get_admin_connection():
    """Establece conexión a la base de datos por defecto 'postgres' para tareas administrativas."""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database="postgres"
    )

def get_connection():
    """Establece conexión a la base de datos de la aplicación."""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def init_db():
    """
    Inicializa PostgreSQL de manera automática:
    1. Crea la base de datos si no existe.
    2. Crea la tabla 'users' con los campos core y la columna JSONB 'extra_data'.
    """
    conn = None
    try:
        conn = get_admin_connection()
        conn.autocommit = True
        with conn.cursor() as cursor:
            # Comprobar si la base de datos ya existe
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (Config.DB_NAME,))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {Config.DB_NAME};")
                print(f"Base de datos '{Config.DB_NAME}' creada con éxito.")
            else:
                print(f"Base de datos '{Config.DB_NAME}' ya existe.")
    except Exception as e:
        print(f"Alerta: No se pudo verificar o crear la base de datos '{Config.DB_NAME}' administrativamente: {e}")
        print("Intentando conectar directamente para crear la tabla...")
    finally:
        if conn:
            conn.close()

    # Inicializar la tabla
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                password VARCHAR(255) NOT NULL,
                extra_data JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("Tabla 'users' verificada/creada exitosamente.")
    except Exception as e:
        print(f"Error crítico al inicializar la tabla 'users': {e}")
        raise e
    finally:
        if conn:
            conn.close()

def save_user(form_data, registered_fields) -> tuple[bool, str]:
    """
    Guarda un usuario clasificando campos core y adicionales.
    Cifra la contraseña de manera segura.
    """
    # Definir campos fijos en la tabla
    core_keys = {"email", "name", "last_name", "age", "password"}
    
    # Extraer valores core
    email = form_data.get("email").strip().lower()
    name = form_data.get("name").strip()
    last_name = form_data.get("last_name").strip()
    
    try:
        age = int(form_data.get("age"))
    except (ValueError, TypeError):
        return False, "La edad debe ser un número válido."
        
    password_hash = generate_password_hash(form_data.get("password"))
    
    # Extraer campos personalizados (que no sean parte de las columnas físicas)
    extra_data = {}
    for field in registered_fields:
        if field.name not in core_keys:
            extra_data[field.name] = form_data.get(field.name)
            
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO users (email, name, last_name, age, password, extra_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            cursor.execute(insert_query, (
                email,
                name,
                last_name,
                age,
                password_hash,
                json.dumps(extra_data)
            ))
            user_id = cursor.fetchone()[0]
            conn.commit()
            return True, f"Usuario registrado exitosamente con ID: {user_id}."
    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()
        return False, "El correo electrónico ya se encuentra registrado."
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error en base de datos al guardar usuario: {str(e)}"
    finally:
        if conn:
            conn.close()

def get_all_users() -> list[dict]:
    """Recupera todos los registros de usuarios para mostrarlos en el frontend."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, email, name, last_name, age, extra_data, created_at FROM users ORDER BY created_at DESC;")
            records = cursor.fetchall()
            # Convertir objetos datetime a strings legibles
            for rec in records:
                if rec.get("created_at"):
                    rec["created_at"] = rec["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            return records
    except Exception as e:
        print(f"Error al recuperar usuarios: {e}")
        return []
    finally:
        if conn:
            conn.close()
